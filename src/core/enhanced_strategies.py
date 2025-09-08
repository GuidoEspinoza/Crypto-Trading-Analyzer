"""🚀 Enhanced Trading Strategies - Versión Profesional
Estrategias de trading mejoradas con análisis multi-indicador,
confirmación de volumen y gestión avanzada de riesgo.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
import warnings
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from functools import lru_cache
import hashlib
import time

from src.config.config import StrategyConfig

# Clases base para estrategias de trading
@dataclass
class TradingSignal:
    """📊 Señal de trading generada por una estrategia"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    price: float
    confidence_score: float
    strength: str  # Weak, Moderate, Strong, Very Strong
    strategy_name: str
    timestamp: datetime
    indicators_data: Dict = None
    notes: str = ""

class TradingStrategy(ABC):
    """🧠 Clase base abstracta para todas las estrategias de trading"""
    
    def __init__(self, name: str):
        self.name = name
        self.is_active = True
        self.config = StrategyConfig.Base()  # Configuración base centralizada
        self.min_confidence = StrategyConfig.Base.DEFAULT_MIN_CONFIDENCE  # Mínima confianza desde config
        self.advanced_indicators = AdvancedIndicators()
    
    @abstractmethod
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """Analizar símbolo y generar señal"""
        pass
    
    def get_market_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        """Obtener datos de mercado"""
        import ccxt
        exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Establecer timestamp como índice y ordenar por datetime
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def get_current_price(self, symbol: str) -> float:
        """Obtener precio actual del símbolo"""
        try:
            import ccxt
            exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
            ticker = exchange.fetch_ticker(symbol)
            return float(ticker['last']) if ticker['last'] else 0.0
        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {e}")
            # Fallback: usar el último precio de los datos históricos
            try:
                df = self.get_market_data(symbol, "1m", limit=1)
                return float(df['close'].iloc[-1]) if not df.empty else 0.0
            except:
                return 0.0

# Importar AdvancedIndicators con path absoluto
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from .advanced_indicators import AdvancedIndicators

# Importación circular evitada - se importará dinámicamente cuando sea necesario
# from .signal_filters import AdvancedSignalFilter, FilteredSignal

logger = logging.getLogger(__name__)

@dataclass
class EnhancedSignal(TradingSignal):
    """Señal de trading mejorada con información adicional"""
    volume_confirmation: bool = False
    trend_confirmation: str = "NEUTRAL"  # BULLISH, BEARISH, NEUTRAL
    risk_reward_ratio: float = 0.0
    stop_loss_price: float = 0.0
    take_profit_price: float = 0.0
    market_regime: str = "NORMAL"  # TRENDING, RANGING, VOLATILE
    confluence_score: int = 0  # Número de indicadores que confirman la señal

