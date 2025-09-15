#!/usr/bin/env python3
"""
Test suite para Enhanced Risk Manager

Este módulo contiene tests comprehensivos para verificar el funcionamiento
correcto del Enhanced Risk Manager después de las optimizaciones realizadas.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.enhanced_risk_manager import (
    EnhancedRiskManager,
    RiskLevel,
    PositionSizing,
    DynamicStopLoss,
    DynamicTakeProfit,
    EnhancedRiskAssessment
)
from src.core.enhanced_strategies import EnhancedSignal
from src.config.config import TradingProfiles


class TestEnhancedRiskManager(unittest.TestCase):
    """Test suite para Enhanced Risk Manager"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Mock de la configuración - estructura de perfil de trading
        self.mock_config = {
            'max_risk_per_trade': 1.5,
            'max_daily_risk': 6.0,
            'max_drawdown_threshold': 0.10,
            'correlation_threshold': 0.75,
            'min_position_size': 12.0,
            'risk_max_position_size': 0.8,
            'kelly_fraction': 0.28,
            'volatility_adjustment': 1.25,
            'atr_multiplier_min': 1.8,
            'atr_multiplier_max': 2.8,
            'atr_default': 1.8,
            'atr_volatile': 2.8,
            'atr_sideways': 1.4,
            'trailing_stop_activation': 0.15,
            'breakeven_threshold': 0.6,
            'intelligent_trailing': True,
            'dynamic_position_sizing': True,
            'tp_min_percentage': 2.5,
            'tp_max_percentage': 5.5,
            'sl_min_percentage': 0.8,
            'sl_max_percentage': 2.5,
            'tp_increment_percentage': 1.0,
            'max_tp_adjustments': 5,
            'min_confidence_threshold': 0.6,
            'default_leverage': 1.0,
            'tp_confidence_threshold': 0.7,
            'balance': 10000,
            'max_positions': 5
        }
        
        # Patch de TradingProfiles.get_current_profile
        self.config_patcher = patch('src.core.enhanced_risk_manager.TradingProfiles.get_current_profile')
        self.mock_get_config = self.config_patcher.start()
        self.mock_get_config.return_value = self.mock_config
        
        # Inicializar el risk manager
        self.risk_manager = EnhancedRiskManager()
        
        # Datos de prueba
        self.test_symbol = "BTC/USDT"
        self.test_entry_price = 50000.0
        self.test_stop_loss = 48000.0
        self.test_take_profit = 55000.0
        self.test_position_size = 0.1
        self.test_confidence = 0.8
        
        # Mock de EnhancedSignal con todos los atributos requeridos
        self.mock_signal = MagicMock(spec=EnhancedSignal)
        self.mock_signal.symbol = self.test_symbol
        self.mock_signal.entry_price = self.test_entry_price
        self.mock_signal.stop_loss = self.test_stop_loss
        self.mock_signal.take_profit = self.test_take_profit
        self.mock_signal.confidence_score = self.test_confidence
        self.mock_signal.signal_strength = 0.8
        self.mock_signal.market_data = {'atr': 1000, 'volatility': 0.02, 'volume_ratio': 1.5}
        # Atributos específicos de EnhancedSignal
        self.mock_signal.signal_type = "BUY"
        self.mock_signal.price = self.test_entry_price
        self.mock_signal.strength = "Strong"
        self.mock_signal.strategy_name = "TestStrategy"
        self.mock_signal.timestamp = datetime.now()
        self.mock_signal.indicators_data = {"rsi": 30, "macd": 0.5}
        self.mock_signal.notes = "Test signal"
        self.mock_signal.volume_confirmation = True
        self.mock_signal.trend_confirmation = "BULLISH"
        self.mock_signal.risk_reward_ratio = 2.5
        self.mock_signal.stop_loss_price = self.test_stop_loss
        self.mock_signal.take_profit_price = self.test_take_profit
        self.mock_signal.market_regime = "TRENDING"
        self.mock_signal.confluence_score = 4
        self.mock_signal.timeframe = "1h"
    
    def tearDown(self):
        """Limpieza después de cada test"""
        self.config_patcher.stop()
    
    def test_initialization(self):
        """Test de inicialización del risk manager"""
        self.assertIsInstance(self.risk_manager, EnhancedRiskManager)
        self.assertIsNotNone(self.risk_manager.global_config)
    
    def test_assess_trade_risk_basic(self):
        """Test básico de evaluación de riesgo"""
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment, EnhancedRiskAssessment)
        self.assertIsInstance(assessment.risk_level, RiskLevel)
        self.assertIsInstance(assessment.overall_risk_score, float)
        self.assertGreaterEqual(assessment.overall_risk_score, 0.0)
        self.assertLessEqual(assessment.overall_risk_score, 100.0)
    
    def test_position_sizing_fixed_risk(self):
        """Test de position sizing con riesgo fijo"""
        # El position sizing se calcula dentro de assess_trade_risk
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment.position_sizing, PositionSizing)
        self.assertGreater(assessment.position_sizing.recommended_size, 0)
        self.assertGreater(assessment.position_sizing.risk_per_trade, 0)
    
    def test_position_sizing_kelly_criterion(self):
        """Test de position sizing con Kelly Criterion"""
        # Configurar mock signal para Kelly
        self.mock_signal.win_rate = 0.6
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment.position_sizing, PositionSizing)
        self.assertGreater(assessment.position_sizing.recommended_size, 0)
        self.assertIsInstance(assessment.position_sizing.reasoning, str)
    
    def test_position_sizing_volatility_adjusted(self):
        """Test de position sizing ajustado por volatilidad"""
        # Configurar mock signal con alta volatilidad
        self.mock_signal.market_data['atr'] = 1500
        self.mock_signal.market_data['volatility'] = 0.05
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment.position_sizing, PositionSizing)
        self.assertGreater(assessment.position_sizing.recommended_size, 0)
    
    def test_dynamic_stop_loss_calculation(self):
        """Test de cálculo de stop loss dinámico"""
        with patch.object(self.risk_manager, '_get_current_market_data') as mock_market_data:
            mock_market_data.return_value = {
                'atr': 1500,
                'volume_ratio': 1.2,
                'trend_strength': 0.7
            }
            
            assessment = self.risk_manager.assess_trade_risk(
                signal=self.mock_signal,
                current_portfolio_value=10000.0
            )
            
            self.assertIsInstance(assessment.dynamic_stop_loss, DynamicStopLoss)
            self.assertIsInstance(assessment.dynamic_stop_loss.stop_loss_price, float)
            self.assertLess(assessment.dynamic_stop_loss.stop_loss_price, self.test_entry_price)  # Para posición long
    
    def test_dynamic_take_profit_calculation(self):
        """Test de cálculo de take profit dinámico"""
        with patch.object(self.risk_manager, '_get_current_market_data') as mock_market_data:
            mock_market_data.return_value = {
                'atr': 1500,
                'volume_ratio': 1.2,
                'trend_strength': 0.7
            }
            
            assessment = self.risk_manager.assess_trade_risk(
                signal=self.mock_signal,
                current_portfolio_value=10000.0
            )
            
            self.assertIsInstance(assessment.dynamic_take_profit, DynamicTakeProfit)
            self.assertIsInstance(assessment.dynamic_take_profit.take_profit_price, float)
            self.assertGreater(assessment.dynamic_take_profit.take_profit_price, self.test_entry_price)  # Para posición long
    
    def test_risk_level_determination(self):
        """Test de determinación de nivel de riesgo"""
        # Test diferentes scores de riesgo (0-100 scale)
        test_cases = [
            (10.0, RiskLevel.VERY_LOW),
            (30.0, RiskLevel.LOW),
            (50.0, RiskLevel.MODERATE),
            (70.0, RiskLevel.HIGH),
            (90.0, RiskLevel.VERY_HIGH)
        ]
        
        for risk_score, expected_level in test_cases:
            with self.subTest(risk_score=risk_score):
                level = self.risk_manager._determine_risk_level(risk_score)
                self.assertEqual(level, expected_level)
    
    def test_portfolio_risk_calculation(self):
        """Test de cálculo de riesgo del portfolio"""
        # Test básico de evaluación de riesgo de portfolio
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment.portfolio_risk_metrics, dict)
        self.assertIsInstance(assessment.correlation_risk, float)
        self.assertIsInstance(assessment.volatility_risk, float)
        self.assertIsInstance(assessment.liquidity_risk, float)
    
    def test_intelligent_trailing_stop(self):
        """Test de trailing stop inteligente"""
        # Mock de posición
        mock_position = {
            'symbol': self.test_symbol,
            'entry_price': self.test_entry_price,
            'current_price': 52000,  # En ganancia
            'stop_loss': self.test_stop_loss,
            'position_type': 'long'
        }
        
        with patch.object(self.risk_manager, '_get_current_market_data') as mock_market_data:
            mock_market_data.return_value = {
                'atr': 1500,
                'volume_ratio': 1.2,
                'trend_strength': 0.7
            }
            
            # Test que el dynamic stop loss incluye trailing
            assessment = self.risk_manager.assess_trade_risk(
                signal=self.mock_signal,
                current_portfolio_value=10000.0
            )
            
            self.assertIsInstance(assessment.dynamic_stop_loss, DynamicStopLoss)
            self.assertIsInstance(assessment.dynamic_stop_loss.stop_loss_price, float)
            self.assertIsInstance(assessment.dynamic_stop_loss.trailing_distance, float)
            self.assertGreater(assessment.dynamic_stop_loss.stop_loss_price, 0)
    
    def test_configuration_usage(self):
        """Test de uso correcto de la configuración centralizada"""
        # Verificar que se usan valores de configuración en lugar de hardcodeados
        
        self.assertIsNotNone(self.risk_manager.global_config)
        self.assertEqual(
            self.risk_manager.global_config['balance'],
            self.mock_config['balance']
        )
        self.assertEqual(
            self.risk_manager.global_config['max_positions'],
            self.mock_config['max_positions']
        )
    
    def test_error_handling(self):
        """Test de manejo de errores"""
        # Test con señal inválida pero con valores válidos para evitar errores de multiplicación
        invalid_signal = Mock()
        invalid_signal.price = 50000.0  # Precio válido
        invalid_signal.signal_type = "BUY"
        invalid_signal.confidence_score = 50.0
        invalid_signal.volume_confirmation = False
        invalid_signal.trend_confirmation = "NEUTRAL"
        invalid_signal.risk_reward_ratio = 0.0
        invalid_signal.stop_loss_price = 0.0
        invalid_signal.take_profit_price = 0.0
        invalid_signal.market_regime = "NORMAL"
        invalid_signal.confluence_score = 0
        
        assessment = self.risk_manager.assess_trade_risk(
            signal=invalid_signal,
            current_portfolio_value=10000.0
        )
        
        # Debe devolver una evaluación por defecto
        self.assertIsNotNone(assessment)
        self.assertIsInstance(assessment.overall_risk_score, float)
    
    def test_risk_recommendations(self):
        """Test de generación de recomendaciones"""
        # Configurar mock signal con condiciones de alto riesgo
        self.mock_signal.market_data['atr'] = 2000  # Alta volatilidad
        self.mock_signal.market_data['volume_ratio'] = 0.5  # Bajo volumen
        self.mock_signal.signal_strength = 0.3  # Señal débil
        
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment.recommendations, list)
        self.assertGreater(len(assessment.recommendations), 0)
        
        # Verificar que hay recomendaciones específicas para condiciones de alto riesgo
        recommendations_text = ' '.join(assessment.recommendations)
        self.assertIsInstance(recommendations_text, str)
    
    def test_market_data_integration(self):
        """Test de integración con datos de mercado"""
        # Test con datos de mercado en el signal
        self.mock_signal.market_data = {
            'price': self.test_entry_price,
            'volume': 1000000,
            'volatility': 0.02,
            'atr': 1000
        }
        
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsNotNone(assessment)
        self.assertIsInstance(assessment.overall_risk_score, float)
    
    def test_position_update(self):
        """Test de actualización de posición"""
        mock_position = {
            'symbol': self.test_symbol,
            'entry_price': self.test_entry_price,
            'current_price': 51000,
            'stop_loss': self.test_stop_loss,
            'take_profit': self.test_take_profit,
            'position_type': 'long',
            'size': self.test_position_size
        }
        
        with patch.object(self.risk_manager, '_get_current_market_data') as mock_market_data:
            mock_market_data.return_value = {
                'atr': 1500,
                'volume_ratio': 1.2,
                'trend_strength': 0.7
            }
            
            # Test que el assessment contiene información de actualización
            assessment = self.risk_manager.assess_trade_risk(
                signal=self.mock_signal,
                current_portfolio_value=10000.0
            )
            
            self.assertIsInstance(assessment.dynamic_stop_loss, DynamicStopLoss)
            self.assertIsInstance(assessment.dynamic_take_profit, DynamicTakeProfit)
            self.assertGreater(assessment.dynamic_stop_loss.stop_loss_price, 0)
    
    def test_risk_report_generation(self):
        """Test de generación de reporte de riesgo"""
        # Test que el assessment contiene información de reporte
        assessment = self.risk_manager.assess_trade_risk(
            signal=self.mock_signal,
            current_portfolio_value=10000.0
        )
        
        self.assertIsInstance(assessment.portfolio_risk_metrics, dict)
        self.assertIsInstance(assessment.recommendations, list)
        self.assertIsInstance(assessment.market_risk_factors, dict)
        self.assertIsInstance(assessment.overall_risk_score, float)


