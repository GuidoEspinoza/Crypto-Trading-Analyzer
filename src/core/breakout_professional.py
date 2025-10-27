"""
💥 BREAKOUT PROFESSIONAL STRATEGY
Estrategia profesional de breakouts con análisis de patrones y volumen

COMPONENTES:
• Consolidación: Triángulos, Flags, Pennants
• Volumen: Expansión en breakout
• Momentum: ADX > 25
• Confirmación: Retest exitoso
• Target: Measured moves

FILTROS:
• Consolidación mínima 20 períodos
• Volumen breakout > 2x promedio
• No falsos breakouts recientes
• Tendencia de fondo favorable
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConsolidationPattern(Enum):
    TRIANGLE_ASCENDING = "TRIANGLE_ASCENDING"
    TRIANGLE_DESCENDING = "TRIANGLE_DESCENDING"
    TRIANGLE_SYMMETRICAL = "TRIANGLE_SYMMETRICAL"
    FLAG_BULLISH = "FLAG_BULLISH"
    FLAG_BEARISH = "FLAG_BEARISH"
    PENNANT = "PENNANT"
    RECTANGLE = "RECTANGLE"
    NONE = "NONE"


class BreakoutDirection(Enum):
    UPWARD = "UPWARD"
    DOWNWARD = "DOWNWARD"
    NONE = "NONE"


class TrendDirection(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"


@dataclass
class ConsolidationInfo:
    """Información sobre el patrón de consolidación"""

    pattern: ConsolidationPattern
    start_index: int
    end_index: int
    duration: int
    resistance_level: float
    support_level: float
    range_size: float
    volume_profile: str  # "DECREASING", "STABLE", "INCREASING"
    strength: float  # 0-100


@dataclass
class BreakoutInfo:
    """Información sobre el breakout"""

    direction: BreakoutDirection
    breakout_price: float
    breakout_volume: float
    volume_ratio: float  # vs promedio
    momentum_strength: float
    adx_value: float
    retest_confirmed: bool
    false_breakout_risk: float


@dataclass
class BreakoutSignal:
    """Señal de breakout profesional"""

    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    price: float
    confidence_score: float
    strength: str
    timestamp: datetime

    # Información del patrón
    consolidation: ConsolidationInfo
    breakout: BreakoutInfo

    # Análisis técnico
    adx_value: float
    volume_expansion: float
    trend_alignment: bool

    # Targets y riesgo
    measured_move_target: float
    stop_loss_price: float
    risk_reward_ratio: float

    # Filtros
    consolidation_duration_ok: bool
    volume_confirmation: bool
    no_recent_false_breakouts: bool
    trend_favorable: bool

    # Notas
    analysis_notes: str


class BreakoutProfessional:
    """
    💥 Estrategia profesional de breakouts

    Identifica patrones de consolidación y confirma breakouts
    con análisis de volumen y momentum
    """

    def __init__(self):
        self.name = "BreakoutProfessional"
        self.min_periods = 60  # Períodos mínimos para análisis
        self.min_consolidation_periods = 20
        self.max_consolidation_periods = 100

        # Parámetros ADX
        self.adx_period = 14
        self.min_adx_strength = 25

        # Parámetros de volumen
        self.min_volume_ratio = 2.0  # 2x el promedio
        self.volume_lookback = 20

        # Filtros de breakout
        self.min_range_size = 0.02  # 2% mínimo de rango
        self.max_false_breakout_lookback = 10
        self.retest_tolerance = 0.005  # 0.5% para retest

        # Umbrales de confianza
        self.min_confidence = 65

    def get_market_data(
        self, symbol: str, timeframe: str, periods: int = 100
    ) -> pd.DataFrame:
        """
        Obtener datos de mercado - será sobrescrito por el adaptador
        """
        logger.warning(f"⚠️ get_market_data no implementado para {symbol}")
        return pd.DataFrame()

    def calculate_adx(
        self, high: pd.Series, low: pd.Series, close: pd.Series
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calcular ADX, +DI, -DI"""
        adx = talib.ADX(
            high.values, low.values, close.values, timeperiod=self.adx_period
        )
        plus_di = talib.PLUS_DI(
            high.values, low.values, close.values, timeperiod=self.adx_period
        )
        minus_di = talib.MINUS_DI(
            high.values, low.values, close.values, timeperiod=self.adx_period
        )

        return pd.Series(adx), pd.Series(plus_di), pd.Series(minus_di)

    def find_swing_points(
        self, df: pd.DataFrame, window: int = 5
    ) -> Tuple[List[Tuple], List[Tuple]]:
        """Encontrar puntos de swing (máximos y mínimos locales)"""
        highs = []
        lows = []

        for i in range(window, len(df) - window):
            # Máximos locales
            if df["high"].iloc[i] == max(df["high"].iloc[i - window : i + window + 1]):
                highs.append((i, df["high"].iloc[i]))

            # Mínimos locales
            if df["low"].iloc[i] == min(df["low"].iloc[i - window : i + window + 1]):
                lows.append((i, df["low"].iloc[i]))

        return highs, lows

    def detect_consolidation_pattern(self, df: pd.DataFrame) -> ConsolidationInfo:
        """
        Detectar patrones de consolidación
        """
        try:
            if len(df) < self.min_consolidation_periods:
                return ConsolidationInfo(
                    ConsolidationPattern.NONE, 0, 0, 0, 0, 0, 0, "STABLE", 0
                )

            # Encontrar swing points
            highs, lows = self.find_swing_points(df)

            if len(highs) < 3 or len(lows) < 3:
                return ConsolidationInfo(
                    ConsolidationPattern.NONE, 0, 0, 0, 0, 0, 0, "STABLE", 0
                )

            # Analizar los últimos swing points para encontrar consolidación
            recent_highs = [
                h for h in highs if h[0] >= len(df) - 50
            ]  # Últimos 50 períodos
            recent_lows = [l for l in lows if l[0] >= len(df) - 50]

            if len(recent_highs) < 2 or len(recent_lows) < 2:
                return ConsolidationInfo(
                    ConsolidationPattern.NONE, 0, 0, 0, 0, 0, 0, "STABLE", 0
                )

            # Calcular niveles de soporte y resistencia
            resistance_level = max([h[1] for h in recent_highs])
            support_level = min([l[1] for l in recent_lows])
            range_size = (resistance_level - support_level) / support_level

            # Verificar duración mínima de consolidación
            start_index = min(
                [h[0] for h in recent_highs] + [l[0] for l in recent_lows]
            )
            end_index = len(df) - 1
            duration = end_index - start_index

            if duration < self.min_consolidation_periods:
                return ConsolidationInfo(
                    ConsolidationPattern.NONE, 0, 0, 0, 0, 0, 0, "STABLE", 0
                )

            # Verificar rango mínimo
            if range_size < self.min_range_size:
                return ConsolidationInfo(
                    ConsolidationPattern.NONE, 0, 0, 0, 0, 0, 0, "STABLE", 0
                )

            # Determinar tipo de patrón
            pattern = self._classify_pattern(recent_highs, recent_lows, df)

            # Analizar perfil de volumen durante consolidación
            volume_profile = self._analyze_volume_profile(df, start_index, end_index)

            # Calcular fuerza del patrón
            strength = self._calculate_pattern_strength(
                recent_highs, recent_lows, duration, range_size
            )

            return ConsolidationInfo(
                pattern=pattern,
                start_index=start_index,
                end_index=end_index,
                duration=duration,
                resistance_level=resistance_level,
                support_level=support_level,
                range_size=range_size,
                volume_profile=volume_profile,
                strength=strength,
            )

        except Exception as e:
            logger.error(f"Error detectando patrón de consolidación: {e}")
            return ConsolidationInfo(
                ConsolidationPattern.NONE, 0, 0, 0, 0, 0, 0, "STABLE", 0
            )

    def _classify_pattern(
        self, highs: List[Tuple], lows: List[Tuple], df: pd.DataFrame
    ) -> ConsolidationPattern:
        """Clasificar el tipo de patrón de consolidación"""
        try:
            if len(highs) < 2 or len(lows) < 2:
                return ConsolidationPattern.NONE

            # Analizar tendencia de máximos y mínimos
            high_trend = self._calculate_trend([h[1] for h in highs])
            low_trend = self._calculate_trend([l[1] for l in lows])

            # Triángulos
            if high_trend < -0.001 and low_trend > 0.001:
                return ConsolidationPattern.TRIANGLE_SYMMETRICAL
            elif high_trend < -0.001 and abs(low_trend) < 0.001:
                return ConsolidationPattern.TRIANGLE_DESCENDING
            elif abs(high_trend) < 0.001 and low_trend > 0.001:
                return ConsolidationPattern.TRIANGLE_ASCENDING

            # Flags y Pennants (requieren tendencia previa)
            prev_trend = self._get_previous_trend(df, highs[0][0])
            if abs(high_trend) < 0.001 and abs(low_trend) < 0.001:
                if prev_trend > 0.02:  # Tendencia alcista previa
                    return ConsolidationPattern.FLAG_BULLISH
                elif prev_trend < -0.02:  # Tendencia bajista previa
                    return ConsolidationPattern.FLAG_BEARISH
                else:
                    return ConsolidationPattern.RECTANGLE

            return ConsolidationPattern.RECTANGLE

        except Exception as e:
            logger.error(f"Error clasificando patrón: {e}")
            return ConsolidationPattern.NONE

    def _calculate_trend(self, values: List[float]) -> float:
        """Calcular la tendencia de una serie de valores"""
        if len(values) < 2:
            return 0

        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        return slope / values[0] if values[0] != 0 else 0

    def _get_previous_trend(self, df: pd.DataFrame, start_index: int) -> float:
        """Obtener la tendencia previa al patrón"""
        if start_index < 20:
            return 0

        prev_data = df["close"].iloc[start_index - 20 : start_index]
        if len(prev_data) < 2:
            return 0

        return (prev_data.iloc[-1] - prev_data.iloc[0]) / prev_data.iloc[0]

    def _analyze_volume_profile(
        self, df: pd.DataFrame, start_idx: int, end_idx: int
    ) -> str:
        """Analizar el perfil de volumen durante la consolidación"""
        try:
            if "volume" not in df.columns:
                return "STABLE"

            volume_data = df["volume"].iloc[start_idx : end_idx + 1]
            if len(volume_data) < 3:
                return "STABLE"

            # Dividir en tres partes y comparar
            third = len(volume_data) // 3
            early_vol = volume_data.iloc[:third].mean()
            mid_vol = volume_data.iloc[third : 2 * third].mean()
            late_vol = volume_data.iloc[2 * third :].mean()

            if late_vol > early_vol * 1.2:
                return "INCREASING"
            elif late_vol < early_vol * 0.8:
                return "DECREASING"
            else:
                return "STABLE"

        except Exception as e:
            logger.error(f"Error analizando volumen: {e}")
            return "STABLE"

    def _calculate_pattern_strength(
        self, highs: List[Tuple], lows: List[Tuple], duration: int, range_size: float
    ) -> float:
        """Calcular la fuerza del patrón"""
        try:
            strength = 50  # Base

            # Duración óptima (20-50 períodos)
            if 20 <= duration <= 50:
                strength += 20
            elif duration > 50:
                strength += 10

            # Rango adecuado (2-8%)
            if 0.02 <= range_size <= 0.08:
                strength += 20

            # Número de toques en soporte/resistencia
            touch_bonus = min(len(highs) + len(lows), 6) * 5
            strength += touch_bonus

            return min(strength, 100)

        except Exception as e:
            logger.error(f"Error calculando fuerza del patrón: {e}")
            return 50

    def detect_breakout(
        self, df: pd.DataFrame, consolidation: ConsolidationInfo
    ) -> BreakoutInfo:
        """
        Detectar si ha ocurrido un breakout
        """
        try:
            if consolidation.pattern == ConsolidationPattern.NONE:
                return BreakoutInfo(BreakoutDirection.NONE, 0, 0, 0, 0, 0, False, 100)

            current_price = df["close"].iloc[-1]
            current_volume = df["volume"].iloc[-1] if "volume" in df.columns else 1

            # Calcular volumen promedio
            avg_volume = (
                df["volume"].tail(self.volume_lookback).mean()
                if "volume" in df.columns
                else 1
            )
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            # Calcular ADX
            adx, plus_di, minus_di = self.calculate_adx(
                df["high"], df["low"], df["close"]
            )
            current_adx = adx.iloc[-1] if not pd.isna(adx.iloc[-1]) else 0

            # Detectar dirección del breakout
            direction = BreakoutDirection.NONE
            breakout_price = current_price

            # Breakout alcista
            if current_price > consolidation.resistance_level * 1.001:  # 0.1% buffer
                direction = BreakoutDirection.UPWARD
                breakout_price = consolidation.resistance_level

            # Breakout bajista
            elif current_price < consolidation.support_level * 0.999:  # 0.1% buffer
                direction = BreakoutDirection.DOWNWARD
                breakout_price = consolidation.support_level

            # Calcular momentum
            momentum_strength = self._calculate_momentum_strength(df, direction)

            # Verificar retest
            retest_confirmed = self._check_retest(df, consolidation, direction)

            # Calcular riesgo de falso breakout
            false_breakout_risk = self._calculate_false_breakout_risk(df, consolidation)

            return BreakoutInfo(
                direction=direction,
                breakout_price=breakout_price,
                breakout_volume=current_volume,
                volume_ratio=volume_ratio,
                momentum_strength=momentum_strength,
                adx_value=current_adx,
                retest_confirmed=retest_confirmed,
                false_breakout_risk=false_breakout_risk,
            )

        except Exception as e:
            logger.error(f"Error detectando breakout: {e}")
            return BreakoutInfo(BreakoutDirection.NONE, 0, 0, 0, 0, 0, False, 100)

    def _calculate_momentum_strength(
        self, df: pd.DataFrame, direction: BreakoutDirection
    ) -> float:
        """Calcular la fuerza del momentum"""
        try:
            if direction == BreakoutDirection.NONE:
                return 0

            # Usar ROC (Rate of Change) para momentum
            roc = talib.ROC(df["close"].values, timeperiod=5)
            current_roc = roc[-1] if not pd.isna(roc[-1]) else 0

            # Normalizar momentum (0-100)
            momentum = abs(current_roc) * 10
            return min(momentum, 100)

        except Exception as e:
            logger.error(f"Error calculando momentum: {e}")
            return 0

    def _check_retest(
        self,
        df: pd.DataFrame,
        consolidation: ConsolidationInfo,
        direction: BreakoutDirection,
    ) -> bool:
        """Verificar si ha habido un retest exitoso"""
        try:
            if direction == BreakoutDirection.NONE:
                return False

            # Buscar retest en los últimos 5-10 períodos
            recent_data = df.tail(10)

            if direction == BreakoutDirection.UPWARD:
                # Buscar si el precio volvió cerca de la resistencia sin romperla hacia abajo
                retest_level = consolidation.resistance_level
                tolerance = retest_level * self.retest_tolerance

                for _, row in recent_data.iterrows():
                    if (
                        abs(row["low"] - retest_level) <= tolerance
                        and row["close"] > retest_level
                    ):
                        return True

            elif direction == BreakoutDirection.DOWNWARD:
                # Buscar si el precio volvió cerca del soporte sin romperlo hacia arriba
                retest_level = consolidation.support_level
                tolerance = retest_level * self.retest_tolerance

                for _, row in recent_data.iterrows():
                    if (
                        abs(row["high"] - retest_level) <= tolerance
                        and row["close"] < retest_level
                    ):
                        return True

            return False

        except Exception as e:
            logger.error(f"Error verificando retest: {e}")
            return False

    def _calculate_false_breakout_risk(
        self, df: pd.DataFrame, consolidation: ConsolidationInfo
    ) -> float:
        """Calcular el riesgo de falso breakout"""
        try:
            # Buscar falsos breakouts recientes
            lookback_data = df.tail(
                self.max_false_breakout_lookback + consolidation.duration
            )
            false_breakouts = 0

            resistance = consolidation.resistance_level
            support = consolidation.support_level

            for i in range(len(lookback_data) - 1):
                current = lookback_data.iloc[i]
                next_candle = lookback_data.iloc[i + 1]

                # Falso breakout alcista
                if current["high"] > resistance and next_candle["close"] < resistance:
                    false_breakouts += 1

                # Falso breakout bajista
                if current["low"] < support and next_candle["close"] > support:
                    false_breakouts += 1

            # Convertir a porcentaje de riesgo
            risk = min(false_breakouts * 25, 100)  # Máximo 100%
            return risk

        except Exception as e:
            logger.error(f"Error calculando riesgo de falso breakout: {e}")
            return 50  # Riesgo medio por defecto

    def calculate_measured_move(
        self, consolidation: ConsolidationInfo, breakout: BreakoutInfo
    ) -> float:
        """Calcular el objetivo de measured move"""
        try:
            range_size = consolidation.resistance_level - consolidation.support_level

            if breakout.direction == BreakoutDirection.UPWARD:
                return consolidation.resistance_level + range_size
            elif breakout.direction == BreakoutDirection.DOWNWARD:
                return consolidation.support_level - range_size
            else:
                return breakout.breakout_price

        except Exception as e:
            logger.error(f"Error calculando measured move: {e}")
            return breakout.breakout_price

    def determine_trend_alignment(
        self, df: pd.DataFrame
    ) -> Tuple[bool, TrendDirection]:
        """Determinar si la tendencia de fondo es favorable"""
        try:
            # Usar EMAs para determinar tendencia de fondo
            ema_50 = talib.EMA(df["close"].values, timeperiod=50)
            ema_200 = talib.EMA(df["close"].values, timeperiod=200)

            if len(ema_50) < 2 or len(ema_200) < 2:
                return False, TrendDirection.NEUTRAL

            current_50 = ema_50[-1]
            current_200 = ema_200[-1]

            if current_50 > current_200 * 1.01:  # 1% buffer
                return True, TrendDirection.BULLISH
            elif current_50 < current_200 * 0.99:  # 1% buffer
                return True, TrendDirection.BEARISH
            else:
                return False, TrendDirection.NEUTRAL

        except Exception as e:
            logger.error(f"Error determinando alineación de tendencia: {e}")
            return False, TrendDirection.NEUTRAL

    def analyze(self, symbol: str, timeframe: str = "1h") -> Optional[BreakoutSignal]:
        """
        Análisis principal de breakout
        """
        try:
            # 1. Obtener datos
            df = self.get_market_data(symbol, timeframe, 150)
            if df.empty or len(df) < self.min_periods:
                logger.warning(f"Datos insuficientes para {symbol}")
                return None

            # 2. Detectar patrón de consolidación
            consolidation = self.detect_consolidation_pattern(df)

            # 3. Verificar filtros básicos
            if consolidation.pattern == ConsolidationPattern.NONE:
                logger.info(f"No se detectó patrón de consolidación para {symbol}")
                return None

            if consolidation.duration < self.min_consolidation_periods:
                logger.info(
                    f"Consolidación muy corta para {symbol}: {consolidation.duration} períodos"
                )
                return None

            # 4. Detectar breakout
            breakout = self.detect_breakout(df, consolidation)

            # 5. Determinar alineación de tendencia
            trend_favorable, trend_direction = self.determine_trend_alignment(df)

            # 6. Aplicar filtros
            consolidation_duration_ok = (
                consolidation.duration >= self.min_consolidation_periods
            )
            volume_confirmation = breakout.volume_ratio >= self.min_volume_ratio
            no_recent_false_breakouts = breakout.false_breakout_risk < 75
            adx_strong = breakout.adx_value >= self.min_adx_strength

            # 7. Generar señal
            signal_type = "HOLD"
            confidence = 50.0
            notes = []

            current_price = df["close"].iloc[-1]

            # Verificar breakout válido
            if breakout.direction != BreakoutDirection.NONE:

                # Breakout alcista
                if breakout.direction == BreakoutDirection.UPWARD:
                    signal_type = "BUY"
                    confidence = 60
                    notes.append(
                        f"Breakout alcista desde {consolidation.resistance_level:.2f}"
                    )

                    # Verificar alineación con tendencia alcista
                    if trend_direction == TrendDirection.BULLISH:
                        confidence += 15
                        notes.append("Alineado con tendencia alcista")

                # Breakout bajista
                elif breakout.direction == BreakoutDirection.DOWNWARD:
                    signal_type = "SELL"
                    confidence = 60
                    notes.append(
                        f"Breakout bajista desde {consolidation.support_level:.2f}"
                    )

                    # Verificar alineación con tendencia bajista
                    if trend_direction == TrendDirection.BEARISH:
                        confidence += 15
                        notes.append("Alineado con tendencia bajista")

                # Aplicar bonificaciones por filtros
                if volume_confirmation:
                    confidence += 10
                    notes.append(
                        f"Volumen confirmado: {breakout.volume_ratio:.1f}x promedio"
                    )

                if adx_strong:
                    confidence += 10
                    notes.append(f"ADX fuerte: {breakout.adx_value:.1f}")

                if breakout.retest_confirmed:
                    confidence += 15
                    notes.append("Retest exitoso confirmado")

                if no_recent_false_breakouts:
                    confidence += 5
                    notes.append("Sin falsos breakouts recientes")

                # Penalizaciones
                if not volume_confirmation:
                    confidence -= 20
                    notes.append(f"Volumen insuficiente: {breakout.volume_ratio:.1f}x")

                if not adx_strong:
                    confidence -= 15
                    notes.append(f"ADX débil: {breakout.adx_value:.1f}")

                if breakout.false_breakout_risk > 50:
                    confidence -= 10
                    notes.append(
                        f"Alto riesgo falso breakout: {breakout.false_breakout_risk:.1f}%"
                    )

            else:
                # No hay breakout, evaluar si estamos en consolidación
                notes.append(f"Consolidación detectada: {consolidation.pattern.value}")
                notes.append(
                    f"Rango: {consolidation.support_level:.2f} - {consolidation.resistance_level:.2f}"
                )
                notes.append(f"Duración: {consolidation.duration} períodos")

            # Filtro de confianza mínima
            if signal_type != "HOLD" and confidence < self.min_confidence:
                signal_type = "HOLD"
                notes.append(
                    f"Confianza insuficiente: {confidence:.1f}% < {self.min_confidence}%"
                )

            # 8. Calcular targets y stop loss
            measured_move_target = self.calculate_measured_move(consolidation, breakout)

            if signal_type == "BUY":
                stop_loss_price = consolidation.support_level
                take_profit_price = measured_move_target
            elif signal_type == "SELL":
                stop_loss_price = consolidation.resistance_level
                take_profit_price = measured_move_target
            else:
                stop_loss_price = current_price
                take_profit_price = current_price

            risk_reward_ratio = (
                (
                    abs(take_profit_price - current_price)
                    / abs(stop_loss_price - current_price)
                )
                if stop_loss_price != current_price
                else 0
            )

            # 9. Crear señal
            return BreakoutSignal(
                symbol=symbol,
                signal_type=signal_type,
                price=current_price,
                confidence_score=confidence,
                strength=(
                    "Strong"
                    if confidence > 80
                    else "Moderate" if confidence > 65 else "Weak"
                ),
                timestamp=datetime.now(),
                consolidation=consolidation,
                breakout=breakout,
                adx_value=breakout.adx_value,
                volume_expansion=breakout.volume_ratio,
                trend_alignment=trend_favorable,
                measured_move_target=measured_move_target,
                stop_loss_price=stop_loss_price,
                risk_reward_ratio=risk_reward_ratio,
                consolidation_duration_ok=consolidation_duration_ok,
                volume_confirmation=volume_confirmation,
                no_recent_false_breakouts=no_recent_false_breakouts,
                trend_favorable=trend_favorable,
                analysis_notes=" | ".join(notes),
            )

        except Exception as e:
            logger.error(f"Error en análisis de Breakout para {symbol}: {e}")
            return None


# Ejemplo de uso
if __name__ == "__main__":
    strategy = BreakoutProfessional()

    # Simular análisis (requiere integración con datos reales)
    signal = strategy.analyze("BTCUSD")

    if signal:
        print(f"💥 SEÑAL BREAKOUT GENERADA:")
        print(f"Símbolo: {signal.symbol}")
        print(f"Señal: {signal.signal_type}")
        print(f"Precio: ${signal.price:.2f}")
        print(f"Confianza: {signal.confidence_score:.1f}%")
        print(f"Patrón: {signal.consolidation.pattern.value}")
        print(f"Breakout: {signal.breakout.direction.value}")
        print(f"ADX: {signal.adx_value:.1f}")
        print(f"Volumen: {signal.volume_expansion:.1f}x")
        print(f"Target: ${signal.measured_move_target:.2f}")
        print(f"Notas: {signal.analysis_notes}")
    else:
        print("❌ No se generó señal o no pasó los filtros")
