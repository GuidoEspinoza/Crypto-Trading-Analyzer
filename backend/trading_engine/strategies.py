"""
🧠 Universal Trading Analyzer - Trading Strategies
Estrategias de trading automático basadas en análisis técnico
"""

import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Importar indicadores directamente
from advanced_indicators import AdvancedIndicators

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar exchange
exchange = ccxt.binance({
    'sandbox': False,
    'enableRateLimit': True,
})

@dataclass
class TradingSignal:
    """
    🎯 Señal de trading generada por una estrategia
    """
    symbol: str
    strategy_name: str
    signal_type: str  # BUY, SELL, HOLD
    price: float
    confidence_score: float
    strength: str  # Weak, Moderate, Strong, Very Strong
    timestamp: datetime
    indicators_data: Dict
    notes: str = ""
    # Atributos adicionales para compatibilidad con enhanced_risk_manager
    volume_confirmation: bool = False
    market_regime: str = "NORMAL"  # TRENDING, RANGING, VOLATILE
    stop_loss_price: float = 0.0
    risk_reward_ratio: float = 0.0

class TradingStrategy(ABC):
    """
    🧠 Clase base abstracta para todas las estrategias de trading
    """
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.min_confidence = 60.0  # Mínima confianza para ejecutar trade
        self.advanced_indicators = AdvancedIndicators()
        
    @abstractmethod
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """
        🔍 Analizar símbolo y generar señal de trading
        
        Args:
            symbol: Par de trading (ej: BTC/USDT)
            timeframe: Marco temporal (1h, 4h, 1d)
            
        Returns:
            TradingSignal: Señal generada por la estrategia
        """
        pass
    
    def get_market_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        """
        📊 Obtener datos del mercado directamente
        
        Args:
            symbol: Par de trading
            timeframe: Marco temporal
            limit: Número de velas
            
        Returns:
            pd.DataFrame: Datos OHLCV
        """
        try:
            # Convertir formato de símbolo
            if "/" in symbol:
                symbol = symbol.replace("/", "")
            
            # Obtener datos históricos
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            # Crear DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error getting market data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_current_price(self, symbol: str) -> float:
        """
        💰 Obtener precio actual
        """
        try:
            if "/" in symbol:
                symbol = symbol.replace("/", "")
            
            ticker = exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"❌ Error getting price for {symbol}: {e}")
            return 0.0

