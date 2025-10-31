# ============================================================================
# ⏰ CONFIGURACIÓN DE HORARIOS Y TIEMPO DE TRADING
# ============================================================================
"""
Configuración centralizada de horarios de trading para el sistema de trading automatizado.

Este módulo define los horarios de operación, zonas horarias, y configuraciones
temporales que determinan cuándo el bot puede operar según diferentes perfiles
de trading (Scalping e Intraday).

Características principales:
- Configuración de zona horaria (UTC para portabilidad global)
- Horarios de trading inteligentes por perfil
- Configuración de trading en fines de semana
- Horarios de reinicio diario del sistema
- Programación flexible por días de la semana

Autor: Sistema de Trading Automatizado
Versión: 2.0
Última actualización: 2024
"""

import pytz
from datetime import datetime, time

# Importar configuración de símbolos para mantener consistencia
from .symbols_config import (
    GLOBAL_SYMBOLS,
    CRYPTO_MAJOR,
    CRYPTO_LARGE_CAP,
    CRYPTO_EMERGING,
    FOREX_MAJOR,
    FOREX_MINOR,
    FOREX_EXOTIC,
    METALS_PRECIOUS,
    ENERGY_COMMODITIES,
    AGRICULTURAL,
    METALS_INDUSTRIAL,
    INDICES_US,
    INDICES_EUROPE,
    INDICES_ASIA,
)

# ============================================================================
# 🌍 CONFIGURACIÓN DE ZONA HORARIA
# ============================================================================

# Zona horaria principal del sistema (UTC)
TIMEZONE = "UTC"  # UTC - Zona horaria universal para portabilidad global
UTC_TZ = pytz.timezone(TIMEZONE)  # Objeto timezone para conversiones

# ============================================================================
# 🔄 CONFIGURACIÓN DE REINICIO DIARIO
# ============================================================================

# Hora de reinicio diario del sistema (formato 24h)
# Este es el momento en que se resetean contadores, estadísticas y límites diarios
DAILY_RESET_HOUR = 0  # Medianoche (00:00)
DAILY_RESET_MINUTE = 0   # Minuto exacto del reinicio

# ============================================================================
# 🕐 HORARIOS DE TRADING INTELIGENTES
# ============================================================================

# 🚨 IMPORTANTE: Estos horarios están optimizados para máxima volatilidad
# y liquidez aprovechando las sesiones de mercados globales

SMART_TRADING_HOURS = {
    # === HORARIO PRINCIPAL DE TRADING ===
    # Optimizado para aprovechar superposición Europa-América
    "start_time": "11:00",  # 11:00 UTC - Apertura mercados europeos (era 08:00 Chile)
    "end_time": "02:30",  # 02:30 UTC - Cierre extendido mercados asiáticos (era 23:30 Chile)
    # === HORARIO EXTENDIDO (24/7 CRYPTO) ===
    # Para trading agresivo aprovechando mercados asiáticos
    "extended_start": "09:00",  # 09:00 UTC - Inicio muy temprano (era 06:00 Chile)
    "extended_end": "02:59",  # 02:59 UTC - Casi 24/7 (era 23:59 Chile)
    # === HORARIO NOCTURNO (SESIÓN ASIÁTICA) ===
    # Aprovecha alta volatilidad en mercados asiáticos
    "night_start": "01:00",  # 01:00 UTC - Inicio sesión asiática (era 22:00 Chile)
    "night_end": "11:00",  # 11:00 UTC - Fin sesión asiática (era 08:00 Chile)
    # === SESIONES DE ALTA VOLATILIDAD ===
    # Horarios específicos para máxima actividad
    "high_volatility_sessions": {
        "asian_open": {"start": "22:00", "end": "02:00"},  # Apertura asiática (UTC)
        "london_open": {"start": "08:00", "end": "12:00"},  # Apertura Londres (UTC)
        "ny_open": {"start": "14:30", "end": "18:30"},  # Apertura NY (UTC)
        "overlap_london_ny": {
            "start": "14:30",
            "end": "17:00",
        },  # Superposición Londres-NY (UTC)
    },
    # === CONFIGURACIÓN AVANZADA ===
    "enabled": True,  # Habilitar horarios inteligentes
    "timezone": "UTC",  # Zona horaria base
}

# ============================================================================
# 📅 PROGRAMACIÓN SEMANAL DE TRADING
# ============================================================================

