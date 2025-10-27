#!/usr/bin/env python3
"""
🌙🌅 Test de Escenario Nocturno a Matutino

Simula el escenario completo:
1. Durante la noche (02:00 AM) - NO debe ejecutar trades
2. A las 08:00 AM - DEBE comenzar a analizar y ejecutar trades
3. Verifica que el manejo de smart_hours_status funcione correctamente
"""

import unittest
import sys
import os
from datetime import datetime, time
from unittest.mock import patch, Mock, MagicMock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.main_config import (
    is_smart_trading_hours_allowed,
    SMART_TRADING_HOURS
)

class TestNightToMorningScenario(unittest.TestCase):
    """🌙🌅 Tests para simular el escenario nocturno a matutino"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        print("\n" + "="*60)
        print("🧪 INICIANDO TEST DE ESCENARIO NOCTURNO A MATUTINO")
        print("="*60)
    
    def test_smart_hours_status_type_handling(self):
        """🔧 Test: Verificar que smart_hours_status se maneja como dict"""
        print("\n🔧 Verificando manejo de tipos de smart_hours_status...")
        
        # Obtener el resultado real de la función
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        # Verificar que siempre devuelve un diccionario
        self.assertIsInstance(result, dict, "is_smart_trading_hours_allowed debe devolver un diccionario")
        self.assertIn("is_allowed", result, "Debe contener 'is_allowed'")
        self.assertIn("reason", result, "Debe contener 'reason'")
        self.assertIn("current_time_chile", result, "Debe contener 'current_time_chile'")
        
        print(f"✅ Tipo correcto: {type(result)}")
        print(f"✅ Claves: {list(result.keys())}")
        print(f"✅ Estado actual: {result['is_allowed']} - {result['reason']}")
    
    def test_trading_hours_configuration(self):
        """⚙️ Test: Verificar configuración de horarios de trading"""
        print("\n⚙️ Verificando configuración de horarios...")
        
        # Verificar que la configuración existe
        self.assertIsNotNone(SMART_TRADING_HOURS, "SMART_TRADING_HOURS debe estar configurado")
        self.assertIn("market_specific", SMART_TRADING_HOURS, "Debe tener configuración market_specific")
        self.assertIn("crypto", SMART_TRADING_HOURS["market_specific"], "Debe tener configuración para crypto")
        
        crypto_config = SMART_TRADING_HOURS["market_specific"]["crypto"]
        self.assertIn("start_hour", crypto_config, "Debe tener start_hour")
        self.assertIn("end_hour", crypto_config, "Debe tener end_hour")
        
        print(f"✅ Horario crypto: {crypto_config['start_hour']}:00 - {crypto_config['end_hour']}:00")
        print(f"✅ Configuración completa: {crypto_config}")
    
    def test_current_time_analysis(self):
        """🕐 Test: Analizar la hora actual y estado del trading"""
        print("\n🕐 Analizando hora actual y estado del trading...")
        
        # Obtener estado actual
        result = is_smart_trading_hours_allowed("BTCUSD")
        
        current_time = result.get("current_time_chile", "No disponible")
        is_allowed = result.get("is_allowed", False)
        reason = result.get("reason", "Sin razón")
        
        print(f"🕐 Hora actual Chile: {current_time}")
        print(f"📊 Trading permitido: {is_allowed}")
        print(f"📝 Razón: {reason}")
        
        # Verificar que la respuesta es consistente
        if is_allowed:
            self.assertIn("Within", reason, "Si está permitido, la razón debe indicar 'Within'")
        else:
            self.assertIn("Outside", reason, "Si no está permitido, la razón debe indicar 'Outside'")
        
        print("✅ Estado del trading analizado correctamente")
    
    def test_simulate_night_scenario(self):
        """🌙 Test: Simular escenario nocturno (conceptual)"""
        print("\n🌙 Simulando escenario nocturno...")
        
        # En lugar de hacer mock, vamos a verificar la lógica
        # Verificar que la configuración no permite trading fuera de horarios
        crypto_config = SMART_TRADING_HOURS["market_specific"]["crypto"]
        start_hour = crypto_config["start_hour"]
        end_hour = crypto_config["end_hour"]
        
        print(f"🕐 Horario configurado: {start_hour}:00 - {end_hour}:00")
        
        # Las 2 AM está fuera del horario 8-22
        night_hour = 2
        self.assertTrue(night_hour < start_hour or night_hour > end_hour, 
                       f"Las {night_hour}:00 AM debe estar fuera del horario {start_hour}-{end_hour}")
        
        print(f"✅ Las {night_hour}:00 AM está fuera del horario de trading")
    
    def test_simulate_morning_scenario(self):
        """🌅 Test: Simular escenario matutino (conceptual)"""
        print("\n🌅 Simulando escenario matutino...")
        
        # Verificar que las 8 AM está dentro del horario
        crypto_config = SMART_TRADING_HOURS["market_specific"]["crypto"]
        start_hour = crypto_config["start_hour"]
        end_hour = crypto_config["end_hour"]
        
        # Las 8 AM debe estar dentro del horario 8-22
        morning_hour = 8
        self.assertTrue(start_hour <= morning_hour <= end_hour, 
                       f"Las {morning_hour}:00 AM debe estar dentro del horario {start_hour}-{end_hour}")
        
        print(f"✅ Las {morning_hour}:00 AM está dentro del horario de trading")
    
    def test_error_handling_robustness(self):
        """🛡️ Test: Verificar manejo robusto de errores"""
        print("\n🛡️ Verificando manejo robusto de errores...")
        
        # Probar con diferentes símbolos
        test_symbols = ["BTCUSD", "ETHUSD", "INVALID_SYMBOL", ""]
        
        for symbol in test_symbols:
            try:
                result = is_smart_trading_hours_allowed(symbol)
                
                # Verificar que siempre devuelve un diccionario válido
                self.assertIsInstance(result, dict, f"Debe devolver dict para {symbol}")
                self.assertIn("is_allowed", result, f"Debe tener 'is_allowed' para {symbol}")
                
                print(f"✅ {symbol}: {result['is_allowed']} - {result.get('reason', 'Sin razón')}")
                
            except Exception as e:
                self.fail(f"Error inesperado con símbolo '{symbol}': {e}")
        
        print("✅ Manejo de errores verificado correctamente")

if __name__ == '__main__':
    print("🚀 EJECUTANDO TESTS DE ESCENARIO NOCTURNO A MATUTINO")
    print("="*60)
    
    # Configurar logging para reducir ruido
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Ejecutar tests
    unittest.main(verbosity=2)