class RSIStrategy(TradingStrategy):
    """
    📊 Estrategia basada en RSI (Relative Strength Index)
    
    Reglas:
    - BUY: RSI < 30 (oversold)
    - SELL: RSI > 70 (overbought)
    - Confirmación con volumen y precio
    """
    
    def __init__(self):
        super().__init__("RSI_Strategy")
        self.oversold_threshold = 30
        self.overbought_threshold = 70
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """
        🔍 Analizar con estrategia RSI
        """
        try:
            # Obtener datos del mercado
            df = self.get_market_data(symbol, timeframe)
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data available")
            
            # Calcular RSI
            df['rsi'] = ta.rsi(df['close'], length=14)
            current_rsi = df['rsi'].iloc[-1]
            
            if pd.isna(current_rsi):
                return self._create_hold_signal(symbol, "RSI calculation failed")
            
            # Lógica de la estrategia RSI
            if current_rsi <= self.oversold_threshold:
                signal_type = "BUY"
                confidence = self._calculate_buy_confidence(current_rsi, df)
                strength = self._get_signal_strength(confidence)
                notes = f"🟢 RSI oversold ({current_rsi:.1f}) - Strong buy signal"
                
            elif current_rsi >= self.overbought_threshold:
                signal_type = "SELL"
                confidence = self._calculate_sell_confidence(current_rsi, df)
                strength = self._get_signal_strength(confidence)
                notes = f"🔴 RSI overbought ({current_rsi:.1f}) - Strong sell signal"
                
            else:
                signal_type = "HOLD"
                confidence = 40.0
                strength = "Weak"
                notes = f"⚪ RSI neutral ({current_rsi:.1f}) - No clear signal"
            
            return TradingSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=confidence,
                strength=strength,
                timestamp=datetime.now(),
                indicators_data={
                    "rsi": current_rsi,
                    "timeframe": timeframe,
                    "oversold_threshold": self.oversold_threshold,
                    "overbought_threshold": self.overbought_threshold,
                    "price": current_price
                },
                notes=notes
            )
            
        except Exception as e:
            logger.error(f"❌ Error in RSI strategy analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _calculate_buy_confidence(self, rsi: float, df: pd.DataFrame) -> float:
        """
        📈 Calcular confianza para señal de compra
        """
        base_confidence = 60.0
        
        # Más oversold = más confianza
        if rsi <= 20:
            base_confidence += 30.0
        elif rsi <= 25:
            base_confidence += 20.0
        elif rsi <= 30:
            base_confidence += 10.0
        
        # Verificar volumen (si está disponible)
        if len(df) > 5:
            recent_volume = df['volume'].tail(5).mean()
            avg_volume = df['volume'].mean()
            if recent_volume > avg_volume * 1.2:  # Volumen alto
                base_confidence += 10.0
        
        return min(95.0, base_confidence)
    
    def _calculate_sell_confidence(self, rsi: float, df: pd.DataFrame) -> float:
        """
        📉 Calcular confianza para señal de venta
        """
        base_confidence = 60.0
        
        # Más overbought = más confianza
        if rsi >= 80:
            base_confidence += 30.0
        elif rsi >= 75:
            base_confidence += 20.0
        elif rsi >= 70:
            base_confidence += 10.0
        
        # Verificar volumen
        if len(df) > 5:
            recent_volume = df['volume'].tail(5).mean()
            avg_volume = df['volume'].mean()
            if recent_volume > avg_volume * 1.2:
                base_confidence += 10.0
        
        return min(95.0, base_confidence)
    
    def _get_signal_strength(self, confidence: float) -> str:
        """💪 Convertir confidence score a strength"""
        if confidence >= 85: return "Very Strong"
        elif confidence >= 70: return "Strong"
        elif confidence >= 55: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> TradingSignal:
        """⚪ Crear señal HOLD por defecto"""
        return TradingSignal(
            symbol=symbol, strategy_name=self.name, signal_type="HOLD",
            price=0.0, confidence_score=0.0, strength="None",
            timestamp=datetime.now(), indicators_data={}, notes=f"⚪ HOLD: {reason}"
        )

class MACDStrategy(TradingStrategy):
    """
    📊 Estrategia basada en MACD (Moving Average Convergence Divergence)
    """
    
    def __init__(self):
        super().__init__("MACD_Strategy")
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """
        🔍 Analizar con estrategia MACD
        """
        try:
            # Obtener datos del mercado
            df = self.get_market_data(symbol, timeframe)
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data available")
            
            # Calcular MACD
            macd_data = ta.macd(df['close'])
            
            if macd_data is None or macd_data.empty:
                return self._create_hold_signal(symbol, "MACD calculation failed")
            
            macd_line = macd_data['MACD_12_26_9'].iloc[-1]
            signal_line = macd_data['MACDs_12_26_9'].iloc[-1]
            histogram = macd_data['MACDh_12_26_9'].iloc[-1]
            
            # Verificar valores válidos
            if pd.isna(macd_line) or pd.isna(signal_line) or pd.isna(histogram):
                return self._create_hold_signal(symbol, "Invalid MACD values")
            
            # Lógica MACD
            if macd_line > signal_line and histogram > 0:
                signal_type = "BUY"
                confidence = self._calculate_macd_confidence(histogram, "BUY")
                notes = f"🟢 MACD bullish crossover - MACD({macd_line:.4f}) > Signal({signal_line:.4f})"
                
            elif macd_line < signal_line and histogram < 0:
                signal_type = "SELL"
                confidence = self._calculate_macd_confidence(histogram, "SELL")
                notes = f"🔴 MACD bearish crossover - MACD({macd_line:.4f}) < Signal({signal_line:.4f})"
                
            else:
                signal_type = "HOLD"
                confidence = 45.0
                notes = f"⚪ MACD neutral - No clear crossover signal"
            
            return TradingSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=confidence,
                strength=self._get_signal_strength(confidence),
                timestamp=datetime.now(),
                indicators_data={
                    "macd_line": macd_line,
                    "signal_line": signal_line,
                    "histogram": histogram,
                    "timeframe": timeframe,
                    "price": current_price
                },
                notes=notes
            )
            
        except Exception as e:
            logger.error(f"❌ Error in MACD strategy analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _calculate_macd_confidence(self, histogram: float, signal_type: str) -> float:
        """📊 Calcular confianza basada en MACD"""
        base_confidence = 55.0
        hist_abs = abs(histogram)
        
        # Mayor histograma = mayor confianza
        if hist_abs > 0.01:
            base_confidence += 25.0
        elif hist_abs > 0.005:
            base_confidence += 15.0
        elif hist_abs > 0.001:
            base_confidence += 10.0
        
        return min(90.0, base_confidence)
    
    def _get_signal_strength(self, confidence: float) -> str:
        """💪 Convertir confidence a strength"""
        if confidence >= 80: return "Very Strong"
        elif confidence >= 65: return "Strong"
        elif confidence >= 50: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> TradingSignal:
        """⚪ Crear señal HOLD"""
        return TradingSignal(
            symbol=symbol, strategy_name=self.name, signal_type="HOLD",
            price=0.0, confidence_score=0.0, strength="None",
            timestamp=datetime.now(), indicators_data={}, notes=f"⚪ HOLD: {reason}"
        )

class IchimokuStrategy(TradingStrategy):
    """
    ☁️ Estrategia basada en Ichimoku Cloud (simplificada)
    """
    
    def __init__(self):
        super().__init__("Ichimoku_Strategy")
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """
        🔍 Analizar con estrategia Ichimoku (versión simplificada)
        """
        try:
            # Obtener datos del mercado
            df = self.get_market_data(symbol, timeframe, limit=52)  # Necesitamos más datos para Ichimoku
            current_price = self.get_current_price(symbol)
            
            if df.empty or len(df) < 26 or current_price == 0:
                return self._create_hold_signal(symbol, "Insufficient data for Ichimoku")
            
            # Calcular Ichimoku básico
            high_9 = df['high'].rolling(window=9).max()
            low_9 = df['low'].rolling(window=9).min()
            tenkan_sen = (high_9 + low_9) / 2
            
            high_26 = df['high'].rolling(window=26).max()
            low_26 = df['low'].rolling(window=26).min()
            kijun_sen = (high_26 + low_26) / 2
            
            # Obtener valores actuales
            current_tenkan = tenkan_sen.iloc[-1]
            current_kijun = kijun_sen.iloc[-1]
            
            if pd.isna(current_tenkan) or pd.isna(current_kijun):
                return self._create_hold_signal(symbol, "Invalid Ichimoku values")
            
            # Lógica Ichimoku simplificada
            if current_price > current_tenkan and current_tenkan > current_kijun:
                signal_type = "BUY"
                confidence = 70.0
                notes = f"🟢 Ichimoku bullish - Price above Tenkan, Tenkan > Kijun"
                
            elif current_price < current_tenkan and current_tenkan < current_kijun:
                signal_type = "SELL"
                confidence = 70.0
                notes = f"🔴 Ichimoku bearish - Price below Tenkan, Tenkan < Kijun"
                
            else:
                signal_type = "HOLD"
                confidence = 40.0
                notes = f"⚪ Ichimoku neutral - Mixed signals"
            
            return TradingSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=confidence,
                strength=self._get_signal_strength(confidence),
                timestamp=datetime.now(),
                indicators_data={
                    "tenkan_sen": current_tenkan,
                    "kijun_sen": current_kijun,
                    "price": current_price,
                    "timeframe": timeframe
                },
                notes=notes
            )
            
        except Exception as e:
            logger.error(f"❌ Error in Ichimoku strategy analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _get_signal_strength(self, confidence: float) -> str:
        """💪 Convertir confidence a strength"""
        if confidence >= 80: return "Very Strong"
        elif confidence >= 65: return "Strong"  
        elif confidence >= 50: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> TradingSignal:
        """⚪ Crear señal HOLD"""
        return TradingSignal(
            symbol=symbol, strategy_name=self.name, signal_type="HOLD",
            price=0.0, confidence_score=0.0, strength="None",
            timestamp=datetime.now(), indicators_data={}, notes=f"⚪ HOLD: {reason}"
        )