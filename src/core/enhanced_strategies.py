"""🚀 Enhanced Trading Strategies - Versión Profesional
Estrategias de trading mejoradas con análisis multi-indicador,
confirmación de volumen y gestión avanzada de riesgo.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import ta
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

from src.config.main_config import (
    StrategyConfig,
    CacheConfig,
    TechnicalAnalysisConfig,
    ConfluenceConfig,
)


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
        self.min_confidence = (
            StrategyConfig.Base.DEFAULT_MIN_CONFIDENCE
        )  # Mínima confianza desde config
        self.advanced_indicators = AdvancedIndicators()
        # Referencia opcional al TradingBot para fuente centralizada de precios
        self.trading_bot = None

    def set_trading_bot(self, bot):
        """Asignar referencia al TradingBot para delegar operaciones comunes (precios, cache, etc.)"""
        self.trading_bot = bot

    @abstractmethod
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """Analizar símbolo y generar señal"""
        pass

    def get_market_data(
        self, symbol: str, timeframe: str = "1h", limit: int = 250
    ) -> pd.DataFrame:
        """Obtener datos de mercado usando Capital.com - EVITA LOOP INFINITO"""
        try:
            # Si hay TradingBot asignado y tiene capital_client, intentar obtener datos directamente
            if (
                hasattr(self, "trading_bot")
                and self.trading_bot
                and hasattr(self.trading_bot, "capital_client")
                and self.trading_bot.capital_client is not None
            ):

                try:
                    # Intentar obtener precio directamente de Capital.com sin usar get_current_price
                    # para evitar loop infinito
                    capital_symbol = symbol  # Asumir que ya está normalizado
                    market_data = self.trading_bot.capital_client.get_market_data(
                        [capital_symbol]
                    )

                    if market_data and capital_symbol in market_data:
                        price_data = market_data[capital_symbol]
                        current_price = None

                        # Intentar obtener precio válido
                        for price_key in ["bid", "offer", "mid"]:
                            if (
                                price_key in price_data
                                and price_data[price_key] is not None
                            ):
                                try:
                                    current_price = float(price_data[price_key])
                                    if current_price > 0:
                                        break
                                except (ValueError, TypeError):
                                    continue

                        if current_price and current_price > 0:
                            # Crear DataFrame básico con datos simulados para compatibilidad
                            import pandas as pd
                            from datetime import datetime, timedelta

                            timestamps = [
                                datetime.now() - timedelta(hours=i)
                                for i in range(limit, 0, -1)
                            ]
                            # Simular datos OHLCV básicos alrededor del precio actual
                            data = []
                            for ts in timestamps:
                                # Variación pequeña alrededor del precio actual
                                variation = 0.01 * (
                                    0.5 - abs(hash(str(ts)) % 100) / 100
                                )
                                price = current_price * (1 + variation)
                                data.append(
                                    {
                                        "timestamp": ts,
                                        "open": price,
                                        "high": price * 1.005,
                                        "low": price * 0.995,
                                        "close": price,
                                        "volume": 1000,
                                    }
                                )

                            df = pd.DataFrame(data)
                            df.set_index("timestamp", inplace=True)
                            df.sort_index(inplace=True)
                            return df

                except Exception as e:
                    logging.warning(
                        f"Error obteniendo datos de Capital.com para {symbol}: {e}"
                    )

            # Fallback: DataFrame vacío (NO intentar get_current_price para evitar loop)
            import pandas as pd

            logging.warning(
                f"No se pudieron obtener datos de mercado para {symbol} - retornando DataFrame vacío"
            )
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

        except Exception as e:
            logging.error(f"Error getting market data for {symbol}: {e}")
            import pandas as pd

            return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    def get_current_price(self, symbol: str) -> float:
        """Obtener precio actual del símbolo usando fuente centralizada si está disponible, con cache TTL"""
        import math

        def _validate_price(price: float) -> bool:
            """Validar que el precio sea válido y seguro para trading"""
            return (
                price is not None
                and not math.isnan(price)
                and not math.isinf(price)
                and price > 0
            )

        try:
            # Si hay TradingBot asignado, delegar para usar cache centralizado y normalización consistente
            if hasattr(self, "trading_bot") and self.trading_bot:
                try:
                    price = self.trading_bot._get_current_price(symbol)
                    if _validate_price(price):
                        return float(price)
                except ValueError as e:
                    # TradingBot ahora lanza ValueError cuando no puede obtener precio válido
                    logging.warning(
                        f"TradingBot no pudo obtener precio para {symbol}: {e}"
                    )
                except Exception as e:
                    logging.error(f"Error inesperado en TradingBot para {symbol}: {e}")

            # Fallback: usar datos históricos como último recurso
            try:
                df = self.get_market_data(symbol, "1m", limit=1)
                if not df.empty:
                    fallback_price = float(df["close"].iloc[-1])
                    if _validate_price(fallback_price):
                        cache_key = self._get_cache_key(
                            "strategy_current_price", symbol
                        )
                        self._store_in_cache(cache_key, fallback_price)
                        return fallback_price
                    else:
                        logging.warning(
                            f"Precio histórico inválido para {symbol}: {fallback_price}"
                        )
                else:
                    logging.warning(
                        f"No hay datos históricos disponibles para {symbol}"
                    )
            except Exception as e:
                logging.error(f"Error obteniendo datos históricos para {symbol}: {e}")

            # CRÍTICO: No retornar 0.0 - lanzar excepción para evitar trades peligrosos
            error_msg = f"🚨 CRÍTICO: No se pudo obtener precio válido para {symbol} desde estrategia"
            logging.error(error_msg)
            raise ValueError(error_msg)

        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            error_msg = f"🚨 CRÍTICO: Error inesperado obteniendo precio en estrategia para {symbol}: {e}"
            logging.error(error_msg)
            raise ValueError(error_msg)


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
    timeframe: str = "1h"  # Timeframe de la señal


class EnhancedTradingStrategy(TradingStrategy):
    """Clase base para estrategias mejoradas con optimizaciones de cache"""

    # Cache compartido entre instancias
    _cache = {}
    _cache_timestamps = {}
    _cache_ttl = CacheConfig.get_ttl_for_operation(
        "price_data"
    )  # TTL desde configuración centralizada

    def __init__(self, name: str, enable_filters: bool = True):
        super().__init__(name)
        # Usar configuración base disponible
        from src.config.main_config import TradingProfiles

        profile = TradingProfiles.get_current_profile()
        self.min_volume_ratio = profile.get(
            "min_volume_ratio", 1.5
        )  # Volumen según perfil activo
        self.min_confluence = profile.get(
            "min_confluence", 3
        )  # Confluencia según perfil activo
        # Signal filters deshabilitados (módulo eliminado)
        self.signal_filter = None

        # Configuración avanzada de confluencia desde configuración centralizada
        self.confluence_weights = ConfluenceConfig.COMPONENT_WEIGHTS.copy()
        # Usar valores por defecto para confluencia
        self.min_confluence_score = ConfluenceConfig.CONFLUENCE_THRESHOLDS["strong"]

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
        if (
            cache_key in cls._cache
            and cache_key in cls._cache_timestamps
            and current_time - cls._cache_timestamps[cache_key] < cls._cache_ttl
        ):
            return cls._cache[cache_key]
        return None

    @classmethod
    def _store_in_cache(cls, cache_key: str, value):
        """Almacenar valor en cache con timestamp"""
        cls._cache[cache_key] = value
        cls._cache_timestamps[cache_key] = time.time()

        # Limpiar cache viejo si es necesario
        if (
            len(cls._cache) > CacheConfig.MAX_CACHE_ENTRIES
        ):  # Límite desde configuración
            cls._cleanup_cache()

    @classmethod
    def _cleanup_cache(cls):
        """Limpiar entradas viejas del cache"""
        current_time = time.time()
        expired_keys = [
            key
            for key, timestamp in cls._cache_timestamps.items()
            if current_time - timestamp >= cls._cache_ttl
        ]
        for key in expired_keys:
            cls._cache.pop(key, None)
            cls._cache_timestamps.pop(key, None)

    def analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analizar volumen avanzado para confirmación de señales con cache"""
        try:
            if "volume" not in df.columns:
                return {
                    "volume_confirmation": False,
                    "volume_ratio": 0.0,
                    "volume_strength": "WEAK",
                }

            # Generar clave de cache basada en los últimos datos de volumen
            volume_data = df["volume"].tail(50).values
            cache_key = self._get_cache_key(
                "analyze_volume", str(volume_data.tobytes())
            )

            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Cálculos optimizados
            volume_series = df["volume"]
            current_volume = volume_series.iloc[-1]

            # Usar vectorización para mejor rendimiento
            rolling_20 = volume_series.rolling(
                TechnicalAnalysisConfig.VOLUME_PERIODS["medium"], min_periods=10
            )
            rolling_50 = volume_series.rolling(
                TechnicalAnalysisConfig.VOLUME_PERIODS["long"], min_periods=25
            )

            avg_volume_20 = rolling_20.mean().iloc[-1]
            avg_volume_50 = rolling_50.mean().iloc[-1]

            if pd.isna(avg_volume_20) or avg_volume_20 == 0:
                return {
                    "volume_confirmation": False,
                    "volume_ratio": 0.0,
                    "volume_strength": "WEAK",
                }

            # Ratios de volumen múltiples
            volume_ratio_20 = current_volume / avg_volume_20
            volume_ratio_50 = (
                current_volume / avg_volume_50
                if not pd.isna(avg_volume_50) and avg_volume_50 > 0
                else 0
            )

            # Análisis de tendencia de volumen
            volume_trend = df["volume"].rolling(10).mean().pct_change(5).iloc[-1]

            # Análisis de volumen por precio (VWAP deviation) - optimizado
            hlc3 = (df["high"] + df["low"] + df["close"]) / 3
            volume_price = (volume_series * hlc3).cumsum()
            volume_cumsum = volume_series.cumsum()
            vwap = volume_price / volume_cumsum
            vwap_deviation = abs(df["close"].iloc[-1] - vwap.iloc[-1]) / vwap.iloc[-1]

            # Clasificación de fuerza de volumen usando configuración centralizada
            volume_strength = TechnicalAnalysisConfig.get_volume_strength(
                volume_ratio_20
            )

            # Confirmación mejorada
            volume_confirmation = (
                volume_ratio_20 >= self.min_volume_ratio
                and volume_strength in ["STRONG", "VERY_STRONG"]
                and vwap_deviation
                < TechnicalAnalysisConfig.VWAP_DEVIATION_THRESHOLD  # Precio cerca del VWAP
            )

            result = {
                "volume_confirmation": bool(volume_confirmation),
                "volume_ratio": round(float(volume_ratio_20), 2),
                "volume_ratio_50": round(float(volume_ratio_50), 2),
                "volume_strength": volume_strength,
                "volume_trend": (
                    round(float(volume_trend), 4) if not pd.isna(volume_trend) else 0.0
                ),
                "vwap_deviation": round(float(vwap_deviation), 4),
                "current_volume": float(current_volume),
                "avg_volume_20": float(avg_volume_20),
                "avg_volume_50": (
                    float(avg_volume_50) if not pd.isna(avg_volume_50) else 0.0
                ),
            }

            # Almacenar en cache
            self._store_in_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return {
                "volume_confirmation": False,
                "volume_ratio": 0.0,
                "volume_strength": "WEAK",
            }

    def calculate_advanced_confluence(
        self, signal_data: Dict, signal_type: str
    ) -> Dict:
        """Calcular puntuación de confluencia avanzada con pesos específicos y cache"""
        try:
            # Generar clave de cache
            cache_key = self._get_cache_key(
                "calculate_confluence", str(signal_data), signal_type
            )

            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            confluence_score = 0.0
            confluence_details = {}

            # Mapas de valores precalculados para mejor rendimiento
            strength_map = {
                "VERY_STRONG": 1.0,
                "STRONG": 0.8,
                "MODERATE": 0.5,
                "WEAK": 0.2,
            }

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
            if (
                "bollinger_bands" in signal_data
                and signal_data["bollinger_bands"].get("signal") == signal_type
            ):
                bb_confidence = (
                    signal_data["bollinger_bands"].get("confidence", 50) / 100
                )
                technical_score += bb_confidence * 0.3
                technical_factors += 1
                confluence_details["bollinger_contribution"] = bb_confidence * 0.3

            # VWAP
            if (
                "vwap" in signal_data
                and signal_data["vwap"].get("signal") == signal_type
            ):
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
                vol_strength = strength_map.get(
                    vol_data.get("volume_strength", "WEAK"), 0.2
                )

                # Confirmación de volumen
                vol_confirmation = (
                    1.0 if vol_data.get("volume_confirmation", False) else 0.3
                )

                # Tendencia de volumen
                vol_trend = vol_data.get("volume_trend", 0)
                trend_bonus = (
                    0.2
                    if (
                        (signal_type == "BUY" and vol_trend > 0)
                        or (signal_type == "SELL" and vol_trend < 0)
                    )
                    else 0
                )

                volume_score = (
                    vol_strength * 0.5 + vol_confirmation * 0.3 + trend_bonus * 0.2
                )
                confluence_details["volume_contribution"] = volume_score

            # === ESTRUCTURA DE MERCADO (20%) ===
            structure_score = 0.0
            structure_factors = 0

            # Soporte y Resistencia
            if (
                "support_resistance" in signal_data
                and signal_data["support_resistance"].get("signal") == signal_type
            ):
                sr_confidence = (
                    signal_data["support_resistance"].get("confidence", 50) / 100
                )
                structure_score += sr_confidence * 0.6
                structure_factors += 1
                confluence_details["sr_contribution"] = sr_confidence * 0.6

            # Líneas de tendencia
            if (
                "trend_lines" in signal_data
                and signal_data["trend_lines"].get("signal") == signal_type
            ):
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
                technical_score * self.confluence_weights["technical"]
                + volume_score * self.confluence_weights["volume"]
                + structure_score * self.confluence_weights["structure"]
                + momentum_score * self.confluence_weights["momentum"]
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
                    "momentum": round(momentum_score, 3),
                },
                "confluence_details": confluence_details,
                "factors_count": {
                    "technical": technical_factors,
                    "structure": structure_factors,
                    "momentum": momentum_factors,
                },
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
                "component_scores": {
                    "technical": 0,
                    "volume": 0,
                    "structure": 0,
                    "momentum": 0,
                },
                "confluence_details": {},
                "factors_count": {"technical": 0, "structure": 0, "momentum": 0},
            }

    def analyze_trend(self, df: pd.DataFrame) -> str:
        """Analizar tendencia usando múltiples indicadores con cache"""
        try:
            # Generar clave de cache basada en los últimos precios
            price_data = df["close"].tail(50).values
            cache_key = self._get_cache_key("analyze_trend", str(price_data.tobytes()))

            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Cálculos optimizados de EMA
            close_series = df["close"]
            ema_20 = ta.ema(
                close_series, length=TechnicalAnalysisConfig.EMA_PERIODS["fast"]
            )
            ema_50 = ta.ema(
                close_series, length=TechnicalAnalysisConfig.EMA_PERIODS["slow"]
            )

            if ema_20 is None or ema_50 is None:
                return "NEUTRAL"

            current_ema_20 = ema_20.iloc[-1]
            current_ema_50 = ema_50.iloc[-1]

            # ADX para fuerza de tendencia
            # Convertir a float64 para evitar warnings de dtype
            high_float = df["high"].astype("float64")
            low_float = df["low"].astype("float64")
            close_float = df["close"].astype("float64")

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                warnings.simplefilter("ignore", UserWarning)
                adx_data = ta.adx(high_float, low_float, close_float, length=14)
            if adx_data is not None and not adx_data.empty:
                # Buscar la columna ADX dinámicamente
                adx_columns = [
                    col for col in adx_data.columns if col.startswith("ADX_")
                ]
                if adx_columns:
                    adx_value = adx_data[adx_columns[0]].iloc[-1]
                else:
                    adx_value = 25
            else:
                adx_value = 25

            # Determinar tendencia
            if (
                current_ema_20 > current_ema_50
                and adx_value > TechnicalAnalysisConfig.ADX_THRESHOLDS["strong_trend"]
            ):
                result = "BULLISH"
            elif (
                current_ema_20 < current_ema_50
                and adx_value > TechnicalAnalysisConfig.ADX_THRESHOLDS["strong_trend"]
            ):
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
            ohlc_data = df[["high", "low", "close"]].tail(50).values
            cache_key = self._get_cache_key(
                "detect_market_regime", str(ohlc_data.tobytes())
            )

            # Verificar cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Calcular volatilidad (ATR) optimizado
            # Convertir a float64 para evitar warnings de dtype
            high_float = df["high"].astype("float64")
            low_float = df["low"].astype("float64")
            close_float = df["close"].astype("float64")

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                warnings.simplefilter("ignore", UserWarning)
                atr = ta.atr(high_float, low_float, close_float, length=14)
            if atr is None or atr.empty:
                return "NORMAL"

            current_atr = atr.iloc[-1]
            avg_atr = atr.rolling(50).mean().iloc[-1]

            if pd.isna(current_atr) or pd.isna(avg_atr):
                return "NORMAL"

            volatility_ratio = current_atr / avg_atr

            # Detectar si está en tendencia o rango
            price_range = (
                df["high"].rolling(20).max().iloc[-1]
                - df["low"].rolling(20).min().iloc[-1]
            )
            current_price = df["close"].iloc[-1]

            if volatility_ratio > TechnicalAnalysisConfig.VOLATILITY_RATIO_THRESHOLD:
                result = "VOLATILE"
            elif (
                abs(
                    current_price
                    - (
                        df["high"]
                        .rolling(TechnicalAnalysisConfig.VOLUME_PERIODS["medium"])
                        .max()
                        .iloc[-1]
                        + df["low"]
                        .rolling(TechnicalAnalysisConfig.VOLUME_PERIODS["medium"])
                        .min()
                        .iloc[-1]
                    )
                    / 2
                )
                < price_range * TechnicalAnalysisConfig.PRICE_RANGE_TOLERANCE
            ):
                result = "RANGING"
            else:
                result = "TRENDING"

            # Almacenar en cache
            self._store_in_cache(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return "NORMAL"

    def calculate_roi_based_risk_reward(
        self, entry_price: float, signal_type: str, position_size: float, atr: float
    ) -> Tuple[float, float, float]:
        """Calcular stop loss, take profit basado en ROI del balance invertido (para scalping)

        Args:
            entry_price: Precio de entrada
            signal_type: "BUY" o "SELL"
            position_size: Tamaño de la posición en USD
            atr: Average True Range

        Returns:
            Tuple[stop_loss_price, take_profit_price, risk_reward_ratio]
        """
        try:
            # Importar configuración dinámica
            from src.config.main_config import RiskManagerConfig

            # Obtener rangos dinámicos desde config (ahora representan ROI del balance)
            sl_roi_min = (
                RiskManagerConfig.get_sl_min_percentage()
            )  # % de pérdida del balance
            sl_roi_max = (
                RiskManagerConfig.get_sl_max_percentage()
            )  # % de pérdida del balance
            tp_roi_min = (
                RiskManagerConfig.get_tp_min_percentage()
            )  # % de ganancia del balance
            tp_roi_max = (
                RiskManagerConfig.get_tp_max_percentage()
            )  # % de ganancia del balance

            # Calcular cantidad de activo que se puede comprar/vender
            quantity = position_size / entry_price

            # Determinar ROI objetivo basado en volatilidad (ATR)
            atr_ratio = atr / entry_price

            if signal_type == "BUY":
                # Para BUY: calcular precios basados en ROI del balance

                # Stop Loss ROI: entre sl_roi_min% y sl_roi_max% de pérdida del balance
                if atr_ratio <= sl_roi_min:
                    target_sl_roi = sl_roi_min
                elif atr_ratio >= sl_roi_max:
                    target_sl_roi = sl_roi_max
                else:
                    target_sl_roi = atr_ratio

                # Take Profit ROI: entre tp_roi_min% y tp_roi_max% de ganancia del balance
                atr_tp_factor = atr_ratio * 1.5  # Factor conservador para TP
                if atr_tp_factor <= tp_roi_min:
                    target_tp_roi = tp_roi_min
                elif atr_tp_factor >= tp_roi_max:
                    target_tp_roi = tp_roi_max
                else:
                    target_tp_roi = atr_tp_factor

                # Calcular precios que generen el ROI objetivo
                # Para BUY: pérdida_balance = (entry_price - stop_loss) * quantity
                # target_sl_roi = pérdida_balance / position_size
                # stop_loss = entry_price - (target_sl_roi * position_size / quantity)
                stop_loss = entry_price - (target_sl_roi * position_size / quantity)

                # Para BUY: ganancia_balance = (take_profit - entry_price) * quantity
                # target_tp_roi = ganancia_balance / position_size
                # take_profit = entry_price + (target_tp_roi * position_size / quantity)
                take_profit = entry_price + (target_tp_roi * position_size / quantity)

            elif signal_type == "SELL":
                # Para SELL: calcular precios basados en ROI del balance

                # Stop Loss ROI: entre sl_roi_min% y sl_roi_max% de pérdida del balance
                if atr_ratio <= sl_roi_min:
                    target_sl_roi = sl_roi_min
                elif atr_ratio >= sl_roi_max:
                    target_sl_roi = sl_roi_max
                else:
                    target_sl_roi = atr_ratio

                # Take Profit ROI: entre tp_roi_min% y tp_roi_max% de ganancia del balance
                atr_tp_factor = atr_ratio * 1.5
                if atr_tp_factor <= tp_roi_min:
                    target_tp_roi = tp_roi_min
                elif atr_tp_factor >= tp_roi_max:
                    target_tp_roi = tp_roi_max
                else:
                    target_tp_roi = atr_tp_factor

                # Calcular precios que generen el ROI objetivo
                # Para SELL: pérdida_balance = (stop_loss - entry_price) * quantity
                # stop_loss = entry_price + (target_sl_roi * position_size / quantity)
                stop_loss = entry_price + (target_sl_roi * position_size / quantity)

                # Para SELL: ganancia_balance = (entry_price - take_profit) * quantity
                # take_profit = entry_price - (target_tp_roi * position_size / quantity)
                take_profit = entry_price - (target_tp_roi * position_size / quantity)
            else:
                return 0.0, 0.0, 0.0

            # Importar configuración dinámica y balance manager
            from src.config.main_config import RiskManagerConfig, get_global_initial_balance
            from src.core.balance_manager import get_current_balance_sync

            # Obtener balance total actual
            try:
                balance_data = get_current_balance_sync()
                total_balance = balance_data.get("available", 0.0)
                if total_balance <= 0:
                    # Fallback al balance inicial si no se puede obtener el actual
                    total_balance = get_global_initial_balance()
            except:
                # Fallback al balance inicial en caso de error
                total_balance = get_global_initial_balance()

            # Obtener rangos dinámicos desde config (representan % del balance total)
            sl_roi_min = RiskManagerConfig.get_sl_min_percentage()  # % de pérdida del balance total
            sl_roi_max = RiskManagerConfig.get_sl_max_percentage()  # % de pérdida del balance total
            tp_roi_min = RiskManagerConfig.get_tp_min_percentage()  # % de ganancia del balance total
            tp_roi_max = RiskManagerConfig.get_tp_max_percentage()  # % de ganancia del balance total

            # Calcular cantidad de activo que se puede comprar/vender
            quantity = position_size / entry_price

            # Determinar ROI objetivo basado en volatilidad (ATR)
            atr_ratio = atr / entry_price

            if signal_type == "BUY":
                # Stop Loss ROI: entre sl_roi_min% y sl_roi_max% de pérdida del balance total
                if atr_ratio <= sl_roi_min:
                    target_sl_roi = sl_roi_min
                elif atr_ratio >= sl_roi_max:
                    target_sl_roi = sl_roi_max
                else:
                    target_sl_roi = atr_ratio

                # Take Profit ROI: entre tp_roi_min% y tp_roi_max% de ganancia del balance total
                atr_tp_factor = atr_ratio * 1.5  # Factor conservador para TP
                if atr_tp_factor <= tp_roi_min:
                    target_tp_roi = tp_roi_min
                elif atr_tp_factor >= tp_roi_max:
                    target_tp_roi = tp_roi_max
                else:
                    target_tp_roi = atr_tp_factor

                # Calcular pérdida máxima permitida en USD (% del balance total)
                max_loss_usd = total_balance * target_sl_roi
                
                # Calcular ganancia objetivo en USD (% del balance total)
                target_profit_usd = total_balance * target_tp_roi

                # Para BUY: pérdida = (entry_price - stop_loss) * quantity
                # max_loss_usd = (entry_price - stop_loss) * quantity
                # stop_loss = entry_price - (max_loss_usd / quantity)
                stop_loss = entry_price - (max_loss_usd / quantity)

                # Para BUY: ganancia = (take_profit - entry_price) * quantity
                # target_profit_usd = (take_profit - entry_price) * quantity
                # take_profit = entry_price + (target_profit_usd / quantity)
                take_profit = entry_price + (target_profit_usd / quantity)

            elif signal_type == "SELL":
                # Stop Loss ROI: entre sl_roi_min% y sl_roi_max% de pérdida del balance total
                if atr_ratio <= sl_roi_min:
                    target_sl_roi = sl_roi_min
                elif atr_ratio >= sl_roi_max:
                    target_sl_roi = sl_roi_max
                else:
                    target_sl_roi = atr_ratio

                # Take Profit ROI: entre tp_roi_min% y tp_roi_max% de ganancia del balance total
                atr_tp_factor = atr_ratio * 1.5
                if atr_tp_factor <= tp_roi_min:
                    target_tp_roi = tp_roi_min
                elif atr_tp_factor >= tp_roi_max:
                    target_tp_roi = tp_roi_max
                else:
                    target_tp_roi = atr_tp_factor

                # Calcular pérdida máxima permitida en USD (% del balance total)
                max_loss_usd = total_balance * target_sl_roi
                
                # Calcular ganancia objetivo en USD (% del balance total)
                target_profit_usd = total_balance * target_tp_roi

                # Para SELL: pérdida = (stop_loss - entry_price) * quantity
                # max_loss_usd = (stop_loss - entry_price) * quantity
                # stop_loss = entry_price + (max_loss_usd / quantity)
                stop_loss = entry_price + (max_loss_usd / quantity)

                # Para SELL: ganancia = (entry_price - take_profit) * quantity
                # target_profit_usd = (entry_price - take_profit) * quantity
                # take_profit = entry_price - (target_profit_usd / quantity)
                take_profit = entry_price - (target_profit_usd / quantity)
            else:
                return 0.0, 0.0, 0.0

            # Validaciones de seguridad para evitar stop loss inválidos
            if signal_type == "BUY":
                # Para BUY, el stop loss debe ser menor que el precio de entrada
                if stop_loss >= entry_price:
                    stop_loss = entry_price * 0.98  # 2% por debajo como fallback
                # El stop loss no puede ser negativo o muy bajo
                if stop_loss <= 0 or stop_loss < entry_price * 0.5:
                    stop_loss = entry_price * 0.95  # 5% por debajo como fallback
            else:  # SELL
                # Para SELL, el stop loss debe ser mayor que el precio de entrada
                if stop_loss <= entry_price:
                    stop_loss = entry_price * 1.02  # 2% por encima como fallback
                # El stop loss no puede ser excesivamente alto
                if stop_loss > entry_price * 2.0:
                    stop_loss = entry_price * 1.05  # 5% por encima como fallback

            # Calcular risk/reward ratio
            risk = abs(entry_price - stop_loss) * quantity
            reward = abs(take_profit - entry_price) * quantity

            if risk > 0:
                risk_reward_ratio = reward / risk
            else:
                risk_reward_ratio = 0.0

            return stop_loss, take_profit, risk_reward_ratio

        except Exception as e:
            logger.error(f"Error calculating ROI-based risk/reward: {str(e)}")
            # Fallback seguro basado en ATR
            if signal_type == "BUY":
                stop_loss = entry_price - (atr * 2)
                take_profit = entry_price + (atr * 3)
            else:
                stop_loss = entry_price + (atr * 2)
                take_profit = entry_price - (atr * 3)
            return stop_loss, take_profit, 1.5

    def calculate_risk_reward(
        self, entry_price: float, signal_type: str, atr: float
    ) -> Tuple[float, float, float]:
        """Calcular stop loss, take profit y ratio riesgo/beneficio

        Usa rangos dinámicos desde config.py:
        - Stop Loss: sl_min% - sl_max% del precio de entrada
        - Take Profit: tp_min% - tp_max% del precio de entrada
        """
        try:
            # Importar configuración dinámica
            from src.config.main_config import RiskManagerConfig

            # Obtener rangos dinámicos desde config
            sl_min = RiskManagerConfig.get_sl_min_percentage()
            sl_max = RiskManagerConfig.get_sl_max_percentage()
            tp_min = RiskManagerConfig.get_tp_min_percentage()
            tp_max = RiskManagerConfig.get_tp_max_percentage()

            # Calcular porcentaje ATR respecto al precio
            atr_ratio = atr / entry_price

            # Determinar SL y TP basado en rangos dinámicos
            if signal_type == "BUY":
                # Stop Loss: sl_min%-sl_max% por debajo del precio de entrada
                if atr_ratio <= sl_min:
                    sl_pct = sl_min  # Mínimo dinámico
                elif atr_ratio >= sl_max:
                    sl_pct = sl_max  # Máximo dinámico
                else:
                    sl_pct = atr_ratio  # Usar ATR si está en rango

                # Take Profit: tp_min%-tp_max% por encima del precio de entrada
                atr_tp = atr_ratio * 1.5
                if atr_tp <= tp_min:
                    tp_pct = tp_min  # Mínimo dinámico
                elif atr_tp >= tp_max:
                    tp_pct = tp_max  # Máximo dinámico
                else:
                    tp_pct = atr_tp  # 1.5x ATR si está en rango

                stop_loss = entry_price * (1 - sl_pct)
                take_profit = entry_price * (1 + tp_pct)

            elif signal_type == "SELL":
                # Stop Loss: sl_min%-sl_max% por encima del precio de entrada
                if atr_ratio <= sl_min:
                    sl_pct = sl_min  # Mínimo dinámico
                elif atr_ratio >= sl_max:
                    sl_pct = sl_max  # Máximo dinámico
                else:
                    sl_pct = atr_ratio  # Usar ATR si está en rango

                # Take Profit: tp_min%-tp_max% por debajo del precio de entrada
                if atr_ratio * 1.5 <= tp_min:
                    tp_pct = tp_min  # Mínimo dinámico
                elif atr_ratio * 1.5 >= tp_max:
                    tp_pct = tp_max  # Máximo dinámico
                else:
                    tp_pct = atr_ratio * 1.5  # 1.5x ATR si está en rango

                stop_loss = entry_price * (1 + sl_pct)
                take_profit = entry_price * (1 - tp_pct)
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
            df = self.get_market_data(symbol, timeframe, limit=250)
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
                quality_grade="B",
            )
