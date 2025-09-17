#!/usr/bin/env python3
"""
Test específico para las optimizaciones de trading_monitor.py
Este test verifica que las configuraciones parametrizadas funcionen correctamente.
"""

import unittest
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.config.trading_monitor_config import (
        TradingMonitorConfig,
        DisplayFormatsConfig,
        PrecisionConfig,
        EmojiConfig,
        AlertsConfig,
        APIConfig,
        MessagesConfig,
        AnalysisConfig,
        DEFAULT_TRADING_MONITOR_CONFIG,
        COMPACT_PROFILE,
        DETAILED_PROFILE,
        NO_EMOJI_PROFILE,
        get_trading_monitor_config
    )
except ImportError as e:
    print(f"❌ Error importando configuraciones: {e}")
    sys.exit(1)

class TestTradingMonitorOptimizations(unittest.TestCase):
    """Test suite para las optimizaciones del trading monitor"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        print("\n" + "="*60)
        print("🧪 INICIANDO TEST DE OPTIMIZACIONES TRADING MONITOR")
        print("="*60)
        
        # Configuración de test básica
        self.test_config = TradingMonitorConfig(
            display_formats=DisplayFormatsConfig(
                main_separator_width=50,
                section_separator_width=30
            ),
            precision=PrecisionConfig(
                price_decimals=4,
                usdt_decimals=2,
                percentage_decimals=2,
                quantity_decimals=6,
                distance_decimals=2,
                pnl_decimals=2
            ),
            emojis=EmojiConfig(
                enabled=True,
                monitor="🔍",
                chart="📊",
                clock="🕐"
            ),
            alerts=AlertsConfig(
                critical_pending_executions=5,
                warning_positions_without_tp=3,
                warning_positions_without_sl=3,
                critical_positions_without_both=1,
                show_tp_alerts=True,
                show_sl_alerts=True,
                show_pending_execution_alerts=True,
                show_missing_protection_alerts=True,
                show_recommendations=True,
                max_retries=3,
                retry_delay_seconds=1.0
            ),
            api=APIConfig(
                request_timeout=10,
                price_request_timeout=5.0,
                max_retries=3,
                retry_delay=1.0,
                price_cache_ttl=30,
                enable_price_cache=True
            ),
            analysis=AnalysisConfig(
                show_trade_details=True,
                show_pnl_calculations=True,
                show_distance_calculations=True,
                show_potential_gains_losses=True,
                show_portfolio_summary=True,
                show_configuration_summary=True,
                show_protection_warnings=True,
                show_execution_alerts=True,
                show_recommendations=True,
                max_positions_detailed=50,
                max_missed_executions_detailed=20,
                max_symbols_price_check=20,
                sort_positions_by_entry_time=True,
                sort_descending=True
            ),
            default_hours_back=24,
            enable_color_output=True,
            enable_detailed_logging=False,
            available_modes=["status", "missed", "detailed"],
            default_mode="status"
        )
    
    def test_config_creation(self):
        """Test 1: Verificar creación de configuración parametrizada"""
        print("\n🧪 Test 1: Verificando creación de configuración...")
        
        # Verificar que la configuración se crea correctamente
        self.assertIsInstance(self.test_config, TradingMonitorConfig)
        self.assertIsInstance(self.test_config.display_formats, DisplayFormatsConfig)
        self.assertIsInstance(self.test_config.precision, PrecisionConfig)
        self.assertIsInstance(self.test_config.emojis, EmojiConfig)
        self.assertIsInstance(self.test_config.alerts, AlertsConfig)
        self.assertIsInstance(self.test_config.api, APIConfig)
        self.assertIsInstance(self.test_config.analysis, AnalysisConfig)
        
        print("✅ Configuración creada correctamente")
    
    def test_predefined_profiles(self):
        """Test 2: Verificar perfiles predefinidos"""
        print("\n🧪 Test 2: Verificando perfiles predefinidos...")
        
        # Verificar que los perfiles existen
        self.assertIsInstance(DEFAULT_TRADING_MONITOR_CONFIG, TradingMonitorConfig)
        self.assertIsInstance(COMPACT_PROFILE, TradingMonitorConfig)
        self.assertIsInstance(DETAILED_PROFILE, TradingMonitorConfig)
        self.assertIsInstance(NO_EMOJI_PROFILE, TradingMonitorConfig)
        
        # Verificar diferencias entre perfiles
        self.assertEqual(COMPACT_PROFILE.display_formats.main_separator_width, 40)
        self.assertEqual(DETAILED_PROFILE.analysis.max_positions_detailed, 100)
        self.assertFalse(NO_EMOJI_PROFILE.emojis.enabled)
        
        print("✅ Perfiles predefinidos verificados")
    
    def test_emoji_configuration(self):
        """Test 3: Verificar configuración de emojis"""
        print("\n🧪 Test 3: Verificando configuración de emojis...")
        
        # Verificar perfil sin emojis
        self.assertFalse(NO_EMOJI_PROFILE.emojis.enabled)
        self.assertEqual(NO_EMOJI_PROFILE.emojis.monitor, "")
        self.assertEqual(NO_EMOJI_PROFILE.emojis.chart, "")
        
        # Verificar perfil con emojis
        self.assertTrue(DEFAULT_TRADING_MONITOR_CONFIG.emojis.enabled)
        self.assertNotEqual(DEFAULT_TRADING_MONITOR_CONFIG.emojis.monitor, "")
        
        print("✅ Configuración de emojis verificada")
    
    def test_serialization(self):
        """Test 4: Verificar serialización y deserialización"""
        print("\n🧪 Test 4: Verificando serialización...")
        
        # Serializar configuración
        config_dict = self.test_config.to_dict()
        self.assertIsInstance(config_dict, dict)
        
        # Deserializar configuración
        restored_config = TradingMonitorConfig.from_dict(config_dict)
        self.assertIsInstance(restored_config, TradingMonitorConfig)
        
        # Verificar que los valores se mantienen
        self.assertEqual(restored_config.precision.price_decimals, 
                        self.test_config.precision.price_decimals)
        self.assertEqual(restored_config.emojis.enabled, 
                        self.test_config.emojis.enabled)
        
        print("✅ Serialización verificada")
    
    def test_file_operations(self):
        """Test 5: Verificar operaciones de archivo"""
        print("\n🧪 Test 5: Verificando operaciones de archivo...")
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            # Guardar configuración
            self.test_config.save_to_file(temp_file)
            self.assertTrue(os.path.exists(temp_file))
            
            # Cargar configuración
            loaded_config = TradingMonitorConfig.load_from_file(temp_file)
            self.assertIsInstance(loaded_config, TradingMonitorConfig)
            
            # Verificar que los datos son correctos
            self.assertEqual(loaded_config.precision.price_decimals,
                           self.test_config.precision.price_decimals)
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        print("✅ Operaciones de archivo verificadas")
    
    def test_get_config_function(self):
        """Test 6: Verificar función get_trading_monitor_config"""
        print("\n🧪 Test 6: Verificando función get_trading_monitor_config...")
        
        # Test con perfiles válidos
        config_default = get_trading_monitor_config('default')
        config_compact = get_trading_monitor_config('compact')
        config_detailed = get_trading_monitor_config('detailed')
        config_no_emoji = get_trading_monitor_config('no_emoji')
        
        # Verificar que se obtienen configuraciones
        self.assertIsInstance(config_default, TradingMonitorConfig)
        self.assertIsInstance(config_compact, TradingMonitorConfig)
        self.assertIsInstance(config_detailed, TradingMonitorConfig)
        self.assertIsInstance(config_no_emoji, TradingMonitorConfig)
        
        # Verificar que son diferentes
        self.assertNotEqual(config_compact.emojis.enabled, config_no_emoji.emojis.enabled)
        
        print("✅ Función get_trading_monitor_config verificada")
    
    def test_comprehensive_integration(self):
        """Test 7: Test integral de todas las funcionalidades"""
        print("\n🧪 Test 7: Ejecutando test integral...")
        
        # Verificar que todas las configuraciones se pueden crear
        configs = [DEFAULT_TRADING_MONITOR_CONFIG, COMPACT_PROFILE, DETAILED_PROFILE, NO_EMOJI_PROFILE]
        
        for i, config in enumerate(configs):
            # Verificar que la configuración es válida
            self.assertIsInstance(config, TradingMonitorConfig)
            
            # Verificar que se puede serializar
            config_dict = config.to_dict()
            self.assertIsInstance(config_dict, dict)
            
            # Verificar que se puede deserializar
            restored_config = TradingMonitorConfig.from_dict(config_dict)
            self.assertIsInstance(restored_config, TradingMonitorConfig)
            
            print(f"✅ Configuración {i+1} verificada integralmente")
        
        print("✅ Test integral completado exitosamente")

def run_tests():
    """Ejecutar todos los tests"""
    print("\n🚀 INICIANDO TESTS DE OPTIMIZACIONES TRADING MONITOR")
    print("="*70)
    
    # Crear suite de tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTradingMonitorOptimizations)
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print(f"✅ {result.testsRun} tests ejecutados")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print(f"❌ {len(result.failures)} fallos")
        print(f"❌ {len(result.errors)} errores")
    
    print("="*70)
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)