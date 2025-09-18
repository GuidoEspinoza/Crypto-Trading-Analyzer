#!/usr/bin/env python3
"""🌐 Constantes Globales del Sistema de Trading

Este módulo centraliza todas las constantes globales compartidas entre módulos,
proporcionando un punto único de configuración para valores fundamentales
del sistema.

Constantes incluidas:
- Balance inicial global
- Configuración de monedas base
- Zona horaria y configuración temporal
- Estrategias de reset
- Límites y umbrales globales
"""

from typing import Dict, Any, List, Union

# ============================================================================
# 💰 CONFIGURACIÓN FINANCIERA GLOBAL
# ============================================================================

# Balance inicial global para todas las posiciones en USDT
# Este valor se usa en:
# - PaperTrader para simulación
# - DatabaseConfig para configuración inicial
# - Tests para configuración de pruebas
GLOBAL_INITIAL_BALANCE: float = 1000.0

# Precio base de USDT (stablecoin)
# Usado como referencia para conversiones y cálculos
USDT_BASE_PRICE: float = 1.0

# Moneda base del sistema
BASE_CURRENCY: str = "USDT"

# ============================================================================
# 🪙 SÍMBOLOS DE TRADING CENTRALIZADOS
# ============================================================================

# Selección basada en alta liquidez, volatilidad y volumen de trading
SYMBOLS: List[str] = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT"
]

# Símbolos para testing (subconjunto de los principales)
TEST_SYMBOLS: List[str] = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# ============================================================================
# ⏰ CONFIGURACIÓN TEMPORAL GLOBAL
# ============================================================================

# Zona horaria para Chile (CLT/CLST)
# Usado en:
# - TradingBot para programación de operaciones
# - DatabaseManager para timestamps
# - Logging para marcas de tiempo
TIMEZONE: str = "America/Santiago"

# Alias para compatibilidad con código existente
CHILE_TZ: str = TIMEZONE

# Horario de reset diario optimizado para trading de criptomonedas en Chile
# Basado en análisis de volatilidad: mejor horario 11:30 AM - 6:00 PM CLT
# Reset configurado a las 11:00 AM CLT para preparar el bot antes del horario óptimo
DAILY_RESET_HOUR: int = 11  # 11:00 AM CLT
DAILY_RESET_MINUTE: int = 0  # 11:00 AM exacto

# ============================================================================
# 🔄 ESTRATEGIAS DE RESET TEMPORAL
# ============================================================================

# Configuración alternativa para diferentes estrategias de reset:
# - CONSERVATIVE: 6:00 AM CLT (antes de mercados globales)
# - AGGRESSIVE: 11:00 AM CLT (antes del horario óptimo de trading)
# - OPTIMAL: 6:00 PM CLT (después del horario óptimo de trading)
RESET_STRATEGIES: Dict[str, Dict[str, int]] = {
    "CONSERVATIVE": {"hour": 6, "minute": 0},   # 6:00 AM CLT
    "AGGRESSIVE": {"hour": 11, "minute": 0},    # 11:00 AM CLT (RECOMENDADO)
    "OPTIMAL": {"hour": 18, "minute": 0}        # 6:00 PM CLT
}

# Estrategia de reset activa (cambiar según perfil de trading)
ACTIVE_RESET_STRATEGY: str = "AGGRESSIVE"  # Recomendado para máxima rentabilidad

# ═══════════════════════════════════════════════════════════
# 🔄 CONFIGURACIÓN DE CIERRE PRE-RESET
# ═══════════════════════════════════════════════════════════
PRE_RESET_CLOSURE_CONFIG: Dict[str, Union[bool, int, float]] = {
    # Configuración principal
    "enabled": True,                    # Habilitar/deshabilitar funcionalidad
    "minutes_before_reset": 15,         # Minutos antes del reset para cerrar (10:45 AM)
    "min_profit_threshold": 0.5,        # Ganancia mínima requerida (%)
    
    # Configuración de ejecución
    "max_positions_per_batch": 10,      # Máximo número de posiciones a cerrar por lote
    "retry_attempts": 3,                # Intentos de reintento por posición
    "retry_delay_seconds": 30,          # Delay entre reintentos (segundos)
    
    # Configuración de logging
    "log_detailed_operations": True,    # Log detallado de cada operación
    "send_notifications": True,         # Enviar notificaciones de cierre
    
    # Configuración de seguridad
    "require_manual_confirmation": False, # Requerir confirmación manual
    "emergency_stop_enabled": True,     # Habilitar parada de emergencia
}

# ============================================================================
# 🎯 PERFIL ACTIVO DEL SISTEMA
# ============================================================================

# Perfil de trading activo del sistema
# Opciones disponibles: RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR
# Este valor se usa en ConfigManager para determinar la configuración activa
ACTIVE_TRADING_PROFILE: str = "OPTIMO"  # Perfil balanceado recomendado

# ============================================================================
# 🎯 LÍMITES Y UMBRALES GLOBALES
# ============================================================================

