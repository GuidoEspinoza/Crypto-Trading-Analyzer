"""
📊 Universal Trading Analyzer - Indicadores Técnicos Avanzados
Biblioteca completa de indicadores profesionales para análisis técnico
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
import warnings
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
import hashlib

# Importar configuración centralizada
from src.config.config import AdvancedIndicatorsConfig

# Suprimir warnings específicos de pandas_ta
warnings.filterwarnings('ignore', message='.*dtype incompatible.*')
warnings.filterwarnings('ignore', category=UserWarning, module='pandas_ta')

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
    """Clase para calcular indicadores técnicos avanzados con optimizaciones"""
    
    # Cache para resultados de indicadores
    _indicator_cache = {}
    _cache_max_size = 1000
    
    @classmethod
    def _get_cache_key(cls, df: pd.DataFrame, indicator_name: str, **kwargs) -> str:
        """🔑 Generar clave de cache basada en datos y parámetros"""
        try:
            # Usar hash de los últimos valores para identificar el dataset
            last_values = f"{df['close'].iloc[-1]}_{df['volume'].iloc[-1]}_{len(df)}"
            params_str = "_".join([f"{k}_{v}" for k, v in sorted(kwargs.items())])
            cache_key = f"{indicator_name}_{last_values}_{params_str}"
            return hashlib.md5(cache_key.encode()).hexdigest()[:16]
        except:
            return f"{indicator_name}_{id(df)}"
    
    @classmethod
    def _get_from_cache(cls, cache_key: str):
        """📦 Obtener resultado del cache"""
        return cls._indicator_cache.get(cache_key)
    
    @classmethod
    def _store_in_cache(cls, cache_key: str, result):
        """💾 Almacenar resultado en cache"""
        if len(cls._indicator_cache) >= cls._cache_max_size:
            # Limpiar cache más antiguo (FIFO simple)
            oldest_key = next(iter(cls._indicator_cache))
            del cls._indicator_cache[oldest_key]
        cls._indicator_cache[cache_key] = result
    
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
    def fibonacci_retracement(df: pd.DataFrame, lookback: int = None) -> FibonacciLevels:
        """
        🔢 Calcular niveles de Fibonacci para retracements
        
        Args:
            df: DataFrame con datos OHLCV
            lookback: Períodos hacia atrás para encontrar máximo y mínimo
            
        Returns:
            FibonacciLevels con todos los niveles calculados
        """
        if lookback is None:
            lookback = AdvancedIndicatorsConfig.FIBONACCI_LOOKBACK
        
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
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                ichimoku_data = ta.ichimoku(high_float, low_float, close_float)
            
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
            high_9 = df['high'].rolling(window=AdvancedIndicatorsConfig.ICHIMOKU_TENKAN_PERIOD).max()
            low_9 = df['low'].rolling(window=AdvancedIndicatorsConfig.ICHIMOKU_TENKAN_PERIOD).min()
            tenkan_sen = (high_9 + low_9) / 2
            
            # Kijun-sen (26 períodos)
            high_26 = df['high'].rolling(window=AdvancedIndicatorsConfig.ICHIMOKU_KIJUN_PERIOD).max()
            low_26 = df['low'].rolling(window=AdvancedIndicatorsConfig.ICHIMOKU_KIJUN_PERIOD).min()
            kijun_sen = (high_26 + low_26) / 2
            
            # Senkou Span A
            senkou_a = ((tenkan_sen + kijun_sen) / 2).shift(AdvancedIndicatorsConfig.ICHIMOKU_SHIFT)
            
            # Senkou Span B (52 períodos)
            high_52 = df['high'].rolling(window=AdvancedIndicatorsConfig.ICHIMOKU_SENKOU_B_PERIOD).max()
            low_52 = df['low'].rolling(window=AdvancedIndicatorsConfig.ICHIMOKU_SENKOU_B_PERIOD).min()
            senkou_b = ((high_52 + low_52) / 2).shift(AdvancedIndicatorsConfig.ICHIMOKU_SHIFT)
            
            # Chikou Span
            chikou_span = df['close'].shift(-AdvancedIndicatorsConfig.ICHIMOKU_SHIFT)
            
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
    def stochastic_oscillator(df: pd.DataFrame, k_period: int = None, d_period: int = None) -> Dict:
        """
        📊 Calcular Oscilador Estocástico
        
        Args:
            df: DataFrame con datos OHLCV
            k_period: Período para %K
            d_period: Período para %D (media móvil de %K)
            
        Returns:
            Diccionario con valores y señales del estocástico
        """
        if k_period is None:
            k_period = AdvancedIndicatorsConfig.STOCHASTIC_K_PERIOD
        if d_period is None:
            d_period = AdvancedIndicatorsConfig.STOCHASTIC_D_PERIOD
            
        try:
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                stoch_data = ta.stoch(high_float, low_float, close_float, k=k_period, d=d_period)
            
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
    def williams_percent_r(df: pd.DataFrame, period: int = None) -> Dict:
        """
        📊 Calcular Williams %R
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período de cálculo
            
        Returns:
            Diccionario con valores y señales de Williams %R
        """
        if period is None:
            period = AdvancedIndicatorsConfig.WILLIAMS_R_PERIOD
            
        try:
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                willr = ta.willr(high_float, low_float, close_float, length=period)
            
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
    def commodity_channel_index(df: pd.DataFrame, period: int = None) -> Dict:
        """
        📊 Calcular Commodity Channel Index (CCI)
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período de cálculo
            
        Returns:
            Diccionario con valores y señales del CCI
        """
        if period is None:
            period = AdvancedIndicatorsConfig.CCI_PERIOD
            
        try:
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                cci = ta.cci(high_float, low_float, close_float, length=period)
            
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
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                psar = ta.psar(high_float, low_float, close_float)
            
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
    
    @classmethod
    def bollinger_bands(cls, df: pd.DataFrame, period: int = None, std_dev: float = None) -> Dict:
        """
        📊 Calcular Bandas de Bollinger (optimizado con cache)
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período para la media móvil
            std_dev: Desviaciones estándar para las bandas
            
        Returns:
            Diccionario con bandas y señales
        """
        if period is None:
            period = AdvancedIndicatorsConfig.BOLLINGER_PERIOD
        if std_dev is None:
            std_dev = AdvancedIndicatorsConfig.BOLLINGER_STD_DEV
            
        # Verificar cache
        cache_key = cls._get_cache_key(df, 'bollinger_bands', period=period, std_dev=std_dev)
        cached_result = cls._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        try:
            # Optimización: usar cálculo manual para datasets pequeños
            if len(df) < 100:
                sma = df['close'].rolling(window=period).mean()
                std = df['close'].rolling(window=period).std()
                upper_band = sma + (std * std_dev)
                lower_band = sma - (std * std_dev)
                middle_band = sma
            else:
                bb = ta.bbands(df['close'], length=period, std=std_dev)
                
                if bb is None or bb.empty:
                    # Fallback a cálculo manual
                    sma = df['close'].rolling(window=period).mean()
                    std = df['close'].rolling(window=period).std()
                    upper_band = sma + (std * std_dev)
                    lower_band = sma - (std * std_dev)
                    middle_band = sma
                else:
                    # Usar pandas-ta
                    columns = bb.columns.tolist()
                    upper_band = bb[columns[0]]  # BBU
                    middle_band = bb[columns[1]]  # BBM
                    lower_band = bb[columns[2]]  # BBL
            
            current_price = df['close'].iloc[-1]
            current_upper = cls.safe_float(upper_band.iloc[-1])
            current_middle = cls.safe_float(middle_band.iloc[-1])
            current_lower = cls.safe_float(lower_band.iloc[-1])
            
            # Calcular posición del precio en las bandas (0-100%)
            if current_upper != current_lower:
                bb_position = ((current_price - current_lower) / (current_upper - current_lower)) * 100
            else:
                bb_position = 50.0
            
            # Generar señales
            if current_price <= current_lower:
                signal = "BUY"
                interpretation = "🟢 Precio toca banda inferior - Posible rebote"
            elif current_price >= current_upper:
                signal = "SELL"
                interpretation = "🔴 Precio toca banda superior - Posible corrección"
            elif bb_position < 20:
                signal = "BUY"
                interpretation = "📈 Precio cerca de banda inferior - Zona de compra"
            elif bb_position > 80:
                signal = "SELL"
                interpretation = "📉 Precio cerca de banda superior - Zona de venta"
            else:
                signal = "HOLD"
                interpretation = "⚪ Precio en rango medio de las bandas"
            
            # Calcular ancho de las bandas (volatilidad)
            band_width = ((current_upper - current_lower) / current_middle) * 100
            
            result = {
                "upper_band": round(current_upper, 2),
                "middle_band": round(current_middle, 2),
                "lower_band": round(current_lower, 2),
                "bb_position": round(bb_position, 1),
                "band_width": round(band_width, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
            # Almacenar en cache
            cls._store_in_cache(cache_key, result)
            return result
            
        except Exception as e:
            current_price = cls.safe_float(df['close'].iloc[-1])
            return {
                "upper_band": current_price * 1.02,
                "middle_band": current_price,
                "lower_band": current_price * 0.98,
                "bb_position": 50.0,
                "band_width": 4.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando Bollinger Bands: {str(e)}"
            }
    
    @classmethod
    def vwap(cls, df: pd.DataFrame) -> Dict:
        """
        📊 Calcular Volume Weighted Average Price (VWAP) (optimizado con cache)
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            Diccionario con VWAP y señales
        """
        # Verificar cache
        cache_key = cls._get_cache_key(df, 'vwap')
        cached_result = cls._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        try:
            # Optimización: usar cálculo manual para datasets pequeños
            if len(df) < 100:
                typical_price = (df['high'] + df['low'] + df['close']) / 3
                vwap_data = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            else:
                # Convertir a float64 para evitar warnings de dtype
                high_float = df['high'].astype('float64')
                low_float = df['low'].astype('float64')
                close_float = df['close'].astype('float64')
                volume_float = df['volume'].astype('float64')
                
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', FutureWarning)
                    warnings.simplefilter('ignore', UserWarning)
                    vwap_data = ta.vwap(high_float, low_float, close_float, volume_float)
                
                if vwap_data is None or vwap_data.empty:
                    # Fallback a cálculo manual
                    typical_price = (df['high'] + df['low'] + df['close']) / 3
                    vwap_data = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
            
            current_vwap = cls.safe_float(vwap_data.iloc[-1])
            current_price = cls.safe_float(df['close'].iloc[-1])
            
            # Calcular desviación del VWAP
            vwap_deviation = ((current_price - current_vwap) / current_vwap) * 100
            
            # Generar señales
            if current_price > current_vwap:
                signal = "BUY"
                interpretation = "🟢 Precio por encima del VWAP - Momentum alcista"
            elif current_price < current_vwap:
                signal = "SELL"
                interpretation = "🔴 Precio por debajo del VWAP - Momentum bajista"
            else:
                signal = "HOLD"
                interpretation = "⚪ Precio en línea con VWAP"
            
            result = {
                "vwap": round(current_vwap, 2),
                "current_price": round(current_price, 2),
                "deviation_percent": round(vwap_deviation, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
            # Almacenar en cache
            cls._store_in_cache(cache_key, result)
            return result
            
        except Exception as e:
            current_price = cls.safe_float(df['close'].iloc[-1])
            return {
                "vwap": current_price,
                "current_price": current_price,
                "deviation_percent": 0.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando VWAP: {str(e)}"
            }
    
    @staticmethod
    def on_balance_volume(df: pd.DataFrame) -> Dict:
        """
        📊 Calcular On Balance Volume (OBV)
        
        Args:
            df: DataFrame con datos OHLCV
            
        Returns:
            Diccionario con OBV y señales
        """
        try:
            # Convertir a float64 para evitar warnings de dtype
            close_float = df['close'].astype('float64')
            volume_float = df['volume'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                obv = ta.obv(close_float, volume_float)
            
            if obv is None or obv.empty:
                # Calcular manualmente
                obv = pd.Series(index=df.index, dtype=float)
                obv.iloc[0] = df['volume'].iloc[0]
                
                for i in range(1, len(df)):
                    if df['close'].iloc[i] > df['close'].iloc[i-1]:
                        obv.iloc[i] = obv.iloc[i-1] + df['volume'].iloc[i]
                    elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                        obv.iloc[i] = obv.iloc[i-1] - df['volume'].iloc[i]
                    else:
                        obv.iloc[i] = obv.iloc[i-1]
            
            current_obv = AdvancedIndicators.safe_float(obv.iloc[-1])
            previous_obv = AdvancedIndicators.safe_float(obv.iloc[-2])
            
            # Calcular OBV SMA para tendencia
            obv_sma = obv.rolling(window=20).mean()
            current_obv_sma = AdvancedIndicators.safe_float(obv_sma.iloc[-1])
            
            # Generar señales basadas en tendencia del OBV
            if current_obv > current_obv_sma and current_obv > previous_obv:
                signal = "BUY"
                interpretation = "🟢 OBV creciente - Acumulación de volumen"
            elif current_obv < current_obv_sma and current_obv < previous_obv:
                signal = "SELL"
                interpretation = "🔴 OBV decreciente - Distribución de volumen"
            else:
                signal = "HOLD"
                interpretation = "⚪ OBV neutral - Sin tendencia clara de volumen"
            
            return {
                "obv": round(current_obv, 0),
                "obv_sma": round(current_obv_sma, 0),
                "obv_change": round(current_obv - previous_obv, 0),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "obv": 0.0,
                "obv_sma": 0.0,
                "obv_change": 0.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando OBV: {str(e)}"
            }
    
    @staticmethod
    def money_flow_index(df: pd.DataFrame, period: int = None) -> Dict:
        """
        💰 Calcular Money Flow Index (MFI)
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período de cálculo
            
        Returns:
            Diccionario con valores y señales del MFI
        """
        if period is None:
            period = AdvancedIndicatorsConfig.MFI_PERIOD
            
        try:
            # Crear una copia del DataFrame con tipos explícitos para evitar warnings de dtype
            df_copy = df[['high', 'low', 'close', 'volume']].copy()
            high_float = df_copy['high'].astype('float64', copy=False)
            low_float = df_copy['low'].astype('float64', copy=False)
            close_float = df_copy['close'].astype('float64', copy=False)
            volume_float = df_copy['volume'].astype('float64', copy=False)
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                mfi = ta.mfi(high_float, low_float, close_float, volume_float, length=period)
            
            if mfi is None or mfi.empty:
                # Calcular manualmente
                typical_price = (df['high'] + df['low'] + df['close']) / 3
                money_flow = typical_price * df['volume']
                
                positive_flow = pd.Series(index=df.index, dtype=float)
                negative_flow = pd.Series(index=df.index, dtype=float)
                
                for i in range(1, len(df)):
                    if typical_price.iloc[i] > typical_price.iloc[i-1]:
                        positive_flow.iloc[i] = money_flow.iloc[i]
                        negative_flow.iloc[i] = 0
                    elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                        positive_flow.iloc[i] = 0
                        negative_flow.iloc[i] = money_flow.iloc[i]
                    else:
                        positive_flow.iloc[i] = 0
                        negative_flow.iloc[i] = 0
                
                positive_flow_sum = positive_flow.rolling(window=period).sum()
                negative_flow_sum = negative_flow.rolling(window=period).sum()
                
                money_ratio = positive_flow_sum / negative_flow_sum
                mfi = 100 - (100 / (1 + money_ratio))
            
            current_mfi = AdvancedIndicators.safe_float(mfi.iloc[-1], 50.0)
            
            # Generar señales
            if current_mfi <= 20:
                signal = "BUY"
                interpretation = "🟢 MFI oversold (<20) - Posible rebote"
            elif current_mfi >= 80:
                signal = "SELL"
                interpretation = "🔴 MFI overbought (>80) - Posible corrección"
            elif current_mfi < 40:
                signal = "BUY"
                interpretation = "📈 MFI bajo - Presión de compra"
            elif current_mfi > 60:
                signal = "SELL"
                interpretation = "📉 MFI alto - Presión de venta"
            else:
                signal = "HOLD"
                interpretation = "⚪ MFI neutral"
            
            return {
                "mfi": round(current_mfi, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "mfi": 50.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando MFI: {str(e)}"
            }
    
    @staticmethod
    def average_true_range(df: pd.DataFrame, period: int = None) -> Dict:
        """
        📊 Calcular Average True Range (ATR) - Medida de volatilidad
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período para el cálculo
            
        Returns:
            Diccionario con ATR y análisis de volatilidad
        """
        if period is None:
            period = AdvancedIndicatorsConfig.ATR_PERIOD
            
        try:
            # Convertir a float64 para evitar warnings de dtype
            high_float = df['high'].astype('float64')
            low_float = df['low'].astype('float64')
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                atr = ta.atr(high_float, low_float, close_float, length=period)
            
            if atr is None or atr.empty:
                # Calcular manualmente
                high_low = df['high'] - df['low']
                high_close_prev = abs(df['high'] - df['close'].shift(1))
                low_close_prev = abs(df['low'] - df['close'].shift(1))
                
                true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
                atr = true_range.rolling(window=period).mean()
            
            current_atr = AdvancedIndicators.safe_float(atr.iloc[-1])
            current_price = AdvancedIndicators.safe_float(df['close'].iloc[-1])
            
            # Calcular ATR como porcentaje del precio
            atr_percentage = (current_atr / current_price) * 100
            
            # Calcular ATR promedio de los últimos 50 períodos para comparación
            atr_avg = atr.tail(50).mean()
            atr_ratio = current_atr / atr_avg if atr_avg > 0 else 1.0
            
            # Interpretar volatilidad
            if atr_percentage > 5.0:
                volatility_level = "MUY ALTA"
                interpretation = "🔴 Volatilidad extrema - Alto riesgo"
            elif atr_percentage > 3.0:
                volatility_level = "ALTA"
                interpretation = "🟠 Volatilidad alta - Precaución"
            elif atr_percentage > 1.5:
                volatility_level = "MEDIA"
                interpretation = "🟡 Volatilidad normal"
            else:
                volatility_level = "BAJA"
                interpretation = "🟢 Volatilidad baja - Mercado estable"
            
            return {
                "atr": round(current_atr, 4),
                "atr_percentage": round(atr_percentage, 2),
                "atr_ratio": round(atr_ratio, 2),
                "volatility_level": volatility_level,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "atr": 0.0,
                "atr_percentage": 1.0,
                "atr_ratio": 1.0,
                "volatility_level": "DESCONOCIDA",
                "interpretation": f"Error calculando ATR: {str(e)}"
            }
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> Dict:
        """
        📊 Calcular RSI básico (método de compatibilidad)
        
        Args:
            df: DataFrame con datos OHLCV o Series de precios
            period: Período para el cálculo (default: 14)
            
        Returns:
            Diccionario con RSI calculado
        """
        # Si se pasa una Series en lugar de DataFrame
        if isinstance(df, pd.Series):
            close_prices = df
        else:
            close_prices = df['close']
            
        try:
            # Convertir a float64 para evitar warnings de dtype
            close_float = close_prices.astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                rsi = ta.rsi(close_float, length=period)
            
            if rsi is None or rsi.empty:
                # Calcular manualmente
                delta = close_prices.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
            
            current_rsi = AdvancedIndicators.safe_float(rsi.iloc[-1], 50.0)
            
            return {
                "rsi": current_rsi,
                "signal": "BUY" if current_rsi < 30 else "SELL" if current_rsi > 70 else "HOLD",
                "interpretation": f"RSI: {current_rsi:.2f}"
            }
            
        except Exception as e:
            return {
                "rsi": 50.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando RSI: {str(e)}"
            }
    
    @classmethod
    def enhanced_rsi(cls, df: pd.DataFrame, period: int = None) -> Dict:
        """
        📊 RSI Mejorado con análisis de divergencias (optimizado con cache)
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período para el cálculo
            
        Returns:
            Diccionario con RSI mejorado y análisis
        """
        if period is None:
            period = AdvancedIndicatorsConfig.RSI_PERIOD
            
        # Verificar cache
        cache_key = cls._get_cache_key(df, 'enhanced_rsi', period=period)
        cached_result = cls._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        try:
            # Optimización: usar cálculo manual para datasets pequeños
            if len(df) < 100:
                delta = df['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
            else:
                # Convertir a float64 para evitar warnings de dtype
                close_float = df['close'].astype('float64')
                
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', FutureWarning)
                    warnings.simplefilter('ignore', UserWarning)
                    rsi = ta.rsi(close_float, length=period)
                
                if rsi is None or rsi.empty:
                    # Fallback a cálculo manual
                    delta = df['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs))
            
            current_rsi = cls.safe_float(rsi.iloc[-1], 50.0)
            
            # Calcular RSI de diferentes períodos para confirmación
            # Convertir a float64 para evitar warnings de dtype
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                rsi_fast = ta.rsi(close_float, length=7)
                rsi_slow = ta.rsi(close_float, length=21)
            
            current_rsi_fast = cls.safe_float(rsi_fast.iloc[-1] if rsi_fast is not None else current_rsi, current_rsi)
            current_rsi_slow = cls.safe_float(rsi_slow.iloc[-1] if rsi_slow is not None else current_rsi, current_rsi)
            
            # Detectar divergencias (simplificado)
            price_trend = "UP" if df['close'].iloc[-1] > df['close'].iloc[-5] else "DOWN"
            rsi_trend = "UP" if current_rsi > rsi.iloc[-5] else "DOWN"
            
            divergence = "BULLISH" if price_trend == "DOWN" and rsi_trend == "UP" else \
                        "BEARISH" if price_trend == "UP" and rsi_trend == "DOWN" else "NONE"
            
            # Obtener umbrales configurables
            from src.config.config import TradingProfiles, TRADING_PROFILE
            config = TradingProfiles.PROFILES[TRADING_PROFILE]
            rsi_oversold = config.get('rsi_oversold', 30)
            rsi_overbought = config.get('rsi_overbought', 70)
            
            # Generar señales mejoradas con umbrales configurables
            if current_rsi <= (rsi_oversold - 10):  # Extremadamente oversold
                signal = "STRONG_BUY"
                interpretation = f"🟢 RSI extremadamente oversold ({current_rsi:.1f} <= {rsi_oversold-10}) - Fuerte señal de compra"
            elif current_rsi <= rsi_oversold:
                signal = "BUY"
                interpretation = f"📈 RSI oversold ({current_rsi:.1f} <= {rsi_oversold}) - Señal de compra"
            elif current_rsi >= (rsi_overbought + 10):  # Extremadamente overbought
                signal = "STRONG_SELL"
                interpretation = f"🔴 RSI extremadamente overbought ({current_rsi:.1f} >= {rsi_overbought+10}) - Fuerte señal de venta"
            elif current_rsi >= rsi_overbought:
                signal = "SELL"
                interpretation = f"📉 RSI overbought ({current_rsi:.1f} >= {rsi_overbought}) - Señal de venta"
            elif current_rsi > 50 and current_rsi_fast > current_rsi_slow:
                signal = "BUY"
                interpretation = "🟢 RSI alcista - Momentum positivo"
            elif current_rsi < 50 and current_rsi_fast < current_rsi_slow:
                signal = "SELL"
                interpretation = "🔴 RSI bajista - Momentum negativo"
            else:
                signal = "HOLD"
                interpretation = "⚪ RSI neutral"
            
            # Ajustar señal por divergencia
            if divergence == "BULLISH" and signal in ["SELL", "STRONG_SELL"]:
                signal = "HOLD"
                interpretation += " (Divergencia alcista detectada)"
            elif divergence == "BEARISH" and signal in ["BUY", "STRONG_BUY"]:
                signal = "HOLD"
                interpretation += " (Divergencia bajista detectada)"
            
            result = {
                "rsi": round(current_rsi, 2),
                "rsi_fast": round(current_rsi_fast, 2),
                "rsi_slow": round(current_rsi_slow, 2),
                "divergence": divergence,
                "signal": signal,
                "interpretation": interpretation
            }
            
            # Almacenar en cache
            cls._store_in_cache(cache_key, result)
            return result
            
        except Exception as e:
            return {
                "rsi": 50.0,
                "rsi_fast": 50.0,
                "rsi_slow": 50.0,
                "divergence": "NONE",
                "signal": "HOLD",
                "interpretation": f"Error calculando RSI mejorado: {str(e)}"
            }
    
    @staticmethod
    def rate_of_change(df: pd.DataFrame, period: int = None) -> Dict:
        """
        📊 Calcular Rate of Change (ROC) - Indicador de momentum
        
        Args:
            df: DataFrame con datos OHLCV
            period: Período para el cálculo
            
        Returns:
            Diccionario con ROC y análisis de momentum
        """
        if period is None:
            period = AdvancedIndicatorsConfig.ROC_PERIOD
            
        try:
            # Convertir a float64 para evitar warnings de dtype
            close_float = df['close'].astype('float64')
            
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', FutureWarning)
                warnings.simplefilter('ignore', UserWarning)
                roc = ta.roc(close_float, length=period)
            
            if roc is None or roc.empty:
                # Calcular manualmente
                roc = ((df['close'] - df['close'].shift(period)) / df['close'].shift(period)) * 100
            
            current_roc = AdvancedIndicators.safe_float(roc.iloc[-1], 0.0)
            
            # Calcular ROC promedio para contexto
            roc_avg = roc.tail(50).mean()
            roc_std = roc.tail(50).std()
            
            # Calcular z-score del ROC actual
            roc_zscore = (current_roc - roc_avg) / roc_std if roc_std > 0 else 0
            
            # Generar señales basadas en ROC
            if current_roc > 5.0:
                signal = "STRONG_BUY"
                interpretation = "🟢 ROC muy positivo - Fuerte momentum alcista"
            elif current_roc > 2.0:
                signal = "BUY"
                interpretation = "📈 ROC positivo - Momentum alcista"
            elif current_roc < -5.0:
                signal = "STRONG_SELL"
                interpretation = "🔴 ROC muy negativo - Fuerte momentum bajista"
            elif current_roc < -2.0:
                signal = "SELL"
                interpretation = "📉 ROC negativo - Momentum bajista"
            elif abs(roc_zscore) > 2.0:
                if current_roc > 0:
                    signal = "BUY"
                    interpretation = "🟢 ROC anormalmente alto - Momentum excepcional"
                else:
                    signal = "SELL"
                    interpretation = "🔴 ROC anormalmente bajo - Momentum negativo excepcional"
            else:
                signal = "HOLD"
                interpretation = "⚪ ROC neutral - Sin momentum claro"
            
            return {
                "roc": round(current_roc, 2),
                "roc_avg": round(roc_avg, 2),
                "roc_zscore": round(roc_zscore, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "roc": 0.0,
                "roc_avg": 0.0,
                "roc_zscore": 0.0,
                "signal": "HOLD",
                "interpretation": f"Error calculando ROC: {str(e)}"
            }
    
    @staticmethod
    def volume_profile(df: pd.DataFrame, bins: int = None) -> Dict:
        """
        📊 Calcular Volume Profile - Análisis de distribución de volumen por precio
        
        Args:
            df: DataFrame con datos OHLCV
            bins: Número de niveles de precio para el análisis
            
        Returns:
            Diccionario con análisis de volume profile
        """
        if bins is None:
            bins = AdvancedIndicatorsConfig.VOLUME_PROFILE_BINS
            
        try:
            # Calcular precio típico
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            
            # Crear bins de precio
            price_min = df['low'].min()
            price_max = df['high'].max()
            price_bins = pd.cut(typical_price, bins=bins, include_lowest=True)
            
            # Agrupar volumen por bins de precio
            volume_by_price = df.groupby(price_bins, observed=True)['volume'].sum().sort_index()
            
            # Encontrar el Point of Control (POC) - nivel con mayor volumen
            poc_bin = volume_by_price.idxmax()
            poc_price = poc_bin.mid
            poc_volume = volume_by_price.max()
            
            # Calcular Value Area (70% del volumen total)
            total_volume = volume_by_price.sum()
            target_volume = total_volume * 0.7
            
            # Encontrar Value Area High (VAH) y Value Area Low (VAL)
            sorted_volumes = volume_by_price.sort_values(ascending=False)
            cumulative_volume = 0
            value_area_bins = []
            
            for bin_name, volume in sorted_volumes.items():
                cumulative_volume += volume
                value_area_bins.append(bin_name)
                if cumulative_volume >= target_volume:
                    break
            
            # Extraer precios de los bins del value area
            value_area_prices = [bin_interval.mid for bin_interval in value_area_bins]
            vah = max(value_area_prices)  # Value Area High
            val = min(value_area_prices)  # Value Area Low
            
            current_price = df['close'].iloc[-1]
            
            # Generar señales basadas en la posición del precio
            if current_price > vah:
                signal = "SELL"
                interpretation = "🔴 Precio por encima del Value Area High - Zona de venta"
            elif current_price < val:
                signal = "BUY"
                interpretation = "🟢 Precio por debajo del Value Area Low - Zona de compra"
            elif abs(current_price - poc_price) / poc_price < 0.01:  # Cerca del POC (1%)
                signal = "HOLD"
                interpretation = "⚪ Precio cerca del Point of Control - Zona de equilibrio"
            elif current_price > poc_price:
                signal = "BUY"
                interpretation = "📈 Precio por encima del POC - Bias alcista"
            else:
                signal = "SELL"
                interpretation = "📉 Precio por debajo del POC - Bias bajista"
            
            return {
                "poc_price": round(poc_price, 2),
                "poc_volume": round(poc_volume, 0),
                "vah": round(vah, 2),
                "val": round(val, 2),
                "current_price": round(current_price, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            current_price = AdvancedIndicators.safe_float(df['close'].iloc[-1])
            return {
                "poc_price": current_price,
                "poc_volume": 0.0,
                "vah": current_price * 1.02,
                "val": current_price * 0.98,
                "current_price": current_price,
                "signal": "HOLD",
                "interpretation": f"Error calculando Volume Profile: {str(e)}"
            }
    
    @staticmethod
    def support_resistance_levels(df: pd.DataFrame, window: int = None, min_touches: int = 2) -> Dict:
        """
        📊 Detectar niveles de soporte y resistencia
        
        Args:
            df: DataFrame con datos OHLCV
            window: Ventana para detectar máximos y mínimos locales
            min_touches: Mínimo número de toques para confirmar un nivel
            
        Returns:
            Diccionario con niveles de soporte y resistencia
        """
        if window is None:
            window = AdvancedIndicatorsConfig.SUPPORT_RESISTANCE_WINDOW
            
        try:
            # Detectar máximos y mínimos locales
            highs = df['high'].rolling(window=window, center=True).max() == df['high']
            lows = df['low'].rolling(window=window, center=True).min() == df['low']
            
            # Extraer precios de máximos y mínimos
            resistance_prices = df.loc[highs, 'high'].tolist()
            support_prices = df.loc[lows, 'low'].tolist()
            
            current_price = df['close'].iloc[-1]
            
            # Agrupar niveles similares (tolerancia del 1%)
            def group_levels(prices, tolerance=0.01):
                if not prices:
                    return []
                
                grouped = []
                prices_sorted = sorted(prices)
                
                current_group = [prices_sorted[0]]
                
                for price in prices_sorted[1:]:
                    if abs(price - current_group[-1]) / current_group[-1] <= tolerance:
                        current_group.append(price)
                    else:
                        if len(current_group) >= min_touches:
                            grouped.append(sum(current_group) / len(current_group))
                        current_group = [price]
                
                if len(current_group) >= min_touches:
                    grouped.append(sum(current_group) / len(current_group))
                
                return grouped
            
            resistance_levels = group_levels(resistance_prices)
            support_levels = group_levels(support_prices)
            
            # Encontrar el soporte y resistencia más cercanos
            nearest_resistance = None
            nearest_support = None
            
            for level in resistance_levels:
                if level > current_price:
                    if nearest_resistance is None or level < nearest_resistance:
                        nearest_resistance = level
            
            for level in support_levels:
                if level < current_price:
                    if nearest_support is None or level > nearest_support:
                        nearest_support = level
            
            # Generar señales
            signal = "HOLD"
            interpretation = "⚪ Precio en rango normal"
            
            if nearest_resistance and abs(current_price - nearest_resistance) / current_price < 0.02:
                signal = "SELL"
                interpretation = "🔴 Precio cerca de resistencia - Posible rechazo"
            elif nearest_support and abs(current_price - nearest_support) / current_price < 0.02:
                signal = "BUY"
                interpretation = "🟢 Precio cerca de soporte - Posible rebote"
            
            return {
                "nearest_resistance": round(nearest_resistance, 2) if nearest_resistance else None,
                "nearest_support": round(nearest_support, 2) if nearest_support else None,
                "resistance_levels": [round(level, 2) for level in resistance_levels[-5:]],  # Últimos 5
                "support_levels": [round(level, 2) for level in support_levels[-5:]],  # Últimos 5
                "current_price": round(current_price, 2),
                "signal": signal,
                "interpretation": interpretation
            }
            
        except Exception as e:
            current_price = AdvancedIndicators.safe_float(df['close'].iloc[-1])
            return {
                "nearest_resistance": None,
                "nearest_support": None,
                "resistance_levels": [],
                "support_levels": [],
                "current_price": current_price,
                "signal": "HOLD",
                "interpretation": f"Error detectando S/R: {str(e)}"
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

    @staticmethod
    def trend_lines_analysis(df: pd.DataFrame, lookback: int = None) -> Dict:
        """
        🔍 Detecta líneas de tendencia y breakouts
        
        Args:
            df: DataFrame con datos OHLCV
            lookback: Número de períodos para análisis
            
        Returns:
            Diccionario con análisis de líneas de tendencia
        """
        if lookback is None:
            lookback = AdvancedIndicatorsConfig.TREND_ANALYSIS_LOOKBACK
            
        try:
            if len(df) < lookback:
                return {"trend_lines": [], "signal": "HOLD", "interpretation": "Insufficient data"}
            
            recent_data = df.tail(lookback)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            closes = recent_data['close'].values
            
            # Detectar línea de tendencia alcista (conectando mínimos)
            def find_uptrend_line(lows, closes):
                min_points = []
                for i in range(2, len(lows) - 2):
                    if lows[i] < lows[i-1] and lows[i] < lows[i+1] and lows[i] < lows[i-2] and lows[i] < lows[i+2]:
                        min_points.append((i, lows[i]))
                
                if len(min_points) < 2:
                    return None
                
                # Tomar los dos puntos más recientes
                p1, p2 = min_points[-2], min_points[-1]
                slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
                
                # Proyectar línea al presente
                current_trend_value = p2[1] + slope * (len(lows) - 1 - p2[0])
                return {"slope": slope, "current_value": current_trend_value, "type": "uptrend"}
            
            # Detectar línea de tendencia bajista (conectando máximos)
            def find_downtrend_line(highs, closes):
                max_points = []
                for i in range(2, len(highs) - 2):
                    if highs[i] > highs[i-1] and highs[i] > highs[i+1] and highs[i] > highs[i-2] and highs[i] > highs[i+2]:
                        max_points.append((i, highs[i]))
                
                if len(max_points) < 2:
                    return None
                
                # Tomar los dos puntos más recientes
                p1, p2 = max_points[-2], max_points[-1]
                slope = (p2[1] - p1[1]) / (p2[0] - p1[0])
                
                # Proyectar línea al presente
                current_trend_value = p2[1] + slope * (len(highs) - 1 - p2[0])
                return {"slope": slope, "current_value": current_trend_value, "type": "downtrend"}
            
            uptrend = find_uptrend_line(lows, closes)
            downtrend = find_downtrend_line(highs, closes)
            
            current_price = closes[-1]
            signal = "HOLD"
            interpretation = "No clear trend lines"
            
            # Analizar breakouts
            if uptrend and current_price > uptrend["current_value"]:
                distance_pct = (current_price - uptrend["current_value"]) / uptrend["current_value"] * 100
                if distance_pct > 0.5:  # Breakout significativo
                    signal = "BUY"
                    interpretation = f"🟢 Uptrend line breakout ({distance_pct:.2f}%)"
                else:
                    interpretation = f"📈 Near uptrend line support"
            
            if downtrend and current_price < downtrend["current_value"]:
                distance_pct = (downtrend["current_value"] - current_price) / downtrend["current_value"] * 100
                if distance_pct > 0.5:  # Breakout significativo
                    signal = "SELL"
                    interpretation = f"🔴 Downtrend line breakdown ({distance_pct:.2f}%)"
                else:
                    interpretation = f"📉 Near downtrend line resistance"
            
            return {
                "trend_lines": {
                    "uptrend": uptrend,
                    "downtrend": downtrend
                },
                "signal": signal,
                "interpretation": interpretation,
                "current_price": current_price
            }
            
        except Exception as e:
            return {"trend_lines": [], "signal": "HOLD", "interpretation": f"Error: {str(e)}"}

    @staticmethod
    def chart_patterns_detection(df: pd.DataFrame, window: int = None) -> Dict:
        """
        📈 Detecta patrones de gráficos comunes
        
        Args:
            df: DataFrame con datos OHLCV
            window: Ventana para análisis de patrones
            
        Returns:
            Diccionario con patrones detectados
        """
        if window is None:
            window = AdvancedIndicatorsConfig.CHART_PATTERNS_WINDOW
            
        try:
            if len(df) < window * 2:
                return {"patterns": [], "signal": "HOLD", "interpretation": "Insufficient data"}
            
            recent_data = df.tail(window * 2)
            highs = recent_data['high'].values
            lows = recent_data['low'].values
            closes = recent_data['close'].values
            
            patterns_detected = []
            
            # Detectar Triángulo Ascendente
            def detect_ascending_triangle():
                # Buscar resistencia horizontal y soporte ascendente
                resistance_level = max(highs[-window:])
                resistance_touches = sum(1 for h in highs[-window:] if abs(h - resistance_level) / resistance_level < 0.01)
                
                # Verificar si los mínimos están subiendo
                recent_lows = lows[-window//2:]
                if len(recent_lows) >= 3:
                    low_trend = (recent_lows[-1] - recent_lows[0]) / len(recent_lows)
                    if resistance_touches >= 2 and low_trend > 0:
                        return {"pattern": "Ascending Triangle", "signal": "BUY", "confidence": 70}
                return None
            
            # Detectar Triángulo Descendente
            def detect_descending_triangle():
                # Buscar soporte horizontal y resistencia descendente
                support_level = min(lows[-window:])
                support_touches = sum(1 for l in lows[-window:] if abs(l - support_level) / support_level < 0.01)
                
                # Verificar si los máximos están bajando
                recent_highs = highs[-window//2:]
                if len(recent_highs) >= 3:
                    high_trend = (recent_highs[-1] - recent_highs[0]) / len(recent_highs)
                    if support_touches >= 2 and high_trend < 0:
                        return {"pattern": "Descending Triangle", "signal": "SELL", "confidence": 70}
                return None
            
            # Detectar Doble Techo
            def detect_double_top():
                if len(highs) < window:
                    return None
                
                # Buscar dos picos similares
                peaks = []
                for i in range(5, len(highs) - 5):
                    if all(highs[i] >= highs[i+j] for j in range(-5, 6) if j != 0):
                        peaks.append((i, highs[i]))
                
                if len(peaks) >= 2:
                    last_two_peaks = peaks[-2:]
                    height_diff = abs(last_two_peaks[1][1] - last_two_peaks[0][1]) / last_two_peaks[0][1]
                    if height_diff < 0.03:  # Diferencia menor al 3%
                        return {"pattern": "Double Top", "signal": "SELL", "confidence": 75}
                return None
            
            # Detectar Doble Suelo
            def detect_double_bottom():
                if len(lows) < window:
                    return None
                
                # Buscar dos valles similares
                valleys = []
                for i in range(5, len(lows) - 5):
                    if all(lows[i] <= lows[i+j] for j in range(-5, 6) if j != 0):
                        valleys.append((i, lows[i]))
                
                if len(valleys) >= 2:
                    last_two_valleys = valleys[-2:]
                    depth_diff = abs(last_two_valleys[1][1] - last_two_valleys[0][1]) / last_two_valleys[0][1]
                    if depth_diff < 0.03:  # Diferencia menor al 3%
                        return {"pattern": "Double Bottom", "signal": "BUY", "confidence": 75}
                return None
            
            # Ejecutar detecciones
            pattern_functions = [
                detect_ascending_triangle,
                detect_descending_triangle,
                detect_double_top,
                detect_double_bottom
            ]
            
            for pattern_func in pattern_functions:
                pattern = pattern_func()
                if pattern:
                    patterns_detected.append(pattern)
            
            # Determinar señal principal
            if patterns_detected:
                # Tomar el patrón con mayor confianza
                best_pattern = max(patterns_detected, key=lambda x: x["confidence"])
                signal = best_pattern["signal"]
                interpretation = f"{best_pattern['pattern']} detected (confidence: {best_pattern['confidence']}%)"
            else:
                signal = "HOLD"
                interpretation = "No clear chart patterns detected"
            
            return {
                "patterns": patterns_detected,
                "signal": signal,
                "interpretation": interpretation,
                "current_price": closes[-1]
            }
            
        except Exception as e:
            return {"patterns": [], "signal": "HOLD", "interpretation": f"Error: {str(e)}"}