"""🧪 Tests para Position Monitor

Este módulo contiene tests comprehensivos para el sistema de monitoreo de posiciones,
incluyendo:
- Monitoreo continuo de precios
- Ejecución automática de TP/SL
- Trailing stops dinámicos
- Gestión de cache y threading
- Coordinación con PositionManager
"""

import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional

# Importaciones del sistema
from src.core.position_monitor import PositionMonitor, PositionStatus
from src.core.position_manager import PositionInfo
from src.core.enhanced_strategies import TradingSignal
from src.core.paper_trader import TradeResult
from src.database.models import Trade
from src.config.config import TradingBotConfig, TradingProfiles


class TestPositionMonitorInitialization:
    """🔧 Tests de inicialización del Position Monitor"""
    
    def test_initialization_basic(self):
        """Test inicialización básica del monitor"""
        price_fetcher = Mock(return_value=50000.0)
        paper_trader = Mock()
        
        monitor = PositionMonitor(price_fetcher, paper_trader)
        
        assert monitor.price_fetcher == price_fetcher
        assert monitor.paper_trader == paper_trader
        assert not monitor.monitoring_active
        assert monitor.monitor_thread is None
        assert len(monitor.processed_trades) == 0
        assert len(monitor.failed_close_attempts) == 0
        assert monitor.position_manager is not None
    
    def test_initialization_with_config(self):
        """Test inicialización con configuración específica"""
        price_fetcher = Mock(return_value=50000.0)
        paper_trader = Mock()
        
        with patch.object(TradingProfiles, 'get_current_profile') as mock_profile:
            mock_profile.return_value = {
                'max_close_attempts': 5,
                'price_cache_duration': 60,
                'position_log_interval': 120,
                'idle_sleep_multiplier': 3,
                'trailing_stop_activation': 0.02,
                'monitor_interval': 30,
                'analysis_interval': 300
            }
            
            monitor = PositionMonitor(price_fetcher, paper_trader)
            
            assert monitor.max_close_attempts == 5
            assert monitor.price_cache_duration == 60
            assert monitor.log_interval == 120
            assert monitor.idle_sleep_multiplier == 3
    
    def test_initialization_stats(self):
        """Test inicialización de estadísticas"""
        price_fetcher = Mock(return_value=50000.0)
        paper_trader = Mock()
        
        monitor = PositionMonitor(price_fetcher, paper_trader)
        
        expected_stats = {
            "tp_executed": 0,
            "sl_executed": 0,
            "positions_monitored": 0,
            "monitoring_cycles": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        assert monitor.stats == expected_stats


class TestPositionMonitorPriceCache:
    """💰 Tests del sistema de cache de precios"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.price_fetcher = Mock()
        self.paper_trader = Mock()
        self.monitor = PositionMonitor(self.price_fetcher, self.paper_trader)
    
    def test_get_current_price_fresh(self):
        """Test obtener precio fresco"""
        self.price_fetcher.return_value = 50000.0
        
        price = self.monitor._get_current_price("BTC/USDT")
        
        assert price == 50000.0
        assert "BTC/USDT" in self.monitor.price_cache
        assert self.monitor.price_cache["BTC/USDT"].value == 50000.0
        assert not self.monitor.price_cache["BTC/USDT"].is_expired()
        self.price_fetcher.assert_called_once_with("BTC/USDT")
    
    def test_get_current_price_cached(self):
        """Test obtener precio desde cache"""
        from src.core.position_monitor import CacheEntry
        from datetime import datetime
        
        # Configurar cache
        self.monitor.price_cache["BTC/USDT"] = CacheEntry(
            value=50000.0,
            timestamp=datetime.now(),
            ttl_seconds=30
        )
        
        price = self.monitor._get_current_price("BTC/USDT")
        
        assert price == 50000.0
        self.price_fetcher.assert_not_called()
    
    def test_get_current_price_cache_expired(self):
        """Test obtener precio cuando cache expiró"""
        from src.core.position_monitor import CacheEntry
        from datetime import datetime, timedelta
        
        # Configurar cache expirado
        self.monitor.price_cache["BTC/USDT"] = CacheEntry(
            value=50000.0,
            timestamp=datetime.now() - timedelta(seconds=100),  # Expirado
            ttl_seconds=30
        )
        self.price_fetcher.return_value = 51000.0
        
        price = self.monitor._get_current_price("BTC/USDT")
        
        assert price == 51000.0
        assert self.monitor.price_cache["BTC/USDT"].value == 51000.0
        self.price_fetcher.assert_called_once_with("BTC/USDT")
    
    def test_get_current_price_error(self):
        """Test manejo de errores al obtener precio"""
        self.price_fetcher.side_effect = Exception("Network error")
        
        price = self.monitor._get_current_price("BTC/USDT")
        
        assert price is None
        self.price_fetcher.assert_called_once_with("BTC/USDT")
    
    def test_get_current_price_invalid_value(self):
        """Test manejo de valores inválidos"""
        self.price_fetcher.return_value = 0  # Precio inválido
        
        price = self.monitor._get_current_price("BTC/USDT")
        
        assert price is None
        self.price_fetcher.assert_called_once_with("BTC/USDT")


class TestPositionMonitorThreading:
    """🧵 Tests del sistema de threading"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.price_fetcher = Mock(return_value=50000.0)
        self.paper_trader = Mock()
        self.monitor = PositionMonitor(self.price_fetcher, self.paper_trader)
    
    def test_start_monitoring(self):
        """Test iniciar monitoreo"""
        # Mock que mantiene el thread vivo por un momento
        def mock_monitoring_loop():
            while self.monitor.monitoring_active and not self.monitor.stop_event.is_set():
                time.sleep(0.01)  # Pequeña pausa para mantener el thread activo
        
        with patch.object(self.monitor, '_monitoring_loop', side_effect=mock_monitoring_loop):
            self.monitor.start_monitoring()
            
            # Dar tiempo al thread para iniciar
            time.sleep(0.05)
            
            assert self.monitor.monitoring_active
            assert self.monitor.monitor_thread is not None
            assert self.monitor.monitor_thread.is_alive()
            assert not self.monitor.stop_event.is_set()
            
            # Limpiar
            self.monitor.stop_monitoring()
    
    def test_start_monitoring_already_active(self):
        """Test iniciar monitoreo cuando ya está activo"""
        self.monitor.monitoring_active = True
        
        with patch.object(self.monitor, '_monitoring_loop'):
            self.monitor.start_monitoring()
            
            assert self.monitor.monitor_thread is None
    
    def test_stop_monitoring(self):
        """Test detener monitoreo"""
        with patch.object(self.monitor, '_monitoring_loop'):
            self.monitor.start_monitoring()
            self.monitor.stop_monitoring()
            
            assert not self.monitor.monitoring_active
            assert self.monitor.stop_event.is_set()
    
    def test_stop_monitoring_not_active(self):
        """Test detener monitoreo cuando no está activo"""
        self.monitor.stop_monitoring()
        
        assert not self.monitor.monitoring_active


class TestPositionMonitorPositionProcessing:
    """📊 Tests del procesamiento de posiciones"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.price_fetcher = Mock(return_value=50000.0)
        self.paper_trader = Mock()
        self.monitor = PositionMonitor(self.price_fetcher, self.paper_trader)
        
        # Mock del PositionManager
        self.mock_position_manager = Mock()
        self.monitor.position_manager = self.mock_position_manager
    
    def test_monitor_position_basic(self):
        """Test monitoreo básico de posición"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        self.mock_position_manager.check_exit_conditions.return_value = None
        
        self.monitor._monitor_position(position)
        
        self.mock_position_manager.update_position_price.assert_called_once_with(1, 50000.0)
        self.mock_position_manager.check_exit_conditions.assert_called_once_with(position)
    
    def test_monitor_position_should_close_success(self):
        """Test cierre exitoso de posición"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        self.mock_position_manager.check_exit_conditions.return_value = "TAKE_PROFIT"
        self.mock_position_manager.close_position.return_value = True
        
        self.monitor._monitor_position(position)
        
        self.mock_position_manager.close_position.assert_called_once_with(1, 50000.0, "TAKE_PROFIT")
        assert 1 in self.monitor.processed_trades
        assert self.monitor.stats["tp_executed"] == 1
    
    def test_monitor_position_should_close_stop_loss(self):
        """Test cierre por stop loss"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        self.mock_position_manager.check_exit_conditions.return_value = "STOP_LOSS"
        self.mock_position_manager.close_position.return_value = True
        
        self.monitor._monitor_position(position)
        
        assert self.monitor.stats["sl_executed"] == 1
    
    def test_monitor_position_close_failure(self):
        """Test fallo al cerrar posición"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        self.mock_position_manager.check_exit_conditions.return_value = "TAKE_PROFIT"
        self.mock_position_manager.close_position.return_value = False
        
        self.monitor._monitor_position(position)
        
        assert 1 not in self.monitor.processed_trades
        assert 1 in self.monitor.failed_close_attempts
        assert self.monitor.failed_close_attempts[1] == 1
    
    def test_monitor_position_max_attempts_reached(self):
        """Test máximo de intentos alcanzado"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        # Configurar máximo de intentos alcanzado
        self.monitor.failed_close_attempts[1] = self.monitor.max_close_attempts
        self.mock_position_manager.check_exit_conditions.return_value = "TAKE_PROFIT"
        
        self.monitor._monitor_position(position)
        
        assert 1 in self.monitor.processed_trades
        self.mock_position_manager.close_position.assert_not_called()
    
    def test_monitor_position_already_processed(self):
        """Test posición ya procesada"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        self.monitor.processed_trades.add(1)
        
        self.monitor._monitor_position(position)
        
        self.mock_position_manager.update_position_price.assert_not_called()
        self.mock_position_manager.check_exit_conditions.assert_not_called()
    
    def test_monitor_position_price_fetch_error(self):
        """Test error al obtener precio"""
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=49000.0,
            current_price=50000.0,
            quantity=0.1,
            entry_value=4900.0,
            current_value=5000.0,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.04,
            stop_loss=48000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=0.5,
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )
        
        self.price_fetcher.side_effect = Exception("Network error")
        
        self.monitor._monitor_position(position)
        
        self.mock_position_manager.update_position_price.assert_not_called()


class TestPositionMonitorCleanup:
    """🧹 Tests del sistema de limpieza"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.price_fetcher = Mock(return_value=50000.0)
        self.paper_trader = Mock()
        self.monitor = PositionMonitor(self.price_fetcher, self.paper_trader)
        
        # Mock del PositionManager
        self.mock_position_manager = Mock()
        self.monitor.position_manager = self.mock_position_manager
    
    def test_cleanup_processed_trades(self):
        """Test limpieza de trades procesados"""
        # Configurar trades procesados y activos
        self.monitor.processed_trades = {1, 2, 3, 4}
        self.monitor.failed_close_attempts = {1: 2, 2: 1, 5: 3}
        
        # Mock posiciones activas (solo 1 y 3)
        active_positions = [
            PositionInfo(
                trade_id=1, symbol="BTC/USDT", trade_type="BUY", entry_price=50000.0,
                current_price=50000.0, quantity=0.1, entry_value=5000.0, current_value=5000.0,
                unrealized_pnl=0.0, unrealized_pnl_percentage=0.0, stop_loss=None, take_profit=None,
                trailing_stop=None, entry_time=datetime.now(), strategy_name="TEST",
                confidence_score=0.8, timeframe="1h", notes="Test position",
                days_held=0.5, max_profit=150.0, max_loss=-50.0, risk_reward_ratio=2.0
            ),
            PositionInfo(
                trade_id=3, symbol="ETH/USDT", trade_type="BUY", entry_price=3000.0,
                current_price=3000.0, quantity=1.0, entry_value=3000.0, current_value=3000.0,
                unrealized_pnl=0.0, unrealized_pnl_percentage=0.0, stop_loss=None, take_profit=None,
                trailing_stop=None, entry_time=datetime.now(), strategy_name="TEST",
                confidence_score=0.8, timeframe="1h", notes="Test position",
                days_held=0.5, max_profit=150.0, max_loss=-50.0, risk_reward_ratio=2.0
            )
        ]
        self.mock_position_manager.get_active_positions.return_value = active_positions
        
        self.monitor._cleanup_processed_trades()
        
        # Verificar limpieza
        assert self.monitor.processed_trades == {1, 3}
        assert self.monitor.failed_close_attempts == {1: 2}
    
    def test_cleanup_processed_trades_error(self):
        """Test manejo de errores en limpieza"""
        self.mock_position_manager.get_active_positions.side_effect = Exception("DB error")
        
        # No debe lanzar excepción
        self.monitor._cleanup_processed_trades()
    
    def test_reset_processed_trades(self):
        """Test reset de trades procesados"""
        self.monitor.processed_trades = {1, 2, 3}
        self.monitor.failed_close_attempts = {1: 2, 2: 1}
        
        self.monitor.reset_processed_trades()
        
        assert len(self.monitor.processed_trades) == 0
        assert len(self.monitor.failed_close_attempts) == 0


class TestPositionMonitorStatistics:
    """📈 Tests de estadísticas del monitor"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.price_fetcher = Mock(return_value=50000.0)
        self.paper_trader = Mock()
        self.monitor = PositionMonitor(self.price_fetcher, self.paper_trader)
        
        # Mock del PositionManager
        self.mock_position_manager = Mock()
        self.monitor.position_manager = self.mock_position_manager
    
    def test_get_monitor_stats(self):
        """Test obtener estadísticas del monitor"""
        # Configurar estado usando métodos thread-safe
        self.monitor.monitoring_active = True
        with self.monitor._stats_lock:
            self.monitor.stats["monitoring_cycles"] = 100
            self.monitor.stats["tp_executed"] = 5
            self.monitor.stats["sl_executed"] = 3
        self.monitor.processed_trades = {1, 2, 3}
        self.monitor.failed_close_attempts = {4: 2}
        
        stats = self.monitor.get_monitor_stats()
        
        expected_stats = {
            "monitoring_active": True,
            "monitoring_cycles": 100,
            "tp_executed": 5,
            "sl_executed": 3,
            "positions_monitored": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_efficiency": "0.00%",
            "cache_size": 0,
            "processed_trades_count": 3,
            "failed_attempts_count": 1,
            "processed_trades": [1, 2, 3],
            "failed_attempts": {4: 2},
            "max_close_attempts": self.monitor.max_close_attempts,
            "thread_pool_active": True
        }
        
        assert stats == expected_stats
    
    def test_get_monitoring_status(self):
        """Test obtener estado del monitoreo"""
        from src.core.position_monitor import CacheEntry
        from datetime import datetime
        
        # Mock estadísticas del PositionManager
        position_stats = {
            "active_positions": 5,
            "positions_managed": 20,
            "take_profits_executed": 8,
            "stop_losses_executed": 4,
            "trailing_stops_activated": 12,
            "total_realized_pnl": 1500.0
        }
        self.mock_position_manager.get_statistics.return_value = position_stats
        
        # Configurar cache de precios con CacheEntry
        self.monitor.price_cache = {
            "BTC/USDT": CacheEntry(value=50000.0, timestamp=datetime.now(), ttl_seconds=30),
            "ETH/USDT": CacheEntry(value=3000.0, timestamp=datetime.now(), ttl_seconds=30)
        }
        
        status = self.monitor.get_monitoring_status()
        
        assert status["monitoring_active"] == self.monitor.monitoring_active
        assert status["monitor_interval"] == self.monitor.monitor_interval
        assert status["cache"]["size"] == 2
        assert status["positions"]["active_positions"] == 5
        assert status["positions"]["total_realized_pnl"] == 1500.0


class TestPositionMonitorIntegration:
    """🔗 Tests de integración del Position Monitor"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.price_fetcher = Mock()
        self.paper_trader = Mock()
        self.monitor = PositionMonitor(self.price_fetcher, self.paper_trader)
    
    @patch('time.sleep')  # Evitar delays en tests
    def test_monitoring_loop_no_positions(self, mock_sleep):
        """Test loop de monitoreo sin posiciones"""
        # Mock del PositionManager
        self.mock_position_manager = Mock()
        self.monitor.position_manager = self.mock_position_manager
        
        # Mock posiciones vacías
        self.mock_position_manager.get_active_positions.return_value = []
        
        # Configurar para que pare después de una iteración
        def stop_after_one(*args, **kwargs):
            self.monitor.monitoring_active = False
        
        mock_sleep.side_effect = stop_after_one
        
        self.monitor.monitoring_active = True
        self.monitor._monitoring_loop()
        
        with self.monitor._stats_lock:
            assert self.monitor.stats["monitoring_cycles"] == 1
        mock_sleep.assert_called_with(self.monitor.monitor_interval * self.monitor.idle_sleep_multiplier)
    
    @patch('time.sleep')
    def test_monitoring_loop_with_positions(self, mock_sleep):
        """Test loop de monitoreo con posiciones"""
        # Mock del PositionManager
        self.mock_position_manager = Mock()
        self.monitor.position_manager = self.mock_position_manager
        
        # Mock posiciones activas
        positions = [
            PositionInfo(
                trade_id=1, symbol="BTC/USDT", trade_type="BUY", entry_price=50000.0,
                current_price=50000.0, quantity=0.1, entry_value=5000.0, current_value=5000.0,
                unrealized_pnl=0.0, unrealized_pnl_percentage=0.0, stop_loss=None, take_profit=None,
                trailing_stop=None, entry_time=datetime.now(), strategy_name="TEST",
                confidence_score=0.8, timeframe="1h", notes="Test position",
                days_held=0.5, max_profit=150.0, max_loss=-50.0, risk_reward_ratio=2.0
            )
        ]
        self.mock_position_manager.get_active_positions.return_value = positions
        self.mock_position_manager.update_trailing_stops.return_value = 0
        self.mock_position_manager.update_dynamic_take_profits.return_value = 0
        self.mock_position_manager.check_exit_conditions.return_value = None
        
        self.price_fetcher.return_value = 51000.0
        
        # Configurar para que pare después de una iteración
        def stop_after_one(*args, **kwargs):
            self.monitor.monitoring_active = False
        
        mock_sleep.side_effect = stop_after_one
        
        self.monitor.monitoring_active = True
        self.monitor._monitoring_loop()
        
        with self.monitor._stats_lock:
            assert self.monitor.stats["monitoring_cycles"] == 1
        self.monitor.position_manager.update_trailing_stops.assert_called_once()
        self.monitor.position_manager.update_dynamic_take_profits.assert_called_once()
    
    def test_full_monitoring_cycle(self):
        """Test ciclo completo de monitoreo"""
        # Mock del PositionManager
        self.mock_position_manager = Mock()
        self.monitor.position_manager = self.mock_position_manager
        
        # Configurar posición que debe cerrarse
        position = PositionInfo(
            trade_id=1,
            symbol="BTC/USDT",
            trade_type="BUY",
            entry_price=50000.0,
            current_price=52500.0,
            quantity=0.1,
            entry_value=5000.0,
            current_value=5250.0,
            unrealized_pnl=250.0,
            unrealized_pnl_percentage=5.0,
            stop_loss=49000.0,
            take_profit=52000.0,
            trailing_stop=None,
            entry_time=datetime.now(),
            strategy_name="TEST",
            confidence_score=0.8,
            timeframe="1h",
            notes="Test position",
            days_held=1.0,
            max_profit=250.0,
            max_loss=-100.0,
            risk_reward_ratio=2.5
        )
        
        self.mock_position_manager.get_active_positions.return_value = [position]
        self.mock_position_manager.check_exit_conditions.return_value = "TAKE_PROFIT"
        self.mock_position_manager.close_position.return_value = True
        self.mock_position_manager.update_trailing_stops.return_value = 0
        self.mock_position_manager.update_dynamic_take_profits.return_value = 0
        
        self.price_fetcher.return_value = 52500.0  # Precio que activa TP
        
        # Ejecutar monitoreo de la posición
        self.monitor._monitor_position(position)
        
        # Verificar que se ejecutó el cierre
        assert 1 in self.monitor.processed_trades
        assert self.monitor.stats["tp_executed"] == 1
        self.mock_position_manager.close_position.assert_called_once_with(1, 52500.0, "TAKE_PROFIT")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])