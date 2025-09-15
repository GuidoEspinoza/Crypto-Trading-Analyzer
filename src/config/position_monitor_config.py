"""Configuraciones específicas del Position Monitor.

Este módulo contiene todas las configuraciones relacionadas con el monitoreo
de posiciones, incluyendo intervalos, alertas y parámetros de seguimiento.
"""

from typing import Dict, Any, List

# ============================================================================
# 📊 CONFIGURACIONES DE POSITION MONITOR POR PERFIL
# ============================================================================

class PositionMonitorProfiles:
    """Configuraciones específicas del Position Monitor por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Monitoring Intervals
            "monitor_interval": 10,  # Intervalo principal de monitoreo (segundos)
            "price_check_interval": 3,  # Intervalo de verificación de precios
            "status_update_interval": 30,  # Intervalo de actualización de estado
            "log_interval": 60,  # Intervalo de logging
            
            # Performance Monitoring
            "pnl_calculation_interval": 15,  # Intervalo de cálculo de P&L
            "performance_snapshot_interval": 300,  # Snapshot de rendimiento (5 min)
            "daily_summary_time": "23:59",  # Hora del resumen diario
            "weekly_summary_day": "sunday",  # Día del resumen semanal
            
            # Alert Thresholds
            "profit_alert_threshold": 0.05,  # Alerta de ganancia (5%)
            "loss_alert_threshold": 0.03,  # Alerta de pérdida (3%)
            "volume_spike_threshold": 3.0,  # Umbral de pico de volumen (3x)
            "price_change_alert": 0.02,  # Alerta de cambio de precio (2%)
            
            # Risk Monitoring
            "drawdown_alert_threshold": 0.04,  # Alerta de drawdown (4%)
            "correlation_check_interval": 120,  # Verificación de correlación (2 min)
            "volatility_spike_threshold": 2.5,  # Umbral de pico de volatilidad
            "liquidity_check_interval": 60,  # Verificación de liquidez (1 min)
            
            # Position Health Checks
            "stale_position_check": 300,  # Verificación de posiciones obsoletas (5 min)
            "unrealized_pnl_check": 30,  # Verificación de P&L no realizado
            "margin_check_interval": 60,  # Verificación de margen
            "exposure_check_interval": 45,  # Verificación de exposición
            
            # Data Collection
            "price_history_length": 1000,  # Longitud del historial de precios
            "trade_history_length": 500,  # Longitud del historial de trades
            "performance_history_days": 30,  # Días de historial de rendimiento
            "cache_cleanup_interval": 3600,  # Limpieza de cache (1 hora)
            
            # Notification Settings
            "enable_profit_notifications": True,  # Notificaciones de ganancia
            "enable_loss_notifications": True,  # Notificaciones de pérdida
            "enable_risk_notifications": True,  # Notificaciones de riesgo
            "notification_cooldown": 300,  # Cooldown de notificaciones (5 min)
            
            # Emergency Monitoring
            "emergency_check_interval": 5,  # Verificación de emergencia
            "circuit_breaker_monitoring": True,  # Monitoreo de circuit breaker
            "panic_mode_threshold": 0.1,  # Umbral de modo pánico (10%)
            "auto_close_on_emergency": True,  # Cierre automático en emergencia
        },
        
        "AGRESIVO": {
            # Monitoring Intervals
            "monitor_interval": 15,  # Intervalo principal de monitoreo (segundos)
            "price_check_interval": 5,  # Intervalo de verificación de precios
            "status_update_interval": 45,  # Intervalo de actualización de estado
            "log_interval": 90,  # Intervalo de logging
            
            # Performance Monitoring
            "pnl_calculation_interval": 20,  # Intervalo de cálculo de P&L
            "performance_snapshot_interval": 450,  # Snapshot de rendimiento (7.5 min)
            "daily_summary_time": "23:59",  # Hora del resumen diario
            "weekly_summary_day": "sunday",  # Día del resumen semanal
            
            # Alert Thresholds
            "profit_alert_threshold": 0.06,  # Alerta de ganancia (6%)
            "loss_alert_threshold": 0.04,  # Alerta de pérdida (4%)
            "volume_spike_threshold": 2.5,  # Umbral de pico de volumen (2.5x)
            "price_change_alert": 0.025,  # Alerta de cambio de precio (2.5%)
            
            # Risk Monitoring
            "drawdown_alert_threshold": 0.05,  # Alerta de drawdown (5%)
            "correlation_check_interval": 180,  # Verificación de correlación (3 min)
            "volatility_spike_threshold": 2.0,  # Umbral de pico de volatilidad
            "liquidity_check_interval": 90,  # Verificación de liquidez (1.5 min)
            
            # Position Health Checks
            "stale_position_check": 450,  # Verificación de posiciones obsoletas (7.5 min)
            "unrealized_pnl_check": 45,  # Verificación de P&L no realizado
            "margin_check_interval": 90,  # Verificación de margen
            "exposure_check_interval": 60,  # Verificación de exposición
            
            # Data Collection
            "price_history_length": 800,  # Longitud del historial de precios
            "trade_history_length": 400,  # Longitud del historial de trades
            "performance_history_days": 30,  # Días de historial de rendimiento
            "cache_cleanup_interval": 5400,  # Limpieza de cache (1.5 horas)
            
            # Notification Settings
            "enable_profit_notifications": True,  # Notificaciones de ganancia
            "enable_loss_notifications": True,  # Notificaciones de pérdida
            "enable_risk_notifications": True,  # Notificaciones de riesgo
            "notification_cooldown": 450,  # Cooldown de notificaciones (7.5 min)
            
            # Emergency Monitoring
            "emergency_check_interval": 8,  # Verificación de emergencia
            "circuit_breaker_monitoring": True,  # Monitoreo de circuit breaker
            "panic_mode_threshold": 0.12,  # Umbral de modo pánico (12%)
            "auto_close_on_emergency": True,  # Cierre automático en emergencia
        },
        
        "OPTIMO": {
            # Monitoring Intervals
            "monitor_interval": 30,  # Intervalo principal de monitoreo (segundos)
            "price_check_interval": 10,  # Intervalo de verificación de precios
            "status_update_interval": 60,  # Intervalo de actualización de estado
            "log_interval": 120,  # Intervalo de logging
            
            # Performance Monitoring
            "pnl_calculation_interval": 30,  # Intervalo de cálculo de P&L
            "performance_snapshot_interval": 600,  # Snapshot de rendimiento (10 min)
            "daily_summary_time": "23:59",  # Hora del resumen diario
            "weekly_summary_day": "sunday",  # Día del resumen semanal
            
            # Alert Thresholds
            "profit_alert_threshold": 0.08,  # Alerta de ganancia (8%)
            "loss_alert_threshold": 0.05,  # Alerta de pérdida (5%)
            "volume_spike_threshold": 2.0,  # Umbral de pico de volumen (2x)
            "price_change_alert": 0.03,  # Alerta de cambio de precio (3%)
            
            # Risk Monitoring
            "drawdown_alert_threshold": 0.06,  # Alerta de drawdown (6%)
            "correlation_check_interval": 300,  # Verificación de correlación (5 min)
            "volatility_spike_threshold": 1.8,  # Umbral de pico de volatilidad
            "liquidity_check_interval": 120,  # Verificación de liquidez (2 min)
            
            # Position Health Checks
            "stale_position_check": 600,  # Verificación de posiciones obsoletas (10 min)
            "unrealized_pnl_check": 60,  # Verificación de P&L no realizado
            "margin_check_interval": 120,  # Verificación de margen
            "exposure_check_interval": 90,  # Verificación de exposición
            
            # Data Collection
            "price_history_length": 600,  # Longitud del historial de precios
            "trade_history_length": 300,  # Longitud del historial de trades
            "performance_history_days": 60,  # Días de historial de rendimiento
            "cache_cleanup_interval": 7200,  # Limpieza de cache (2 horas)
            
            # Notification Settings
            "enable_profit_notifications": True,  # Notificaciones de ganancia
            "enable_loss_notifications": True,  # Notificaciones de pérdida
            "enable_risk_notifications": True,  # Notificaciones de riesgo
            "notification_cooldown": 600,  # Cooldown de notificaciones (10 min)
            
            # Emergency Monitoring
            "emergency_check_interval": 15,  # Verificación de emergencia
            "circuit_breaker_monitoring": True,  # Monitoreo de circuit breaker
            "panic_mode_threshold": 0.15,  # Umbral de modo pánico (15%)
            "auto_close_on_emergency": True,  # Cierre automático en emergencia
        },
        
        "CONSERVADOR": {
            # Monitoring Intervals
            "monitor_interval": 60,  # Intervalo principal de monitoreo (segundos)
            "price_check_interval": 20,  # Intervalo de verificación de precios
            "status_update_interval": 120,  # Intervalo de actualización de estado
            "log_interval": 180,  # Intervalo de logging
            
            # Performance Monitoring
            "pnl_calculation_interval": 60,  # Intervalo de cálculo de P&L
            "performance_snapshot_interval": 900,  # Snapshot de rendimiento (15 min)
            "daily_summary_time": "23:59",  # Hora del resumen diario
            "weekly_summary_day": "sunday",  # Día del resumen semanal
            
            # Alert Thresholds
            "profit_alert_threshold": 0.1,  # Alerta de ganancia (10%)
            "loss_alert_threshold": 0.06,  # Alerta de pérdida (6%)
            "volume_spike_threshold": 1.5,  # Umbral de pico de volumen (1.5x)
            "price_change_alert": 0.04,  # Alerta de cambio de precio (4%)
            
            # Risk Monitoring
            "drawdown_alert_threshold": 0.08,  # Alerta de drawdown (8%)
            "correlation_check_interval": 600,  # Verificación de correlación (10 min)
            "volatility_spike_threshold": 1.5,  # Umbral de pico de volatilidad
            "liquidity_check_interval": 180,  # Verificación de liquidez (3 min)
            
            # Position Health Checks
            "stale_position_check": 900,  # Verificación de posiciones obsoletas (15 min)
            "unrealized_pnl_check": 120,  # Verificación de P&L no realizado
            "margin_check_interval": 180,  # Verificación de margen
            "exposure_check_interval": 120,  # Verificación de exposición
            
            # Data Collection
            "price_history_length": 400,  # Longitud del historial de precios
            "trade_history_length": 200,  # Longitud del historial de trades
            "performance_history_days": 90,  # Días de historial de rendimiento
            "cache_cleanup_interval": 10800,  # Limpieza de cache (3 horas)
            
            # Notification Settings
            "enable_profit_notifications": True,  # Notificaciones de ganancia
            "enable_loss_notifications": True,  # Notificaciones de pérdida
            "enable_risk_notifications": True,  # Notificaciones de riesgo
            "notification_cooldown": 900,  # Cooldown de notificaciones (15 min)
            
            # Emergency Monitoring
            "emergency_check_interval": 30,  # Verificación de emergencia
            "circuit_breaker_monitoring": True,  # Monitoreo de circuit breaker
            "panic_mode_threshold": 0.2,  # Umbral de modo pánico (20%)
            "auto_close_on_emergency": False,  # Cierre automático deshabilitado
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_position_monitor_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del position monitor para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa el perfil por defecto
    
    Returns:
        Diccionario con la configuración del position monitor
    """
    from .trading_bot_config import TRADING_PROFILE
    
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in PositionMonitorProfiles.PROFILES:
        raise ValueError(f"Perfil de position monitor no válido: {profile}")
    
    return PositionMonitorProfiles.PROFILES[profile]