# Límites de posiciones globales
MAX_GLOBAL_POSITIONS: int = 10
MAX_DAILY_TRADES_GLOBAL: int = 50

# Umbrales de riesgo globales
MAX_GLOBAL_DRAWDOWN: float = 0.20  # 20% máximo drawdown
MIN_CONFIDENCE_THRESHOLD_GLOBAL: float = 70.0  # 70% confianza mínima

# Timeouts y límites de tiempo
DEFAULT_TIMEOUT_SECONDS: int = 30
MAX_RETRY_ATTEMPTS: int = 3

# ============================================================================
# 📊 CONFIGURACIÓN DE CACHE GLOBAL
# ============================================================================

# TTL por defecto para cache (en segundos)
DEFAULT_CACHE_TTL: int = 300  # 5 minutos

# Tamaño máximo de cache
MAX_CACHE_SIZE: int = 1000

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD
# ============================================================================

def get_reset_config(strategy: str = None) -> Dict[str, int]:
    """🔄 Obtener configuración de reset según estrategia
    
    Args:
        strategy: Estrategia de reset (CONSERVATIVE, AGGRESSIVE, OPTIMAL)
                 Si es None, usa ACTIVE_RESET_STRATEGY
    
    Returns:
        Dict con hour y minute para el reset
    """
    if strategy is None:
        strategy = ACTIVE_RESET_STRATEGY
    
    return RESET_STRATEGIES.get(strategy, RESET_STRATEGIES["AGGRESSIVE"])


def get_global_financial_config() -> Dict[str, Any]:
    """💰 Obtener configuración financiera global
    
    Returns:
        Dict con configuración financiera centralizada
    """
    return {
        "initial_balance": GLOBAL_INITIAL_BALANCE,
        "base_price": USDT_BASE_PRICE,
        "base_currency": BASE_CURRENCY,
        "max_positions": MAX_GLOBAL_POSITIONS,
        "max_daily_trades": MAX_DAILY_TRADES_GLOBAL,
        "max_drawdown": MAX_GLOBAL_DRAWDOWN
    }


def get_global_temporal_config() -> Dict[str, Any]:
    """⏰ Obtener configuración temporal global
    
    Returns:
        Dict con configuración temporal centralizada
    """
    return {
        "timezone": TIMEZONE,
        "reset_hour": DAILY_RESET_HOUR,
        "reset_minute": DAILY_RESET_MINUTE,
        "reset_strategy": ACTIVE_RESET_STRATEGY,
        "reset_config": get_reset_config()
    }


def validate_global_constants() -> Dict[str, bool]:
    """✅ Validar que las constantes globales están en rangos válidos
    
    Returns:
        Dict con resultados de validación
    """
    validations = {
        "balance_valid": GLOBAL_INITIAL_BALANCE > 0,
        "usdt_price_valid": USDT_BASE_PRICE > 0,
        "reset_hour_valid": 0 <= DAILY_RESET_HOUR <= 23,
        "reset_minute_valid": 0 <= DAILY_RESET_MINUTE <= 59,
        "max_positions_valid": MAX_GLOBAL_POSITIONS > 0,
        "max_drawdown_valid": 0 < MAX_GLOBAL_DRAWDOWN <= 1.0,
        "confidence_threshold_valid": 0 < MIN_CONFIDENCE_THRESHOLD_GLOBAL <= 100,
        "cache_ttl_valid": DEFAULT_CACHE_TTL > 0,
        "timeout_valid": DEFAULT_TIMEOUT_SECONDS > 0,
        "retry_attempts_valid": MAX_RETRY_ATTEMPTS > 0
    }
    
    validations["all_valid"] = all(validations.values())
    return validations


# ============================================================================
# 📋 EXPORTACIONES
# ============================================================================

__all__ = [
    # Constantes financieras
    "GLOBAL_INITIAL_BALANCE",
    "USDT_BASE_PRICE", 
    "BASE_CURRENCY",
    
    # Símbolos de trading
    "SYMBOLS",
    "TEST_SYMBOLS",
    
    # Constantes temporales
    "TIMEZONE",
    "DAILY_RESET_HOUR",
    "DAILY_RESET_MINUTE",
    "RESET_STRATEGIES",
    "ACTIVE_RESET_STRATEGY",
    
    # Perfil activo
    "ACTIVE_TRADING_PROFILE",
    
    # Límites globales
    "MAX_GLOBAL_POSITIONS",
    "MAX_DAILY_TRADES_GLOBAL",
    "MAX_GLOBAL_DRAWDOWN",
    "MIN_CONFIDENCE_THRESHOLD_GLOBAL",
    
    # Configuración de sistema
    "DEFAULT_TIMEOUT_SECONDS",
    "MAX_RETRY_ATTEMPTS",
    "DEFAULT_CACHE_TTL",
    "MAX_CACHE_SIZE",
    
    # Funciones de utilidad
    "get_reset_config",
    "get_global_financial_config",
    "get_global_temporal_config",
    "validate_global_constants"
]