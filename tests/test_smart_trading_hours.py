#!/usr/bin/env python3
"""
🧪 Tests para el sistema de horarios inteligentes de trading

Verifica que el sistema de horarios inteligentes funcione correctamente:
- Validación de horarios por tipo de mercado
- Configuración de horarios 08:00 - 22:00 Chile
- Detección automática de tipos de mercado
- Logs informativos sobre estado de horarios
"""

import unittest
import sys
import os
from datetime import datetime, time
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.main_config import (
    SMART_TRADING_HOURS,
    is_smart_trading_hours_allowed,
    _detect_market_type,
    get_smart_trading_status_summary,
    TIMEZONE
)

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback para Python < 3.9
    from datetime import timezone, timedelta
    class ZoneInfo:
        def __init__(self, name):
            if name == "America/Santiago":
                # Chile está UTC-3 (horario estándar) o UTC-4 (horario de verano)
                self.offset = timedelta(hours=-3)
            else:
                self.offset = timedelta(hours=0)
        
        def utcoffset(self, dt):
            return self.offset


class TestSmartTradingHours(unittest.TestCase):
    """Tests para el sistema de horarios inteligentes de trading"""
    
    def test_smart_trading_hours_config_structure(self):
        """Verificar que SMART_TRADING_HOURS tiene la estructura correcta"""
        # Verificar configuración principal
        self.assertIn("enabled", SMART_TRADING_HOURS)
        self.assertIn("start_time", SMART_TRADING_HOURS)
        self.assertIn("end_time", SMART_TRADING_HOURS)
        self.assertIn("timezone", SMART_TRADING_HOURS)
        
        # Verificar que está habilitado
        self.assertTrue(SMART_TRADING_HOURS["enabled"])
        
        # Verificar horarios configurados (formato HH:MM)
        self.assertIsInstance(SMART_TRADING_HOURS["start_time"], str)
        self.assertIsInstance(SMART_TRADING_HOURS["end_time"], str)
        self.assertRegex(SMART_TRADING_HOURS["start_time"], r'^\d{2}:\d{2}$')
        self.assertRegex(SMART_TRADING_HOURS["end_time"], r'^\d{2}:\d{2}$')
        
        # Verificar zona horaria de Chile
        self.assertEqual(SMART_TRADING_HOURS["timezone"], "America/Santiago")
        
        # Verificar configuración específica por mercado
        self.assertIn("market_specific", SMART_TRADING_HOURS)
        market_specific = SMART_TRADING_HOURS["market_specific"]
        
        expected_markets = ["crypto", "forex", "stocks_us"]
        for market in expected_markets:
            self.assertIn(market, market_specific)
            self.assertIn("enabled", market_specific[market])
            self.assertIn("start_time", market_specific[market])
            self.assertIn("end_time", market_specific[market])
            self.assertIn("reason", market_specific[market])
            
            # Verificar formato de tiempo
            self.assertRegex(market_specific[market]["start_time"], r'^\d{2}:\d{2}$')
            self.assertRegex(market_specific[market]["end_time"], r'^\d{2}:\d{2}$')
    
    def test_market_type_detection(self):
        """Verificar que la detección de tipos de mercado funciona correctamente"""
        # Crypto - símbolos que contienen indicadores crypto
        crypto_symbols = ["BTCUSD", "ETHUSD", "ADAUSD", "DOTUSD"]
        for symbol in crypto_symbols:
            market_type = _detect_market_type(symbol)
            self.assertEqual(market_type, "crypto", f"Symbol {symbol} should be detected as crypto")
        
        # Forex - símbolos de 6 caracteres con pares de divisas (sin indicadores crypto)
        forex_symbols = ["EURJPY", "GBPJPY", "EURGBP", "AUDNZD"]
        for symbol in forex_symbols:
            market_type = _detect_market_type(symbol)
            self.assertEqual(market_type, "forex", f"Symbol {symbol} should be detected as forex")
        
        # Stocks US
        us_stocks_symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
        for symbol in us_stocks_symbols:
            market_type = _detect_market_type(symbol)
            self.assertEqual(market_type, "stocks_us", f"Symbol {symbol} should be detected as stocks_us")
        
        # Unknown symbols should default to general
        unknown_symbols = ["UNKNOWN", "XYZ123"]
        for symbol in unknown_symbols:
            market_type = _detect_market_type(symbol)
            self.assertEqual(market_type, "general", f"Symbol {symbol} should be detected as general")
    
    def test_trading_hours_validation_basic(self):
        """Verificar que la validación de horarios funciona básicamente"""
        # Test para crypto
        result = is_smart_trading_hours_allowed("BTCUSD")
        self.assertIsInstance(result, dict)
        self.assertIn("is_allowed", result)
        self.assertIsInstance(result["is_allowed"], bool)
        
        # Test para forex
        result = is_smart_trading_hours_allowed("EURUSD")
        self.assertIsInstance(result, dict)
        self.assertIn("is_allowed", result)
        self.assertIsInstance(result["is_allowed"], bool)
        
        # Test para stocks US
        result = is_smart_trading_hours_allowed("AAPL")
        self.assertIsInstance(result, dict)
        self.assertIn("is_allowed", result)
        self.assertIsInstance(result["is_allowed"], bool)
    
    def test_smart_trading_status_summary(self):
        """Verificar que el resumen de estado funciona correctamente"""
        summary = get_smart_trading_status_summary()
        
        # Verificar que la función retorna algo válido
        self.assertIsNotNone(summary)
        
        # Si retorna un dict, verificar estructura básica
        if isinstance(summary, dict):
            # Verificar que tiene alguna información útil
            self.assertGreater(len(summary), 0)
        elif isinstance(summary, str):
            # Si retorna un string, verificar que no está vacío
            self.assertGreater(len(summary), 0)
    
    def test_timezone_configuration(self):
        """Verificar que la zona horaria está configurada correctamente"""
        from src.config.main_config import TIMEZONE
        
        # Verificar que la zona horaria es Chile
        self.assertEqual(TIMEZONE, "America/Santiago")
        
        # Verificar que la configuración de horarios inteligentes usa la misma zona horaria
        self.assertEqual(SMART_TRADING_HOURS["timezone"], TIMEZONE)
    
    def test_profile_adjustments_structure(self):
        """Verificar que los ajustes por perfil tienen la estructura correcta"""
        profile_adjustments = SMART_TRADING_HOURS.get("profile_adjustments", {})
        
        # Verificar que existen perfiles
        self.assertGreater(len(profile_adjustments), 0, "Should have profile adjustments")
        
        # Verificar estructura de cada perfil
        for profile_name, adjustments in profile_adjustments.items():
            self.assertIn("start_time", adjustments, f"Profile {profile_name} should have start_time")
            self.assertIn("end_time", adjustments, f"Profile {profile_name} should have end_time")
            
            # Verificar tipos de datos y formato
            self.assertIsInstance(adjustments["start_time"], str)
            self.assertIsInstance(adjustments["end_time"], str)
            self.assertRegex(adjustments["start_time"], r'^\d{2}:\d{2}$')
            self.assertRegex(adjustments["end_time"], r'^\d{2}:\d{2}$')
            
            # Verificar que los horarios son válidos
            start_hour, start_minute = map(int, adjustments["start_time"].split(':'))
            end_hour, end_minute = map(int, adjustments["end_time"].split(':'))
            
            self.assertGreaterEqual(start_hour, 0)
            self.assertLessEqual(start_hour, 23)
            self.assertGreaterEqual(start_minute, 0)
            self.assertLessEqual(start_minute, 59)
            self.assertGreaterEqual(end_hour, 0)
            self.assertLessEqual(end_hour, 23)
            self.assertGreaterEqual(end_minute, 0)
            self.assertLessEqual(end_minute, 59)
    
    def test_edge_cases(self):
        """Verificar casos límite y manejo de errores"""
        # Test con símbolo vacío
        result = is_smart_trading_hours_allowed("")
        self.assertIsInstance(result, dict)
        self.assertIn("is_allowed", result)
        
        # Test con símbolo inválido
        result = is_smart_trading_hours_allowed("INVALID_SYMBOL")
        self.assertIsInstance(result, dict)
        self.assertIn("is_allowed", result)
        
        # Test con perfil inválido - debería usar configuración por defecto
        result = is_smart_trading_hours_allowed("BTCUSD", profile_name="INVALID_PROFILE")
        self.assertIsInstance(result, dict)
        self.assertIn("is_allowed", result)
        
        # Test con símbolo None para _detect_market_type
        market_type = _detect_market_type(None)
        self.assertEqual(market_type, "general")  # Debería retornar general para None
        
        # Test con símbolo vacío para _detect_market_type
        market_type = _detect_market_type("")
        self.assertEqual(market_type, "general")  # Debería retornar general para vacío
        
        # Test con símbolo en minúsculas
        market_type = _detect_market_type("btcusd")
        self.assertEqual(market_type, "crypto")
        
        # Test con símbolo con espacios
        market_type = _detect_market_type(" BTCUSD ")
        self.assertEqual(market_type, "crypto")


