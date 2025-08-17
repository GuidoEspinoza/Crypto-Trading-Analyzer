"""
📊 Universal Trading Analyzer - Indicadores Técnicos Avanzados
Biblioteca completa de indicadores profesionales para análisis técnico
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FibonacciLevels:
    """Niveles de Fibonacci para retracements y extensiones"""
    level_0: float      # 0%
    level_236: float    # 23.6%
    level_382: float    # 38.2%
    level_500: float    # 50%
    level_618: float    # 61.8%
    level_786: float    # 78.6%
    level_100: float    # 100%
    
@dataclass
class IchimokuCloud:
    """Componentes del Ichimoku Cloud"""
    tenkan_sen: float        # Línea de conversión
    kijun_sen: float         # Línea base
    senkou_span_a: float     # Nube A
    senkou_span_b: float     # Nube B
    chikou_span: float       # Línea rezagada
    cloud_color: str         # Verde o Roja
    price_position: str      # Arriba/Dentro/Debajo de la nube

class AdvancedIndicators:
    """Clase para calcular indicadores técnicos avanzados"""
    
    @staticmethod
    def safe_float(value, default: float = 0.0) -> float:
        """
        🛡️ Convertir valor a float seguro, manejando NaN e infinitos
        
        Args:
            value: Valor a convertir
            default: Valor por defecto si hay error
            
        Returns:
            Float válido para JSON
        """
        try:
            if pd.isna(value) or np.isinf(value):
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def fibonacci_retracement(df: pd.DataFrame, lookback: int = 50) -> FibonacciLevels:
        """
        🔢 Calcular niveles de Fibonacci para retracements
        
        Args:
            df: DataFrame con datos OHLCV
            lookback: Períodos hacia atrás para encontrar máximo y mínimo
            
        Returns:
            FibonacciLevels con todos los niveles calculados
        """
        # Encontrar máximo y mínimo en el período
        recent_data = df.tail(lookback)
        swing_high = recent_data['high'].max()
        swing_low = recent_data['low'].min()
        
        # Calcular diferencia
        diff = swing_high - swing_low
        
        # Calcular niveles de Fibonacci (retracement desde el máximo)
        return FibonacciLevels(
            level_0=AdvancedIndicators.safe_float(swing_high),
            level_236=AdvancedIndicators.safe_float(swing_high - (diff * 0.236)),
            level_382=AdvancedIndicators.safe_float(swing_high - (diff * 0.382)),
            level_500=AdvancedIndicators.safe_float(swing_high - (diff * 0.500)),
            level_618=AdvancedIndicators.safe_float(swing_high - (diff * 0.618)),
            level_786=AdvancedIndicators.safe_float(swing_high - (diff * 0.786)),
            level_100=AdvancedIndicators.safe_float(swing_low)
        )
    
    @staticmethod
    def ichimoku_cloud(df: pd.DataFrame) -> IchimokuCloud:
        """
        ☁️ Calcular Ichimoku Cloud completo
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            IchimokuCloud con todos los componentes
        """
        # Calcular Ichimoku usando pandas-ta
        try:
            # Método 1: Usar ichimoku directamente
            ichimoku_data = ta.ichimoku(df['high'], df['low'], df['close'])
            
            if ichimoku_data is None or ichimoku_data.empty:
                raise ValueError("No se pudieron calcular los datos de Ichimoku")
            
            # Obtener valores más recientes
            latest_idx = -1
            while pd.isna(ichimoku_data.iloc[latest_idx].iloc[0]) and abs(latest_idx) < len(ichimoku_data):
                latest_idx -= 1
            
            latest = ichimoku_data.iloc[latest_idx]
            current_price = df['close'].iloc[latest_idx]
            
            # Extraer componentes (los nombres pueden variar)
            columns = ichimoku_data.columns.tolist()
            
            tenkan_sen = latest[columns[0]]  # Generalmente ITS_9
            kijun_sen = latest[columns[1]]   # Generalmente IKS_26
            senkou_a = latest[columns[2]]    # Generalmente ISA_9
            senkou_b = latest[columns[3]]    # Generalmente ISB_26
            chikou_span = latest[columns[4]] # Generalmente ICS_26
            
        except Exception:
            # Método 2: Calcular manualmente si falla el método automático
            # Tenkan-sen (9 períodos)
            high_9 = df['high'].rolling(window=9).max()
            low_9 = df['low'].rolling(window=9).min()
            tenkan_sen = (high_9 + low_9) / 2
            
            # Kijun-sen (26 períodos)
            high_26 = df['high'].rolling(window=26).max()
            low_26 = df['low'].rolling(window=26).min()
            kijun_sen = (high_26 + low_26) / 2
            
            # Senkou Span A
            senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
            
            # Senkou Span B (52 períodos)
            high_52 = df['high'].rolling(window=52).max()
            low_52 = df['low'].rolling(window=52).min()
            senkou_b = ((high_52 + low_52) / 2).shift(26)
            
            # Chikou Span
            chikou_span = df['close'].shift(-26)
            
            # Obtener valores actuales
            tenkan_sen = tenkan_sen.iloc[-1]
            kijun_sen = kijun_sen.iloc[-1]
            senkou_a = senkou_a.iloc[-1] if not pd.isna(senkou_a.iloc[-1]) else senkou_a.dropna().iloc[-1] if not senkou_a.dropna().empty else 0
            senkou_b = senkou_b.iloc[-1] if not pd.isna(senkou_b.iloc[-1]) else senkou_b.dropna().iloc[-1] if not senkou_b.dropna().empty else 0
            chikou_span = chikou_span.iloc[-1] if not pd.isna(chikou_span.iloc[-1]) else df['close'].iloc[-1]
            current_price = df['close'].iloc[-1]
        
        # Usar safe_float para todos los valores
        tenkan_sen = AdvancedIndicators.safe_float(tenkan_sen)
        kijun_sen = AdvancedIndicators.safe_float(kijun_sen)
        senkou_a = AdvancedIndicators.safe_float(senkou_a)
        senkou_b = AdvancedIndicators.safe_float(senkou_b)
        chikou_span = AdvancedIndicators.safe_float(chikou_span)
        
        # Determinar color de la nube
        cloud_color = "Verde" if senkou_a > senkou_b else "Roja"
        
        # Determinar posición del precio respecto a la nube
        cloud_top = max(senkou_a, senkou_b)
        cloud_bottom = min(senkou_a, senkou_b)
        current_price = AdvancedIndicators.safe_float(current_price)
        
        if current_price > cloud_top:
            price_position = "Arriba de la nube (Alcista)"
        elif current_price < cloud_bottom:
            price_position = "Debajo de la nube (Bajista)"
        else:
            price_position = "Dentro de la nube (Neutral)"
        
        return IchimokuCloud(
            tenkan_sen=tenkan_sen,
            kijun_sen=kijun_sen,
            senkou_span_a=senkou_a,
            senkou_span_b=senkou_b,
            chikou_span=chikou_span,
            cloud_color=cloud_color,
            price_position=price_position
        )
    
    @staticmethod
    def stochastic_oscillator(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict:
        """
        📊 Calcular Oscilador Estocástico
        
        Args:
            df: DataFrame con datos OHLCV
            k_period: Período para %K
            d_period: Período para %D (media móvil de %K)
            
        Returns:
            Diccionario con valores y señales del estocástico
        """
        try:
            stoch_data = ta.stoch(df['high'], df['low'], df['close'], k=k_period, d=d_period)
            
            if stoch_data is None or stoch_data.empty:
                # Calcular manualmente
                lowest_low = df['low'].rolling(window=k_period).min()
                highest_high = df['high'].rolling(window=k_period).max()
                k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
                d_percent = k_percent.rolling(window=d_period).mean()
                
                k_current = k_percent.iloc[-1]
                d_current = d_percent.iloc[-1]
            else:
                # Usar pandas-ta
                columns = stoch_data.columns.tolist()
                k_current = stoch_data[columns[0]].iloc[-1]
                d_current = stoch_data[columns[1]].iloc[-1]
            
            # Usar safe_float para evitar NaN
            k_current = AdvancedIndicators.safe_float(k_current, 50.0)
            d_current = AdvancedIndicators.safe_float(d_current, 50.0)
            
            # Generar señales
            if k_current <= 20 and d_current <= 20:
                signal = "BUY"
                interpretation = "🟢 Zona de sobrecompra - Posible rebote"
            elif k_current >= 80 and d_current >= 80:
                signal = "SELL"
                interpretation = "🔴 Zona de sobreventa - Posible corrección"
            elif k_current > d_current:
                signal = "BUY"
                interpretation = "📈 %K cruza por encima de %D - Momentum alcista"
            elif k_current < d_current:
                signal = "SELL"
                interpretation = "📉 %K cruza por debajo de %D - Momentum bajista"
            else:
                signal = "HOLD"
                interpretation = "⚪ Sin señal clara"
            
            return {
                "k_percent": round(k_current, 2),
                "d_percent": round(d_current, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "k_percent": 50.0,
                "d_percent": 50.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando estocástico: {str(e)}"
            }
    
    @staticmethod
    def williams_percent_r(df: pd.DataFrame, period: int = 14) -> Dict:
        """
        📊 Calcular Williams %R
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período para el cálculo
            
        Returns:
            Diccionario con valor y señales de Williams %R
        """
        try:
            willr = ta.willr(df['high'], df['low'], df['close'], length=period)
            
            if willr is None or willr.empty:
                # Calcular manualmente
                highest_high = df['high'].rolling(window=period).max()
                lowest_low = df['low'].rolling(window=period).min()
                willr = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
            
            current_willr = AdvancedIndicators.safe_float(willr.iloc[-1], -50.0)
            
            # Generar señales (Williams %R se mueve entre -100 y 0)
            if current_willr <= -80:
                signal = "BUY"
                interpretation = "🟢 Zona de sobrecompra (-80 a -100) - Posible rebote"
            elif current_willr >= -20:
                signal = "SELL"
                interpretation = "🔴 Zona de sobreventa (-20 a 0) - Posible corrección"
            else:
                signal = "HOLD"
                interpretation = "⚪ Rango medio - Sin señal clara"
            
            return {
                "williams_r": round(current_willr, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "williams_r": -50.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando Williams %R: {str(e)}"
            }
    
    @staticmethod
    def awesome_oscillator(df: pd.DataFrame) -> Dict:
        """
        🌊 Calcular Awesome Oscillator (AO)
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            Diccionario con valor y señales del AO
        """
        try:
            ao = ta.ao(df['high'], df['low'])
            
            if ao is None or ao.empty:
                # Calcular manualmente
                median_price = (df['high'] + df['low']) / 2
                sma_5 = median_price.rolling(window=5).mean()
                sma_34 = median_price.rolling(window=34).mean()
                ao = sma_5 - sma_34
            
            current_ao = AdvancedIndicators.safe_float(ao.iloc[-1], 0.0)
            previous_ao = AdvancedIndicators.safe_float(ao.iloc[-2], 0.0)
            
            # Generar señales basadas en cambio de momentum
            if current_ao > 0 and previous_ao <= 0:
                signal = "BUY"
                interpretation = "🟢 Cruce por encima de cero - Momentum alcista"
            elif current_ao < 0 and previous_ao >= 0:
                signal = "SELL"
                interpretation = "🔴 Cruce por debajo de cero - Momentum bajista"
            elif current_ao > previous_ao:
                signal = "BUY"
                interpretation = "📈 AO creciente - Fortalecimiento del momentum"
            elif current_ao < previous_ao:
                signal = "SELL"
                interpretation = "📉 AO decreciente - Debilitamiento del momentum"
            else:
                signal = "HOLD"
                interpretation = "⚪ AO estable - Sin cambio de momentum"
            
            return {
                "awesome_oscillator": round(current_ao, 6),
                "previous_ao": round(previous_ao, 6),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "awesome_oscillator": 0.0,
                "previous_ao": 0.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando AO: {str(e)}"
            }
    
    @staticmethod
    def commodity_channel_index(df: pd.DataFrame, period: int = 20) -> Dict:
        """
        📊 Calcular Commodity Channel Index (CCI)
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período para el cálculo
            
        Returns:
            Diccionario con valor y señales del CCI
        """
        try:
            cci = ta.cci(df['high'], df['low'], df['close'], length=period)
            
            if cci is None or cci.empty:
                # Calcular manualmente
                typical_price = (df['high'] + df['low'] + df['close']) / 3
                sma_tp = typical_price.rolling(window=period).mean()
                mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
                cci = (typical_price - sma_tp) / (0.015 * mad)
            
            current_cci = AdvancedIndicators.safe_float(cci.iloc[-1], 0.0)
            
            # Generar señales basadas en niveles del CCI
            if current_cci > 100:
                signal = "SELL"
                interpretation = "🔴 CCI > +100 - Sobrecomprado, posible corrección"
            elif current_cci < -100:
                signal = "BUY"
                interpretation = "🟢 CCI < -100 - Sobrevendido, posible rebote"
            elif current_cci > 0:
                signal = "BUY"
                interpretation = "📈 CCI positivo - Tendencia alcista"
            else:
                signal = "SELL"
                interpretation = "📉 CCI negativo - Tendencia bajista"
            
            return {
                "cci": round(current_cci, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "cci": 0.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando CCI: {str(e)}"
            }
    
    @staticmethod
    def parabolic_sar(df: pd.DataFrame) -> Dict:
        """
        🎯 Calcular Parabolic SAR
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            Diccionario con valor y señales del Parabolic SAR
        """
        try:
            psar = ta.psar(df['high'], df['low'], df['close'])
            
            if psar is None or psar.empty:
                # Implementación básica manual
                # Para simplicidad, usamos una aproximación
                current_price = df['close'].iloc[-1]
                high_20 = df['high'].rolling(window=20).max().iloc[-1]
                low_20 = df['low'].rolling(window=20).min().iloc[-1]
                
                # SAR aproximado basado en tendencia reciente
                if current_price > (high_20 + low_20) / 2:
                    current_psar = low_20 * 0.98  # Tendencia alcista
                else:
                    current_psar = high_20 * 1.02  # Tendencia bajista
            else:
                # Usar pandas-ta
                if isinstance(psar, pd.DataFrame):
                    current_psar = psar.iloc[-1, 0]
                else:
                    current_psar = psar.iloc[-1]
            
            current_price = AdvancedIndicators.safe_float(df['close'].iloc[-1])
            current_psar = AdvancedIndicators.safe_float(current_psar, current_price * 0.99)
            
            # El Parabolic SAR da señales de cambio de tendencia
            if current_price > current_psar:
                signal = "BUY"
                interpretation = "🟢 Precio por encima del SAR - Tendencia alcista"
            else:
                signal = "SELL"
                interpretation = "🔴 Precio por debajo del SAR - Tendencia bajista"
            
            return {
                "psar": round(current_psar, 2),
                "current_price": round(current_price, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            current_price = AdvancedIndicators.safe_float(df['close'].iloc[-1])
            return {
                "psar": round(current_price * 0.99, 2),
                "current_price": round(current_price, 2),
                "signal": "HOLD",
                "interpretation": f"Error calculando PSAR: {str(e)}"
            }
    
    @staticmethod
    def detect_candlestick_patterns(df: pd.DataFrame) -> Dict:
        """
        🕯️ Detectar patrones de velas japonesas
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            Diccionario con patrones detectados
        """
        try:
            # Obtener últimas 3 velas para patrones
            recent = df.tail(3)
            latest = recent.iloc[-1]
            
            # Calcular tamaños de cuerpos y sombras
            body_size = abs(latest['close'] - latest['open'])
            upper_shadow = latest['high'] - max(latest['open'], latest['close'])
            lower_shadow = min(latest['open'], latest['close']) - latest['low']
            total_range = latest['high'] - latest['low']
            
            detected_patterns = []
            
            # Evitar división por cero
            if total_range == 0:
                total_range = 0.01
            
            # Doji
            if body_size < (total_range * 0.1):
                detected_patterns.append({
                    "name": "Doji",
                    "signal": "NEUTRAL",
                    "description": "⚪ Indecisión en el mercado - Posible cambio de tendencia"
                })
            
            # Martillo (Hammer)
            if (lower_shadow > body_size * 2 and 
                upper_shadow < body_size * 0.5 and 
                latest['close'] > latest['open']):
                detected_patterns.append({
                    "name": "Martillo",
                    "signal": "BUY",
                    "description": "🔨 Patrón de reversión alcista - Rechazo de precios bajos"
                })
            
            # Estrella fugaz (Shooting Star)
            if (upper_shadow > body_size * 2 and 
                lower_shadow < body_size * 0.5 and 
                latest['close'] < latest['open']):
                detected_patterns.append({
                    "name": "Estrella Fugaz",
                    "signal": "SELL",
                    "description": "💫 Patrón de reversión bajista - Rechazo de precios altos"
                })
            
            # Engulfing alcista
            if len(recent) >= 2:
                prev = recent.iloc[-2]
                if (prev['close'] < prev['open'] and  # Vela anterior bajista
                    latest['close'] > latest['open'] and  # Vela actual alcista
                    latest['open'] < prev['close'] and  # Abre por debajo del cierre anterior
                    latest['close'] > prev['open']):  # Cierra por encima de la apertura anterior
                    detected_patterns.append({
                        "name": "Envolvente Alcista",
                        "signal": "BUY",
                        "description": "🟢 Patrón de reversión alcista fuerte - Absorción de venta"
                    })
            
            return {
                "patterns_detected": len(detected_patterns),
                "patterns": detected_patterns if detected_patterns else [{"name": "Ninguno", "signal": "NEUTRAL", "description": "No se detectaron patrones relevantes"}]
            }
            
        except Exception as e:
            return {
                "patterns_detected": 0,
                "patterns": [{"name": "Error", "signal": "NEUTRAL", "description": f"Error detectando patrones: {str(e)}"}]
            }