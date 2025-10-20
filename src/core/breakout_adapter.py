"""
💥 BREAKOUT PROFESSIONAL ADAPTER
Adaptador para integrar la estrategia Breakout Professional con el sistema de trading
"""

import logging
from datetime import datetime
from typing import Optional
from src.core.breakout_professional import BreakoutProfessional, BreakoutSignal, BreakoutDirection
from src.core.enhanced_strategies import EnhancedSignal, TradingStrategy
from src.config.main_config import StrategyConfig, TradingBotConfig

logger = logging.getLogger(__name__)

class BreakoutAdapter(TradingStrategy):
    """
    Adaptador para la estrategia Breakout Professional
    Convierte las señales específicas a EnhancedSignal para el sistema
    """
    
    def __init__(self, capital_client):
        """
        Inicializar el adaptador Breakout
        
        Args:
            capital_client: Cliente de Capital.com para obtener datos
        """
        super().__init__(capital_client)
        self.strategy = BreakoutProfessional()
        self.name = "BreakoutProfessional"
        
        # Inyectar el método get_market_data de la clase padre en la estrategia
        self.strategy.get_market_data = self.get_market_data
        
        # Exponer min_confidence desde la configuración centralizada
        self.min_confidence = TradingBotConfig.get_min_confidence_threshold()
        
        logger.info(f"✅ {self.name} adapter inicializado")
    

    
    def _create_hold_signal(self, symbol: str, price: float, reason: str = "No conditions met") -> EnhancedSignal:
        """
        Crear una señal HOLD por defecto
        """
        return EnhancedSignal(
            symbol=symbol,
            signal_type="HOLD",
            price=price,
            confidence_score=50.0,
            strength="Weak",
            strategy_name=self.name,
            timestamp=datetime.now(),
            trend_confirmation="NEUTRAL",
            volume_confirmation=False,
            confluence_score=25,
            notes=f"Breakout: {reason}",
            risk_reward_ratio=0.0,
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            timeframe="1h",
            indicators_data={}
        )
    
    def _convert_to_enhanced_signal(self, breakout_signal: BreakoutSignal) -> EnhancedSignal:
        """
        Convertir BreakoutSignal a EnhancedSignal
        """
        try:
            # Mapear el tipo de señal
            signal_type = breakout_signal.signal_type
            
            # Calcular confluence score basado en los componentes
            confluence_score = 50.0  # Base
            
            # Pattern strength contribution
            confluence_score += breakout_signal.consolidation.strength * 0.2
            
            # ADX contribution
            if breakout_signal.adx_value >= 25:
                confluence_score += 15
            elif breakout_signal.adx_value >= 20:
                confluence_score += 10
            
            # Volume expansion contribution
            if breakout_signal.volume_expansion >= 2.0:
                confluence_score += 15
            elif breakout_signal.volume_expansion >= 1.5:
                confluence_score += 10
            
            # Trend alignment contribution
            if breakout_signal.trend_alignment:
                confluence_score += 15
            
            # Breakout direction contribution
            if breakout_signal.breakout.direction != BreakoutDirection.NONE:
                confluence_score += 10
                
                # Retest confirmation bonus
                if breakout_signal.breakout.retest_confirmed:
                    confluence_score += 10
            
            # Risk factors (reduce confluence)
            if breakout_signal.breakout.false_breakout_risk > 50:
                confluence_score -= 10
            
            if not breakout_signal.volume_confirmation:
                confluence_score -= 15
            
            # Limit confluence score
            confluence_score = max(min(confluence_score, 100.0), 0.0)
            
            # Determinar confirmaciones
            trend_confirmation = (breakout_signal.trend_alignment and 
                                breakout_signal.breakout.direction != BreakoutDirection.NONE)
            
            volume_confirmation = breakout_signal.volume_confirmation
            
            # Crear notas detalladas
            notes_parts = [
                f"Pattern: {breakout_signal.consolidation.pattern.value}",
                f"Duration: {breakout_signal.consolidation.duration}p",
                f"Breakout: {breakout_signal.breakout.direction.value}",
                f"ADX: {breakout_signal.adx_value:.1f}",
                f"Volume: {breakout_signal.volume_expansion:.1f}x",
                f"Range: {breakout_signal.consolidation.range_size:.1%}"
            ]
            
            if breakout_signal.breakout.retest_confirmed:
                notes_parts.append("Retest OK")
            
            if breakout_signal.breakout.false_breakout_risk > 50:
                notes_parts.append(f"False BO Risk: {breakout_signal.breakout.false_breakout_risk:.0f}%")
            
            if breakout_signal.analysis_notes:
                notes_parts.append(breakout_signal.analysis_notes)
            
            notes = " | ".join(notes_parts)
            
            return EnhancedSignal(
                symbol=breakout_signal.symbol,
                signal_type=signal_type,
                price=breakout_signal.price,
                confidence_score=breakout_signal.confidence_score,
                strength=breakout_signal.strength,
                strategy_name=self.name,
                timestamp=breakout_signal.timestamp,
                trend_confirmation="BULLISH" if trend_confirmation else "NEUTRAL",
                volume_confirmation=volume_confirmation,
                confluence_score=int(confluence_score),
                notes=notes,
                risk_reward_ratio=breakout_signal.risk_reward_ratio,
                stop_loss_price=breakout_signal.stop_loss_price,
                take_profit_price=breakout_signal.measured_move_target,
                market_regime="TRENDING",
                timeframe="1h",
                indicators_data={
                    "adx": breakout_signal.adx_value,
                    "volume_expansion": breakout_signal.volume_expansion,
                    "consolidation": {
                        "range_size": breakout_signal.consolidation.range_size,
                        "duration": breakout_signal.consolidation.duration,
                        "support_level": breakout_signal.consolidation.support_level,
                        "resistance_level": breakout_signal.consolidation.resistance_level
                    },
                    "breakout": {
                        "direction": breakout_signal.breakout.direction.value,
                        "strength": breakout_signal.breakout.momentum_strength,
                        "retest_confirmed": breakout_signal.breakout.retest_confirmed,
                        "false_breakout_risk": breakout_signal.breakout.false_breakout_risk
                    }
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo señal Breakout: {e}")
            return self._create_hold_signal(
                breakout_signal.symbol, 
                breakout_signal.price, 
                f"Error en conversión: {str(e)}"
            )
    
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """
        Ejecutar análisis de Breakout y devolver EnhancedSignal
        
        Args:
            symbol: Símbolo a analizar (ej: "SOLUSD")
            timeframe: Marco temporal (ej: "1h", "4h", "1d")
            
        Returns:
            EnhancedSignal con el resultado del análisis
        """
        try:
            logger.info(f"💥 Analizando {symbol} con Breakout Professional ({timeframe})")
            
            # Ejecutar análisis de la estrategia
            breakout_signal = self.strategy.analyze(symbol, timeframe)
            
            if breakout_signal is None:
                logger.warning(f"⚠️ No se pudo generar señal Breakout para {symbol}")
                # Intentar obtener precio actual para señal HOLD
                try:
                    data = self._get_market_data(symbol, timeframe, 1)
                    current_price = data['close'].iloc[-1] if data is not None and not data.empty else 0.0
                except:
                    current_price = 0.0
                
                return self._create_hold_signal(symbol, current_price, "Análisis falló")
            
            # Convertir a EnhancedSignal
            enhanced_signal = self._convert_to_enhanced_signal(breakout_signal)
            
            logger.info(f"✅ Señal Breakout generada para {symbol}: "
                       f"{enhanced_signal.signal_type} (Confianza: {enhanced_signal.confidence_score:.1f}%)")
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"❌ Error en análisis Breakout para {symbol}: {e}")
            
            # Crear señal HOLD de emergencia
            try:
                data = self._get_market_data(symbol, timeframe, 1)
                current_price = data['close'].iloc[-1] if data is not None and not data.empty else 0.0
            except:
                current_price = 0.0
            
            return self._create_hold_signal(symbol, current_price, f"Error: {str(e)}")

# Ejemplo de uso
if __name__ == "__main__":
    # Este código se ejecutaría solo si se ejecuta directamente el archivo
    print("💥 Breakout Professional Adapter")
    print("Este adaptador integra la estrategia Breakout con el sistema de trading")
    print("Uso: Instanciar con un capital_client y llamar analyze(symbol, timeframe)")