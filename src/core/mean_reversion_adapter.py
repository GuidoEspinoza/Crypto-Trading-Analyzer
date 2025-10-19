"""
🔄 MEAN REVERSION PROFESSIONAL ADAPTER
Adaptador para integrar la estrategia Mean Reversion Professional con el sistema de trading
"""

import logging
from datetime import datetime
from typing import Optional
from src.core.mean_reversion_professional import MeanReversionProfessional, MeanReversionSignal
from src.core.enhanced_strategies import EnhancedSignal, TradingStrategy

logger = logging.getLogger(__name__)

class MeanReversionAdapter(TradingStrategy):
    """
    Adaptador para la estrategia Mean Reversion Professional
    Convierte las señales específicas a EnhancedSignal para el sistema
    """
    
    def __init__(self, capital_client):
        """
        Inicializar el adaptador
        
        Args:
            capital_client: Cliente de Capital.com para obtener datos
        """
        super().__init__(capital_client)
        self.strategy = MeanReversionProfessional()
        self.name = "MeanReversionProfessional"
        
        # Inyectar el método get_market_data de la clase padre en la estrategia
        self.strategy.get_market_data = self.get_market_data
        
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
            notes=f"Mean Reversion: {reason}",
            risk_reward_ratio=0.0,
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            timeframe="1h",
            indicators_data={}
        )
    
    def _convert_to_enhanced_signal(self, mr_signal: MeanReversionSignal) -> EnhancedSignal:
        """
        Convertir MeanReversionSignal a EnhancedSignal
        """
        try:
            # Mapear el tipo de señal
            signal_type = mr_signal.signal_type
            
            # Calcular confluence score basado en los componentes
            confluence_score = 50.0  # Base
            
            # RSI contribution
            if mr_signal.signal_type == "BUY" and mr_signal.rsi_value < 30:
                confluence_score += 15
            elif mr_signal.signal_type == "SELL" and mr_signal.rsi_value > 70:
                confluence_score += 15
            
            # Stochastic contribution
            if mr_signal.signal_type == "BUY" and mr_signal.stochastic_k < 20:
                confluence_score += 10
            elif mr_signal.signal_type == "SELL" and mr_signal.stochastic_k > 80:
                confluence_score += 10
            
            # Bollinger Bands contribution
            if mr_signal.signal_type == "BUY" and mr_signal.bb_position < -0.8:
                confluence_score += 10
            elif mr_signal.signal_type == "SELL" and mr_signal.bb_position > 0.8:
                confluence_score += 10
            
            # Divergence contribution
            if mr_signal.divergence.confidence > 70:
                confluence_score += 15
            
            # Limit confluence score
            confluence_score = min(confluence_score, 100.0)
            
            # Determinar confirmaciones
            trend_confirmation = (mr_signal.market_regime.value == "RANGING" and 
                                mr_signal.divergence.confidence > 50)
            
            volume_confirmation = mr_signal.volume_confirmation
            
            # Crear notas detalladas
            notes_parts = [
                f"RSI: {mr_signal.rsi_value:.1f}",
                f"Stoch: {mr_signal.stochastic_k:.1f}/{mr_signal.stochastic_d:.1f}",
                f"BB Pos: {mr_signal.bb_position:.2f}",
                f"Divergence: {mr_signal.divergence.type.value}",
                f"Regime: {mr_signal.market_regime.value}",
                f"Near Level: {mr_signal.distance_to_level:.1%}"
            ]
            
            if mr_signal.analysis_notes:
                notes_parts.append(mr_signal.analysis_notes)
            
            notes = " | ".join(notes_parts)
            
            return EnhancedSignal(
                symbol=mr_signal.symbol,
                signal_type=signal_type,
                price=mr_signal.price,
                confidence_score=mr_signal.confidence_score,
                strength=mr_signal.strength,
                strategy_name=self.name,
                timestamp=mr_signal.timestamp,
                trend_confirmation="BULLISH" if trend_confirmation else "NEUTRAL",
                volume_confirmation=volume_confirmation,
                confluence_score=int(confluence_score),
                notes=notes,
                risk_reward_ratio=mr_signal.risk_reward_ratio,
                stop_loss_price=mr_signal.stop_loss_price,
                take_profit_price=mr_signal.take_profit_price,
                market_regime=mr_signal.market_regime.value,
                timeframe="1h",
                indicators_data={
                    "rsi": mr_signal.rsi_value,
                    "stochastic_k": mr_signal.stochastic_k,
                    "stochastic_d": mr_signal.stochastic_d,
                    "bb_position": mr_signal.bb_position,
                    "divergence": {
                        "type": mr_signal.divergence.type.value,
                        "confidence": mr_signal.divergence.confidence
                    },
                    "market_regime": mr_signal.market_regime.value,
                    "distance_to_level": mr_signal.distance_to_level
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Error convirtiendo señal Mean Reversion: {e}")
            return self._create_hold_signal(
                mr_signal.symbol, 
                mr_signal.price, 
                f"Error en conversión: {str(e)}"
            )
    
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """
        Ejecutar análisis de Mean Reversion y devolver EnhancedSignal
        
        Args:
            symbol: Símbolo a analizar (ej: "SOLUSD")
            timeframe: Marco temporal (ej: "1h", "4h", "1d")
            
        Returns:
            EnhancedSignal con el resultado del análisis
        """
        try:
            logger.info(f"🔄 Analizando {symbol} con Mean Reversion Professional ({timeframe})")
            
            # Ejecutar análisis de la estrategia
            mr_signal = self.strategy.analyze(symbol, timeframe)
            
            if mr_signal is None:
                logger.warning(f"⚠️ No se pudo generar señal Mean Reversion para {symbol}")
                # Intentar obtener precio actual para señal HOLD
                try:
                    data = self._get_market_data(symbol, timeframe, 1)
                    current_price = data['close'].iloc[-1] if data is not None and not data.empty else 0.0
                except:
                    current_price = 0.0
                
                return self._create_hold_signal(symbol, current_price, "Análisis falló")
            
            # Convertir a EnhancedSignal
            enhanced_signal = self._convert_to_enhanced_signal(mr_signal)
            
            logger.info(f"✅ Señal Mean Reversion generada para {symbol}: "
                       f"{enhanced_signal.signal_type} (Confianza: {enhanced_signal.confidence_score:.1f}%)")
            
            return enhanced_signal
            
        except Exception as e:
            logger.error(f"❌ Error en análisis Mean Reversion para {symbol}: {e}")
            
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
    print("🔄 Mean Reversion Professional Adapter")
    print("Este adaptador integra la estrategia Mean Reversion con el sistema de trading")
    print("Uso: Instanciar con un capital_client y llamar analyze(symbol, timeframe)")