def get_available_monitor_profiles() -> List[str]:
    """Obtiene la lista de perfiles de position monitor disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(PositionMonitorProfiles.PROFILES.keys())

def validate_monitor_profile(profile: str) -> bool:
    """Valida si un perfil de position monitor es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in PositionMonitorProfiles.PROFILES

def get_monitoring_intervals(profile: str = None) -> Dict[str, int]:
    """Obtiene los intervalos de monitoreo para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los intervalos de monitoreo
    """
    config = get_position_monitor_config(profile)
    
    return {
        "monitor_interval": config["monitor_interval"],
        "price_check_interval": config["price_check_interval"],
        "status_update_interval": config["status_update_interval"],
        "log_interval": config["log_interval"],
        "pnl_calculation_interval": config["pnl_calculation_interval"]
    }

def get_alert_thresholds(profile: str = None) -> Dict[str, float]:
    """Obtiene los umbrales de alerta para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con los umbrales de alerta
    """
    config = get_position_monitor_config(profile)
    
    return {
        "profit_alert_threshold": config["profit_alert_threshold"],
        "loss_alert_threshold": config["loss_alert_threshold"],
        "volume_spike_threshold": config["volume_spike_threshold"],
        "price_change_alert": config["price_change_alert"],
        "drawdown_alert_threshold": config["drawdown_alert_threshold"]
    }

def get_notification_settings(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración de notificaciones para el perfil especificado.
    
    Args:
        profile: Perfil de trading
    
    Returns:
        Diccionario con la configuración de notificaciones
    """
    config = get_position_monitor_config(profile)
    
    return {
        "enable_profit_notifications": config["enable_profit_notifications"],
        "enable_loss_notifications": config["enable_loss_notifications"],
        "enable_risk_notifications": config["enable_risk_notifications"],
        "notification_cooldown": config["notification_cooldown"]
    }

# ============================================================================
# 📊 CONFIGURACIÓN GLOBAL EXPORTADA
# ============================================================================

# Configuración global del Position Monitor (para compatibilidad)
POSITION_MONITOR_CONFIG = PositionMonitorProfiles.PROFILES

def validate_position_monitor_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración de position monitor.
    
    Args:
        config: Configuración a validar
        
    Returns:
        True si la configuración es válida
    """
    return True