# Configuración de días y horarios de trading por día de la semana
# Formato: día_semana: {"activo": bool, "horario": "tipo_horario"}
TRADING_SCHEDULE = {
    # === DÍAS LABORALES ===
    # Máxima actividad durante días de semana
    "monday": {
        "active": True,
        "schedule_type": "principal",  # Usa horario principal
        "description": "Lunes - Inicio de semana, alta volatilidad",
    },
    "tuesday": {
        "active": True,
        "schedule_type": "principal",
        "description": "Martes - Continuidad de tendencias semanales",
    },
    "wednesday": {
        "active": True,
        "schedule_type": "principal",
        "description": "Miércoles - Punto medio, movimientos balanceados",
    },
    "thursday": {
        "active": True,
        "schedule_type": "principal",
        "description": "Jueves - Preparación para cierre semanal",
    },
    "friday": {
        "active": True,
        "schedule_type": "principal",
        "description": "Viernes - Cierre semanal, posibles reversiones",
    },
    # === FINES DE SEMANA ===
    # Actividad habilitada para criptomonedas (mercado 24/7)
    "saturday": {
        "active": True,  # ✅ HABILITADO para aprovechar mercado crypto 24/7
        "schedule_type": "weekend_crypto",
        "description": "Sábado - Mercado crypto activo, menor competencia institucional",
    },
    "sunday": {
        "active": True,  # ✅ HABILITADO para preparación semanal
        "schedule_type": "weekend_crypto",
        "description": "Domingo - Posicionamiento para apertura semanal",
    },
}

# ============================================================================
# 🏃‍♂️ CONFIGURACIÓN DE TRADING EN FINES DE SEMANA POR PERFIL
# ============================================================================

# Trading de fin de semana para perfil SCALPING
# Aprovecha la menor competencia institucional y movimientos únicos del weekend
SCALPING_WEEKEND_TRADING = {
    "enabled": True,  # ✅ HABILITADO para aprovechar mercado crypto 24/7
    "saturday": {
        "active": True,  # ✅ Activo los sábados
        "start_time": "11:00",  # 11:00 UTC - Inicio temprano (era 08:00 Chile)
        "end_time": "01:00",  # 01:00 UTC - Sesión extendida (era 22:00 Chile)
        "max_trades": 15,  # Límite aumentado para fin de semana
        "min_confidence": 70.0,  # Confianza ligeramente reducida (más oportunidades)
        "description": "Sábado Scalping - Aprovechando menor competencia institucional",
    },
    "sunday": {
        "active": True,  # ✅ Activo los domingos
        "start_time": "13:00",  # 13:00 UTC - Inicio moderado (era 10:00 Chile)
        "end_time": "02:00",  # 02:00 UTC - Hasta tarde (era 23:00 Chile)
        "max_trades": 12,  # Límite moderado para preparación semanal
        "min_confidence": 72.0,  # Confianza moderada
        "description": "Domingo Scalping - Posicionamiento para nueva semana",
    },
}

# Trading de fin de semana para perfil INTRADAY
# Conservador pero activo, enfocado en movimientos de calidad en crypto 24/7
INTRADAY_WEEKEND_TRADING = {
    "enabled": True,  # ✅ HABILITADO para aprovechar oportunidades crypto weekend
    "saturday": {
        "active": True,  # ✅ Activo los sábados
        "start_time": "12:00",  # 12:00 UTC - Inicio moderado (era 09:00 Chile)
        "end_time": "23:00",  # 23:00 UTC - Sesión extendida (era 20:00 Chile)
        "max_trades": 8,  # Límite moderado para weekend
        "min_confidence": 78.0,  # Confianza alta pero accesible
        "description": "Sábado Intraday - Señales de calidad con menor competencia",
    },
    "sunday": {
        "active": True,  # ✅ Activo los domingos
        "start_time": "15:00",  # 15:00 UTC - Inicio tarde (era 12:00 Chile)
        "end_time": "01:00",  # 01:00 UTC - Hasta tarde (era 22:00 Chile)
        "max_trades": 6,  # Límite conservador para preparación
        "min_confidence": 80.0,  # Confianza alta para calidad
        "description": "Domingo Intraday - Posicionamiento estratégico semanal",
    },
}

# ============================================================================
# 📊 CONFIGURACIÓN DE HORARIOS POR PERFIL DE TRADING
# ============================================================================

