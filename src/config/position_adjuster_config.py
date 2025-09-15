"""Configuraciones específicas del Position Adjuster.

Este módulo contiene todas las configuraciones relacionadas con el ajuste
de posiciones, incluyendo umbrales, intervalos y parámetros de optimización.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE POSITION ADJUSTER POR PERFIL
# ============================================================================

class PositionAdjusterProfiles:
    """Configuraciones específicas del Position Adjuster por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Adjustment Triggers
            "profit_adjustment_threshold": 0.03,  # Umbral de ajuste por ganancia (3%)
            "loss_adjustment_threshold": 0.02,  # Umbral de ajuste por pérdida (2%)
            "volatility_adjustment_threshold": 0.05,  # Umbral de ajuste por volatilidad (5%)
            "time_based_adjustment_interval": 900,  # Ajuste basado en tiempo (15 min)
            
            # Stop Loss Adjustments
            "dynamic_sl_enabled": True,  # Stop loss dinámico habilitado
            "sl_adjustment_step": 0.005,  # Paso de ajuste de SL (0.5%)
            "min_sl_distance": 0.01,  # Distancia mínima de SL (1%)
            "max_sl_distance": 0.05,  # Distancia máxima de SL (5%)
            "sl_trailing_activation": 0.02,  # Activación de trailing SL (2%)
            
            # Take Profit Adjustments
            "dynamic_tp_enabled": True,  # Take profit dinámico habilitado
            "tp_adjustment_step": 0.01,  # Paso de ajuste de TP (1%)
            "min_tp_distance": 0.02,  # Distancia mínima de TP (2%)
            "max_tp_distance": 0.15,  # Distancia máxima de TP (15%)
            "tp_scaling_factor": 1.5,  # Factor de escalado de TP
            
            # Position Size Adjustments
            "size_adjustment_enabled": True,  # Ajuste de tamaño habilitado
            "size_increase_threshold": 0.025,  # Umbral para aumentar tamaño (2.5%)
            "size_decrease_threshold": 0.015,  # Umbral para disminuir tamaño (1.5%)
            "max_size_adjustment": 0.5,  # Ajuste máximo de tamaño (50%)
            "min_position_size": 0.1,  # Tamaño mínimo de posición (10%)
            
            # Risk-Based Adjustments
            "risk_adjustment_enabled": True,  # Ajuste basado en riesgo habilitado
            "correlation_adjustment_threshold": 0.7,  # Umbral de ajuste por correlación
            "drawdown_adjustment_threshold": 0.03,  # Umbral de ajuste por drawdown (3%)
            "volatility_scaling_factor": 0.8,  # Factor de escalado por volatilidad
            
            # Market Condition Adjustments
            "trend_adjustment_enabled": True,  # Ajuste por tendencia habilitado
            "trend_strength_threshold": 0.6,  # Umbral de fuerza de tendencia
            "sideways_market_detection": True,  # Detección de mercado lateral
            "news_impact_adjustment": True,  # Ajuste por impacto de noticias
            
            # Timing and Frequency
            "adjustment_check_interval": 60,  # Intervalo de verificación (1 min)
            "max_adjustments_per_hour": 6,  # Máximo ajustes por hora
            "adjustment_cooldown": 300,  # Cooldown entre ajustes (5 min)
            "emergency_adjustment_enabled": True,  # Ajustes de emergencia habilitados
            
            # Performance Optimization
            "performance_tracking_enabled": True,  # Seguimiento de rendimiento habilitado
            "adjustment_success_threshold": 0.7,  # Umbral de éxito de ajustes (70%)
            "learning_rate": 0.1,  # Tasa de aprendizaje para optimización
            "adaptive_thresholds": True,  # Umbrales adaptativos habilitados
        },
        
        "AGRESIVO": {
            # Adjustment Triggers
            "profit_adjustment_threshold": 0.04,  # Umbral de ajuste por ganancia (4%)
            "loss_adjustment_threshold": 0.025,  # Umbral de ajuste por pérdida (2.5%)
            "volatility_adjustment_threshold": 0.06,  # Umbral de ajuste por volatilidad (6%)
            "time_based_adjustment_interval": 1200,  # Ajuste basado en tiempo (20 min)
            
            # Stop Loss Adjustments
            "dynamic_sl_enabled": True,  # Stop loss dinámico habilitado
            "sl_adjustment_step": 0.008,  # Paso de ajuste de SL (0.8%)
            "min_sl_distance": 0.015,  # Distancia mínima de SL (1.5%)
            "max_sl_distance": 0.06,  # Distancia máxima de SL (6%)
            "sl_trailing_activation": 0.025,  # Activación de trailing SL (2.5%)
            
            # Take Profit Adjustments
            "dynamic_tp_enabled": True,  # Take profit dinámico habilitado
            "tp_adjustment_step": 0.012,  # Paso de ajuste de TP (1.2%)
            "min_tp_distance": 0.025,  # Distancia mínima de TP (2.5%)
            "max_tp_distance": 0.18,  # Distancia máxima de TP (18%)
            "tp_scaling_factor": 1.4,  # Factor de escalado de TP
            
            # Position Size Adjustments
            "size_adjustment_enabled": True,  # Ajuste de tamaño habilitado
            "size_increase_threshold": 0.03,  # Umbral para aumentar tamaño (3%)
            "size_decrease_threshold": 0.02,  # Umbral para disminuir tamaño (2%)
            "max_size_adjustment": 0.4,  # Ajuste máximo de tamaño (40%)
            "min_position_size": 0.15,  # Tamaño mínimo de posición (15%)
            
            # Risk-Based Adjustments
            "risk_adjustment_enabled": True,  # Ajuste basado en riesgo habilitado
            "correlation_adjustment_threshold": 0.65,  # Umbral de ajuste por correlación
            "drawdown_adjustment_threshold": 0.04,  # Umbral de ajuste por drawdown (4%)
            "volatility_scaling_factor": 0.75,  # Factor de escalado por volatilidad
            
            # Market Condition Adjustments
            "trend_adjustment_enabled": True,  # Ajuste por tendencia habilitado
            "trend_strength_threshold": 0.65,  # Umbral de fuerza de tendencia
            "sideways_market_detection": True,  # Detección de mercado lateral
            "news_impact_adjustment": True,  # Ajuste por impacto de noticias
            
            # Timing and Frequency
            "adjustment_check_interval": 90,  # Intervalo de verificación (1.5 min)
            "max_adjustments_per_hour": 4,  # Máximo ajustes por hora
            "adjustment_cooldown": 450,  # Cooldown entre ajustes (7.5 min)
            "emergency_adjustment_enabled": True,  # Ajustes de emergencia habilitados
            
            # Performance Optimization
            "performance_tracking_enabled": True,  # Seguimiento de rendimiento habilitado
            "adjustment_success_threshold": 0.65,  # Umbral de éxito de ajustes (65%)
            "learning_rate": 0.08,  # Tasa de aprendizaje para optimización
            "adaptive_thresholds": True,  # Umbrales adaptativos habilitados
        },
        
        "OPTIMO": {
            # Adjustment Triggers
            "profit_adjustment_threshold": 0.05,  # Umbral de ajuste por ganancia (5%)
            "loss_adjustment_threshold": 0.03,  # Umbral de ajuste por pérdida (3%)
            "volatility_adjustment_threshold": 0.08,  # Umbral de ajuste por volatilidad (8%)
            "time_based_adjustment_interval": 1800,  # Ajuste basado en tiempo (30 min)
            
            # Stop Loss Adjustments
            "dynamic_sl_enabled": True,  # Stop loss dinámico habilitado
            "sl_adjustment_step": 0.01,  # Paso de ajuste de SL (1%)
            "min_sl_distance": 0.02,  # Distancia mínima de SL (2%)
            "max_sl_distance": 0.08,  # Distancia máxima de SL (8%)
            "sl_trailing_activation": 0.03,  # Activación de trailing SL (3%)
            
            # Take Profit Adjustments
            "dynamic_tp_enabled": True,  # Take profit dinámico habilitado
            "tp_adjustment_step": 0.015,  # Paso de ajuste de TP (1.5%)
            "min_tp_distance": 0.03,  # Distancia mínima de TP (3%)
            "max_tp_distance": 0.2,  # Distancia máxima de TP (20%)
            "tp_scaling_factor": 1.3,  # Factor de escalado de TP
            
            # Position Size Adjustments
            "size_adjustment_enabled": True,  # Ajuste de tamaño habilitado
            "size_increase_threshold": 0.04,  # Umbral para aumentar tamaño (4%)
            "size_decrease_threshold": 0.025,  # Umbral para disminuir tamaño (2.5%)
            "max_size_adjustment": 0.3,  # Ajuste máximo de tamaño (30%)
            "min_position_size": 0.2,  # Tamaño mínimo de posición (20%)
            
            # Risk-Based Adjustments
            "risk_adjustment_enabled": True,  # Ajuste basado en riesgo habilitado
            "correlation_adjustment_threshold": 0.6,  # Umbral de ajuste por correlación
            "drawdown_adjustment_threshold": 0.05,  # Umbral de ajuste por drawdown (5%)
            "volatility_scaling_factor": 0.7,  # Factor de escalado por volatilidad
            
            # Market Condition Adjustments
            "trend_adjustment_enabled": True,  # Ajuste por tendencia habilitado
            "trend_strength_threshold": 0.7,  # Umbral de fuerza de tendencia
            "sideways_market_detection": True,  # Detección de mercado lateral
            "news_impact_adjustment": True,  # Ajuste por impacto de noticias
            
            # Timing and Frequency
            "adjustment_check_interval": 120,  # Intervalo de verificación (2 min)
            "max_adjustments_per_hour": 3,  # Máximo ajustes por hora
            "adjustment_cooldown": 600,  # Cooldown entre ajustes (10 min)
            "emergency_adjustment_enabled": True,  # Ajustes de emergencia habilitados
            
            # Performance Optimization
            "performance_tracking_enabled": True,  # Seguimiento de rendimiento habilitado
            "adjustment_success_threshold": 0.75,  # Umbral de éxito de ajustes (75%)
            "learning_rate": 0.05,  # Tasa de aprendizaje para optimización
            "adaptive_thresholds": True,  # Umbrales adaptativos habilitados
        },
        
        "CONSERVADOR": {
            # Adjustment Triggers
            "profit_adjustment_threshold": 0.08,  # Umbral de ajuste por ganancia (8%)
            "loss_adjustment_threshold": 0.04,  # Umbral de ajuste por pérdida (4%)
            "volatility_adjustment_threshold": 0.1,  # Umbral de ajuste por volatilidad (10%)
            "time_based_adjustment_interval": 3600,  # Ajuste basado en tiempo (1 hora)
            
            # Stop Loss Adjustments
            "dynamic_sl_enabled": True,  # Stop loss dinámico habilitado
            "sl_adjustment_step": 0.015,  # Paso de ajuste de SL (1.5%)
            "min_sl_distance": 0.03,  # Distancia mínima de SL (3%)
            "max_sl_distance": 0.1,  # Distancia máxima de SL (10%)
            "sl_trailing_activation": 0.05,  # Activación de trailing SL (5%)
            
            # Take Profit Adjustments
            "dynamic_tp_enabled": True,  # Take profit dinámico habilitado
            "tp_adjustment_step": 0.02,  # Paso de ajuste de TP (2%)
            "min_tp_distance": 0.05,  # Distancia mínima de TP (5%)
            "max_tp_distance": 0.25,  # Distancia máxima de TP (25%)
            "tp_scaling_factor": 1.2,  # Factor de escalado de TP
            
            # Position Size Adjustments
            "size_adjustment_enabled": False,  # Ajuste de tamaño deshabilitado
            "size_increase_threshold": 0.06,  # Umbral para aumentar tamaño (6%)
            "size_decrease_threshold": 0.04,  # Umbral para disminuir tamaño (4%)
            "max_size_adjustment": 0.2,  # Ajuste máximo de tamaño (20%)
            "min_position_size": 0.25,  # Tamaño mínimo de posición (25%)
            
            # Risk-Based Adjustments
            "risk_adjustment_enabled": True,  # Ajuste basado en riesgo habilitado
            "correlation_adjustment_threshold": 0.5,  # Umbral de ajuste por correlación
            "drawdown_adjustment_threshold": 0.06,  # Umbral de ajuste por drawdown (6%)
            "volatility_scaling_factor": 0.6,  # Factor de escalado por volatilidad
            
            # Market Condition Adjustments
            "trend_adjustment_enabled": True,  # Ajuste por tendencia habilitado
            "trend_strength_threshold": 0.8,  # Umbral de fuerza de tendencia
            "sideways_market_detection": True,  # Detección de mercado lateral
            "news_impact_adjustment": False,  # Ajuste por impacto de noticias deshabilitado
            
            # Timing and Frequency
            "adjustment_check_interval": 300,  # Intervalo de verificación (5 min)
            "max_adjustments_per_hour": 2,  # Máximo ajustes por hora
            "adjustment_cooldown": 1800,  # Cooldown entre ajustes (30 min)
            "emergency_adjustment_enabled": False,  # Ajustes de emergencia deshabilitados
            
            # Performance Optimization
            "performance_tracking_enabled": True,  # Seguimiento de rendimiento habilitado
            "adjustment_success_threshold": 0.8,  # Umbral de éxito de ajustes (80%)
            "learning_rate": 0.03,  # Tasa de aprendizaje para optimización
            "adaptive_thresholds": False,  # Umbrales adaptativos deshabilitados
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_position_adjuster_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del position adjuster para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración del position adjuster
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in PositionAdjusterProfiles.PROFILES:
        raise ValueError(f"Perfil de position adjuster no válido: {profile}")
    
    return PositionAdjusterProfiles.PROFILES[profile]

def get_available_adjuster_profiles() -> List[str]:
    """Obtiene la lista de perfiles de position adjuster disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(PositionAdjusterProfiles.PROFILES.keys())

def validate_adjuster_profile(profile: str) -> bool:
    """Valida si un perfil de position adjuster es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in PositionAdjusterProfiles.PROFILES

def get_adjustment_thresholds(profile: str = None) -> Dict[str, float]:
    """Obtiene los umbrales de ajuste para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los umbrales de ajuste
    """
    config = get_position_adjuster_config(profile)
    
    return {
        "profit_adjustment_threshold": config["profit_adjustment_threshold"],
        "loss_adjustment_threshold": config["loss_adjustment_threshold"],
        "volatility_adjustment_threshold": config["volatility_adjustment_threshold"],
        "drawdown_adjustment_threshold": config["drawdown_adjustment_threshold"]
    }

def get_sl_tp_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de Stop Loss y Take Profit para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de SL/TP
    """
    config = get_position_adjuster_config(profile)
    
    return {
        "dynamic_sl_enabled": config["dynamic_sl_enabled"],
        "sl_adjustment_step": config["sl_adjustment_step"],
        "min_sl_distance": config["min_sl_distance"],
        "max_sl_distance": config["max_sl_distance"],
        "dynamic_tp_enabled": config["dynamic_tp_enabled"],
        "tp_adjustment_step": config["tp_adjustment_step"],
        "min_tp_distance": config["min_tp_distance"],
        "max_tp_distance": config["max_tp_distance"]
    }

def get_timing_config(profile: str = None) -> Dict[str, int]:
    """Obtiene la configuración de timing para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de timing
    """
    config = get_position_adjuster_config(profile)
    
    return {
        "adjustment_check_interval": config["adjustment_check_interval"],
        "max_adjustments_per_hour": config["max_adjustments_per_hour"],
        "adjustment_cooldown": config["adjustment_cooldown"],
        "time_based_adjustment_interval": config["time_based_adjustment_interval"]
    }