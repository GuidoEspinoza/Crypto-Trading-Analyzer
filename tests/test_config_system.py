"""🧪 Tests para el Sistema de Configuración Centralizada
Tests comprehensivos para validar el funcionamiento del sistema de configuración.

Desarrollado por: Experto en Trading & Programación
"""

import pytest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.config import (
    TechnicalConfig,
    TradingProfile,
    ConfigFactory,
    get_config_factory,
    AdaptiveConfigManager,
    MarketCondition,
    PerformanceMetrics,
    AdaptationRule,
    get_adaptive_manager
)

class TestTechnicalConfig:
    """Tests para TechnicalConfig"""
    
    def test_technical_config_creation(self):
        """Test creación de configuración técnica"""
        config = TechnicalConfig()
        
        assert config.strategy is not None
        assert config.risk is not None
        assert config.volume is not None
        assert config.rsi is not None
        assert config.macd is not None
        assert config.bollinger is not None
        
        # Verificar valores por defecto
        assert config.strategy.base_confidence == 0.5
        assert config.risk.max_position_size == 0.1
        assert config.rsi.period == 14
    
    def test_technical_config_validation(self):
        """Test validación de configuración técnica"""
        config = TechnicalConfig()
        
        # Test valores válidos
        config.strategy.base_confidence = 0.8
        assert config.strategy.base_confidence == 0.8
        
        # Test valores límite
        config.risk.max_position_size = 0.05
        assert config.risk.max_position_size == 0.05

class TestConfigFactory:
    """Tests para ConfigFactory"""
    
    def test_config_factory_singleton(self):
        """Test patrón singleton del factory"""
        factory1 = get_config_factory()
        factory2 = get_config_factory()
        
        assert factory1 is factory2
    
    def test_config_factory_profiles(self):
        """Test configuraciones por perfil"""
        factory = get_config_factory()
        
        # Test todos los perfiles
        for profile in TradingProfile:
            config = factory.get_config(profile)
            assert isinstance(config, TechnicalConfig)
            assert config is not None
    
    def test_config_factory_conservative_profile(self):
        """Test configuración conservadora"""
        factory = get_config_factory()
        config = factory.get_config(TradingProfile.CONSERVATIVE)
        
        # Verificar características conservadoras
        assert config.strategy.min_confidence_threshold >= 0.6
        assert config.risk.max_position_size <= 0.08
        assert config.risk.stop_loss_percentage <= 0.025
    
    def test_config_factory_aggressive_profile(self):
        """Test configuración agresiva"""
        factory = get_config_factory()
        config = factory.get_config(TradingProfile.AGGRESSIVE)
        
        # Verificar características agresivas
        assert config.strategy.min_confidence_threshold <= 0.6
        assert config.risk.max_position_size >= 0.08
        assert config.risk.take_profit_percentage >= 0.03