# Mapeo de horarios específicos para cada perfil de trading
PROFILE_TRADING_SCHEDULE = {
    # === PERFIL SCALPING ===
    # Horarios extendidos para aprovechar más oportunidades
    "SCALPING": {
        "weekday_schedule": "extended",  # Usa horario extendido en días laborales
        "weekend_config": SCALPING_WEEKEND_TRADING,
        "night_trading": True,  # Permite trading nocturno
        "early_start": True,  # Inicio temprano activado
        "late_end": True,  # Fin tardío activado
        "description": "Horarios extendidos para máximas oportunidades de scalping",
    },
    # === PERFIL INTRADAY ===
    # Horarios principales para trading de calidad
    "INTRADAY": {
        "weekday_schedule": "principal",  # Usa horario principal solamente
        "weekend_config": INTRADAY_WEEKEND_TRADING,
        "night_trading": False,  # Sin trading nocturno
        "early_start": False,  # Sin inicio temprano
        "late_end": False,  # Sin fin tardío
        "description": "Horarios principales para trading intraday de calidad",
    },
}

# ============================================================================
# 🔧 FUNCIONES DE UTILIDAD PARA HORARIOS
# ============================================================================


def get_trading_hours_for_profile(profile_name: str) -> dict:
    """
    Obtiene la configuración de horarios para un perfil específico.

    Args:
        profile_name (str): Nombre del perfil ("SCALPING" o "INTRADAY")

    Returns:
        dict: Configuración de horarios del perfil
    """
    return PROFILE_TRADING_SCHEDULE.get(
        profile_name, PROFILE_TRADING_SCHEDULE["INTRADAY"]
    )


def is_weekend_trading_enabled(profile_name: str) -> bool:
    """
    Verifica si el trading en fin de semana está habilitado para un perfil.

    Args:
        profile_name (str): Nombre del perfil

    Returns:
        bool: True si el trading de fin de semana está habilitado
    """
    profile_config = get_trading_hours_for_profile(profile_name)
    return profile_config["weekend_config"]["enabled"]


def get_active_trading_days() -> list:
    """
    Obtiene la lista de días en que el trading está activo.

    Returns:
        list: Lista de días activos para trading
    """
    return [day for day, config in TRADING_SCHEDULE.items() if config["active"]]


def get_schedule_info() -> dict:
    """
    Obtiene información resumida de la configuración de horarios.

    Returns:
        dict: Diccionario con información de horarios
    """
    return {
        "timezone": TIMEZONE,
        "daily_reset": f"{DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d}",
        "principal_hours": f"{SMART_TRADING_HOURS['start_time']} - {SMART_TRADING_HOURS['end_time']}",
        "extended_hours": f"{SMART_TRADING_HOURS['extended_start']} - {SMART_TRADING_HOURS['extended_end']}",
        "active_days": get_active_trading_days(),
        "weekend_scalping": SCALPING_WEEKEND_TRADING["enabled"],
        "weekend_intraday": INTRADAY_WEEKEND_TRADING["enabled"],
    }


# ============================================================================
# 🌍 CONFIGURACIÓN ESPECÍFICA POR TIPO DE MERCADO
# ============================================================================

# Función auxiliar para obtener símbolos por categoría desde GLOBAL_SYMBOLS
def _get_symbols_by_category(category_type: str) -> list:
    """
    Obtiene símbolos de GLOBAL_SYMBOLS filtrados por categoría.
    
    Args:
        category_type: Tipo de categoría ('crypto', 'forex', 'commodities', 'indices')
    
    Returns:
        list: Lista de símbolos de la categoría especificada
    """
    if category_type == "crypto":
        # Obtener todos los símbolos crypto de GLOBAL_SYMBOLS
        crypto_symbols = CRYPTO_MAJOR + CRYPTO_LARGE_CAP[:4] + CRYPTO_EMERGING[:2]
        return crypto_symbols
    
    elif category_type == "forex":
        # Obtener todos los símbolos forex de GLOBAL_SYMBOLS
        forex_symbols = FOREX_MAJOR + FOREX_MINOR[:3] + FOREX_EXOTIC[:2]
        return forex_symbols
    
    elif category_type == "commodities":
        # Obtener todos los símbolos commodities de GLOBAL_SYMBOLS
        commodities_symbols = METALS_PRECIOUS + ENERGY_COMMODITIES[:2] + AGRICULTURAL[:2] + METALS_INDUSTRIAL[:2]
        return commodities_symbols
    
    elif category_type == "indices":
        # Obtener todos los símbolos índices de GLOBAL_SYMBOLS
        indices_symbols = INDICES_US + INDICES_EUROPE[:2] + INDICES_ASIA[:2]
        return indices_symbols
    
    return []

