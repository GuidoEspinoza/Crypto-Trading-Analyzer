"""Configuraciones específicas del Market Analyzer.

Este módulo contiene todas las configuraciones relacionadas con el análisis
de mercado, incluyendo indicadores técnicos, timeframes y parámetros de análisis.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE MARKET ANALYZER POR PERFIL
# ============================================================================

class MarketAnalyzerProfiles:
    """Configuraciones específicas del Market Analyzer por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Timeframes de análisis
            "primary_timeframes": ["1m", "5m", "15m"],  # Timeframes principales
            "secondary_timeframes": ["30m", "1h"],  # Timeframes secundarios
            "trend_timeframes": ["4h", "1d"],  # Timeframes para tendencia
            "analysis_depth": "fast",  # Profundidad de análisis
            
            # Indicadores técnicos
            "technical_indicators": {
                "sma_periods": [9, 21, 50],  # Períodos de SMA
                "ema_periods": [12, 26, 50],  # Períodos de EMA
                "rsi_period": 14,  # Período de RSI
                "macd_fast": 12,  # MACD rápido
                "macd_slow": 26,  # MACD lento
                "macd_signal": 9,  # Señal MACD
                "bb_period": 20,  # Período de Bollinger Bands
                "bb_std": 2,  # Desviación estándar BB
                "stoch_k": 14,  # Período K de Stochastic
                "stoch_d": 3,  # Período D de Stochastic
                "atr_period": 14,  # Período de ATR
                "volume_sma": 20,  # SMA de volumen
            },
            
            # Configuración de señales
            "signal_config": {
                "min_signal_strength": 0.6,  # Fuerza mínima de señal
                "signal_confirmation_required": 2,  # Confirmaciones requeridas
                "divergence_detection": True,  # Detección de divergencias
                "pattern_recognition": True,  # Reconocimiento de patrones
                "support_resistance_levels": 5,  # Niveles de soporte/resistencia
                "fibonacci_levels": True,  # Niveles de Fibonacci
            },
            
            # Análisis de tendencia
            "trend_analysis": {
                "trend_strength_threshold": 0.7,  # Umbral de fuerza de tendencia
                "trend_reversal_sensitivity": 0.8,  # Sensibilidad de reversión
                "trend_confirmation_periods": 3,  # Períodos de confirmación
                "adx_threshold": 25,  # Umbral de ADX
                "trend_line_detection": True,  # Detección de líneas de tendencia
            },
            
            # Análisis de volatilidad
            "volatility_analysis": {
                "volatility_threshold_high": 0.05,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.01,  # Umbral bajo de volatilidad
                "volatility_window": 20,  # Ventana de volatilidad
                "volatility_adjustment": True,  # Ajuste por volatilidad
                "vix_correlation": False,  # Correlación con VIX
            },
            
            # Análisis de volumen
            "volume_analysis": {
                "volume_spike_threshold": 2.0,  # Umbral de pico de volumen
                "volume_trend_periods": 10,  # Períodos de tendencia de volumen
                "obv_enabled": True,  # On-Balance Volume habilitado
                "volume_profile": False,  # Perfil de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Market Sentiment
            "sentiment_analysis": {
                "fear_greed_weight": 0.3,  # Peso del índice Fear & Greed
                "social_sentiment_weight": 0.2,  # Peso del sentimiento social
                "news_sentiment_weight": 0.3,  # Peso del sentimiento de noticias
                "technical_sentiment_weight": 0.2,  # Peso del sentimiento técnico
                "sentiment_update_interval": 300,  # Intervalo de actualización (5 min)
            },
            
            # Configuración de actualización
            "update_config": {
                "data_update_interval": 30,  # Intervalo de actualización de datos (30s)
                "analysis_update_interval": 60,  # Intervalo de análisis (1 min)
                "cache_duration": 300,  # Duración de caché (5 min)
                "real_time_analysis": True,  # Análisis en tiempo real
                "background_updates": True,  # Actualizaciones en segundo plano
            },
            
            # Configuración de alertas
            "alert_config": {
                "price_alert_threshold": 0.02,  # Umbral de alerta de precio (2%)
                "volume_alert_threshold": 3.0,  # Umbral de alerta de volumen
                "technical_alert_enabled": True,  # Alertas técnicas habilitadas
                "pattern_alert_enabled": True,  # Alertas de patrones habilitadas
                "breakout_alert_enabled": True,  # Alertas de breakout habilitadas
            },
            
            # Performance y optimización
            "performance_config": {
                "parallel_analysis": True,  # Análisis paralelo
                "max_concurrent_symbols": 10,  # Máximo símbolos concurrentes
                "memory_optimization": True,  # Optimización de memoria
                "data_compression": True,  # Compresión de datos
                "analysis_timeout": 30,  # Timeout de análisis (30s)
            }
        },
        
        "AGRESIVO": {
            # Timeframes de análisis
            "primary_timeframes": ["1m", "5m", "15m", "30m"],  # Timeframes principales
            "secondary_timeframes": ["1h", "2h"],  # Timeframes secundarios
            "trend_timeframes": ["4h", "1d"],  # Timeframes para tendencia
            "analysis_depth": "medium",  # Profundidad de análisis
            
            # Indicadores técnicos
            "technical_indicators": {
                "sma_periods": [9, 21, 50, 100],  # Períodos de SMA
                "ema_periods": [12, 26, 50, 100],  # Períodos de EMA
                "rsi_period": 14,  # Período de RSI
                "macd_fast": 12,  # MACD rápido
                "macd_slow": 26,  # MACD lento
                "macd_signal": 9,  # Señal MACD
                "bb_period": 20,  # Período de Bollinger Bands
                "bb_std": 2,  # Desviación estándar BB
                "stoch_k": 14,  # Período K de Stochastic
                "stoch_d": 3,  # Período D de Stochastic
                "atr_period": 14,  # Período de ATR
                "volume_sma": 20,  # SMA de volumen
            },
            
            # Configuración de señales
            "signal_config": {
                "min_signal_strength": 0.65,  # Fuerza mínima de señal
                "signal_confirmation_required": 2,  # Confirmaciones requeridas
                "divergence_detection": True,  # Detección de divergencias
                "pattern_recognition": True,  # Reconocimiento de patrones
                "support_resistance_levels": 7,  # Niveles de soporte/resistencia
                "fibonacci_levels": True,  # Niveles de Fibonacci
            },
            
            # Análisis de tendencia
            "trend_analysis": {
                "trend_strength_threshold": 0.65,  # Umbral de fuerza de tendencia
                "trend_reversal_sensitivity": 0.75,  # Sensibilidad de reversión
                "trend_confirmation_periods": 3,  # Períodos de confirmación
                "adx_threshold": 25,  # Umbral de ADX
                "trend_line_detection": True,  # Detección de líneas de tendencia
            },
            
            # Análisis de volatilidad
            "volatility_analysis": {
                "volatility_threshold_high": 0.06,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.015,  # Umbral bajo de volatilidad
                "volatility_window": 20,  # Ventana de volatilidad
                "volatility_adjustment": True,  # Ajuste por volatilidad
                "vix_correlation": True,  # Correlación con VIX
            },
            
            # Análisis de volumen
            "volume_analysis": {
                "volume_spike_threshold": 2.5,  # Umbral de pico de volumen
                "volume_trend_periods": 15,  # Períodos de tendencia de volumen
                "obv_enabled": True,  # On-Balance Volume habilitado
                "volume_profile": True,  # Perfil de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Market Sentiment
            "sentiment_analysis": {
                "fear_greed_weight": 0.25,  # Peso del índice Fear & Greed
                "social_sentiment_weight": 0.25,  # Peso del sentimiento social
                "news_sentiment_weight": 0.3,  # Peso del sentimiento de noticias
                "technical_sentiment_weight": 0.2,  # Peso del sentimiento técnico
                "sentiment_update_interval": 240,  # Intervalo de actualización (4 min)
            },
            
            # Configuración de actualización
            "update_config": {
                "data_update_interval": 45,  # Intervalo de actualización de datos (45s)
                "analysis_update_interval": 90,  # Intervalo de análisis (1.5 min)
                "cache_duration": 450,  # Duración de caché (7.5 min)
                "real_time_analysis": True,  # Análisis en tiempo real
                "background_updates": True,  # Actualizaciones en segundo plano
            },
            
            # Configuración de alertas
            "alert_config": {
                "price_alert_threshold": 0.025,  # Umbral de alerta de precio (2.5%)
                "volume_alert_threshold": 2.5,  # Umbral de alerta de volumen
                "technical_alert_enabled": True,  # Alertas técnicas habilitadas
                "pattern_alert_enabled": True,  # Alertas de patrones habilitadas
                "breakout_alert_enabled": True,  # Alertas de breakout habilitadas
            },
            
            # Performance y optimización
            "performance_config": {
                "parallel_analysis": True,  # Análisis paralelo
                "max_concurrent_symbols": 8,  # Máximo símbolos concurrentes
                "memory_optimization": True,  # Optimización de memoria
                "data_compression": True,  # Compresión de datos
                "analysis_timeout": 45,  # Timeout de análisis (45s)
            }
        },
        
        "OPTIMO": {
            # Timeframes de análisis
            "primary_timeframes": ["5m", "15m", "30m", "1h"],  # Timeframes principales
            "secondary_timeframes": ["2h", "4h"],  # Timeframes secundarios
            "trend_timeframes": ["1d", "3d"],  # Timeframes para tendencia
            "analysis_depth": "deep",  # Profundidad de análisis
            
            # Indicadores técnicos
            "technical_indicators": {
                "sma_periods": [9, 21, 50, 100, 200],  # Períodos de SMA
                "ema_periods": [12, 26, 50, 100, 200],  # Períodos de EMA
                "rsi_period": 14,  # Período de RSI
                "macd_fast": 12,  # MACD rápido
                "macd_slow": 26,  # MACD lento
                "macd_signal": 9,  # Señal MACD
                "bb_period": 20,  # Período de Bollinger Bands
                "bb_std": 2,  # Desviación estándar BB
                "stoch_k": 14,  # Período K de Stochastic
                "stoch_d": 3,  # Período D de Stochastic
                "atr_period": 14,  # Período de ATR
                "volume_sma": 20,  # SMA de volumen
            },
            
            # Configuración de señales
            "signal_config": {
                "min_signal_strength": 0.7,  # Fuerza mínima de señal
                "signal_confirmation_required": 3,  # Confirmaciones requeridas
                "divergence_detection": True,  # Detección de divergencias
                "pattern_recognition": True,  # Reconocimiento de patrones
                "support_resistance_levels": 10,  # Niveles de soporte/resistencia
                "fibonacci_levels": True,  # Niveles de Fibonacci
            },
            
            # Análisis de tendencia
            "trend_analysis": {
                "trend_strength_threshold": 0.7,  # Umbral de fuerza de tendencia
                "trend_reversal_sensitivity": 0.7,  # Sensibilidad de reversión
                "trend_confirmation_periods": 4,  # Períodos de confirmación
                "adx_threshold": 25,  # Umbral de ADX
                "trend_line_detection": True,  # Detección de líneas de tendencia
            },
            
            # Análisis de volatilidad
            "volatility_analysis": {
                "volatility_threshold_high": 0.08,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.02,  # Umbral bajo de volatilidad
                "volatility_window": 30,  # Ventana de volatilidad
                "volatility_adjustment": True,  # Ajuste por volatilidad
                "vix_correlation": True,  # Correlación con VIX
            },
            
            # Análisis de volumen
            "volume_analysis": {
                "volume_spike_threshold": 3.0,  # Umbral de pico de volumen
                "volume_trend_periods": 20,  # Períodos de tendencia de volumen
                "obv_enabled": True,  # On-Balance Volume habilitado
                "volume_profile": True,  # Perfil de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Market Sentiment
            "sentiment_analysis": {
                "fear_greed_weight": 0.2,  # Peso del índice Fear & Greed
                "social_sentiment_weight": 0.2,  # Peso del sentimiento social
                "news_sentiment_weight": 0.35,  # Peso del sentimiento de noticias
                "technical_sentiment_weight": 0.25,  # Peso del sentimiento técnico
                "sentiment_update_interval": 180,  # Intervalo de actualización (3 min)
            },
            
            # Configuración de actualización
            "update_config": {
                "data_update_interval": 60,  # Intervalo de actualización de datos (1 min)
                "analysis_update_interval": 120,  # Intervalo de análisis (2 min)
                "cache_duration": 600,  # Duración de caché (10 min)
                "real_time_analysis": True,  # Análisis en tiempo real
                "background_updates": True,  # Actualizaciones en segundo plano
            },
            
            # Configuración de alertas
            "alert_config": {
                "price_alert_threshold": 0.03,  # Umbral de alerta de precio (3%)
                "volume_alert_threshold": 2.0,  # Umbral de alerta de volumen
                "technical_alert_enabled": True,  # Alertas técnicas habilitadas
                "pattern_alert_enabled": True,  # Alertas de patrones habilitadas
                "breakout_alert_enabled": True,  # Alertas de breakout habilitadas
            },
            
            # Performance y optimización
            "performance_config": {
                "parallel_analysis": True,  # Análisis paralelo
                "max_concurrent_symbols": 6,  # Máximo símbolos concurrentes
                "memory_optimization": True,  # Optimización de memoria
                "data_compression": True,  # Compresión de datos
                "analysis_timeout": 60,  # Timeout de análisis (60s)
            }
        },
        
        "CONSERVADOR": {
            # Timeframes de análisis
            "primary_timeframes": ["15m", "30m", "1h", "2h"],  # Timeframes principales
            "secondary_timeframes": ["4h", "6h"],  # Timeframes secundarios
            "trend_timeframes": ["1d", "3d", "1w"],  # Timeframes para tendencia
            "analysis_depth": "comprehensive",  # Profundidad de análisis
            
            # Indicadores técnicos
            "technical_indicators": {
                "sma_periods": [20, 50, 100, 200],  # Períodos de SMA
                "ema_periods": [21, 50, 100, 200],  # Períodos de EMA
                "rsi_period": 21,  # Período de RSI
                "macd_fast": 12,  # MACD rápido
                "macd_slow": 26,  # MACD lento
                "macd_signal": 9,  # Señal MACD
                "bb_period": 20,  # Período de Bollinger Bands
                "bb_std": 2,  # Desviación estándar BB
                "stoch_k": 21,  # Período K de Stochastic
                "stoch_d": 5,  # Período D de Stochastic
                "atr_period": 21,  # Período de ATR
                "volume_sma": 30,  # SMA de volumen
            },
            
            # Configuración de señales
            "signal_config": {
                "min_signal_strength": 0.8,  # Fuerza mínima de señal
                "signal_confirmation_required": 4,  # Confirmaciones requeridas
                "divergence_detection": True,  # Detección de divergencias
                "pattern_recognition": True,  # Reconocimiento de patrones
                "support_resistance_levels": 15,  # Niveles de soporte/resistencia
                "fibonacci_levels": True,  # Niveles de Fibonacci
            },
            
            # Análisis de tendencia
            "trend_analysis": {
                "trend_strength_threshold": 0.8,  # Umbral de fuerza de tendencia
                "trend_reversal_sensitivity": 0.6,  # Sensibilidad de reversión
                "trend_confirmation_periods": 5,  # Períodos de confirmación
                "adx_threshold": 30,  # Umbral de ADX
                "trend_line_detection": True,  # Detección de líneas de tendencia
            },
            
            # Análisis de volatilidad
            "volatility_analysis": {
                "volatility_threshold_high": 0.1,  # Umbral alto de volatilidad
                "volatility_threshold_low": 0.03,  # Umbral bajo de volatilidad
                "volatility_window": 50,  # Ventana de volatilidad
                "volatility_adjustment": True,  # Ajuste por volatilidad
                "vix_correlation": True,  # Correlación con VIX
            },
            
            # Análisis de volumen
            "volume_analysis": {
                "volume_spike_threshold": 4.0,  # Umbral de pico de volumen
                "volume_trend_periods": 30,  # Períodos de tendencia de volumen
                "obv_enabled": True,  # On-Balance Volume habilitado
                "volume_profile": True,  # Perfil de volumen
                "accumulation_distribution": True,  # Acumulación/Distribución
            },
            
            # Market Sentiment
            "sentiment_analysis": {
                "fear_greed_weight": 0.15,  # Peso del índice Fear & Greed
                "social_sentiment_weight": 0.15,  # Peso del sentimiento social
                "news_sentiment_weight": 0.4,  # Peso del sentimiento de noticias
                "technical_sentiment_weight": 0.3,  # Peso del sentimiento técnico
                "sentiment_update_interval": 120,  # Intervalo de actualización (2 min)
            },
            
            # Configuración de actualización
            "update_config": {
                "data_update_interval": 120,  # Intervalo de actualización de datos (2 min)
                "analysis_update_interval": 300,  # Intervalo de análisis (5 min)
                "cache_duration": 1800,  # Duración de caché (30 min)
                "real_time_analysis": False,  # Análisis en tiempo real deshabilitado
                "background_updates": True,  # Actualizaciones en segundo plano
            },
            
            # Configuración de alertas
            "alert_config": {
                "price_alert_threshold": 0.05,  # Umbral de alerta de precio (5%)
                "volume_alert_threshold": 1.5,  # Umbral de alerta de volumen
                "technical_alert_enabled": True,  # Alertas técnicas habilitadas
                "pattern_alert_enabled": True,  # Alertas de patrones habilitadas
                "breakout_alert_enabled": False,  # Alertas de breakout deshabilitadas
            },
            
            # Performance y optimización
            "performance_config": {
                "parallel_analysis": False,  # Análisis paralelo deshabilitado
                "max_concurrent_symbols": 3,  # Máximo símbolos concurrentes
                "memory_optimization": True,  # Optimización de memoria
                "data_compression": True,  # Compresión de datos
                "analysis_timeout": 120,  # Timeout de análisis (2 min)
            }
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_market_analyzer_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del market analyzer para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración del market analyzer
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in MarketAnalyzerProfiles.PROFILES:
        raise ValueError(f"Perfil de market analyzer no válido: {profile}")
    
    return MarketAnalyzerProfiles.PROFILES[profile]

def get_available_analyzer_profiles() -> List[str]:
    """Obtiene la lista de perfiles de market analyzer disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(MarketAnalyzerProfiles.PROFILES.keys())

def validate_analyzer_profile(profile: str) -> bool:
    """Valida si un perfil de market analyzer es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in MarketAnalyzerProfiles.PROFILES

def get_timeframes_config(profile: str = None) -> Dict[str, List[str]]:
    """Obtiene la configuración de timeframes para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los timeframes configurados
    """
    config = get_market_analyzer_config(profile)
    
    return {
        "primary_timeframes": config["primary_timeframes"],
        "secondary_timeframes": config["secondary_timeframes"],
        "trend_timeframes": config["trend_timeframes"]
    }

def get_technical_indicators_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de indicadores técnicos para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de indicadores técnicos
    """
    config = get_market_analyzer_config(profile)
    return config["technical_indicators"]

def get_signal_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de señales para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de señales
    """
    config = get_market_analyzer_config(profile)
    return config["signal_config"]

def get_update_intervals(profile: str = None) -> Dict[str, int]:
    """Obtiene los intervalos de actualización para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los intervalos de actualización
    """
    config = get_market_analyzer_config(profile)
    
    return {
        "data_update_interval": config["update_config"]["data_update_interval"],
        "analysis_update_interval": config["update_config"]["analysis_update_interval"],
        "cache_duration": config["update_config"]["cache_duration"]
    }

# ============================================================================
# 🛡️ CONFIGURACIÓN LEGACY PARA COMPATIBILIDAD
# ============================================================================

# Configuración legacy que mapea perfiles a configuraciones
MARKET_VALIDATOR_CONFIG = {
    "RAPIDO": MarketAnalyzerProfiles.PROFILES["RAPIDO"],
    "AGRESIVO": MarketAnalyzerProfiles.PROFILES["AGRESIVO"],
    "OPTIMO": MarketAnalyzerProfiles.PROFILES["OPTIMO"],
    "CONSERVADOR": MarketAnalyzerProfiles.PROFILES["CONSERVADOR"]
}

def validate_market_validator_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración de market validator.
    
    Args:
        config: Configuración a validar
        
    Returns:
        True si la configuración es válida
    """
    return True