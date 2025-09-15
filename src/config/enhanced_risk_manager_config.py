"""Configuraciones específicas del Risk Manager.

Este módulo contiene todas las configuraciones relacionadas con la gestión de riesgo,
incluyendo límites de posición, drawdown, correlaciones y parámetros de protección.
"""

from typing import Dict, Any, List

# ============================================================================
# 🛡️ CONFIGURACIONES DE RISK MANAGER POR PERFIL
# ============================================================================

class RiskManagerProfiles:
    """Configuraciones específicas del Risk Manager por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Risk Manager Core Config
            "max_risk_per_trade": 1.5,  # Riesgo máximo por trade (%)
            "max_daily_risk": 6.0,  # Riesgo máximo diario (%)
            "max_drawdown_threshold": 0.10,  # Drawdown máximo (10% como decimal)
            "correlation_threshold": 0.75,  # Umbral de correlación
            "min_position_size": 12.0,  # Tamaño mínimo de posición (USDT)
            "risk_max_position_size": 0.8,  # Tamaño máximo de posición (80% como decimal)
            
            # Kelly Criterion Config
            "kelly_fraction": 0.28,  # Fracción de Kelly optimizada
            "kelly_win_rate": 0.65,  # Tasa de ganancia asumida
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly
            
            # Volatility and ATR Config
            "volatility_adjustment": 1.25,  # Factor de ajuste por volatilidad
            "atr_multiplier_min": 1.8,  # Multiplicador ATR mínimo
            "atr_multiplier_max": 2.8,  # Multiplicador ATR máximo
            "atr_default": 1.8,  # ATR por defecto
            "atr_volatile": 2.8,  # ATR para mercados volátiles
            "atr_sideways": 1.4,  # ATR para mercados laterales
            
            # Stop Loss and Take Profit Config
            "tp_min_percentage": 2.5,  # Take Profit mínimo (%)
            "tp_max_percentage": 5.5,  # Take Profit máximo (%)
            "sl_min_percentage": 0.8,  # Stop Loss mínimo (%)
            "sl_max_percentage": 2.5,  # Stop Loss máximo (%)
            "tp_increment_percentage": 1.0,  # Incremento base de TP (%)
            "max_tp_adjustments": 5,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.7,  # Umbral confianza para ajustar TP
            
            # Trailing Stop Config
            "trailing_stop_activation": 0.15,  # Activación trailing stop (15% como decimal)
            "breakeven_threshold": 0.6,  # Umbral para breakeven
            "intelligent_trailing": True,  # Trailing inteligente activado
            "default_trailing_distance": 2.0,  # Distancia de trailing por defecto (%)
            
            # Position Sizing Config
            "dynamic_position_sizing": True,  # Tamaño dinámico de posición
            "default_leverage": 1.0,  # Leverage por defecto
            "tp_increment_base_pct": 1.0,  # Incremento base de TP (%)
            
            # Daily Limits Config
            "max_daily_loss_percent": 5.0,  # Pérdida máxima diaria (%)
            "min_confidence_threshold": 0.6,  # Confianza mínima para trades
            "position_size_multiplier": 1.0,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 1.2,  # Factor de ajuste por volatilidad
        },
        
        "AGRESIVO": {
            # Risk Manager Core Config
            "max_risk_per_trade": 1.0,  # Riesgo máximo por trade (%)
            "max_daily_risk": 4.5,  # Riesgo máximo diario (%)
            "max_drawdown_threshold": 0.08,  # Drawdown máximo (8% como decimal)
            "correlation_threshold": 0.65,  # Umbral de correlación
            "min_position_size": 8.0,  # Tamaño mínimo de posición (USDT)
            "risk_max_position_size": 0.6,  # Tamaño máximo de posición (60% como decimal)
            
            # Kelly Criterion Config
            "kelly_fraction": 0.20,  # Fracción de Kelly conservadora
            "kelly_win_rate": 0.68,  # Tasa de ganancia asumida
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly
            
            # Volatility and ATR Config
            "volatility_adjustment": 1.10,  # Factor de ajuste por volatilidad
            "atr_multiplier_min": 2.2,  # Multiplicador ATR mínimo
            "atr_multiplier_max": 3.8,  # Multiplicador ATR máximo
            "atr_default": 2.5,  # ATR por defecto
            "atr_volatile": 3.8,  # ATR para mercados volátiles
            "atr_sideways": 2.2,  # ATR para mercados laterales
            
            # Stop Loss and Take Profit Config
            "tp_min_percentage": 3.0,  # Take Profit mínimo (%)
            "tp_max_percentage": 6.0,  # Take Profit máximo (%)
            "sl_min_percentage": 1.0,  # Stop Loss mínimo (%)
            "sl_max_percentage": 3.0,  # Stop Loss máximo (%)
            "tp_increment_percentage": 1.0,  # Incremento base de TP (%)
            "max_tp_adjustments": 5,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.7,  # Umbral confianza para ajustar TP
            
            # Trailing Stop Config
            "trailing_stop_activation": 0.15,  # Activación trailing stop (15% como decimal)
            "breakeven_threshold": 0.8,  # Umbral para breakeven
            "intelligent_trailing": True,  # Trailing inteligente activado
            "default_trailing_distance": 2.2,  # Distancia de trailing por defecto (%)
            
            # Position Sizing Config
            "dynamic_position_sizing": True,  # Tamaño dinámico de posición
            "default_leverage": 1.0,  # Leverage por defecto
            "tp_increment_base_pct": 1.3,  # Incremento base de TP (%)
            
            # Daily Limits Config
            "max_daily_loss_percent": 4.0,  # Pérdida máxima diaria (%)
            "min_confidence_threshold": 0.65,  # Confianza mínima para trades
            "position_size_multiplier": 1.2,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 1.3,  # Factor de ajuste por volatilidad
        },
        
        "OPTIMO": {
            # Risk Manager Core Config
            "max_risk_per_trade": 0.8,  # Riesgo máximo por trade (%)
            "max_daily_risk": 3.0,  # Riesgo máximo diario (%)
            "max_drawdown_threshold": 0.06,  # Drawdown máximo (6% como decimal)
            "correlation_threshold": 0.55,  # Umbral de correlación
            "min_position_size": 15.0,  # Tamaño mínimo de posición (USDT)
            "risk_max_position_size": 0.4,  # Tamaño máximo de posición (40% como decimal)
            
            # Kelly Criterion Config
            "kelly_fraction": 0.15,  # Fracción de Kelly conservadora
            "kelly_win_rate": 0.72,  # Tasa de ganancia asumida
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly
            
            # Volatility and ATR Config
            "volatility_adjustment": 0.95,  # Factor de ajuste por volatilidad
            "atr_multiplier_min": 2.8,  # Multiplicador ATR mínimo
            "atr_multiplier_max": 4.5,  # Multiplicador ATR máximo
            "atr_default": 3.2,  # ATR por defecto
            "atr_volatile": 4.5,  # ATR para mercados volátiles
            "atr_sideways": 2.8,  # ATR para mercados laterales
            
            # Stop Loss and Take Profit Config
            "tp_min_percentage": 4.0,  # Take Profit mínimo (%)
            "tp_max_percentage": 8.0,  # Take Profit máximo (%)
            "sl_min_percentage": 1.2,  # Stop Loss mínimo (%)
            "sl_max_percentage": 3.5,  # Stop Loss máximo (%)
            "tp_increment_percentage": 1.5,  # Incremento base de TP (%)
            "max_tp_adjustments": 4,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.75,  # Umbral confianza para ajustar TP
            
            # Trailing Stop Config
            "trailing_stop_activation": 0.20,  # Activación trailing stop (20% como decimal)
            "breakeven_threshold": 1.0,  # Umbral para breakeven
            "intelligent_trailing": True,  # Trailing inteligente activado
            "default_trailing_distance": 2.8,  # Distancia de trailing por defecto (%)
            
            # Position Sizing Config
            "dynamic_position_sizing": True,  # Tamaño dinámico de posición
            "default_leverage": 1.0,  # Leverage por defecto
            "tp_increment_base_pct": 1.8,  # Incremento base de TP (%)
            
            # Daily Limits Config
            "max_daily_loss_percent": 3.0,  # Pérdida máxima diaria (%)
            "min_confidence_threshold": 0.72,  # Confianza mínima para trades
            "position_size_multiplier": 0.8,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 0.9,  # Factor de ajuste por volatilidad
        },
        
        "CONSERVADOR": {
            # Risk Manager Core Config
            "max_risk_per_trade": 0.5,  # Riesgo máximo por trade (%)
            "max_daily_risk": 2.0,  # Riesgo máximo diario (%)
            "max_drawdown_threshold": 0.04,  # Drawdown máximo (4% como decimal)
            "correlation_threshold": 0.45,  # Umbral de correlación
            "min_position_size": 20.0,  # Tamaño mínimo de posición (USDT)
            "risk_max_position_size": 0.25,  # Tamaño máximo de posición (25% como decimal)
            
            # Kelly Criterion Config
            "kelly_fraction": 0.10,  # Fracción de Kelly muy conservadora
            "kelly_win_rate": 0.75,  # Tasa de ganancia asumida
            "kelly_avg_loss": 1.0,  # Pérdida promedio para Kelly
            
            # Volatility and ATR Config
            "volatility_adjustment": 0.80,  # Factor de ajuste por volatilidad
            "atr_multiplier_min": 3.5,  # Multiplicador ATR mínimo
            "atr_multiplier_max": 5.5,  # Multiplicador ATR máximo
            "atr_default": 4.0,  # ATR por defecto
            "atr_volatile": 5.5,  # ATR para mercados volátiles
            "atr_sideways": 3.5,  # ATR para mercados laterales
            
            # Stop Loss and Take Profit Config
            "tp_min_percentage": 5.0,  # Take Profit mínimo (%)
            "tp_max_percentage": 10.0,  # Take Profit máximo (%)
            "sl_min_percentage": 1.5,  # Stop Loss mínimo (%)
            "sl_max_percentage": 4.0,  # Stop Loss máximo (%)
            "tp_increment_percentage": 2.0,  # Incremento base de TP (%)
            "max_tp_adjustments": 3,  # Máximo ajustes de TP
            "tp_confidence_threshold": 0.8,  # Umbral confianza para ajustar TP
            
            # Trailing Stop Config
            "trailing_stop_activation": 0.25,  # Activación trailing stop (25% como decimal)
            "breakeven_threshold": 1.5,  # Umbral para breakeven
            "intelligent_trailing": True,  # Trailing inteligente activado
            "default_trailing_distance": 3.5,  # Distancia de trailing por defecto (%)
            
            # Position Sizing Config
            "dynamic_position_sizing": True,  # Tamaño dinámico de posición
            "default_leverage": 1.0,  # Leverage por defecto
            "tp_increment_base_pct": 2.5,  # Incremento base de TP (%)
            
            # Daily Limits Config
            "max_daily_loss_percent": 2.0,  # Pérdida máxima diaria (%)
            "min_confidence_threshold": 0.8,  # Confianza mínima para trades
            "position_size_multiplier": 0.6,  # Multiplicador de tamaño de posición
            "volatility_adjustment_factor": 0.7,  # Factor de ajuste por volatilidad
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_risk_manager_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del risk manager para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración del risk manager
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in RiskManagerProfiles.PROFILES:
        raise ValueError(f"Perfil de risk manager no válido: {profile}")
    
    return RiskManagerProfiles.PROFILES[profile]

def get_available_risk_manager_profiles() -> List[str]:
    """Obtiene la lista de perfiles de risk manager disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(RiskManagerProfiles.PROFILES.keys())