# Configuración optimizada según volatilidad y características de cada mercado
MARKET_SPECIFIC_CONFIG = {
    "crypto": {
        "high_volatility_hours": {
            # Horarios de mayor volatilidad para criptomonedas
            "asian_session": {
                "start": time(0, 0),
                "end": time(8, 0),
            },  # Apertura asiática
            "european_session": {
                "start": time(8, 0),
                "end": time(16, 0),
            },  # Apertura europea
            "us_session": {
                "start": time(14, 0),
                "end": time(22, 0),
            },  # Apertura US (overlap)
            "weekend_activity": {
                "start": time(20, 0),
                "end": time(2, 0),
            },  # Actividad nocturna weekend
        },
        # Usar símbolos principales de crypto desde GLOBAL_SYMBOLS
        "optimal_symbols": CRYPTO_MAJOR[:4],  # Top 4 crypto principales
        "min_confidence_adjustment": -5.0,  # Reducir 5% confianza mínima (más oportunidades)
        "max_trades_multiplier": 1.3,  # 30% más trades permitidos
    },
    "forex": {
        "high_volatility_hours": {
            # Horarios de mayor volatilidad para forex
            "london_open": {
                "start": time(8, 0),
                "end": time(10, 0),
            },  # Apertura Londres
            "ny_open": {
                "start": time(14, 0),
                "end": time(16, 0),
            },  # Apertura Nueva York
            "london_ny_overlap": {
                "start": time(14, 0),
                "end": time(17, 0),
            },  # Overlap principal
            "asian_close": {"start": time(7, 0), "end": time(9, 0)},  # Cierre asiático
        },
        # Usar símbolos principales de forex desde GLOBAL_SYMBOLS
        "optimal_symbols": FOREX_MAJOR[:4],  # Top 4 pares mayores
        "min_confidence_adjustment": 0.0,  # Sin ajuste (mantener estándar)
        "max_trades_multiplier": 1.0,  # Sin multiplicador
    },
    "commodities": {
        "high_volatility_hours": {
            # Horarios de mayor volatilidad para commodities
            "gold_active": {"start": time(9, 0), "end": time(11, 0)},  # Oro más activo
            "oil_active": {
                "start": time(15, 0),
                "end": time(17, 0),
            },  # Petróleo más activo
            "general_active": {
                "start": time(14, 0),
                "end": time(16, 0),
            },  # Actividad general
        },
        # Usar símbolos principales de commodities desde GLOBAL_SYMBOLS
        "optimal_symbols": METALS_PRECIOUS + ENERGY_COMMODITIES[:2] + METALS_INDUSTRIAL[:1],  # Metales preciosos + energía + industrial
        "min_confidence_adjustment": 2.0,  # Aumentar 2% confianza (más conservador)
        "max_trades_multiplier": 0.8,  # 20% menos trades (más selectivo)
    },
}

# Configuración de sesiones de alta volatilidad global
HIGH_VOLATILITY_SESSIONS = {
    "morning_breakout": {
        "start": time(11, 30),
        "end": time(13, 30),
        "description": "Sesión de breakout matutino - Mayor volatilidad europea (UTC)",
        "confidence_boost": 5.0,  # Aumentar confianza en señales durante esta sesión
    },
    "afternoon_momentum": {
        "start": time(17, 30),
        "end": time(19, 30),
        "description": "Sesión de momentum vespertino - Overlap EU-US (UTC)",
        "confidence_boost": 7.0,  # Mayor boost por ser sesión premium
    },
    "evening_continuation": {
        "start": time(23, 0),
        "end": time(1, 0),
        "description": "Sesión de continuación nocturna - Crypto y mercados asiáticos (UTC)",
        "confidence_boost": 3.0,  # Boost moderado para sesión nocturna
    },
}

# ============================================================================
# ⚠️ CONFIGURACIÓN DE SEGURIDAD Y LÍMITES TEMPORALES
# ============================================================================

