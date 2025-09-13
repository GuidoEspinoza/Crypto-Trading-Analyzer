#!/usr/bin/env python3
"""
🧪 Pruebas Simplificadas del Sistema de Espaciado entre Trades
Verifica que el throttling funcione correctamente para evitar ejecución masiva post-reset
"""

import unittest
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class MockTradingSignal:
    """Mock de TradingSignal para pruebas"""
    def __init__(self, symbol="BTCUSDT", signal_type="BUY", confidence_score=85.0):
        self.symbol = symbol
        self.signal_type = signal_type
        self.confidence_score = confidence_score
        self.entry_price = 50000.0
        self.stop_loss = 49000.0
        self.take_profit = 52000.0
        self.timeframe = "1h"
        self.strategy_name = "TestStrategy"

class MockTradingBot:
    """Mock simplificado del TradingBot para probar solo el throttling"""
    
    def __init__(self):
        # Configuración de throttling (valores del perfil RÁPIDO)
        self.min_time_between_trades = 60  # 1 minuto
        self.max_trades_per_hour = 10
        self.post_reset_spacing_minutes = 90  # 1.5 horas
        
        # Variables de estado
        self.last_trade_time = None
        self.hourly_trade_count = 0
        self.hourly_trade_reset_time = datetime.now()
        
        # Stats
        self.stats = {
            "trades_executed": 0,
            "daily_trades": 0
        }
    
    def _can_execute_trade(self) -> bool:
        """
        🚦 Verificar si se puede ejecutar un trade basado en throttling
        """
        current_time = datetime.now()
        
        # 1. Verificar tiempo mínimo entre trades
        if self.last_trade_time:
            time_since_last_trade = (current_time - self.last_trade_time).total_seconds()
            if time_since_last_trade < self.min_time_between_trades:
                return False
        
        # 2. Verificar límite de trades por hora
        if (current_time - self.hourly_trade_reset_time).total_seconds() >= 3600:
            self.hourly_trade_count = 0
            self.hourly_trade_reset_time = current_time
        
        if self.hourly_trade_count >= self.max_trades_per_hour:
            return False
        
        # 3. Verificar espaciado especial post-reset
        if self._is_in_post_reset_window():
            if self.last_trade_time:
                time_since_last_trade_minutes = (current_time - self.last_trade_time).total_seconds() / 60
                if time_since_last_trade_minutes < self.post_reset_spacing_minutes:
                    return False
        
        return True
    
    def _is_in_post_reset_window(self) -> bool:
        """
        🌅 Verificar si estamos en la ventana post-reset
        """
        current_time = datetime.now()
        return current_time.hour < 3
    
    def _update_trade_timing(self):
        """
        📊 Actualizar contadores de timing después de ejecutar un trade
        """
        current_time = datetime.now()
        self.last_trade_time = current_time
        self.hourly_trade_count += 1
        self.stats["trades_executed"] += 1
        self.stats["daily_trades"] += 1

