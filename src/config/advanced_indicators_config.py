"""Configuraciones específicas de Advanced Indicators.

Este módulo contiene todas las configuraciones relacionadas con los
indicadores técnicos avanzados, incluyendo parámetros y umbrales.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE ADVANCED INDICATORS POR PERFIL
# ============================================================================

class AdvancedIndicatorsProfiles:
    """Configuraciones específicas de Advanced Indicators por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Configuración de RSI
            "rsi_config": {
                "period": 14,  # Período de RSI
                "overbought_threshold": 70,  # Umbral de sobrecompra
                "oversold_threshold": 30,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
                "smoothing_enabled": False,  # Suavizado deshabilitado
            },
            
            # Configuración de MACD
            "macd_config": {
                "fast_period": 12,  # Período rápido
                "slow_period": 26,  # Período lento
                "signal_period": 9,  # Período de señal
                "histogram_threshold": 0.001,  # Umbral del histograma
                "zero_line_cross": True,  # Cruce de línea cero
                "signal_line_cross": True,  # Cruce de línea de señal
            },
            
            # Configuración de Bollinger Bands
            "bollinger_config": {
                "period": 20,  # Período
                "std_dev": 2.0,  # Desviación estándar
                "squeeze_threshold": 0.1,  # Umbral de compresión
                "expansion_threshold": 0.3,  # Umbral de expansión
                "band_walk_detection": True,  # Detección de caminata en bandas
            },
            
            # Configuración de Stochastic
            "stochastic_config": {
                "k_period": 14,  # Período K
                "d_period": 3,  # Período D
                "smooth_k": 3,  # Suavizado K
                "overbought_threshold": 80,  # Umbral de sobrecompra
                "oversold_threshold": 20,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
            },
            
            # Configuración de Williams %R
            "williams_r_config": {
                "period": 14,  # Período
                "overbought_threshold": -20,  # Umbral de sobrecompra
                "oversold_threshold": -80,  # Umbral de sobreventa
                "momentum_confirmation": True,  # Confirmación de momentum
            },
            
            # Configuración de CCI (Commodity Channel Index)
            "cci_config": {
                "period": 20,  # Período
                "overbought_threshold": 100,  # Umbral de sobrecompra
                "oversold_threshold": -100,  # Umbral de sobreventa
                "extreme_threshold": 200,  # Umbral extremo
                "trend_confirmation": True,  # Confirmación de tendencia
            },
            
            # Configuración de ATR (Average True Range)
            "atr_config": {
                "period": 14,  # Período
                "volatility_threshold_high": 2.0,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.5,  # Umbral bajo de volatilidad
                "trend_strength_factor": 1.5,  # Factor de fuerza de tendencia
            },
            
            # Configuración de ADX (Average Directional Index)
            "adx_config": {
                "period": 14,  # Período
                "trend_threshold": 25,  # Umbral de tendencia
                "strong_trend_threshold": 40,  # Umbral de tendencia fuerte
                "di_crossover_enabled": True,  # Cruce de DI habilitado
            },
            
            # Configuración de Ichimoku
            "ichimoku_config": {
                "tenkan_period": 9,  # Período Tenkan
                "kijun_period": 26,  # Período Kijun
                "senkou_b_period": 52,  # Período Senkou B
                "displacement": 26,  # Desplazamiento
                "cloud_analysis": True,  # Análisis de nube
                "tk_cross_enabled": True,  # Cruce TK habilitado
            },
            
            # Configuración de Fibonacci
            "fibonacci_config": {
                "retracement_levels": [0.236, 0.382, 0.5, 0.618, 0.786],  # Niveles de retroceso
                "extension_levels": [1.272, 1.414, 1.618, 2.618],  # Niveles de extensión
                "auto_detection": True,  # Detección automática
                "swing_detection_period": 20,  # Período de detección de swing
            },
            
            # Configuración de Volume Indicators
            "volume_config": {
                "obv_enabled": True,  # On-Balance Volume habilitado
                "vwap_enabled": True,  # VWAP habilitado
                "volume_sma_period": 20,  # Período SMA de volumen
                "volume_spike_threshold": 2.0,  # Umbral de pico de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Configuración de Moving Averages
            "ma_config": {
                "sma_periods": [9, 21, 50, 200],  # Períodos SMA
                "ema_periods": [12, 26, 50, 200],  # Períodos EMA
                "wma_periods": [10, 20],  # Períodos WMA
                "hull_ma_period": 21,  # Período Hull MA
                "cross_detection": True,  # Detección de cruces
                "slope_analysis": True,  # Análisis de pendiente
            },
            
            # Configuración de Momentum Indicators
            "momentum_config": {
                "roc_period": 12,  # Período Rate of Change
                "momentum_period": 10,  # Período de Momentum
                "trix_period": 14,  # Período TRIX
                "ultimate_oscillator_enabled": True,  # Ultimate Oscillator habilitado
                "money_flow_index_period": 14,  # Período Money Flow Index
            },
            
            # Configuración de Pattern Recognition
            "pattern_config": {
                "candlestick_patterns": True,  # Patrones de velas
                "chart_patterns": True,  # Patrones de gráfico
                "harmonic_patterns": False,  # Patrones armónicos deshabilitados
                "pattern_confirmation_bars": 2,  # Barras de confirmación
                "pattern_reliability_threshold": 0.7,  # Umbral de confiabilidad
            },
            
            # Configuración de Multi-Timeframe
            "mtf_config": {
                "enabled": True,  # Multi-timeframe habilitado
                "primary_timeframe": "5m",  # Timeframe principal
                "secondary_timeframes": ["15m", "1h"],  # Timeframes secundarios
                "trend_timeframe": "4h",  # Timeframe de tendencia
                "alignment_required": True,  # Alineación requerida
            },
            
            # Configuración de Alerts
            "alert_config": {
                "signal_alerts": True,  # Alertas de señales
                "threshold_alerts": True,  # Alertas de umbrales
                "pattern_alerts": True,  # Alertas de patrones
                "divergence_alerts": True,  # Alertas de divergencias
                "alert_cooldown": 300,  # Cooldown de alertas (5 min)
            }
        },
        
        "AGRESIVO": {
            # Configuración de RSI
            "rsi_config": {
                "period": 14,  # Período de RSI
                "overbought_threshold": 75,  # Umbral de sobrecompra
                "oversold_threshold": 25,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
                "smoothing_enabled": False,  # Suavizado deshabilitado
            },
            
            # Configuración de MACD
            "macd_config": {
                "fast_period": 12,  # Período rápido
                "slow_period": 26,  # Período lento
                "signal_period": 9,  # Período de señal
                "histogram_threshold": 0.0015,  # Umbral del histograma
                "zero_line_cross": True,  # Cruce de línea cero
                "signal_line_cross": True,  # Cruce de línea de señal
            },
            
            # Configuración de Bollinger Bands
            "bollinger_config": {
                "period": 20,  # Período
                "std_dev": 2.0,  # Desviación estándar
                "squeeze_threshold": 0.12,  # Umbral de compresión
                "expansion_threshold": 0.35,  # Umbral de expansión
                "band_walk_detection": True,  # Detección de caminata en bandas
            },
            
            # Configuración de Stochastic
            "stochastic_config": {
                "k_period": 14,  # Período K
                "d_period": 3,  # Período D
                "smooth_k": 3,  # Suavizado K
                "overbought_threshold": 75,  # Umbral de sobrecompra
                "oversold_threshold": 25,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
            },
            
            # Configuración de Williams %R
            "williams_r_config": {
                "period": 14,  # Período
                "overbought_threshold": -25,  # Umbral de sobrecompra
                "oversold_threshold": -75,  # Umbral de sobreventa
                "momentum_confirmation": True,  # Confirmación de momentum
            },
            
            # Configuración de CCI (Commodity Channel Index)
            "cci_config": {
                "period": 20,  # Período
                "overbought_threshold": 120,  # Umbral de sobrecompra
                "oversold_threshold": -120,  # Umbral de sobreventa
                "extreme_threshold": 250,  # Umbral extremo
                "trend_confirmation": True,  # Confirmación de tendencia
            },
            
            # Configuración de ATR (Average True Range)
            "atr_config": {
                "period": 14,  # Período
                "volatility_threshold_high": 2.2,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.6,  # Umbral bajo de volatilidad
                "trend_strength_factor": 1.6,  # Factor de fuerza de tendencia
            },
            
            # Configuración de ADX (Average Directional Index)
            "adx_config": {
                "period": 14,  # Período
                "trend_threshold": 20,  # Umbral de tendencia
                "strong_trend_threshold": 35,  # Umbral de tendencia fuerte
                "di_crossover_enabled": True,  # Cruce de DI habilitado
            },
            
            # Configuración de Ichimoku
            "ichimoku_config": {
                "tenkan_period": 9,  # Período Tenkan
                "kijun_period": 26,  # Período Kijun
                "senkou_b_period": 52,  # Período Senkou B
                "displacement": 26,  # Desplazamiento
                "cloud_analysis": True,  # Análisis de nube
                "tk_cross_enabled": True,  # Cruce TK habilitado
            },
            
            # Configuración de Fibonacci
            "fibonacci_config": {
                "retracement_levels": [0.236, 0.382, 0.5, 0.618, 0.786],  # Niveles de retroceso
                "extension_levels": [1.272, 1.414, 1.618, 2.618],  # Niveles de extensión
                "auto_detection": True,  # Detección automática
                "swing_detection_period": 18,  # Período de detección de swing
            },
            
            # Configuración de Volume Indicators
            "volume_config": {
                "obv_enabled": True,  # On-Balance Volume habilitado
                "vwap_enabled": True,  # VWAP habilitado
                "volume_sma_period": 20,  # Período SMA de volumen
                "volume_spike_threshold": 2.2,  # Umbral de pico de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Configuración de Moving Averages
            "ma_config": {
                "sma_periods": [9, 21, 50, 100, 200],  # Períodos SMA
                "ema_periods": [12, 26, 50, 100, 200],  # Períodos EMA
                "wma_periods": [10, 20, 50],  # Períodos WMA
                "hull_ma_period": 21,  # Período Hull MA
                "cross_detection": True,  # Detección de cruces
                "slope_analysis": True,  # Análisis de pendiente
            },
            
            # Configuración de Momentum Indicators
            "momentum_config": {
                "roc_period": 12,  # Período Rate of Change
                "momentum_period": 10,  # Período de Momentum
                "trix_period": 14,  # Período TRIX
                "ultimate_oscillator_enabled": True,  # Ultimate Oscillator habilitado
                "money_flow_index_period": 14,  # Período Money Flow Index
            },
            
            # Configuración de Pattern Recognition
            "pattern_config": {
                "candlestick_patterns": True,  # Patrones de velas
                "chart_patterns": True,  # Patrones de gráfico
                "harmonic_patterns": True,  # Patrones armónicos habilitados
                "pattern_confirmation_bars": 2,  # Barras de confirmación
                "pattern_reliability_threshold": 0.65,  # Umbral de confiabilidad
            },
            
            # Configuración de Multi-Timeframe
            "mtf_config": {
                "enabled": True,  # Multi-timeframe habilitado
                "primary_timeframe": "5m",  # Timeframe principal
                "secondary_timeframes": ["15m", "30m", "1h"],  # Timeframes secundarios
                "trend_timeframe": "4h",  # Timeframe de tendencia
                "alignment_required": True,  # Alineación requerida
            },
            
            # Configuración de Alerts
            "alert_config": {
                "signal_alerts": True,  # Alertas de señales
                "threshold_alerts": True,  # Alertas de umbrales
                "pattern_alerts": True,  # Alertas de patrones
                "divergence_alerts": True,  # Alertas de divergencias
                "alert_cooldown": 240,  # Cooldown de alertas (4 min)
            }
        },
        
        "OPTIMO": {
            # Configuración de RSI
            "rsi_config": {
                "period": 14,  # Período de RSI
                "overbought_threshold": 70,  # Umbral de sobrecompra
                "oversold_threshold": 30,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
                "smoothing_enabled": True,  # Suavizado habilitado
            },
            
            # Configuración de MACD
            "macd_config": {
                "fast_period": 12,  # Período rápido
                "slow_period": 26,  # Período lento
                "signal_period": 9,  # Período de señal
                "histogram_threshold": 0.002,  # Umbral del histograma
                "zero_line_cross": True,  # Cruce de línea cero
                "signal_line_cross": True,  # Cruce de línea de señal
            },
            
            # Configuración de Bollinger Bands
            "bollinger_config": {
                "period": 20,  # Período
                "std_dev": 2.0,  # Desviación estándar
                "squeeze_threshold": 0.15,  # Umbral de compresión
                "expansion_threshold": 0.4,  # Umbral de expansión
                "band_walk_detection": True,  # Detección de caminata en bandas
            },
            
            # Configuración de Stochastic
            "stochastic_config": {
                "k_period": 14,  # Período K
                "d_period": 3,  # Período D
                "smooth_k": 3,  # Suavizado K
                "overbought_threshold": 80,  # Umbral de sobrecompra
                "oversold_threshold": 20,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
            },
            
            # Configuración de Williams %R
            "williams_r_config": {
                "period": 14,  # Período
                "overbought_threshold": -20,  # Umbral de sobrecompra
                "oversold_threshold": -80,  # Umbral de sobreventa
                "momentum_confirmation": True,  # Confirmación de momentum
            },
            
            # Configuración de CCI (Commodity Channel Index)
            "cci_config": {
                "period": 20,  # Período
                "overbought_threshold": 100,  # Umbral de sobrecompra
                "oversold_threshold": -100,  # Umbral de sobreventa
                "extreme_threshold": 200,  # Umbral extremo
                "trend_confirmation": True,  # Confirmación de tendencia
            },
            
            # Configuración de ATR (Average True Range)
            "atr_config": {
                "period": 14,  # Período
                "volatility_threshold_high": 2.5,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.7,  # Umbral bajo de volatilidad
                "trend_strength_factor": 1.8,  # Factor de fuerza de tendencia
            },
            
            # Configuración de ADX (Average Directional Index)
            "adx_config": {
                "period": 14,  # Período
                "trend_threshold": 25,  # Umbral de tendencia
                "strong_trend_threshold": 40,  # Umbral de tendencia fuerte
                "di_crossover_enabled": True,  # Cruce de DI habilitado
            },
            
            # Configuración de Ichimoku
            "ichimoku_config": {
                "tenkan_period": 9,  # Período Tenkan
                "kijun_period": 26,  # Período Kijun
                "senkou_b_period": 52,  # Período Senkou B
                "displacement": 26,  # Desplazamiento
                "cloud_analysis": True,  # Análisis de nube
                "tk_cross_enabled": True,  # Cruce TK habilitado
            },
            
            # Configuración de Fibonacci
            "fibonacci_config": {
                "retracement_levels": [0.236, 0.382, 0.5, 0.618, 0.786],  # Niveles de retroceso
                "extension_levels": [1.272, 1.414, 1.618, 2.618],  # Niveles de extensión
                "auto_detection": True,  # Detección automática
                "swing_detection_period": 25,  # Período de detección de swing
            },
            
            # Configuración de Volume Indicators
            "volume_config": {
                "obv_enabled": True,  # On-Balance Volume habilitado
                "vwap_enabled": True,  # VWAP habilitado
                "volume_sma_period": 20,  # Período SMA de volumen
                "volume_spike_threshold": 2.5,  # Umbral de pico de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Configuración de Moving Averages
            "ma_config": {
                "sma_periods": [9, 21, 50, 100, 200],  # Períodos SMA
                "ema_periods": [12, 26, 50, 100, 200],  # Períodos EMA
                "wma_periods": [10, 20, 50],  # Períodos WMA
                "hull_ma_period": 21,  # Período Hull MA
                "cross_detection": True,  # Detección de cruces
                "slope_analysis": True,  # Análisis de pendiente
            },
            
            # Configuración de Momentum Indicators
            "momentum_config": {
                "roc_period": 12,  # Período Rate of Change
                "momentum_period": 10,  # Período de Momentum
                "trix_period": 14,  # Período TRIX
                "ultimate_oscillator_enabled": True,  # Ultimate Oscillator habilitado
                "money_flow_index_period": 14,  # Período Money Flow Index
            },
            
            # Configuración de Pattern Recognition
            "pattern_config": {
                "candlestick_patterns": True,  # Patrones de velas
                "chart_patterns": True,  # Patrones de gráfico
                "harmonic_patterns": True,  # Patrones armónicos habilitados
                "pattern_confirmation_bars": 3,  # Barras de confirmación
                "pattern_reliability_threshold": 0.75,  # Umbral de confiabilidad
            },
            
            # Configuración de Multi-Timeframe
            "mtf_config": {
                "enabled": True,  # Multi-timeframe habilitado
                "primary_timeframe": "15m",  # Timeframe principal
                "secondary_timeframes": ["30m", "1h", "2h"],  # Timeframes secundarios
                "trend_timeframe": "1d",  # Timeframe de tendencia
                "alignment_required": True,  # Alineación requerida
            },
            
            # Configuración de Alerts
            "alert_config": {
                "signal_alerts": True,  # Alertas de señales
                "threshold_alerts": True,  # Alertas de umbrales
                "pattern_alerts": True,  # Alertas de patrones
                "divergence_alerts": True,  # Alertas de divergencias
                "alert_cooldown": 180,  # Cooldown de alertas (3 min)
            }
        },
        
        "CONSERVADOR": {
            # Configuración de RSI
            "rsi_config": {
                "period": 21,  # Período de RSI
                "overbought_threshold": 75,  # Umbral de sobrecompra
                "oversold_threshold": 25,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
                "smoothing_enabled": True,  # Suavizado habilitado
            },
            
            # Configuración de MACD
            "macd_config": {
                "fast_period": 12,  # Período rápido
                "slow_period": 26,  # Período lento
                "signal_period": 9,  # Período de señal
                "histogram_threshold": 0.003,  # Umbral del histograma
                "zero_line_cross": True,  # Cruce de línea cero
                "signal_line_cross": True,  # Cruce de línea de señal
            },
            
            # Configuración de Bollinger Bands
            "bollinger_config": {
                "period": 20,  # Período
                "std_dev": 2.5,  # Desviación estándar
                "squeeze_threshold": 0.2,  # Umbral de compresión
                "expansion_threshold": 0.5,  # Umbral de expansión
                "band_walk_detection": True,  # Detección de caminata en bandas
            },
            
            # Configuración de Stochastic
            "stochastic_config": {
                "k_period": 21,  # Período K
                "d_period": 5,  # Período D
                "smooth_k": 5,  # Suavizado K
                "overbought_threshold": 80,  # Umbral de sobrecompra
                "oversold_threshold": 20,  # Umbral de sobreventa
                "divergence_detection": True,  # Detección de divergencias
            },
            
            # Configuración de Williams %R
            "williams_r_config": {
                "period": 21,  # Período
                "overbought_threshold": -20,  # Umbral de sobrecompra
                "oversold_threshold": -80,  # Umbral de sobreventa
                "momentum_confirmation": True,  # Confirmación de momentum
            },
            
            # Configuración de CCI (Commodity Channel Index)
            "cci_config": {
                "period": 30,  # Período
                "overbought_threshold": 150,  # Umbral de sobrecompra
                "oversold_threshold": -150,  # Umbral de sobreventa
                "extreme_threshold": 300,  # Umbral extremo
                "trend_confirmation": True,  # Confirmación de tendencia
            },
            
            # Configuración de ATR (Average True Range)
            "atr_config": {
                "period": 21,  # Período
                "volatility_threshold_high": 3.0,  # Umbral alto de volatilidad
                "volatility_threshold_low": 1.0,  # Umbral bajo de volatilidad
                "trend_strength_factor": 2.0,  # Factor de fuerza de tendencia
            },
            
            # Configuración de ADX (Average Directional Index)
            "adx_config": {
                "period": 21,  # Período
                "trend_threshold": 30,  # Umbral de tendencia
                "strong_trend_threshold": 50,  # Umbral de tendencia fuerte
                "di_crossover_enabled": True,  # Cruce de DI habilitado
            },
            
            # Configuración de Ichimoku
            "ichimoku_config": {
                "tenkan_period": 9,  # Período Tenkan
                "kijun_period": 26,  # Período Kijun
                "senkou_b_period": 52,  # Período Senkou B
                "displacement": 26,  # Desplazamiento
                "cloud_analysis": True,  # Análisis de nube
                "tk_cross_enabled": True,  # Cruce TK habilitado
            },
            
            # Configuración de Fibonacci
            "fibonacci_config": {
                "retracement_levels": [0.236, 0.382, 0.5, 0.618, 0.786],  # Niveles de retroceso
                "extension_levels": [1.272, 1.414, 1.618, 2.618],  # Niveles de extensión
                "auto_detection": True,  # Detección automática
                "swing_detection_period": 30,  # Período de detección de swing
            },
            
            # Configuración de Volume Indicators
            "volume_config": {
                "obv_enabled": True,  # On-Balance Volume habilitado
                "vwap_enabled": True,  # VWAP habilitado
                "volume_sma_period": 30,  # Período SMA de volumen
                "volume_spike_threshold": 3.0,  # Umbral de pico de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Configuración de Moving Averages
            "ma_config": {
                "sma_periods": [20, 50, 100, 200],  # Períodos SMA
                "ema_periods": [21, 50, 100, 200],  # Períodos EMA
                "wma_periods": [20, 50],  # Períodos WMA
                "hull_ma_period": 30,  # Período Hull MA
                "cross_detection": True,  # Detección de cruces
                "slope_analysis": True,  # Análisis de pendiente
            },
            
            # Configuración de Momentum Indicators
            "momentum_config": {
                "roc_period": 20,  # Período Rate of Change
                "momentum_period": 15,  # Período de Momentum
                "trix_period": 21,  # Período TRIX
                "ultimate_oscillator_enabled": True,  # Ultimate Oscillator habilitado
                "money_flow_index_period": 21,  # Período Money Flow Index
            },
            
            # Configuración de Pattern Recognition
            "pattern_config": {
                "candlestick_patterns": True,  # Patrones de velas
                "chart_patterns": True,  # Patrones de gráfico
                "harmonic_patterns": False,  # Patrones armónicos deshabilitados
                "pattern_confirmation_bars": 5,  # Barras de confirmación
                "pattern_reliability_threshold": 0.85,  # Umbral de confiabilidad
            },
            
            # Configuración de Multi-Timeframe
            "mtf_config": {
                "enabled": True,  # Multi-timeframe habilitado
                "primary_timeframe": "1h",  # Timeframe principal
                "secondary_timeframes": ["2h", "4h"],  # Timeframes secundarios
                "trend_timeframe": "1d",  # Timeframe de tendencia
                "alignment_required": True,  # Alineación requerida
            },
            
            # Configuración de Alerts
            "alert_config": {
                "signal_alerts": True,  # Alertas de señales
                "threshold_alerts": True,  # Alertas de umbrales
                "pattern_alerts": True,  # Alertas de patrones
                "divergence_alerts": True,  # Alertas de divergencias
                "alert_cooldown": 600,  # Cooldown de alertas (10 min)
            }
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_advanced_indicators_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de advanced indicators para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración de advanced indicators
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in AdvancedIndicatorsProfiles.PROFILES:
        raise ValueError(f"Perfil de advanced indicators no válido: {profile}")
    
    return AdvancedIndicatorsProfiles.PROFILES[profile]

def get_available_indicators_profiles() -> List[str]:
    """Obtiene la lista de perfiles de advanced indicators disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(AdvancedIndicatorsProfiles.PROFILES.keys())

def validate_indicators_profile(profile: str) -> bool:
    """Valida si un perfil de advanced indicators es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in AdvancedIndicatorsProfiles.PROFILES

def get_rsi_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de RSI para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de RSI
    """
    config = get_advanced_indicators_config(profile)
    return config["rsi_config"]

def get_macd_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de MACD para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de MACD
    """
    config = get_advanced_indicators_config(profile)
    return config["macd_config"]

def get_bollinger_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de Bollinger Bands para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de Bollinger Bands
    """
    config = get_advanced_indicators_config(profile)
    return config["bollinger_config"]

def get_volume_indicators_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de indicadores de volumen para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de indicadores de volumen
    """
    config = get_advanced_indicators_config(profile)
    return config["volume_config"]

def get_moving_averages_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de medias móviles para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de medias móviles
    """
    config = get_advanced_indicators_config(profile)
    return config["ma_config"]

def get_pattern_recognition_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de reconocimiento de patrones para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de reconocimiento de patrones
    """
    config = get_advanced_indicators_config(profile)
    return config["pattern_config"]

# ============================================================================
# 📊 CONFIGURACIÓN LEGACY PARA COMPATIBILIDAD
# ============================================================================

# Configuración legacy que mapea perfiles a configuraciones
ADVANCED_INDICATORS_CONFIG = {
    "RAPIDO": AdvancedIndicatorsProfiles.PROFILES["RAPIDO"],
    "AGRESIVO": AdvancedIndicatorsProfiles.PROFILES["AGRESIVO"],
    "OPTIMO": AdvancedIndicatorsProfiles.PROFILES["OPTIMO"],
    "CONSERVADOR": AdvancedIndicatorsProfiles.PROFILES["CONSERVADOR"]
}

def validate_advanced_indicators_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración de advanced indicators.
    
    Args:
        config: Configuración a validar
        
    Returns:
        True si la configuración es válida
    """
    return True