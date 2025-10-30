"""📈 TREND FOLLOWING PROFESSIONAL STRATEGY
Estrategia de seguimiento de tendencia de nivel institucional con filtros avanzados,
análisis de estructura de mercado y sistema de scoring profesional.

Esta estrategia implementa:
- Análisis de estructura de mercado (HH/HL, LH/LL)
- Alineación de tendencia multi-timeframe
- Filtros de confluencia avanzados
- Sistema de scoring institucional
- Gestión de riesgo profesional
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass
import pytz

from .enhanced_strategies import TradingSignal, EnhancedSignal
from .mean_reversion_professional import MarketRegime

logger = logging.getLogger(__name__)


class TrendFollowingProfessional:
    """📈 Estrategia de seguimiento de tendencia profesional"""

    def __init__(self):
        self.name = "TrendFollowingProfessional"

        # Parámetros de la estrategia - OPTIMIZADOS PARA ANTI-LATERAL
        self.ema_fast = 34  # AUMENTADO: de 21 a 34 para señales más suaves
        self.ema_medium = 89  # AUMENTADO: de 50 a 89 para mejor filtrado
        self.ema_slow = 200  # EMA200 estándar para tendencias de largo plazo
        self.atr_period = 21  # AUMENTADO: de 14 a 21 para volatilidad más estable
        self.adx_period = (
            21  # AUMENTADO: de 14 a 21 para fuerza de tendencia más confiable
        )
        self.rsi_period = 21  # AUMENTADO: de 14 a 21 para menos ruido
        self.volume_sma = 34  # AUMENTADO: de 20 a 34 para volumen más estable

    def get_market_data(
        self, symbol: str, timeframe: str = "1h", limit: int = 600  # AUMENTADO: de 500 a 600 para EMA200
    ) -> pd.DataFrame:
        """Obtiene datos de mercado - será inyectado por el adaptador"""
        # Este método será sobrescrito por el adaptador con datos reales
        logger.warning(
            f"get_market_data no ha sido inyectado correctamente para {symbol}"
        )
        return pd.DataFrame()

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos los indicadores técnicos necesarios"""
        if df.empty:
            return df

        # EMAs para análisis de tendencia
        df["ema_21"] = ta.ema(df["close"], length=self.ema_fast)
        df["ema_50"] = ta.ema(df["close"], length=self.ema_medium)
        df["ema_200"] = ta.ema(df["close"], length=self.ema_slow)

        # ATR para volatilidad y stops
        df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=self.atr_period)

        # ADX para fuerza de tendencia
        adx_data = ta.adx(df["high"], df["low"], df["close"], length=self.adx_period)
        df["adx"] = adx_data[f"ADX_{self.adx_period}"]
        df["di_plus"] = adx_data[f"DMP_{self.adx_period}"]
        df["di_minus"] = adx_data[f"DMN_{self.adx_period}"]

        # RSI para momentum
        df["rsi"] = ta.rsi(df["close"], length=self.rsi_period)

        # MACD para momentum y divergencias
        macd_data = ta.macd(df["close"])
        df["macd"] = macd_data["MACD_12_26_9"]
        df["macd_signal"] = macd_data["MACDs_12_26_9"]
        df["macd_histogram"] = macd_data["MACDh_12_26_9"]

        # Volumen
        df["volume_sma"] = ta.sma(df["volume"], length=self.volume_sma)
        df["volume_ratio"] = df["volume"] / df["volume_sma"]

        # Bollinger Bands para volatilidad
        bb_data = ta.bbands(df["close"], length=20)
        df["bb_upper"] = bb_data["BBU_20_2.0"]
        df["bb_middle"] = bb_data["BBM_20_2.0"]
        df["bb_lower"] = bb_data["BBL_20_2.0"]
        df["bb_width"] = (df["bb_upper"] - df["bb_lower"]) / df["bb_middle"]

        return df

    def analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analiza la estructura de mercado (HH/HL vs LH/LL)"""
        if len(df) < 50:
            return {"structure": "insufficient_data", "strength": 0}

        # Identificar pivots (simplificado)
        highs = df["high"].rolling(window=5, center=True).max() == df["high"]
        lows = df["low"].rolling(window=5, center=True).min() == df["low"]

        # Obtener últimos 10 pivots altos y bajos
        recent_highs = df[highs]["high"].tail(5).values
        recent_lows = df[lows]["low"].tail(5).values

        if len(recent_highs) < 3 or len(recent_lows) < 3:
            return {"structure": "insufficient_pivots", "strength": 0}

        # Analizar tendencia de highs y lows
        higher_highs = sum(
            recent_highs[i] > recent_highs[i - 1] for i in range(1, len(recent_highs))
        )
        higher_lows = sum(
            recent_lows[i] > recent_lows[i - 1] for i in range(1, len(recent_lows))
        )

        lower_highs = sum(
            recent_highs[i] < recent_highs[i - 1] for i in range(1, len(recent_highs))
        )
        lower_lows = sum(
            recent_lows[i] < recent_lows[i - 1] for i in range(1, len(recent_lows))
        )

        # Determinar estructura
        if higher_highs >= 3 and higher_lows >= 2:
            return {
                "structure": "uptrend",
                "strength": (higher_highs + higher_lows) / 6,
            }
        elif lower_highs >= 3 and lower_lows >= 2:
            return {
                "structure": "downtrend",
                "strength": (lower_highs + lower_lows) / 6,
            }
        else:
            return {"structure": "sideways", "strength": 0.3}

    def analyze_trend_alignment(self, df: pd.DataFrame) -> Dict:
        """Verifica alineación de tendencia en múltiples timeframes - VERSIÓN MENOS ESTRICTA"""
        if df.empty or len(df) < self.ema_slow:
            return {"aligned": False, "direction": "neutral", "strength": 0}

        current = df.iloc[-1]

        # Verificar orden de EMAs
        emas_bullish = current["ema_21"] > current["ema_50"] > current["ema_200"]
        emas_bearish = current["ema_21"] < current["ema_50"] < current["ema_200"]

        # Verificar precio vs EMAs
        price_above_emas = current["close"] > current["ema_21"]
        price_below_emas = current["close"] < current["ema_21"]

        # Verificar pendiente de EMAs (más tolerante)
        ema21_slope = (current["ema_21"] - df["ema_21"].iloc[-5]) / 5
        ema50_slope = (current["ema_50"] - df["ema_50"].iloc[-5]) / 5

        # CRITERIOS MENOS ESTRICTOS - Solo necesita 2 de 3 condiciones
        
        # Tendencia alcista fuerte (todas las condiciones)
        if emas_bullish and price_above_emas and ema21_slope > 0 and ema50_slope > 0:
            return {"aligned": True, "direction": "bullish", "strength": 0.9}
        
        # Tendencia bajista fuerte (todas las condiciones)
        elif emas_bearish and price_below_emas and ema21_slope < 0 and ema50_slope < 0:
            return {"aligned": True, "direction": "bearish", "strength": 0.9}
        
        # Tendencia alcista moderada (2 de 3 condiciones)
        elif (emas_bullish and price_above_emas) or (emas_bullish and ema21_slope > 0) or (price_above_emas and ema21_slope > 0):
            return {"aligned": True, "direction": "bullish", "strength": 0.6}
        
        # Tendencia bajista moderada (2 de 3 condiciones) - NUEVO
        elif (emas_bearish and price_below_emas) or (emas_bearish and ema21_slope < 0) or (price_below_emas and ema21_slope < 0):
            return {"aligned": True, "direction": "bearish", "strength": 0.6}
        
        # Tendencia alcista débil (solo EMAs o solo precio)
        elif emas_bullish or (price_above_emas and ema21_slope > 0):
            return {"aligned": True, "direction": "bullish", "strength": 0.4}
        
        # Tendencia bajista débil (solo EMAs o solo precio) - NUEVO
        elif emas_bearish or (price_below_emas and ema21_slope < 0):
            return {"aligned": True, "direction": "bearish", "strength": 0.4}
        
        else:
            return {"aligned": False, "direction": "neutral", "strength": 0.3}

    def analyze_multi_timeframe_alignment(self, symbol: str) -> Dict:
        """🎯 NUEVA FUNCIÓN: Validación estricta de alineación multi-timeframe

        Analiza la alineación de tendencias en múltiples timeframes para evitar
        trades contradictorios como la venta de GOLD con tendencia alcista en 4h.

        Args:
            symbol: Símbolo a analizar

        Returns:
            Dict con información de alineación multi-timeframe
        """
        from src.config.main_config import TradingProfiles

        # Obtener configuración del perfil actual
        profile = TradingProfiles.get_current_profile()
        timeframes = profile.get("timeframes", ["30m", "1h", "4h"])
        mtf_require_alignment = profile.get("mtf_require_trend_alignment", True)
        mtf_min_consensus = profile.get("mtf_min_consensus", 0.80)

        if not mtf_require_alignment:
            return {
                "aligned": True,
                "consensus": 1.0,
                "details": "MTF validation disabled",
                "has_conflict": False,
                "conflict_details": [],
            }

        timeframe_analysis = {}
        trend_directions = []
        alignment_scores = []

        logger.info(
            f"🔍 Analizando alineación multi-timeframe para {symbol} en {timeframes}"
        )

        # Analizar cada timeframe
        for tf in timeframes:
            try:
                df = self.get_market_data(symbol, tf, limit=250)
                if df.empty or len(df) < self.ema_slow:
                    logger.warning(f"⚠️ Datos insuficientes para {symbol} en {tf}")
                    continue

                # Calcular indicadores para este timeframe
                df = self.calculate_technical_indicators(df)

                # Analizar tendencia en este timeframe
                trend_analysis = self.analyze_trend_alignment(df)
                structure_analysis = self.analyze_market_structure(df)

                timeframe_analysis[tf] = {
                    "trend": trend_analysis,
                    "structure": structure_analysis,
                    "direction": trend_analysis["direction"],
                    "strength": trend_analysis["strength"],
                }

                trend_directions.append(trend_analysis["direction"])
                alignment_scores.append(trend_analysis["strength"])

                logger.info(
                    f"📊 {tf}: {trend_analysis['direction']} (fuerza: {trend_analysis['strength']:.2f})"
                )

            except Exception as e:
                logger.error(f"❌ Error analizando {tf} para {symbol}: {e}")
                continue

        # Validar que tenemos suficientes timeframes
        if len(timeframe_analysis) < 2:
            logger.warning(f"⚠️ Insuficientes timeframes analizados para {symbol}")
            return {
                "aligned": False,
                "consensus": 0.0,
                "details": "Insufficient timeframes",
                "has_conflict": False,
                "conflict_details": [],
            }

        # Calcular consenso de direcciones
        bullish_count = trend_directions.count("bullish")
        bearish_count = trend_directions.count("bearish")
        neutral_count = trend_directions.count("neutral")
        total_count = len(trend_directions)

        # Determinar dirección dominante
        if bullish_count > bearish_count and bullish_count > neutral_count:
            dominant_direction = "bullish"
            consensus_ratio = bullish_count / total_count
        elif bearish_count > bullish_count and bearish_count > neutral_count:
            dominant_direction = "bearish"
            consensus_ratio = bearish_count / total_count
        else:
            dominant_direction = "neutral"
            consensus_ratio = (
                max(bullish_count, bearish_count, neutral_count) / total_count
            )

        # Verificar si hay conflictos críticos
        has_conflict = False
        conflict_details = []

        # CRÍTICO: Detectar conflictos entre timeframes cortos y largos
        if len(timeframes) >= 3:
            short_tf = timeframes[0]  # 30m
            medium_tf = timeframes[1]  # 1h
            long_tf = timeframes[-1]  # 4h

            short_direction = timeframe_analysis.get(short_tf, {}).get(
                "direction", "neutral"
            )
            medium_direction = timeframe_analysis.get(medium_tf, {}).get(
                "direction", "neutral"
            )
            long_direction = timeframe_analysis.get(long_tf, {}).get(
                "direction", "neutral"
            )

            # Conflicto crítico: timeframe largo opuesto a cortos
            if (long_direction == "bullish" and short_direction == "bearish") or (
                long_direction == "bearish" and short_direction == "bullish"
            ):
                has_conflict = True
                conflict_details.append(
                    f"Conflicto crítico: {long_tf}={long_direction} vs {short_tf}={short_direction}"
                )
                logger.warning(
                    f"🚨 CONFLICTO CRÍTICO detectado en {symbol}: {long_tf}={long_direction} vs {short_tf}={short_direction}"
                )

        # Calcular fuerza promedio de alineación
        avg_strength = (
            sum(alignment_scores) / len(alignment_scores) if alignment_scores else 0.0
        )

        # Determinar si está alineado
        is_aligned = (
            consensus_ratio >= mtf_min_consensus
            and not has_conflict
            and avg_strength >= 0.5
            and dominant_direction != "neutral"
        )

        result = {
            "aligned": is_aligned,
            "consensus": consensus_ratio,
            "dominant_direction": dominant_direction,
            "avg_strength": avg_strength,
            "has_conflict": has_conflict,
            "conflict_details": conflict_details,
            "timeframe_analysis": timeframe_analysis,
            "details": f"Consenso: {consensus_ratio:.1%}, Dirección: {dominant_direction}, Conflictos: {has_conflict}",
        }

        if not is_aligned:
            logger.warning(
                f"🚫 Alineación MTF RECHAZADA para {symbol}: {result['details']}"
            )
        else:
            logger.info(
                f"✅ Alineación MTF APROBADA para {symbol}: {result['details']}"
            )

        return result

    def analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analiza momentum y divergencias"""
        if df.empty or len(df) < 20:
            return {"momentum": "neutral", "strength": 0, "divergence": False}

        current = df.iloc[-1]

        # Análisis de RSI
        rsi_bullish = 30 < current["rsi"] < 70 and current["rsi"] > df["rsi"].iloc[-5]
        rsi_bearish = 30 < current["rsi"] < 70 and current["rsi"] < df["rsi"].iloc[-5]
        rsi_overbought = current["rsi"] > 70
        rsi_oversold = current["rsi"] < 30

        # Análisis de MACD
        macd_bullish = (
            current["macd"] > current["macd_signal"] and current["macd_histogram"] > 0
        )
        macd_bearish = (
            current["macd"] < current["macd_signal"] and current["macd_histogram"] < 0
        )

        # Análisis de ADX
        adx_strong = current["adx"] > 25
        di_bullish = current["di_plus"] > current["di_minus"]
        di_bearish = current["di_plus"] < current["di_minus"]

        # Combinar señales
        bullish_signals = sum([rsi_bullish, macd_bullish, di_bullish and adx_strong])
        bearish_signals = sum([rsi_bearish, macd_bearish, di_bearish and adx_strong])

        if bullish_signals >= 2 and not rsi_overbought:
            return {
                "momentum": "bullish",
                "strength": bullish_signals / 3,
                "divergence": False,
            }
        elif bearish_signals >= 2 and not rsi_oversold:
            return {
                "momentum": "bearish",
                "strength": bearish_signals / 3,
                "divergence": False,
            }
        else:
            return {"momentum": "neutral", "strength": 0.3, "divergence": False}

    def analyze_volume_confirmation(self, df: pd.DataFrame) -> Dict:
        """Analiza confirmación por volumen"""
        if df.empty or len(df) < self.volume_sma:
            return {"confirmed": False, "strength": 0}

        current = df.iloc[-1]

        # Volumen por encima de la media
        volume_above_average = current["volume_ratio"] > 1.2

        # Volumen creciente en últimas 3 velas
        volume_increasing = df["volume"].tail(3).is_monotonic_increasing

        # Precio y volumen en la misma dirección
        price_change = (current["close"] - df["close"].iloc[-2]) / df["close"].iloc[-2]
        volume_change = (current["volume"] - df["volume"].iloc[-2]) / df["volume"].iloc[
            -2
        ]

        same_direction = (price_change > 0 and volume_change > 0) or (
            price_change < 0 and volume_change > 0
        )

        confirmations = sum([volume_above_average, volume_increasing, same_direction])

        return {
            "confirmed": confirmations >= 2,
            "strength": confirmations / 3,
            "volume_ratio": current["volume_ratio"],
        }

    def determine_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Determina el régimen de mercado actual"""
        if df.empty or len(df) < 50:
            return MarketRegime.RANGING

        current = df.iloc[-1]

        # Análisis de volatilidad
        volatility_percentile = self.calculate_volatility_percentile(df)

        # Análisis de tendencia
        trend_analysis = self.analyze_trend_alignment(df)
        structure_analysis = self.analyze_market_structure(df)

        # Análisis de breakout
        bb_squeeze = current["bb_width"] < df["bb_width"].rolling(20).mean() * 0.8
        recent_breakout = (
            current["close"] > current["bb_upper"]
            or current["close"] < current["bb_lower"]
        )

        # Determinar régimen
        if recent_breakout and current["adx"] > 30:
            return MarketRegime.BREAKOUT
        elif volatility_percentile > 80:
            return MarketRegime.VOLATILE
        elif trend_analysis["aligned"] and trend_analysis["strength"] > 0.7:
            if trend_analysis["direction"] == "bullish":
                return MarketRegime.TRENDING_UP
            else:
                return MarketRegime.TRENDING_DOWN
        else:
            return MarketRegime.RANGING

    def calculate_volatility_percentile(
        self, df: pd.DataFrame, period: int = 100
    ) -> float:
        """Calcula el percentil de volatilidad actual"""
        if len(df) < period:
            return 50.0

        current_volatility = df["atr"].iloc[-1]
        historical_volatility = df["atr"].tail(period)

        percentile = (
            (historical_volatility < current_volatility).sum()
            / len(historical_volatility)
            * 100
        )
        return percentile

    def calculate_stop_loss_take_profit(
        self, df: pd.DataFrame, signal_type: str, entry_price: float
    ) -> Tuple[float, float]:
        """Calcula stop loss y take profit basado en ATR"""
        if df.empty:
            return entry_price, entry_price

        current_atr = df["atr"].iloc[-1]
        atr_multiplier_sl = 2.0  # Stop loss a 2 ATR
        atr_multiplier_tp = 3.0  # Take profit a 3 ATR (1:1.5 R/R)

        if signal_type == "BUY":
            stop_loss = entry_price - (current_atr * atr_multiplier_sl)
            take_profit = entry_price + (current_atr * atr_multiplier_tp)
        else:  # SELL
            stop_loss = entry_price + (current_atr * atr_multiplier_sl)
            take_profit = entry_price - (current_atr * atr_multiplier_tp)

        return stop_loss, take_profit

    def analyze(self, symbol: str, timeframe: str = "1h") -> Optional[EnhancedSignal]:
        """Análisis principal de la estrategia"""
        try:
            # 1. Obtener datos de mercado
            df = self.get_market_data(symbol, timeframe)
            if df.empty:
                logger.warning(f"No se pudieron obtener datos para {symbol}")
                return None

            # 2. 🎯 VALIDACIÓN MULTI-TIMEFRAME CRÍTICA (NUEVA)
            # Esta validación debe ejecutarse ANTES que cualquier otro análisis
            # para evitar trades contradictorios como la venta de GOLD con tendencia alcista en 4h
            mtf_analysis = self.analyze_multi_timeframe_alignment(symbol)

            if not mtf_analysis["aligned"]:
                logger.warning(
                    f"🚫 TRADE RECHAZADO por conflicto multi-timeframe en {symbol}: {mtf_analysis['details']}"
                )
                if mtf_analysis["has_conflict"]:
                    for conflict in mtf_analysis["conflict_details"]:
                        logger.warning(f"   ⚠️ {conflict}")
                return None

            logger.info(
                f"✅ Validación multi-timeframe APROBADA para {symbol}: {mtf_analysis['details']}"
            )

            # 2.5. NUEVO: Filtro de horario de trading para mercados estadounidenses
            trading_hours = self._is_us_trading_hours(symbol)
            if not trading_hours["is_trading_hours"]:
                logger.info(
                    f"🕘 Trading fuera de horario para {symbol}: {trading_hours['reason']}"
                )
                return None

            # 3. Calcular indicadores técnicos
            df = self.calculate_technical_indicators(df)

            # 4. Análisis de componentes (ahora con validación MTF previa)
            trend_analysis = self.analyze_trend_alignment(df)
            momentum_analysis = self.analyze_momentum(df)
            volume_analysis = self.analyze_volume_confirmation(df)
            structure_analysis = self.analyze_market_structure(df)
            market_regime = self.determine_market_regime(df)

            current_price = df["close"].iloc[-1]

            # 5. FILTROS AVANZADOS - Detectar mercado lateral y volatilidad
            sideways_analysis = self.detect_sideways_market(df)
            volatility_analysis = self.calculate_volatility_filter(df)

            # NUEVO: Filtro crítico mejorado - Anular solo en casos extremos de mercado lateral
            if (
                sideways_analysis["is_sideways"]
                and sideways_analysis["confidence"] > 80.0
            ):
                logger.info(
                    f"🚫 Mercado lateral extremo detectado para {symbol}: {sideways_analysis['reason']}"
                )
                return None

            # Filtro crítico: Evitar trades sin volatilidad suficiente
            if not volatility_analysis["sufficient_volatility"]:
                logger.info(
                    f"🚫 Volatilidad insuficiente para {symbol}: {volatility_analysis['reason']}"
                )
                return None

            # 6. Determinar tipo de señal basado en confluencias MEJORADAS
            # Ahora con validación adicional de que la dirección coincida con MTF
            signal_type = "HOLD"
            confluence_count = 0
            confluence_details = []

            # Lógica de señal BUY MEJORADA con validación MTF
            if (
                trend_analysis["aligned"]
                and trend_analysis["direction"] == "bullish"
                and momentum_analysis["momentum"] == "bullish"
                and structure_analysis["structure"]
                in ["uptrend"]  # REMOVIDO "sideways"
                and not sideways_analysis["is_sideways"]  # FILTRO ADICIONAL
                and mtf_analysis["dominant_direction"] == "bullish"
            ):  # 🎯 NUEVA VALIDACIÓN MTF

                signal_type = "BUY"
                confluence_count += 1
                confluence_details.append("Tendencia alcista alineada")

                # Confluencia adicional por alineación MTF
                confluence_count += 1
                confluence_details.append(
                    f"Alineación MTF alcista (consenso: {mtf_analysis['consensus']:.1%})"
                )

                if momentum_analysis["strength"] > 0.6:  # AJUSTADO de 0.7 a 0.6 para ser menos estricto
                    confluence_count += 1
                    confluence_details.append("Momentum alcista fuerte")

                if volume_analysis["confirmed"]:
                    confluence_count += 1
                    confluence_details.append("Volumen confirmatorio")

                if market_regime in [MarketRegime.TRENDING_UP, MarketRegime.BREAKOUT]:
                    confluence_count += 1
                    confluence_details.append(
                        f"Régimen favorable: {market_regime.value}"
                    )

                # NUEVA CONFLUENCIA: Volatilidad adecuada
                if volatility_analysis["atr_normalized"] > 0.005:  # ATR > 0.5% (ajustado de 1% para ser menos estricto)
                    confluence_count += 1
                    confluence_details.append("Volatilidad favorable para trading")

            # Lógica de señal SELL MEJORADA con validación MTF
            elif (
                trend_analysis["aligned"]
                and trend_analysis["direction"] == "bearish"
                and momentum_analysis["momentum"] == "bearish"
                and structure_analysis["structure"]
                in ["downtrend"]  # REMOVIDO "sideways"
                and not sideways_analysis["is_sideways"]  # FILTRO ADICIONAL
                and mtf_analysis["dominant_direction"] == "bearish"
            ):  # 🎯 NUEVA VALIDACIÓN MTF

                signal_type = "SELL"
                confluence_count += 1
                confluence_details.append("Tendencia bajista alineada")

                # Confluencia adicional por alineación MTF
                confluence_count += 1
                confluence_details.append(
                    f"Alineación MTF bajista (consenso: {mtf_analysis['consensus']:.1%})"
                )

                if momentum_analysis["strength"] > 0.6:  # AJUSTADO de 0.7 a 0.6 para ser menos estricto
                    confluence_count += 1
                    confluence_details.append("Momentum bajista fuerte")

                if volume_analysis["confirmed"]:
                    confluence_count += 1
                    confluence_details.append("Volumen confirmatorio")

                if market_regime in [MarketRegime.TRENDING_DOWN, MarketRegime.BREAKOUT]:
                    confluence_count += 1
                    confluence_details.append(
                        f"Régimen favorable: {market_regime.value}"
                    )

                # NUEVA CONFLUENCIA: Volatilidad adecuada
                if volatility_analysis["atr_normalized"] > 0.005:  # ATR > 0.5% (ajustado de 1% para ser menos estricto)
                    confluence_count += 1
                    confluence_details.append("Volatilidad favorable para trading")

            # 5. Calcular stop loss y take profit
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(
                df, signal_type, current_price
            )

            # 6. Calcular métricas de riesgo
            risk_amount = abs(current_price - stop_loss)
            reward_amount = abs(take_profit - current_price)
            risk_reward_ratio = reward_amount / risk_amount if risk_amount > 0 else 0

            # 7. Crear señal profesional
            signal = EnhancedSignal(
                symbol=symbol,
                signal_type=signal_type,
                price=current_price,
                confidence_score=0.0,  # Se calculará después
                strength=(
                    "Strong"
                    if confluence_count >= 5
                    else "Moderate" if confluence_count >= 3 else "Weak"
                ),
                strategy_name=self.name,
                timestamp=datetime.now(),
                # Componentes de análisis EnhancedSignal
                volume_confirmation=volume_analysis["confirmed"],
                trend_confirmation=(
                    "BULLISH"
                    if signal_type == "BUY"
                    else "BEARISH" if signal_type == "SELL" else "NEUTRAL"
                ),
                risk_reward_ratio=risk_reward_ratio,
                stop_loss_price=stop_loss,
                take_profit_price=take_profit,
                market_regime=(
                    market_regime.value
                    if hasattr(market_regime, "value")
                    else str(market_regime)
                ),
                confluence_score=confluence_count,
                timeframe=timeframe,
                # Notas adicionales
                notes=f"Trend: {trend_analysis['direction']}, Momentum: {momentum_analysis['momentum']}, Structure: {structure_analysis['structure']}, R/R: {risk_reward_ratio:.2f}",
            )

            # 8. Calcular confianza basada en confluencias
            base_confidence = 50.0
            confluence_bonus = confluence_count * 8.0  # 8% por confluencia
            volume_bonus = 10.0 if volume_analysis["confirmed"] else 0.0
            trend_bonus = 15.0 if trend_analysis["aligned"] else 0.0

            # NUEVO: Ponderación por ADX - Aumentar confianza cuando ADX > 25 (tendencia fuerte)
            current_adx = df["adx"].iloc[-1] if not pd.isna(df["adx"].iloc[-1]) else 20
            adx_bonus = 0.0
            if current_adx > 25:
                # Bonus progresivo: 5% base + 0.2% por cada punto de ADX sobre 25
                adx_bonus = 5.0 + (current_adx - 25) * 0.2
                adx_bonus = min(adx_bonus, 15.0)  # Máximo 15% de bonus
                logger.info(
                    f"📈 ADX fuerte detectado para {symbol} (ADX: {current_adx:.1f}) - Aumentando confianza en {adx_bonus:.1f}%"
                )

            # NUEVO: Penalización por mercado lateral
            sideways_penalty = 0.0
            if (
                sideways_analysis["is_sideways"]
                and sideways_analysis["confidence"] > 60.0
            ):
                # Reducir confianza proporcionalmente a la confianza de detección lateral
                sideways_penalty = (
                    sideways_analysis["confidence"] - 60.0
                ) * 0.5  # 0.5% por cada 1% de confianza lateral
                logger.info(
                    f"⚠️ Mercado lateral detectado para {symbol} (confianza: {sideways_analysis['confidence']:.1f}%) - Reduciendo confianza en {sideways_penalty:.1f}%"
                )

            signal.confidence_score = min(
                95.0,
                base_confidence
                + confluence_bonus
                + volume_bonus
                + trend_bonus
                + adx_bonus
                - sideways_penalty,
            )

            # 9. Filtros básicos de calidad MEJORADOS
            if signal.confidence_score < 55.0:  # AJUSTADO temporalmente de 60% a 55%
                logger.info(
                    f"Señal para {symbol} no alcanza confianza mínima (55%): {signal.confidence_score:.1f}%"
                )
                return None

            if confluence_count < 3:  # AJUSTADO de 4 a 3 confluencias para ser menos estricto
                logger.info(
                    f"Señal para {symbol} no tiene suficientes confluencias: {confluence_count} (mínimo 3)"
                )
                return None

            # 10. Filtro adicional de Risk/Reward ratio
            if risk_reward_ratio < 1.5:  # NUEVO: R/R mínimo de 1.5:1
                logger.info(
                    f"Señal para {symbol} tiene R/R insuficiente: {risk_reward_ratio:.2f} (mínimo 1.5)"
                )
                return None

            return signal

        except Exception as e:
            logger.error(f"Error en análisis de {symbol}: {str(e)}")
            return None

    def detect_sideways_market(self, df: pd.DataFrame) -> Dict:
        """🔍 Detecta mercados laterales para evitar trades innecesarios"""
        if len(df) < 50:
            return {
                "is_sideways": False,
                "confidence": 0.0,
                "reason": "insufficient_data",
            }

        try:
            # Obtener configuración del perfil actual
            from src.config.main_config import TradingProfiles

            profile = TradingProfiles.get_current_profile()
            sideways_detection_period = profile.get(
                "sideways_detection_period", 120
            )  # Default 120 minutos

            # Convertir período de minutos a número de velas (asumiendo timeframe de 1h = 60 min)
            # Para 1h timeframe: 120 min = 2 velas
            # Para 15m timeframe: 120 min = 8 velas
            # Para 5m timeframe: 120 min = 24 velas
            timeframe_minutes = self._get_timeframe_minutes()
            detection_candles = max(
                5, min(50, sideways_detection_period // timeframe_minutes)
            )

            # 1. Análisis de rango de precios (período dinámico basado en configuración)
            recent_data = df.tail(detection_candles)
            price_range = (
                recent_data["high"].max() - recent_data["low"].min()
            ) / recent_data["close"].mean()

            # 2. Análisis de EMAs - mercado lateral si están muy cerca
            current_ema21 = df["ema_21"].iloc[-1] if not pd.isna(df["ema_21"].iloc[-1]) else None
            current_ema50 = df["ema_50"].iloc[-1] if not pd.isna(df["ema_50"].iloc[-1]) else None
            current_ema200 = df["ema_200"].iloc[-1] if not pd.isna(df["ema_200"].iloc[-1]) else None

            # Calcular distancias entre EMAs (solo si ambos valores son válidos)
            ema_21_50_distance = (
                abs(current_ema21 - current_ema50) / current_ema50
                if current_ema21 is not None and current_ema50 is not None and current_ema50 != 0
                else 1.0  # Valor por defecto que indica EMAs no convergentes
            )
            ema_50_200_distance = (
                abs(current_ema50 - current_ema200) / current_ema200
                if current_ema50 is not None and current_ema200 is not None and current_ema200 != 0
                else 1.0  # Valor por defecto que indica EMAs no convergentes
            )

            # 3. Análisis de ADX - valores bajos indican mercado lateral
            current_adx = df["adx"].iloc[-1] if not pd.isna(df["adx"].iloc[-1]) else 25

            # 4. Análisis de volatilidad (Bollinger Bands width)
            bb_width = (
                df["bb_width"].iloc[-1]
                if not pd.isna(df["bb_width"].iloc[-1])
                else 0.05
            )

            # 5. Análisis de momentum (MACD)
            macd_histogram = df["macd_histogram"].tail(5)
            macd_oscillations = len(
                [
                    i
                    for i in range(1, len(macd_histogram))
                    if (macd_histogram.iloc[i] > 0) != (macd_histogram.iloc[i - 1] > 0)
                ]
            )

            # 6. Criterios para mercado lateral
            sideways_indicators = []

            # Rango de precios estrecho (< 3%)
            if price_range < 0.03:
                sideways_indicators.append("narrow_price_range")

            # EMAs muy cercanas (< 1.5%)
            if ema_21_50_distance < 0.015 and ema_50_200_distance < 0.015:
                sideways_indicators.append("emas_converged")

            # ADX bajo (< 25 = tendencia débil)
            if current_adx < 25:
                sideways_indicators.append("weak_trend_adx")

            # Baja volatilidad (BB width < 0.03)
            if bb_width < 0.03:
                sideways_indicators.append("low_volatility")

            # MACD oscilando mucho (> 2 cambios de signo en 5 velas)
            if macd_oscillations >= 2:
                sideways_indicators.append("macd_oscillating")

            # 7. Determinar si es mercado lateral
            sideways_count = len(sideways_indicators)
            is_sideways = sideways_count >= 3  # Al menos 3 de 5 indicadores
            confidence = min(95.0, sideways_count * 20.0)  # 20% por indicador

            return {
                "is_sideways": is_sideways,
                "confidence": confidence,
                "indicators": sideways_indicators,
                "metrics": {
                    "price_range": price_range,
                    "ema_distance": ema_21_50_distance,
                    "adx": current_adx,
                    "bb_width": bb_width,
                    "macd_oscillations": macd_oscillations,
                },
                "reason": f"Detected {sideways_count}/5 sideways indicators: {', '.join(sideways_indicators)}",
            }

        except Exception as e:
            logger.error(f"Error detecting sideways market: {e}")
            return {"is_sideways": False, "confidence": 0.0, "reason": f"error: {e}"}

    def calculate_volatility_filter(self, df: pd.DataFrame) -> Dict:
        """📊 Filtro de volatilidad para evitar trades en mercados sin movimiento"""
        if len(df) < 20:
            return {"sufficient_volatility": True, "reason": "insufficient_data"}

        try:
            # 1. ATR normalizado (ATR / precio)
            current_atr = df["atr"].iloc[-1]
            current_price = df["close"].iloc[-1]
            atr_normalized = current_atr / current_price

            # 2. Volatilidad histórica (últimas 20 velas)
            returns = df["close"].pct_change().tail(20)
            historical_volatility = returns.std() * np.sqrt(
                24
            )  # Anualizada para crypto

            # 3. Rango verdadero promedio
            true_ranges = []
            for i in range(1, min(21, len(df))):
                tr = max(
                    df["high"].iloc[-i] - df["low"].iloc[-i],
                    abs(df["high"].iloc[-i] - df["close"].iloc[-i - 1]),
                    abs(df["low"].iloc[-i] - df["close"].iloc[-i - 1]),
                )
                true_ranges.append(tr / df["close"].iloc[-i])

            avg_true_range = np.mean(true_ranges) if true_ranges else 0

            # 4. Criterios de volatilidad mínima (ajustados para ser más realistas)
            min_atr_normalized = 0.008  # 0.8% mínimo (reducido de 1.5%)
            min_historical_vol = 0.03   # 3% anualizada mínima (reducido de 5% para ser menos estricto)
            min_true_range = 0.008      # 0.8% rango verdadero mínimo (reducido de 1.2%)

            # 5. Evaluación (al menos 2 de 3 criterios deben cumplirse)
            volatility_criteria = [
                atr_normalized >= min_atr_normalized,
                historical_volatility >= min_historical_vol,
                avg_true_range >= min_true_range
            ]
            
            sufficient_volatility = sum(volatility_criteria) >= 2

            return {
                "sufficient_volatility": sufficient_volatility,
                "atr_normalized": atr_normalized,
                "historical_volatility": historical_volatility,
                "avg_true_range": avg_true_range,
                "reason": f"ATR: {atr_normalized:.3f}, HV: {historical_volatility:.3f}, TR: {avg_true_range:.3f}",
            }

        except Exception as e:
            logger.error(f"Error calculating volatility filter: {e}")
            return {"sufficient_volatility": True, "reason": f"error: {e}"}

    def _get_timeframe_minutes(self) -> int:
        """⏰ Convertir timeframe a minutos

        Returns:
            Número de minutos del timeframe actual
        """
        # Mapeo de timeframes comunes a minutos
        timeframe_map = {
            "1m": 1,
            "5m": 5,
            "15m": 15,
            "30m": 30,
            "1h": 60,
            "4h": 240,
            "1d": 1440,
        }

        # Obtener timeframe del perfil actual o usar default
        from src.config.main_config import TradingProfiles

        profile = TradingProfiles.get_current_profile()
        timeframes = profile.get("timeframes", ["1h"])
        current_timeframe = timeframes[0] if timeframes else "1h"

        return timeframe_map.get(current_timeframe, 60)  # Default 60 minutos (1h)

    def _is_us_trading_hours(self, symbol: str) -> Dict:
        """🕘 Verificar si estamos dentro del horario de trading de mercados estadounidenses

        Args:
            symbol: Símbolo del activo

        Returns:
            Dict con información del horario de trading
        """
        # Símbolos que requieren horario de trading estadounidense
        us_symbols = [
            "NVDA",
            "US500",
            "SPY",
            "QQQ",
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "TSLA",
        ]

        # Si no es un símbolo estadounidense, permitir trading 24/7
        if not any(us_sym in symbol.upper() for us_sym in us_symbols):
            return {
                "is_trading_hours": True,
                "reason": "24/7 market (crypto/forex)",
                "current_time": datetime.now(),
                "market_status": "open",
            }

        try:
            # Obtener hora actual en EST/EDT
            est = pytz.timezone("US/Eastern")
            current_time = datetime.now(est)

            # Verificar si es día de semana (lunes=0, domingo=6)
            weekday = current_time.weekday()
            if weekday >= 5:  # Sábado (5) o Domingo (6)
                return {
                    "is_trading_hours": False,
                    "reason": f"Weekend - Market closed",
                    "current_time": current_time,
                    "market_status": "closed_weekend",
                }

            # Verificar horario de trading (09:30 - 16:00 EST/EDT)
            market_open = current_time.replace(
                hour=9, minute=30, second=0, microsecond=0
            )
            market_close = current_time.replace(
                hour=16, minute=0, second=0, microsecond=0
            )

            is_open = market_open <= current_time <= market_close

            if is_open:
                return {
                    "is_trading_hours": True,
                    "reason": f"US market open (09:30-16:00 EST/EDT)",
                    "current_time": current_time,
                    "market_status": "open",
                }
            else:
                return {
                    "is_trading_hours": False,
                    "reason": f"US market closed - Current time: {current_time.strftime('%H:%M')} EST/EDT (Market: 09:30-16:00)",
                    "current_time": current_time,
                    "market_status": "closed_hours",
                }

        except Exception as e:
            logger.error(f"Error checking US trading hours: {e}")
            # En caso de error, permitir trading para no bloquear el sistema
            return {
                "is_trading_hours": True,
                "reason": f"Error checking hours: {e}",
                "current_time": datetime.now(),
                "market_status": "error_default_open",
            }


# Ejemplo de uso
if __name__ == "__main__":
    strategy = TrendFollowingProfessional()

    # Simular análisis (requiere integración con datos reales)
    signal = strategy.analyze("BTCUSD")

    if signal:
        print(f"📊 SEÑAL PROFESIONAL GENERADA:")
        print(f"Símbolo: {signal.symbol}")
        print(f"Señal: {signal.signal_type}")
        print(f"Precio: ${signal.price:.2f}")
        print(f"Confianza: {signal.confidence_score:.1f}%")
        print(f"Calidad: {signal.quality.value}")
        print(f"Stop Loss: ${signal.stop_loss_price:.2f}")
        print(f"Take Profit: ${signal.take_profit_price:.2f}")
        print(f"R/R Ratio: {signal.risk_reward_ratio:.2f}")
        print(f"Confluencias: {signal.confluence_score}")
        print(f"Detalles: {', '.join(signal.confluence_details)}")
    else:
        print("❌ No se generó señal o no pasó los filtros profesionales")
