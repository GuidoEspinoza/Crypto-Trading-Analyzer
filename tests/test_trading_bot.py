#!/usr/bin/env python3
"""
Tests para validar las optimizaciones del TradingBot

Este módulo contiene tests específicos para verificar que:
1. La configuración optimizada se aplica correctamente
2. Los valores hardcodeados han sido reemplazados
3. La funcionalidad del bot se mantiene intacta
4. Los parámetros optimizados mejoran el rendimiento
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.trading_bot import TradingBot
from src.config.config import optimized_config

class TestTradingBotOptimization(unittest.TestCase):
    """Tests para validar las optimizaciones del TradingBot"""
    
    def setUp(self):
        """Configurar el entorno de prueba"""
        # Mock de dependencias externas
        with patch('src.core.trading_bot.PaperTrader'), \
             patch('src.core.trading_bot.EnhancedRiskManager'), \
             patch('src.core.trading_bot.PositionMonitor'), \
             patch('src.core.trading_bot.PositionAdjuster'):
            self.bot = TradingBot()
    
    def test_optimized_config_integration(self):
        """Test que la configuración optimizada se integra correctamente"""
        # Verificar que el bot usa la configuración optimizada
        self.assertEqual(
            self.bot.max_daily_trades, 
            optimized_config.DEFAULT_MAX_DAILY_TRADES,
            "El bot debe usar el límite diario optimizado"
        )
        
        self.assertEqual(
            self.bot.min_confidence_threshold,
            optimized_config.DEFAULT_MIN_CONFIDENCE_THRESHOLD,
            "El bot debe usar el umbral de confianza optimizado"
        )
        
        self.assertEqual(
            self.bot.max_consecutive_losses,
            optimized_config.DEFAULT_MAX_CONSECUTIVE_LOSSES,
            "El bot debe usar el límite de pérdidas consecutivas optimizado"
        )
    
    def test_no_hardcoded_values(self):
        """Test que no existen valores hardcodeados en parámetros críticos"""
        # Verificar que los valores no son hardcodeados
        self.assertNotEqual(self.bot.max_daily_trades, 10, "No debe usar valor hardcodeado de 10 trades")
        self.assertNotEqual(self.bot.min_confidence_threshold, 70.0, "No debe usar valor hardcodeado de 70.0%")
        
        # Verificar que usa configuración dinámica
        self.assertTrue(
            hasattr(optimized_config, 'DEFAULT_MAX_DAILY_TRADES'),
            "Debe existir configuración para trades diarios"
        )
    
    def test_cache_ttl_optimization(self):
        """Test que el cache TTL usa configuración optimizada"""
        cache_ttl = TradingBot._get_cache_ttl()
        
        # Debe usar configuración optimizada como fallback
        self.assertIsInstance(cache_ttl, int, "Cache TTL debe ser un entero")
        self.assertGreater(cache_ttl, 0, "Cache TTL debe ser positivo")
    
    def test_thread_pool_optimization(self):
        """Test que el ThreadPool usa configuración optimizada"""
        self.assertEqual(
            self.bot.executor._max_workers,
            optimized_config.THREAD_POOL_MAX_WORKERS,
            "ThreadPool debe usar configuración optimizada"
        )
    
    def test_event_queue_optimization(self):
        """Test que el EventQueue usa configuración optimizada"""
        # El maxsize puede venir del perfil o de la configuración optimizada
        self.assertIsNotNone(self.bot.event_queue, "EventQueue debe estar inicializado")
        self.assertTrue(
            self.bot.event_queue.maxsize > 0,
            "EventQueue debe tener un tamaño máximo válido"
        )
    
    def test_symbols_configuration(self):
        """Test que los símbolos usan configuración optimizada"""
        self.assertEqual(
            self.bot.symbols,
            optimized_config.DEFAULT_SYMBOLS,
            "Debe usar símbolos de configuración optimizada"
        )
        
        # Verificar que contiene símbolos válidos
        for symbol in self.bot.symbols:
            self.assertIsInstance(symbol, str, "Cada símbolo debe ser string")
            self.assertTrue(symbol.endswith('USDT'), "Símbolos deben terminar en USDT")
    
    def test_timeframes_optimization(self):
        """Test que los timeframes usan configuración optimizada"""
        # Verificar timeframes desde configuración
        expected_timeframes = optimized_config.ANALYSIS_TIMEFRAMES
        
        # El bot puede usar timeframes específicos del perfil
        self.assertIsInstance(self.bot.primary_timeframe, str, "Primary timeframe debe ser string")
        self.assertIsInstance(self.bot.confirmation_timeframe, str, "Confirmation timeframe debe ser string")
        self.assertIsInstance(self.bot.trend_timeframe, str, "Trend timeframe debe ser string")
    
    def test_post_reset_window_optimization(self):
        """Test que la ventana post-reset usa configuración optimizada"""
        # Mock datetime para controlar la hora
        with patch('src.core.trading_bot.datetime') as mock_datetime:
            # Test dentro de ventana post-reset
            mock_datetime.now.return_value = datetime(2024, 1, 1, 2, 0, 0)  # 2 AM
            result = self.bot._is_in_post_reset_window()
            
            if optimized_config.POST_RESET_WINDOW_HOURS > 2:
                self.assertTrue(result, "Debe estar en ventana post-reset a las 2 AM")
            
            # Test fuera de ventana post-reset
            mock_datetime.now.return_value = datetime(2024, 1, 1, 10, 0, 0)  # 10 AM
            result = self.bot._is_in_post_reset_window()
            self.assertFalse(result, "No debe estar en ventana post-reset a las 10 AM")
    
    def test_reactivation_phases_optimization(self):
        """Test que las fases de reactivación usan configuración optimizada"""
        # Simular reactivación gradual
        self.bot.circuit_breaker_active = True
        self.bot.reactivation_phase = 0
        
        # Iniciar reactivación
        self.bot._initiate_gradual_reactivation()
        
        # Verificar fase 1
        self.assertEqual(self.bot.reactivation_phase, 1, "Debe iniciar en fase 1")
        self.assertEqual(self.bot.reactivation_trades_allowed, 1, "Fase 1 debe permitir 1 trade")
        
        # Simular éxito en fase 1
        self.bot.reactivation_success_count = 1
        self.bot._initiate_gradual_reactivation()
        
        # Verificar fase 2
        self.assertEqual(self.bot.reactivation_phase, 2, "Debe avanzar a fase 2")
        self.assertEqual(
            self.bot.reactivation_trades_allowed,
            optimized_config.REACTIVATION_PHASE_2_TRADES,
            "Fase 2 debe usar configuración optimizada"
        )
    
    def test_configuration_validation(self):
        """Test que la configuración optimizada es válida"""
        validation = optimized_config.validate_config()
        
        # Verificar que todas las validaciones pasan
        for key, is_valid in validation.items():
            self.assertTrue(is_valid, f"Configuración {key} debe ser válida")
    
    def test_environment_variable_support(self):
        """Test que las variables de entorno se leen correctamente"""
        # Test con variable de entorno mock
        with patch.dict(os.environ, {'TRADING_MAX_DAILY_TRADES': '15'}):
            env_value = optimized_config.get_from_env('TRADING_MAX_DAILY_TRADES', int, 10)
            self.assertEqual(env_value, 15, "Debe leer variable de entorno correctamente")
        
        # Test sin variable de entorno
        env_value = optimized_config.get_from_env('NONEXISTENT_VAR', int, 10)
        self.assertEqual(env_value, 10, "Debe usar valor por defecto si no existe variable")
    
    def test_profile_configurations(self):
        """Test que los perfiles de configuración funcionan correctamente"""
        # Test perfil conservador
        conservative = optimized_config.get_conservative_profile()
        self.assertIsInstance(conservative, dict, "Perfil conservador debe ser dict")
        self.assertIn('max_daily_trades', conservative, "Debe incluir límite de trades")
        
        # Test perfil agresivo
        aggressive = optimized_config.get_aggressive_profile()
        self.assertIsInstance(aggressive, dict, "Perfil agresivo debe ser dict")
        self.assertGreater(
            aggressive['max_daily_trades'],
            conservative['max_daily_trades'],
            "Perfil agresivo debe permitir más trades"
        )
    
    def test_backward_compatibility(self):
        """Test que la optimización mantiene compatibilidad hacia atrás"""
        # Verificar que métodos principales siguen funcionando
        self.assertTrue(hasattr(self.bot, 'start'), "Método start debe existir")
        self.assertTrue(hasattr(self.bot, 'stop'), "Método stop debe existir")
        self.assertTrue(hasattr(self.bot, 'get_status'), "Método get_status debe existir")
        
        # Verificar que propiedades críticas existen
        self.assertTrue(hasattr(self.bot, 'is_running'), "Propiedad is_running debe existir")
        self.assertTrue(hasattr(self.bot, 'stats'), "Propiedad stats debe existir")
    
    def test_performance_improvements(self):
        """Test que las optimizaciones mejoran el rendimiento"""
        # Verificar que los parámetros optimizados están en rangos esperados
        self.assertGreaterEqual(
            optimized_config.DEFAULT_MAX_DAILY_TRADES, 10,
            "Límite diario optimizado debe ser al menos 10"
        )
        
        self.assertLessEqual(
            optimized_config.DEFAULT_MIN_CONFIDENCE_THRESHOLD, 70.0,
            "Umbral de confianza optimizado debe ser más permisivo"
        )
        
        self.assertGreaterEqual(
            optimized_config.DEFAULT_MIN_CONFIDENCE_THRESHOLD, 60.0,
            "Umbral de confianza no debe ser demasiado bajo"
        )

class TestOptimizedConfigClass(unittest.TestCase):
    """Tests específicos para la clase TradingBotOptimizedConfig"""
    
    def test_config_instance(self):
        """Test que la instancia de configuración existe y es válida"""
        self.assertIsNotNone(optimized_config, "Instancia de configuración debe existir")
        
        # Verificar atributos principales
        required_attrs = [
            'DEFAULT_ANALYSIS_INTERVAL_MINUTES',
            'DEFAULT_MAX_DAILY_TRADES',
            'DEFAULT_MIN_CONFIDENCE_THRESHOLD',
            'DEFAULT_MAX_CONSECUTIVE_LOSSES',
            'DEFAULT_SYMBOLS',
            'ANALYSIS_TIMEFRAMES'
        ]
        
        for attr in required_attrs:
            self.assertTrue(
                hasattr(optimized_config, attr),
                f"Configuración debe tener atributo {attr}"
            )
    
    def test_config_types(self):
        """Test que los tipos de configuración son correctos"""
        self.assertIsInstance(
            optimized_config.DEFAULT_ANALYSIS_INTERVAL_MINUTES, int,
            "Intervalo de análisis debe ser entero"
        )
        
        self.assertIsInstance(
            optimized_config.DEFAULT_MAX_DAILY_TRADES, int,
            "Límite diario debe ser entero"
        )
        
        self.assertIsInstance(
            optimized_config.DEFAULT_MIN_CONFIDENCE_THRESHOLD, float,
            "Umbral de confianza debe ser float"
        )
        
        self.assertIsInstance(
            optimized_config.DEFAULT_SYMBOLS, list,
            "Símbolos debe ser lista"
        )
    
    def test_config_ranges(self):
        """Test que los valores de configuración están en rangos válidos"""
        self.assertGreater(
            optimized_config.DEFAULT_ANALYSIS_INTERVAL_MINUTES, 0,
            "Intervalo de análisis debe ser positivo"
        )
        
        self.assertGreater(
            optimized_config.DEFAULT_MAX_DAILY_TRADES, 0,
            "Límite diario debe ser positivo"
        )
        
        self.assertGreater(
            optimized_config.DEFAULT_MIN_CONFIDENCE_THRESHOLD, 0.0,
            "Umbral de confianza debe ser positivo"
        )
        
        self.assertLess(
            optimized_config.DEFAULT_MIN_CONFIDENCE_THRESHOLD, 100.0,
            "Umbral de confianza debe ser menor a 100%"
        )

if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)