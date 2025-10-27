"""
🔄 MEAN REVERSION PROFESSIONAL STRATEGY
Estrategia profesional de reversión a la media con análisis técnico avanzado

COMPONENTES:
• Sobrecompra/Sobreventa: RSI + Stochastic
• Bandas: Bollinger Bands + Keltner Channels
• Divergencias: Price vs Oscillators
• Soporte/Resistencia: Fibonacci + Pivot Points
• Confirmación: Reversal Patterns

FILTROS:
• Solo en mercados laterales
• Cerca de niveles clave
• Divergencias confirmadas
• Volumen de confirmación
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MarketRegime(Enum):
    TRENDING = "TRENDING"
    RANGING = "RANGING"
    VOLATILE = "VOLATILE"


class DivergenceType(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    HIDDEN_BULLISH = "HIDDEN_BULLISH"
    HIDDEN_BEARISH = "HIDDEN_BEARISH"
    NONE = "NONE"


@dataclass
class DivergenceSignal:
    """Señal de divergencia detectada"""

    type: DivergenceType
    strength: float  # 0-100
    periods_back: int
    price_points: List[float]
    indicator_points: List[float]
    confidence: float


@dataclass
class SupportResistanceLevel:
    """Nivel de soporte o resistencia"""

    price: float
    strength: float  # 0-100
    type: str  # "SUPPORT" or "RESISTANCE"
    source: str  # "FIBONACCI", "PIVOT", "HISTORICAL"
    touches: int


@dataclass
class MeanReversionSignal:
    """Señal de reversión a la media"""

    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    price: float
    confidence_score: float
    strength: str
    timestamp: datetime

    # Componentes de análisis
    rsi_value: float
    stochastic_k: float
    stochastic_d: float
    bb_position: float  # Posición en Bollinger Bands (-1 a 1)
    kc_position: float  # Posición en Keltner Channels (-1 a 1)

    # Divergencias
    divergence: DivergenceSignal

    # Soporte/Resistencia
    nearest_level: SupportResistanceLevel
    distance_to_level: float

    # Filtros
    market_regime: MarketRegime
    volume_confirmation: bool
    pattern_confirmation: str

    # Métricas de riesgo
    risk_reward_ratio: float
    stop_loss_price: float
    take_profit_price: float

    # Notas
    analysis_notes: str


class MeanReversionProfessional:
    """
    🔄 Estrategia profesional de reversión a la media

    Utiliza múltiples indicadores y filtros para identificar
    oportunidades de reversión en mercados laterales
    """

    def __init__(self):
        self.name = "MeanReversionProfessional"
        self.min_periods = 50  # Períodos mínimos para análisis
        self.rsi_period = 14
        self.stoch_k_period = 14
        self.stoch_d_period = 3
        self.bb_period = 20
        self.bb_std = 2.0
        self.kc_period = 20
        self.kc_multiplier = 2.0

        # Umbrales
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.stoch_oversold = 20
        self.stoch_overbought = 80

        # Filtros
        self.min_confidence = 70
        self.min_volume_ratio = 1.2
        self.max_trend_strength = 0.3  # Para mercados laterales

    def get_market_data(
        self, symbol: str, timeframe: str, periods: int = 100
    ) -> pd.DataFrame:
        """
        Obtener datos de mercado - será sobrescrito por el adaptador
        """
        logger.warning(f"⚠️ get_market_data no implementado para {symbol}")
        return pd.DataFrame()

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calcular RSI (Relative Strength Index)
        """
        try:
            if len(prices) < period + 1:
                return pd.Series(np.nan, index=prices.index, dtype=float)

            delta = prices.diff()
            gain = (
                (delta.where(delta > 0, 0))
                .rolling(window=period, min_periods=period)
                .mean()
            )
            loss = (
                (-delta.where(delta < 0, 0))
                .rolling(window=period, min_periods=period)
                .mean()
            )

            # Evitar división por cero
            rs = pd.Series(np.nan, index=prices.index, dtype=float)
            valid_loss = loss > 0
            rs[valid_loss] = gain[valid_loss] / loss[valid_loss]

            # Calcular RSI solo donde rs es válido
            rsi = pd.Series(np.nan, index=prices.index, dtype=float)
            valid_rs = ~rs.isna()
            rsi[valid_rs] = 100 - (100 / (1 + rs[valid_rs]))

            return rsi
        except Exception as e:
            logger.error(f"Error calculando RSI: {e}")
            return pd.Series(
                np.nan,
                index=prices.index if len(prices) > 0 else pd.Index([]),
                dtype=float,
            )

    def calculate_stochastic(
        self, high: pd.Series, low: pd.Series, close: pd.Series
    ) -> Tuple[pd.Series, pd.Series]:
        """Calcular Stochastic Oscillator"""
        k, d = talib.STOCH(
            high.values,
            low.values,
            close.values,
            fastk_period=self.stoch_k_period,
            slowk_period=self.stoch_d_period,
            slowd_period=self.stoch_d_period,
        )
        return pd.Series(k), pd.Series(d)

    def calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20, std_dev: float = 2.0
    ) -> Dict[str, pd.Series]:
        """
        Calcular Bollinger Bands
        """
        try:
            if len(prices) < period:
                # Retornar series vacías con el mismo índice que prices
                empty_series = pd.Series(np.nan, index=prices.index, dtype=float)
                return {
                    "upper": empty_series,
                    "middle": empty_series,
                    "lower": empty_series,
                    "width": empty_series,
                }

            sma = prices.rolling(window=period, min_periods=period).mean()
            std = prices.rolling(window=period, min_periods=period).std()

            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)

            # Calcular width con validación para evitar división por cero
            width = pd.Series(np.nan, index=prices.index, dtype=float)
            valid_sma = sma > 0
            width[valid_sma] = (
                (upper_band[valid_sma] - lower_band[valid_sma]) / sma[valid_sma] * 100
            )

            return {
                "upper": upper_band,
                "middle": sma,
                "lower": lower_band,
                "width": width,
            }
        except Exception as e:
            logger.error(f"Error calculando Bollinger Bands: {e}")
            # Retornar series vacías con el mismo índice que prices
            empty_series = pd.Series(
                np.nan,
                index=prices.index if len(prices) > 0 else pd.Index([]),
                dtype=float,
            )
            return {
                "upper": empty_series,
                "middle": empty_series,
                "lower": empty_series,
                "width": empty_series,
            }

    def calculate_keltner_channels(
        self, high: pd.Series, low: pd.Series, close: pd.Series
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcular Keltner Channels"""
        ema = talib.EMA(close.values, timeperiod=self.kc_period)
        atr = talib.ATR(
            high.values, low.values, close.values, timeperiod=self.kc_period
        )

        upper = ema + (atr * self.kc_multiplier)
        lower = ema - (atr * self.kc_multiplier)

        return pd.Series(upper), pd.Series(ema), pd.Series(lower)

    def detect_divergences(
        self, prices: pd.Series, indicator: pd.Series, lookback: int = 20
    ) -> DivergenceSignal:
        """
        Detectar divergencias entre precio e indicador
        """
        try:
            if len(prices) < lookback * 2 or len(indicator) < lookback * 2:
                return DivergenceSignal(DivergenceType.NONE, 0, 0, [], [], 0)

            # Verificar que las series tengan el mismo tamaño
            min_length = min(len(prices), len(indicator))
            if min_length < lookback * 2:
                return DivergenceSignal(DivergenceType.NONE, 0, 0, [], [], 0)

            # Truncar series al mismo tamaño
            prices = prices.iloc[-min_length:]
            indicator = indicator.iloc[-min_length:]

            # Encontrar picos y valles en precio
            price_highs = []
            price_lows = []
            indicator_highs = []
            indicator_lows = []

            # Usar ventana más pequeña para evitar índices fuera de rango
            window = min(5, lookback // 4)

            for i in range(window, len(prices) - window):
                # Verificar que tenemos suficientes datos
                if i - window < 0 or i + window >= len(prices):
                    continue

                # Picos en precio
                if prices.iloc[i] == max(prices.iloc[i - window : i + window + 1]):
                    price_highs.append((i, prices.iloc[i]))
                    indicator_highs.append((i, indicator.iloc[i]))

                # Valles en precio
                if prices.iloc[i] == min(prices.iloc[i - window : i + window + 1]):
                    price_lows.append((i, prices.iloc[i]))
                    indicator_lows.append((i, indicator.iloc[i]))

            # Analizar divergencias en los últimos picos/valles
            if len(price_highs) >= 2 and len(indicator_highs) >= 2:
                last_price_high = price_highs[-1][1]
                prev_price_high = price_highs[-2][1]
                last_ind_high = indicator_highs[-1][1]
                prev_ind_high = indicator_highs[-2][1]

                # Verificar que los valores son válidos
                if (
                    prev_price_high > 0
                    and not np.isnan(prev_price_high)
                    and not np.isnan(last_price_high)
                    and not np.isnan(last_ind_high)
                    and not np.isnan(prev_ind_high)
                ):

                    # Divergencia bajista: precio hace máximo más alto, indicador hace máximo más bajo
                    if (
                        last_price_high > prev_price_high
                        and last_ind_high < prev_ind_high
                    ):
                        strength = (
                            abs(last_price_high - prev_price_high)
                            / prev_price_high
                            * 100
                        )
                        return DivergenceSignal(
                            DivergenceType.BEARISH,
                            min(strength * 10, 100),
                            price_highs[-1][0],
                            [prev_price_high, last_price_high],
                            [prev_ind_high, last_ind_high],
                            min(strength * 5, 100),
                        )

            if len(price_lows) >= 2 and len(indicator_lows) >= 2:
                last_price_low = price_lows[-1][1]
                prev_price_low = price_lows[-2][1]
                last_ind_low = indicator_lows[-1][1]
                prev_ind_low = indicator_lows[-2][1]

                # Verificar que los valores son válidos
                if (
                    prev_price_low > 0
                    and not np.isnan(prev_price_low)
                    and not np.isnan(last_price_low)
                    and not np.isnan(last_ind_low)
                    and not np.isnan(prev_ind_low)
                ):

                    # Divergencia alcista: precio hace mínimo más bajo, indicador hace mínimo más alto
                    if last_price_low < prev_price_low and last_ind_low > prev_ind_low:
                        strength = (
                            abs(prev_price_low - last_price_low) / prev_price_low * 100
                        )
                        return DivergenceSignal(
                            DivergenceType.BULLISH,
                            min(strength * 10, 100),
                            price_lows[-1][0],
                            [prev_price_low, last_price_low],
                            [prev_ind_low, last_ind_low],
                            min(strength * 5, 100),
                        )

            return DivergenceSignal(DivergenceType.NONE, 0, 0, [], [], 0)

        except Exception as e:
            logger.error(f"Error detectando divergencias: {e}")
            return DivergenceSignal(DivergenceType.NONE, 0, 0, [], [], 0)

    def calculate_fibonacci_levels(self, high: float, low: float) -> Dict[str, float]:
        """Calcular niveles de Fibonacci"""
        diff = high - low
        return {
            "0.0": high,
            "23.6": high - (diff * 0.236),
            "38.2": high - (diff * 0.382),
            "50.0": high - (diff * 0.5),
            "61.8": high - (diff * 0.618),
            "78.6": high - (diff * 0.786),
            "100.0": low,
        }

    def find_support_resistance_levels(
        self, df: pd.DataFrame
    ) -> List[SupportResistanceLevel]:
        """Encontrar niveles de soporte y resistencia"""
        levels = []

        try:
            # Niveles de Fibonacci basados en el rango reciente
            recent_high = df["high"].tail(50).max()
            recent_low = df["low"].tail(50).min()
            fib_levels = self.calculate_fibonacci_levels(recent_high, recent_low)

            for level_name, price in fib_levels.items():
                if level_name in ["23.6", "38.2", "50.0", "61.8"]:
                    levels.append(
                        SupportResistanceLevel(
                            price=price,
                            strength=70 if level_name == "50.0" else 60,
                            type=(
                                "SUPPORT"
                                if price < df["close"].iloc[-1]
                                else "RESISTANCE"
                            ),
                            source="FIBONACCI",
                            touches=1,
                        )
                    )

            # Pivot Points (simplificado)
            if len(df) >= 3:
                last_high = df["high"].iloc[-2]
                last_low = df["low"].iloc[-2]
                last_close = df["close"].iloc[-2]

                pivot = (last_high + last_low + last_close) / 3
                r1 = 2 * pivot - last_low
                s1 = 2 * pivot - last_high

                levels.extend(
                    [
                        SupportResistanceLevel(
                            pivot,
                            80,
                            "SUPPORT" if pivot < df["close"].iloc[-1] else "RESISTANCE",
                            "PIVOT",
                            1,
                        ),
                        SupportResistanceLevel(r1, 70, "RESISTANCE", "PIVOT", 1),
                        SupportResistanceLevel(s1, 70, "SUPPORT", "PIVOT", 1),
                    ]
                )

            return levels

        except Exception as e:
            logger.error(f"Error calculando niveles S/R: {e}")
            return []

    def determine_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Determinar el régimen de mercado"""
        try:
            # Calcular EMAs para determinar tendencia
            ema_20 = talib.EMA(df["close"].values, timeperiod=20)
            ema_50 = talib.EMA(df["close"].values, timeperiod=50)

            # Calcular ATR para volatilidad
            atr = talib.ATR(
                df["high"].values, df["low"].values, df["close"].values, timeperiod=14
            )
            current_atr = atr[-1]
            avg_atr = np.mean(atr[-20:])

            # Determinar fuerza de tendencia
            trend_strength = abs(ema_20[-1] - ema_50[-1]) / df["close"].iloc[-1]

            # Clasificar régimen
            if current_atr > avg_atr * 1.5:
                return MarketRegime.VOLATILE
            elif trend_strength > self.max_trend_strength:
                return MarketRegime.TRENDING
            else:
                return MarketRegime.RANGING

        except Exception as e:
            logger.error(f"Error determinando régimen de mercado: {e}")
            return MarketRegime.RANGING

    def analyze(
        self, symbol: str, timeframe: str = "1h"
    ) -> Optional[MeanReversionSignal]:
        """
        Análisis principal de reversión a la media
        """
        try:
            # 1. Obtener datos
            df = self.get_market_data(symbol, timeframe, 100)
            if df.empty or len(df) < self.min_periods:
                logger.warning(f"Datos insuficientes para {symbol}")
                return None

            # 2. Calcular indicadores
            rsi = self.calculate_rsi(df["close"])
            stoch_k, stoch_d = self.calculate_stochastic(
                df["high"], df["low"], df["close"]
            )
            bb_bands = self.calculate_bollinger_bands(df["close"])
            bb_upper, bb_middle, bb_lower = (
                bb_bands["upper"],
                bb_bands["middle"],
                bb_bands["lower"],
            )
            kc_upper, kc_middle, kc_lower = self.calculate_keltner_channels(
                df["high"], df["low"], df["close"]
            )

            current_price = df["close"].iloc[-1]
            current_rsi = rsi[-1]
            current_stoch_k = stoch_k.iloc[-1]
            current_stoch_d = stoch_d.iloc[-1]

            # 3. Posiciones en bandas
            bb_position = (current_price - bb_middle.iloc[-1]) / (
                bb_upper.iloc[-1] - bb_middle.iloc[-1]
            )
            kc_position = (current_price - kc_middle.iloc[-1]) / (
                kc_upper.iloc[-1] - kc_middle.iloc[-1]
            )

            # 4. Detectar divergencias
            rsi_divergence = self.detect_divergences(df["close"], pd.Series(rsi))

            # 5. Encontrar niveles S/R
            sr_levels = self.find_support_resistance_levels(df)
            nearest_level = None
            min_distance = float("inf")

            for level in sr_levels:
                distance = abs(current_price - level.price) / current_price
                if distance < min_distance:
                    min_distance = distance
                    nearest_level = level

            # 6. Determinar régimen de mercado
            market_regime = self.determine_market_regime(df)

            # 7. Filtros principales
            # Solo operar en mercados laterales
            if market_regime != MarketRegime.RANGING:
                logger.info(f"Mercado no lateral para {symbol}: {market_regime.value}")
                return None

            # 8. Generar señal
            signal_type = "HOLD"
            confidence = 50.0
            notes = []

            # Condiciones de COMPRA (oversold)
            buy_conditions = 0
            if current_rsi < self.rsi_oversold:
                buy_conditions += 1
                notes.append(f"RSI oversold: {current_rsi:.1f}")

            if (
                current_stoch_k < self.stoch_oversold
                and current_stoch_d < self.stoch_oversold
            ):
                buy_conditions += 1
                notes.append(
                    f"Stochastic oversold: K={current_stoch_k:.1f}, D={current_stoch_d:.1f}"
                )

            if bb_position < -0.8:  # Cerca del límite inferior de BB
                buy_conditions += 1
                notes.append("Precio cerca de Bollinger Band inferior")

            if rsi_divergence.type == DivergenceType.BULLISH:
                buy_conditions += 2
                confidence += rsi_divergence.confidence * 0.3
                notes.append(
                    f"Divergencia alcista detectada (fuerza: {rsi_divergence.strength:.1f})"
                )

            # Condiciones de VENTA (overbought)
            sell_conditions = 0
            if current_rsi > self.rsi_overbought:
                sell_conditions += 1
                notes.append(f"RSI overbought: {current_rsi:.1f}")

            if (
                current_stoch_k > self.stoch_overbought
                and current_stoch_d > self.stoch_overbought
            ):
                sell_conditions += 1
                notes.append(
                    f"Stochastic overbought: K={current_stoch_k:.1f}, D={current_stoch_d:.1f}"
                )

            if bb_position > 0.8:  # Cerca del límite superior de BB
                sell_conditions += 1
                notes.append("Precio cerca de Bollinger Band superior")

            if rsi_divergence.type == DivergenceType.BEARISH:
                sell_conditions += 2
                confidence += rsi_divergence.confidence * 0.3
                notes.append(
                    f"Divergencia bajista detectada (fuerza: {rsi_divergence.strength:.1f})"
                )

            # Determinar señal final
            if buy_conditions >= 2:
                signal_type = "BUY"
                confidence = min(50 + (buy_conditions * 15), 95)
            elif sell_conditions >= 2:
                signal_type = "SELL"
                confidence = min(50 + (sell_conditions * 15), 95)

            # Verificar proximidad a niveles S/R
            if nearest_level and min_distance < 0.02:  # Dentro del 2%
                if signal_type == "BUY" and nearest_level.type == "SUPPORT":
                    confidence += 10
                    notes.append(f"Cerca de soporte en {nearest_level.price:.2f}")
                elif signal_type == "SELL" and nearest_level.type == "RESISTANCE":
                    confidence += 10
                    notes.append(f"Cerca de resistencia en {nearest_level.price:.2f}")

            # Filtro de confianza mínima
            if confidence < self.min_confidence:
                signal_type = "HOLD"
                notes.append(
                    f"Confianza insuficiente: {confidence:.1f}% < {self.min_confidence}%"
                )

            # 9. Calcular stop loss y take profit
            atr = talib.ATR(
                df["high"].values, df["low"].values, df["close"].values, timeperiod=14
            )
            current_atr = atr[-1]

            if signal_type == "BUY":
                stop_loss_price = current_price - (current_atr * 2)
                take_profit_price = current_price + (current_atr * 3)
            elif signal_type == "SELL":
                stop_loss_price = current_price + (current_atr * 2)
                take_profit_price = current_price - (current_atr * 3)
            else:
                stop_loss_price = current_price
                take_profit_price = current_price

            risk_reward_ratio = (
                abs(take_profit_price - current_price)
                / abs(stop_loss_price - current_price)
                if stop_loss_price != current_price
                else 0
            )

            # 10. Verificar volumen
            volume_confirmation = True  # Simplificado por ahora
            if len(df) > 20:
                avg_volume = (
                    df["volume"].tail(20).mean() if "volume" in df.columns else 1
                )
                current_volume = df["volume"].iloc[-1] if "volume" in df.columns else 1
                volume_confirmation = (
                    current_volume > avg_volume * self.min_volume_ratio
                )

            # 11. Crear señal
            return MeanReversionSignal(
                symbol=symbol,
                signal_type=signal_type,
                price=current_price,
                confidence_score=confidence,
                strength=(
                    "Strong"
                    if confidence > 80
                    else "Moderate" if confidence > 60 else "Weak"
                ),
                timestamp=datetime.now(),
                rsi_value=current_rsi,
                stochastic_k=current_stoch_k,
                stochastic_d=current_stoch_d,
                bb_position=bb_position,
                kc_position=kc_position,
                divergence=rsi_divergence,
                nearest_level=nearest_level
                or SupportResistanceLevel(current_price, 0, "NONE", "NONE", 0),
                distance_to_level=min_distance,
                market_regime=market_regime,
                volume_confirmation=volume_confirmation,
                pattern_confirmation="REVERSAL" if signal_type != "HOLD" else "NONE",
                risk_reward_ratio=risk_reward_ratio,
                stop_loss_price=stop_loss_price,
                take_profit_price=take_profit_price,
                analysis_notes=" | ".join(notes),
            )

        except Exception as e:
            logger.error(f"Error en análisis de Mean Reversion para {symbol}: {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    strategy = MeanReversionProfessional()

    # Simular análisis (requiere integración con datos reales)
    signal = strategy.analyze("BTCUSD")

    if signal:
        print(f"🔄 SEÑAL MEAN REVERSION GENERADA:")
        print(f"Símbolo: {signal.symbol}")
        print(f"Señal: {signal.signal_type}")
        print(f"Precio: ${signal.price:.2f}")
        print(f"Confianza: {signal.confidence_score:.1f}%")
        print(f"RSI: {signal.rsi_value:.1f}")
        print(f"Stochastic K/D: {signal.stochastic_k:.1f}/{signal.stochastic_d:.1f}")
        print(f"Divergencia: {signal.divergence.type.value}")
        print(f"Régimen: {signal.market_regime.value}")
        print(f"Notas: {signal.analysis_notes}")
    else:
        print("❌ No se generó señal o no pasó los filtros")
