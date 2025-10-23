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

from .enhanced_strategies import TradingSignal, EnhancedSignal
from .mean_reversion_professional import MarketRegime

logger = logging.getLogger(__name__)

class TrendFollowingProfessional:
    """📈 Estrategia de seguimiento de tendencia profesional"""
    
    def __init__(self):
        self.name = "TrendFollowingProfessional"
        
        # Parámetros de la estrategia
        self.ema_fast = 21
        self.ema_medium = 50
        self.ema_slow = 200
        self.atr_period = 14
        self.adx_period = 14
        self.rsi_period = 14
        self.volume_sma = 20
    
    def get_market_data(self, symbol: str, timeframe: str = "1h", limit: int = 500) -> pd.DataFrame:
        """Obtiene datos de mercado - será inyectado por el adaptador"""
        # Este método será sobrescrito por el adaptador con datos reales
        logger.warning(f"get_market_data no ha sido inyectado correctamente para {symbol}")
        return pd.DataFrame()
    
    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos los indicadores técnicos necesarios"""
        if df.empty:
            return df
        
        # EMAs para análisis de tendencia
        df['ema_21'] = ta.ema(df['close'], length=self.ema_fast)
        df['ema_50'] = ta.ema(df['close'], length=self.ema_medium)
        df['ema_200'] = ta.ema(df['close'], length=self.ema_slow)
        
        # ATR para volatilidad y stops
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=self.atr_period)
        
        # ADX para fuerza de tendencia
        adx_data = ta.adx(df['high'], df['low'], df['close'], length=self.adx_period)
        df['adx'] = adx_data['ADX_14']
        df['di_plus'] = adx_data['DMP_14']
        df['di_minus'] = adx_data['DMN_14']
        
        # RSI para momentum
        df['rsi'] = ta.rsi(df['close'], length=self.rsi_period)
        
        # MACD para momentum y divergencias
        macd_data = ta.macd(df['close'])
        df['macd'] = macd_data['MACD_12_26_9']
        df['macd_signal'] = macd_data['MACDs_12_26_9']
        df['macd_histogram'] = macd_data['MACDh_12_26_9']
        
        # Volumen
        df['volume_sma'] = ta.sma(df['volume'], length=self.volume_sma)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Bollinger Bands para volatilidad
        bb_data = ta.bbands(df['close'], length=20)
        df['bb_upper'] = bb_data['BBU_20_2.0']
        df['bb_middle'] = bb_data['BBM_20_2.0']
        df['bb_lower'] = bb_data['BBL_20_2.0']
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        return df
    
    def analyze_market_structure(self, df: pd.DataFrame) -> Dict:
        """Analiza la estructura de mercado (HH/HL vs LH/LL)"""
        if len(df) < 50:
            return {"structure": "insufficient_data", "strength": 0}
        
        # Identificar pivots (simplificado)
        highs = df['high'].rolling(window=5, center=True).max() == df['high']
        lows = df['low'].rolling(window=5, center=True).min() == df['low']
        
        # Obtener últimos 10 pivots altos y bajos
        recent_highs = df[highs]['high'].tail(5).values
        recent_lows = df[lows]['low'].tail(5).values
        
        if len(recent_highs) < 3 or len(recent_lows) < 3:
            return {"structure": "insufficient_pivots", "strength": 0}
        
        # Analizar tendencia de highs y lows
        higher_highs = sum(recent_highs[i] > recent_highs[i-1] for i in range(1, len(recent_highs)))
        higher_lows = sum(recent_lows[i] > recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        lower_highs = sum(recent_highs[i] < recent_highs[i-1] for i in range(1, len(recent_highs)))
        lower_lows = sum(recent_lows[i] < recent_lows[i-1] for i in range(1, len(recent_lows)))
        
        # Determinar estructura
        if higher_highs >= 3 and higher_lows >= 2:
            return {"structure": "uptrend", "strength": (higher_highs + higher_lows) / 6}
        elif lower_highs >= 3 and lower_lows >= 2:
            return {"structure": "downtrend", "strength": (lower_highs + lower_lows) / 6}
        else:
            return {"structure": "sideways", "strength": 0.3}
    
    def analyze_trend_alignment(self, df: pd.DataFrame) -> Dict:
        """Verifica alineación de tendencia en múltiples timeframes"""
        if df.empty or len(df) < self.ema_slow:
            return {"aligned": False, "direction": "neutral", "strength": 0}
        
        current = df.iloc[-1]
        
        # Verificar orden de EMAs
        emas_bullish = (current['ema_21'] > current['ema_50'] > current['ema_200'])
        emas_bearish = (current['ema_21'] < current['ema_50'] < current['ema_200'])
        
        # Verificar precio vs EMAs
        price_above_emas = current['close'] > current['ema_21']
        price_below_emas = current['close'] < current['ema_21']
        
        # Verificar pendiente de EMAs
        ema21_slope = (current['ema_21'] - df['ema_21'].iloc[-5]) / 5
        ema50_slope = (current['ema_50'] - df['ema_50'].iloc[-5]) / 5
        
        if emas_bullish and price_above_emas and ema21_slope > 0 and ema50_slope > 0:
            return {"aligned": True, "direction": "bullish", "strength": 0.9}
        elif emas_bearish and price_below_emas and ema21_slope < 0 and ema50_slope < 0:
            return {"aligned": True, "direction": "bearish", "strength": 0.9}
        elif emas_bullish and price_above_emas:
            return {"aligned": True, "direction": "bullish", "strength": 0.6}
        elif emas_bearish and price_below_emas:
            return {"aligned": True, "direction": "bearish", "strength": 0.6}
        else:
            return {"aligned": False, "direction": "neutral", "strength": 0.3}
    
    def analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """Analiza momentum y divergencias"""
        if df.empty or len(df) < 20:
            return {"momentum": "neutral", "strength": 0, "divergence": False}
        
        current = df.iloc[-1]
        
        # Análisis de RSI
        rsi_bullish = 30 < current['rsi'] < 70 and current['rsi'] > df['rsi'].iloc[-5]
        rsi_bearish = 30 < current['rsi'] < 70 and current['rsi'] < df['rsi'].iloc[-5]
        rsi_overbought = current['rsi'] > 70
        rsi_oversold = current['rsi'] < 30
        
        # Análisis de MACD
        macd_bullish = (current['macd'] > current['macd_signal'] and 
                       current['macd_histogram'] > 0)
        macd_bearish = (current['macd'] < current['macd_signal'] and 
                       current['macd_histogram'] < 0)
        
        # Análisis de ADX
        adx_strong = current['adx'] > 25
        di_bullish = current['di_plus'] > current['di_minus']
        di_bearish = current['di_plus'] < current['di_minus']
        
        # Combinar señales
        bullish_signals = sum([rsi_bullish, macd_bullish, di_bullish and adx_strong])
        bearish_signals = sum([rsi_bearish, macd_bearish, di_bearish and adx_strong])
        
        if bullish_signals >= 2 and not rsi_overbought:
            return {"momentum": "bullish", "strength": bullish_signals / 3, "divergence": False}
        elif bearish_signals >= 2 and not rsi_oversold:
            return {"momentum": "bearish", "strength": bearish_signals / 3, "divergence": False}
        else:
            return {"momentum": "neutral", "strength": 0.3, "divergence": False}
    
    def analyze_volume_confirmation(self, df: pd.DataFrame) -> Dict:
        """Analiza confirmación por volumen"""
        if df.empty or len(df) < self.volume_sma:
            return {"confirmed": False, "strength": 0}
        
        current = df.iloc[-1]
        
        # Volumen por encima de la media
        volume_above_average = current['volume_ratio'] > 1.2
        
        # Volumen creciente en últimas 3 velas
        volume_increasing = (df['volume'].tail(3).is_monotonic_increasing)
        
        # Precio y volumen en la misma dirección
        price_change = (current['close'] - df['close'].iloc[-2]) / df['close'].iloc[-2]
        volume_change = (current['volume'] - df['volume'].iloc[-2]) / df['volume'].iloc[-2]
        
        same_direction = (price_change > 0 and volume_change > 0) or (price_change < 0 and volume_change > 0)
        
        confirmations = sum([volume_above_average, volume_increasing, same_direction])
        
        return {
            "confirmed": confirmations >= 2,
            "strength": confirmations / 3,
            "volume_ratio": current['volume_ratio']
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
        bb_squeeze = current['bb_width'] < df['bb_width'].rolling(20).mean() * 0.8
        recent_breakout = (current['close'] > current['bb_upper'] or 
                          current['close'] < current['bb_lower'])
        
        # Determinar régimen
        if recent_breakout and current['adx'] > 30:
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
    
    def calculate_volatility_percentile(self, df: pd.DataFrame, period: int = 100) -> float:
        """Calcula el percentil de volatilidad actual"""
        if len(df) < period:
            return 50.0
        
        current_volatility = df['atr'].iloc[-1]
        historical_volatility = df['atr'].tail(period)
        
        percentile = (historical_volatility < current_volatility).sum() / len(historical_volatility) * 100
        return percentile
    
    def calculate_stop_loss_take_profit(self, df: pd.DataFrame, signal_type: str, entry_price: float) -> Tuple[float, float]:
        """Calcula stop loss y take profit basado en ATR"""
        if df.empty:
            return entry_price, entry_price
        
        current_atr = df['atr'].iloc[-1]
        atr_multiplier_sl = 2.0  # Stop loss a 2 ATR
        atr_multiplier_tp = 3.0  # Take profit a 3 ATR (1:1.5 R/R)
        
        if signal_type == "BUY":
            stop_loss = entry_price - (current_atr * atr_multiplier_sl)
            take_profit = entry_price + (current_atr * atr_multiplier_tp)
        else:  # SELL
            stop_loss = entry_price + (current_atr * atr_multiplier_sl)
            take_profit = entry_price - (current_atr * atr_multiplier_tp)
        
        return stop_loss, take_profit
    
    def analyze(self, symbol: str, timeframe: str = "1h") -> Optional[ProfessionalSignal]:
        """Análisis principal de la estrategia"""
        try:
            # 1. Obtener datos de mercado
            df = self.get_market_data(symbol, timeframe)
            if df.empty:
                logger.warning(f"No se pudieron obtener datos para {symbol}")
                return None
            
            # 2. Calcular indicadores técnicos
            df = self.calculate_technical_indicators(df)
            
            # 3. Análisis de componentes
            trend_analysis = self.analyze_trend_alignment(df)
            momentum_analysis = self.analyze_momentum(df)
            volume_analysis = self.analyze_volume_confirmation(df)
            structure_analysis = self.analyze_market_structure(df)
            market_regime = self.determine_market_regime(df)
            
            current_price = df['close'].iloc[-1]
            
            # 4. Determinar señal
            signal_type = "HOLD"
            confluence_count = 0
            confluence_details = []
            
            # Lógica de señal BUY
            if (trend_analysis["aligned"] and trend_analysis["direction"] == "bullish" and
                momentum_analysis["momentum"] == "bullish" and
                structure_analysis["structure"] in ["uptrend", "sideways"]):
                
                signal_type = "BUY"
                confluence_count += 1
                confluence_details.append("Tendencia alcista alineada")
                
                if momentum_analysis["strength"] > 0.6:
                    confluence_count += 1
                    confluence_details.append("Momentum alcista fuerte")
                
                if volume_analysis["confirmed"]:
                    confluence_count += 1
                    confluence_details.append("Volumen confirmatorio")
                
                if market_regime in [MarketRegime.TRENDING_UP, MarketRegime.BREAKOUT]:
                    confluence_count += 1
                    confluence_details.append(f"Régimen favorable: {market_regime.value}")
            
            # Lógica de señal SELL
            elif (trend_analysis["aligned"] and trend_analysis["direction"] == "bearish" and
                  momentum_analysis["momentum"] == "bearish" and
                  structure_analysis["structure"] in ["downtrend", "sideways"]):
                
                signal_type = "SELL"
                confluence_count += 1
                confluence_details.append("Tendencia bajista alineada")
                
                if momentum_analysis["strength"] > 0.6:
                    confluence_count += 1
                    confluence_details.append("Momentum bajista fuerte")
                
                if volume_analysis["confirmed"]:
                    confluence_count += 1
                    confluence_details.append("Volumen confirmatorio")
                
                if market_regime in [MarketRegime.TRENDING_DOWN, MarketRegime.BREAKOUT]:
                    confluence_count += 1
                    confluence_details.append(f"Régimen favorable: {market_regime.value}")
            
            # 5. Calcular stop loss y take profit
            stop_loss, take_profit = self.calculate_stop_loss_take_profit(df, signal_type, current_price)
            
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
                strength="Strong" if confluence_count >= 4 else "Moderate" if confluence_count >= 3 else "Weak",
                strategy_name=self.name,
                timestamp=datetime.now(),
                
                # Componentes de análisis EnhancedSignal
                volume_confirmation=volume_analysis["confirmed"],
                trend_confirmation="BULLISH" if signal_type == "BUY" else "BEARISH" if signal_type == "SELL" else "NEUTRAL",
                risk_reward_ratio=risk_reward_ratio,
                stop_loss_price=stop_loss,
                take_profit_price=take_profit,
                market_regime=market_regime.value if hasattr(market_regime, 'value') else str(market_regime),
                confluence_score=confluence_count,
                timeframe=timeframe,
                
                # Notas adicionales
                notes=f"Trend: {trend_analysis['direction']}, Momentum: {momentum_analysis['momentum']}, Structure: {structure_analysis['structure']}, R/R: {risk_reward_ratio:.2f}"
            )
            
            # 8. Calcular confianza basada en confluencias
            base_confidence = 50.0
            confluence_bonus = confluence_count * 8.0  # 8% por confluencia
            volume_bonus = 10.0 if volume_analysis["confirmed"] else 0.0
            trend_bonus = 15.0 if trend_analysis["aligned"] else 0.0
            
            signal.confidence_score = min(95.0, base_confidence + confluence_bonus + volume_bonus + trend_bonus)
            
            # 9. Filtros básicos de calidad
            if signal.confidence_score < 65.0:
                logger.info(f"Señal para {symbol} no alcanza confianza mínima (65%): {signal.confidence_score:.1f}%")
                return None
            
            if confluence_count < 3:
                logger.info(f"Señal para {symbol} no tiene suficientes confluencias: {confluence_count}")
                return None
            
            return signal
            
        except Exception as e:
            logger.error(f"Error en análisis de {symbol}: {str(e)}")
            return None

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
        print(f"Confluencias: {signal.confluence_count}")
        print(f"Detalles: {', '.join(signal.confluence_details)}")
    else:
        print("❌ No se generó señal o no pasó los filtros profesionales")