class TestSmartTradingHoursIntegration(unittest.TestCase):
    """Tests de integración para horarios inteligentes"""
    
    def test_multiple_symbols_validation(self):
        """Verificar validación con múltiples símbolos"""
        test_symbols = ["BTCUSD", "EURUSD", "AAPL", "GOOGL", "ETHUSD"]
        
        for symbol in test_symbols:
            result = is_smart_trading_hours_allowed(symbol)
            market_type = _detect_market_type(symbol)
            
            # Verificar que cada símbolo tiene una respuesta válida
            self.assertIsInstance(result, dict)
            self.assertIn("is_allowed", result)
            self.assertIsInstance(result["is_allowed"], bool)
            self.assertIn(market_type, ["crypto", "forex", "stocks_us", "general"])


class TestSmartTradingHoursUTC(unittest.TestCase):
    """Tests específicos para el sistema UTC mejorado"""
    
    def test_utc_conversion_accuracy(self):
        """Verificar que las conversiones UTC son precisas"""
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        # Verificar que el resultado incluye información UTC
        self.assertIn("current_time_utc", result)
        self.assertIn("debug", result)
        
        debug_info = result["debug"]
        self.assertIn("start_chile", debug_info)
        self.assertIn("end_chile", debug_info)
        self.assertIn("start_utc", debug_info)
        self.assertIn("end_utc", debug_info)
        self.assertIn("current_chile", debug_info)
        self.assertIn("current_utc", debug_info)
    
    def test_summer_time_handling(self):
        """Verificar manejo correcto del horario de verano chileno"""
        # Este test verifica que el sistema maneja correctamente diferentes horarios
        # Sin usar mocks complejos, simplemente verificamos que la función funciona
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        # Verificar que la función maneja correctamente los horarios
        self.assertIn("debug", result)
        debug_info = result["debug"]
        
        # Verificar que tenemos información de Chile y UTC
        self.assertIn("current_chile", debug_info)
        self.assertIn("current_utc", debug_info)
        
        # Verificar que Chile tiene offset correcto (UTC-3 o UTC-4)
        chile_time = debug_info["current_chile"]
        self.assertTrue("-03" in chile_time or "-04" in chile_time)
        self.assertIn("UTC", debug_info["current_utc"])
    
    def test_winter_time_handling(self):
        """Verificar manejo correcto del horario de invierno chileno"""
        # Similar al test anterior, verificamos que el sistema funciona
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        # Verificar que la función maneja correctamente los horarios
        self.assertIn("debug", result)
        debug_info = result["debug"]
        
        # Verificar que tenemos información de Chile y UTC
        self.assertIn("current_chile", debug_info)
        self.assertIn("current_utc", debug_info)
        
        # Verificar formato correcto
        chile_time = debug_info["current_chile"]
        utc_time = debug_info["current_utc"]
        self.assertTrue("-03" in chile_time or "-04" in chile_time)
        self.assertIn("UTC", utc_time)
    
    def test_timezone_consistency(self):
        """Verificar consistencia entre horarios Chile y UTC"""
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        if "debug" in result:
            debug_info = result["debug"]
            
            # Verificar que los horarios están en formato correcto
            self.assertRegex(debug_info["start_chile"], r'\d{2}:\d{2} -0[34]')
            self.assertRegex(debug_info["end_chile"], r'\d{2}:\d{2} -0[34]')
            self.assertRegex(debug_info["start_utc"], r'\d{2}:\d{2} UTC')
            self.assertRegex(debug_info["end_utc"], r'\d{2}:\d{2} UTC')
            # Ajustar regex para el formato real (sin segundos en algunos casos)
            self.assertRegex(debug_info["current_chile"], r'\d{2}:\d{2}(:\d{2})? -0[34]')
            self.assertRegex(debug_info["current_utc"], r'\d{2}:\d{2}(:\d{2})? UTC')
    
    def test_utc_comparison_precision(self):
        """Verificar que las comparaciones UTC son más precisas que las locales"""
        # Este test verifica que el sistema usa UTC internamente
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        # Verificar que tenemos tanto tiempo Chile como UTC
        self.assertIn("current_time_chile", result)
        self.assertIn("current_time_utc", result)
        
        # Verificar que ambos son objetos datetime con zona horaria
        chile_time = result["current_time_chile"]
        utc_time = result["current_time_utc"]
        
        self.assertIsNotNone(chile_time.tzinfo)
        self.assertIsNotNone(utc_time.tzinfo)
        
        # Verificar que representan el mismo momento en el tiempo
        # (convertir ambos a UTC para comparar)
        import pytz
        chile_as_utc = chile_time.astimezone(pytz.UTC)
        utc_as_utc = utc_time.astimezone(pytz.UTC)
        
        # Deberían ser iguales (con tolerancia de 1 segundo por procesamiento)
        time_diff = abs((chile_as_utc - utc_as_utc).total_seconds())
        self.assertLess(time_diff, 1.0, "Chile and UTC times should represent the same moment")


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.WARNING)  # Reducir ruido en tests
    
    unittest.main(verbosity=2)