class TestAdaptiveConfigManager:
    """Tests para AdaptiveConfigManager"""
    
    @pytest.fixture
    def mock_config_factory(self):
        """Mock del config factory"""
        factory = Mock(spec=ConfigFactory)
        factory.get_config.return_value = TechnicalConfig()
        return factory
    
    @pytest.fixture
    def adaptive_manager(self, mock_config_factory):
        """Fixture del adaptive manager"""
        return AdaptiveConfigManager(mock_config_factory)
    
    def test_adaptive_manager_initialization(self, adaptive_manager):
        """Test inicialización del adaptive manager"""
        assert adaptive_manager.current_profile == TradingProfile.MODERATE
        assert adaptive_manager.adaptation_enabled == True
        assert len(adaptive_manager.adaptation_rules) > 0
        assert adaptive_manager.min_trades_for_adaptation == 10
    
    def test_market_condition_analysis(self, adaptive_manager):
        """Test análisis de condiciones de mercado"""
        # Test alta volatilidad
        market_data = {
            'volatility': 0.05,
            'trend_strength': 0.8,
            'momentum': 0.8,
            'price_change_24h': 0.1
        }
        
        conditions = adaptive_manager.analyze_market_conditions(market_data)
        
        assert MarketCondition.HIGH_VOLATILITY in conditions
        assert MarketCondition.TRENDING in conditions
        assert MarketCondition.BULL_MARKET in conditions
    
    def test_market_condition_analysis_bear(self, adaptive_manager):
        """Test análisis de mercado bajista"""
        market_data = {
            'volatility': 0.01,
            'trend_strength': 0.2,
            'momentum': 0.2,
            'price_change_24h': -0.08
        }
        
        conditions = adaptive_manager.analyze_market_conditions(market_data)
        
        assert MarketCondition.LOW_VOLATILITY in conditions
        assert MarketCondition.RANGING in conditions
        assert MarketCondition.BEAR_MARKET in conditions
    
    def test_performance_metrics_update(self, adaptive_manager):
        """Test actualización de métricas de rendimiento"""
        metrics = PerformanceMetrics(
            win_rate=0.65,
            profit_factor=1.8,
            sharpe_ratio=1.2,
            max_drawdown=0.15,
            avg_trade_duration=4.5,
            total_trades=25,
            last_updated=datetime.now()
        )
        
        adaptive_manager.update_performance_metrics(metrics)
        
        assert len(adaptive_manager.performance_history) == 1
        assert adaptive_manager.performance_history[0] == metrics
    
    def test_should_adapt_conditions(self, adaptive_manager):
        """Test condiciones para adaptación"""
        # Sin métricas - no debe adaptar
        assert not adaptive_manager.should_adapt([MarketCondition.HIGH_VOLATILITY])
        
        # Con pocas trades - no debe adaptar
        metrics = PerformanceMetrics(
            win_rate=0.65, profit_factor=1.8, sharpe_ratio=1.2,
            max_drawdown=0.15, avg_trade_duration=4.5,
            total_trades=5, last_updated=datetime.now()
        )
        adaptive_manager.update_performance_metrics(metrics)
        assert not adaptive_manager.should_adapt([MarketCondition.HIGH_VOLATILITY])
        
        # Con suficientes trades - debe adaptar
        metrics.total_trades = 15
        adaptive_manager.update_performance_metrics(metrics)
        assert adaptive_manager.should_adapt([MarketCondition.HIGH_VOLATILITY])
    
    def test_adaptation_cooldown(self, adaptive_manager):
        """Test cooldown de adaptación"""
        # Simular adaptación reciente
        adaptive_manager.last_adaptation_time = datetime.now() - timedelta(hours=2)
        
        metrics = PerformanceMetrics(
            win_rate=0.65, profit_factor=1.8, sharpe_ratio=1.2,
            max_drawdown=0.15, avg_trade_duration=4.5,
            total_trades=15, last_updated=datetime.now()
        )
        adaptive_manager.update_performance_metrics(metrics)
        
        # No debe adaptar por cooldown
        assert not adaptive_manager.should_adapt([MarketCondition.HIGH_VOLATILITY])
        
        # Después del cooldown debe adaptar
        adaptive_manager.last_adaptation_time = datetime.now() - timedelta(hours=5)
        assert adaptive_manager.should_adapt([MarketCondition.HIGH_VOLATILITY])
    
    def test_configuration_adaptation(self, adaptive_manager):
        """Test adaptación de configuración"""
        # Configurar métricas suficientes
        metrics = PerformanceMetrics(
            win_rate=0.65, profit_factor=1.8, sharpe_ratio=1.2,
            max_drawdown=0.15, avg_trade_duration=4.5,
            total_trades=15, last_updated=datetime.now()
        )
        adaptive_manager.update_performance_metrics(metrics)
        
        # Test adaptación a conservador por alta volatilidad
        original_profile = adaptive_manager.current_profile
        new_profile = adaptive_manager.adapt_configuration([MarketCondition.HIGH_VOLATILITY])
        
        if new_profile:
            assert new_profile == TradingProfile.CONSERVATIVE
            assert len(adaptive_manager.adaptation_history) > 0
    
    def test_adaptation_summary(self, adaptive_manager):
        """Test resumen de adaptaciones"""
        summary = adaptive_manager.get_adaptation_summary()
        
        assert 'current_profile' in summary
        assert 'adaptation_enabled' in summary
        assert 'total_adaptations' in summary
        assert 'performance_history_count' in summary
        assert 'active_rules' in summary
        
        assert summary['current_profile'] == TradingProfile.MODERATE.value
        assert summary['adaptation_enabled'] == True

