"""🚀 Enhanced Trading Strategies - Versión Profesional
Estrategias de trading mejoradas con análisis multi-indicador,
confirmación de volumen y gestión avanzada de riesgo.

Desarrollado por: Experto en Trading & Programación
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from abc import ABC, abstractmethod

from .config import StrategyConfig

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
        self.min_confidence = 60.0  # Mínima confianza para ejecutar trade
        self.advanced_indicators = AdvancedIndicators()
    
    @abstractmethod
    def analyze(self, symbol: str, timeframe: str = "1h") -> TradingSignal:
        """Analizar símbolo y generar señal"""
        pass
    
    def get_market_data(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
        """Obtener datos de mercado"""
        import ccxt
        exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    
    def get_current_price(self, symbol: str) -> float:
        """Obtener precio actual del símbolo"""
        try:
            import ccxt
            exchange = ccxt.binance({'sandbox': False, 'enableRateLimit': True})
            ticker = exchange.fetch_ticker(symbol)
            return float(ticker['last']) if ticker['last'] else 0.0
        except Exception as e:
            logging.error(f"Error getting current price for {symbol}: {e}")
            # Fallback: usar el último precio de los datos históricos
            try:
                df = self.get_market_data(symbol, "1m", limit=1)
                return float(df['close'].iloc[-1]) if not df.empty else 0.0
            except:
                return 0.0

# Importar AdvancedIndicators con path absoluto
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from advanced_indicators import AdvancedIndicators

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

class EnhancedTradingStrategy(TradingStrategy):
    """Clase base para estrategias mejoradas"""
    
    def __init__(self, name: str, enable_filters: bool = True):
        super().__init__(name)
        self.min_volume_ratio = 1.2  # Volumen debe ser 20% mayor al promedio
        self.min_confluence = 2  # Mínimo 2 indicadores deben confirmar
        # Signal filters deshabilitados (módulo eliminado)
        self.signal_filter = None
        
    def analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Analizar volumen para confirmación de señales"""
        try:
            if 'volume' not in df.columns:
                return {"volume_confirmation": False, "volume_ratio": 0.0}
            
            current_volume = df['volume'].iloc[-1]
            avg_volume_20 = df['volume'].rolling(20).mean().iloc[-1]
            
            if pd.isna(avg_volume_20) or avg_volume_20 == 0:
                return {"volume_confirmation": False, "volume_ratio": 0.0}
            
            volume_ratio = current_volume / avg_volume_20
            volume_confirmation = bool(volume_ratio >= self.min_volume_ratio)
            
            return {
                "volume_confirmation": volume_confirmation,
                "volume_ratio": round(float(volume_ratio), 2),
                "current_volume": float(current_volume),
                "avg_volume": float(avg_volume_20)
            }
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return {"volume_confirmation": False, "volume_ratio": 0.0}
    
    def analyze_trend(self, df: pd.DataFrame) -> str:
        """Analizar tendencia usando múltiples indicadores"""
        try:
            # EMA 20 vs EMA 50
            ema_20 = ta.ema(df['close'], length=20)
            ema_50 = ta.ema(df['close'], length=50)
            
            if ema_20 is None or ema_50 is None:
                return "NEUTRAL"
            
            current_ema_20 = ema_20.iloc[-1]
            current_ema_50 = ema_50.iloc[-1]
            
            # ADX para fuerza de tendencia
            adx_data = ta.adx(df['high'], df['low'], df['close'])
            if adx_data is not None and not adx_data.empty:
                adx_value = adx_data['ADX_14'].iloc[-1] if 'ADX_14' in adx_data.columns else 25
            else:
                adx_value = 25
            
            # Determinar tendencia
            if current_ema_20 > current_ema_50 and adx_value > 25:
                return "BULLISH"
            elif current_ema_20 < current_ema_50 and adx_value > 25:
                return "BEARISH"
            else:
                return "NEUTRAL"
                
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return "NEUTRAL"
    
    def detect_market_regime(self, df: pd.DataFrame) -> str:
        """Detectar régimen de mercado"""
        try:
            # Calcular volatilidad (ATR)
            atr = ta.atr(df['high'], df['low'], df['close'], length=14)
            if atr is None or atr.empty:
                return "NORMAL"
            
            current_atr = atr.iloc[-1]
            avg_atr = atr.rolling(50).mean().iloc[-1]
            
            if pd.isna(current_atr) or pd.isna(avg_atr):
                return "NORMAL"
            
            volatility_ratio = current_atr / avg_atr
            
            # Detectar si está en tendencia o rango
            price_range = df['high'].rolling(20).max().iloc[-1] - df['low'].rolling(20).min().iloc[-1]
            current_price = df['close'].iloc[-1]
            
            if volatility_ratio > 1.5:
                return "VOLATILE"
            elif abs(current_price - (df['high'].rolling(20).max().iloc[-1] + df['low'].rolling(20).min().iloc[-1]) / 2) < price_range * 0.2:
                return "RANGING"
            else:
                return "TRENDING"
                
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return "NORMAL"
    
    def calculate_risk_reward(self, entry_price: float, signal_type: str, atr: float) -> Tuple[float, float, float]:
        """Calcular stop loss, take profit y ratio riesgo/beneficio"""
        try:
            if signal_type == "BUY":
                stop_loss = entry_price - (2 * atr)  # 2 ATR por debajo
                take_profit = entry_price + (3 * atr)  # 3 ATR por encima
            elif signal_type == "SELL":
                stop_loss = entry_price + (2 * atr)  # 2 ATR por encima
                take_profit = entry_price - (3 * atr)  # 3 ATR por debajo
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
            df = self.get_market_data(symbol, timeframe, limit=100)
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
                quality_grade="B"
            )

