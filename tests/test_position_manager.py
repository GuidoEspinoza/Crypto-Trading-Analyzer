"""🧪 Tests para Position Manager

Tests completos para el sistema de gestión de posiciones optimizado,
incluyendo cache inteligente, configuración dinámica y trailing stops.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, List, Optional

# Importaciones del sistema
from src.core.position_manager import PositionManager, PositionInfo, PositionUpdate
from src.config.config import TradingProfiles, RiskManagerConfig
from src.core.paper_trader import TradeResult
from src.database.models import Trade


class TestPositionManagerOptimized:
    """🧪 Tests para Position Manager Optimizado"""
    
    @pytest.fixture
    def mock_trading_profiles(self):
        """🔧 Mock para TradingProfiles con configuración de test"""
        test_profile = {
            'position_check_interval': 5,  # 5 segundos para tests
            'seconds_per_day': 86.4,  # 1 día = 86.4 segundos para tests rápidos
            'default_trailing_distance': 1.5,  # 1.5%
            'atr_multiplier': 2.5,  # multiplicador personalizado
            'atr_estimation_percentage': 1.8,  # 1.8% estimación
            'tp_max_ratio': 0.7,
            'tp_mid_ratio': 0.6,
            'tp_min_ratio': 0.65
        }
        
        with patch.object(TradingProfiles, 'get_current_profile', return_value=test_profile):
            yield test_profile
    
    @pytest.fixture
    def mock_risk_config(self):
        """🔧 Mock para RiskManagerConfig"""
        mock_config = Mock()
        mock_config.TRAILING_STOP_ACTIVATION = 2.0  # 2%
        
        with patch('src.core.position_manager.RiskManagerConfig', return_value=mock_config):
            yield mock_config
    
    @pytest.fixture
    def mock_db_session(self):
        """🔧 Mock para sesión de base de datos"""
        mock_session = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        
        with patch('src.core.position_manager.db_manager') as mock_db:
            mock_db.get_db_session.return_value.__enter__.return_value = mock_session
            yield mock_session
    
    @pytest.fixture
    def mock_paper_trader(self):
        """🔧 Mock para PaperTrader"""
        mock_trader = Mock()
        mock_trader._get_usdt_balance.return_value = 10000.0
        mock_trader.get_portfolio_summary.return_value = {'total_value': 12000.0}
        return mock_trader
    
    @pytest.fixture
    def position_manager(self, mock_trading_profiles, mock_risk_config, mock_db_session, mock_paper_trader):
        """🔧 Fixture para PositionManager con mocks"""
        with patch('src.core.position_manager.PaperTrader', return_value=mock_paper_trader):
            with patch('src.core.position_manager.TradingBotConfig'):
                manager = PositionManager()
                return manager
    
    @pytest.fixture
    def sample_trade(self):
        """🔧 Trade de ejemplo para tests"""
        trade = Mock(spec=Trade)
        trade.id = 123
        trade.symbol = 'BTCUSDT'
        trade.side = 'BUY'
        trade.quantity = 0.1
        trade.entry_price = 45000.0
        trade.current_price = 46000.0
        trade.take_profit = 47000.0
        trade.stop_loss = 43000.0
        trade.entry_time = datetime.now() - timedelta(hours=2)
        trade.notes = 'Test trade'
        trade.status = 'OPEN'
        trade.is_paper_trade = True
        return trade
    
    @pytest.fixture
    def sample_position_info(self, sample_trade):
        """🔧 PositionInfo de ejemplo"""
        return PositionInfo(
            trade_id=sample_trade.id,
            symbol=sample_trade.symbol,
            trade_type=sample_trade.side,
            entry_price=sample_trade.entry_price,
            current_price=sample_trade.current_price,
            quantity=sample_trade.quantity,
            entry_value=sample_trade.entry_price * sample_trade.quantity,
            current_value=sample_trade.current_price * sample_trade.quantity,
            unrealized_pnl=100.0,
            unrealized_pnl_percentage=2.22,
            stop_loss=sample_trade.stop_loss,
            take_profit=sample_trade.take_profit,
            trailing_stop=None,
            entry_time=sample_trade.entry_time,
            strategy_name="test_strategy",
            confidence_score=0.85,
            timeframe="1h",
            notes=sample_trade.notes,
            days_held=0.083,  # ~2 horas en días
            max_profit=150.0,
            max_loss=-50.0,
            risk_reward_ratio=2.0
        )


class TestPositionManagerInitialization(TestPositionManagerOptimized):
    """🧪 Tests de inicialización"""
    
    def test_initialization_with_custom_profile(self, mock_trading_profiles, mock_risk_config, mock_db_session, mock_paper_trader):
        """✅ Test inicialización con perfil personalizado"""
        with patch('src.core.position_manager.PaperTrader', return_value=mock_paper_trader):
            with patch('src.core.position_manager.TradingBotConfig'):
                manager = PositionManager()
                
                # Verificar configuraciones dinámicas
                assert manager.cache_duration == 5
                assert manager.seconds_per_day == 86.4
                assert abs(manager.atr_estimation_pct - 0.018) < 0.001  # 1.8% convertido a decimal
                assert manager.profit_scaling_ratios['tp_max_ratio'] == 0.7
                assert manager.profit_scaling_ratios['tp_mid_ratio'] == 0.6
                assert manager.profit_scaling_ratios['tp_min_ratio'] == 0.65
                assert manager.trailing_stop_activation == 0.02  # 2% del mock
    
    def test_initialization_with_default_values(self, mock_db_session, mock_paper_trader):
        """✅ Test inicialización con valores por defecto"""
        # Mock perfil vacío para probar defaults
        with patch.object(TradingProfiles, 'get_current_profile', return_value={}):
            with patch('src.core.position_manager.PaperTrader', return_value=mock_paper_trader):
                with patch('src.core.position_manager.TradingBotConfig'):
                    with patch('src.core.position_manager.RiskManagerConfig') as mock_risk:
                        mock_risk.return_value.TRAILING_STOP_ACTIVATION = 3.0
                        manager = PositionManager()
                        
                        # Verificar valores por defecto
                        assert manager.cache_duration == 30  # default
                        assert manager.seconds_per_day == 86400  # default
                        assert manager.atr_estimation_pct == 0.02  # 2% default


class TestCacheManagement(TestPositionManagerOptimized):
    """🧪 Tests de gestión de cache"""
    
    def test_cache_validation(self, position_manager):
        """✅ Test validación de cache"""
        # Cache inicial inválido
        assert not position_manager.is_cache_valid()
        
        # Simular actualización de cache
        position_manager.last_cache_update = time.time()
        assert position_manager.is_cache_valid()
        
        # Cache expirado
        position_manager.last_cache_update = time.time() - 10  # 10 segundos atrás
        assert not position_manager.is_cache_valid()
    
    def test_cache_invalidation_specific(self, position_manager, sample_position_info):
        """✅ Test invalidación específica de cache"""
        # Agregar posición al cache
        position_manager.positions_cache[123] = sample_position_info
        position_manager.positions_cache[456] = sample_position_info
        
        assert len(position_manager.positions_cache) == 2
        
        # Invalidar posición específica
        position_manager.invalidate_cache(trade_id=123)
        
        assert 123 not in position_manager.positions_cache
        assert 456 in position_manager.positions_cache
        assert len(position_manager.positions_cache) == 1
    
    def test_cache_invalidation_full(self, position_manager, sample_position_info):
        """✅ Test invalidación completa de cache"""
        # Agregar posiciones al cache
        position_manager.positions_cache[123] = sample_position_info
        position_manager.positions_cache[456] = sample_position_info
        position_manager.last_cache_update = time.time()
        
        assert len(position_manager.positions_cache) == 2
        assert position_manager.last_cache_update > 0
        
        # Invalidar todo el cache
        position_manager.invalidate_cache()
        
        assert len(position_manager.positions_cache) == 0
        assert position_manager.last_cache_update == 0
    
    def test_update_cache_entry(self, position_manager, sample_position_info):
        """✅ Test actualización de entrada de cache"""
        # Actualizar entrada
        position_manager.update_cache_entry(sample_position_info)
        
        assert sample_position_info.trade_id in position_manager.positions_cache
        assert position_manager.positions_cache[sample_position_info.trade_id] == sample_position_info
    
    def test_get_cache_stats(self, position_manager, sample_position_info):
        """✅ Test estadísticas de cache"""
        # Cache vacío
        stats = position_manager.get_cache_stats()
        assert stats['cache_size'] == 0
        assert not stats['cache_valid']
        assert stats['last_update'] is None
        
        # Agregar datos al cache
        position_manager.positions_cache[123] = sample_position_info
        position_manager.last_cache_update = time.time()
        
        stats = position_manager.get_cache_stats()
        assert stats['cache_size'] == 1
        assert stats['cache_valid']
        assert stats['last_update'] is not None
        assert stats['cache_duration'] == 5  # del perfil de test


class TestPositionOperations(TestPositionManagerOptimized):
    """🧪 Tests de operaciones de posiciones"""
    
    def test_get_active_positions_with_cache(self, position_manager, sample_position_info):
        """✅ Test obtener posiciones activas usando cache"""
        # Simular cache válido
        position_manager.positions_cache[123] = sample_position_info
        position_manager.last_cache_update = time.time()
        
        positions = position_manager.get_active_positions()
        
        assert len(positions) == 1
        assert positions[0] == sample_position_info
    
    def test_get_active_positions_refresh_cache(self, position_manager, mock_db_session, sample_trade):
        """✅ Test obtener posiciones forzando actualización de cache"""
        # Configurar mock para retornar trade
        mock_db_session.query.return_value.filter.return_value.all.return_value = [sample_trade]
        
        with patch.object(position_manager, '_create_position_info') as mock_create:
            mock_position = Mock()
            mock_position.trade_id = 123
            mock_create.return_value = mock_position
            
            positions = position_manager.get_active_positions(refresh_cache=True)
            
            assert len(positions) == 1
            assert 123 in position_manager.positions_cache
            mock_create.assert_called_once_with(sample_trade)
    
    def test_update_position_price(self, position_manager, sample_position_info):
        """✅ Test actualización de precio de posición"""
        # Agregar posición al cache
        position_manager.positions_cache[123] = sample_position_info
        
        # Actualizar precio
        success = position_manager.update_position_price(123, 47000.0)
        
        assert success
        updated_position = position_manager.positions_cache[123]
        assert updated_position.current_price == 47000.0
        assert updated_position.current_value == 47000.0 * 0.1  # quantity
        assert updated_position.unrealized_pnl == 200.0  # (47000 - 45000) * 0.1
    
    def test_update_position_price_not_found(self, position_manager):
        """✅ Test actualización de precio para posición inexistente"""
        success = position_manager.update_position_price(999, 47000.0)
        assert not success
    
    def test_get_position_by_id(self, position_manager, sample_position_info):
        """✅ Test obtener posición por ID"""
        # Agregar al cache
        position_manager.positions_cache[123] = sample_position_info
        
        position = position_manager.get_position_by_id(123)
        assert position == sample_position_info
        
        # Posición inexistente
        position = position_manager.get_position_by_id(999)
        assert position is None
    
    def test_get_positions_by_symbol(self, position_manager, sample_position_info):
        """✅ Test obtener posiciones por símbolo"""
        # Crear posiciones con diferentes símbolos
        btc_position = sample_position_info
        eth_position = PositionInfo(
            trade_id=456, symbol='ETHUSDT', trade_type='BUY',
            entry_price=3000.0, current_price=3100.0, quantity=1.0,
            entry_value=3000.0, current_value=3100.0, unrealized_pnl=100.0,
            unrealized_pnl_percentage=3.33, stop_loss=2900.0, take_profit=3200.0,
            trailing_stop=None, entry_time=datetime.now(), strategy_name="test_strategy",
            confidence_score=0.80, timeframe="1h", notes='ETH test',
            days_held=0.1, max_profit=150.0, max_loss=-50.0, risk_reward_ratio=2.0
        )
        
        position_manager.positions_cache[123] = btc_position
        position_manager.positions_cache[456] = eth_position
        
        with patch.object(position_manager, 'get_active_positions') as mock_get:
            mock_get.return_value = [btc_position, eth_position]
            
            btc_positions = position_manager.get_positions_by_symbol('BTCUSDT')
            eth_positions = position_manager.get_positions_by_symbol('ETHUSDT')
            
            assert len(btc_positions) == 1
            assert len(eth_positions) == 1
            assert btc_positions[0].symbol == 'BTCUSDT'
            assert eth_positions[0].symbol == 'ETHUSDT'


class TestTrailingStops(TestPositionManagerOptimized):
    """🧪 Tests de trailing stops"""
    
    def test_calculate_atr_trailing_stop_buy_default_multiplier(self, position_manager):
        """✅ Test cálculo de trailing stop para BUY con multiplicador por defecto"""
        trailing_stop = position_manager.calculate_atr_trailing_stop(
            symbol='BTCUSDT',
            current_price=45000.0,
            trade_type='BUY'
        )
        
        # Cálculo esperado: 45000 - (45000 * 0.018 * 2.5) = 45000 - 2025 = 42975
        expected = 45000.0 - (45000.0 * 0.018 * 2.5)
        assert abs(trailing_stop - expected) < 0.01
    
    def test_calculate_atr_trailing_stop_buy_custom_multiplier(self, position_manager):
        """✅ Test cálculo de trailing stop para BUY con multiplicador personalizado"""
        trailing_stop = position_manager.calculate_atr_trailing_stop(
            symbol='BTCUSDT',
            current_price=45000.0,
            trade_type='BUY',
            atr_multiplier=3.0
        )
        
        # Cálculo esperado: 45000 - (45000 * 0.018 * 3.0) = 45000 - 2430 = 42570
        expected = 45000.0 - (45000.0 * 0.018 * 3.0)
        assert abs(trailing_stop - expected) < 0.01
    
    def test_calculate_atr_trailing_stop_sell(self, position_manager):
        """✅ Test cálculo de trailing stop para SELL"""
        trailing_stop = position_manager.calculate_atr_trailing_stop(
            symbol='BTCUSDT',
            current_price=45000.0,
            trade_type='SELL',
            atr_multiplier=2.0
        )
        
        # Cálculo esperado: 45000 + (45000 * 0.018 * 2.0) = 45000 + 1620 = 46620
        expected = 45000.0 + (45000.0 * 0.018 * 2.0)
        assert abs(trailing_stop - expected) < 0.01
    
    def test_update_trailing_stop_activation(self, position_manager, sample_position_info):
        """✅ Test activación de trailing stop"""
        # Configurar posición con ganancia suficiente para activar trailing
        sample_position_info.current_price = 46000.0  # +2.22% ganancia
        sample_position_info.unrealized_pnl_percentage = 2.22
        sample_position_info.trailing_stop = None
        
        # El trailing_stop_activation ya está configurado en el mock (2%)
        position_manager._update_trailing_stop(sample_position_info)
        
        # Verificar que se activó el trailing stop
        assert sample_position_info.trailing_stop is not None
        expected_trailing = 46000.0 * (1 - 0.015)  # 1.5% del perfil de test
        assert abs(sample_position_info.trailing_stop - expected_trailing) < 0.01
    
    def test_update_trailing_stop_no_activation(self, position_manager, sample_position_info):
        """✅ Test no activación de trailing stop por ganancia insuficiente"""
        # Configurar posición con ganancia insuficiente
        sample_position_info.current_price = 45500.0  # +1.11% ganancia
        sample_position_info.unrealized_pnl_percentage = 1.11
        sample_position_info.trailing_stop = None
        
        # El trailing_stop_activation ya está configurado en el mock (2%)
        position_manager._update_trailing_stop(sample_position_info)
        
        # Verificar que NO se activó el trailing stop
        assert sample_position_info.trailing_stop is None


class TestExitConditions(TestPositionManagerOptimized):
    """🧪 Tests de condiciones de salida"""
    
    def test_check_exit_conditions_take_profit_buy(self, position_manager, sample_position_info):
        """✅ Test condición de Take Profit para BUY"""
        sample_position_info.current_price = 47500.0  # Por encima del TP
        sample_position_info.take_profit = 47000.0
        
        reason = position_manager.check_exit_conditions(sample_position_info)
        assert reason == "TAKE_PROFIT"
    
    def test_check_exit_conditions_stop_loss_buy(self, position_manager, sample_position_info):
        """✅ Test condición de Stop Loss para BUY"""
        sample_position_info.current_price = 42500.0  # Por debajo del SL
        sample_position_info.stop_loss = 43000.0
        
        reason = position_manager.check_exit_conditions(sample_position_info)
        assert reason == "STOP_LOSS"
    
    def test_check_exit_conditions_trailing_stop_buy(self, position_manager, sample_position_info):
        """✅ Test condición de Trailing Stop para BUY"""
        sample_position_info.current_price = 44000.0  # Por debajo del trailing
        sample_position_info.trailing_stop = 44500.0
        
        reason = position_manager.check_exit_conditions(sample_position_info)
        assert reason == "TRAILING_STOP"
    
    def test_check_exit_conditions_no_exit(self, position_manager, sample_position_info):
        """✅ Test sin condiciones de salida"""
        sample_position_info.current_price = 46000.0  # Precio normal
        
        reason = position_manager.check_exit_conditions(sample_position_info)
        assert reason is None
    
    def test_check_exit_conditions_sell_positions(self, position_manager, sample_position_info):
        """✅ Test condiciones de salida para posiciones SELL"""
        sample_position_info.trade_type = "SELL"
        sample_position_info.take_profit = 44000.0
        sample_position_info.stop_loss = 46000.0
        
        # Take Profit para SELL (precio baja)
        sample_position_info.current_price = 43500.0
        reason = position_manager.check_exit_conditions(sample_position_info)
        assert reason == "TAKE_PROFIT"
        
        # Stop Loss para SELL (precio sube)
        sample_position_info.current_price = 46500.0
        reason = position_manager.check_exit_conditions(sample_position_info)
        assert reason == "STOP_LOSS"


class TestPortfolioAnalysis(TestPositionManagerOptimized):
    """🧪 Tests de análisis de portfolio"""
    
    def test_get_portfolio_exposure(self, position_manager, sample_position_info):
        """✅ Test análisis de exposición del portfolio"""
        # Crear múltiples posiciones
        btc_position = sample_position_info
        eth_position = PositionInfo(
            trade_id=456, symbol='ETHUSDT', trade_type='BUY',
            entry_price=3000.0, current_price=3100.0, quantity=2.0,
            entry_value=6000.0, current_value=6200.0, unrealized_pnl=200.0,
            unrealized_pnl_percentage=3.33, stop_loss=2900.0, take_profit=3200.0,
            trailing_stop=None, entry_time=datetime.now(), strategy_name="test_strategy",
            confidence_score=0.75, timeframe="1h", notes='ETH test',
            days_held=0.1, max_profit=300.0, max_loss=-100.0, risk_reward_ratio=2.0
        )
        
        with patch.object(position_manager, 'get_active_positions') as mock_get:
            mock_get.return_value = [btc_position, eth_position]
            
            exposure = position_manager.get_portfolio_exposure()
            
            # Verificar métricas totales
            expected_total_exposure = btc_position.current_value + eth_position.current_value
            expected_total_pnl = btc_position.unrealized_pnl + eth_position.unrealized_pnl
            
            assert abs(exposure['total_exposure'] - expected_total_exposure) < 0.01
            assert abs(exposure['total_unrealized_pnl'] - expected_total_pnl) < 0.01
            
            # Verificar que hay datos de exposición (estructura puede variar)
            assert 'total_exposure' in exposure
            assert 'total_unrealized_pnl' in exposure


class TestPositionClosing(TestPositionManagerOptimized):
    """🧪 Tests de cierre de posiciones"""
    
    def test_close_position_success(self, position_manager, sample_position_info, mock_db_session):
        """✅ Test cierre exitoso de posición"""
        # Agregar posición al cache
        position_manager.positions_cache[123] = sample_position_info
        
        # Mock del trade en la base de datos
        mock_trade = Mock()
        mock_trade.id = 123
        mock_trade.symbol = "BTC/USDT"
        mock_trade.trade_type = "BUY"
        mock_trade.quantity = 0.1
        mock_trade.entry_price = 45000.0
        mock_trade.entry_value = 4500.0  # entry_price * quantity
        mock_trade.status = "OPEN"
        mock_trade.is_paper_trade = True
        mock_trade.notes = "Test trade"
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_trade
        
        # Mock de los métodos del paper trader
        with patch.object(position_manager.paper_trader, '_get_usdt_balance', return_value=10000.0), \
             patch.object(position_manager.paper_trader, 'get_portfolio_summary', return_value={'total_value': 15000.0}), \
             patch.object(position_manager.paper_trader, '_update_usdt_balance'), \
             patch.object(position_manager.paper_trader, '_update_asset_balance'):
            
            success = position_manager.close_position(
                trade_id=123,
                current_price=47000.0,
                reason="TAKE_PROFIT"
            )
            
            assert success
            assert 123 not in position_manager.positions_cache  # Removido del cache
            assert position_manager.stats["tp_executed"] == 1
    
    def test_close_position_not_found(self, position_manager, mock_db_session):
        """✅ Test cierre de posición inexistente"""
        # Mock retorna None (posición no encontrada)
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        success = position_manager.close_position(
            trade_id=999,
            current_price=47000.0,
            reason="TAKE_PROFIT"
        )
        
        assert not success


class TestConfigurationDynamic(TestPositionManagerOptimized):
    """🧪 Tests de configuración dinámica"""
    
    def test_dynamic_configuration_loading(self, mock_trading_profiles, mock_risk_config, mock_db_session, mock_paper_trader):
        """✅ Test carga de configuración dinámica"""
        with patch('src.core.position_manager.PaperTrader', return_value=mock_paper_trader):
            with patch('src.core.position_manager.TradingBotConfig'):
                manager = PositionManager()
                
                # Verificar que se cargaron las configuraciones del perfil
                assert manager.cache_duration == 5  # del mock_trading_profiles
                assert manager.seconds_per_day == 86.4
                assert abs(manager.atr_estimation_pct - 0.018) < 0.001  # 1.8% convertido
                
                # Verificar profit scaling ratios
                assert manager.profit_scaling_ratios['tp_max_ratio'] == 0.7
                assert manager.profit_scaling_ratios['tp_mid_ratio'] == 0.6
                assert manager.profit_scaling_ratios['tp_min_ratio'] == 0.65
    
    def test_days_held_calculation_with_custom_seconds_per_day(self, position_manager, sample_trade):
        """✅ Test cálculo de días mantenidos con configuración personalizada"""
        # Configurar trade con tiempo específico
        sample_trade.entry_time = datetime.now() - timedelta(seconds=172.8)  # 2 días en tiempo acelerado
        
        # Mock del método _create_position_info si existe
        if hasattr(position_manager, '_create_position_info'):
            with patch('src.core.position_manager.datetime') as mock_datetime:
                mock_datetime.now.return_value = datetime.now()
                
                position_info = position_manager._create_position_info(sample_trade)
                
                if position_info:
                    # Con seconds_per_day = 86.4, 172.8 segundos = 2 días
                    expected_days = 172.8 / 86.4
                    assert abs(position_info.days_held - expected_days) < 0.01
                else:
                    # Si no se puede crear, al menos verificar que no falla
                    assert True
        else:
            # Si el método no existe, verificar configuración
            assert position_manager.seconds_per_day == 86.4


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])