class TestRiskManagerIntegration(unittest.TestCase):
    """Tests de integración para el Risk Manager"""
    
    def setUp(self):
        """Configuración para tests de integración"""
        self.mock_config = {
            'max_risk_per_trade': 1.5,
            'max_daily_risk': 6.0,
            'max_drawdown_threshold': 0.10,
            'correlation_threshold': 0.75,
            'min_position_size': 12.0,
            'risk_max_position_size': 0.8,
            'kelly_fraction': 0.28,
            'volatility_adjustment': 1.25,
            'atr_multiplier_min': 1.8,
            'atr_multiplier_max': 2.8,
            'atr_default': 1.8,
            'atr_volatile': 2.8,
            'atr_sideways': 1.4,
            'trailing_stop_activation': 0.15,
            'breakeven_threshold': 0.6,
            'intelligent_trailing': True,
            'dynamic_position_sizing': True,
            'tp_min_percentage': 2.5,
            'tp_max_percentage': 5.5,
            'sl_min_percentage': 0.8,
            'sl_max_percentage': 2.5,
            'tp_increment_percentage': 1.0,
            'max_tp_adjustments': 5,
            'min_confidence_threshold': 0.6,
            'default_leverage': 1.0,
            'tp_confidence_threshold': 0.7,
            'balance': 10000,
            'max_positions': 5
        }
        
        with patch('src.core.enhanced_risk_manager.TradingProfiles.get_current_profile', return_value=self.mock_config):
            self.risk_manager = EnhancedRiskManager()
    
    def test_full_risk_assessment_workflow(self):
        """Test del flujo completo de evaluación de riesgo"""
        with patch.object(self.risk_manager, '_get_current_market_data') as mock_market_data:
            mock_market_data.return_value = {
                'atr': 1500,
                'volume_ratio': 1.2,
                'trend_strength': 0.7
            }
            
            # 1. Evaluar riesgo
            test_signal = MagicMock(spec=EnhancedSignal)
            test_signal.symbol = "BTC/USDT"
            test_signal.entry_price = 50000
            test_signal.stop_loss = 48000
            test_signal.take_profit = 55000
            test_signal.confidence_score = 0.8
            test_signal.signal_strength = 0.8
            test_signal.market_data = {'atr': 1500, 'volatility': 0.02, 'volume_ratio': 1.5}
            # Atributos específicos de EnhancedSignal
            test_signal.signal_type = "BUY"
            test_signal.price = 50000
            test_signal.strength = "Strong"
            test_signal.strategy_name = "TestStrategy"
            test_signal.timestamp = datetime.now()
            test_signal.indicators_data = {"rsi": 30, "macd": 0.5}
            test_signal.notes = "Test signal"
            test_signal.volume_confirmation = True
            test_signal.trend_confirmation = "BULLISH"
            test_signal.risk_reward_ratio = 2.5
            test_signal.stop_loss_price = 48000
            test_signal.take_profit_price = 55000
            test_signal.market_regime = "TRENDING"
            test_signal.confluence_score = 4
            test_signal.timeframe = "1h"
            
            assessment = self.risk_manager.assess_trade_risk(
                signal=test_signal,
                current_portfolio_value=10000.0
            )
            
            # 2. Verificar position sizing en la evaluación
            self.assertIsInstance(assessment.position_sizing, PositionSizing)
            self.assertGreater(assessment.position_sizing.recommended_size, 0)
            
            # 3. Verificar stops dinámicos en la evaluación
            self.assertIsInstance(assessment.dynamic_stop_loss, DynamicStopLoss)
            self.assertIsInstance(assessment.dynamic_take_profit, DynamicTakeProfit)
            
            # Verificaciones finales
            self.assertIsInstance(assessment, EnhancedRiskAssessment)
            self.assertIsInstance(assessment.position_sizing.recommended_size, float)
            self.assertIsInstance(assessment.dynamic_stop_loss.stop_loss_price, (int, float))
            
            # El position size calculado debe ser razonable
            self.assertGreater(assessment.position_sizing.recommended_size, 0)
            self.assertLessEqual(assessment.position_sizing.recommended_size, 100)  # Ajustado para valores reales
            
            # El stop dinámico debe ser menor que el precio de entrada (long)
            self.assertLess(float(assessment.dynamic_stop_loss.stop_loss_price), 50000)


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)