# Límites de tiempo para prevenir trading excesivo
TIME_LIMITS = {
    "max_consecutive_hours": 8,  # Máximo 8 horas consecutivas de trading
    "mandatory_break_minutes": 30,  # Descanso obligatorio cada 4 horas
    "daily_max_hours": 12,  # Máximo 12 horas de trading por día
    "weekly_max_hours": 60,  # Máximo 60 horas de trading por semana
    "cooldown_after_loss_minutes": 15,  # Cooldown después de pérdidas
    "emergency_stop_hour": 2,  # Hora de parada de emergencia (02:00 UTC, era 23:00 Chile)
}

# Configuración de pausas automáticas
AUTO_BREAKS = {
    "enabled": True,  # Activar pausas automáticas
    "break_every_hours": 4,  # Pausa cada 4 horas
    "break_duration_minutes": 15,  # Duración de pausa: 15 minutos
    "long_break_every_hours": 8,  # Pausa larga cada 8 horas
    "long_break_duration_minutes": 30,  # Duración pausa larga: 30 minutos
}

# ============================================================================
# 🔧 FUNCIONES UTILITARIAS DE HORARIOS
# ============================================================================


def is_trading_day_allowed(profile_name: str = None) -> bool:
    """
    Verifica si el trading está permitido en el día actual según la configuración.

    Args:
        profile_name: Nombre del perfil (opcional, usa el actual si no se especifica)

    Returns:
        bool: True si el trading está permitido hoy
    """
    from datetime import datetime
    from .profiles_config import TRADING_PROFILE

    # Obtener el día actual en UTC
    current_day = datetime.now(UTC_TZ).strftime("%A").lower()

    # Si no se especifica perfil, usar el actual
    if profile_name is None:
        profile_name = TRADING_PROFILE

    # Verificar configuración del día en TRADING_SCHEDULE
    day_config = TRADING_SCHEDULE.get(current_day, {})
    if not day_config:
        return False

    # Verificar si el día está activo
    is_active = day_config.get("active", False)

    # Si es fin de semana, verificar configuración específica del perfil
    if current_day in ["saturday", "sunday"]:
        profile_config = PROFILE_TRADING_SCHEDULE.get(profile_name, {})
        weekend_config = profile_config.get("weekend_config", {})

        # Verificar si el trading de fin de semana está habilitado para el perfil
        weekend_enabled = weekend_config.get("enabled", False)
        day_weekend_config = weekend_config.get(current_day, {})
        day_weekend_active = day_weekend_config.get("active", False)

        return is_active and weekend_enabled and day_weekend_active

    # Para días de semana, usar la configuración general
    return is_active


def get_weekend_trading_params(profile_name: str = None) -> dict:
    """
    Obtiene los parámetros de trading ajustados para fines de semana.

    Args:
        profile_name: Nombre del perfil (opcional, usa el actual si no se especifica)

    Returns:
        dict: Parámetros de trading para fines de semana
    """
    from datetime import datetime
    from .profiles_config import TRADING_PROFILE

    # Si no se especifica perfil, usar el actual
    if profile_name is None:
        profile_name = TRADING_PROFILE

    # Verificar si es fin de semana en UTC
    current_day = datetime.now(UTC_TZ).strftime("%A").lower()
    is_weekend = current_day in ["saturday", "sunday"]

    if not is_weekend:
        # No es fin de semana, retornar parámetros normales (sin modificadores)
        return {
            "min_confidence_multiplier": 1.0,
            "max_daily_trades_multiplier": 1.0,
            "max_position_size_multiplier": 1.0,
        }

    # Es fin de semana, obtener parámetros específicos del perfil
    if profile_name in PROFILE_TRADING_SCHEDULE:
        return PROFILE_TRADING_SCHEDULE[profile_name].get(
            "weekend_params",
            {
                "min_confidence_multiplier": 1.0,
                "max_daily_trades_multiplier": 1.0,
                "max_position_size_multiplier": 1.0,
            },
        )

    # Fallback a parámetros conservadores por defecto
    return {
        "min_confidence_multiplier": 1.15,
        "max_daily_trades_multiplier": 0.6,
        "max_position_size_multiplier": 0.85,
    }


