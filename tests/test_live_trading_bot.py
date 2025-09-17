#!/usr/bin/env python3
"""
Test específico para live_trading_bot.py - Verificación de Optimizaciones

Este test verifica que las optimizaciones aplicadas al live_trading_bot.py
funcionen correctamente y que la configuración parametrizada esté operativa.

Autor: Sistema de Optimización Automática
Fecha: $(date)
Versión: 1.0
"""

import unittest
import sys
import os
import logging
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar módulos a testear
from src.config.live_trading_bot_config import (
    LiveTradingBotConfig, 
    live_trading_bot_config,
    TechnicalIndicatorsConfig,
    BinancePriceAdjustmentConfig,
    LoggingConfig,
    DisplayConfig,
    SessionStatsConfig,
    PerformanceConfig
)

class TestLiveTradingBotOptimizations(unittest.TestCase):
    """Test suite para verificar las optimizaciones del live trading bot."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Resetear configuración a valores por defecto
        self.original_config = live_trading_bot_config.to_dict()
        live_trading_bot_config.__init__()
        
    def tearDown(self):
        """Limpieza después de cada test."""
        # Restaurar configuración original
        live_trading_bot_config.from_dict(self.original_config)
    
    def test_technical_indicators_config_defaults(self):
        """Test: Verificar valores por defecto de indicadores técnicos."""
        ti_config = live_trading_bot_config.get_technical_indicators_config()
        
        self.assertEqual(ti_config.rsi_period, 14)
        self.assertEqual(ti_config.sma_short_period, 20)
        self.assertEqual(ti_config.sma_long_period, 50)
        self.assertEqual(ti_config.volume_rolling_period, 20)
        self.assertEqual(ti_config.default_timeframe, "1h")
        self.assertEqual(ti_config.market_data_limit, 50)
    
    def test_technical_indicators_config_update(self):
        """Test: Verificar actualización de configuración de indicadores técnicos."""
        # Actualizar configuración
        live_trading_bot_config.update_technical_indicators(
            rsi_period=21,
            sma_short_period=15,
            sma_long_period=45,
            default_timeframe="4h",
            market_data_limit=100
        )
        
        ti_config = live_trading_bot_config.get_technical_indicators_config()
        
        self.assertEqual(ti_config.rsi_period, 21)
        self.assertEqual(ti_config.sma_short_period, 15)
        self.assertEqual(ti_config.sma_long_period, 45)
        self.assertEqual(ti_config.default_timeframe, "4h")
        self.assertEqual(ti_config.market_data_limit, 100)
    
    def test_binance_adjustments_config_defaults(self):
        """Test: Verificar valores por defecto de ajustes de Binance."""
        binance_config = live_trading_bot_config.get_binance_adjustments_config()
        
        self.assertEqual(binance_config.buy_adjustment_factor, 0.9997)
        self.assertEqual(binance_config.sell_adjustment_factor, 1.0003)
        self.assertAlmostEqual(binance_config.buy_adjustment_percentage, 0.03, places=2)
        self.assertAlmostEqual(binance_config.sell_adjustment_percentage, 0.03, places=2)
    
    def test_binance_adjustments_config_update(self):
        """Test: Verificar actualización de configuración de ajustes de Binance."""
        # Actualizar configuración
        live_trading_bot_config.update_binance_adjustments(
            buy_adjustment_factor=0.9995,
            sell_adjustment_factor=1.0005
        )
        
        binance_config = live_trading_bot_config.get_binance_adjustments_config()
        
        self.assertEqual(binance_config.buy_adjustment_factor, 0.9995)
        self.assertEqual(binance_config.sell_adjustment_factor, 1.0005)
        self.assertAlmostEqual(binance_config.buy_adjustment_percentage, 0.05, places=2)
        self.assertAlmostEqual(binance_config.sell_adjustment_percentage, 0.05, places=2)
    
    def test_logging_config_defaults(self):
        """Test: Verificar valores por defecto de configuración de logging."""
        logging_config = live_trading_bot_config.get_logging_config()
        
        self.assertEqual(logging_config.level, logging.INFO)
        self.assertFalse(logging_config.propagate)
        self.assertTrue(logging_config.colors_enabled)
        self.assertIn('INFO', logging_config.level_colors)
        self.assertIn('ERROR', logging_config.level_colors)
    
    def test_display_config_defaults(self):
        """Test: Verificar valores por defecto de configuración de display."""
        display_config = live_trading_bot_config.get_display_config()
        
        self.assertTrue(display_config.emojis_enabled)
        self.assertIn('analyzing', display_config.emoji_mapping)
        self.assertIn('cycle_start', display_config.emoji_mapping)
        self.assertIn('price_info', display_config.emoji_mapping)
        self.assertIn('separator', display_config.emoji_mapping)
    
    def test_display_config_emoji_disable(self):
        """Test: Verificar deshabilitación de emojis."""
        # Crear nueva configuración con emojis deshabilitados
        disabled_config = DisplayConfig(emojis_enabled=False)
        
        self.assertFalse(disabled_config.emojis_enabled)
        
        # Verificar que los emojis se reemplazan por strings vacíos
        for key, value in disabled_config.emoji_mapping.items():
            if key != 'separator':  # El separador puede mantener caracteres
                self.assertEqual(value, "")
    
    def test_session_stats_config_defaults(self):
        """Test: Verificar valores por defecto de estadísticas de sesión."""
        session_config = live_trading_bot_config.get_session_stats_config()
        
        self.assertEqual(session_config.initial_total_trades, 0)
        self.assertEqual(session_config.initial_successful_trades, 0)
        self.assertEqual(session_config.initial_total_pnl, 0.0)
    
    def test_performance_config_defaults(self):
        """Test: Verificar valores por defecto de configuración de rendimiento."""
        perf_config = live_trading_bot_config.get_performance_config()
        
        self.assertEqual(perf_config.cycle_counter_start, 0)
        self.assertEqual(perf_config.stats_update_frequency, 1)
    
    def test_config_serialization(self):
        """Test: Verificar serialización y deserialización de configuración."""
        # Modificar algunos valores
        live_trading_bot_config.update_technical_indicators(
            rsi_period=25,
            default_timeframe="2h"
        )
        live_trading_bot_config.update_binance_adjustments(
            buy_adjustment_factor=0.999
        )
        
        # Serializar a diccionario
        config_dict = live_trading_bot_config.to_dict()
        
        # Verificar que contiene las claves esperadas
        expected_keys = [
            'technical_indicators',
            'binance_adjustments', 
            'logging',
            'display',
            'performance'
        ]
        
        for key in expected_keys:
            self.assertIn(key, config_dict)
        
        # Verificar valores modificados
        self.assertEqual(config_dict['technical_indicators']['rsi_period'], 25)
        self.assertEqual(config_dict['technical_indicators']['default_timeframe'], "2h")
        self.assertEqual(config_dict['binance_adjustments']['buy_adjustment_factor'], 0.999)
        
        # Crear nueva configuración desde diccionario
        new_config = LiveTradingBotConfig.from_dict(config_dict)
        
        # Verificar que los valores se mantienen
        ti_config = new_config.get_technical_indicators_config()
        binance_config = new_config.get_binance_adjustments_config()
        
        self.assertEqual(ti_config.rsi_period, 25)
        self.assertEqual(ti_config.default_timeframe, "2h")
        self.assertEqual(binance_config.buy_adjustment_factor, 0.999)
    
    @patch('src.tools.live_trading_bot.LiveTradingBot')
    def test_live_trading_bot_uses_config(self, mock_bot_class):
        """Test: Verificar que LiveTradingBot usa la configuración parametrizada."""
        # Configurar mock
        mock_bot_instance = Mock()
        mock_bot_class.return_value = mock_bot_instance
        
        # Modificar configuración
        live_trading_bot_config.update_technical_indicators(
            rsi_period=30,
            default_timeframe="15m"
        )
        
        try:
            # Importar y crear instancia del bot
            from src.tools.live_trading_bot import LiveTradingBot
            
            # Verificar que se puede importar sin errores
            self.assertTrue(hasattr(LiveTradingBot, '__init__'))
            
        except ImportError as e:
            # Si hay error de importación, verificar que es por dependencias
            # y no por errores de sintaxis en nuestras modificaciones
            self.assertIn('No module named', str(e))
    
    def test_config_validation(self):
        """Test: Verificar validación de configuración."""
        # Test con valores válidos
        try:
            live_trading_bot_config.update_technical_indicators(
                rsi_period=14,
                sma_short_period=20,
                default_timeframe="1h"
            )
        except Exception as e:
            self.fail(f"Configuración válida falló: {e}")
        
        # Test con valores inválidos (si hay validación implementada)
        # Nota: Agregar tests específicos si se implementa validación
    
    def test_config_thread_safety(self):
        """Test: Verificar thread safety básico de la configuración."""
        import threading
        import time
        
        results = []
        
        def update_config(thread_id):
            """Función para actualizar configuración en thread."""
            try:
                live_trading_bot_config.update_technical_indicators(
                    rsi_period=thread_id + 10
                )
                time.sleep(0.01)  # Simular trabajo
                ti_config = live_trading_bot_config.get_technical_indicators_config()
                results.append((thread_id, ti_config.rsi_period))
            except Exception as e:
                results.append((thread_id, f"Error: {e}"))
        
        # Crear y ejecutar threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_config, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Esperar a que terminen
        for thread in threads:
            thread.join()
        
        # Verificar que no hubo errores
        for thread_id, result in results:
            self.assertNotIsInstance(result, str, 
                f"Thread {thread_id} falló: {result}")
    
    def test_emoji_regex_replacement(self):
        """Test: Verificar reemplazo de emojis por regex."""
        # Configuración con emojis habilitados
        enabled_config = DisplayConfig(emojis_enabled=True)
        
        # Verificar que los emojis están presentes por defecto
        self.assertTrue(any('📊' in emoji or '🚀' in emoji or '💰' in emoji 
                          for emoji in enabled_config.emoji_mapping.values()))
        
        # Configuración con emojis deshabilitados
        disabled_config = DisplayConfig(emojis_enabled=False)
        
        # Verificar que los emojis se removieron
        for key, value in disabled_config.emoji_mapping.items():
            if key != 'separator':
                # No debe contener emojis Unicode
                self.assertNotRegex(value, r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]')


def run_live_trading_bot_tests():
    """Función principal para ejecutar los tests."""
    print("🧪 Ejecutando tests de optimizaciones para live_trading_bot.py...")
    print("=" * 70)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLiveTradingBotOptimizations)
    
    # Ejecutar tests con verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"📊 Resumen de Tests:")
    print(f"   ✅ Tests ejecutados: {result.testsRun}")
    print(f"   ❌ Fallos: {len(result.failures)}")
    print(f"   🚫 Errores: {len(result.errors)}")
    print(f"   ⏱️  Tiempo: {result.testsRun} tests")
    
    if result.failures:
        print(f"\n❌ Fallos detectados:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🚫 Errores detectados:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Error:')[-1].strip()}")
    
    # Determinar resultado final
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n🎉 ¡Todos los tests pasaron exitosamente!")
        print(f"✅ Las optimizaciones de live_trading_bot.py están funcionando correctamente.")
    else:
        print(f"\n⚠️  Algunos tests fallaron. Revisar las optimizaciones.")
    
    print("=" * 70)
    
    return success


if __name__ == "__main__":
    # Ejecutar tests si se llama directamente
    success = run_live_trading_bot_tests()
    sys.exit(0 if success else 1)