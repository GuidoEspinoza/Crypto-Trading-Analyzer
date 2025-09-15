"""Configuraciones específicas del Position Manager.

Este módulo contiene todas las configuraciones relacionadas con la gestión
de posiciones, incluyendo límites, timeouts y parámetros de monitoreo.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE POSITION MANAGER POR PERFIL
# ============================================================================

class PositionManagerProfiles:
    """Configuraciones específicas del Position Manager por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Position Limits
            "max_positions": 8,  # Máximo número de posiciones simultáneas
            "max_position_value": 500.0,  # Valor máximo por posición (USDT)
            "min_position_value": 5.0,  # Valor mínimo por posición (USDT)
            "max_total_exposure": 0.8,  # Exposición total máxima (80%)
            "position_size_increment": 0.1,  # Incremento de tamaño de posición
            
            # Stop Loss & Take Profit
            "default_stop_loss": 0.02,  # Stop loss por defecto (2%)
            "default_take_profit": 0.04,  # Take profit por defecto (4%)
            "max_stop_loss": 0.05,  # Stop loss máximo (5%)
            "min_take_profit": 0.02,  # Take profit mínimo (2%)
            "trailing_stop_activation": 0.03,  # Activación de trailing stop (3%)
            "trailing_stop_distance": 0.015,  # Distancia del trailing stop (1.5%)
            
            # Position Monitoring
            "position_check_interval": 15,  # Intervalo de verificación (segundos)
            "price_update_interval": 5,  # Intervalo de actualización de precios
            "position_timeout": 1800,  # Timeout de posición (30 min)
            "stale_position_threshold": 3600,  # Umbral de posición obsoleta (1 hora)
            
            # Risk Management
            "max_drawdown_per_position": 0.03,  # Drawdown máximo por posición (3%)
            "correlation_threshold": 0.7,  # Umbral de correlación
            "volatility_adjustment": True,  # Ajuste por volatilidad
            "dynamic_sizing": True,  # Tamaño dinámico de posición
            
            # Order Management
            "order_retry_attempts": 3,  # Intentos de reintento de órdenes
            "order_timeout": 30,  # Timeout de órdenes (segundos)
            "partial_fill_threshold": 0.9,  # Umbral de llenado parcial (90%)
            "slippage_tolerance": 0.005,  # Tolerancia al slippage (0.5%)
            
            # Position Scaling
            "scaling_enabled": True,  # Escalado de posiciones habilitado
            "scaling_intervals": [0.02, 0.04, 0.06],  # Intervalos de escalado
            "max_scale_attempts": 3,  # Máximo intentos de escalado
            "scale_size_multiplier": 0.5,  # Multiplicador de tamaño para escalado
            
            # Emergency Controls
            "emergency_close_threshold": 0.08,  # Umbral de cierre de emergencia (8%)
            "panic_sell_enabled": True,  # Venta de pánico habilitada
            "circuit_breaker_threshold": 0.15,  # Umbral del circuit breaker (15%)
            "max_daily_loss": 0.1,  # Pérdida diaria máxima (10%)
        },
        
        "AGRESIVO": {
            # Position Limits
            "max_positions": 6,  # Máximo número de posiciones simultáneas
            "max_position_value": 750.0,  # Valor máximo por posición (USDT)
            "min_position_value": 10.0,  # Valor mínimo por posición (USDT)
            "max_total_exposure": 0.7,  # Exposición total máxima (70%)
            "position_size_increment": 0.15,  # Incremento de tamaño de posición
            
            # Stop Loss & Take Profit
            "default_stop_loss": 0.025,  # Stop loss por defecto (2.5%)
            "default_take_profit": 0.05,  # Take profit por defecto (5%)
            "max_stop_loss": 0.06,  # Stop loss máximo (6%)
            "min_take_profit": 0.025,  # Take profit mínimo (2.5%)
            "trailing_stop_activation": 0.04,  # Activación de trailing stop (4%)
            "trailing_stop_distance": 0.02,  # Distancia del trailing stop (2%)
            
            # Position Monitoring
            "position_check_interval": 20,  # Intervalo de verificación (segundos)
            "price_update_interval": 8,  # Intervalo de actualización de precios
            "position_timeout": 2700,  # Timeout de posición (45 min)
            "stale_position_threshold": 5400,  # Umbral de posición obsoleta (1.5 horas)
            
            # Risk Management
            "max_drawdown_per_position": 0.04,  # Drawdown máximo por posición (4%)
            "correlation_threshold": 0.65,  # Umbral de correlación
            "volatility_adjustment": True,  # Ajuste por volatilidad
            "dynamic_sizing": True,  # Tamaño dinámico de posición
            
            # Order Management
            "order_retry_attempts": 3,  # Intentos de reintento de órdenes
            "order_timeout": 45,  # Timeout de órdenes (segundos)
            "partial_fill_threshold": 0.85,  # Umbral de llenado parcial (85%)
            "slippage_tolerance": 0.008,  # Tolerancia al slippage (0.8%)
            
            # Position Scaling
            "scaling_enabled": True,  # Escalado de posiciones habilitado
            "scaling_intervals": [0.025, 0.05, 0.075],  # Intervalos de escalado
            "max_scale_attempts": 2,  # Máximo intentos de escalado
            "scale_size_multiplier": 0.6,  # Multiplicador de tamaño para escalado
            
            # Emergency Controls
            "emergency_close_threshold": 0.1,  # Umbral de cierre de emergencia (10%)
            "panic_sell_enabled": True,  # Venta de pánico habilitada
            "circuit_breaker_threshold": 0.18,  # Umbral del circuit breaker (18%)
            "max_daily_loss": 0.12,  # Pérdida diaria máxima (12%)
        },
        
        "OPTIMO": {
            # Position Limits
            "max_positions": 4,  # Máximo número de posiciones simultáneas
            "max_position_value": 1000.0,  # Valor máximo por posición (USDT)
            "min_position_value": 15.0,  # Valor mínimo por posición (USDT)
            "max_total_exposure": 0.6,  # Exposición total máxima (60%)
            "position_size_increment": 0.2,  # Incremento de tamaño de posición
            
            # Stop Loss & Take Profit
            "default_stop_loss": 0.03,  # Stop loss por defecto (3%)
            "default_take_profit": 0.06,  # Take profit por defecto (6%)
            "max_stop_loss": 0.07,  # Stop loss máximo (7%)
            "min_take_profit": 0.03,  # Take profit mínimo (3%)
            "trailing_stop_activation": 0.05,  # Activación de trailing stop (5%)
            "trailing_stop_distance": 0.025,  # Distancia del trailing stop (2.5%)
            
            # Position Monitoring
            "position_check_interval": 30,  # Intervalo de verificación (segundos)
            "price_update_interval": 10,  # Intervalo de actualización de precios
            "position_timeout": 3600,  # Timeout de posición (1 hora)
            "stale_position_threshold": 7200,  # Umbral de posición obsoleta (2 horas)
            
            # Risk Management
            "max_drawdown_per_position": 0.05,  # Drawdown máximo por posición (5%)
            "correlation_threshold": 0.6,  # Umbral de correlación
            "volatility_adjustment": True,  # Ajuste por volatilidad
            "dynamic_sizing": True,  # Tamaño dinámico de posición
            
            # Order Management
            "order_retry_attempts": 2,  # Intentos de reintento de órdenes
            "order_timeout": 60,  # Timeout de órdenes (segundos)
            "partial_fill_threshold": 0.8,  # Umbral de llenado parcial (80%)
            "slippage_tolerance": 0.01,  # Tolerancia al slippage (1%)
            
            # Position Scaling
            "scaling_enabled": True,  # Escalado de posiciones habilitado
            "scaling_intervals": [0.03, 0.06],  # Intervalos de escalado
            "max_scale_attempts": 2,  # Máximo intentos de escalado
            "scale_size_multiplier": 0.7,  # Multiplicador de tamaño para escalado
            
            # Emergency Controls
            "emergency_close_threshold": 0.12,  # Umbral de cierre de emergencia (12%)
            "panic_sell_enabled": True,  # Venta de pánico habilitada
            "circuit_breaker_threshold": 0.2,  # Umbral del circuit breaker (20%)
            "max_daily_loss": 0.15,  # Pérdida diaria máxima (15%)
        },
        
        "CONSERVADOR": {
            # Position Limits
            "max_positions": 3,  # Máximo número de posiciones simultáneas
            "max_position_value": 1500.0,  # Valor máximo por posición (USDT)
            "min_position_value": 25.0,  # Valor mínimo por posición (USDT)
            "max_total_exposure": 0.4,  # Exposición total máxima (40%)
            "position_size_increment": 0.25,  # Incremento de tamaño de posición
            
            # Stop Loss & Take Profit
            "default_stop_loss": 0.04,  # Stop loss por defecto (4%)
            "default_take_profit": 0.08,  # Take profit por defecto (8%)
            "max_stop_loss": 0.08,  # Stop loss máximo (8%)
            "min_take_profit": 0.04,  # Take profit mínimo (4%)
            "trailing_stop_activation": 0.06,  # Activación de trailing stop (6%)
            "trailing_stop_distance": 0.03,  # Distancia del trailing stop (3%)
            
            # Position Monitoring
            "position_check_interval": 60,  # Intervalo de verificación (segundos)
            "price_update_interval": 15,  # Intervalo de actualización de precios
            "position_timeout": 7200,  # Timeout de posición (2 horas)
            "stale_position_threshold": 14400,  # Umbral de posición obsoleta (4 horas)
            
            # Risk Management
            "max_drawdown_per_position": 0.06,  # Drawdown máximo por posición (6%)
            "correlation_threshold": 0.5,  # Umbral de correlación
            "volatility_adjustment": True,  # Ajuste por volatilidad
            "dynamic_sizing": False,  # Tamaño dinámico de posición deshabilitado
            
            # Order Management
            "order_retry_attempts": 2,  # Intentos de reintento de órdenes
            "order_timeout": 90,  # Timeout de órdenes (segundos)
            "partial_fill_threshold": 0.75,  # Umbral de llenado parcial (75%)
            "slippage_tolerance": 0.015,  # Tolerancia al slippage (1.5%)
            
            # Position Scaling
            "scaling_enabled": False,  # Escalado de posiciones deshabilitado
            "scaling_intervals": [0.04],  # Intervalos de escalado
            "max_scale_attempts": 1,  # Máximo intentos de escalado
            "scale_size_multiplier": 0.5,  # Multiplicador de tamaño para escalado
            
            # Emergency Controls
            "emergency_close_threshold": 0.15,  # Umbral de cierre de emergencia (15%)
            "panic_sell_enabled": False,  # Venta de pánico deshabilitada
            "circuit_breaker_threshold": 0.25,  # Umbral del circuit breaker (25%)
            "max_daily_loss": 0.08,  # Pérdida diaria máxima (8%)
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_position_manager_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del position manager para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración del position manager
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in PositionManagerProfiles.PROFILES:
        raise ValueError(f"Perfil de position manager no válido: {profile}")
    
    return PositionManagerProfiles.PROFILES[profile]

def get_available_position_manager_profiles() -> List[str]:
    """Obtiene la lista de perfiles de position manager disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(PositionManagerProfiles.PROFILES.keys())

def validate_position_manager_profile(profile: str) -> bool:
    """Valida si un perfil de position manager es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in PositionManagerProfiles.PROFILES

def get_position_limits(profile: str = None) -> Dict[str, Any]:
    """Obtiene los límites de posición para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los límites de posición
    """
    config = get_position_manager_config(profile)
    
    return {
        "max_positions": config["max_positions"],
        "max_position_value": config["max_position_value"],
        "min_position_value": config["min_position_value"],
        "max_total_exposure": config["max_total_exposure"],
        "position_size_increment": config["position_size_increment"]
    }

def get_risk_parameters(profile: str = None) -> Dict[str, Any]:
    """Obtiene los parámetros de riesgo para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los parámetros de riesgo
    """
    config = get_position_manager_config(profile)
    
    return {
        "default_stop_loss": config["default_stop_loss"],
        "default_take_profit": config["default_take_profit"],
        "max_stop_loss": config["max_stop_loss"],
        "min_take_profit": config["min_take_profit"],
        "trailing_stop_activation": config["trailing_stop_activation"],
        "trailing_stop_distance": config["trailing_stop_distance"],
        "max_drawdown_per_position": config["max_drawdown_per_position"]
    }

def get_monitoring_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de monitoreo para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de monitoreo
    """
    config = get_position_manager_config(profile)
    
    return {
        "position_check_interval": config["position_check_interval"],
        "price_update_interval": config["price_update_interval"],
        "position_timeout": config["position_timeout"],
        "stale_position_threshold": config["stale_position_threshold"]
    }

# ============================================================================
# 📊 FUNCIONES DE VALIDACIÓN
# ============================================================================

def validate_position_manager_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración del Position Manager.
    
    Args:
        config: Configuración a validar
    
    Returns:
        True si la configuración es válida, False en caso contrario
    """
    required_keys = [
        'max_positions', 'max_position_value', 'min_position_value',
        'default_stop_loss', 'default_take_profit', 'position_check_interval'
    ]
    
    # Verificar que existan las claves requeridas
    for key in required_keys:
        if key not in config:
            return False
    
    # Validar rangos de valores
    if config.get('max_positions', 0) <= 0:
        return False
    if config.get('max_position_value', 0) <= config.get('min_position_value', 0):
        return False
    if not (0 < config.get('default_stop_loss', 0) < 1):
        return False
    if not (0 < config.get('default_take_profit', 0) < 1):
        return False
    if config.get('position_check_interval', 0) <= 0:
        return False
    
    return True

# ============================================================================
# 📊 CONSTANTE DE CONFIGURACIÓN PARA COMPATIBILIDAD
# ============================================================================

# Constante que expone todos los perfiles para compatibilidad con imports
POSITION_MANAGER_CONFIG = PositionManagerProfiles.PROFILES