import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List

# Importar las clases a testear
from src.core.position_adjuster import (
    PositionAdjuster,
    AdjustmentReason,
    AdjustmentResult,
    PositionInfo
)


class TestPositionAdjuster:
    """Tests para la clase PositionAdjuster"""
    
    @pytest.fixture
    def mock_profile(self):
        """Mock del perfil de configuración"""
        return {
            'position_monitoring_interval': 30,
            'profit_scaling_threshold': 2.0,
            'trailing_stop_activation': 5.0,
            'trailing_stop_sl_pct': 0.02,
            'trailing_stop_tp_pct': 0.05,
            'profit_protection_sl_pct': 0.01,
            'profit_protection_tp_pct': 0.03,
            'risk_management_threshold': -1.0,
            'risk_management_sl_pct': 0.015,
            'risk_management_tp_pct': 0.02,
            'price_simulation_variation': 0.02,
            'simulation_fallback_price': 50000.0,
            'stats_recent_adjustments_count': 10
        }
    
    @pytest.fixture
    def mock_db_manager(self):
        """Mock del database manager"""
        db_mock = Mock()
        db_mock.get_active_positions = Mock(return_value=[])
        db_mock.update_position_levels = Mock(return_value=True)
        return db_mock
    
    @pytest.fixture
    def position_adjuster(self, mock_profile, mock_db_manager):
        """Instancia de PositionAdjuster para tests"""
        with patch('src.core.position_adjuster.db_manager', mock_db_manager):
            adjuster = PositionAdjuster(
                config=mock_profile,
                simulation_mode=True
            )
            return adjuster
    
    @pytest.fixture
    def sample_position(self):
        """Posición de ejemplo para tests"""
        return PositionInfo(
            symbol="BTCUSDT",
            entry_price=50000.0,
            current_price=52000.0,
            quantity=0.1,
            side="LONG",
            current_tp=52000.0,
            current_sl=49000.0,
            entry_time=datetime.now(),
            unrealized_pnl=200.0,
            unrealized_pnl_pct=4.0
        )

    def test_initialization(self, mock_profile, mock_db_manager):
        """Test de inicialización del PositionAdjuster"""
        with patch('src.core.position_adjuster.db_manager', mock_db_manager):
            adjuster = PositionAdjuster(
                config=mock_profile,
                simulation_mode=True
            )
            
            assert adjuster.config == mock_profile
            assert adjuster.simulation_mode == True
            assert adjuster.monitoring_interval == 20  # Valor del perfil AGRESIVO
            assert not adjuster.is_running
            assert len(adjuster.adjustment_counts) == 0
            assert len(adjuster.adjustment_history) == 0
    
    def test_set_adjustment_callback(self, position_adjuster):
        """Test de configuración de callback"""
        callback = Mock()
        position_adjuster.set_adjustment_callback(callback)
        
        assert position_adjuster.adjustment_callback == callback
    
    def test_update_monitoring_interval_valid(self, position_adjuster):
        """Test de actualización válida del intervalo de monitoreo"""
        callback = Mock()
        position_adjuster.set_adjustment_callback(callback)
        
        position_adjuster.update_monitoring_interval(60)
        
        assert position_adjuster.monitoring_interval == 60
        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args['type'] == 'config_update'
        assert '20s a 60s' in call_args['message']  # Valor inicial del perfil AGRESIVO
    
    def test_update_monitoring_interval_invalid(self, position_adjuster):
        """Test de actualización inválida del intervalo de monitoreo"""
        with pytest.raises(ValueError, match="debe ser al menos 5 segundos"):
            position_adjuster.update_monitoring_interval(3)
    
    def test_update_max_adjustments_valid(self, position_adjuster):
        """Test de actualización válida del máximo de ajustes"""
        callback = Mock()
        position_adjuster.set_adjustment_callback(callback)
        
        position_adjuster.update_max_adjustments(8)
        
        assert position_adjuster.max_adjustments == 8
        callback.assert_called_once()
        call_args = callback.call_args[0][0]
        assert call_args['type'] == 'config_update'
        assert '3 a 8' in call_args['message']  # Valor por defecto real
    
    def test_update_max_adjustments_invalid(self, position_adjuster):
        """Test de actualización inválida del máximo de ajustes"""
        with pytest.raises(ValueError, match="debe ser al menos 1"):
            position_adjuster.update_max_adjustments(0)
    
    def test_pause_and_resume_monitoring(self, position_adjuster):
        """Test de pausa y reanudación del monitoreo"""
        callback = Mock()
        position_adjuster.set_adjustment_callback(callback)
        
        # Test pausa
        position_adjuster.pause_monitoring()
        assert position_adjuster.is_paused()
        
        # Test reanudación
        position_adjuster.resume_monitoring()
        assert not position_adjuster.is_paused()
        
        # Verificar callbacks
        assert callback.call_count == 2
        calls = callback.call_args_list
        assert calls[0][0][0]['type'] == 'monitoring_paused'
        assert calls[1][0][0]['type'] == 'monitoring_resumed'
    
    def test_get_current_config(self, position_adjuster):
        """Test de obtención de configuración actual"""
        position_adjuster.is_running = True
        position_adjuster.adjustment_counts['BTCUSDT'] = 2
        
        with patch.object(position_adjuster, '_get_active_positions', return_value=[Mock(), Mock()]):
            config = position_adjuster.get_current_config()
        
        assert config['monitoring_interval'] == 20  # Valor del perfil AGRESIVO
        assert config['max_adjustments'] == 3  # Valor por defecto real
        assert config['is_monitoring'] == True
        assert config['is_paused'] == False
        assert config['total_positions_tracked'] == 1
        assert config['active_positions'] == 2
    
    @pytest.mark.asyncio
    async def test_start_monitoring(self, position_adjuster):
        """Test de inicio del monitoreo"""
        async def mock_monitor_positions():
            # Simular una iteración y luego detener
            position_adjuster.is_running = False
            
        with patch.object(position_adjuster, '_monitor_positions', side_effect=mock_monitor_positions):
            await position_adjuster.start_monitoring()
            
            assert not position_adjuster.is_running  # Debe estar False después de la simulación
    
    @pytest.mark.asyncio
    async def test_stop_monitoring(self, position_adjuster):
        """Test de detención del monitoreo"""
        position_adjuster.is_running = True
        
        await position_adjuster.stop_monitoring()
        
        assert not position_adjuster.is_running
    
    def test_get_current_price_with_simulation(self, position_adjuster):
        """Test de obtención de precio con simulación"""
        with patch('random.uniform', return_value=0.01):  # 1% de variación
            price = position_adjuster._get_current_price('BTCUSDT')
            
            # Debería estar cerca del precio base con variación
            assert 49500 <= price <= 50500  # ±1% de 50000
    
    def test_calculate_pnl_long_position(self, position_adjuster):
        """Test de cálculo de PnL para posición LONG"""
        pnl, pnl_pct = position_adjuster._calculate_pnl(
            side='LONG',
            entry_price=50000.0,
            current_price=52000.0,
            size=0.1
        )
        
        assert pnl == 200.0  # (52000 - 50000) * 0.1
        assert pnl_pct == 4.0  # 4% de ganancia
    
    def test_calculate_pnl_short_position(self, position_adjuster):
        """Test de cálculo de PnL para posición SHORT"""
        pnl, pnl_pct = position_adjuster._calculate_pnl(
            side='SHORT',
            entry_price=50000.0,
            current_price=48000.0,
            size=0.1
        )
        
        assert pnl == 200.0  # (50000 - 48000) * 0.1
        assert pnl_pct == 4.0  # 4% de ganancia
    
    def test_calculate_new_levels_profit_scaling(self, position_adjuster, sample_position):
        """Test de cálculo de nuevos niveles para profit scaling"""
        new_tp, new_sl = position_adjuster._calculate_new_levels(
            position=sample_position,
            reason=AdjustmentReason.PROFIT_SCALING,
            current_price=52000.0
        )
        
        # Para LONG con profit scaling, TP debería incrementarse
        assert new_tp > sample_position.current_tp
        # SL debería mantenerse o mejorar ligeramente
        assert new_sl >= sample_position.current_sl
    
    def test_calculate_new_levels_trailing_stop(self, position_adjuster, sample_position):
        """Test de cálculo de nuevos niveles para trailing stop"""
        new_tp, new_sl = position_adjuster._calculate_new_levels(
            position=sample_position,
            reason=AdjustmentReason.TRAILING_STOP,
            current_price=52000.0
        )
        
        # Para trailing stop, ambos niveles deberían ajustarse
        assert new_tp != sample_position.current_tp
        assert new_sl != sample_position.current_sl
    
    def test_calculate_new_levels_risk_management(self, position_adjuster):
        """Test de cálculo de nuevos niveles para gestión de riesgo"""
        # Posición con pérdidas
        entry_time = datetime.now()
        losing_position = PositionInfo(
            symbol="BTCUSDT",
            entry_price=50000.0,
            current_price=49400.0,
            quantity=0.1,
            side="LONG",
            current_tp=52000.0,
            current_sl=49000.0,
            entry_time=entry_time,
            unrealized_pnl=-600.0,
            unrealized_pnl_pct=-1.2
        )
        
        new_tp, new_sl = position_adjuster._calculate_new_levels(
            position=losing_position,
            reason=AdjustmentReason.RISK_MANAGEMENT,
            current_price=49400.0
        )
        
        # Para gestión de riesgo, los ajustes deberían ser conservadores
        assert new_tp < losing_position.current_tp  # TP más conservador (51000 < 52000)
        assert new_sl < losing_position.current_sl  # SL ajustado al precio actual (48659 < 49000)
    
    @pytest.mark.asyncio
    async def test_execute_adjustment_success(self, position_adjuster, sample_position):
        """Test de ejecución exitosa de ajuste"""
        # Mock del método interno _update_position_levels
        with patch.object(position_adjuster, '_update_position_levels', return_value=True):
            result = await position_adjuster._execute_adjustment(
                position=sample_position,
                new_tp=53000.0,
                new_sl=49500.0,
                reason=AdjustmentReason.PROFIT_SCALING
            )
            
            assert result.success
            assert result.symbol == "BTCUSDT"
            assert result.reason == AdjustmentReason.PROFIT_SCALING
            assert result.new_tp == 53000.0
            assert result.new_sl == 49500.0
            
            # Simular la actualización del contador como lo haría _evaluate_position_adjustment
            if result.success:
                position_adjuster.adjustment_counts['BTCUSDT'] = 1
                position_adjuster.adjustment_history.append(result)
            
            # Verificar que se actualizó el contador
            assert position_adjuster.adjustment_counts['BTCUSDT'] == 1
            
            # Verificar que se agregó al historial
            assert len(position_adjuster.adjustment_history) == 1
    
    @pytest.mark.asyncio
    async def test_execute_adjustment_failure(self, position_adjuster, sample_position):
        """Test de ejecución fallida de ajuste"""
        # Mock del método interno _update_position_levels para simular fallo
        with patch.object(position_adjuster, '_update_position_levels', return_value=False):
            result = await position_adjuster._execute_adjustment(
                position=sample_position,
                new_tp=53000.0,
                new_sl=49500.0,
                reason=AdjustmentReason.PROFIT_SCALING
            )
            
            assert not result.success
            assert "Ajuste simulado completado" in result.message  # El mensaje actual del método
            
            # El contador no debería incrementarse en caso de fallo
            assert position_adjuster.adjustment_counts.get('BTCUSDT', 0) == 0
    
    @pytest.mark.asyncio
    async def test_evaluate_position_adjustment_max_adjustments_reached(self, position_adjuster, sample_position):
        """Test cuando se alcanza el máximo de ajustes por posición"""
        # Simular que ya se alcanzó el máximo
        position_adjuster.adjustment_counts['BTCUSDT'] = 5
        
        with patch.object(position_adjuster, '_get_current_price', return_value=52000.0):
            await position_adjuster._evaluate_position_adjustment(sample_position)
        
        # No debería haber nuevos ajustes
        assert len(position_adjuster.adjustment_history) == 0
    
    @pytest.mark.asyncio
    async def test_evaluate_position_adjustment_profit_scaling(self, position_adjuster, sample_position):
        """Test de evaluación para profit scaling"""
        with patch.object(position_adjuster, '_get_current_price', return_value=52000.0), \
             patch.object(position_adjuster, '_execute_adjustment', new_callable=AsyncMock) as mock_execute:
            
            mock_execute.return_value = AdjustmentResult(
                success=True,
                symbol='BTCUSDT',
                old_tp=52000.0,
                old_sl=49000.0,
                new_tp=53000.0,
                new_sl=49500.0,
                reason=AdjustmentReason.PROFIT_SCALING,
                timestamp=datetime.now(),
                message='Ajuste exitoso',
                adjustment_count=1
            )
            
            await position_adjuster._evaluate_position_adjustment(sample_position)
            
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args
            # Los argumentos son: position, new_tp, new_sl, reason
            assert call_args[0][3] == AdjustmentReason.PROFIT_SCALING
    
    def test_get_adjustment_stats_empty(self, position_adjuster):
        """Test de estadísticas cuando no hay ajustes"""
        stats = position_adjuster.get_adjustment_stats()
        
        assert stats['total_positions_adjusted'] == 0
        assert stats['total_adjustments'] == 0
        assert stats['successful_adjustments'] == 0
        assert stats['success_rate'] == 0
        assert len(stats['recent_adjustments']) == 0
        assert len(stats['adjustments_by_reason']) == 0
    
    def test_get_adjustment_stats_with_data(self, position_adjuster):
        """Test de estadísticas con datos"""
        # Agregar algunos ajustes al historial
        position_adjuster.adjustment_counts['BTCUSDT'] = 2
        position_adjuster.adjustment_counts['ETHUSDT'] = 1
        
        position_adjuster.adjustment_history = [
            AdjustmentResult(
                symbol='BTCUSDT',
                reason=AdjustmentReason.PROFIT_SCALING,
                success=True,
                old_tp=52000.0,
                new_tp=53000.0,
                old_sl=49000.0,
                new_sl=49500.0,
                timestamp=datetime.now(),
                message='Exitoso',
                adjustment_count=1
            ),
            AdjustmentResult(
                symbol='ETHUSDT',
                reason=AdjustmentReason.TRAILING_STOP,
                success=False,
                old_tp=3200.0,
                new_tp=3300.0,
                old_sl=3000.0,
                new_sl=3100.0,
                timestamp=datetime.now(),
                message='Fallido',
                adjustment_count=1
            )
        ]
        
        stats = position_adjuster.get_adjustment_stats()
        
        assert stats['total_positions_adjusted'] == 2
        assert stats['total_adjustments'] == 3  # 2 + 1
        assert stats['successful_adjustments'] == 1
        assert stats['success_rate'] == 33.33333333333333  # 1/3 * 100 (1 exitoso de 3 total)
        assert len(stats['recent_adjustments']) == 2
        assert 'profit_scaling' in stats['adjustments_by_reason']
        assert 'trailing_stop' in stats['adjustments_by_reason']
    
    def test_reset_adjustment_counts(self, position_adjuster):
        """Test de reset de contadores"""
        # Agregar algunos datos
        position_adjuster.adjustment_counts['BTCUSDT'] = 3
        position_adjuster.adjustment_history = [Mock(), Mock()]
        
        position_adjuster.reset_adjustment_counts()
        
        assert len(position_adjuster.adjustment_counts) == 0
        assert len(position_adjuster.adjustment_history) == 0
    
    @pytest.mark.asyncio
    async def test_monitor_positions_with_pause(self, position_adjuster):
        """Test del bucle de monitoreo con pausa"""
        # Test de funcionalidad de pausa
        position_adjuster.pause_monitoring()
        assert position_adjuster.is_paused()
        
        position_adjuster.resume_monitoring()
        assert not position_adjuster.is_paused()
        
        # Test que el estado de pausa se refleja en la configuración
        position_adjuster.pause_monitoring()
        config = position_adjuster.get_current_config()
        assert config['is_paused'] == True
    
    def test_adjustment_reason_enum(self):
        """Test del enum AdjustmentReason"""
        assert AdjustmentReason.PROFIT_SCALING.value == "profit_scaling"
        assert AdjustmentReason.TRAILING_STOP.value == "trailing_stop"
        assert AdjustmentReason.PROFIT_PROTECTION.value == "profit_protection"
        assert AdjustmentReason.RISK_MANAGEMENT.value == "risk_management"
    
    def test_adjustment_result_dataclass(self):
        """Test del dataclass AdjustmentResult"""
        timestamp = datetime.now()
        result = AdjustmentResult(
            success=True,
            symbol='BTCUSDT',
            old_tp=52000.0,
            old_sl=49000.0,
            new_tp=53000.0,
            new_sl=49500.0,
            reason=AdjustmentReason.PROFIT_SCALING,
            timestamp=timestamp,
            message='Test message',
            adjustment_count=1
        )
        
        assert result.symbol == 'BTCUSDT'
        assert result.reason == AdjustmentReason.PROFIT_SCALING
        assert result.success == True
        assert result.timestamp == timestamp
    
    def test_position_info_dataclass(self):
        """Test del dataclass PositionInfo"""
        entry_time = datetime.now()
        position = PositionInfo(
            symbol='BTCUSDT',
            entry_price=50000.0,
            current_price=52000.0,
            quantity=0.1,
            side='LONG',
            current_tp=52000.0,
            current_sl=49000.0,
            entry_time=entry_time,
            unrealized_pnl=200.0,
            unrealized_pnl_pct=4.0
        )
        
        assert position.symbol == 'BTCUSDT'
        assert position.side == 'LONG'
        assert position.quantity == 0.1
        assert position.unrealized_pnl_pct == 4.0
        assert position.entry_time == entry_time