class TestAdaptationRules:
    """Tests para reglas de adaptación"""
    
    def test_adaptation_rule_creation(self):
        """Test creación de reglas de adaptación"""
        rule = AdaptationRule(
            condition=MarketCondition.HIGH_VOLATILITY,
            min_performance_threshold=0.6,
            target_profile=TradingProfile.CONSERVATIVE,
            confidence_adjustment=-10.0,
            risk_adjustment=-0.5
        )
        
        assert rule.condition == MarketCondition.HIGH_VOLATILITY
        assert rule.target_profile == TradingProfile.CONSERVATIVE
        assert rule.enabled == True
    
    def test_adaptation_rule_validation(self):
        """Test validación de reglas"""
        rule = AdaptationRule(
            condition=MarketCondition.BULL_MARKET,
            min_performance_threshold=0.7,
            target_profile=TradingProfile.AGGRESSIVE,
            confidence_adjustment=5.0,
            risk_adjustment=0.3
        )
        
        # Verificar valores válidos
        assert 0.0 <= rule.min_performance_threshold <= 1.0
        assert -50.0 <= rule.confidence_adjustment <= 50.0
        assert -1.0 <= rule.risk_adjustment <= 1.0

class TestConfigPersistence:
    """Tests para persistencia de configuración"""
    
    def test_config_save_load(self):
        """Test guardado y carga de configuración"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "test_config.json")
            
            # Crear configuración de prueba
            original_data = {
                'current_profile': TradingProfile.AGGRESSIVE.value,
                'adaptation_history': [
                    {
                        'timestamp': datetime.now().isoformat(),
                        'from_profile': 'BALANCED',
                        'to_profile': 'AGGRESSIVE'
                    }
                ]
            }
            
            # Guardar
            with open(config_file, 'w') as f:
                json.dump(original_data, f)
            
            # Cargar y verificar
            with open(config_file, 'r') as f:
                loaded_data = json.load(f)
            
            assert loaded_data['current_profile'] == TradingProfile.AGGRESSIVE.value
            assert len(loaded_data['adaptation_history']) == 1

class TestIntegration:
    """Tests de integración del sistema completo"""
    
    def test_full_system_integration(self):
        """Test integración completa del sistema"""
        # Obtener factory y manager
        factory = get_config_factory()
        
        # Crear manager adaptativo
        with patch('src.config.adaptive_config.os.path.exists', return_value=False):
            manager = AdaptiveConfigManager(factory)
        
        # Test flujo completo
        assert manager.current_profile == TradingProfile.MODERATE
        
        # Simular condiciones de mercado
        market_data = {
            'volatility': 0.05,
            'trend_strength': 0.3,
            'momentum': 0.2,
            'price_change_24h': -0.06
        }
        
        conditions = manager.analyze_market_conditions(market_data)
        assert len(conditions) > 0
        
        # Agregar métricas de rendimiento
        metrics = PerformanceMetrics(
            win_rate=0.55, profit_factor=1.3, sharpe_ratio=0.8,
            max_drawdown=0.25, avg_trade_duration=6.0,
            total_trades=20, last_updated=datetime.now()
        )
        manager.update_performance_metrics(metrics)
        
        # Test adaptación
        if manager.should_adapt(conditions):
            new_profile = manager.adapt_configuration(conditions)
            if new_profile:
                assert new_profile in TradingProfile
                assert len(manager.adaptation_history) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])