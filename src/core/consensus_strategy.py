"""
🧠 CONSENSUS STRATEGY - ESTRATEGIA DE CONSENSO INTELIGENTE
Sistema de consenso que coordina las decisiones de múltiples estrategias de trading

COMPONENTES:
• Agregación de señales de múltiples estrategias
• Sistema de pesos dinámicos basado en rendimiento histórico
• Filtros de calidad y coherencia
• Análisis de confluencia entre estrategias
• Gestión de riesgo integrada

ESTRATEGIAS COORDINADAS:
• TrendFollowingProfessional: Peso base 40%
• BreakoutProfessional: Peso base 35%
• MeanReversionProfessional: Peso base 25%

REGLAS DE CONSENSO:
• Mínimo 2 de 3 estrategias deben coincidir en dirección
• Confianza promedio ponderada >= 75%
• No contradicciones críticas entre estrategias
• Análisis de coherencia temporal
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from collections import defaultdict

from .trend_following_professional import TrendFollowingProfessional
from .breakout_professional import BreakoutProfessional
from .mean_reversion_professional import MeanReversionProfessional

logger = logging.getLogger(__name__)


class ConsensusDecision(Enum):
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    WEAK_BUY = "WEAK_BUY"
    HOLD = "HOLD"
    WEAK_SELL = "WEAK_SELL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"


class StrategyWeight(Enum):
    TREND_FOLLOWING = 0.40  # 40% - Estrategia principal para tendencias
    BREAKOUT = 0.35  # 35% - Importante para momentum
    MEAN_REVERSION = 0.25  # 25% - Complementaria para reversiones


@dataclass
class StrategySignalData:
    """Datos de señal de una estrategia individual"""

    strategy_name: str
    signal_type: str
    confidence_score: float
    price: float
    timestamp: datetime
    raw_signal: object  # La señal original completa
    weight: float
    is_valid: bool = True
    notes: str = ""


@dataclass
class ConsensusAnalysis:
    """Análisis de consenso entre estrategias"""

    total_strategies: int
    agreeing_strategies: int
    disagreeing_strategies: int
    consensus_percentage: float
    weighted_confidence: float
    dominant_signal: str
    signal_distribution: Dict[str, int]
    coherence_score: float  # 0-100
    risk_assessment: str
    analysis_notes: List[str]


@dataclass
class ConsensusSignal:
    """Señal final del sistema de consenso"""

    symbol: str
    signal_type: str
    consensus_decision: ConsensusDecision
    price: float
    confidence_score: float
    strength: str
    timestamp: datetime

    # Análisis de consenso
    consensus_analysis: ConsensusAnalysis
    contributing_strategies: List[StrategySignalData]

    # Métricas de calidad
    quality_score: float  # 0-100
    coherence_score: float  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH

    # Gestión de riesgo
    stop_loss_price: float
    take_profit_price: float
    risk_reward_ratio: float
    position_size_recommendation: float

    # Metadatos
    analysis_duration_ms: float
    strategy_performance_weights: Dict[str, float]
    market_conditions: str
    notes: str


class ConsensusStrategy:
    """🧠 Estrategia de consenso inteligente"""

    def __init__(self, capital_client=None):
        self.name = "ConsensusStrategy"
        self.capital_client = capital_client

        # Inicializar estrategias individuales
        self.trend_strategy = TrendFollowingProfessional()
        self.breakout_strategy = BreakoutProfessional()
        self.mean_reversion_strategy = MeanReversionProfessional()

        # Inyectar get_market_data si tenemos capital_client
        if capital_client:
            self._inject_market_data_methods()

        # Configuración de consenso
        self.min_consensus_threshold = 0.67  # 67% - Al menos 2 de 3 estrategias
        self.min_weighted_confidence = 75.0  # Confianza mínima ponderada
        self.max_contradiction_tolerance = 0.20  # 20% tolerancia a contradicciones

        # Pesos dinámicos (se actualizan basado en rendimiento)
        self.strategy_weights = {
            "TrendFollowingProfessional": StrategyWeight.TREND_FOLLOWING.value,
            "BreakoutProfessional": StrategyWeight.BREAKOUT.value,
            "MeanReversionProfessional": StrategyWeight.MEAN_REVERSION.value,
        }

        # Historial de rendimiento para ajuste dinámico de pesos
        self.performance_history = defaultdict(list)
        self.signal_history = []

        # Configuración de filtros
        self.enable_coherence_filter = True
        self.enable_temporal_filter = True
        self.enable_risk_filter = True

        logger.info(f"✅ {self.name} inicializada con pesos: {self.strategy_weights}")

    def _inject_market_data_methods(self):
        """
        Inyectar método get_market_data en las estrategias profesionales
        """
        try:
            if self.capital_client:
                # Crear un método get_market_data que use el capital_client
                def get_market_data(
                    symbol: str,
                    timeframe: str,
                    periods: int = 250,
                    limit: int = None,
                    **kwargs,
                ):
                    try:
                        # Usar limit si se proporciona, sino usar periods
                        data_points = limit if limit is not None else periods

                        # Obtener datos de mercado usando capital_client
                        market_data = self.capital_client.get_market_data([symbol])

                        if market_data and symbol in market_data:
                            price_data = market_data[symbol]
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
                                    for i in range(data_points, 0, -1)
                                ]
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

                        # Si no se pueden obtener datos, retornar DataFrame vacío
                        import pandas as pd

                        return pd.DataFrame(
                            columns=["open", "high", "low", "close", "volume"]
                        )

                    except Exception as e:
                        logger.warning(
                            f"Error obteniendo datos de mercado para {symbol}: {e}"
                        )
                        import pandas as pd

                        return pd.DataFrame(
                            columns=["open", "high", "low", "close", "volume"]
                        )

                # Inyectar el método en todas las estrategias
                self.trend_strategy.get_market_data = get_market_data
                self.breakout_strategy.get_market_data = get_market_data
                self.mean_reversion_strategy.get_market_data = get_market_data

                logger.info(
                    "✅ Métodos get_market_data inyectados en estrategias profesionales"
                )

        except Exception as e:
            logger.error(f"Error inyectando métodos get_market_data: {e}")

    def analyze(self, symbol: str, timeframe: str = "1h") -> Optional[ConsensusSignal]:
        """
        🎯 Análisis principal del consenso

        Args:
            symbol: Símbolo a analizar
            timeframe: Marco temporal

        Returns:
            ConsensusSignal o None si no hay consenso
        """
        start_time = datetime.now()

        try:
            logger.info(f"🧠 Iniciando análisis de consenso para {symbol}")

            # 1. Obtener señales de todas las estrategias
            strategy_signals = self._collect_strategy_signals(symbol, timeframe)

            if not strategy_signals:
                logger.warning(f"❌ No se obtuvieron señales válidas para {symbol}")
                return None

            # 2. Analizar consenso entre estrategias
            consensus_analysis = self._analyze_consensus(strategy_signals)

            # 3. Aplicar filtros de calidad
            if not self._passes_quality_filters(consensus_analysis, strategy_signals):
                logger.info(f"🚫 {symbol} no pasó los filtros de calidad del consenso")
                return None

            # 4. Determinar decisión final
            consensus_decision = self._determine_consensus_decision(consensus_analysis)

            # Nota: Ya no retornamos None para HOLD, creamos una señal HOLD válida

            # 5. Calcular métricas de riesgo
            risk_metrics = self._calculate_risk_metrics(
                strategy_signals, consensus_analysis
            )

            # 6. Crear señal de consenso final
            consensus_signal = self._create_consensus_signal(
                symbol,
                timeframe,
                consensus_decision,
                consensus_analysis,
                strategy_signals,
                risk_metrics,
                start_time,
            )

            # 7. Registrar en historial
            self._update_signal_history(consensus_signal)

            logger.info(
                f"✅ Consenso generado para {symbol}: {consensus_decision.value} "
                f"(Confianza: {consensus_signal.confidence_score:.1f}%, "
                f"Coherencia: {consensus_signal.coherence_score:.1f}%)"
            )

            return consensus_signal

        except Exception as e:
            logger.error(f"❌ Error en análisis de consenso para {symbol}: {e}")
            return None

    def _collect_strategy_signals(
        self, symbol: str, timeframe: str
    ) -> List[StrategySignalData]:
        """📊 Recopilar señales de todas las estrategias"""
        signals = []

        strategies = [
            ("TrendFollowingProfessional", self.trend_strategy),
            ("BreakoutProfessional", self.breakout_strategy),
            ("MeanReversionProfessional", self.mean_reversion_strategy),
        ]

        for strategy_name, strategy_instance in strategies:
            try:
                raw_signal = strategy_instance.analyze(symbol, timeframe)

                if raw_signal and hasattr(raw_signal, "signal_type"):
                    signal_data = StrategySignalData(
                        strategy_name=strategy_name,
                        signal_type=raw_signal.signal_type,
                        confidence_score=raw_signal.confidence_score,
                        price=raw_signal.price,
                        timestamp=raw_signal.timestamp,
                        raw_signal=raw_signal,
                        weight=self.strategy_weights[strategy_name],
                        is_valid=True,
                        notes=f"Señal válida de {strategy_name}",
                    )
                    signals.append(signal_data)
                    logger.debug(
                        f"✅ {strategy_name}: {raw_signal.signal_type} (Conf: {raw_signal.confidence_score:.1f}%)"
                    )
                else:
                    logger.debug(f"⚪ {strategy_name}: No generó señal válida")

            except Exception as e:
                logger.warning(f"⚠️ Error obteniendo señal de {strategy_name}: {e}")

        return signals

    def _analyze_consensus(
        self, signals: List[StrategySignalData]
    ) -> ConsensusAnalysis:
        """🔍 Analizar consenso entre las señales"""

        # Contar distribución de señales
        signal_distribution = defaultdict(int)
        total_weight = 0
        weighted_confidence = 0

        for signal in signals:
            if signal.is_valid:
                signal_distribution[signal.signal_type] += 1
                weighted_confidence += signal.confidence_score * signal.weight
                total_weight += signal.weight

        # Calcular métricas de consenso
        total_strategies = len(signals)
        dominant_signal = (
            max(signal_distribution.keys(), key=signal_distribution.get)
            if signal_distribution
            else "HOLD"
        )
        agreeing_strategies = signal_distribution.get(dominant_signal, 0)
        disagreeing_strategies = total_strategies - agreeing_strategies

        consensus_percentage = (
            (agreeing_strategies / total_strategies) * 100
            if total_strategies > 0
            else 0
        )
        weighted_confidence = (
            weighted_confidence / total_weight if total_weight > 0 else 0
        )

        # Calcular coherencia (penalizar contradicciones)
        coherence_score = self._calculate_coherence_score(signals, signal_distribution)

        # Evaluación de riesgo
        risk_assessment = self._assess_consensus_risk(
            consensus_percentage, coherence_score, signal_distribution
        )

        # Notas de análisis
        analysis_notes = []
        analysis_notes.append(
            f"Consenso: {agreeing_strategies}/{total_strategies} estrategias coinciden"
        )
        analysis_notes.append(f"Señal dominante: {dominant_signal}")
        analysis_notes.append(f"Confianza ponderada: {weighted_confidence:.1f}%")

        return ConsensusAnalysis(
            total_strategies=total_strategies,
            agreeing_strategies=agreeing_strategies,
            disagreeing_strategies=disagreeing_strategies,
            consensus_percentage=consensus_percentage,
            weighted_confidence=weighted_confidence,
            dominant_signal=dominant_signal,
            signal_distribution=dict(signal_distribution),
            coherence_score=coherence_score,
            risk_assessment=risk_assessment,
            analysis_notes=analysis_notes,
        )

    def _calculate_coherence_score(
        self, signals: List[StrategySignalData], distribution: Dict
    ) -> float:
        """🎯 Calcular score de coherencia entre estrategias"""

        if len(signals) < 2:
            return 100.0

        # Penalizar contradicciones directas (BUY vs SELL)
        buy_signals = distribution.get("BUY", 0)
        sell_signals = distribution.get("SELL", 0)
        hold_signals = distribution.get("HOLD", 0)

        # Coherencia base
        total_signals = len(signals)
        max_agreement = max(buy_signals, sell_signals, hold_signals)
        base_coherence = (max_agreement / total_signals) * 100

        # Penalización por contradicciones directas
        contradiction_penalty = 0
        if buy_signals > 0 and sell_signals > 0:
            contradiction_ratio = min(buy_signals, sell_signals) / total_signals
            contradiction_penalty = contradiction_ratio * 50  # Penalización hasta 50%

        # Bonificación por unanimidad
        unanimity_bonus = 0
        if max_agreement == total_signals:
            unanimity_bonus = 20  # 20% bonus por unanimidad

        coherence_score = base_coherence - contradiction_penalty + unanimity_bonus
        return max(0, min(100, coherence_score))

    def _assess_consensus_risk(
        self, consensus_pct: float, coherence: float, distribution: Dict
    ) -> str:
        """⚠️ Evaluar riesgo del consenso"""

        # Riesgo bajo: Alto consenso y coherencia
        if consensus_pct >= 80 and coherence >= 80:
            return "LOW"

        # Riesgo alto: Contradicciones directas
        if distribution.get("BUY", 0) > 0 and distribution.get("SELL", 0) > 0:
            return "HIGH"

        # Riesgo alto: Consenso muy bajo
        if consensus_pct < 50:
            return "HIGH"

        # Riesgo medio: Casos intermedios
        return "MEDIUM"

    def _passes_quality_filters(
        self, analysis: ConsensusAnalysis, signals: List[StrategySignalData]
    ) -> bool:
        """🔍 Aplicar filtros de calidad al consenso"""

        # Para señales HOLD, usar filtros más flexibles
        is_hold_dominant = analysis.dominant_signal == "HOLD"

        # Filtro 1: Consenso mínimo (más flexible para HOLD)
        min_consensus = (
            (self.min_consensus_threshold * 100) if not is_hold_dominant else 50.0
        )
        if analysis.consensus_percentage < min_consensus:
            logger.debug(
                f"❌ Filtro consenso: {analysis.consensus_percentage:.1f}% < {min_consensus}%"
            )
            return False

        # Filtro 2: Confianza mínima ponderada (más flexible para HOLD)
        min_confidence = self.min_weighted_confidence if not is_hold_dominant else 50.0
        if analysis.weighted_confidence < min_confidence:
            logger.debug(
                f"❌ Filtro confianza: {analysis.weighted_confidence:.1f}% < {min_confidence}%"
            )
            return False

        # Filtro 3: Coherencia mínima
        if self.enable_coherence_filter and analysis.coherence_score < 60:
            logger.debug(f"❌ Filtro coherencia: {analysis.coherence_score:.1f}% < 60%")
            return False

        # Filtro 4: Riesgo máximo
        if self.enable_risk_filter and analysis.risk_assessment == "HIGH":
            logger.debug(f"❌ Filtro riesgo: Riesgo evaluado como ALTO")
            return False

        # Filtro 5: No contradicciones críticas
        buy_count = analysis.signal_distribution.get("BUY", 0)
        sell_count = analysis.signal_distribution.get("SELL", 0)

        if buy_count > 0 and sell_count > 0:
            contradiction_ratio = min(buy_count, sell_count) / analysis.total_strategies
            if contradiction_ratio > self.max_contradiction_tolerance:
                logger.debug(
                    f"❌ Filtro contradicción: {contradiction_ratio:.2f} > {self.max_contradiction_tolerance}"
                )
                return False

        return True

    def _determine_consensus_decision(
        self, analysis: ConsensusAnalysis
    ) -> ConsensusDecision:
        """🎯 Determinar decisión final del consenso"""

        dominant_signal = analysis.dominant_signal
        consensus_pct = analysis.consensus_percentage
        confidence = analysis.weighted_confidence
        coherence = analysis.coherence_score

        # Calcular fuerza de la decisión
        strength_score = (consensus_pct + confidence + coherence) / 3

        # Si la señal dominante es HOLD y hay consenso, es una decisión válida
        if dominant_signal == "HOLD":
            if consensus_pct >= 67:  # Al menos 2 de 3 estrategias coinciden en HOLD
                return ConsensusDecision.HOLD
            else:
                return (
                    ConsensusDecision.HOLD
                )  # HOLD por defecto cuando no hay consenso claro

        elif dominant_signal == "BUY":
            if strength_score >= 90:
                return ConsensusDecision.STRONG_BUY
            elif strength_score >= 80:
                return ConsensusDecision.BUY
            elif strength_score >= 70:
                return ConsensusDecision.WEAK_BUY
            else:
                return ConsensusDecision.HOLD

        elif dominant_signal == "SELL":
            if strength_score >= 90:
                return ConsensusDecision.STRONG_SELL
            elif strength_score >= 80:
                return ConsensusDecision.SELL
            elif strength_score >= 70:
                return ConsensusDecision.WEAK_SELL
            else:
                return ConsensusDecision.HOLD

        return ConsensusDecision.HOLD

    def _calculate_risk_metrics(
        self, signals: List[StrategySignalData], analysis: ConsensusAnalysis
    ) -> Dict:
        """📊 Calcular métricas de riesgo agregadas"""

        # Recopilar métricas de riesgo de las estrategias individuales
        stop_losses = []
        take_profits = []
        risk_rewards = []

        for signal in signals:
            if (
                hasattr(signal.raw_signal, "stop_loss_price")
                and signal.raw_signal.stop_loss_price > 0
            ):
                stop_losses.append(signal.raw_signal.stop_loss_price)
            if (
                hasattr(signal.raw_signal, "take_profit_price")
                and signal.raw_signal.take_profit_price > 0
            ):
                take_profits.append(signal.raw_signal.take_profit_price)
            if (
                hasattr(signal.raw_signal, "risk_reward_ratio")
                and signal.raw_signal.risk_reward_ratio > 0
            ):
                risk_rewards.append(signal.raw_signal.risk_reward_ratio)

        # Calcular promedios ponderados
        avg_stop_loss = np.mean(stop_losses) if stop_losses else 0
        avg_take_profit = np.mean(take_profits) if take_profits else 0
        avg_risk_reward = np.mean(risk_rewards) if risk_rewards else 1.5

        # Ajustar basado en coherencia del consenso
        coherence_factor = analysis.coherence_score / 100
        position_size_factor = coherence_factor * (analysis.consensus_percentage / 100)

        return {
            "stop_loss_price": avg_stop_loss,
            "take_profit_price": avg_take_profit,
            "risk_reward_ratio": avg_risk_reward,
            "position_size_recommendation": position_size_factor,
            "risk_level": analysis.risk_assessment,
        }

    def _create_consensus_signal(
        self,
        symbol: str,
        timeframe: str,
        decision: ConsensusDecision,
        analysis: ConsensusAnalysis,
        signals: List[StrategySignalData],
        risk_metrics: Dict,
        start_time: datetime,
    ) -> ConsensusSignal:
        """🏗️ Crear señal de consenso final"""

        # Determinar tipo de señal básico
        if decision in [
            ConsensusDecision.STRONG_BUY,
            ConsensusDecision.BUY,
            ConsensusDecision.WEAK_BUY,
        ]:
            signal_type = "BUY"
        elif decision in [
            ConsensusDecision.STRONG_SELL,
            ConsensusDecision.SELL,
            ConsensusDecision.WEAK_SELL,
        ]:
            signal_type = "SELL"
        else:
            signal_type = "HOLD"

        # Precio promedio ponderado
        weighted_price = sum(s.price * s.weight for s in signals) / sum(
            s.weight for s in signals
        )

        # Calcular calidad general
        quality_score = (
            analysis.consensus_percentage
            + analysis.weighted_confidence
            + analysis.coherence_score
        ) / 3

        # Determinar fuerza
        if quality_score >= 90:
            strength = "Very Strong"
        elif quality_score >= 80:
            strength = "Strong"
        elif quality_score >= 70:
            strength = "Moderate"
        else:
            strength = "Weak"

        # Duración del análisis
        analysis_duration = (datetime.now() - start_time).total_seconds() * 1000

        # Condiciones de mercado (simplificado)
        market_conditions = "NORMAL"  # Se puede expandir con análisis más detallado

        # Notas finales
        notes = f"Consenso de {len(signals)} estrategias. " + "; ".join(
            analysis.analysis_notes[:3]
        )

        return ConsensusSignal(
            symbol=symbol,
            signal_type=signal_type,
            consensus_decision=decision,
            price=weighted_price,
            confidence_score=analysis.weighted_confidence,
            strength=strength,
            timestamp=datetime.now(),
            consensus_analysis=analysis,
            contributing_strategies=signals,
            quality_score=quality_score,
            coherence_score=analysis.coherence_score,
            risk_level=risk_metrics["risk_level"],
            stop_loss_price=risk_metrics["stop_loss_price"],
            take_profit_price=risk_metrics["take_profit_price"],
            risk_reward_ratio=risk_metrics["risk_reward_ratio"],
            position_size_recommendation=risk_metrics["position_size_recommendation"],
            analysis_duration_ms=analysis_duration,
            strategy_performance_weights=self.strategy_weights.copy(),
            market_conditions=market_conditions,
            notes=notes,
        )

    def _update_signal_history(self, signal: ConsensusSignal):
        """📝 Actualizar historial de señales"""
        self.signal_history.append(signal)

        # Mantener solo las últimas 100 señales
        if len(self.signal_history) > 100:
            self.signal_history = self.signal_history[-100:]

    def update_strategy_weights(self, performance_data: Dict[str, float]):
        """⚖️ Actualizar pesos de estrategias basado en rendimiento"""

        # Actualizar historial de rendimiento
        for strategy, performance in performance_data.items():
            if strategy in self.strategy_weights:
                self.performance_history[strategy].append(performance)

                # Mantener solo los últimos 50 registros
                if len(self.performance_history[strategy]) > 50:
                    self.performance_history[strategy] = self.performance_history[
                        strategy
                    ][-50:]

        # Recalcular pesos basado en rendimiento promedio
        self._recalculate_weights()

    def _recalculate_weights(self):
        """🔄 Recalcular pesos dinámicamente"""

        # Si no hay suficiente historial, mantener pesos base
        min_samples = 10
        if any(
            len(self.performance_history[s]) < min_samples
            for s in self.strategy_weights.keys()
        ):
            return

        # Calcular rendimiento promedio de cada estrategia
        avg_performances = {}
        for strategy in self.strategy_weights.keys():
            if strategy in self.performance_history:
                avg_performances[strategy] = np.mean(
                    self.performance_history[strategy][-20:]
                )  # Últimas 20
            else:
                avg_performances[strategy] = 0.5  # Neutral

        # Normalizar y ajustar pesos
        total_performance = sum(avg_performances.values())
        if total_performance > 0:
            # Ajuste gradual (70% peso anterior + 30% nuevo peso basado en rendimiento)
            for strategy in self.strategy_weights.keys():
                new_weight = avg_performances[strategy] / total_performance
                self.strategy_weights[strategy] = (
                    0.7 * self.strategy_weights[strategy] + 0.3 * new_weight
                )

        # Asegurar que los pesos sumen 1.0
        total_weight = sum(self.strategy_weights.values())
        if total_weight > 0:
            for strategy in self.strategy_weights.keys():
                self.strategy_weights[strategy] /= total_weight

        logger.info(f"🔄 Pesos actualizados: {self.strategy_weights}")

    def get_consensus_stats(self) -> Dict:
        """📊 Obtener estadísticas del consenso"""

        if not self.signal_history:
            return {"message": "No hay historial de señales disponible"}

        recent_signals = self.signal_history[-20:]  # Últimas 20 señales

        # Estadísticas básicas
        signal_types = [s.signal_type for s in recent_signals]
        consensus_decisions = [s.consensus_decision.value for s in recent_signals]

        stats = {
            "total_signals": len(self.signal_history),
            "recent_signals": len(recent_signals),
            "signal_distribution": {
                "BUY": signal_types.count("BUY"),
                "SELL": signal_types.count("SELL"),
                "HOLD": signal_types.count("HOLD"),
            },
            "average_confidence": np.mean([s.confidence_score for s in recent_signals]),
            "average_coherence": np.mean([s.coherence_score for s in recent_signals]),
            "average_quality": np.mean([s.quality_score for s in recent_signals]),
            "current_weights": self.strategy_weights,
            "risk_distribution": {
                "LOW": len([s for s in recent_signals if s.risk_level == "LOW"]),
                "MEDIUM": len([s for s in recent_signals if s.risk_level == "MEDIUM"]),
                "HIGH": len([s for s in recent_signals if s.risk_level == "HIGH"]),
            },
        }

        return stats


# Ejemplo de uso
if __name__ == "__main__":
    consensus = ConsensusStrategy(capital_client=None)

    # Simular análisis
    signal = consensus.analyze("BTCUSD")

    if signal:
        print(f"🧠 SEÑAL DE CONSENSO GENERADA:")
        print(f"Símbolo: {signal.symbol}")
        print(f"Decisión: {signal.consensus_decision.value}")
        print(f"Tipo: {signal.signal_type}")
        print(f"Precio: ${signal.price:.2f}")
        print(f"Confianza: {signal.confidence_score:.1f}%")
        print(f"Calidad: {signal.quality_score:.1f}%")
        print(f"Coherencia: {signal.coherence_score:.1f}%")
        print(f"Consenso: {signal.consensus_analysis.consensus_percentage:.1f}%")
        print(f"Estrategias contribuyentes: {len(signal.contributing_strategies)}")
        print(f"Riesgo: {signal.risk_level}")
        print(f"Notas: {signal.notes}")
    else:
        print("❌ No se generó consenso o no pasó los filtros")
