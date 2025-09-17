"""🚀 Enhanced Trading Strategies - Versión Profesional
Estrategias de trading mejoradas con análisis multi-indicador,
confirmación de volumen y gestión avanzada de riesgo.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
import warnings
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod
from functools import lru_cache
import hashlib
import time

from src.config.config_manager import ConfigManager
from src.config.config import TechnicalAnalysisConfig, StrategyConfig

# Configuración centralizada
try:
    config_manager = ConfigManager()
    config = config_manager.get_consolidated_config()
    if config is None:
        config = {}
    
    # Importar constantes de confianza desde StrategyConfig.Base
    BASE_CONFIDENCE = StrategyConfig.Base.BASE_CONFIDENCE
    HOLD_CONFIDENCE = StrategyConfig.Base.HOLD_CONFIDENCE
    
except Exception as e:
    # Configuración de fallback en caso de error
    config = {
        'fibonacci': {'retracement_levels': [0.236, 0.382, 0.500, 0.618, 0.786]},
        'advanced_indicators': {
            'ichimoku_tenkan_period': 9,
            'ichimoku_kijun_period': 26,
            'ichimoku_shift': 26,
            'ichimoku_senkou_b_period': 52,
            'stochastic_k_period': 14,
            'stochastic_d_period': 3
        },
        'oscillator': {
            'stochastic_thresholds': {'oversold': 20, 'overbought': 80},
            'williams_r_thresholds': {'oversold': -80, 'overbought': -20},
            'cci_thresholds': {'oversold': -100, 'overbought': 100},
            'rsi_thresholds': {'oversold_extreme': 20, 'oversold': 30, 'overbought': 70, 'overbought_extreme': 80},
            'roc_thresholds': {'strong_positive': 5.0, 'moderate_positive': 2.0, 'moderate_negative': -2.0, 'strong_negative': -5.0}
        },
        'calculation': {
            'cci_constant': 0.015,
            'approximation_factors': {'close': 0.98, 'far': 1.02, 'very_close': 0.995}
        },
        'threshold': {
            'proximity_threshold': 0.01,
            'breakout_threshold': 0.02
        }
    }
    
    # Constantes de fallback
    BASE_CONFIDENCE = 50.0
    HOLD_CONFIDENCE = 45.0
    ENHANCED_CONFIDENCE = 60.0

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
        self.min_confidence = 65.0  # Mínima confianza por defecto
        self.advanced_indicators = AdvancedIndicators()
    
    @abstractmethod
    def analyze(self, symbol: str, timeframe: str = None) -> TradingSignal:
        """Analizar símbolo y generar señal"""
        pass
    
    def get_market_data(self, symbol: str, timeframe: str = None, limit: int = 100) -> pd.DataFrame:
        """Obtener datos de mercado"""
        # Usar timeframe del perfil activo si no se especifica
        if timeframe is None:
            from src.config.config import TradingBotConfig
            trading_config = TradingBotConfig()
            timeframe = trading_config.get_primary_timeframe()
        
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
            # Fallback: usar el último precio de los datos históricos con timeframe primario
            try:
                from src.config.config import TradingBotConfig
                trading_config = TradingBotConfig()
                primary_timeframe = trading_config.get_primary_timeframe()
                df = self.get_market_data(symbol, primary_timeframe, limit=1)
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
    timeframe: str = None  # Timeframe de la señal (se asignará dinámicamente)
    
    # Nuevos campos para gestión temporal
    expected_duration_hours: float = 0.0  # Duración esperada del trade en horas
    max_hold_time_hours: float = 0.0  # Tiempo máximo de retención antes de salida forzada
    time_based_exit_enabled: bool = False  # Si está habilitada la salida por tiempo

class EnhancedTradingStrategy(TradingStrategy):
    """Clase base para estrategias mejoradas con optimizaciones de cache"""
    
    # Cache compartido entre instancias
    _cache = {}
    _cache_timestamps = {}
    _cache_ttl = 300  # TTL por defecto: 5 minutos
    
    def __init__(self, name: str, enable_filters: bool = True):
        super().__init__(name)
        # Configuración desde ConfigManager
        self.min_volume_ratio = 1.2  # Valor por defecto
        self.min_confluence = 0.6  # Valor por defecto
        # Signal filters deshabilitados (módulo eliminado)
        self.signal_filter = None
        
        # Configuración avanzada de confluencia con valores por defecto
        self.confluence_weights = {
            'rsi': 0.25, 'macd': 0.25, 'bollinger': 0.25, 'volume': 0.25
        }
        self.min_confluence_score = 0.7
    
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
        if len(cls._cache) > 1000:  # Límite por defecto
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
            rolling_20 = volume_series.rolling(20, min_periods=10)  # Período medio por defecto
            rolling_50 = volume_series.rolling(50, min_periods=25)  # Período largo por defecto
            
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
            
            # Clasificación de fuerza de volumen con umbrales por defecto
            if volume_ratio_20 >= 3.0:  # Umbral muy fuerte
                volume_strength = "VERY_STRONG"
            elif volume_ratio_20 >= 2.0:  # Umbral fuerte
                volume_strength = "STRONG"
            elif volume_ratio_20 >= 1.5:  # Umbral moderado
                volume_strength = "MODERATE"
            else:
                volume_strength = "WEAK"
            
            # Confirmación mejorada
            volume_confirmation = (
                volume_ratio_20 >= self.min_volume_ratio and
                volume_strength in ["STRONG", "VERY_STRONG"] and
                vwap_deviation < 0.02  # Precio cerca del VWAP (2% por defecto)
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
            ema_20 = ta.ema(close_series, length=TechnicalAnalysisConfig.EMA_PERIODS["fast"])
            ema_50 = ta.ema(close_series, length=TechnicalAnalysisConfig.EMA_PERIODS["slow"])
            
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
            if current_ema_20 > current_ema_50 and adx_value > TechnicalAnalysisConfig.ADX_THRESHOLDS["strong_trend"]:
                result = "UPTREND"
            elif current_ema_20 < current_ema_50 and adx_value > TechnicalAnalysisConfig.ADX_THRESHOLDS["strong_trend"]:
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
                from src.config.config_manager import ConfigManager
                config = ConfigManager().get_consolidated_config()
                atr = ta.atr(high_float, low_float, close_float, length=config.get("strategy", {}).get("base", {}).get("default_atr_period", 14))
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
            
            if volatility_ratio > TechnicalAnalysisConfig.VOLATILITY_RATIO_THRESHOLD:
                result = "VOLATILE"
            elif abs(current_price - (df['high'].rolling(TechnicalAnalysisConfig.VOLUME_PERIODS["medium"]).max().iloc[-1] + df['low'].rolling(TechnicalAnalysisConfig.VOLUME_PERIODS["medium"]).min().iloc[-1]) / 2) < price_range * TechnicalAnalysisConfig.PRICE_RANGE_TOLERANCE:
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
        
        Usa rangos dinámicos desde config["py"]:
        - Stop Loss: sl_min% - sl_max% del precio de entrada
        - Take Profit: tp_min% - tp_max% del precio de entrada
        """
        try:
            # Importar configuración del perfil activo
            from src.config.config_manager import ConfigManager
            
            # Obtener configuración del perfil activo (AGRESIVO)
            risk_config = ConfigManager.get_module_config('risk_manager')
            
            # Usar los valores configurados en el perfil AGRESIVO
            sl_percentage = risk_config.get('stop_loss_percentage', 2.5)  # 2.5% para AGRESIVO
            tp_percentage = risk_config.get('take_profit_percentage', 5.5)  # 5.5% para AGRESIVO
            
            # Usar valores fijos del perfil AGRESIVO
            if signal_type == "BUY":
                # Para compras: SL 2.5% abajo, TP 5.5% arriba
                stop_loss = entry_price * (1 - sl_percentage / 100)
                take_profit = entry_price * (1 + tp_percentage / 100)
                
            elif signal_type == "SELL":
                # Para ventas: SL 2.5% arriba, TP 5.5% abajo
                stop_loss = entry_price * (1 + sl_percentage / 100)
                take_profit = entry_price * (1 - tp_percentage / 100)
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
    
    def calculate_time_based_parameters(self, timeframe: str, signal_type: str) -> tuple:
        """
        🕐 Calcular parámetros temporales basados en el timeframe
        
        Args:
            timeframe: Timeframe del análisis (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            signal_type: Tipo de señal (BUY/SELL)
            
        Returns:
            tuple: (expected_duration_hours, max_hold_time_hours, time_based_exit_enabled)
        """
        try:
            # Mapeo de timeframes a duración esperada (en horas)
            timeframe_duration_map = {
                # Timeframes cortos - trades rápidos
                "1m": {"expected": 0.5, "max_hold": 2.0},      # 30 min esperado, máx 2h
                "3m": {"expected": 1.0, "max_hold": 4.0},      # 1h esperado, máx 4h
                "5m": {"expected": 2.0, "max_hold": 8.0},      # 2h esperado, máx 8h
                "15m": {"expected": 4.0, "max_hold": 12.0},    # 4h esperado, máx 12h
                "30m": {"expected": 8.0, "max_hold": 24.0},    # 8h esperado, máx 1 día
                
                # Timeframes medios - trades de medio plazo
                "1h": {"expected": 12.0, "max_hold": 48.0},    # 12h esperado, máx 2 días
                "2h": {"expected": 24.0, "max_hold": 72.0},    # 1 día esperado, máx 3 días
                "4h": {"expected": 48.0, "max_hold": 168.0},   # 2 días esperado, máx 1 semana
                
                # Timeframes largos - trades de largo plazo
                "6h": {"expected": 72.0, "max_hold": 240.0},   # 3 días esperado, máx 10 días
                "8h": {"expected": 96.0, "max_hold": 336.0},   # 4 días esperado, máx 2 semanas
                "12h": {"expected": 168.0, "max_hold": 504.0}, # 1 semana esperado, máx 3 semanas
                "1d": {"expected": 240.0, "max_hold": 720.0},  # 10 días esperado, máx 1 mes
                "3d": {"expected": 504.0, "max_hold": 1440.0}, # 3 semanas esperado, máx 2 meses
                "1w": {"expected": 1008.0, "max_hold": 2160.0} # 6 semanas esperado, máx 3 meses
            }
            
            # Obtener configuración del perfil activo
            from src.config.config_manager import ConfigManager
            profile_config = ConfigManager.get_consolidated_config()
            
            # Verificar si la salida basada en tiempo está habilitada en el perfil
            time_based_config = profile_config.get("advanced_optimizations", {}).get("time_based_exits", {})
            time_based_exit_enabled = time_based_config.get("enabled", True)  # Habilitado por defecto
            
            # Obtener duración base del timeframe
            duration_config = timeframe_duration_map.get(timeframe, {"expected": 24.0, "max_hold": 72.0})
            
            expected_duration = duration_config["expected"]
            max_hold_time = duration_config["max_hold"]
            
            # Ajustar según el perfil activo
            profile_name = ConfigManager.get_active_profile()
            
            if profile_name == "RAPIDO":
                # Perfil rápido: reducir tiempos en 40%
                expected_duration *= 0.6
                max_hold_time *= 0.6
            elif profile_name == "AGRESIVO":
                # Perfil agresivo: reducir tiempos en 20%
                expected_duration *= 0.8
                max_hold_time *= 0.8
            elif profile_name == "OPTIMO":
                # Perfil óptimo: mantener tiempos estándar
                pass  # Sin cambios
            elif profile_name == "CONSERVADOR":
                # Perfil conservador: aumentar tiempos en 50%
                expected_duration *= 1.5
                max_hold_time *= 1.5
            
            # Ajustar según tipo de señal (opcional)
            signal_multiplier = time_based_config.get("signal_type_multiplier", {})
            if signal_type in signal_multiplier:
                multiplier = signal_multiplier[signal_type]
                expected_duration *= multiplier
                max_hold_time *= multiplier
            
            return expected_duration, max_hold_time, time_based_exit_enabled
            
        except Exception as e:
            logger.error(f"Error calculating time-based parameters: {str(e)}")
            # Valores por defecto seguros
            return 24.0, 72.0, False
    
    def analyze_with_filters(self, symbol: str, timeframe: str = None):
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
            from src.config.config import DataLimitsConfig
            df = self.get_market_data(symbol, timeframe, limit=DataLimitsConfig.get_strategy_limit())
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
    
    def apply_multiple_confirmation_filters(self, signal_data: Dict[str, Any], df: pd.DataFrame) -> Dict[str, Any]:
        """🔍 Aplica filtros de confirmación múltiple para validar señales de trading
        
        Args:
            signal_data: Datos de la señal original
            df: DataFrame con datos OHLCV
            
        Returns:
            Dict con resultado de filtros y puntuación de confirmación
        """
        try:
            # Obtener configuración de optimizaciones avanzadas
            from src.config.config_manager import ConfigManager
            config = ConfigManager().get_consolidated_config()
            advanced_opts = config.get("advanced_optimizations", {})
            
            # Configuración de filtros
            filter_config = advanced_opts.get("confirmation_filters", {
                "min_confirmations": 3,
                "volume_confirmation": True,
                "trend_confirmation": True,
                "momentum_confirmation": True,
                "volatility_filter": True,
                "support_resistance_filter": True
            })
            
            confirmations = []
            confirmation_scores = {}
            
            # === 1. FILTRO DE VOLUMEN ===
            if filter_config.get("volume_confirmation", True):
                volume_analysis = self.analyze_volume(df)
                if volume_analysis.get("volume_trend") == "INCREASING":
                    confirmations.append("volume_increasing")
                    confirmation_scores["volume"] = 85.0
                elif volume_analysis.get("relative_volume", 1.0) > 1.2:
                    confirmations.append("volume_above_average")
                    confirmation_scores["volume"] = 70.0
                else:
                    confirmation_scores["volume"] = 30.0
            
            # === 2. FILTRO DE TENDENCIA ===
            if filter_config.get("trend_confirmation", True):
                trend = self.analyze_trend(df)
                signal_type = signal_data.get("signal_type", "HOLD")
                
                if (signal_type == "BUY" and trend == "UPTREND") or \
                   (signal_type == "SELL" and trend == "BEARISH"):
                    confirmations.append("trend_aligned")
                    confirmation_scores["trend"] = 90.0
                elif trend == "NEUTRAL":
                    confirmation_scores["trend"] = 50.0
                else:
                    confirmation_scores["trend"] = 20.0
            
            # === 3. FILTRO DE MOMENTUM ===
            if filter_config.get("momentum_confirmation", True):
                try:
                    # RSI para momentum
                    rsi = ta.rsi(df['close'], length=14)
                    if rsi is not None and not rsi.empty:
                        current_rsi = rsi.iloc[-1]
                        prev_rsi = rsi.iloc[-2] if len(rsi) > 1 else current_rsi
                        
                        signal_type = signal_data.get("signal_type", "HOLD")
                        
                        if signal_type == "BUY" and current_rsi > prev_rsi and current_rsi < 70:
                            confirmations.append("momentum_bullish")
                            confirmation_scores["momentum"] = 80.0
                        elif signal_type == "SELL" and current_rsi < prev_rsi and current_rsi > 30:
                            confirmations.append("momentum_bearish")
                            confirmation_scores["momentum"] = 80.0
                        else:
                            confirmation_scores["momentum"] = 40.0
                    else:
                        confirmation_scores["momentum"] = 50.0
                except Exception:
                    confirmation_scores["momentum"] = 50.0
            
            # === 4. FILTRO DE VOLATILIDAD ===
            if filter_config.get("volatility_filter", True):
                market_regime = self.detect_market_regime(df)
                
                if market_regime in ["TRENDING", "NORMAL"]:
                    confirmations.append("volatility_favorable")
                    confirmation_scores["volatility"] = 75.0
                elif market_regime == "RANGING":
                    confirmation_scores["volatility"] = 60.0
                else:  # VOLATILE
                    confirmation_scores["volatility"] = 25.0
            
            # === 5. FILTRO DE SOPORTE/RESISTENCIA ===
            if filter_config.get("support_resistance_filter", True):
                try:
                    current_price = df['close'].iloc[-1]
                    
                    # Calcular niveles de soporte y resistencia simples
                    high_20 = df['high'].rolling(20).max().iloc[-1]
                    low_20 = df['low'].rolling(20).min().iloc[-1]
                    
                    # Distancia a niveles clave
                    resistance_distance = (high_20 - current_price) / current_price
                    support_distance = (current_price - low_20) / current_price
                    
                    signal_type = signal_data.get("signal_type", "HOLD")
                    
                    if signal_type == "BUY" and support_distance > 0.02:  # 2% sobre soporte
                        confirmations.append("above_support")
                        confirmation_scores["support_resistance"] = 70.0
                    elif signal_type == "SELL" and resistance_distance < 0.02:  # 2% bajo resistencia
                        confirmations.append("below_resistance")
                        confirmation_scores["support_resistance"] = 70.0
                    else:
                        confirmation_scores["support_resistance"] = 45.0
                        
                except Exception:
                    confirmation_scores["support_resistance"] = 50.0
            
            # === CÁLCULO DE PUNTUACIÓN FINAL ===
            total_confirmations = len(confirmations)
            min_confirmations = filter_config.get("min_confirmations", 3)
            
            # Puntuación promedio ponderada
            if confirmation_scores:
                weighted_score = sum(confirmation_scores.values()) / len(confirmation_scores)
            else:
                weighted_score = 50.0
            
            # Bonus por múltiples confirmaciones
            confirmation_bonus = min(total_confirmations * 5, 20)  # Máximo 20% bonus
            final_score = min(weighted_score + confirmation_bonus, 100.0)
            
            # Determinar si pasa los filtros
            passes_filters = (
                total_confirmations >= min_confirmations and
                final_score >= 60.0
            )
            
            # Clasificación de calidad
            if final_score >= 85:
                quality_grade = "A+"
            elif final_score >= 75:
                quality_grade = "A"
            elif final_score >= 65:
                quality_grade = "B+"
            elif final_score >= 55:
                quality_grade = "B"
            else:
                quality_grade = "C"
            
            return {
                "passes_filters": passes_filters,
                "confirmation_score": round(final_score, 2),
                "confirmations_count": total_confirmations,
                "min_confirmations_required": min_confirmations,
                "confirmations_list": confirmations,
                "individual_scores": confirmation_scores,
                "quality_grade": quality_grade,
                "filter_details": {
                    "volume_analysis": confirmation_scores.get("volume", 0),
                    "trend_alignment": confirmation_scores.get("trend", 0),
                    "momentum_strength": confirmation_scores.get("momentum", 0),
                    "volatility_regime": confirmation_scores.get("volatility", 0),
                    "support_resistance": confirmation_scores.get("support_resistance", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error applying multiple confirmation filters: {e}")
            return {
                "passes_filters": False,
                "confirmation_score": 0.0,
                "confirmations_count": 0,
                "min_confirmations_required": 3,
                "confirmations_list": [],
                "individual_scores": {},
                "quality_grade": "F",
                "filter_details": {}
            }

class ProfessionalRSIStrategy(EnhancedTradingStrategy):
    """🎯 Estrategia RSI Profesional con confirmaciones múltiples y nuevos indicadores"""
    
    def __init__(self):
        super().__init__("Professional_RSI_Enhanced")
        
        # 🎯 Configuración desde perfil activo centralizado
        from src.config.config_manager import ConfigManager
        
        # Obtener configuración del perfil activo
        strategies_config = ConfigManager.get_module_config('strategies')
        indicators_config = ConfigManager.get_module_config('indicators')
        trading_config = ConfigManager.get_module_config('trading_bot')
        
        # === PARÁMETROS RSI DESDE PERFIL ===
        self.rsi_oversold = strategies_config.get('rsi_oversold', 30)
        self.rsi_overbought = strategies_config.get('rsi_overbought', 70)
        self.rsi_period = indicators_config.get('rsi_period', 14)
        
        # === CONFIANZA MÍNIMA DESDE PERFIL ===
        self.min_confidence = trading_config.get('min_confidence', 70.0)  # Ya está en formato correcto
        
        # === PARÁMETROS DE CONFIRMACIÓN ===
        self.min_volume_ratio = 1.2  # Ratio mínimo de volumen vs promedio
        self.min_confluence = 2      # Mínimo de confirmaciones requeridas
        self.trend_strength_threshold = 0.6  # Umbral de fuerza de tendencia
        
        # === FILTROS DE CALIDAD ===
        self.min_atr_ratio = 0.8     # Ratio mínimo ATR para volatilidad
        self.max_spread_threshold = 0.003  # Máximo spread permitido
        
        # 📊 Log de configuración cargada
        logger.info(f"🎯 RSI Strategy configurada desde perfil {ConfigManager.get_active_profile()}:")
        logger.info(f"   • RSI: {self.rsi_oversold}/{self.rsi_overbought} (período: {self.rsi_period})")
        logger.info(f"   • Confianza mínima: {self.min_confidence*100:.1f}%")
        
    def analyze(self, symbol: str, timeframe: str = None) -> EnhancedSignal:
        """Análisis RSI profesional con confirmaciones avanzadas"""
        try:
            from src.config.config import DataLimitsConfig
            df = self.get_market_data(symbol, timeframe, limit=DataLimitsConfig.get_strategy_limit())
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data")
            
            # === INDICADORES PRINCIPALES ===
            # RSI Mejorado con análisis de divergencias
            enhanced_rsi = AdvancedIndicators.enhanced_rsi(df, symbol, timeframe)
            
            # Bollinger Bands para contexto de volatilidad
            bollinger = AdvancedIndicators.bollinger_bands(df, symbol, timeframe)
            
            # VWAP para análisis institucional
            vwap_analysis = AdvancedIndicators.vwap(df, symbol, timeframe)
            
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
            confidence = BASE_CONFIDENCE  # Usar constante centralizada
            notes = []
            
            # === ANÁLISIS RSI MEJORADO ===
            rsi_signal = enhanced_rsi["signal"]
            if rsi_signal in ["BUY", "STRONG_BUY"]:
                confluence_score += 2 if rsi_signal == "STRONG_BUY" else 1
                signal_type = "BUY"
                confidence += 15 if rsi_signal == "STRONG_BUY" else 8
                notes.append(f"Enhanced RSI: {enhanced_rsi['interpretation']}")
            elif rsi_signal in ["SELL", "STRONG_SELL"]:
                confluence_score += 2 if rsi_signal == "STRONG_SELL" else 1
                signal_type = "SELL"
                confidence += 15 if rsi_signal == "STRONG_SELL" else 8
                notes.append(f"Enhanced RSI: {enhanced_rsi['interpretation']}")
            
            # === CONFIRMACIÓN BOLLINGER BANDS ===
            if bollinger["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 6
                notes.append(f"Bollinger confirms: {bollinger['interpretation']}")
            
            # === CONFIRMACIÓN VWAP ===
            if vwap_analysis["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 5
                notes.append(f"VWAP confirms: {vwap_analysis['interpretation']}")
            
            # === ANÁLISIS DE VOLUMEN AVANZADO ===
            volume_signals = [obv_analysis["signal"], mfi_analysis["signal"], volume_profile["signal"]]
            volume_confirmations = sum(1 for vs in volume_signals if vs == signal_type and signal_type != "HOLD")
            
            if volume_confirmations >= 2:
                confluence_score += 2
                confidence += 10
                notes.append(f"Strong volume confirmation ({volume_confirmations}/3)")
            elif volume_confirmations == 1:
                confluence_score += 1
                confidence += 4
                notes.append("Volume confirmation")
            
            # === MOMENTUM Y VOLATILIDAD ===
            if roc_analysis["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 4
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
                confidence += 6
                notes.append(f"S/R level: {support_resistance['interpretation']}")
            
            # === LÍNEAS DE TENDENCIA ===
            if trend_lines["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 5
                notes.append(f"Trend line: {trend_lines['interpretation']}")
            
            # === PATRONES DE GRÁFICO ===
            if chart_patterns["signal"] == signal_type and signal_type != "HOLD":
                # Determinar fuerza del patrón basado en confianza
                pattern_strength = "STRONG" if any(p.get("confidence", 0) >= 75 for p in chart_patterns.get("patterns", [])) else "MODERATE"
                confluence_score += 2 if pattern_strength == "STRONG" else 1
                confidence += 8 if pattern_strength == "STRONG" else 5
                notes.append(f"Chart pattern: {chart_patterns['interpretation']}")
            
            # === CONFIRMACIONES TRADICIONALES ===
            # Confirmación con Stochastic
            if stoch["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 4
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
            
            # Calcular parámetros temporales basados en timeframe
            expected_duration, max_hold_time, time_based_exit_enabled = self.calculate_time_based_parameters(
                timeframe, signal_type
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
                timeframe=timeframe,
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
                confluence_score=int(confluence_score),
                # Parámetros temporales basados en timeframe
                expected_duration_hours=round(float(expected_duration), 2),
                max_hold_time_hours=round(float(max_hold_time), 2),
                time_based_exit_enabled=bool(time_based_exit_enabled)
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
        
        # 🎯 Configuración desde perfil activo centralizado
        from src.config.config_manager import ConfigManager
        
        # Obtener configuración del perfil activo
        profile_config = ConfigManager.get_consolidated_config()
        strategies_config = ConfigManager.get_module_config('strategies')
        indicators_config = ConfigManager.get_module_config('indicators')
        trading_config = ConfigManager.get_module_config('trading_bot')
        
        # === TIMEFRAMES DESDE PERFIL ===
        self.timeframes = profile_config.get('timeframes', ['15m', '30m', '1h'])
        
        # === CONFIANZA MÍNIMA DESDE PERFIL ===
        self.min_confidence = trading_config.get('min_confidence', 70.0)  # Ya está en formato correcto
        
        # === CONFIGURACIÓN RSI DINÁMICA DESDE PERFIL ===
        self.rsi_config = self._build_dynamic_rsi_config(strategies_config)
        self.timeframe_weights = self._build_dynamic_weights()
        
        # === PARÁMETROS DE CONSENSO ===
        self.min_timeframe_consensus = 2  # Mínimo de timeframes que deben coincidir
        self.trend_alignment_required = True  # Requiere alineación de tendencias
        
        # 📊 Log de configuración cargada
        logger.info(f"📊 MultiTimeframe Strategy configurada desde perfil {ConfigManager.get_active_profile()}:")
        logger.info(f"   • Timeframes: {', '.join(self.timeframes)}")
        logger.info(f"   • Confianza mínima: {self.min_confidence*100:.1f}%")
        logger.info(f"   • RSI base: {strategies_config.get('rsi_oversold', 30)}/{strategies_config.get('rsi_overbought', 70)}")
        
    def _build_dynamic_rsi_config(self, strategies_config: Dict[str, Any]) -> Dict[str, Dict[str, int]]:
        """Construir configuración RSI dinámica basada en timeframes del perfil"""
        # Obtener valores base del perfil
        base_oversold = strategies_config.get('rsi_oversold', 30)
        base_overbought = strategies_config.get('rsi_overbought', 70)
        
        rsi_config = {}
        for tf in self.timeframes:
            # Ajustar niveles RSI según el timeframe, basándose en los valores del perfil
            if 'm' in tf and int(tf.replace('m', '')) <= 5:  # Timeframes muy cortos
                # Más estricto para timeframes cortos
                rsi_config[tf] = {
                    "oversold": max(20, base_oversold - 5), 
                    "overbought": min(80, base_overbought + 5)
                }
            elif 'm' in tf and int(tf.replace('m', '')) <= 30:  # Timeframes medios
                # Usar valores del perfil
                rsi_config[tf] = {
                    "oversold": base_oversold, 
                    "overbought": base_overbought
                }
            else:  # Timeframes largos (1h+)
                # Más conservador para timeframes largos
                rsi_config[tf] = {
                    "oversold": max(15, base_oversold - 10), 
                    "overbought": min(85, base_overbought + 10)
                }
        return rsi_config
    
    def _build_dynamic_weights(self) -> Dict[str, float]:
        """Construir pesos dinámicos basados en timeframes del perfil"""
        weights = {}
        num_timeframes = len(self.timeframes)
        if num_timeframes == 0:
            return {}
        
        # Distribuir pesos: más peso a timeframes intermedios
        if num_timeframes == 1:
            weights[self.timeframes[0]] = 1.0
        elif num_timeframes == 2:
            weights[self.timeframes[0]] = 0.6  # Timeframe más corto
            weights[self.timeframes[1]] = 0.4  # Timeframe más largo
        else:
            # Para 3 o más timeframes
            weights[self.timeframes[0]] = 0.5   # Timeframe más corto
            weights[self.timeframes[-1]] = 0.2  # Timeframe más largo
            # Distribuir el resto entre timeframes intermedios
            remaining_weight = 0.3
            intermediate_count = num_timeframes - 2
            if intermediate_count > 0:
                weight_per_intermediate = remaining_weight / intermediate_count
                for i in range(1, num_timeframes - 1):
                    weights[self.timeframes[i]] = weight_per_intermediate
        
        return weights
    
    def analyze(self, symbol: str, timeframe: str = None) -> EnhancedSignal:
        """Análisis multi-timeframe"""
        try:
            signals = {}
            trends = {}
            
            # Analizar cada timeframe
            for tf in self.timeframes:
                try:
                    from src.config.config_manager import ConfigManager
                    config = ConfigManager().get_consolidated_config()
                    df = self.get_market_data(symbol, tf, limit=config.get("threshold", {}).get("trend_limit", 100))
                    if not df.empty:
                        trends[tf] = self.analyze_trend(df)
                        
                        # RSI para cada timeframe
                        # Convertir a float64 para evitar warnings de dtype
                        close_float = df['close'].astype('float64')
                        
                        with warnings.catch_warnings():
                            warnings.simplefilter('ignore', FutureWarning)
                            warnings.simplefilter('ignore', UserWarning)
                            from src.config.config_manager import ConfigManager
                            config = ConfigManager().get_consolidated_config()
                            rsi = ta.rsi(close_float, length=config.get("strategy", {}).get("professional_rsi", {}).get("rsi_period", 14))
                        if rsi is not None:
                            rsi_value = rsi.iloc[-1]
                            # Usar configuración por defecto si no existe para este timeframe
                            default_config = {"oversold": 30, "overbought": 70}
                            rsi_thresholds = self.rsi_config.get(tf, default_config)
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
            
            # Ponderar por timeframe usando pesos dinámicos del perfil
            weights = self.timeframe_weights
            weighted_buy = sum(weights.get(tf, 1) for tf, signal in signals.items() if signal == "BUY")
            weighted_sell = sum(weights.get(tf, 1) for tf, signal in signals.items() if signal == "SELL")
            
            current_price = self.get_current_price(symbol)
            df_main = self.get_market_data(symbol, timeframe)
            
            if weighted_buy > weighted_sell and buy_votes >= 2:
                signal_type = "BUY"
                # Usar la constante global definida en el módulo
                enhanced_confidence = globals().get('ENHANCED_CONFIDENCE', 60.0)
                confidence = enhanced_confidence + (weighted_buy * 5)
            elif weighted_sell > weighted_buy and sell_votes >= 2:
                signal_type = "SELL"
                # Usar la constante global definida en el módulo
                enhanced_confidence = globals().get('ENHANCED_CONFIDENCE', 60.0)
                confidence = enhanced_confidence + (weighted_sell * 5)
            else:
                signal_type = "HOLD"
                # Usar la constante global definida en el módulo
                hold_confidence = globals().get('HOLD_CONFIDENCE', 45.0)
                confidence = hold_confidence
            
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
                from src.config.config_manager import ConfigManager
                config = ConfigManager().get_consolidated_config()
                atr = ta.atr(high_float, low_float, close_float, length=config.get("strategy", {}).get("base", {}).get("default_atr_period", 14))
            current_atr = atr.iloc[-1] if atr is not None else current_price * config.get("threshold", {}).get("atr_fallback", 0.02)
            
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, signal_type, current_atr
            )
            
            # Usar el timeframe más largo disponible para confirmación de tendencia
            longest_tf = self.timeframes[-1] if self.timeframes else list(trends.keys())[-1] if trends else "1h"
            
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
                trend_confirmation=str(trends.get(longest_tf, "NEUTRAL")),
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
        
        # 🎯 Configuración desde perfil activo centralizado
        from src.config.config_manager import ConfigManager
        
        # Obtener configuración del perfil activo
        profile_config = ConfigManager.get_consolidated_config()
        strategies_config = ConfigManager.get_module_config('strategies')
        trading_config = ConfigManager.get_module_config('trading_bot')
        
        # Inicializar sub-estrategias
        self.rsi_strategy = ProfessionalRSIStrategy()
        self.mtf_strategy = MultiTimeframeStrategy()
        
        # === PESOS DE ESTRATEGIAS DESDE PERFIL ===
        # Usar pesos del perfil o valores por defecto
        default_weights = {"Professional_RSI": 0.4, "Multi_Timeframe": 0.6}
        self.strategy_weights = strategies_config.get('ensemble_weights', default_weights)
        
        # === CONFIGURACIÓN DE CONSENSO DESDE PERFIL ===
        # Corregir configuración problemática: usar valores específicos para ensemble
        ensemble_consensus = strategies_config.get('ensemble_min_consensus_threshold', 0.55)
        self.min_consensus_threshold = ensemble_consensus if ensemble_consensus <= 1.0 else ensemble_consensus / 100.0
        self.confidence_boost_factor = strategies_config.get('ensemble_confidence_boost_factor', 1.25)
        
        # 📊 Log de configuración cargada
        logger.info(f"🎯 Ensemble Strategy configurada desde perfil {ConfigManager.get_active_profile()}:")
        logger.info(f"   • Pesos: RSI={self.strategy_weights.get('Professional_RSI', 0.4)*100:.0f}%, MTF={self.strategy_weights.get('Multi_Timeframe', 0.6)*100:.0f}%")
        logger.info(f"   • Consenso mínimo: {self.min_consensus_threshold*100:.1f}%")
        logger.info(f"   • Factor boost: {self.confidence_boost_factor:.1f}x")
        
    def analyze(self, symbol: str, timeframe: str = None) -> EnhancedSignal:
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
            from src.config.config import DataLimitsConfig
            df = self.get_market_data(symbol, timeframe, limit=DataLimitsConfig.get_strategy_limit())
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
                from src.config.config_manager import ConfigManager
                config = ConfigManager().get_consolidated_config()
                atr = ta.atr(high_float, low_float, close_float, length=config.get("strategy", {}).get("base", {}).get("default_atr_period", 14))
            current_atr = atr.iloc[-1] if atr is not None else current_price * config.get("threshold", {}).get("atr_fallback", 0.02)
            
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
            
            # VALIDACIÓN CRÍTICA: Verificar si las estrategias principales dan señales activas
            main_strategies_active = 0
            for strategy_name, signal in strategy_signals.items():
                if signal and signal.signal_type != "HOLD":
                    main_strategies_active += 1
            
            # Si ninguna estrategia principal da señal activa, forzar HOLD
            if main_strategies_active == 0:
                return {
                    "signal_type": "HOLD",
                    "confidence": 45.0,
                    "consensus": 0.0,
                    "weighted_score": 0.0,
                    "buy_score": 0.0,
                    "sell_score": 0.0,
                    "confluence_score": 0,
                    "notes": ["All main strategies suggest HOLD - Ensemble forced HOLD"]
                }
            
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
                confidence = HOLD_CONFIDENCE
            else:
                consensus = max(buy_score, sell_score) / total_score
                
                if buy_score > sell_score and consensus >= self.min_consensus_threshold:
                    signal_type = "BUY"
                    confidence = min(95, BASE_CONFIDENCE + (buy_score * 40))
                elif sell_score > buy_score and consensus >= self.min_consensus_threshold:
                    signal_type = "SELL"
                    confidence = min(95, BASE_CONFIDENCE + (sell_score * 40))
                else:
                    signal_type = "HOLD"
                    from src.config.config_manager import ConfigManager
                    config = ConfigManager().get_consolidated_config()
                    confidence = config.get("strategy", {}).get("base", {}).get("hold_confidence", 50)
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