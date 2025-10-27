"""
Pruebas unitarias para el filtro de cooldown del TradingBot.

Estas pruebas verifican que el sistema de cooldown funcione correctamente
para evitar trades inmediatos del mismo símbolo y señales opuestas.
"""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta


class MockTradingSignal:
    """Mock de TradingSignal para las pruebas."""
    
    def __init__(self, symbol: str, signal_type: str, confidence: float = 85.0):
        self.symbol = symbol
        self.signal_type = signal_type
        self.confidence_score = confidence
        self.entry_price = 100.0
        self.stop_loss = 95.0
        self.take_profit = 105.0
        self.timestamp = datetime.now()
        self.strategy_name = "test_strategy"
        self.timeframe = "1h"


class MockTradingBot:
    """Mock simplificado del TradingBot para probar solo la lógica de cooldown."""
    
    def __init__(self):
        # Configuración de cooldown (simulando perfil SCALPING)
        self.min_time_between_trades_minutes = 5
        self.min_time_between_opposite_signals_minutes = 10
        
        # Tracking de trades
        self.last_trade_times = {}
        self.last_signal_types = {}
        
        # Mock del logger
        self.logger = Mock()
    
    def _check_trade_cooldown(self, signal: MockTradingSignal) -> bool:
        """
        Verificar si una señal debe ser filtrada por cooldown.
        
        Returns:
            True si la señal puede ejecutarse, False si debe ser filtrada
        """
        symbol = signal.symbol
        current_time = datetime.now()
        
        # Si no hay trades previos para este símbolo, permitir
        if symbol not in self.last_trade_times:
            return True
        
        last_trade_time = self.last_trade_times[symbol]
        last_signal_type = self.last_signal_types.get(symbol)
        
        # Calcular tiempo transcurrido
        time_diff = current_time - last_trade_time
        minutes_passed = time_diff.total_seconds() / 60
        
        # Verificar cooldown básico entre trades del mismo símbolo
        if minutes_passed < self.min_time_between_trades_minutes:
            self.logger.info(f"⏳ {symbol}: Trade filtrado por cooldown básico. "
                           f"Tiempo restante: {self.min_time_between_trades_minutes - minutes_passed:.1f} min")
            return False
        
        # Verificar cooldown extendido para señales opuestas
        if (last_signal_type and 
            last_signal_type != signal.signal_type and 
            minutes_passed < self.min_time_between_opposite_signals_minutes):
            self.logger.info(f"⏳ {symbol}: Señal opuesta filtrada por cooldown extendido. "
                           f"Tiempo restante: {self.min_time_between_opposite_signals_minutes - minutes_passed:.1f} min")
            return False
        
        return True
    
    def _update_trade_tracking(self, signal: MockTradingSignal):
        """Actualizar el tracking de trades para cooldown."""
        symbol = signal.symbol
        self.last_trade_times[symbol] = datetime.now()
        self.last_signal_types[symbol] = signal.signal_type
        
        self.logger.info(f"📊 Tracking actualizado para {symbol}: {signal.signal_type}")