def is_smart_trading_hours_allowed(
    symbol: str = None, profile_name: str = None
) -> dict:
    """
    🕘 Verifica si estamos dentro de los horarios inteligentes de trading en UTC.
    Usa UTC para comparaciones precisas y portabilidad global.

    Args:
        symbol: Símbolo del activo (opcional, para validación específica por mercado)
        profile_name: Nombre del perfil (opcional, usa el actual si no se especifica)

    Returns:
        dict: Información detallada sobre el estado del horario de trading
    """
    from datetime import datetime, time
    import pytz
    from .profiles_config import TRADING_PROFILE

    # Si los horarios inteligentes están deshabilitados, permitir siempre
    if not SMART_TRADING_HOURS.get("enabled", True):
        return {
            "is_allowed": True,
            "reason": "Smart trading hours disabled - 24/7 trading",
            "current_time_utc": datetime.now(pytz.UTC),
            "market_status": "always_open",
        }

    try:
        # Obtener zona horaria UTC
        utc_tz = pytz.timezone(SMART_TRADING_HOURS["timezone"])

        # Obtener tiempo actual en UTC
        utc_now = datetime.now(pytz.UTC)
        current_time_utc = utc_now

        # Si no se especifica perfil, usar el actual
        if profile_name is None:
            profile_name = TRADING_PROFILE

        # Obtener horarios base (formato HH:MM en UTC)
        start_time_str = SMART_TRADING_HOURS["start_time"]
        end_time_str = SMART_TRADING_HOURS["end_time"]

        # Aplicar ajustes por perfil si existen
        profile_adjustments = SMART_TRADING_HOURS.get("profile_adjustments", {})
        if profile_name in profile_adjustments:
            start_time_str = profile_adjustments[profile_name].get(
                "start_time", start_time_str
            )
            end_time_str = profile_adjustments[profile_name].get(
                "end_time", end_time_str
            )

        # Aplicar configuración específica por mercado si se proporciona símbolo
        market_type = _detect_market_type(symbol) if symbol else "general"
        market_config = SMART_TRADING_HOURS.get("market_specific", {}).get(market_type)

        if market_config and market_config.get("enabled", True):
            start_time_str = market_config.get("start_time", start_time_str)
            end_time_str = market_config.get("end_time", end_time_str)
            market_reason = market_config.get("reason", "Market-specific hours")
        else:
            market_reason = "General trading hours"

        # Crear horarios en UTC para comparaciones precisas
        # Fix: Convertir objetos time() a string si es necesario
        if isinstance(start_time_str, time):
            start_time_str = start_time_str.strftime("%H:%M")
        if isinstance(end_time_str, time):
            end_time_str = end_time_str.strftime("%H:%M")
            
        start_hour, start_minute = map(int, start_time_str.split(":"))
        end_hour, end_minute = map(int, end_time_str.split(":"))

        # Crear datetime en UTC para hoy con los horarios configurados
        today_utc = current_time_utc.date()
        start_datetime_utc = utc_tz.localize(
            datetime.combine(today_utc, time(start_hour, start_minute))
        )
        end_datetime_utc = utc_tz.localize(
            datetime.combine(today_utc, time(end_hour, end_minute))
        )

        # Verificar si estamos dentro del horario (comparación en UTC)
        # Manejar correctamente horarios que cruzan medianoche
        current_time_only = current_time_utc.time()
        start_time_only = start_datetime_utc.time()
        end_time_only = end_datetime_utc.time()
        
        if start_time_only <= end_time_only:
            # Horario normal (no cruza medianoche): ej. 08:00 - 17:00
            is_within_hours = start_time_only <= current_time_only <= end_time_only
        else:
            # Horario que cruza medianoche: ej. 11:00 - 02:30
            is_within_hours = (
                current_time_only >= start_time_only or 
                current_time_only <= end_time_only
            )

        if is_within_hours:
            return {
                "is_allowed": True,
                "reason": f"Within smart trading hours ({start_time_str}-{end_time_str} UTC) - {market_reason}",
                "current_time_utc": current_time_utc,
                "market_status": "open",
                "market_type": market_type,
                "active_hours": f"{start_time_str}-{end_time_str}",
                "profile": profile_name,
            }
        else:
            return {
                "is_allowed": False,
                "reason": f"Outside smart trading hours ({start_time_str}-{end_time_str} UTC) - Current: {current_time_utc.strftime('%H:%M')}",
                "current_time_utc": current_time_utc,
                "market_status": "closed_hours",
                "market_type": market_type,
                "active_hours": f"{start_time_str}-{end_time_str}",
                "profile": profile_name,
                "next_open_time": start_time_str,
            }

    except Exception as e:
        # En caso de error, permitir trading para no bloquear el sistema
        return {
            "is_allowed": True,
            "reason": f"Error checking smart hours: {e} - Defaulting to allow",
            "current_time_utc": datetime.now(pytz.UTC),
            "market_status": "error_default_open",
            "error": str(e),
        }


