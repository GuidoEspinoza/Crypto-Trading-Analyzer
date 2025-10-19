"""🔌 PROFESSIONAL STRATEGY ADAPTER
Adaptador para integrar las estrategias profesionales con el sistema existente.
Versión simplificada para diagnóstico.
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from dataclasses import dataclass

# Importar el sistema existente
from .enhanced_strategies import TradingSignal, TradingStrategy, EnhancedSignal
from .capital_client import CapitalClient

logger = logging.getLogger(__name__)

class ProfessionalStrategyAdapter(TradingStrategy):
    """🎯 Adaptador para estrategias profesionales - Versión simplificada"""
    
    def __init__(self, capital_client: CapitalClient):
        super().__init__(capital_client)
        self.name = "TrendFollowingProfessional"
        
        # Configuración del adaptador
        self.min_professional_score = 70  # Umbral más bajo para testing
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis simplificado para diagnóstico"""
        try:
            logger.info(f"🎯 Iniciando análisis profesional simplificado para {symbol}")
            
            # 1. Obtener datos de mercado usando el método base
            df = self.get_market_data(symbol, timeframe, 200)
            
            if df.empty:
                logger.warning(f"No hay datos disponibles para {symbol}")
                return self._create_hold_signal(symbol, 0.0, "Sin datos disponibles")
            
            logger.info(f"✅ Datos obtenidos para {symbol}: {len(df)} velas")
            
            # 2. Análisis técnico básico
            try:
                # Calcular indicadores básicos
                df['ema_21'] = ta.ema(df['close'], length=21)
                df['ema_50'] = ta.ema(df['close'], length=50)
                df['rsi'] = ta.rsi(df['close'], length=14)
                df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
                
                # Obtener valores actuales
                current_price = float(df['close'].iloc[-1])
                current_rsi = float(df['rsi'].iloc[-1]) if not pd.isna(df['rsi'].iloc[-1]) else 50.0
                ema_21 = float(df['ema_21'].iloc[-1]) if not pd.isna(df['ema_21'].iloc[-1]) else current_price
                ema_50 = float(df['ema_50'].iloc[-1]) if not pd.isna(df['ema_50'].iloc[-1]) else current_price
                atr = float(df['atr'].iloc[-1]) if not pd.isna(df['atr'].iloc[-1]) else current_price * 0.02
                
                logger.info(f"📊 Indicadores calculados - RSI: {current_rsi:.1f}, EMA21: {ema_21:.2f}, EMA50: {ema_50:.2f}")
                
                # 3. Lógica de señal simplificada
                signal_type = "HOLD"
                confidence = 50.0
                notes = []
                
                # Análisis de tendencia
                if current_price > ema_21 > ema_50:
                    if current_rsi < 70:  # No sobrecomprado
                        signal_type = "BUY"
                        confidence = 75.0
                        notes.append("🟢 Tendencia alcista confirmada")
                        notes.append(f"📈 Precio > EMA21 > EMA50")
                elif current_price < ema_21 < ema_50:
                    if current_rsi > 30:  # No sobrevendido
                        signal_type = "SELL"
                        confidence = 75.0
                        notes.append("🔴 Tendencia bajista confirmada")
                        notes.append(f"📉 Precio < EMA21 < EMA50")
                else:
                    notes.append("🔄 Mercado lateral o sin tendencia clara")
                
                # Ajustar confianza basado en RSI
                if current_rsi > 70:
                    confidence *= 0.8
                    notes.append("⚠️ RSI sobrecomprado")
                elif current_rsi < 30:
                    confidence *= 0.8
                    notes.append("⚠️ RSI sobrevendido")
                
                # Calcular stop loss y take profit
                stop_loss_price = current_price
                take_profit_price = current_price
                risk_reward_ratio = 0.0
                
                if signal_type == "BUY":
                    stop_loss_price = current_price - (atr * 2)
                    take_profit_price = current_price + (atr * 3)
                    risk_reward_ratio = 1.5
                elif signal_type == "SELL":
                    stop_loss_price = current_price + (atr * 2)
                    take_profit_price = current_price - (atr * 3)
                    risk_reward_ratio = 1.5
                
                # Determinar régimen de mercado
                volatility = atr / current_price
                if volatility > 0.03:
                    market_regime = "VOLATILE"
                elif abs(ema_21 - ema_50) / current_price > 0.02:
                    market_regime = "TRENDING"
                else:
                    market_regime = "RANGING"
                
                notes.append(f"🎯 Análisis profesional completado")
                notes.append(f"💹 Volatilidad: {volatility*100:.2f}%")
                
                # 4. Crear señal
                trading_signal = EnhancedSignal(
                    symbol=symbol,
                    signal_type=signal_type,
                    confidence_score=confidence,
                    strength="Strong" if confidence > 80 else "Moderate" if confidence > 60 else "Weak",
                    price=current_price,
                    strategy_name="TrendFollowingProfessional",
                    timestamp=datetime.now(),
                    volume_confirmation=True,  # Simplificado
                    trend_confirmation="BULLISH" if signal_type == "BUY" else "BEARISH" if signal_type == "SELL" else "NEUTRAL",
                    risk_reward_ratio=risk_reward_ratio,
                    stop_loss_price=stop_loss_price,
                    take_profit_price=take_profit_price,
                    market_regime=market_regime,
                    confluence_score=int(confidence / 10),  # Convertir a entero
                    notes=" | ".join(notes)
                )
                
                logger.info(f"✅ Señal profesional generada: {signal_type} ({confidence:.1f}%)")
                return trading_signal
                
            except Exception as e:
                logger.error(f"Error en cálculo de indicadores para {symbol}: {str(e)}")
                return self._create_hold_signal(symbol, 0.0, f"Error en indicadores: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error general en análisis profesional de {symbol}: {str(e)}")
            return self._create_hold_signal(symbol, 0.0, f"Error general: {str(e)}")
    
    def _create_hold_signal(self, symbol: str, confidence: float, reason: str) -> EnhancedSignal:
        """Crea una señal HOLD por defecto"""
        try:
            # Intentar obtener precio actual
            current_price = 0.0
            try:
                df = self.get_market_data(symbol, "1h", 1)
                if not df.empty:
                    current_price = float(df['close'].iloc[-1])
            except:
                current_price = 0.0
            
            return EnhancedSignal(
                symbol=symbol,
                signal_type="HOLD",
                confidence_score=confidence,
                strength="Weak",
                price=current_price,
                strategy_name="TrendFollowingProfessional",
                timestamp=datetime.now(),
                volume_confirmation=False,
                trend_confirmation="NEUTRAL",
                risk_reward_ratio=0.0,
                stop_loss_price=current_price,
                take_profit_price=current_price,
                market_regime="RANGING",
                confluence_score=0,
                notes=f"🔄 HOLD: {reason}"
            )
        except Exception as e:
            logger.error(f"Error creando señal HOLD: {str(e)}")
            return EnhancedSignal(
                symbol=symbol,
                signal_type="HOLD",
                confidence_score=0.0,
                strength="Weak",
                price=0.0,
                strategy_name="TrendFollowingProfessional",
                timestamp=datetime.now(),
                volume_confirmation=False,
                trend_confirmation="NEUTRAL",
                risk_reward_ratio=0.0,
                stop_loss_price=0.0,
                take_profit_price=0.0,
                market_regime="RANGING",
                confluence_score=0,
                notes="❌ Error crítico en análisis"
            )

# Función de fábrica para crear la estrategia adaptada
def create_professional_strategy(capital_client: CapitalClient) -> ProfessionalStrategyAdapter:
    """Crea una instancia de la estrategia profesional adaptada"""
    return ProfessionalStrategyAdapter(capital_client)