def validate_risk_manager_profile(profile: str) -> bool:
    """Valida si un perfil de risk manager es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in RiskManagerProfiles.PROFILES

def get_risk_limits(profile: str = None) -> Dict[str, float]:
    """Obtiene los límites de riesgo para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los límites de riesgo
    """
    config = get_risk_manager_config(profile)
    
    return {
        "max_risk_per_trade": config["max_risk_per_trade"],
        "max_daily_risk": config["max_daily_risk"],
        "max_drawdown_threshold": config["max_drawdown_threshold"],
        "max_daily_loss_percent": config["max_daily_loss_percent"],
        "min_confidence_threshold": config["min_confidence_threshold"]
    }

def get_position_sizing_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de tamaño de posición para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de tamaño de posición
    """
    config = get_risk_manager_config(profile)
    
    return {
        "min_position_size": config["min_position_size"],
        "risk_max_position_size": config["risk_max_position_size"],
        "kelly_fraction": config["kelly_fraction"],
        "dynamic_position_sizing": config["dynamic_position_sizing"],
        "position_size_multiplier": config["position_size_multiplier"]
    }

# ============================================================================
# 🛡️ CONFIGURACIÓN LEGACY PARA COMPATIBILIDAD
# ============================================================================

# Configuración legacy que mapea perfiles a configuraciones
ENHANCED_RISK_MANAGER_CONFIG = {
    "RAPIDO": RiskManagerProfiles.PROFILES["RAPIDO"],
    "AGRESIVO": RiskManagerProfiles.PROFILES["AGRESIVO"],
    "OPTIMO": RiskManagerProfiles.PROFILES["OPTIMO"],
    "CONSERVADOR": RiskManagerProfiles.PROFILES["CONSERVADOR"]
}

def validate_enhanced_risk_manager_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración de enhanced risk manager.
    
    Args:
        config: Configuración a validar
        
    Returns:
        True si la configuración es válida
    """
    return True