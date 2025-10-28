"""
🧠 CONSENSUS STRATEGY ADAPTER
Adaptador para la estrategia de consenso que coordina múltiples estrategias

FUNCIONALIDAD:
• Adapta ConsensusStrategy al formato esperado por TradingBot
• Convierte ConsensusSignal a TradingSignal estándar
• Mantiene compatibilidad con el sistema existente
• Proporciona métricas adicionales del consenso
"""

import logging
from datetime import datetime
from typing import Optional

from .enhanced_strategies import TradingSignal
from .consensus_strategy import ConsensusStrategy, ConsensusDecision

logger = logging.getLogger(__name__)


class ConsensusAdapter:
    """🧠 Adaptador para la estrategia de consenso"""

    def __init__(self, capital_client=None):
        """
        Inicializar adaptador de consenso

        Args:
            capital_client: Cliente de Capital.com (opcional, para compatibilidad)
        """
        self.name = "ConsensusStrategy"
        self.capital_client = capital_client
        self.consensus_strategy = ConsensusStrategy(capital_client)
        self.trading_bot = None

        logger.info("🧠 ConsensusAdapter inicializado")

    def set_trading_bot(self, bot):
        """Asignar referencia al TradingBot"""
        self.trading_bot = bot
        logger.debug("🔗 TradingBot referencia asignada al ConsensusAdapter")

    def analyze(self, symbol: str, timeframe: str = "1h") -> Optional[TradingSignal]:
        """
        🎯 Analizar símbolo usando consenso de estrategias

        Args:
            symbol: Símbolo a analizar
            timeframe: Marco temporal

        Returns:
            TradingSignal o None si no hay consenso
        """
        try:
            logger.debug(f"🧠 Analizando {symbol} con estrategia de consenso")

            # Obtener señal de consenso
            consensus_signal = self.consensus_strategy.analyze(symbol, timeframe)

            if not consensus_signal:
                logger.debug(f"⚪ No se generó consenso para {symbol}")
                return (
                    None  # Retornar None en lugar de crear señal HOLD con 0% confianza
                )

            # Convertir ConsensusSignal a TradingSignal estándar
            trading_signal = self._convert_to_trading_signal(consensus_signal)

            logger.info(
                f"✅ Consenso generado para {symbol}: {trading_signal.signal_type} "
                f"(Confianza: {trading_signal.confidence_score:.1f}%, "
                f"Decisión: {consensus_signal.consensus_decision.value})"
            )

            return trading_signal

        except Exception as e:
            logger.error(f"❌ Error en análisis de consenso para {symbol}: {e}")
            return None  # Retornar None en lugar de crear señal HOLD con 0% confianza

    def _convert_to_trading_signal(self, consensus_signal) -> TradingSignal:
        """
        🔄 Convertir ConsensusSignal a TradingSignal estándar

        Args:
            consensus_signal: Señal de consenso original

        Returns:
            TradingSignal compatible con TradingBot
        """

        # Mapear decisión de consenso a tipo de señal
        signal_type = consensus_signal.signal_type

        # Calcular confianza ajustada basada en la calidad del consenso
        # Combinar confianza ponderada con calidad y coherencia
        adjusted_confidence = (
            consensus_signal.confidence_score * 0.6  # 60% confianza ponderada
            + consensus_signal.quality_score * 0.25  # 25% calidad general
            + consensus_signal.coherence_score * 0.15  # 15% coherencia
        )

        # Asegurar que esté en rango 0-100
        adjusted_confidence = max(0, min(100, adjusted_confidence))

        # Determinar strength basado en la decisión de consenso
        strength_mapping = {
            "STRONG_BUY": "Very Strong",
            "BUY": "Strong",
            "WEAK_BUY": "Moderate",
            "HOLD": "Weak",
            "WEAK_SELL": "Moderate",
            "SELL": "Strong",
            "STRONG_SELL": "Very Strong",
        }
        strength = strength_mapping.get(
            consensus_signal.consensus_decision.value, "Moderate"
        )

        # Crear señal de trading estándar
        trading_signal = TradingSignal(
            symbol=consensus_signal.symbol,
            signal_type=signal_type,
            confidence_score=adjusted_confidence,
            strength=strength,
            price=consensus_signal.price,
            timestamp=consensus_signal.timestamp,
            strategy_name="ConsensusStrategy",
        )

        # Agregar datos específicos del consenso como atributos adicionales
        trading_signal.consensus_decision = consensus_signal.consensus_decision.value
        trading_signal.consensus_percentage = (
            consensus_signal.consensus_analysis.consensus_percentage
        )
        trading_signal.coherence_score = consensus_signal.coherence_score
        trading_signal.quality_score = consensus_signal.quality_score
        trading_signal.risk_level = consensus_signal.risk_level
        trading_signal.contributing_strategies_count = len(
            consensus_signal.contributing_strategies
        )
        trading_signal.analysis_duration_ms = consensus_signal.analysis_duration_ms

        # Métricas de riesgo del consenso
        trading_signal.stop_loss_price = consensus_signal.stop_loss_price
        trading_signal.take_profit_price = consensus_signal.take_profit_price
        trading_signal.risk_reward_ratio = consensus_signal.risk_reward_ratio
        trading_signal.position_size_recommendation = (
            consensus_signal.position_size_recommendation
        )

        # Información de estrategias contribuyentes
        contributing_strategies = []
        for strategy_signal in consensus_signal.contributing_strategies:
            contributing_strategies.append(
                {
                    "name": strategy_signal.strategy_name,
                    "signal": strategy_signal.signal_type,
                    "confidence": strategy_signal.confidence_score,
                    "weight": strategy_signal.weight,
                }
            )
        trading_signal.contributing_strategies = contributing_strategies

        # Notas del consenso
        trading_signal.consensus_notes = consensus_signal.notes

        return trading_signal

    def _create_hold_signal(self, symbol: str, timeframe: str) -> TradingSignal:
        """
        ⏸️ Crear señal HOLD cuando no hay consenso

        Args:
            symbol: Símbolo analizado
            timeframe: Marco temporal

        Returns:
            TradingSignal con tipo HOLD
        """
        return TradingSignal(
            symbol=symbol,
            signal_type="HOLD",
            confidence_score=0.0,
            strength="Weak",
            price=0.0,
            timestamp=datetime.now(),
            strategy_name="ConsensusStrategy",
        )

    def get_consensus_stats(self) -> dict:
        """
        📊 Obtener estadísticas del consenso

        Returns:
            Diccionario con estadísticas del consenso
        """
        return self.consensus_strategy.get_consensus_stats()

    def update_strategy_weights(self, performance_data: dict):
        """
        ⚖️ Actualizar pesos de estrategias basado en rendimiento

        Args:
            performance_data: Datos de rendimiento por estrategia

        Returns:
            Diccionario con el resultado de la actualización
        """
        try:
            self.consensus_strategy.update_strategy_weights(performance_data)
            logger.info("⚖️ Pesos de estrategias actualizados en ConsensusAdapter")

            # Obtener los pesos actualizados
            updated_weights = self.get_strategy_weights()

            return {
                "success": True,
                "updated_weights": updated_weights,
                "message": "Strategy weights updated successfully",
            }
        except Exception as e:
            logger.error(f"❌ Error updating strategy weights: {e}")
            return {"success": False, "error": str(e)}

    def get_strategy_weights(self) -> dict:
        """
        📊 Obtener pesos actuales de las estrategias

        Returns:
            Diccionario con pesos de cada estrategia
        """
        return self.consensus_strategy.strategy_weights.copy()

    def get_last_consensus_analysis(self) -> dict:
        """
        🔍 Obtener detalles del último análisis de consenso

        Returns:
            Diccionario con detalles del último consenso
        """
        if not self.consensus_strategy.signal_history:
            return {"message": "No hay historial de consenso disponible"}

        last_signal = self.consensus_strategy.signal_history[-1]

        return {
            "symbol": last_signal.symbol,
            "decision": last_signal.consensus_decision.value,
            "signal_type": last_signal.signal_type,
            "confidence": last_signal.confidence_score,
            "quality": last_signal.quality_score,
            "coherence": last_signal.coherence_score,
            "consensus_percentage": last_signal.consensus_analysis.consensus_percentage,
            "contributing_strategies": len(last_signal.contributing_strategies),
            "risk_level": last_signal.risk_level,
            "timestamp": last_signal.timestamp.isoformat(),
            "analysis_duration_ms": last_signal.analysis_duration_ms,
            "strategy_weights": last_signal.strategy_performance_weights,
            "notes": last_signal.notes,
        }