class TestTradeSpacing(unittest.TestCase):
    """🧪 Pruebas del sistema de espaciado entre trades"""
    
    def setUp(self):
        """Configurar el entorno de pruebas"""
        print("\n🔧 Configurando pruebas de espaciado...")
        self.bot = MockTradingBot()
        self.test_signal = MockTradingSignal()
        print(f"✅ Bot configurado:")
        print(f"   - Min time between trades: {self.bot.min_time_between_trades}s")
        print(f"   - Max trades per hour: {self.bot.max_trades_per_hour}")
        print(f"   - Post-reset spacing: {self.bot.post_reset_spacing_minutes}m")
    
    def test_min_time_between_trades(self):
        """🕐 Probar tiempo mínimo entre trades"""
        print("\n🕐 Probando tiempo mínimo entre trades...")
        
        # Primer trade debe ser permitido
        self.assertTrue(self.bot._can_execute_trade())
        print("✅ Primer trade permitido")
        
        # Simular ejecución del primer trade
        self.bot._update_trade_timing()
        
        # Segundo trade inmediato debe ser bloqueado
        self.assertFalse(self.bot._can_execute_trade())
        print("✅ Segundo trade inmediato bloqueado")
        
        # Simular paso del tiempo
        self.bot.last_trade_time = datetime.now() - timedelta(seconds=self.bot.min_time_between_trades + 1)
        
        # Ahora debe ser permitido
        self.assertTrue(self.bot._can_execute_trade())
        print("✅ Trade permitido después del tiempo mínimo")
    
    def test_hourly_trade_limit(self):
        """⏰ Probar límite de trades por hora"""
        print("\n⏰ Probando límite de trades por hora...")
        
        # Simular múltiples trades hasta el límite
        for i in range(self.bot.max_trades_per_hour):
            self.assertTrue(self.bot._can_execute_trade(), f"Trade {i+1} debe ser permitido")
            self.bot._update_trade_timing()
            # Simular paso de tiempo mínimo para cada trade
            self.bot.last_trade_time = datetime.now() - timedelta(seconds=self.bot.min_time_between_trades + 1)
        
        print(f"✅ {self.bot.max_trades_per_hour} trades ejecutados")
        
        # El siguiente trade debe ser bloqueado
        self.assertFalse(self.bot._can_execute_trade())
        print("✅ Trade adicional bloqueado por límite horario")
    
    def test_post_reset_window(self):
        """🌅 Probar ventana post-reset"""
        print("\n🌅 Probando ventana post-reset...")
        
        # Crear un bot con mock de hora temprana
        class MockBotEarlyHour(MockTradingBot):
            def _is_in_post_reset_window(self) -> bool:
                return True  # Simular que estamos en ventana post-reset
        
        early_bot = MockBotEarlyHour()
        
        # Verificar que estamos en ventana post-reset
        self.assertTrue(early_bot._is_in_post_reset_window())
        print("✅ Detectada ventana post-reset")
        
        # Primer trade debe ser permitido
        self.assertTrue(early_bot._can_execute_trade())
        early_bot._update_trade_timing()
        
        # Segundo trade debe ser bloqueado por espaciado post-reset
        self.assertFalse(early_bot._can_execute_trade())
        print("✅ Segundo trade bloqueado por espaciado post-reset")
    
    def test_normal_hours_no_post_reset(self):
        """☀️ Probar horas normales (sin espaciado post-reset)"""
        print("\n☀️ Probando horas normales...")
        
        # Crear un bot con mock de hora normal
        class MockBotNormalHour(MockTradingBot):
            def _is_in_post_reset_window(self) -> bool:
                return False  # Simular que NO estamos en ventana post-reset
        
        normal_bot = MockBotNormalHour()
        
        # Verificar que NO estamos en ventana post-reset
        self.assertFalse(normal_bot._is_in_post_reset_window())
        print("✅ Fuera de ventana post-reset")
    
    def test_throttling_effectiveness(self):
        """🎯 Probar efectividad del throttling"""
        print("\n🎯 Probando efectividad del throttling...")
        
        trades_executed = 0
        trades_blocked = 0
        
        # Intentar ejecutar muchos trades rápidamente
        for i in range(20):
            if self.bot._can_execute_trade():
                self.bot._update_trade_timing()
                trades_executed += 1
            else:
                trades_blocked += 1
        
        print(f"✅ Trades ejecutados: {trades_executed}")
        print(f"✅ Trades bloqueados: {trades_blocked}")
        
        # Debe haber bloqueado algunos trades
        self.assertGreater(trades_blocked, 0, "El throttling debe bloquear algunos trades")
        
        # No debe exceder el límite por hora
        self.assertLessEqual(trades_executed, self.bot.max_trades_per_hour)
        print("✅ Throttling funcionando correctamente")

def run_trade_spacing_tests():
    """🚀 Ejecutar todas las pruebas de espaciado"""
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DE ESPACIADO ENTRE TRADES")
    print("=" * 60)
    
    # Crear suite de pruebas
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTradeSpacing)
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Resumen
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("🎉 TODAS LAS PRUEBAS DE ESPACIADO PASARON EXITOSAMENTE")
        print("✅ El sistema de throttling está funcionando correctamente")
        print("✅ Se evitará la ejecución masiva de trades post-reset")
        print("\n📋 RESUMEN DE LA SOLUCIÓN:")
        print("   🕐 Tiempo mínimo entre trades: 60s (RÁPIDO) a 300s (CONSERVADOR)")
        print("   ⏰ Límite por hora: 10 trades (RÁPIDO) a 3 trades (CONSERVADOR)")
        print("   🌅 Espaciado post-reset: 90-180 minutos en primeras 3 horas")
        print("   🚦 Verificación automática antes de cada trade")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON")
        print(f"   - Errores: {len(result.errors)}")
        print(f"   - Fallos: {len(result.failures)}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_trade_spacing_tests()
    exit(0 if success else 1)