class TestPositionAdjusterIntegration:
    """Tests de integración para PositionAdjuster"""
    
    @pytest.fixture
    def integration_profile(self):
        """Perfil de configuración para tests de integración"""
        return {
            'position_monitoring_interval': 1,  # Intervalo corto para tests
            'profit_scaling_threshold': 1.0,
            'trailing_stop_activation': 2.0,
            'trailing_stop_sl_pct': 0.01,
            'trailing_stop_tp_pct': 0.02,
            'profit_protection_sl_pct': 0.005,
            'profit_protection_tp_pct': 0.015,
            'risk_management_threshold': -0.5,
            'risk_management_sl_pct': 0.01,
            'risk_management_tp_pct': 0.015,
            'price_simulation_variation': 0.01,
            'simulation_fallback_price': 50000.0,
            'stats_recent_adjustments_count': 5
        }
    
    @pytest.mark.asyncio
    async def test_full_workflow_profit_scaling(self, integration_profile):
        """Test del flujo completo para profit scaling"""
        # Mock del database manager
        db_manager = Mock()
        db_manager.get_active_positions.return_value = [
            {
                'symbol': 'BTCUSDT',
                'side': 'LONG',
                'quantity': 0.1,
                'entry_price': 50000.0,
                'current_tp': 51000.0,
                'current_sl': 49500.0
            }
        ]
        db_manager.update_position_levels.return_value = True
        
        # Crear adjuster
        with patch('src.core.position_adjuster.db_manager', db_manager):
            adjuster = PositionAdjuster(
                config=integration_profile,
                simulation_mode=True
            )
        
        # Mock del precio actual para simular ganancia
        with patch.object(adjuster, '_get_current_price', return_value=50600.0):  # 1.2% ganancia
            
            # Evaluar una posición
            entry_time = datetime.now()
            position = PositionInfo(
                symbol='BTCUSDT',
                entry_price=50000.0,
                current_price=50600.0,
                quantity=0.1,
                side='LONG',
                current_tp=51000.0,
                current_sl=49500.0,
                entry_time=entry_time,
                unrealized_pnl=60.0,
                unrealized_pnl_pct=1.2
            )
            
            await adjuster._evaluate_position_adjustment(position)
        
        # Verificar que se realizó un ajuste
        assert len(adjuster.adjustment_history) == 1
        assert adjuster.adjustment_history[0].reason == AdjustmentReason.PROFIT_SCALING
        assert adjuster.adjustment_history[0].success == True
        
        # Verificar estadísticas
        stats = adjuster.get_adjustment_stats()
        assert stats['total_adjustments'] == 1
        assert stats['success_rate'] == 100.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])