class TestCooldownFilter(unittest.TestCase):
    """Pruebas para el filtro de cooldown del TradingBot."""
    
    def setUp(self):
        """Configuración inicial para cada prueba."""
        self.bot = MockTradingBot()
    
    def test_first_trade_allowed(self):
        """Verificar que el primer trade de un símbolo sea permitido."""
        signal = MockTradingSignal("BTCUSD", "BUY")
        
        # El primer trade debe ser permitido
        result = self.bot._check_trade_cooldown(signal)
        self.assertTrue(result, "El primer trade debe ser permitido")
    
    def test_same_symbol_cooldown_respected(self):
        """Verificar que se respete el cooldown entre trades del mismo símbolo."""
        symbol = "ETHUSD"
        
        # Primer trade
        first_signal = MockTradingSignal(symbol, "BUY")
        self.bot._update_trade_tracking(first_signal)
        
        # Segundo trade inmediato del mismo símbolo (debe ser rechazado)
        second_signal = MockTradingSignal(symbol, "BUY")
        result = self.bot._check_trade_cooldown(second_signal)
        self.assertFalse(result, "El segundo trade inmediato debe ser rechazado por cooldown")
    
    def test_same_symbol_cooldown_expired(self):
        """Verificar que el cooldown expire después del tiempo configurado."""
        symbol = "ADAUSD"
        
        # Simular primer trade hace 6 minutos (más que el cooldown de 5 minutos)
        past_time = datetime.now() - timedelta(minutes=6)
        self.bot.last_trade_times[symbol] = past_time
        self.bot.last_signal_types[symbol] = "BUY"
        
        # Nuevo trade debe ser permitido
        signal = MockTradingSignal(symbol, "BUY")
        result = self.bot._check_trade_cooldown(signal)
        self.assertTrue(result, "El trade debe ser permitido después de que expire el cooldown")
    
    def test_opposite_signal_cooldown_respected(self):
        """Verificar que se respete el cooldown entre señales opuestas."""
        symbol = "SOLUSD"
        
        # Primer trade BUY
        first_signal = MockTradingSignal(symbol, "BUY")
        self.bot._update_trade_tracking(first_signal)
        
        # Señal SELL inmediata (debe ser rechazada por cooldown de señales opuestas)
        opposite_signal = MockTradingSignal(symbol, "SELL")
        result = self.bot._check_trade_cooldown(opposite_signal)
        self.assertFalse(result, "La señal opuesta inmediata debe ser rechazada por cooldown")
    
    def test_opposite_signal_cooldown_expired(self):
        """Verificar que el cooldown de señales opuestas expire después del tiempo configurado."""
        symbol = "DOTUSD"
        
        # Simular primer trade BUY hace 11 minutos (más que el cooldown de 10 minutos)
        past_time = datetime.now() - timedelta(minutes=11)
        self.bot.last_trade_times[symbol] = past_time
        self.bot.last_signal_types[symbol] = "BUY"
        
        # Señal SELL debe ser permitida
        opposite_signal = MockTradingSignal(symbol, "SELL")
        result = self.bot._check_trade_cooldown(opposite_signal)
        self.assertTrue(result, "La señal opuesta debe ser permitida después de que expire el cooldown")
    
    def test_same_direction_signal_within_cooldown(self):
        """Verificar que señales en la misma dirección respeten el cooldown básico."""
        symbol = "LINKUSD"
        
        # Primer trade BUY
        first_signal = MockTradingSignal(symbol, "BUY")
        self.bot._update_trade_tracking(first_signal)
        
        # Segunda señal BUY inmediata (debe ser rechazada por cooldown básico)
        same_signal = MockTradingSignal(symbol, "BUY")
        result = self.bot._check_trade_cooldown(same_signal)
        self.assertFalse(result, "La segunda señal en la misma dirección debe ser rechazada por cooldown")
    
    def test_different_symbols_no_interference(self):
        """Verificar que el cooldown de un símbolo no afecte a otros símbolos."""
        # Trade en BTCUSD
        btc_signal = MockTradingSignal("BTCUSD", "BUY")
        self.bot._update_trade_tracking(btc_signal)
        
        # Trade inmediato en ETHUSD debe ser permitido
        eth_signal = MockTradingSignal("ETHUSD", "BUY")
        result = self.bot._check_trade_cooldown(eth_signal)
        self.assertTrue(result, "El cooldown de un símbolo no debe afectar a otros símbolos")
    
    def test_update_trade_tracking(self):
        """Verificar que el tracking se actualice correctamente."""
        symbol = "AVAXUSD"
        signal = MockTradingSignal(symbol, "SELL")
        
        # Verificar estado inicial
        self.assertNotIn(symbol, self.bot.last_trade_times)
        self.assertNotIn(symbol, self.bot.last_signal_types)
        
        # Actualizar tracking
        self.bot._update_trade_tracking(signal)
        
        # Verificar que se actualizó
        self.assertIn(symbol, self.bot.last_trade_times)
        self.assertIn(symbol, self.bot.last_signal_types)
        self.assertEqual(self.bot.last_signal_types[symbol], "SELL")
        
        # Verificar que el timestamp es reciente (menos de 1 segundo de diferencia)
        time_diff = datetime.now() - self.bot.last_trade_times[symbol]
        self.assertLess(time_diff.total_seconds(), 1.0)
    
    def test_cooldown_timing_precision(self):
        """Verificar la precisión del timing del cooldown."""
        symbol = "MATICUSD"
        
        # Simular trade hace exactamente 5 minutos (límite del cooldown básico)
        exact_time = datetime.now() - timedelta(minutes=5, seconds=1)  # 1 segundo extra
        self.bot.last_trade_times[symbol] = exact_time
        self.bot.last_signal_types[symbol] = "BUY"
        
        # Debe ser permitido (justo después del límite)
        signal = MockTradingSignal(symbol, "BUY")
        result = self.bot._check_trade_cooldown(signal)
        self.assertTrue(result, "El trade debe ser permitido justo después del límite de cooldown")
        
        # Simular trade hace menos de 5 minutos
        recent_time = datetime.now() - timedelta(minutes=4, seconds=59)  # 1 segundo menos
        self.bot.last_trade_times[symbol] = recent_time
        
        # Debe ser rechazado (justo antes del límite)
        result = self.bot._check_trade_cooldown(signal)
        self.assertFalse(result, "El trade debe ser rechazado justo antes del límite de cooldown")


if __name__ == '__main__':
    unittest.main()