class EnhancedTradingStrategy(TradingStrategy):
    """Clase base para estrategias mejoradas con optimizaciones de cache"""
    
    # Cache compartido entre instancias
    _cache = {}
    _cache_timestamps = {}
    _cache_ttl = 300  # 5 minutos TTL
    
    def __init__(self, name: str, enable_filters: bool = True):
        super().__init__(name)
        self.min_volume_ratio = 1.2  # Volumen debe ser 20% mayor al promedio
        self.min_confluence = 2  # Mínimo 2 indicadores deben confirmar
        # Signal filters deshabilitados (módulo eliminado)
        self.signal_filter = None
        
        # Configuración avanzada de confluencia
        self.confluence_weights = {
            "technical": 0.4,    # Indicadores técnicos
            "volume": 0.25,      # Análisis de volumen
            "structure": 0.2,    # Estructura de mercado (S/R, tendencias)
            "momentum": 0.15     # Momentum e impulso
        }
        self.min_confluence_score = 0.65  # Puntuación mínima de confluencia
    
    @classmethod
    def _get_cache_key(cls, method_name: str, *args, **kwargs) -> str:
        """Generar clave de cache única para método y parámetros"""
        try:
            # Crear hash de los argumentos
            key_data = f"{method_name}_{str(args)}_{str(sorted(kwargs.items()))}"
            return hashlib.md5(key_data.encode()).hexdigest()
        except Exception:
            return f"{method_name}_{time.time()}"
    
    @classmethod
    def _get_from_cache(cls, cache_key: str):
        """Obtener valor del cache si es válido"""
        current_time = time.time()
        if (cache_key in cls._cache and 
            cache_key in cls._cache_timestamps and
            current_time - cls._cache_timestamps[cache_key] < cls._cache_ttl):
            return cls._cache[cache_key]
        return None
    
    @classmethod
    def _store_in_cache(cls, cache_key: str, value):
        """Almacenar valor en cache con timestamp"""
        cls._cache[cache_key] = value
        cls._cache_timestamps[cache_key] = time.time()
        
        # Limpiar cache viejo si es necesario
        if len(cls._cache) > 1000:  # Límite de entradas
            cls._cleanup_cache()
    
    @classmethod
    def _cleanup_cache(cls):
        """Limpiar entradas viejas del cache"""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in cls._cache_timestamps.items()
            if current_time - timestamp >= cls._cache_ttl
        ]
        for key in expired_keys:
            cls._cache.pop(key, None)
            cls._cache_timestamps.pop(key, None)
        
    def analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analizar volumen avanzado para confirmación de señales con cache"""
        try:
            if 'volume' not in df.columns:
                return {"volume_confirmation": False, "volume_ratio": 0.0, "volume_strength": "WEAK"}
            
            # Generar clave de cache basada en los últimos datos de volumen
            volume_data = df['volume'].tail(50).values
            cache_key = self._get_cache_key("analyze_volume", str(volume_data.tobytes()))
            
            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Cálculos optimizados
            volume_series = df['volume']
            current_volume = volume_series.iloc[-1]
            
            # Usar vectorización para mejor rendimiento
            rolling_20 = volume_series.rolling(20, min_periods=10)
            rolling_50 = volume_series.rolling(50, min_periods=25)
            
            avg_volume_20 = rolling_20.mean().iloc[-1]
            avg_volume_50 = rolling_50.mean().iloc[-1]
            
            if pd.isna(avg_volume_20) or avg_volume_20 == 0:
                return {"volume_confirmation": False, "volume_ratio": 0.0, "volume_strength": "WEAK"}
            
            # Ratios de volumen múltiples
            volume_ratio_20 = current_volume / avg_volume_20
            volume_ratio_50 = current_volume / avg_volume_50 if not pd.isna(avg_volume_50) and avg_volume_50 > 0 else 0
            
            # Análisis de tendencia de volumen
            volume_trend = df['volume'].rolling(10).mean().pct_change(5).iloc[-1]
            
            # Análisis de volumen por precio (VWAP deviation) - optimizado
            hlc3 = (df['high'] + df['low'] + df['close']) / 3
            volume_price = (volume_series * hlc3).cumsum()
            volume_cumsum = volume_series.cumsum()
            vwap = volume_price / volume_cumsum
            vwap_deviation = abs(df['close'].iloc[-1] - vwap.iloc[-1]) / vwap.iloc[-1]
            
            # Clasificación de fuerza de volumen
            if volume_ratio_20 >= 2.5:
                volume_strength = "VERY_STRONG"
            elif volume_ratio_20 >= 1.8:
                volume_strength = "STRONG"
            elif volume_ratio_20 >= 1.3:
                volume_strength = "MODERATE"
            else:
                volume_strength = "WEAK"
            
            # Confirmación mejorada
            volume_confirmation = (
                volume_ratio_20 >= self.min_volume_ratio and
                volume_strength in ["STRONG", "VERY_STRONG"] and
                vwap_deviation < 0.02  # Precio cerca del VWAP
            )
            
            result = {
                "volume_confirmation": bool(volume_confirmation),
                "volume_ratio": round(float(volume_ratio_20), 2),
                "volume_ratio_50": round(float(volume_ratio_50), 2),
                "volume_strength": volume_strength,
                "volume_trend": round(float(volume_trend), 4) if not pd.isna(volume_trend) else 0.0,
                "vwap_deviation": round(float(vwap_deviation), 4),
                "current_volume": float(current_volume),
                "avg_volume_20": float(avg_volume_20),
                "avg_volume_50": float(avg_volume_50) if not pd.isna(avg_volume_50) else 0.0
            }
            
            # Almacenar en cache
            self._store_in_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return {"volume_confirmation": False, "volume_ratio": 0.0, "volume_strength": "WEAK"}
    
    def calculate_advanced_confluence(self, signal_data: Dict, signal_type: str) -> Dict:
        """Calcular puntuación de confluencia avanzada con pesos específicos y cache"""
        try:
            # Generar clave de cache
            cache_key = self._get_cache_key("calculate_confluence", str(signal_data), signal_type)
            
            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            confluence_score = 0.0
            confluence_details = {}
            
            # Mapas de valores precalculados para mejor rendimiento
            strength_map = {"VERY_STRONG": 1.0, "STRONG": 0.8, "MODERATE": 0.5, "WEAK": 0.2}
            
            # === ANÁLISIS TÉCNICO (40%) ===
            technical_score = 0.0
            technical_factors = 0
            
            # RSI mejorado
            if "rsi" in signal_data and signal_data["rsi"].get("signal") == signal_type:
                rsi_strength = signal_data["rsi"].get("strength", 0) / 100
                technical_score += rsi_strength * 0.4
                technical_factors += 1
                confluence_details["rsi_contribution"] = rsi_strength * 0.4
            
            # Bollinger Bands
            if "bollinger_bands" in signal_data and signal_data["bollinger_bands"].get("signal") == signal_type:
                bb_confidence = signal_data["bollinger_bands"].get("confidence", 50) / 100
                technical_score += bb_confidence * 0.3
                technical_factors += 1
                confluence_details["bollinger_contribution"] = bb_confidence * 0.3
            
            # VWAP
            if "vwap" in signal_data and signal_data["vwap"].get("signal") == signal_type:
                vwap_strength = signal_data["vwap"].get("strength", 50) / 100
                technical_score += vwap_strength * 0.3
                technical_factors += 1
                confluence_details["vwap_contribution"] = vwap_strength * 0.3
            
            # Normalizar puntuación técnica
            if technical_factors > 0:
                technical_score = technical_score / technical_factors
            
            # === ANÁLISIS DE VOLUMEN (25%) ===
            volume_score = 0.0
            if "volume_analysis" in signal_data:
                vol_data = signal_data["volume_analysis"]
                
                # Fuerza del volumen usando mapa precalculado
                vol_strength = strength_map.get(vol_data.get("volume_strength", "WEAK"), 0.2)
                
                # Confirmación de volumen
                vol_confirmation = 1.0 if vol_data.get("volume_confirmation", False) else 0.3
                
                # Tendencia de volumen
                vol_trend = vol_data.get("volume_trend", 0)
                trend_bonus = 0.2 if (
                    (signal_type == "BUY" and vol_trend > 0) or 
                    (signal_type == "SELL" and vol_trend < 0)
                ) else 0
                
                volume_score = (vol_strength * 0.5 + vol_confirmation * 0.3 + trend_bonus * 0.2)
                confluence_details["volume_contribution"] = volume_score
            
            # === ESTRUCTURA DE MERCADO (20%) ===
            structure_score = 0.0
            structure_factors = 0
            
            # Soporte y Resistencia
            if "support_resistance" in signal_data and signal_data["support_resistance"].get("signal") == signal_type:
                sr_confidence = signal_data["support_resistance"].get("confidence", 50) / 100
                structure_score += sr_confidence * 0.6
                structure_factors += 1
                confluence_details["sr_contribution"] = sr_confidence * 0.6
            
            # Líneas de tendencia
            if "trend_lines" in signal_data and signal_data["trend_lines"].get("signal") == signal_type:
                tl_confidence = signal_data["trend_lines"].get("confidence", 50) / 100
                structure_score += tl_confidence * 0.4
                structure_factors += 1
                confluence_details["trendline_contribution"] = tl_confidence * 0.4
            
            # Normalizar puntuación de estructura
            if structure_factors > 0:
                structure_score = structure_score / structure_factors
            
            # === MOMENTUM (15%) ===
            momentum_score = 0.0
            momentum_factors = 0
            
            # ROC (Rate of Change)
            if "roc" in signal_data and signal_data["roc"].get("signal") == signal_type:
                roc_strength = signal_data["roc"].get("strength", 50) / 100
                momentum_score += roc_strength * 0.5
                momentum_factors += 1
                confluence_details["roc_contribution"] = roc_strength * 0.5
            
            # MFI (Money Flow Index)
            if "mfi" in signal_data and signal_data["mfi"].get("signal") == signal_type:
                mfi_strength = signal_data["mfi"].get("strength", 50) / 100
                momentum_score += mfi_strength * 0.5
                momentum_factors += 1
                confluence_details["mfi_contribution"] = mfi_strength * 0.5
            
            # Normalizar puntuación de momentum
            if momentum_factors > 0:
                momentum_score = momentum_score / momentum_factors
            
            # === CÁLCULO FINAL DE CONFLUENCIA ===
            confluence_score = (
                technical_score * self.confluence_weights["technical"] +
                volume_score * self.confluence_weights["volume"] +
                structure_score * self.confluence_weights["structure"] +
                momentum_score * self.confluence_weights["momentum"]
            )
            
            # Clasificación de confluencia
            confluence_level = "WEAK"
            if confluence_score >= 0.8:
                confluence_level = "VERY_STRONG"
            elif confluence_score >= 0.65:
                confluence_level = "STRONG"
            elif confluence_score >= 0.45:
                confluence_level = "MODERATE"
            
            result = {
                "confluence_score": round(confluence_score, 3),
                "confluence_level": confluence_level,
                "meets_threshold": confluence_score >= self.min_confluence_score,
                "component_scores": {
                    "technical": round(technical_score, 3),
                    "volume": round(volume_score, 3),
                    "structure": round(structure_score, 3),
                    "momentum": round(momentum_score, 3)
                },
                "confluence_details": confluence_details,
                "factors_count": {
                    "technical": technical_factors,
                    "structure": structure_factors,
                    "momentum": momentum_factors
                }
            }
            
            # Almacenar en cache
            self._store_in_cache(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error calculating advanced confluence: {e}")
            return {
                "confluence_score": 0.0,
                "confluence_level": "WEAK",
                "meets_threshold": False,
                "component_scores": {"technical": 0, "volume": 0, "structure": 0, "momentum": 0},
                "confluence_details": {},
                "factors_count": {"technical": 0, "structure": 0, "momentum": 0}
            }
    
    def analyze_trend(self, df: pd.DataFrame) -> str:
        """Analizar tendencia usando múltiples indicadores con cache"""
        try:
            # Generar clave de cache basada en los últimos precios
            price_data = df['close'].tail(50).values
            cache_key = self._get_cache_key("analyze_trend", str(price_data.tobytes()))
            
            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Cálculos optimizados de EMA
            close_series = df['close']
            ema_20 = ta.ema(close_series, length=20)
            ema_50 = ta.ema(close_series, length=50)
            
            if ema_20 is None or ema_50 is None:
                return "NEUTRAL"
            
            current_ema_20 = ema_20.iloc[-1]
            current_ema_50 = ema_50.iloc[-1]
            
            # ADX para fuerza de tendencia
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                adx_data = ta.adx(high_float, low_float, close_float)
            if adx_data is not None and not adx_data.empty:
                adx_value = adx_data['ADX_14'].iloc[-1] if 'ADX_14' in adx_data.columns else 25
            else:
                adx_value = 25
            
            # Determinar tendencia
            if current_ema_20 > current_ema_50 and adx_value > 25:
                result = "BULLISH"
            elif current_ema_20 < current_ema_50 and adx_value > 25:
                result = "BEARISH"
            else:
                result = "NEUTRAL"
            
            # Almacenar en cache
            self._store_in_cache(cache_key, result)
            return result
                
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return "NEUTRAL"
    
    def detect_market_regime(self, df: pd.DataFrame) -> str:
        """Detectar régimen de mercado con cache"""
        try:
            # Generar clave de cache basada en datos OHLC recientes
            ohlc_data = df[['high', 'low', 'close']].tail(50).values
            cache_key = self._get_cache_key("detect_market_regime", str(ohlc_data.tobytes()))
            
            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Calcular volatilidad (ATR) optimizado
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                atr = ta.atr(high_float, low_float, close_float, length=14)
            if atr is None or atr.empty:
                return "NORMAL"
            
            current_atr = atr.iloc[-1]
            avg_atr = atr.rolling(50).mean().iloc[-1]
            
            if pd.isna(current_atr) or pd.isna(avg_atr):
                return "NORMAL"
            
            volatility_ratio = current_atr / avg_atr
            
            # Detectar si está en tendencia o rango
            price_range = df['high'].rolling(20).max().iloc[-1] - df['low'].rolling(20).min().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if volatility_ratio > 1.5:
                result = "VOLATILE"
            elif abs(current_price - (df['high'].rolling(20).max().iloc[-1] + df['low'].rolling(20).min().iloc[-1]) / 2) < price_range * 0.2:
                result = "RANGING"
            else:
                result = "TRENDING"
            
            # Almacenar en cache
            self._store_in_cache(cache_key, result)
            return result
                
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return "NORMAL"
    
    def calculate_risk_reward(self, entry_price: float, signal_type: str, atr: float) -> Tuple[float, float, float]:
        """Calcular stop loss, take profit y ratio riesgo/beneficio
        
        Usa rangos dinámicos desde config.py:
        - Stop Loss: sl_min% - sl_max% del precio de entrada
        - Take Profit: tp_min% - tp_max% del precio de entrada
        """
        try:
            # Importar configuración dinámica
            from src.config.config import RiskManagerConfig
            
            # Obtener rangos dinámicos desde config
            sl_min = RiskManagerConfig.get_sl_min_percentage()
            sl_max = RiskManagerConfig.get_sl_max_percentage()
            tp_min = RiskManagerConfig.get_tp_min_percentage()
            tp_max = RiskManagerConfig.get_tp_max_percentage()
            
            # Calcular porcentaje ATR respecto al precio
            atr_percentage = (atr / entry_price) * 100
            
            # Determinar SL y TP basado en rangos dinámicos
            if signal_type == "BUY":
                # Stop Loss: sl_min%-sl_max% por debajo del precio de entrada
                if atr_percentage <= sl_min:
                    sl_pct = sl_min  # Mínimo dinámico
                elif atr_percentage >= sl_max:
                    sl_pct = sl_max  # Máximo dinámico
                else:
                    sl_pct = atr_percentage  # Usar ATR si está en rango
                
                # Take Profit: tp_min%-tp_max% por encima del precio de entrada
                if atr_percentage * 1.5 <= tp_min:
                    tp_pct = tp_min  # Mínimo dinámico
                elif atr_percentage * 1.5 >= tp_max:
                    tp_pct = tp_max  # Máximo dinámico
                else:
                    tp_pct = atr_percentage * 1.5  # 1.5x ATR si está en rango
                
                stop_loss = entry_price * (1 - sl_pct / 100)
                take_profit = entry_price * (1 + tp_pct / 100)
                
            elif signal_type == "SELL":
                # Stop Loss: sl_min%-sl_max% por encima del precio de entrada
                if atr_percentage <= sl_min:
                    sl_pct = sl_min  # Mínimo dinámico
                elif atr_percentage >= sl_max:
                    sl_pct = sl_max  # Máximo dinámico
                else:
                    sl_pct = atr_percentage  # Usar ATR si está en rango
                
                # Take Profit: tp_min%-tp_max% por debajo del precio de entrada
                if atr_percentage * 1.5 <= tp_min:
                    tp_pct = tp_min  # Mínimo dinámico
                elif atr_percentage * 1.5 >= tp_max:
                    tp_pct = tp_max  # Máximo dinámico
                else:
                    tp_pct = atr_percentage * 1.5  # 1.5x ATR si está en rango
                
                stop_loss = entry_price * (1 + sl_pct / 100)
                take_profit = entry_price * (1 - tp_pct / 100)
            else:
                return 0.0, 0.0, 0.0
            
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            
            if risk > 0:
                risk_reward_ratio = reward / risk
            else:
                risk_reward_ratio = 0.0
                
            return stop_loss, take_profit, risk_reward_ratio
            
        except Exception as e:
            logger.error(f"Error calculating risk/reward: {str(e)}")
            return 0.0, 0.0, 0.0
    
    def analyze_with_filters(self, symbol: str, timeframe: str = "1h"):
        """🔍 Analiza con filtros avanzados aplicados"""
        # Importación dinámica de FilteredSignal
        try:
            from .signal_filters import FilteredSignal
        except ImportError:
            # Fallback para importación directa
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from trading_engine.signal_filters import FilteredSignal
        # Obtener señal original
        original_signal = self.analyze(symbol, timeframe)
        
        # Aplicar filtros si están habilitados
        if self.signal_filter:
            df = self.get_market_data(symbol, timeframe, limit=100)
            return self.signal_filter.filter_signal(original_signal, df)
        else:
            # Sin filtros, crear FilteredSignal básico
            return FilteredSignal(
                original_signal=original_signal,
                filtered_signal=original_signal.signal_type,
                filter_score=100.0,
                filters_passed=["no_filters_enabled"],
                filters_failed=[],
                risk_assessment="MEDIUM",
                quality_grade="B"
            )

class ProfessionalRSIStrategy(EnhancedTradingStrategy):
    """🎯 Estrategia RSI Profesional con confirmaciones múltiples y nuevos indicadores"""
    
    def __init__(self):
        super().__init__("Professional_RSI_Enhanced")
        
        # Configuración desde archivo centralizado
        self.config = StrategyConfig.ProfessionalRSI()
        self.min_confidence = self.config.MIN_CONFIDENCE
        self.rsi_oversold = self.config.RSI_OVERSOLD
        self.rsi_overbought = self.config.RSI_OVERBOUGHT
        self.rsi_period = self.config.RSI_PERIOD
        
        # Configuración de confirmaciones
        self.min_volume_ratio = self.config.MIN_VOLUME_RATIO
        self.min_confluence = self.config.MIN_CONFLUENCE
        self.trend_strength_threshold = self.config.TREND_STRENGTH_THRESHOLD
        
        # Configuración de filtros de calidad
        self.min_atr_ratio = self.config.MIN_ATR_RATIO
        self.max_spread_threshold = self.config.MAX_SPREAD_THRESHOLD
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis RSI profesional con confirmaciones avanzadas"""
        try:
            df = self.get_market_data(symbol, timeframe, limit=100)
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data")
            
            # === INDICADORES PRINCIPALES ===
            # RSI Mejorado con análisis de divergencias
            enhanced_rsi = AdvancedIndicators.enhanced_rsi(df)
            
            # Bollinger Bands para contexto de volatilidad
            bollinger = AdvancedIndicators.bollinger_bands(df)
            
            # VWAP para análisis institucional
            vwap_analysis = AdvancedIndicators.vwap(df)
            
            # === INDICADORES DE VOLUMEN ===
            # On Balance Volume
            obv_analysis = AdvancedIndicators.on_balance_volume(df)
            
            # Money Flow Index
            mfi_analysis = AdvancedIndicators.money_flow_index(df)
            
            # Volume Profile
            volume_profile = AdvancedIndicators.volume_profile(df)
            
            # === INDICADORES DE VOLATILIDAD Y MOMENTUM ===
            # Average True Range
            atr_analysis = AdvancedIndicators.average_true_range(df)
            
            # Rate of Change
            roc_analysis = AdvancedIndicators.rate_of_change(df)
            
            # === ANÁLISIS DE ESTRUCTURA DE MERCADO ===
            # Soporte y Resistencia
            support_resistance = AdvancedIndicators.support_resistance_levels(df)
            
            # Análisis de líneas de tendencia
            trend_lines = AdvancedIndicators.trend_lines_analysis(df)
            
            # Detección de patrones de gráfico
            chart_patterns = AdvancedIndicators.chart_patterns_detection(df)
            
            # Confirmaciones adicionales (indicadores existentes)
            stoch = AdvancedIndicators.stochastic_oscillator(df)
            williams_r = AdvancedIndicators.williams_percent_r(df)
            volume_analysis = self.analyze_volume(df)
            trend = self.analyze_trend(df)
            market_regime = self.detect_market_regime(df)
            
            # ATR para stop loss (usar el nuevo análisis)
            current_atr = atr_analysis["atr"]
            
            # === LÓGICA DE SEÑALES CON CONFLUENCIA AVANZADA ===
            confluence_score = 0
            signal_type = "HOLD"
            confidence = self.config.BASE_CONFIDENCE  # Usar configuración centralizada
            notes = []
            
            # === ANÁLISIS RSI MEJORADO ===
            rsi_signal = enhanced_rsi["signal"]
            if rsi_signal in ["BUY", "STRONG_BUY"]:
                confluence_score += 2 if rsi_signal == "STRONG_BUY" else 1
                signal_type = "BUY"
                confidence += 25 if rsi_signal == "STRONG_BUY" else 15
                notes.append(f"Enhanced RSI: {enhanced_rsi['interpretation']}")
            elif rsi_signal in ["SELL", "STRONG_SELL"]:
                confluence_score += 2 if rsi_signal == "STRONG_SELL" else 1
                signal_type = "SELL"
                confidence += 25 if rsi_signal == "STRONG_SELL" else 15
                notes.append(f"Enhanced RSI: {enhanced_rsi['interpretation']}")
            
            # === CONFIRMACIÓN BOLLINGER BANDS ===
            if bollinger["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 12
                notes.append(f"Bollinger confirms: {bollinger['interpretation']}")
            
            # === CONFIRMACIÓN VWAP ===
            if vwap_analysis["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 10
                notes.append(f"VWAP confirms: {vwap_analysis['interpretation']}")
            
            # === ANÁLISIS DE VOLUMEN AVANZADO ===
            volume_signals = [obv_analysis["signal"], mfi_analysis["signal"], volume_profile["signal"]]
            volume_confirmations = sum(1 for vs in volume_signals if vs == signal_type and signal_type != "HOLD")
            
            if volume_confirmations >= 2:
                confluence_score += 2
                confidence += 20
                notes.append(f"Strong volume confirmation ({volume_confirmations}/3)")
            elif volume_confirmations == 1:
                confluence_score += 1
                confidence += 10
                notes.append("Volume confirmation")
            
            # === MOMENTUM Y VOLATILIDAD ===
            if roc_analysis["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 8
                notes.append(f"ROC momentum: {roc_analysis['interpretation']}")
            
            # Ajustar por volatilidad (ATR)
            if atr_analysis["volatility_level"] == "MUY ALTA":
                confidence -= 15
                notes.append("High volatility warning")
            elif atr_analysis["volatility_level"] == "BAJA":
                confidence += 5
                notes.append("Low volatility favorable")
            
            # === SOPORTE Y RESISTENCIA ===
            if support_resistance["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 15
                notes.append(f"S/R level: {support_resistance['interpretation']}")
            
            # === LÍNEAS DE TENDENCIA ===
            if trend_lines["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 12
                notes.append(f"Trend line: {trend_lines['interpretation']}")
            
            # === PATRONES DE GRÁFICO ===
            if chart_patterns["signal"] == signal_type and signal_type != "HOLD":
                # Determinar fuerza del patrón basado en confianza
                pattern_strength = "STRONG" if any(p.get("confidence", 0) >= 75 for p in chart_patterns.get("patterns", [])) else "MODERATE"
                confluence_score += 2 if pattern_strength == "STRONG" else 1
                confidence += 18 if pattern_strength == "STRONG" else 10
                notes.append(f"Chart pattern: {chart_patterns['interpretation']}")
            
            # === CONFIRMACIONES TRADICIONALES ===
            # Confirmación con Stochastic
            if stoch["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 8
                notes.append("Stochastic confirms")
            
            # Confirmación con Williams %R
            if williams_r["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 6
                notes.append("Williams %R confirms")
            
            # === CONFIRMACIÓN DE TENDENCIA ===
            if (signal_type == "BUY" and trend == "BULLISH") or (signal_type == "SELL" and trend == "BEARISH"):
                confluence_score += 1
                confidence += 15
                notes.append(f"Trend confirms ({trend})")
            
            # Penalizar si va contra la tendencia fuerte
            if (signal_type == "BUY" and trend == "BEARISH") or (signal_type == "SELL" and trend == "BULLISH"):
                confidence -= 20
                notes.append("Against strong trend")
            
            # === FILTROS DE CALIDAD ===
            # Requerir mínimo de confluencia para señales fuertes
            if confluence_score < self.min_confluence and signal_type != "HOLD":
                signal_type = "HOLD"
                confidence = 45
                notes.append(f"Insufficient confluence ({confluence_score}/{self.min_confluence})")
            
            # Ajustar por régimen de mercado
            if market_regime == "VOLATILE":
                confidence -= 10
                notes.append("High volatility")
            elif market_regime == "RANGING" and signal_type != "HOLD":
                confidence += 5
                notes.append("Range-bound market")
            
            # Requiere mínima confluencia
            if confluence_score < self.min_confluence and signal_type != "HOLD":
                signal_type = "HOLD"
                confidence = 45
                notes.append("Insufficient confluence")
            
            # Calcular stop loss y take profit
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, signal_type, current_atr
            )
            
            # Verificar ratio riesgo/beneficio mínimo
            if risk_reward < 1.5 and signal_type != "HOLD":
                signal_type = "HOLD"
                confidence = 40
                notes.append("Poor risk/reward ratio")
            
            return EnhancedSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=min(95, max(0, confidence)),
                strength=self._get_signal_strength(confidence),
                timestamp=datetime.now(),
                indicators_data={
                    # Indicadores tradicionales
                    "rsi": enhanced_rsi,
                    "stochastic": stoch,
                    "williams_r": williams_r,
                    "volume_analysis": volume_analysis,
                    "atr": round(current_atr, 4),
                    "timeframe": timeframe,
                    
                    # Nuevos indicadores avanzados
                    "bollinger_bands": bollinger,
                    "vwap": vwap_analysis,
                    "obv": obv_analysis,
                    "mfi": mfi_analysis,
                    "volume_profile": volume_profile,
                    "roc": roc_analysis,
                    "support_resistance": support_resistance,
                    "atr_analysis": atr_analysis,
                    "volatility_level": atr_analysis["volatility_level"],
                    "trend_lines": trend_lines,
                    "chart_patterns": chart_patterns
                },
                notes=" | ".join(notes) if notes else "No clear signals",
                volume_confirmation=bool(volume_analysis["volume_confirmation"]),
                trend_confirmation=str(trend),
                risk_reward_ratio=round(float(risk_reward), 2),
                stop_loss_price=round(float(stop_loss), 2),
                take_profit_price=round(float(take_profit), 2),
                market_regime=str(market_regime),
                confluence_score=int(confluence_score)
            )
            
        except Exception as e:
            logger.error(f"Error in Professional RSI analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _get_signal_strength(self, confidence: float) -> str:
        """Convertir confidence a strength"""
        if confidence >= 85: return "Very Strong"
        elif confidence >= 70: return "Strong"
        elif confidence >= 55: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> EnhancedSignal:
        """Crear señal HOLD"""
        return EnhancedSignal(
            symbol=symbol,
            strategy_name=self.name,
            signal_type="HOLD",
            price=0.0,
            confidence_score=0.0,
            strength="None",
            timestamp=datetime.now(),
            indicators_data={},
            notes=f"HOLD: {reason}",
            volume_confirmation=False,
            trend_confirmation="NEUTRAL",
            risk_reward_ratio=0.0,
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            confluence_score=0
        )

class MultiTimeframeStrategy(EnhancedTradingStrategy):
    """📊 Estrategia Multi-Timeframe para confirmación de tendencia"""
    
    def __init__(self):
        super().__init__("Multi_Timeframe")
        
        # Configuración desde archivo centralizado
        self.config = StrategyConfig.MultiTimeframe()
        self.timeframes = self.config.TIMEFRAMES
        self.min_confidence = self.config.MIN_CONFIDENCE
        self.rsi_config = self.config.RSI_CONFIG
        self.timeframe_weights = self.config.TIMEFRAME_WEIGHTS
        self.min_timeframe_consensus = self.config.MIN_TIMEFRAME_CONSENSUS
        self.trend_alignment_required = self.config.TREND_ALIGNMENT_REQUIRED
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis multi-timeframe"""
        try:
            signals = {}
            trends = {}
            
            # Analizar cada timeframe
            for tf in self.timeframes:
                try:
                    df = self.get_market_data(symbol, tf, limit=50)
                    if not df.empty:
                        trends[tf] = self.analyze_trend(df)
                        
                        # RSI para cada timeframe
                        # Convertir a float64 para evitar warnings de dtype
                        close_float = df['close'].astype('float64')
                        
                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore', FutureWarning)
                            warnings.simplefilter('ignore', UserWarning)
                            rsi = ta.rsi(close_float, length=14)
                        if rsi is not None:
                            rsi_value = rsi.iloc[-1]
                            rsi_thresholds = self.rsi_config.get(tf, self.rsi_config.get("1h", {"oversold": 30, "overbought": 70}))
                            if rsi_value <= rsi_thresholds["oversold"]:
                                signals[tf] = "BUY"
                            elif rsi_value >= rsi_thresholds["overbought"]:
                                signals[tf] = "SELL"
                            else:
                                signals[tf] = "HOLD"
                        else:
                            signals[tf] = "HOLD"
                    else:
                        signals[tf] = "HOLD"
                        trends[tf] = "NEUTRAL"
                except Exception as e:
                    logger.warning(f"Error analyzing {tf}: {e}")
                    signals[tf] = "HOLD"
                    trends[tf] = "NEUTRAL"
            
            # Determinar señal consenso
            buy_votes = sum(1 for s in signals.values() if s == "BUY")
            sell_votes = sum(1 for s in signals.values() if s == "SELL")
            
            # Ponderar por timeframe (mayor peso a timeframes más largos)
            weights = {"1h": 1, "4h": 2, "1d": 3}
            weighted_buy = sum(weights.get(tf, 1) for tf, signal in signals.items() if signal == "BUY")
            weighted_sell = sum(weights.get(tf, 1) for tf, signal in signals.items() if signal == "SELL")
            
            current_price = self.get_current_price(symbol)
            df_main = self.get_market_data(symbol, timeframe)
            
            if weighted_buy > weighted_sell and buy_votes >= 2:
                signal_type = "BUY"
                confidence = self.config.ENHANCED_CONFIDENCE + (weighted_buy * 5)
            elif weighted_sell > weighted_buy and sell_votes >= 2:
                signal_type = "SELL"
                confidence = self.config.ENHANCED_CONFIDENCE + (weighted_sell * 5)
            else:
                signal_type = "HOLD"
                confidence = self.config.HOLD_CONFIDENCE
            
            # Análisis de volumen y otros factores
            volume_analysis = self.analyze_volume(df_main) if not df_main.empty else {"volume_confirmation": False}
            market_regime = self.detect_market_regime(df_main) if not df_main.empty else "NORMAL"
            
            # ATR para stop loss
            # Convertir a float64 para evitar warnings de dtype
            high_float = df_main['high'].astype('float64')
            low_float = df_main['low'].astype('float64')
            close_float = df_main['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                atr = ta.atr(high_float, low_float, close_float, length=StrategyConfig.Base.DEFAULT_ATR_PERIOD)
            current_atr = atr.iloc[-1] if atr is not None else current_price * 0.02
            
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, signal_type, current_atr
            )
            
            return EnhancedSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=min(95, confidence),
                strength=self._get_signal_strength(confidence),
                timestamp=datetime.now(),
                indicators_data={
                    "timeframe_signals": signals,
                    "timeframe_trends": trends,
                    "buy_votes": buy_votes,
                    "sell_votes": sell_votes,
                    "weighted_buy": weighted_buy,
                    "weighted_sell": weighted_sell,
                    "volume_analysis": volume_analysis
                },
                notes=f"Multi-TF: {buy_votes}B/{sell_votes}S votes, Trends: {trends}",
                volume_confirmation=bool(volume_analysis.get("volume_confirmation", False)),
                trend_confirmation=str(trends.get("1d", "NEUTRAL")),
                risk_reward_ratio=round(float(risk_reward), 2),
                stop_loss_price=round(float(stop_loss), 2),
                take_profit_price=round(float(take_profit), 2),
                market_regime=str(market_regime),
                confluence_score=int(buy_votes + sell_votes)
            )
            
        except Exception as e:
            logger.error(f"Error in Multi-Timeframe analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _get_signal_strength(self, confidence: float) -> str:
        if confidence >= 85: return "Very Strong"
        elif confidence >= 70: return "Strong"
        elif confidence >= 55: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> EnhancedSignal:
        return EnhancedSignal(
            symbol=symbol, strategy_name=self.name, signal_type="HOLD",
            price=0.0, confidence_score=0.0, strength="None",
            timestamp=datetime.now(), indicators_data={}, notes=f"HOLD: {reason}",
            volume_confirmation=False, trend_confirmation="NEUTRAL",
            risk_reward_ratio=0.0, stop_loss_price=0.0, take_profit_price=0.0,
            market_regime="NORMAL", confluence_score=0
        )

class EnsembleStrategy(EnhancedTradingStrategy):
    """🎯 Estrategia Ensemble - Combina múltiples estrategias con votación inteligente"""
    
    def __init__(self):
        super().__init__("Ensemble_Master")
        
        # Configuración desde archivo centralizado
        self.config = StrategyConfig.Ensemble()
        
        # Inicializar sub-estrategias
        self.rsi_strategy = ProfessionalRSIStrategy()
        self.mtf_strategy = MultiTimeframeStrategy()
        
        # Pesos para cada estrategia (basado en performance histórica)
        self.strategy_weights = self.config.STRATEGY_WEIGHTS
        
        # Configuración de consenso
        self.min_consensus_threshold = self.config.MIN_CONSENSUS_THRESHOLD
        self.confidence_boost_factor = self.config.CONFIDENCE_BOOST_FACTOR
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis ensemble combinando múltiples estrategias"""
        try:
            # Obtener señales de todas las estrategias
            signals = {}
            
            # RSI Profesional
            try:
                rsi_signal = self.rsi_strategy.analyze(symbol, timeframe)
                signals["Professional_RSI"] = rsi_signal
            except Exception as e:
                logger.warning(f"Error in RSI strategy: {e}")
                signals["Professional_RSI"] = None
            
            # Multi-Timeframe
            try:
                mtf_signal = self.mtf_strategy.analyze(symbol, timeframe)
                signals["Multi_Timeframe"] = mtf_signal
            except Exception as e:
                logger.warning(f"Error in MTF strategy: {e}")
                signals["Multi_Timeframe"] = None
            
            # Análisis adicional propio
            df = self.get_market_data(symbol, timeframe, limit=100)
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data")
            
            # Análisis de patrones de velas
            candlestick_patterns = AdvancedIndicators.detect_candlestick_patterns(df)
            
            # Análisis de momentum (Awesome Oscillator)
            ao_analysis = AdvancedIndicators.awesome_oscillator(df)
            
            # Análisis de volumen
            volume_analysis = self.analyze_volume(df)
            
            # Análisis de tendencia
            trend = self.analyze_trend(df)
            
            # Régimen de mercado
            market_regime = self.detect_market_regime(df)
            
            # Combinar señales usando votación ponderada
            ensemble_result = self._combine_signals(signals, {
                "candlestick": candlestick_patterns,
                "awesome_oscillator": ao_analysis,
                "volume": volume_analysis,
                "trend": trend,
                "market_regime": market_regime
            })
            
            # ATR para stop loss
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                atr = ta.atr(high_float, low_float, close_float, length=14)
            current_atr = atr.iloc[-1] if atr is not None else current_price * 0.02
            
            # Calcular stop loss y take profit
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, ensemble_result["signal_type"], current_atr
            )
            
            # Verificar ratio riesgo/beneficio
            if risk_reward < 2.0 and ensemble_result["signal_type"] != "HOLD":
                ensemble_result["signal_type"] = "HOLD"
                ensemble_result["confidence"] = 40
                ensemble_result["notes"].append("Poor risk/reward ratio")
            
            return EnhancedSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=ensemble_result["signal_type"],
                price=current_price,
                confidence_score=ensemble_result["confidence"],
                strength=self._get_signal_strength(ensemble_result["confidence"]),
                timestamp=datetime.now(),
                indicators_data={
                    "strategy_signals": {k: v.signal_type if v else "ERROR" for k, v in signals.items()},
                    "strategy_confidences": {k: v.confidence_score if v else 0 for k, v in signals.items()},
                    "candlestick_patterns": candlestick_patterns,
                    "awesome_oscillator": ao_analysis,
                    "volume_analysis": volume_analysis,
                    "ensemble_consensus": ensemble_result["consensus"],
                    "weighted_score": ensemble_result["weighted_score"],
                    "timeframe": timeframe
                },
                notes=" | ".join(ensemble_result["notes"]),
                volume_confirmation=bool(volume_analysis.get("volume_confirmation", False)),
                trend_confirmation=str(trend),
                risk_reward_ratio=round(float(risk_reward), 2),
                stop_loss_price=round(float(stop_loss), 2),
                take_profit_price=round(float(take_profit), 2),
                market_regime=str(market_regime),
                confluence_score=int(ensemble_result["confluence_score"])
            )
            
        except Exception as e:
            logger.error(f"Error in Ensemble analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _combine_signals(self, strategy_signals: Dict, additional_analysis: Dict) -> Dict:
        """Combinar señales usando votación ponderada inteligente"""
        try:
            # Inicializar contadores
            buy_score = 0.0
            sell_score = 0.0
            total_weight = 0.0
            notes = []
            confluence_score = 0
            
            # Procesar señales de estrategias principales
            for strategy_name, signal in strategy_signals.items():
                if signal is None:
                    continue
                    
                weight = self.strategy_weights.get(strategy_name, 0.3)
                confidence_factor = signal.confidence_score / 100.0
                weighted_contribution = weight * confidence_factor
                
                if signal.signal_type == "BUY":
                    buy_score += weighted_contribution
                    confluence_score += 1
                    notes.append(f"{strategy_name}: BUY ({signal.confidence_score:.1f}%)")
                elif signal.signal_type == "SELL":
                    sell_score += weighted_contribution
                    confluence_score += 1
                    notes.append(f"{strategy_name}: SELL ({signal.confidence_score:.1f}%)")
                else:
                    notes.append(f"{strategy_name}: HOLD")
                
                total_weight += weight
            
            # Análisis de patrones de velas (peso menor)
            candlestick_weight = 0.15
            for pattern in additional_analysis["candlestick"]["patterns"]:
                if pattern["signal"] == "BUY":
                    buy_score += candlestick_weight * 0.7
                    notes.append(f"Candlestick: {pattern['name']} (BUY)")
                    confluence_score += 1
                elif pattern["signal"] == "SELL":
                    sell_score += candlestick_weight * 0.7
                    notes.append(f"Candlestick: {pattern['name']} (SELL)")
                    confluence_score += 1
            
            # Awesome Oscillator (peso menor)
            ao_weight = 0.1
            ao_signal = additional_analysis["awesome_oscillator"]["signal"]
            if ao_signal == "BUY":
                buy_score += ao_weight
                notes.append("AO: Bullish momentum")
                confluence_score += 1
            elif ao_signal == "SELL":
                sell_score += ao_weight
                notes.append("AO: Bearish momentum")
                confluence_score += 1
            
            # Confirmación de volumen (boost)
            volume_boost = 1.0
            if additional_analysis["volume"]["volume_confirmation"]:
                volume_boost = 1.2
                notes.append(f"Volume confirms ({additional_analysis['volume']['volume_ratio']}x avg)")
                confluence_score += 1
            
            # Aplicar boost de volumen
            buy_score *= volume_boost
            sell_score *= volume_boost
            
            # Penalización por régimen de mercado
            market_regime = additional_analysis["market_regime"]
            if market_regime == "VOLATILE":
                buy_score *= 0.8
                sell_score *= 0.8
                notes.append("High volatility penalty")
            elif market_regime == "RANGING":
                # En mercados laterales, preferir señales de reversión
                buy_score *= 1.1
                sell_score *= 1.1
                notes.append("Range-bound market boost")
            
            # Determinar señal final
            total_score = buy_score + sell_score
            if total_score == 0:
                consensus = 0.5
                signal_type = "HOLD"
                confidence = self.config.HOLD_CONFIDENCE
            else:
                consensus = max(buy_score, sell_score) / total_score
                
                if buy_score > sell_score and consensus >= self.min_consensus_threshold:
                    signal_type = "BUY"
                    confidence = min(95, self.config.BASE_CONFIDENCE + (buy_score * 40))
                elif sell_score > buy_score and consensus >= self.min_consensus_threshold:
                    signal_type = "SELL"
                    confidence = min(95, self.config.BASE_CONFIDENCE + (sell_score * 40))
                else:
                    signal_type = "HOLD"
                    confidence = StrategyConfig.Base.HOLD_CONFIDENCE
                    notes.append(f"Insufficient consensus ({consensus:.1%})")
            
            # Boost de confianza por consenso alto
            if consensus >= 0.8:
                confidence *= self.confidence_boost_factor
                confidence = min(95, confidence)
                notes.append(f"High consensus boost ({consensus:.1%})")
            
            return {
                "signal_type": signal_type,
                "confidence": round(confidence, 1),
                "consensus": round(consensus, 3),
                "weighted_score": round(total_score, 3),
                "buy_score": round(buy_score, 3),
                "sell_score": round(sell_score, 3),
                "confluence_score": confluence_score,
                "notes": notes
            }
            
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return {
                "signal_type": "HOLD",
                "confidence": 0,
                "consensus": 0,
                "weighted_score": 0,
                "buy_score": 0,
                "sell_score": 0,
                "confluence_score": 0,
                "notes": [f"Error combining signals: {str(e)}"]
            }
    
    def _get_signal_strength(self, confidence: float) -> str:
        """Convertir confidence a strength"""
        if confidence >= 90: return "Very Strong"
        elif confidence >= 75: return "Strong"
        elif confidence >= 60: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> EnhancedSignal:
        """Crear señal HOLD"""
        return EnhancedSignal(
            symbol=symbol,
            strategy_name=self.name,
            signal_type="HOLD",
            price=0.0,
            confidence_score=0.0,
            strength="None",
            timestamp=datetime.now(),
            indicators_data={},
            notes=f"HOLD: {reason}",
            volume_confirmation=False,
            trend_confirmation="NEUTRAL",
            risk_reward_ratio=0.0,
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            confluence_score=0
        )