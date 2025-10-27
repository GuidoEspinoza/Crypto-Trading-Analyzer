# ============================================================================
# ⏰ CONFIGURACIÓN DE HORARIOS Y TIEMPO DE TRADING
# ============================================================================
"""
Configuración centralizada de horarios de trading para el sistema de trading automatizado.

Este módulo define los horarios de operación, zonas horarias, y configuraciones
temporales que determinan cuándo el bot puede operar según diferentes perfiles
de trading (Scalping e Intraday).

Características principales:
- Configuración de zona horaria (Chile/Santiago)
- Horarios de trading inteligentes por perfil
- Configuración de trading en fines de semana
- Horarios de reinicio diario del sistema
- Programación flexible por días de la semana

Autor: Sistema de Trading Automatizado
Versión: 2.0
Última actualización: 2024
"""

import pytz
from datetime import time

# ============================================================================
# 🌍 CONFIGURACIÓN DE ZONA HORARIA
# ============================================================================

# Zona horaria principal del sistema (Chile)
TIMEZONE = "America/Santiago"  # UTC-3 (UTC-4 en horario de invierno)
CHILE_TZ = pytz.timezone(TIMEZONE)  # Objeto timezone para conversiones

# ============================================================================
# 🔄 CONFIGURACIÓN DE REINICIO DIARIO
# ============================================================================

# Hora de reinicio diario del sistema (formato 24h)
# Este es el momento en que se resetean contadores, estadísticas y límites diarios
DAILY_RESET_HOUR = 0  # Medianoche (00:00)
DAILY_RESET_MINUTE = 0  # Minuto exacto del reinicio

# ============================================================================
# 🕐 HORARIOS DE TRADING INTELIGENTES
# ============================================================================

# 🚨 IMPORTANTE: Estos horarios están optimizados para máxima volatilidad
# y liquidez en los mercados de criptomonedas

SMART_TRADING_HOURS = {
    # === HORARIO PRINCIPAL DE TRADING ===
    # Coincide con apertura de mercados europeos y estadounidenses
    "start_time": time(9, 30),  # 09:30 - Inicio de sesión principal
    "end_time": time(13, 0),  # 13:00 - Fin de sesión principal
    # === HORARIO EXTENDIDO (OPCIONAL) ===
    # Para trading más agresivo durante alta volatilidad
    "extended_start": time(8, 0),  # 08:00 - Inicio extendido
    "extended_end": time(15, 0),  # 15:00 - Fin extendido
    # === HORARIO NOCTURNO (SOLO SCALPING) ===
    # Para aprovechar movimientos en mercados asiáticos
    "night_start": time(22, 0),  # 22:00 - Inicio nocturno
    "night_end": time(2, 0),  # 02:00 - Fin nocturno (día siguiente)
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
    # Actividad reducida, solo para perfiles específicos
    "saturday": {
        "active": False,  # Desactivado por defecto
        "schedule_type": "weekend",
        "description": "Sábado - Mercado de criptos 24/7, volatilidad reducida",
    },
    "sunday": {
        "active": False,  # Desactivado por defecto
        "schedule_type": "weekend",
        "description": "Domingo - Preparación para nueva semana",
    },
}

# ============================================================================
# 🏃‍♂️ CONFIGURACIÓN DE TRADING EN FINES DE SEMANA POR PERFIL
# ============================================================================

# Trading de fin de semana para perfil SCALPING
# Aprovecha la menor competencia y movimientos únicos del weekend
SCALPING_WEEKEND_TRADING = {
    "enabled": False,  # 🚨 DESACTIVADO por defecto para mayor seguridad
    "saturday": {
        "active": False,
        "start_time": time(10, 0),  # Inicio más tardío los sábados
        "end_time": time(16, 0),  # Sesión más corta
        "max_trades": 8,  # Límite reducido de trades
        "min_confidence": 80.0,  # Confianza más alta requerida
        "description": "Sábado Scalping - Sesión conservadora",
    },
    "sunday": {
        "active": False,
        "start_time": time(14, 0),  # Tarde del domingo
        "end_time": time(20, 0),  # Preparación para lunes
        "max_trades": 5,  # Límite muy reducido
        "min_confidence": 82.0,  # Confianza muy alta
        "description": "Domingo Scalping - Preparación semanal",
    },
}

# Trading de fin de semana para perfil INTRADAY
# Más conservador, enfocado en movimientos de mayor calidad
INTRADAY_WEEKEND_TRADING = {
    "enabled": False,  # 🚨 DESACTIVADO por defecto para máxima seguridad
    "saturday": {
        "active": False,
        "start_time": time(11, 0),  # Inicio conservador
        "end_time": time(15, 0),  # Sesión corta y enfocada
        "max_trades": 4,  # Muy pocos trades
        "min_confidence": 85.0,  # Confianza muy alta
        "description": "Sábado Intraday - Solo señales premium",
    },
    "sunday": {
        "active": False,
        "start_time": time(15, 0),  # Solo tarde del domingo
        "end_time": time(18, 0),  # Sesión muy corta
        "max_trades": 2,  # Máximo 2 trades
        "min_confidence": 88.0,  # Confianza extrema
        "description": "Domingo Intraday - Solo oportunidades excepcionales",
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
# ⚠️ CONFIGURACIÓN DE SEGURIDAD Y LÍMITES TEMPORALES
# ============================================================================

# Límites de tiempo para prevenir trading excesivo
TIME_LIMITS = {
    "max_consecutive_hours": 8,  # Máximo 8 horas consecutivas de trading
    "mandatory_break_minutes": 30,  # Descanso obligatorio cada 4 horas
    "daily_max_hours": 12,  # Máximo 12 horas de trading por día
    "weekly_max_hours": 60,  # Máximo 60 horas de trading por semana
    "cooldown_after_loss_minutes": 15,  # Cooldown después de pérdidas
    "emergency_stop_hour": 23,  # Hora de parada de emergencia (23:00)
}

# Configuración de pausas automáticas
AUTO_BREAKS = {
    "enabled": True,  # Activar pausas automáticas
    "break_every_hours": 4,  # Pausa cada 4 horas
    "break_duration_minutes": 15,  # Duración de pausa: 15 minutos
    "long_break_every_hours": 8,  # Pausa larga cada 8 horas
    "long_break_duration_minutes": 30,  # Duración pausa larga: 30 minutos
}