# Función de utilidad para crear el adaptador
def create_consensus_adapter(capital_client=None) -> ConsensusAdapter:
    """
    🏭 Factory function para crear ConsensusAdapter

    Args:
        capital_client: Cliente de Capital.com (opcional)

    Returns:
        ConsensusAdapter configurado
    """
    return ConsensusAdapter(capital_client)


# Ejemplo de uso
if __name__ == "__main__":
    # Crear adaptador
    adapter = create_consensus_adapter()

    # Simular análisis
    signal = adapter.analyze("BTCUSD")

    if signal and signal.signal_type != "HOLD":
        print(f"🧠 SEÑAL DE CONSENSO:")
        print(f"Símbolo: {signal.symbol}")
        print(f"Tipo: {signal.signal_type}")
        print(f"Confianza: {signal.confidence_score:.1f}%")
        print(f"Precio: ${signal.price:.2f}")
        print(f"Decisión: {getattr(signal, 'consensus_decision', 'N/A')}")
        print(f"Consenso: {getattr(signal, 'consensus_percentage', 0):.1f}%")
        print(f"Coherencia: {getattr(signal, 'coherence_score', 0):.1f}%")
        print(f"Estrategias: {getattr(signal, 'contributing_strategies_count', 0)}")
    else:
        print("❌ No se generó señal de consenso válida")
