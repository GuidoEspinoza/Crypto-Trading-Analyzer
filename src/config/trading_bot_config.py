"""Configuraciones específicas del Trading Bot.

Este módulo contiene todas las configuraciones relacionadas con el comportamiento
del trading bot, incluyendo perfiles de trading, timeframes, límites y parámetros
de ejecución.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any

# Importar constantes globales centralizadas
from .global_constants import (
    GLOBAL_INITIAL_BALANCE,
    USDT_BASE_PRICE,
    TIMEZONE,
    DAILY_RESET_HOUR,
    DAILY_RESET_MINUTE,
    RESET_STRATEGIES,
    ACTIVE_RESET_STRATEGY
)

# ============================================================================
# 🎯 SELECTOR DE PERFIL DE TRADING - CAMBIAR AQUÍ
# ============================================================================

# 🔥 CAMBIAR ESTE VALOR PARA CAMBIAR TODO EL COMPORTAMIENTO DEL BOT
TRADING_PROFILE = "AGRESIVO"  # Opciones: "RAPIDO", "AGRESIVO", "OPTIMO", "CONSERVADOR"

# NOTA: Las constantes globales (GLOBAL_INITIAL_BALANCE, TIMEZONE, etc.) 
# ahora se importan desde global_constants.py para centralizar la configuración

# ============================================================================
# 📊 CONFIGURACIONES DE TRADING BOT POR PERFIL
# ============================================================================

class TradingBotProfiles:
    """Configuraciones específicas del Trading Bot por perfil."""
    
    PROFILES = {
        "RAPIDO": {
            # Trading Bot Core Config
            "cache_ttl_seconds": 120,  # TTL del cache en segundos (2 min)
            "event_queue_maxsize": 500,  # Tamaño máximo de la cola de eventos
            "executor_shutdown_timeout": 20,  # Timeout para shutdown del executor (seg)
            "thread_join_timeout": 8,  # Timeout para join de threads (seg)
            "analysis_future_timeout": 20,  # Timeout para análisis paralelo (seg)
            
            # Connection and Network Config
            "connection_timeout": 30,  # Timeout de conexión en segundos
            "read_timeout": 60,  # Timeout de lectura en segundos
            "retry_delay": 5,  # Delay entre reintentos en segundos
            "max_retries": 3,  # Número máximo de reintentos
            "backoff_factor": 2.0,  # Factor de backoff exponencial
            
            # Monitoring and Intervals Config
            "position_check_interval": 30,  # Intervalo de verificación de posiciones (seg)
            "market_data_refresh_interval": 60,  # Intervalo de actualización de datos (seg)
            "health_check_interval": 300,  # Intervalo de health check (seg)
            "log_rotation_interval": 3600,  # Intervalo de rotación de logs (seg)
            
            # Performance and Optimization Config
            "max_concurrent_requests": 10,  # Máximo de requests concurrentes
            "request_rate_limit": 100,  # Límite de requests por minuto
            "memory_threshold_mb": 512,  # Umbral de memoria en MB
            "cpu_threshold_percent": 80,  # Umbral de CPU en porcentaje
            
            # Error Handling Config
            "error_cooldown_seconds": 60,  # Tiempo de espera tras error (seg)
            "max_consecutive_errors": 5,  # Máximo errores consecutivos
            "circuit_breaker_threshold": 10,  # Umbral para circuit breaker
            "circuit_breaker_timeout": 300,  # Timeout del circuit breaker (seg)
            
            # Trade Spacing Config - Para evitar ejecución masiva post-reset
            "min_time_between_trades_seconds": 30,  # Mínimo 30 segundos entre trades
            "max_trades_per_hour": 15,  # Máximo 15 trades por hora
            "post_reset_spacing_minutes": 60,  # Espaciado especial en primera hora post-reset
            
            # Analysis Config
            "analysis_interval": 30,  # Intervalo de análisis en segundos (óptimo para scalping)
            "min_confidence": 65.0,  # Confianza mínima para trades
            "max_daily_trades": 20,  # Máximo trades diarios
            "max_positions": 8,  # Máximo posiciones simultáneas
            
            # Timeframes - Scalping y trading rápido
            "timeframes": ["1m", "3m", "5m", "15m"],
        },
        
        "AGRESIVO": {
            # Trading Bot Core Config
            "cache_ttl_seconds": 150,  # TTL del cache en segundos (2.5 min)
            "event_queue_maxsize": 600,  # Tamaño máximo de la cola de eventos
            "executor_shutdown_timeout": 25,  # Timeout para shutdown del executor (seg)
            "thread_join_timeout": 8,  # Timeout para join de threads (seg)
            "analysis_future_timeout": 25,  # Timeout para análisis paralelo (seg)
            
            # Connection and Network Config
            "connection_timeout": 25,  # Timeout de conexión más agresivo
            "read_timeout": 45,  # Timeout de lectura más rápido
            "retry_delay": 3,  # Delay entre reintentos más corto
            "max_retries": 5,  # Más reintentos para agresividad
            "backoff_factor": 1.5,  # Factor de backoff más agresivo
            
            # Monitoring and Intervals Config
            "position_check_interval": 20,  # Verificación más frecuente
            "market_data_refresh_interval": 45,  # Actualización más frecuente
            "health_check_interval": 240,  # Health check más frecuente
            "log_rotation_interval": 3600,  # Rotación de logs estándar
            
            # Performance and Optimization Config
            "max_concurrent_requests": 15,  # Más requests concurrentes
            "request_rate_limit": 150,  # Mayor límite de requests
            "memory_threshold_mb": 768,  # Mayor umbral de memoria
            "cpu_threshold_percent": 85,  # Mayor umbral de CPU
            
            # Error Handling Config
            "error_cooldown_seconds": 45,  # Menor tiempo de espera
            "max_consecutive_errors": 7,  # Más tolerancia a errores
            "circuit_breaker_threshold": 12,  # Mayor umbral para circuit breaker
            "circuit_breaker_timeout": 240,  # Menor timeout del circuit breaker
            
            # Trade Spacing Config
            "min_time_between_trades_seconds": 45,  # Espaciado moderado
            "max_trades_per_hour": 12,  # Límite moderado por hora
            "post_reset_spacing_minutes": 90,  # Espaciado post-reset moderado
            
            # Analysis Config
            "analysis_interval": 45,  # Intervalo de análisis en segundos (coherente con timeframes 5m-1h)
            "min_confidence": 72.0,  # Confianza mínima para trades
            "max_daily_trades": 15,  # Máximo trades diarios
            "max_positions": 7,  # Máximo posiciones simultáneas
            
            # Timeframes - Trading intradiario agresivo
            "timeframes": ["5m", "15m", "30m", "1h"],
        },
        
        "OPTIMO": {
            # Trading Bot Core Config
            "cache_ttl_seconds": 300,  # TTL del cache más largo (5 min)
            "event_queue_maxsize": 400,  # Cola más pequeña para estabilidad
            "executor_shutdown_timeout": 30,  # Timeout más largo para shutdown
            "thread_join_timeout": 12,  # Timeout más largo para threads
            "analysis_future_timeout": 35,  # Timeout más largo para análisis
            
            # Connection and Network Config
            "connection_timeout": 45,  # Timeout más conservador
            "read_timeout": 90,  # Timeout de lectura más largo
            "retry_delay": 8,  # Delay más largo entre reintentos
            "max_retries": 3,  # Reintentos conservadores
            "backoff_factor": 2.5,  # Factor de backoff más conservador
            
            # Monitoring and Intervals Config
            "position_check_interval": 60,  # Verificación menos frecuente
            "market_data_refresh_interval": 120,  # Actualización menos frecuente
            "health_check_interval": 600,  # Health check menos frecuente
            "log_rotation_interval": 7200,  # Rotación de logs menos frecuente
            
            # Performance and Optimization Config
            "max_concurrent_requests": 5,  # Menos requests concurrentes
            "request_rate_limit": 50,  # Menor límite de requests
            "memory_threshold_mb": 256,  # Menor umbral de memoria
            "cpu_threshold_percent": 70,  # Menor umbral de CPU
            
            # Error Handling Config
            "error_cooldown_seconds": 120,  # Mayor tiempo de espera tras error
            "max_consecutive_errors": 3,  # Menor tolerancia a errores
            "circuit_breaker_threshold": 5,  # Menor umbral para circuit breaker
            "circuit_breaker_timeout": 600,  # Mayor timeout del circuit breaker
            
            # Trade Spacing Config
            "min_time_between_trades_seconds": 120,  # Espaciado conservador
            "max_trades_per_hour": 6,  # Límite conservador por hora
            "post_reset_spacing_minutes": 180,  # Espaciado post-reset conservador
            
            # Analysis Config
            "analysis_interval": 60,  # Intervalo de análisis más largo
            "min_confidence": 78.0,  # Confianza alta para trades
            "max_daily_trades": 8,  # Máximo trades diarios conservador
            "max_positions": 4,  # Máximo posiciones simultáneas conservador
            
            # Timeframes - Swing trading balanceado
            "timeframes": ["30m", "1h", "4h", "1d"],
        },
        
        "CONSERVADOR": {
            # Trading Bot Core Config
            "cache_ttl_seconds": 600,  # TTL del cache muy largo (10 min)
            "event_queue_maxsize": 200,  # Cola pequeña para máxima estabilidad
            "executor_shutdown_timeout": 45,  # Timeout muy largo para shutdown
            "thread_join_timeout": 15,  # Timeout muy largo para threads
            "analysis_future_timeout": 60,  # Timeout muy largo para análisis
            
            # Connection and Network Config
            "connection_timeout": 60,  # Timeout muy conservador
            "read_timeout": 120,  # Timeout de lectura muy largo
            "retry_delay": 15,  # Delay muy largo entre reintentos
            "max_retries": 2,  # Pocos reintentos
            "backoff_factor": 3.0,  # Factor de backoff muy conservador
            
            # Monitoring and Intervals Config
            "position_check_interval": 120,  # Verificación muy poco frecuente
            "market_data_refresh_interval": 300,  # Actualización muy poco frecuente
            "health_check_interval": 1200,  # Health check muy poco frecuente
            "log_rotation_interval": 14400,  # Rotación de logs muy poco frecuente
            
            # Performance and Optimization Config
            "max_concurrent_requests": 3,  # Muy pocos requests concurrentes
            "request_rate_limit": 30,  # Límite muy bajo de requests
            "memory_threshold_mb": 128,  # Umbral muy bajo de memoria
            "cpu_threshold_percent": 60,  # Umbral muy bajo de CPU
            
            # Error Handling Config
            "error_cooldown_seconds": 300,  # Tiempo muy largo de espera tras error
            "max_consecutive_errors": 2,  # Muy poca tolerancia a errores
            "circuit_breaker_threshold": 3,  # Umbral muy bajo para circuit breaker
            "circuit_breaker_timeout": 1200,  # Timeout muy largo del circuit breaker
            
            # Trade Spacing Config
            "min_time_between_trades_seconds": 300,  # Espaciado muy conservador
            "max_trades_per_hour": 3,  # Límite muy conservador por hora
            "post_reset_spacing_minutes": 360,  # Espaciado post-reset muy conservador
            
            # Analysis Config
            "analysis_interval": 120,  # Intervalo de análisis muy largo
            "min_confidence": 85.0,  # Confianza muy alta para trades
            "max_daily_trades": 5,  # Máximo trades diarios muy conservador
            "max_positions": 3,  # Máximo posiciones simultáneas muy conservador
            
            # Timeframes - Trading de posición a largo plazo
            "timeframes": ["2h", "4h", "1d", "1w"],
        }
    }

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_trading_bot_config(profile: str = None) -> Dict[str, Any]:
    """Obtiene la configuración del trading bot para el perfil especificado.
    
    Args:
        profile: Perfil de trading (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
                Si es None, usa TRADING_PROFILE global
    
    Returns:
        Diccionario con la configuración del trading bot
    """
    if profile is None:
        profile = TRADING_PROFILE
    
    if profile not in TradingBotProfiles.PROFILES:
        raise ValueError(f"Perfil de trading bot no válido: {profile}")
    
    return TradingBotProfiles.PROFILES[profile]

def get_available_trading_bot_profiles() -> List[str]:
    """Obtiene la lista de perfiles de trading bot disponibles.
    
    Returns:
        Lista de nombres de perfiles disponibles
    """
    return list(TradingBotProfiles.PROFILES.keys())

def validate_trading_bot_profile(profile: str) -> bool:
    """Valida si un perfil de trading bot es válido.
    
    Args:
        profile: Nombre del perfil a validar
    
    Returns:
        True si el perfil es válido, False en caso contrario
    """
    return profile in TradingBotProfiles.PROFILES

def validate_trading_bot_config(config: Dict[str, Any]) -> bool:
    """Valida la configuración del trading bot.
    
    Args:
        config: Diccionario con la configuración a validar
    
    Returns:
        True si la configuración es válida, False en caso contrario
    """
    required_keys = [
        'cache_ttl_seconds', 'event_queue_maxsize', 'connection_timeout',
        'analysis_interval', 'min_confidence', 'max_daily_trades'
    ]
    
    for key in required_keys:
        if key not in config:
            return False
    
    return True

# ============================================================================
# 🎯 CONFIGURACIÓN EXPORTADA
# ============================================================================

# Variable que se importa desde config.py
TRADING_BOT_CONFIG = TradingBotProfiles.PROFILES