class ProfessionalRSIStrategy(EnhancedTradingStrategy):
    """🎯 Estrategia RSI Profesional con confirmaciones múltiples y nuevos indicadores"""
    
    def __init__(self):
        super().__init__("Professional_RSI_Enhanced")
        
        # Configuración desde archivo centralizado
        self.config = StrategyConfig.ProfessionalRSI()
        self.min_confidence = self.config.MIN_CONFIDENCE
        self.rsi_oversold = self.config.RSI_OVERSOLD
        self.rsi_overbought = self.config.RSI_OVERBOUGHT
        self.rsi_period = self.config.RSI_PERIOD
        
        # Configuración de confirmaciones
        self.min_volume_ratio = self.config.MIN_VOLUME_RATIO
        self.min_confluence = self.config.MIN_CONFLUENCE
        self.trend_strength_threshold = self.config.TREND_STRENGTH_THRESHOLD
        
        # Configuración de filtros de calidad
        self.min_atr_ratio = self.config.MIN_ATR_RATIO
        self.max_spread_threshold = self.config.MAX_SPREAD_THRESHOLD
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis RSI profesional con confirmaciones avanzadas"""
        try:
            df = self.get_market_data(symbol, timeframe, limit=100)
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data")
            
            # === INDICADORES PRINCIPALES ===
            # RSI Mejorado con análisis de divergencias
            enhanced_rsi = AdvancedIndicators.enhanced_rsi(df)
            
            # Bollinger Bands para contexto de volatilidad
            bollinger = AdvancedIndicators.bollinger_bands(df)
            
            # VWAP para análisis institucional
            vwap_analysis = AdvancedIndicators.vwap(df)
            
            # === INDICADORES DE VOLUMEN ===
            # On Balance Volume
            obv_analysis = AdvancedIndicators.on_balance_volume(df)
            
            # Money Flow Index
            mfi_analysis = AdvancedIndicators.money_flow_index(df)
            
            # Volume Profile
            volume_profile = AdvancedIndicators.volume_profile(df)
            
            # === INDICADORES DE VOLATILIDAD Y MOMENTUM ===
            # Average True Range
            atr_analysis = AdvancedIndicators.average_true_range(df)
            
            # Rate of Change
            roc_analysis = AdvancedIndicators.rate_of_change(df)
            
            # === ANÁLISIS DE ESTRUCTURA DE MERCADO ===
            # Soporte y Resistencia
            support_resistance = AdvancedIndicators.support_resistance_levels(df)
            
            # Análisis de líneas de tendencia
            trend_lines = AdvancedIndicators.trend_lines_analysis(df)
            
            # Detección de patrones de gráfico
            chart_patterns = AdvancedIndicators.chart_patterns_detection(df)
            
            # Confirmaciones adicionales (indicadores existentes)
            stoch = AdvancedIndicators.stochastic_oscillator(df)
            williams_r = AdvancedIndicators.williams_percent_r(df)
            volume_analysis = self.analyze_volume(df)
            trend = self.analyze_trend(df)
            market_regime = self.detect_market_regime(df)
            
            # ATR para stop loss (usar el nuevo análisis)
            current_atr = atr_analysis["atr"]
            
            # === LÓGICA DE SEÑALES CON CONFLUENCIA AVANZADA ===
            confluence_score = 0
            signal_type = "HOLD"
            confidence = 50.0
            notes = []
            
            # === ANÁLISIS RSI MEJORADO ===
            rsi_signal = enhanced_rsi["signal"]
            if rsi_signal in ["BUY", "STRONG_BUY"]:
                confluence_score += 2 if rsi_signal == "STRONG_BUY" else 1
                signal_type = "BUY"
                confidence += 25 if rsi_signal == "STRONG_BUY" else 15
                notes.append(f"Enhanced RSI: {enhanced_rsi['interpretation']}")
            elif rsi_signal in ["SELL", "STRONG_SELL"]:
                confluence_score += 2 if rsi_signal == "STRONG_SELL" else 1
                signal_type = "SELL"
                confidence += 25 if rsi_signal == "STRONG_SELL" else 15
                notes.append(f"Enhanced RSI: {enhanced_rsi['interpretation']}")
            
            # === CONFIRMACIÓN BOLLINGER BANDS ===
            if bollinger["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 12
                notes.append(f"Bollinger confirms: {bollinger['interpretation']}")
            
            # === CONFIRMACIÓN VWAP ===
            if vwap_analysis["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 10
                notes.append(f"VWAP confirms: {vwap_analysis['interpretation']}")
            
            # === ANÁLISIS DE VOLUMEN AVANZADO ===
            volume_signals = [obv_analysis["signal"], mfi_analysis["signal"], volume_profile["signal"]]
            volume_confirmations = sum(1 for vs in volume_signals if vs == signal_type and signal_type != "HOLD")
            
            if volume_confirmations >= 2:
                confluence_score += 2
                confidence += 20
                notes.append(f"Strong volume confirmation ({volume_confirmations}/3)")
            elif volume_confirmations == 1:
                confluence_score += 1
                confidence += 10
                notes.append("Volume confirmation")
            
            # === MOMENTUM Y VOLATILIDAD ===
            if roc_analysis["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 8
                notes.append(f"ROC momentum: {roc_analysis['interpretation']}")
            
            # Ajustar por volatilidad (ATR)
            if atr_analysis["volatility_level"] == "MUY ALTA":
                confidence -= 15
                notes.append("High volatility warning")
            elif atr_analysis["volatility_level"] == "BAJA":
                confidence += 5
                notes.append("Low volatility favorable")
            
            # === SOPORTE Y RESISTENCIA ===
            if support_resistance["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 15
                notes.append(f"S/R level: {support_resistance['interpretation']}")
            
            # === LÍNEAS DE TENDENCIA ===
            if trend_lines["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 12
                notes.append(f"Trend line: {trend_lines['interpretation']}")
            
            # === PATRONES DE GRÁFICO ===
            if chart_patterns["signal"] == signal_type and signal_type != "HOLD":
                # Determinar fuerza del patrón basado en confianza
                pattern_strength = "STRONG" if any(p.get("confidence", 0) >= 75 for p in chart_patterns.get("patterns", [])) else "MODERATE"
                confluence_score += 2 if pattern_strength == "STRONG" else 1
                confidence += 18 if pattern_strength == "STRONG" else 10
                notes.append(f"Chart pattern: {chart_patterns['interpretation']}")
            
            # === CONFIRMACIONES TRADICIONALES ===
            # Confirmación con Stochastic
            if stoch["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 8
                notes.append("Stochastic confirms")
            
            # Confirmación con Williams %R
            if williams_r["signal"] == signal_type and signal_type != "HOLD":
                confluence_score += 1
                confidence += 6
                notes.append("Williams %R confirms")
            
            # === CONFIRMACIÓN DE TENDENCIA ===
            if (signal_type == "BUY" and trend == "BULLISH") or (signal_type == "SELL" and trend == "BEARISH"):
                confluence_score += 1
                confidence += 15
                notes.append(f"Trend confirms ({trend})")
            
            # Penalizar si va contra la tendencia fuerte
            if (signal_type == "BUY" and trend == "BEARISH") or (signal_type == "SELL" and trend == "BULLISH"):
                confidence -= 20
                notes.append("Against strong trend")
            
            # === FILTROS DE CALIDAD ===
            # Requerir mínimo de confluencia para señales fuertes
            if confluence_score < self.min_confluence and signal_type != "HOLD":
                signal_type = "HOLD"
                confidence = 45
                notes.append(f"Insufficient confluence ({confluence_score}/{self.min_confluence})")
            
            # Ajustar por régimen de mercado
            if market_regime == "VOLATILE":
                confidence -= 10
                notes.append("High volatility")
            elif market_regime == "RANGING" and signal_type != "HOLD":
                confidence += 5
                notes.append("Range-bound market")
            
            # Requiere mínima confluencia
            if confluence_score < self.min_confluence and signal_type != "HOLD":
                signal_type = "HOLD"
                confidence = 45
                notes.append("Insufficient confluence")
            
            # Calcular stop loss y take profit
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, signal_type, current_atr
            )
            
            # Verificar ratio riesgo/beneficio mínimo
            if risk_reward < 1.5 and signal_type != "HOLD":
                signal_type = "HOLD"
                confidence = 40
                notes.append("Poor risk/reward ratio")
            
            return EnhancedSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=min(95, max(0, confidence)),
                strength=self._get_signal_strength(confidence),
                timestamp=datetime.now(),
                indicators_data={
                    # Indicadores tradicionales
                    "rsi": enhanced_rsi,
                    "stochastic": stoch,
                    "williams_r": williams_r,
                    "volume_analysis": volume_analysis,
                    "atr": round(current_atr, 4),
                    "timeframe": timeframe,
                    
                    # Nuevos indicadores avanzados
                    "bollinger_bands": bollinger,
                    "vwap": vwap_analysis,
                    "obv": obv_analysis,
                    "mfi": mfi_analysis,
                    "volume_profile": volume_profile,
                    "roc": roc_analysis,
                    "support_resistance": support_resistance,
                    "atr_analysis": atr_analysis,
                    "volatility_level": atr_analysis["volatility_level"],
                    "trend_lines": trend_lines,
                    "chart_patterns": chart_patterns
                },
                notes=" | ".join(notes) if notes else "No clear signals",
                volume_confirmation=bool(volume_analysis["volume_confirmation"]),
                trend_confirmation=str(trend),
                risk_reward_ratio=round(float(risk_reward), 2),
                stop_loss_price=round(float(stop_loss), 2),
                take_profit_price=round(float(take_profit), 2),
                market_regime=str(market_regime),
                confluence_score=int(confluence_score)
            )
            
        except Exception as e:
            logger.error(f"Error in Professional RSI analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _get_signal_strength(self, confidence: float) -> str:
        """Convertir confidence a strength"""
        if confidence >= 85: return "Very Strong"
        elif confidence >= 70: return "Strong"
        elif confidence >= 55: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> EnhancedSignal:
        """Crear señal HOLD"""
        return EnhancedSignal(
            symbol=symbol,
            strategy_name=self.name,
            signal_type="HOLD",
            price=0.0,
            confidence_score=0.0,
            strength="None",
            timestamp=datetime.now(),
            indicators_data={},
            notes=f"HOLD: {reason}",
            volume_confirmation=False,
            trend_confirmation="NEUTRAL",
            risk_reward_ratio=0.0,
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            confluence_score=0
        )

class MultiTimeframeStrategy(EnhancedTradingStrategy):
    """📊 Estrategia Multi-Timeframe para confirmación de tendencia"""
    
    def __init__(self):
        super().__init__("Multi_Timeframe")
        
        # Configuración desde archivo centralizado
        self.config = StrategyConfig.MultiTimeframe()
        self.timeframes = self.config.TIMEFRAMES
        self.min_confidence = self.config.MIN_CONFIDENCE
        self.rsi_config = self.config.RSI_CONFIG
        self.timeframe_weights = self.config.TIMEFRAME_WEIGHTS
        self.min_timeframe_consensus = self.config.MIN_TIMEFRAME_CONSENSUS
        self.trend_alignment_required = self.config.TREND_ALIGNMENT_REQUIRED
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis multi-timeframe"""
        try:
            signals = {}
            trends = {}
            
            # Analizar cada timeframe
            for tf in self.timeframes:
                try:
                    df = self.get_market_data(symbol, tf, limit=50)
                    if not df.empty:
                        trends[tf] = self.analyze_trend(df)
                        
                        # RSI para cada timeframe
                        rsi = ta.rsi(df['close'], length=14)
                        if rsi is not None:
                            rsi_value = rsi.iloc[-1]
                            if rsi_value <= 30:
                                signals[tf] = "BUY"
                            elif rsi_value >= 70:
                                signals[tf] = "SELL"
                            else:
                                signals[tf] = "HOLD"
                        else:
                            signals[tf] = "HOLD"
                    else:
                        signals[tf] = "HOLD"
                        trends[tf] = "NEUTRAL"
                except Exception as e:
                    logger.warning(f"Error analyzing {tf}: {e}")
                    signals[tf] = "HOLD"
                    trends[tf] = "NEUTRAL"
            
            # Determinar señal consenso
            buy_votes = sum(1 for s in signals.values() if s == "BUY")
            sell_votes = sum(1 for s in signals.values() if s == "SELL")
            
            # Ponderar por timeframe (mayor peso a timeframes más largos)
            weights = {"1h": 1, "4h": 2, "1d": 3}
            weighted_buy = sum(weights.get(tf, 1) for tf, signal in signals.items() if signal == "BUY")
            weighted_sell = sum(weights.get(tf, 1) for tf, signal in signals.items() if signal == "SELL")
            
            current_price = self.get_current_price(symbol)
            df_main = self.get_market_data(symbol, timeframe)
            
            if weighted_buy > weighted_sell and buy_votes >= 2:
                signal_type = "BUY"
                confidence = 60 + (weighted_buy * 5)
            elif weighted_sell > weighted_buy and sell_votes >= 2:
                signal_type = "SELL"
                confidence = 60 + (weighted_sell * 5)
            else:
                signal_type = "HOLD"
                confidence = 45
            
            # Análisis de volumen y otros factores
            volume_analysis = self.analyze_volume(df_main) if not df_main.empty else {"volume_confirmation": False}
            market_regime = self.detect_market_regime(df_main) if not df_main.empty else "NORMAL"
            
            # ATR para stop loss
            atr = ta.atr(df_main['high'], df_main['low'], df_main['close'], length=14)
            current_atr = atr.iloc[-1] if atr is not None else current_price * 0.02
            
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, signal_type, current_atr
            )
            
            return EnhancedSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=signal_type,
                price=current_price,
                confidence_score=min(95, confidence),
                strength=self._get_signal_strength(confidence),
                timestamp=datetime.now(),
                indicators_data={
                    "timeframe_signals": signals,
                    "timeframe_trends": trends,
                    "buy_votes": buy_votes,
                    "sell_votes": sell_votes,
                    "weighted_buy": weighted_buy,
                    "weighted_sell": weighted_sell,
                    "volume_analysis": volume_analysis
                },
                notes=f"Multi-TF: {buy_votes}B/{sell_votes}S votes, Trends: {trends}",
                volume_confirmation=bool(volume_analysis.get("volume_confirmation", False)),
                trend_confirmation=str(trends.get("1d", "NEUTRAL")),
                risk_reward_ratio=round(float(risk_reward), 2),
                stop_loss_price=round(float(stop_loss), 2),
                take_profit_price=round(float(take_profit), 2),
                market_regime=str(market_regime),
                confluence_score=int(buy_votes + sell_votes)
            )
            
        except Exception as e:
            logger.error(f"Error in Multi-Timeframe analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _get_signal_strength(self, confidence: float) -> str:
        if confidence >= 85: return "Very Strong"
        elif confidence >= 70: return "Strong"
        elif confidence >= 55: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> EnhancedSignal:
        return EnhancedSignal(
            symbol=symbol, strategy_name=self.name, signal_type="HOLD",
            price=0.0, confidence_score=0.0, strength="None",
            timestamp=datetime.now(), indicators_data={}, notes=f"HOLD: {reason}",
            volume_confirmation=False, trend_confirmation="NEUTRAL",
            risk_reward_ratio=0.0, stop_loss_price=0.0, take_profit_price=0.0,
            market_regime="NORMAL", confluence_score=0
        )

class EnsembleStrategy(EnhancedTradingStrategy):
    """🎯 Estrategia Ensemble - Combina múltiples estrategias con votación inteligente"""
    
    def __init__(self):
        super().__init__("Ensemble_Master")
        
        # Configuración desde archivo centralizado
        self.config = StrategyConfig.Ensemble()
        
        # Inicializar sub-estrategias
        self.rsi_strategy = ProfessionalRSIStrategy()
        self.mtf_strategy = MultiTimeframeStrategy()
        
        # Pesos para cada estrategia (basado en performance histórica)
        self.strategy_weights = self.config.STRATEGY_WEIGHTS
        
        # Configuración de ensemble
        self.min_consensus_threshold = self.config.MIN_CONSENSUS_THRESHOLD
        self.confidence_boost_factor = self.config.CONFIDENCE_BOOST_FACTOR
        
    def analyze(self, symbol: str, timeframe: str = "1h") -> EnhancedSignal:
        """Análisis ensemble combinando múltiples estrategias"""
        try:
            # Obtener señales de todas las estrategias
            signals = {}
            
            # RSI Profesional
            try:
                rsi_signal = self.rsi_strategy.analyze(symbol, timeframe)
                signals["Professional_RSI"] = rsi_signal
            except Exception as e:
                logger.warning(f"Error in RSI strategy: {e}")
                signals["Professional_RSI"] = None
            
            # Multi-Timeframe
            try:
                mtf_signal = self.mtf_strategy.analyze(symbol, timeframe)
                signals["Multi_Timeframe"] = mtf_signal
            except Exception as e:
                logger.warning(f"Error in MTF strategy: {e}")
                signals["Multi_Timeframe"] = None
            
            # Análisis adicional propio
            df = self.get_market_data(symbol, timeframe, limit=100)
            current_price = self.get_current_price(symbol)
            
            if df.empty or current_price == 0:
                return self._create_hold_signal(symbol, "No market data")
            
            # Análisis de patrones de velas
            candlestick_patterns = AdvancedIndicators.detect_candlestick_patterns(df)
            
            # Análisis de momentum (Awesome Oscillator)
            ao_analysis = AdvancedIndicators.awesome_oscillator(df)
            
            # Análisis de volumen
            volume_analysis = self.analyze_volume(df)
            
            # Análisis de tendencia
            trend = self.analyze_trend(df)
            
            # Régimen de mercado
            market_regime = self.detect_market_regime(df)
            
            # Combinar señales usando votación ponderada
            ensemble_result = self._combine_signals(signals, {
                "candlestick": candlestick_patterns,
                "awesome_oscillator": ao_analysis,
                "volume": volume_analysis,
                "trend": trend,
                "market_regime": market_regime
            })
            
            # ATR para stop loss
            atr = ta.atr(df['high'], df['low'], df['close'], length=14)
            current_atr = atr.iloc[-1] if atr is not None else current_price * 0.02
            
            # Calcular stop loss y take profit
            stop_loss, take_profit, risk_reward = self.calculate_risk_reward(
                current_price, ensemble_result["signal_type"], current_atr
            )
            
            # Verificar ratio riesgo/beneficio
            if risk_reward < 2.0 and ensemble_result["signal_type"] != "HOLD":
                ensemble_result["signal_type"] = "HOLD"
                ensemble_result["confidence"] = 40
                ensemble_result["notes"].append("Poor risk/reward ratio")
            
            return EnhancedSignal(
                symbol=symbol,
                strategy_name=self.name,
                signal_type=ensemble_result["signal_type"],
                price=current_price,
                confidence_score=ensemble_result["confidence"],
                strength=self._get_signal_strength(ensemble_result["confidence"]),
                timestamp=datetime.now(),
                indicators_data={
                    "strategy_signals": {k: v.signal_type if v else "ERROR" for k, v in signals.items()},
                    "strategy_confidences": {k: v.confidence_score if v else 0 for k, v in signals.items()},
                    "candlestick_patterns": candlestick_patterns,
                    "awesome_oscillator": ao_analysis,
                    "volume_analysis": volume_analysis,
                    "ensemble_consensus": ensemble_result["consensus"],
                    "weighted_score": ensemble_result["weighted_score"],
                    "timeframe": timeframe
                },
                notes=" | ".join(ensemble_result["notes"]),
                volume_confirmation=bool(volume_analysis.get("volume_confirmation", False)),
                trend_confirmation=str(trend),
                risk_reward_ratio=round(float(risk_reward), 2),
                stop_loss_price=round(float(stop_loss), 2),
                take_profit_price=round(float(take_profit), 2),
                market_regime=str(market_regime),
                confluence_score=int(ensemble_result["confluence_score"])
            )
            
        except Exception as e:
            logger.error(f"Error in Ensemble analysis: {e}")
            return self._create_hold_signal(symbol, f"Error: {str(e)}")
    
    def _combine_signals(self, strategy_signals: Dict, additional_analysis: Dict) -> Dict:
        """Combinar señales usando votación ponderada inteligente"""
        try:
            # Inicializar contadores
            buy_score = 0.0
            sell_score = 0.0
            total_weight = 0.0
            notes = []
            confluence_score = 0
            
            # Procesar señales de estrategias principales
            for strategy_name, signal in strategy_signals.items():
                if signal is None:
                    continue
                    
                weight = self.strategy_weights.get(strategy_name, 0.3)
                confidence_factor = signal.confidence_score / 100.0
                weighted_contribution = weight * confidence_factor
                
                if signal.signal_type == "BUY":
                    buy_score += weighted_contribution
                    confluence_score += 1
                    notes.append(f"{strategy_name}: BUY ({signal.confidence_score:.1f}%)")
                elif signal.signal_type == "SELL":
                    sell_score += weighted_contribution
                    confluence_score += 1
                    notes.append(f"{strategy_name}: SELL ({signal.confidence_score:.1f}%)")
                else:
                    notes.append(f"{strategy_name}: HOLD")
                
                total_weight += weight
            
            # Análisis de patrones de velas (peso menor)
            candlestick_weight = 0.15
            for pattern in additional_analysis["candlestick"]["patterns"]:
                if pattern["signal"] == "BUY":
                    buy_score += candlestick_weight * 0.7
                    notes.append(f"Candlestick: {pattern['name']} (BUY)")
                    confluence_score += 1
                elif pattern["signal"] == "SELL":
                    sell_score += candlestick_weight * 0.7
                    notes.append(f"Candlestick: {pattern['name']} (SELL)")
                    confluence_score += 1
            
            # Awesome Oscillator (peso menor)
            ao_weight = 0.1
            ao_signal = additional_analysis["awesome_oscillator"]["signal"]
            if ao_signal == "BUY":
                buy_score += ao_weight
                notes.append("AO: Bullish momentum")
                confluence_score += 1
            elif ao_signal == "SELL":
                sell_score += ao_weight
                notes.append("AO: Bearish momentum")
                confluence_score += 1
            
            # Confirmación de volumen (boost)
            volume_boost = 1.0
            if additional_analysis["volume"]["volume_confirmation"]:
                volume_boost = 1.2
                notes.append(f"Volume confirms ({additional_analysis['volume']['volume_ratio']}x avg)")
                confluence_score += 1
            
            # Aplicar boost de volumen
            buy_score *= volume_boost
            sell_score *= volume_boost
            
            # Penalización por régimen de mercado
            market_regime = additional_analysis["market_regime"]
            if market_regime == "VOLATILE":
                buy_score *= 0.8
                sell_score *= 0.8
                notes.append("High volatility penalty")
            elif market_regime == "RANGING":
                # En mercados laterales, preferir señales de reversión
                buy_score *= 1.1
                sell_score *= 1.1
                notes.append("Range-bound market boost")
            
            # Determinar señal final
            total_score = buy_score + sell_score
            if total_score == 0:
                consensus = 0.5
                signal_type = "HOLD"
                confidence = 45
            else:
                consensus = max(buy_score, sell_score) / total_score
                
                if buy_score > sell_score and consensus >= self.min_consensus_threshold:
                    signal_type = "BUY"
                    confidence = min(95, 50 + (buy_score * 40))
                elif sell_score > buy_score and consensus >= self.min_consensus_threshold:
                    signal_type = "SELL"
                    confidence = min(95, 50 + (sell_score * 40))
                else:
                    signal_type = "HOLD"
                    confidence = 45
                    notes.append(f"Insufficient consensus ({consensus:.1%})")
            
            # Boost de confianza por consenso alto
            if consensus >= 0.8:
                confidence *= self.confidence_boost_factor
                confidence = min(95, confidence)
                notes.append(f"High consensus boost ({consensus:.1%})")
            
            return {
                "signal_type": signal_type,
                "confidence": round(confidence, 1),
                "consensus": round(consensus, 3),
                "weighted_score": round(total_score, 3),
                "buy_score": round(buy_score, 3),
                "sell_score": round(sell_score, 3),
                "confluence_score": confluence_score,
                "notes": notes
            }
            
        except Exception as e:
            logger.error(f"Error combining signals: {e}")
            return {
                "signal_type": "HOLD",
                "confidence": 0,
                "consensus": 0,
                "weighted_score": 0,
                "buy_score": 0,
                "sell_score": 0,
                "confluence_score": 0,
                "notes": [f"Error combining signals: {str(e)}"]
            }
    
    def _get_signal_strength(self, confidence: float) -> str:
        """Convertir confidence a strength"""
        if confidence >= 90: return "Very Strong"
        elif confidence >= 75: return "Strong"
        elif confidence >= 60: return "Moderate"
        else: return "Weak"
    
    def _create_hold_signal(self, symbol: str, reason: str) -> EnhancedSignal:
        """Crear señal HOLD"""
        return EnhancedSignal(
            symbol=symbol,
            strategy_name=self.name,
            signal_type="HOLD",
            price=0.0,
            confidence_score=0.0,
            strength="None",
            timestamp=datetime.now(),
            indicators_data={},
            notes=f"HOLD: {reason}",
            volume_confirmation=False,
            trend_confirmation="NEUTRAL",
            risk_reward_ratio=0.0,
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            confluence_score=0
        )