def _detect_market_type(symbol: str) -> str:
    """
    🔍 Detecta el tipo de mercado basado en el símbolo.

    Args:
        symbol: Símbolo del activo

    Returns:
        str: Tipo de mercado ('crypto', 'forex', 'stocks_us', 'general')
    """
    if not symbol:
        return "general"

    symbol_upper = symbol.upper()

    # Detectar criptomonedas
    crypto_indicators = [
        "USDT",
        "USDC",
        "BTC",
        "ETH",
        "BNB",
        "ADA",
        "DOT",
        "LINK",
        "UNI",
    ]
    if any(indicator in symbol_upper for indicator in crypto_indicators):
        return "crypto"

    # Detectar forex
    forex_pairs = ["EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD", "USD"]
    if len(symbol_upper) == 6 and any(pair in symbol_upper for pair in forex_pairs):
        return "forex"

    # Detectar acciones estadounidenses
    us_stocks = ["NVDA", "US500", "SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    if any(stock in symbol_upper for stock in us_stocks):
        return "stocks_us"

    return "general"


def get_smart_trading_status_summary() -> dict:
    """
    📊 Obtiene un resumen del estado actual de los horarios inteligentes.

    Returns:
        dict: Resumen completo del estado de trading
    """
    from datetime import datetime
    import pytz
    from .profiles_config import TRADING_PROFILE

    try:
        utc_tz = pytz.timezone(SMART_TRADING_HOURS["timezone"])
        current_time_utc = datetime.now(pytz.UTC)

        # Estado general
        general_status = is_smart_trading_hours_allowed()

        # Estado por tipo de mercado
        market_statuses = {}
        for market_type in ["crypto", "forex", "stocks_us"]:
            market_statuses[market_type] = is_smart_trading_hours_allowed(
                f"sample_{market_type}"
            )

        return {
            "current_time_utc": current_time_utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "smart_hours_enabled": SMART_TRADING_HOURS.get("enabled", True),
            "general_status": general_status,
            "market_statuses": market_statuses,
            "active_profile": TRADING_PROFILE,
            "configuration": {
                "base_hours": f"{SMART_TRADING_HOURS['start_time']}-{SMART_TRADING_HOURS['end_time']}",
                "timezone": SMART_TRADING_HOURS["timezone"],
            },
        }

    except Exception as e:
        return {
            "error": f"Error getting smart trading status: {e}",
            "current_time_utc": datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S %Z"),
            "smart_hours_enabled": False,
        }


def get_market_specific_config(symbol: str) -> dict:
    """
    Obtiene la configuración específica para un símbolo basada en su tipo de mercado.

    Args:
        symbol: Símbolo del activo (ej: "BTCUSD", "EURUSD", "GOLD")

    Returns:
        dict: Configuración específica del mercado
    """
    market_type = _detect_market_type(symbol)
    return MARKET_SPECIFIC_CONFIG.get(market_type, MARKET_SPECIFIC_CONFIG["forex"])


def is_high_volatility_session(current_time: time = None) -> dict:
    """
    Verifica si la hora actual está dentro de una sesión de alta volatilidad.

    Args:
        current_time: Hora actual (opcional, usa la actual si no se especifica)

    Returns:
        dict: Información sobre la sesión de alta volatilidad
    """
    from datetime import datetime

    if current_time is None:
        current_time = datetime.now(UTC_TZ).time()

    for session_name, session_config in HIGH_VOLATILITY_SESSIONS.items():
        start_time = session_config["start"]
        end_time = session_config["end"]

        # Manejar sesiones que cruzan medianoche
        if start_time > end_time:
            if current_time >= start_time or current_time <= end_time:
                return {
                    "is_high_volatility": True,
                    "session_name": session_name,
                    "session_config": session_config,
                    "confidence_boost": session_config.get("confidence_boost", 0.0),
                    "description": session_config.get("description", ""),
                }
        else:
            if start_time <= current_time <= end_time:
                return {
                    "is_high_volatility": True,
                    "session_name": session_name,
                    "session_config": session_config,
                    "confidence_boost": session_config.get("confidence_boost", 0.0),
                    "description": session_config.get("description", ""),
                }

    return {
        "is_high_volatility": False,
        "session_name": None,
        "session_config": {},
        "confidence_boost": 0.0,
        "description": "Sesión de volatilidad normal",
    }


def get_optimized_trading_params(symbol: str, profile_name: str = None) -> dict:
    """
    Obtiene parámetros de trading optimizados para un símbolo específico.

    Args:
        symbol: Símbolo del activo
        profile_name: Nombre del perfil (opcional)

    Returns:
        dict: Parámetros optimizados de trading
    """
    from datetime import datetime
    from .profiles_config import TRADING_PROFILE

    if profile_name is None:
        profile_name = TRADING_PROFILE

    # Obtener configuración específica del mercado
    market_config = get_market_specific_config(symbol)

    # Obtener información de sesión de alta volatilidad
    volatility_info = is_high_volatility_session()

    # Obtener parámetros base del perfil
    base_params = (
        get_weekend_trading_params(profile_name)
        if datetime.now(UTC_TZ).strftime("%A").lower() in ["saturday", "sunday"]
        else {}
    )

    # Calcular ajustes
    confidence_adjustment = market_config.get("min_confidence_adjustment", 0.0)
    if volatility_info["is_high_volatility"]:
        confidence_adjustment += volatility_info["confidence_boost"]

    trades_multiplier = market_config.get("max_trades_multiplier", 1.0)

    return {
        "symbol": symbol,
        "market_type": _detect_market_type(symbol),
        "profile": profile_name,
        "confidence_adjustment": confidence_adjustment,
        "max_trades_multiplier": trades_multiplier,
        "is_optimal_symbol": symbol in market_config.get("optimal_symbols", []),
        "volatility_session": volatility_info,
        "market_config": market_config,
        "base_params": base_params,
        "recommended_action": (
            "ACTIVE"
            if symbol in market_config.get("optimal_symbols", [])
            else "MONITOR"
        ),
    }


def get_current_market_opportunities() -> dict:
    """
    Obtiene las oportunidades actuales del mercado basadas en horarios y volatilidad.

    Returns:
        dict: Oportunidades actuales del mercado
    """
    from datetime import datetime

    current_time = datetime.now(UTC_TZ)
    current_hour = current_time.time()

    opportunities = {
        "timestamp": current_time.isoformat(),
        "high_volatility_session": is_high_volatility_session(current_hour),
        "optimal_symbols_by_market": {},
        "session_recommendations": [],
    }

    # Analizar cada tipo de mercado
    for market_type, config in MARKET_SPECIFIC_CONFIG.items():
        market_opportunities = []

        # Verificar si estamos en horarios de alta volatilidad para este mercado
        for session_name, session_times in config["high_volatility_hours"].items():
            start_time = session_times["start"]
            end_time = session_times["end"]

            # Manejar sesiones que cruzan medianoche
            is_active = False
            if start_time > end_time:
                is_active = current_hour >= start_time or current_hour <= end_time
            else:
                is_active = start_time <= current_hour <= end_time

            if is_active:
                market_opportunities.append(
                    {
                        "session": session_name,
                        "active": True,
                        "optimal_symbols": config["optimal_symbols"],
                        "confidence_adjustment": config["min_confidence_adjustment"],
                        "trades_multiplier": config["max_trades_multiplier"],
                    }
                )

        opportunities["optimal_symbols_by_market"][market_type] = {
            "symbols": config["optimal_symbols"],
            "active_sessions": market_opportunities,
            "is_optimal_time": len(market_opportunities) > 0,
        }

    # Generar recomendaciones
    if opportunities["high_volatility_session"]["is_high_volatility"]:
        opportunities["session_recommendations"].append(
            f"🔥 Sesión de alta volatilidad activa: {opportunities['high_volatility_session']['description']}"
        )

    # Recomendar símbolos óptimos para el momento actual
    for market_type, market_info in opportunities["optimal_symbols_by_market"].items():
        if market_info["is_optimal_time"]:
            opportunities["session_recommendations"].append(
                f"📈 Momento óptimo para {market_type.upper()}: {', '.join(market_info['symbols'])}"
            )

    return opportunities
