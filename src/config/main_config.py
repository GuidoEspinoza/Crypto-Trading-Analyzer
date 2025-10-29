"""
🤖 CONFIGURACIÓN PRINCIPAL DEL BOT DE TRADING CFD
===============================================

Este módulo centraliza todas las configuraciones del sistema de trading automatizado,
proporcionando una arquitectura modular y escalable para la gestión de parámetros.

📋 CONTENIDO DEL MÓDULO:
    🔧 Configuraciones de Perfiles de Trading
    💰 Configuraciones de Gestión de Riesgo
    📊 Configuraciones de Paper Trading
    🎯 Configuraciones de Estrategias
    📈 Configuraciones de Indicadores Técnicos
    ⏰ Configuraciones de Horarios Inteligentes
    🌐 Configuraciones de APIs y Conexiones
    💾 Configuraciones de Cache y Rendimiento
    📝 Configuraciones de Logging
    🔍 Configuraciones de Monitoreo
    ✅ Validación y Inicialización Automática

🏗️ ARQUITECTURA MODULAR:
    - profiles_config.py: Perfiles de trading (SCALPING, INTRADAY)
    - time_trading_config.py: Horarios y programación temporal
    - symbols_config.py: Símbolos y configuración de mercados
    - main_config.py: Configuración principal y clases centralizadas

⚡ PERFILES DE TRADING ESPECIALIZADOS:
    🔥 SCALPING: Timeframes 1m-5m, máxima frecuencia, ganancias rápidas ultra-agresivas
        • Operaciones de alta velocidad con stop-loss ajustados
        • Análisis cada 30 segundos para máxima reactividad
        • Gestión de riesgo conservadora para proteger capital

    📈 INTRADAY: Timeframes 15m-1h, operaciones diarias, balance entre velocidad y precisión
        • Operaciones de mediano plazo con análisis profundo
        • Análisis cada 5 minutos para decisiones informadas
        • Mayor tolerancia al riesgo para capturas de tendencias

🎯 CAMBIO RÁPIDO DE PERFILES:
    Para cambiar entre configuraciones, modifica la variable TRADING_PROFILE en profiles_config.py:
    - "SCALPING" para estrategia ultra-rápida de ganancias inmediatas
    - "INTRADAY" para estrategia diaria balanceada con mayor precisión

🛡️ CARACTERÍSTICAS DE SEGURIDAD:
    ✨ Validación automática de parámetros en tiempo real
    🔒 Límites de riesgo dinámicos por perfil
    ⏰ Horarios inteligentes optimizados para mercados globales en UTC
    📊 Monitoreo continuo de rendimiento y drawdown
    🚨 Sistema de alertas y notificaciones automáticas

👨‍💻 AUTOR: Sistema de Trading Automatizado
📅 ÚLTIMA ACTUALIZACIÓN: 2024
🔄 VERSIÓN: 3.0 - Arquitectura Modular Avanzada
"""

import logging
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

# Carga de variables de entorno desde .env si está presente
load_dotenv()

# ============================================================================
# 📦 IMPORTACIONES DE CONFIGURACIONES MODULARIZADAS
# ============================================================================

# 🎯 Símbolos de Trading: Lista de activos disponibles para operar
from .symbols_config import GLOBAL_SYMBOLS

# 👤 Perfiles de Trading: Configuraciones especializadas (SCALPING/INTRADAY)
from .profiles_config import TRADING_PROFILE, PROFILES

# ⏰ Configuraciones Temporales: Horarios, zonas horarias y programación
from .time_trading_config import (
    TIMEZONE,  # Zona horaria principal del sistema
    UTC_TZ,  # Zona horaria UTC para trading global
    DAILY_RESET_HOUR,  # Hora de reinicio diario del sistema
    DAILY_RESET_MINUTE,  # Minuto de reinicio diario del sistema
    SMART_TRADING_HOURS,  # Horarios inteligentes optimizados
    TRADING_SCHEDULE,  # Programación semanal de trading
    SCALPING_WEEKEND_TRADING,  # Configuración de trading en fines de semana (Scalping)
    INTRADAY_WEEKEND_TRADING,  # Configuración de trading en fines de semana (Intraday)
    PROFILE_TRADING_SCHEDULE,  # Horarios específicos por perfil
    # Funciones relacionadas con tiempo
    is_trading_day_allowed,  # Validación de días de trading
    get_weekend_trading_params,  # Parámetros de trading de fin de semana
    is_smart_trading_hours_allowed,  # Validación de horarios inteligentes
    get_smart_trading_status_summary,  # Resumen de estado de horarios
    _detect_market_type,  # Detección de tipo de mercado
)

# ============================================================================
# 📝 CONFIGURACIÓN DE LOGGING Y UTILIDADES
# ============================================================================

# 📊 Logger principal para validación y monitoreo del sistema
logger = logging.getLogger(__name__)


def _get_env_float(var_name: str, default: float) -> float:
    """
    🔧 Utilidad para leer variables de entorno como float con fallback seguro.

    Args:
        var_name (str): Nombre de la variable de entorno
        default (float): Valor por defecto si la variable no existe o está vacía

    Returns:
        float: Valor de la variable de entorno o valor por defecto

    Example:
        >>> balance = _get_env_float("INITIAL_BALANCE", 1000.0)
        >>> # Retorna el valor de INITIAL_BALANCE o 1000.0 si no existe
    """
    value = os.getenv(var_name)
    if value is None or value == "":
        return default
    try:
        return float(value)
    except Exception:
        logger.warning(
            f"Valor inválido para {var_name}: {value}, usando default {default}"
        )
        return default


# Utilidad para leer variables de entorno como boolean con fallback seguro
def _get_env_bool(var_name: str, default: bool) -> bool:
    value = os.getenv(var_name)
    if value is None or value == "":
        return default

    # Convertir string a boolean
    value_lower = value.lower().strip()
    if value_lower in ("true", "1", "yes", "on", "enabled"):
        return True
    elif value_lower in ("false", "0", "no", "off", "disabled"):
        return False
    else:
        logger.warning(
            f"Valor inválido para {var_name}: {value}, usando default {default}"
        )
        return default


class TradingProfiles:
    """
    🎯 Gestión centralizada de perfiles de trading especializados para CFDs.

    Esta clase proporciona una interfaz unificada para acceder a las configuraciones
    de los diferentes perfiles de trading (SCALPING, INTRADAY) definidos en
    profiles_config.py.

    🔧 FUNCIONALIDADES:
        • Acceso dinámico al perfil activo
        • Validación automática de perfiles
        • Métodos getter para todos los parámetros
        • Compatibilidad con código legacy

    📊 PERFILES DISPONIBLES:
        🔥 SCALPING: Trading de alta frecuencia (1m-5m)
        📈 INTRADAY: Trading diario balanceado (15m-1h)
    """

    # 📋 Referencia a los perfiles importados desde profiles_config.py
    PROFILES = PROFILES

    @classmethod
    def get_profile(cls, profile_name: str) -> Dict[str, Any]:
        """
        📋 Obtiene la configuración del perfil especificado.

        Args:
            profile_name (str): Nombre del perfil ('SCALPING' o 'INTRADAY')

        Returns:
            Dict[str, Any]: Configuración completa del perfil

        Raises:
            ValueError: Si el perfil no existe
        """
        if profile_name not in PROFILES:
            raise ValueError(
                f"Perfil '{profile_name}' no válido. Opciones: {list(PROFILES.keys())}"
            )
        return PROFILES[profile_name]

    @classmethod
    def get_current_profile(cls) -> Dict[str, Any]:
        """Obtiene el perfil actualmente configurado."""
        return cls.get_profile(TRADING_PROFILE)

    @classmethod
    def get_max_daily_trades(cls) -> int:
        """Máximo de trades diarios según perfil activo."""
        return cls.get_current_profile()["max_daily_trades"]

    @classmethod
    def get_adaptive_daily_trades_limit(
        cls, current_trades_count: int = 0, signal_confidence: float = 0.0
    ) -> int:
        """
        Calcula el límite adaptativo de trades diarios basado en la confianza de la señal.

        Args:
            current_trades_count: Número actual de trades realizados hoy
            signal_confidence: Confianza de la señal actual (0-100)

        Returns:
            Límite máximo de trades permitidos para el día
        """
        profile = cls.get_current_profile()
        base_limit = profile["max_daily_trades"]

        # Si el perfil no tiene configuración adaptativa, usar límite base
        if not profile.get("max_daily_trades_adaptive", False):
            return base_limit

        # Obtener configuración adaptativa
        quality_threshold = profile.get("daily_trades_quality_threshold", 80.0)
        bonus_trades = profile.get("max_daily_trades_bonus", 0)

        # Si la señal tiene alta confianza, permitir trades adicionales
        if signal_confidence >= quality_threshold:
            return base_limit + bonus_trades

        # Para señales de confianza normal, usar límite base
        return base_limit

    @classmethod
    def get_max_consecutive_losses(cls) -> int:
        """Obtiene el límite de pérdidas consecutivas según el perfil activo."""
        profile = cls.get_current_profile()

        # Calcular límite dinámico basado en max_daily_trades
        max_trades = profile["max_daily_trades"]

        # Límite conservador: 20% del máximo de trades diarios
        base_limit = max(
            3, int(max_trades * 0.20)
        )  # Mínimo 3, máximo 20% de trades diarios

        # Ajuste por confianza: si la confianza es muy alta, permitir un poco más de tolerancia
        min_confidence = profile["min_confidence"]
        if min_confidence >= 80.0:
            # Para confianza muy alta (≥80%), permitir 1-2 pérdidas adicionales
            confidence_bonus = 2
        elif min_confidence >= 75.0:
            # Para confianza alta (≥75%), permitir 1 pérdida adicional
            confidence_bonus = 1
        else:
            # Para confianza normal (<75%), no hay bonus
            confidence_bonus = 0

        # Límite final con bonus por confianza
        final_limit = base_limit + confidence_bonus

        # Asegurar que no exceda un máximo razonable (30% de trades diarios)
        max_allowed = int(max_trades * 0.30)

        return min(final_limit, max_allowed)


# ============================================================================
# 🏭 CONFIGURACIÓN DEL MODO DE OPERACIÓN DEL SISTEMA
# ============================================================================
"""
Esta sección define el modo de operación del sistema (desarrollo vs producción)
y configura automáticamente las características dependientes del modo.
"""

# 🎯 Modo principal del sistema
PRODUCTION_MODE = (
    _get_env_float("PRODUCTION_MODE", 0.0) == 1.0
)  # False por defecto (modo desarrollo)

# 📊 Configuraciones de trading dependientes del modo
# Dashboard eliminado - usando Capital.com directamente para mayor eficiencia
PAPER_TRADING_ONLY = (
    not PRODUCTION_MODE
)  # Paper trading en desarrollo, trading real en producción

ENABLE_REAL_TRADING = _get_env_bool(
    "ENABLE_REAL_TRADING", PRODUCTION_MODE
)  # Trading real configurado por variable de entorno o modo de producción

# 🔍 Configuraciones de logging y debugging
VERBOSE_LOGGING = not PRODUCTION_MODE  # Logging detallado habilitado en desarrollo
ENABLE_DEBUG_FEATURES = (
    not PRODUCTION_MODE
)  # Características de debug solo en desarrollo

# ============================================================================
# 💰 CONFIGURACIÓN DE BALANCE
# ============================================================================


def _get_capital_balance() -> float:
    """
    Obtiene el balance disponible real de la cuenta de Capital.com

    Returns:
        float: Balance disponible en USD, o 0.0 si hay error
    """
    try:
        # Importación diferida para evitar dependencias circulares
        import sys
        import importlib

        # Importar dinámicamente el módulo
        capital_module = importlib.import_module("src.core.capital_client")
        create_capital_client_from_env = getattr(
            capital_module, "create_capital_client_from_env"
        )

        # Crear cliente de Capital.com
        capital_client = create_capital_client_from_env()

        # Obtener balance disponible
        balance_info = capital_client.get_available_balance()

        if balance_info and "available" in balance_info:
            available_balance = float(balance_info["available"])
            print(f"✅ Balance real obtenido de Capital.com: ${available_balance:,.2f}")
            return available_balance
        else:
            print(
                "⚠️ No se pudo obtener el balance de Capital.com, usando balance por defecto"
            )
            return 0.0

    except Exception as e:
        print(f"❌ Error al obtener balance de Capital.com: {e}")
        return 0.0


# 💰 Balance inicial global para todas las posiciones en USD (paper trading)
PAPER_GLOBAL_INITIAL_BALANCE = 1000.0

# 💰 Balance inicial global para todas las posiciones en USD (real trading)
# Se obtiene dinámicamente de Capital.com cuando ENABLE_REAL_TRADING está habilitado
REAL_GLOBAL_INITIAL_BALANCE = (
    0.0  # Se inicializa en 0, se obtiene dinámicamente cuando se necesite
)


def get_global_initial_balance() -> float:
    """
    Obtiene el balance inicial global dinámicamente según el modo de trading.

    Esta función determina automáticamente si usar el balance de paper trading
    o el balance real de Capital.com basándose en la configuración actual.

    Returns:
        float: Balance inicial en USD

    Note:
        - En modo paper trading: retorna PAPER_GLOBAL_INITIAL_BALANCE
        - En modo real trading: obtiene y cachea el balance de Capital.com
        - El balance real se obtiene solo una vez para optimizar rendimiento
    """
    global REAL_GLOBAL_INITIAL_BALANCE

    if _get_env_bool("ENABLE_REAL_TRADING", False):
        # Si el trading real está habilitado, obtener balance real de Capital.com
        if (
            REAL_GLOBAL_INITIAL_BALANCE == 0.0
        ):  # Solo obtener si no se ha obtenido antes (cache)
            REAL_GLOBAL_INITIAL_BALANCE = _get_capital_balance()
        return REAL_GLOBAL_INITIAL_BALANCE
    else:
        # Si no, usar balance de paper trading
        return PAPER_GLOBAL_INITIAL_BALANCE


# 💰 Balance inicial global para todas las posiciones en USD
# Usa balance real si el trading real está habilitado, sino usa paper trading
GLOBAL_INITIAL_BALANCE = PAPER_GLOBAL_INITIAL_BALANCE  # Por defecto paper trading, se actualiza dinámicamente

# 💵 Precio base de USD (moneda fiat de referencia)
USD_BASE_PRICE = 1.0

# ============================================================================
# 🤖 CONFIGURACIÓN DEL TRADING BOT PRINCIPAL
# ============================================================================


class TradingBotConfig:
    """
    Configuración principal del trading bot con parámetros dinámicos basados en perfiles.

    Esta clase centraliza toda la configuración del bot de trading, proporcionando
    métodos de clase para obtener parámetros específicos según el perfil activo.
    Todos los valores se obtienen dinámicamente del perfil actual, permitiendo
    cambios de configuración sin reiniciar el sistema.

    Características principales:
    - ⚙️ Configuración dinámica basada en perfiles de trading
    - 📊 Parámetros específicos para análisis técnico y timeframes
    - 🔄 Intervalos de actualización y monitoreo configurables
    - 🛡️ Límites de riesgo y gestión de posiciones
    - 🎯 Umbrales de confianza adaptativos por perfil

    Perfiles soportados:
    - Scalping: Trading de alta frecuencia con timeframes cortos
    - Intraday: Trading intradía con análisis de tendencias
    - Swing: Trading de posiciones a medio plazo
    - Conservative: Trading conservador con bajo riesgo

    Uso:
        # Obtener configuración dinámica del perfil activo
        interval = TradingBotConfig.get_analysis_interval()
        threshold = TradingBotConfig.get_min_confidence_threshold()
        timeframes = TradingBotConfig.get_professional_timeframes()

    Nota:
        Todos los métodos son de clase (@classmethod) para acceso directo
        sin necesidad de instanciar la clase.
    """

    """Configuración principal del bot de trading."""

    # Lista de símbolos para analizar - Optimizada para trading
    # Selección basada en alta liquidez, volatilidad y volumen de trading
    SYMBOLS = GLOBAL_SYMBOLS

    # Símbolos para el bot en vivo - Misma lista optimizada
    SYMBOLS_LIVE_BOT = GLOBAL_SYMBOLS

    # 🎯 CONFIGURACIÓN DINÁMICA BASADA EN PERFIL SELECCIONADO

    @classmethod
    def get_analysis_interval(cls) -> int:
        """
        Obtiene el intervalo de análisis en minutos según el perfil activo.

        Returns:
            int: Intervalo en minutos entre análisis (ej: 1 para Scalping, 15 para Swing)
        """
        return TradingProfiles.get_current_profile()["analysis_interval"]

    @classmethod
    def get_min_confidence_threshold(cls) -> float:
        """
        Obtiene el umbral mínimo de confianza para ejecutar trades según el perfil.

        Returns:
            float: Porcentaje de confianza mínimo (0-100) para abrir posiciones
        """
        return TradingProfiles.get_current_profile()["min_confidence"]

    @classmethod
    def get_max_concurrent_positions(cls) -> int:
        """
        Obtiene el máximo número de posiciones concurrentes permitidas.

        Returns:
            int: Número máximo de posiciones abiertas simultáneamente
        """
        return TradingProfiles.get_current_profile()["max_positions"]

    @classmethod
    def get_professional_timeframes(cls) -> List[str]:
        """
        Obtiene los timeframes profesionales para análisis técnico según el perfil.

        Returns:
            List[str]: Lista de timeframes (ej: ['1m', '5m', '15m'] para Scalping)
        """
        return TradingProfiles.get_current_profile()["timeframes"]

    # 💰 CONFIGURACIÓN DE PORTFOLIO Y VALORES BASE
    @classmethod
    def get_default_portfolio_value(cls) -> float:
        """
        Obtiene el valor por defecto del portfolio para cálculos iniciales.

        Returns:
            float: Valor del balance inicial global (paper o real según configuración)
        """
        return get_global_initial_balance()

    DEFAULT_PORTFOLIO_VALUE: float = (
        1000.0  # Valor por defecto, se actualiza dinámicamente
    )

    # ⏱️ CONFIGURACIÓN DE TIMEFRAMES DINÁMICOS
    @classmethod
    def get_primary_timeframe(cls) -> str:
        """
        Obtiene el timeframe principal para análisis según el perfil activo.

        Returns:
            str: Timeframe principal (primer elemento de la lista de timeframes del perfil)
        """
        timeframes = cls.get_professional_timeframes()
        return timeframes[0] if timeframes else "1m"

    @classmethod
    def get_confirmation_timeframe(cls) -> str:
        """
        Obtiene el timeframe de confirmación para validar señales.

        Returns:
            str: Timeframe de confirmación (segundo elemento o el primero si solo hay uno)
        """
        timeframes = cls.get_professional_timeframes()
        return timeframes[1] if len(timeframes) > 1 else timeframes[0]

    @classmethod
    def get_trend_timeframe(cls) -> str:
        """
        Obtiene el timeframe de tendencia para análisis de contexto mayor.

        Returns:
            str: Timeframe de tendencia (último elemento de la lista de timeframes)
        """
        timeframes = cls.get_professional_timeframes()
        return timeframes[-1] if timeframes else "15m"

    # 📝 CONFIGURACIÓN DE DESCRIPCIÓN Y METADATOS
    @classmethod
    def get_bot_description(cls) -> str:
        """Descripción del bot según perfil activo."""
        return TradingProfiles.get_current_profile()["name"]

    @classmethod
    def get_live_update_interval(cls) -> int:
        """Intervalo de actualización del live bot en minutos según perfil."""
        return TradingProfiles.get_current_profile()["analysis_interval"]

    @classmethod
    def get_first_analysis_delay(cls) -> int:
        """Delay para primer análisis (en minutos) según perfil."""
        # Usar el doble del intervalo de análisis como delay inicial
        return TradingProfiles.get_current_profile()["analysis_interval"] * 2

    @classmethod
    def get_monitoring_interval(cls) -> int:
        """Intervalo de monitoreo de posiciones según perfil."""
        return TradingProfiles.get_current_profile().get(
            "position_monitoring_interval", 30
        )

    @classmethod
    def get_position_monitoring_enabled(cls) -> bool:
        """Indica si el monitoreo automático de posiciones está habilitado según perfil."""
        return TradingProfiles.get_current_profile().get(
            "enable_position_monitoring", False
        )

    @classmethod
    def get_cleanup_interval(cls) -> int:
        """Intervalo de limpieza según perfil."""
        return TradingProfiles.get_current_profile().get("cleanup_interval", 10)

    @classmethod
    def get_thread_join_timeout(cls) -> int:
        """Timeout para join de threads según perfil."""
        return TradingProfiles.get_current_profile().get("thread_join_timeout", 10)

    @classmethod
    def get_executor_shutdown_timeout(cls) -> int:
        """Timeout para shutdown de executor según perfil."""
        return TradingProfiles.get_current_profile().get(
            "executor_shutdown_timeout", 30
        )

    @classmethod
    def get_analysis_future_timeout(cls) -> int:
        """Timeout para futures de análisis según perfil."""
        return TradingProfiles.get_current_profile().get("analysis_future_timeout", 30)

    @classmethod
    def get_max_consecutive_losses(cls) -> int:
        """Máximo de pérdidas consecutivas antes de activar circuit breaker según perfil activo."""
        return TradingProfiles.get_current_profile()["max_consecutive_losses"]


# ============================================================================
# 📊 CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================


class PaperTraderConfig:
    """
    Configuración del simulador de trading (Paper Trading) con parámetros dinámicos.

    Esta clase gestiona toda la configuración para el trading simulado, permitiendo
    probar estrategias sin riesgo financiero real. Los parámetros se obtienen
    dinámicamente del perfil activo para mantener consistencia con la estrategia.

    Características principales:
    - 💰 Balance inicial configurable por perfil
    - 🎯 Límites de posición y exposición adaptativos
    - 📈 Umbrales de confianza específicos para paper trading
    - 🔒 Controles de riesgo y liquidez
    - ⚡ Simulación de slippage realista

    Funcionalidades:
    - Gestión automática del balance inicial
    - Validación de tamaños de posición
    - Control de exposición total del portfolio
    - Simulación de condiciones de mercado reales
    - Métricas de rendimiento y análisis

    Uso:
        # Obtener configuración dinámica
        balance = PaperTraderConfig.get_initial_balance()
        max_pos = PaperTraderConfig.get_max_position_size()
        threshold = PaperTraderConfig.get_min_confidence_threshold()

    Nota:
        El paper trading es esencial para validar estrategias antes del
        trading real y para desarrollo de nuevas funcionalidades.
    """

    """Configuración del simulador de trading (paper trading)."""

    # Balance inicial en USD para simulación
    @classmethod
    def get_initial_balance(cls) -> float:
        """Obtiene el balance inicial según configuración."""
        return get_global_initial_balance()

    INITIAL_BALANCE: float = 1000.0  # Valor por defecto, se actualiza dinámicamente

    @classmethod
    def get_max_position_size(cls) -> float:
        """Obtiene el tamaño máximo de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["max_position_size_percent"] / 100

    @classmethod
    def get_max_total_exposure(cls) -> float:
        """Obtiene la exposición total máxima según perfil activo."""
        return TradingProfiles.get_current_profile()["max_total_exposure_percent"] / 100

    @classmethod
    def get_min_trade_value(cls) -> float:
        """Obtiene el valor mínimo por trade según perfil activo."""
        return TradingProfiles.get_current_profile()["min_trade_value"]

    @classmethod
    def get_min_confidence_threshold(cls) -> float:
        """Obtiene el umbral mínimo de confianza según perfil activo."""
        return TradingProfiles.get_current_profile()["paper_min_confidence"]

    @classmethod
    def get_max_slippage(cls) -> float:
        """Obtiene el slippage máximo permitido según perfil activo."""
        return TradingProfiles.get_current_profile()["max_slippage"]

    @classmethod
    def get_min_liquidity(cls) -> float:
        """Obtiene la liquidez mínima requerida según perfil activo."""
        return TradingProfiles.get_current_profile()["min_liquidity"]

    # Propiedades dinámicas para compatibilidad con código existente
    MAX_POSITION_SIZE: float = property(
        lambda self: TradingProfiles.get_current_profile()["max_position_size"]
    )
    MAX_TOTAL_EXPOSURE: float = property(
        lambda self: TradingProfiles.get_current_profile()["max_total_exposure"]
    )
    MIN_TRADE_VALUE: float = property(
        lambda self: TradingProfiles.get_current_profile()["min_trade_value"]
    )
    MIN_CONFIDENCE_THRESHOLD: float = property(
        lambda self: TradingProfiles.get_current_profile()["paper_min_confidence"]
    )
    MAX_SLIPPAGE: float = property(
        lambda self: TradingProfiles.get_current_profile()["max_slippage"]
    )
    MIN_LIQUIDITY: float = property(
        lambda self: TradingProfiles.get_current_profile()["min_liquidity"]
    )

    # Máximo % del balance disponible para trading (reserva para fees)
    MAX_BALANCE_USAGE: float = 0.95


# ============================================================================
# 🛡️ CONFIGURACIÓN DEL GESTOR DE RIESGO
# ============================================================================


class RiskManagerConfig:
    """
    Configuración avanzada del gestor de riesgo con parámetros dinámicos por perfil.

    Esta clase centraliza todos los parámetros de gestión de riesgo del sistema,
    proporcionando controles adaptativos según el perfil de trading activo.
    Incluye gestión de posiciones, stop-loss, take-profit, y circuit breakers.

    Características principales:
    - 🎯 Límites de riesgo por trade y diarios adaptativos
    - 📊 Gestión dinámica de tamaños de posición
    - 🔄 ATR (Average True Range) configurables por volatilidad
    - 🛑 Stop-loss y take-profit inteligentes
    - ⚡ Trailing stops y breakeven automáticos
    - 🚨 Circuit breakers por drawdown y pérdidas consecutivas

    Parámetros de riesgo:
    - Riesgo máximo por trade (% del capital)
    - Riesgo diario máximo acumulado
    - Umbral de drawdown para suspensión
    - Correlación máxima entre posiciones
    - Multiplicadores ATR por condición de mercado

    Uso:
        # Obtener límites de riesgo dinámicos
        max_risk = RiskManagerConfig.get_max_risk_per_trade()
        atr_mult = RiskManagerConfig.get_atr_default()
        sl_pct = RiskManagerConfig.get_sl_min_percentage()

    Nota:
        La gestión de riesgo es crítica para la supervivencia del capital
        y debe ser monitoreada constantemente durante el trading.
    """

    """Configuración del gestor de riesgo avanzado."""

    @classmethod
    def get_max_risk_per_trade(cls) -> float:
        """Obtiene el riesgo máximo por trade según perfil activo."""
        return TradingProfiles.get_current_profile()["max_risk_per_trade_percent"] / 100

    @classmethod
    def get_max_daily_risk(cls) -> float:
        """Obtiene el riesgo máximo diario según perfil activo."""
        return TradingProfiles.get_current_profile()["max_daily_risk_percent"] / 100

    @classmethod
    def get_max_drawdown_threshold(cls) -> float:
        """Obtiene el umbral de drawdown máximo según perfil activo."""
        return (
            TradingProfiles.get_current_profile()["max_drawdown_threshold_percent"]
            / 100
        )

    @classmethod
    def get_correlation_threshold(cls) -> float:
        """Obtiene el umbral de correlación según perfil activo."""
        return TradingProfiles.get_current_profile()["correlation_threshold"]

    @classmethod
    def get_min_position_size(cls) -> float:
        """Obtiene el tamaño mínimo de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["min_position_size"]

    @classmethod
    def get_max_position_size(cls) -> float:
        """Obtiene el tamaño máximo de posición según perfil activo."""
        return (
            TradingProfiles.get_current_profile()["risk_max_position_size_percent"]
            / 100
        )

    @classmethod
    def get_kelly_fraction(cls) -> float:
        """Obtiene la fracción Kelly según perfil activo."""
        return TradingProfiles.get_current_profile()["kelly_fraction"]

    @classmethod
    def get_atr_multiplier_min(cls) -> float:
        """Obtiene el multiplicador ATR mínimo según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_multiplier_min"]

    @classmethod
    def get_atr_multiplier_max(cls) -> float:
        """Obtiene el multiplicador ATR máximo según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_multiplier_max"]

    @classmethod
    def get_atr_default(cls) -> float:
        """Obtiene el multiplicador ATR por defecto según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_default"]

    @classmethod
    def get_atr_volatile(cls) -> float:
        """Obtiene el multiplicador ATR para mercados volátiles según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_volatile"]

    @classmethod
    def get_atr_sideways(cls) -> float:
        """Obtiene el multiplicador ATR para mercados laterales según perfil activo."""
        return TradingProfiles.get_current_profile()["atr_sideways"]

    @classmethod
    def get_trailing_stop_activation(cls) -> float:
        """Obtiene el umbral de activación del trailing stop según perfil activo."""
        return TradingProfiles.get_current_profile()["trailing_stop_activation"]

    @classmethod
    def get_breakeven_threshold(cls) -> float:
        """Obtiene el umbral de breakeven según perfil activo."""
        return (
            TradingProfiles.get_current_profile()["breakeven_threshold_percent"] / 100
        )

    @classmethod
    def get_tp_min_percentage(cls) -> float:
        """Obtiene el porcentaje mínimo de Take Profit según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_min_percent"] / 100

    @classmethod
    def get_tp_max_percentage(cls) -> float:
        """Obtiene el porcentaje máximo de Take Profit según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_max_percent"] / 100

    @classmethod
    def get_sl_min_percentage(cls) -> float:
        """Obtiene el porcentaje mínimo de Stop Loss según perfil activo."""
        return TradingProfiles.get_current_profile()["sl_min_percent"] / 100

    @classmethod
    def get_sl_max_percentage(cls) -> float:
        """Obtiene el porcentaje máximo de Stop Loss según perfil activo."""
        return TradingProfiles.get_current_profile()["sl_max_percent"] / 100

    @classmethod
    def get_tp_increment_percentage(cls) -> float:
        """Obtiene el porcentaje de incremento de TP según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_increment_percent"]

    @classmethod
    def get_tp_confidence_threshold(cls) -> float:
        """Obtiene el umbral de confianza para ajustar TP según perfil activo."""
        return TradingProfiles.get_current_profile()["tp_confidence_threshold"]

    @classmethod
    def get_max_daily_loss_percent(cls) -> float:
        """Obtiene el porcentaje máximo de pérdida diaria según perfil activo."""
        return TradingProfiles.get_current_profile()["max_daily_loss_percent"]

    @classmethod
    @classmethod
    def get_min_confidence_threshold(cls) -> float:
        """Obtiene el umbral mínimo de confianza según perfil activo."""
        return TradingProfiles.get_current_profile()["min_confidence_threshold"]

    @classmethod
    def get_position_size_multiplier(cls) -> float:
        """Obtiene el multiplicador de tamaño de posición según perfil activo."""
        return TradingProfiles.get_current_profile()["position_size_multiplier"]

    # Propiedades dinámicas para compatibilidad con código existente
    MAX_RISK_PER_TRADE: float = property(
        lambda self: TradingProfiles.get_current_profile()["max_risk_per_trade_percent"]
    )
    MAX_DAILY_RISK: float = property(
        lambda self: TradingProfiles.get_current_profile()["max_daily_risk_percent"]
    )
    MAX_DRAWDOWN_THRESHOLD: float = property(
        lambda self: TradingProfiles.get_current_profile()[
            "max_drawdown_threshold_percent"
        ]
    )
    CORRELATION_THRESHOLD: float = property(
        lambda self: TradingProfiles.get_current_profile()["correlation_threshold"]
    )
    MIN_POSITION_SIZE: float = property(
        lambda self: TradingProfiles.get_current_profile()["min_position_size"]
    )
    MAX_POSITION_SIZE: float = property(
        lambda self: TradingProfiles.get_current_profile()[
            "risk_max_position_size_percent"
        ]
    )
    KELLY_FRACTION: float = property(
        lambda self: TradingProfiles.get_current_profile()["kelly_fraction"]
    )

    ATR_MULTIPLIER_MIN: float = property(
        lambda self: TradingProfiles.get_current_profile()["atr_multiplier_min"]
    )
    ATR_MULTIPLIER_MAX: float = property(
        lambda self: TradingProfiles.get_current_profile()["atr_multiplier_max"]
    )
    ATR_DEFAULT: float = property(
        lambda self: TradingProfiles.get_current_profile()["atr_default"]
    )
    ATR_VOLATILE: float = property(
        lambda self: TradingProfiles.get_current_profile()["atr_volatile"]
    )
    ATR_SIDEWAYS: float = property(
        lambda self: TradingProfiles.get_current_profile()["atr_sideways"]
    )
    TRAILING_STOP_ACTIVATION: float = property(
        lambda self: TradingProfiles.get_current_profile()["trailing_stop_activation"]
    )
    BREAKEVEN_THRESHOLD: float = property(
        lambda self: TradingProfiles.get_current_profile()[
            "breakeven_threshold_percent"
        ]
    )

    # Valor inicial del portfolio para cálculos de riesgo en USD - Se alimenta del PaperTrader para consistencia
    INITIAL_PORTFOLIO_VALUE: float = (
        PaperTraderConfig.INITIAL_BALANCE
    )  # Mantiene consistencia automática


# ============================================================================
# 📊 CONFIGURACIÓN DE ESTRATEGIAS DE TRADING
# ============================================================================


class StrategyConfig:
    """
    Configuración centralizada de las estrategias de trading.

    Esta clase proporciona configuraciones específicas para diferentes tipos de estrategias
    de trading, incluyendo configuraciones base y especializadas para cada perfil.

    Características principales:
    - Configuraciones dinámicas basadas en perfiles activos
    - Parámetros de confianza y ATR personalizables
    - Configuraciones base para todas las estrategias
    - Soporte para múltiples tipos de estrategias

    Estrategias soportadas:
    - Estrategias base con configuraciones generales
    - Configuraciones específicas por perfil de trading
    - Parámetros de confianza adaptativos

    Ejemplo de uso:
        >>> config = StrategyConfig.get_current_profile_config()
        >>> min_confidence = StrategyConfig.Base.get_default_min_confidence()
        >>> atr_period = StrategyConfig.Base.get_default_atr_period()

    Nota:
        Las configuraciones se actualizan automáticamente según el perfil activo
        y proporcionan valores por defecto seguros para todas las estrategias.
    """

    @classmethod
    def get_current_profile_config(cls) -> Dict[str, Any]:
        """
        Obtiene la configuración completa del perfil activo.

        Returns:
            Dict[str, Any]: Diccionario con toda la configuración del perfil actual
        """
        return TradingProfiles.get_current_profile()

    # ---- 🎯 Configuración Base de Estrategias ----
    class Base:
        """
        Configuración base compartida por todas las estrategias de trading.

        Esta subclase proporciona parámetros fundamentales que son utilizados
        por todas las estrategias, incluyendo niveles de confianza y períodos ATR.

        Características:
        - Configuraciones dinámicas basadas en el perfil activo
        - Valores de fallback para garantizar estabilidad
        - Niveles de confianza predefinidos para diferentes tipos de señales
        - Compatibilidad con código existente

        Ejemplo de uso:
            >>> min_confidence = StrategyConfig.Base.get_default_min_confidence()
            >>> atr_period = StrategyConfig.Base.get_default_atr_period()
            >>> hold_level = StrategyConfig.Base.HOLD_CONFIDENCE
        """

        @classmethod
        def get_default_min_confidence(cls) -> float:
            """
            Obtiene la confianza mínima según el perfil activo.

            Returns:
                float: Nivel de confianza mínimo (por defecto 55.0)
            """
            return TradingProfiles.get_current_profile().get(
                "default_min_confidence", 55.0
            )

        @classmethod
        def get_default_atr_period(cls) -> int:
            """
            Obtiene el período ATR según el perfil activo.

            Returns:
                int: Período para el cálculo del ATR (por defecto 10)
            """
            return TradingProfiles.get_current_profile().get("default_atr_period", 10)

        # 📊 Valores de confianza por defecto para diferentes tipos de señales
        HOLD_CONFIDENCE: float = 45.0  # Señales de mantener posición
        BASE_CONFIDENCE: float = 50.0  # Confianza base para señales estándar
        ENHANCED_CONFIDENCE: float = 60.0  # Confianza para señales mejoradas

        # 🔄 Compatibilidad con código existente (valores de fallback)
        DEFAULT_MIN_CONFIDENCE: float = 55.0  # Fallback para confianza mínima
        DEFAULT_ATR_PERIOD: int = 10  # Fallback para período ATR


# ============================================================================
# 📝 CONFIGURACIÓN DE LOGGING
# ============================================================================


class LoggingConfig:
    """
    Configuración centralizada del sistema de logging.

    Esta clase define todos los parámetros relacionados con el registro de eventos
    y actividades del sistema de trading, incluyendo niveles, formatos y rotación.

    Características principales:
    - Configuración de niveles de logging
    - Formato estandarizado de mensajes
    - Rotación automática de archivos de log
    - Gestión de archivos de backup

    Niveles soportados:
    - DEBUG: Información detallada para debugging
    - INFO: Información general del sistema
    - WARNING: Advertencias importantes
    - ERROR: Errores que no detienen la ejecución
    - CRITICAL: Errores críticos del sistema

    Ejemplo de uso:
        >>> level = LoggingConfig.LOG_LEVEL
        >>> format_str = LoggingConfig.LOG_FORMAT
        >>> max_size = LoggingConfig.MAX_LOG_SIZE_MB

    Nota:
        Los logs se rotan automáticamente cuando alcanzan el tamaño máximo,
        manteniendo un número específico de archivos de backup.
    """

    # 📊 Nivel de logging por defecto (INFO para balance entre información y rendimiento)
    LOG_LEVEL: str = "INFO"

    # 🎯 Formato de logs con timestamp completo (incluye fecha, hora, módulo y nivel)
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # 📁 Archivo principal de logs del sistema
    LOG_FILE: str = "trading_bot.log"

    # 💾 Tamaño máximo del archivo de log en MB antes de rotación
    MAX_LOG_SIZE_MB: int = 10

    # 🔄 Número de archivos de backup a mantener durante la rotación
    LOG_BACKUP_COUNT: int = 5


# ============================================================================
# 🚀 CONFIGURACIÓN DE TRADING EN VIVO (LIVE TRADING)
# ============================================================================


class LiveTradingConfig:
    """
    Configuración específica para operaciones de trading en vivo.

    Esta clase contiene todos los parámetros necesarios para ejecutar trading
    real con dinero, incluyendo configuraciones de órdenes, timeouts y fees.

    Características principales:
    - Balance inicial sincronizado con paper trading
    - Configuración de fees dinámicos por perfil
    - Timeouts optimizados para estrategias rápidas
    - Configuración de reintentos de órdenes
    - Intervalos de verificación de órdenes

    Configuraciones de seguridad:
    - Timeouts cortos para estrategias rápidas
    - Límite de reintentos para evitar loops
    - Verificación frecuente del estado de órdenes

    Ejemplo de uso:
        >>> balance = LiveTradingConfig.INITIAL_BALANCE
        >>> fees = LiveTradingConfig.TRADING_FEES
        >>> timeout = LiveTradingConfig.ORDER_TIMEOUT

    Nota:
        El balance inicial se sincroniza automáticamente con PaperTraderConfig
        para mantener consistencia entre modos de trading.
    """

    # 💰 Balance inicial real en USD - Sincronizado automáticamente con paper trading
    INITIAL_BALANCE: float = (
        PaperTraderConfig.INITIAL_BALANCE
    )  # Mantiene consistencia automática

    # 💸 Comisiones de exchange en % por trade - Configurable vía entorno TRADING_FEES
    # Fallback: perfil actual TradingProfiles["trading_fees"] si existe, sino 0.001 (0.1%)
    TRADING_FEES: float = _get_env_float(
        "TRADING_FEES", TradingProfiles.get_current_profile().get("trading_fees", 0.001)
    )

    # ⏱️ Timeout para órdenes en segundos - Optimizado por estrategia
    # Scalping: 15s (ejecución rápida) - Intraday: 35s (más tolerante)
    ORDER_TIMEOUT: int = 15  # Estrategia rápida

    # 🔄 Reintentos máximos para órdenes fallidas - Balanceado por estrategia
    # Scalping: 2 reintentos (rápido) - Intraday: 3 reintentos (más persistente)
    MAX_ORDER_RETRIES: int = 2  # Estrategia rápida

    # 🔍 Intervalo de verificación de órdenes en segundos - Frecuencia de monitoreo
    # Scalping: 1s (alta frecuencia) - Intraday: 1.8s (frecuencia moderada)
    ORDER_CHECK_INTERVAL: int = 1  # Estrategia rápida


# Expone TRADING_FEES a nivel de módulo para compatibilidad retroactiva
TRADING_FEES: float = LiveTradingConfig.TRADING_FEES

# ============================================================================
# FUNCIÓN DE UTILIDAD PARA OBTENER CONFIGURACIONES
# ============================================================================


def get_config(config_type: str) -> Any:
    """Obtiene la configuración especificada.

    Args:
        config_type: Tipo de configuración ('bot', 'risk', 'paper', 'strategy', 'db', 'log', 'live', 'testing', 'indicators')

    Returns:
        Clase de configuración correspondiente
    """
    configs = {
        "bot": TradingBotConfig,
        "risk": RiskManagerConfig,
        "paper": PaperTraderConfig,
        "strategy": StrategyConfig,
        "log": LoggingConfig,
        "live": LiveTradingConfig,
        "testing": TestingConfig,
        "indicators": AdvancedIndicatorsConfig,
    }

    if config_type not in configs:
        raise ValueError(
            f"Tipo de configuración '{config_type}' no válido. Opciones: {list(configs.keys())}"
        )

    return configs[config_type]


# ============================================================================
# CONFIGURACIÓN DE INDICADORES AVANZADOS
# ============================================================================


class AdvancedIndicatorsConfig:
    """Configuración de períodos y umbrales para indicadores técnicos avanzados."""

    # Períodos para Ichimoku Cloud
    ICHIMOKU_TENKAN_PERIOD: int = 9  # Tenkan-sen (línea de conversión)
    ICHIMOKU_KIJUN_PERIOD: int = 26  # Kijun-sen (línea base)
    ICHIMOKU_SENKOU_PERIOD: int = 52  # Senkou Span A
    ICHIMOKU_SENKOU_B_PERIOD: int = 52  # Senkou Span B
    ICHIMOKU_SHIFT: int = 26  # Desplazamiento para proyección

    # Períodos para osciladores
    STOCHASTIC_K_PERIOD: int = 14  # Período para %K del Estocástico
    STOCHASTIC_D_PERIOD: int = 3  # Período para %D del Estocástico
    WILLIAMS_R_PERIOD: int = 14  # Período para Williams %R

    # Umbrales para osciladores
    STOCHASTIC_OVERSOLD: float = 20.0  # Umbral de sobreventa
    STOCHASTIC_OVERBOUGHT: float = 80.0  # Umbral de sobrecompra
    WILLIAMS_R_OVERSOLD: float = -80.0  # Umbral de sobreventa Williams %R
    WILLIAMS_R_OVERBOUGHT: float = -20.0  # Umbral de sobrecompra Williams %R

    # Períodos para otros indicadores
    RSI_PERIOD: int = 14  # Período para RSI
    CCI_PERIOD: int = 20  # Período para CCI
    BOLLINGER_PERIOD: int = 20  # Período para Bandas de Bollinger
    BOLLINGER_STD_DEV: float = 2.0  # Desviación estándar para Bollinger
    MFI_PERIOD: int = 14  # Período para Money Flow Index
    ATR_PERIOD: int = 14  # Período para Average True Range
    ROC_PERIOD: int = 12  # Período para Rate of Change

    # Configuración para análisis de soporte/resistencia
    SUPPORT_RESISTANCE_WINDOW: int = 20  # Ventana para S/R
    SUPPORT_RESISTANCE_MIN_TOUCHES: int = 2  # Mínimo de toques para validar nivel

    # Configuración para análisis de volumen
    VOLUME_PROFILE_BINS: int = 20  # Número de bins para perfil de volumen

    # Configuración para Fibonacci
    FIBONACCI_LOOKBACK: int = 50  # Período de lookback para Fibonacci

    # Configuración para análisis de tendencias
    TREND_ANALYSIS_LOOKBACK: int = 50  # Período para análisis de líneas de tendencia
    CHART_PATTERNS_WINDOW: int = 20  # Ventana para detección de patrones


# ============================================================================
# CONFIGURACIÓN DE TESTING
# ============================================================================


class TestingConfig:
    """Configuración específica para testing y desarrollo."""

    # Símbolos para testing - subset reducido para pruebas rápidas
    TEST_SYMBOLS: List[str] = GLOBAL_SYMBOLS[:3]  # Primeros 3 símbolos

    # Configuración de trading bot para testing
    TEST_MIN_CONFIDENCE: float = 70.0
    TEST_MAX_DAILY_TRADES: int = 5

    # Configuración de análisis para testing
    TEST_ANALYSIS_INTERVAL: int = 300  # 300 segundos (5 minutos)

    # Balance para testing
    TEST_PAPER_BALANCE: float = 100.0


# ============================================================================
# CONFIGURACIÓN POR DEFECTO PARA DESARROLLO
# ============================================================================

# Configuración rápida para desarrollo y testing
DEV_CONFIG = {
    "symbols": TradingBotConfig.SYMBOLS[:3],  # Solo 3 símbolos para testing
    "analysis_interval": TestingConfig.TEST_ANALYSIS_INTERVAL,  # Análisis cada 5 minutos para testing
    "min_confidence": 60.0,  # Umbral más bajo para testing
    "paper_balance": TestingConfig.TEST_PAPER_BALANCE,  # Balance menor para testing
}

# ============================================================================
# 🔧 CONFIGURACIONES CENTRALIZADAS DE PARÁMETROS HARDCODEADOS
# ============================================================================


class APIConfig:
    """🌐 Configuración centralizada de APIs y endpoints"""

    # API Configuration (Binance removed - using Capital.com only)

    # Request Configuration
    REQUEST_TIMEOUT = 5  # segundos
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # segundos

    # Sleep intervals para scheduler y error handling
    SCHEDULER_SLEEP_INTERVAL = 2  # segundos (aumentado para evitar rate limiting)
    ERROR_RECOVERY_SLEEP = 10  # segundos (aumentado para mejor recuperación)
    LATENCY_SIMULATION_SLEEP = 0.5  # segundos (aumentado para simular latencia real)

    # Data Limits
    DEFAULT_KLINES_LIMIT = 1000
    MAX_KLINES_LIMIT = 1500
    MIN_KLINES_LIMIT = 100

    @classmethod
    def get_request_config(cls) -> dict:
        """Obtener configuración de requests"""
        return {
            "timeout": cls.REQUEST_TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY,
        }


class CacheConfig:
    """💾 Configuración centralizada de cache"""

    # Cache TTL (Time To Live)
    DEFAULT_TTL = 300  # 5 minutos
    SHORT_TTL = 60  # 1 minuto
    LONG_TTL = 900  # 15 minutos

    # Cache Limits
    MAX_CACHE_ENTRIES = 1000
    CLEANUP_THRESHOLD = 1200

    # Cache Keys
    CACHE_KEY_PREFIXES = {
        "volume_analysis": "vol_",
        "trend_analysis": "trend_",
        "confluence": "conf_",
        "market_regime": "regime_",
    }

    @classmethod
    def get_ttl_for_operation(cls, operation_type: str) -> int:
        """Obtener TTL según tipo de operación"""
        ttl_map = {
            "price_data": cls.SHORT_TTL,
            "technical_analysis": cls.DEFAULT_TTL,
            "market_structure": cls.LONG_TTL,
        }
        return ttl_map.get(operation_type, cls.DEFAULT_TTL)


class TechnicalAnalysisConfig:
    """📊 Configuración centralizada de análisis técnico"""

    # Períodos de Rolling Windows
    VOLUME_PERIODS = {"short": 10, "medium": 20, "long": 50}

    # Períodos EMA
    EMA_PERIODS = {"fast": 20, "slow": 50, "trend": 200}

    # Umbrales de Volumen
    VOLUME_THRESHOLDS = {
        "very_strong": 2.5,
        "strong": 1.8,
        "moderate": 1.3,
        "weak": 1.0,
    }

    # Umbrales ADX
    ADX_THRESHOLDS = {"strong_trend": 25, "weak_trend": 20, "no_trend": 15}

    # Desviaciones y Tolerancias
    VWAP_DEVIATION_THRESHOLD = 0.02  # 2%
    VOLATILITY_RATIO_THRESHOLD = 1.5
    PRICE_RANGE_TOLERANCE = 0.2  # 20%

    # Factores de Aproximación
    APPROXIMATION_FACTORS = {
        "close": 0.98,
        "exact": 1.00,
        "far": 1.02,
        "very_close": 0.99,
    }

    @classmethod
    def get_volume_strength(cls, ratio: float) -> str:
        """Determinar fuerza del volumen basado en ratio"""
        if ratio >= cls.VOLUME_THRESHOLDS["very_strong"]:
            return "VERY_STRONG"
        elif ratio >= cls.VOLUME_THRESHOLDS["strong"]:
            return "STRONG"
        elif ratio >= cls.VOLUME_THRESHOLDS["moderate"]:
            return "MODERATE"
        else:
            return "WEAK"


class ConfluenceConfig:
    """🎯 Configuración centralizada de confluencia"""

    # Pesos de Componentes
    COMPONENT_WEIGHTS = {
        "technical": 0.4,
        "volume": 0.25,
        "structure": 0.2,
        "momentum": 0.15,
    }

    # Umbrales de Confluencia
    CONFLUENCE_THRESHOLDS = {
        "very_strong": 0.8,
        "strong": 0.65,
        "moderate": 0.45,
        "weak": 0.0,
    }

    # Pesos de Indicadores Técnicos
    TECHNICAL_WEIGHTS = {"rsi": 0.4, "bollinger_bands": 0.3, "vwap": 0.3}

    # Pesos de Análisis de Volumen
    VOLUME_WEIGHTS = {"strength": 0.5, "confirmation": 0.3, "trend_bonus": 0.2}

    # Pesos de Estructura de Mercado
    STRUCTURE_WEIGHTS = {"support_resistance": 0.6, "trend_lines": 0.4}

    # Pesos de Momentum
    MOMENTUM_WEIGHTS = {"roc": 0.5, "mfi": 0.5}

    @classmethod
    def get_confluence_level(cls, score: float) -> str:
        """Determinar nivel de confluencia basado en score"""
        if score >= cls.CONFLUENCE_THRESHOLDS["very_strong"]:
            return "VERY_STRONG"
        elif score >= cls.CONFLUENCE_THRESHOLDS["strong"]:
            return "STRONG"
        elif score >= cls.CONFLUENCE_THRESHOLDS["moderate"]:
            return "MODERATE"
        else:
            return "WEAK"


class MonitoringConfig:
    """🔍 Configuración centralizada de monitoreo"""

    # Intervalos de Tiempo
    DEFAULT_HOURS_BACK = 24
    ANALYSIS_INTERVALS = {
        "short": 1,  # 1 hora
        "medium": 6,  # 6 horas
        "long": 24,  # 24 horas
        "extended": 72,  # 72 horas
    }

    # Intervalos de Actualización
    UPDATE_INTERVALS = {
        "live_bot": 30,  # 30 segundos
        "monitoring": 60,  # 1 minuto
        "analysis": 300,  # 5 minutos
        "reporting": 900,  # 15 minutos
    }

    # Límites de Datos
    DATA_LIMITS = {
        "max_missed_executions": 100,
        "max_log_entries": 1000,
        "max_history_days": 30,
    }

    @classmethod
    def get_analysis_hours(cls, analysis_type: str) -> int:
        """Obtener horas de análisis según tipo"""
        return cls.ANALYSIS_INTERVALS.get(analysis_type, cls.DEFAULT_HOURS_BACK)

    @classmethod
    def get_update_interval(cls, component: str) -> int:
        """Obtener intervalo de actualización según componente"""
        return cls.UPDATE_INTERVALS.get(component, 60)


class FibonacciConfig:
    """📐 Configuración centralizada de niveles de Fibonacci"""

    # Niveles de Retroceso de Fibonacci
    RETRACEMENT_LEVELS = [0.236, 0.382, 0.500, 0.618, 0.786]

    # Niveles de Extensión de Fibonacci
    EXTENSION_LEVELS = [1.272, 1.414, 1.618, 2.000, 2.618]

    # Tolerancias para Niveles
    LEVEL_TOLERANCES = {
        "tight": 0.005,  # 0.5%
        "normal": 0.01,  # 1%
        "loose": 0.02,  # 2%
    }

    @classmethod
    def get_retracement_levels(cls) -> list:
        """Obtener niveles de retroceso"""
        return cls.RETRACEMENT_LEVELS.copy()

    @classmethod
    def get_extension_levels(cls) -> list:
        """Obtener niveles de extensión"""
        return cls.EXTENSION_LEVELS.copy()


class OscillatorConfig:
    """📈 Configuración centralizada de osciladores"""

    # Umbrales RSI
    RSI_THRESHOLDS = {
        "oversold_extreme": 20,
        "oversold": 30,
        "neutral_low": 40,
        "neutral_high": 60,
        "overbought": 70,
        "overbought_extreme": 80,
    }

    # Umbrales Williams %R
    WILLIAMS_R_THRESHOLDS = {"oversold": -80, "overbought": -20}

    # Umbrales Stochastic
    STOCHASTIC_THRESHOLDS = {"oversold": 20, "overbought": 80}

    # Umbrales de Señales
    SIGNAL_THRESHOLDS = {
        "strong_buy": -100,
        "buy": -50,
        "neutral": 0,
        "sell": 50,
        "strong_sell": 100,
    }

    @classmethod
    def get_rsi_condition(cls, rsi_value: float) -> str:
        """Determinar condición RSI"""
        if rsi_value <= cls.RSI_THRESHOLDS["oversold_extreme"]:
            return "OVERSOLD_EXTREME"
        elif rsi_value <= cls.RSI_THRESHOLDS["oversold"]:
            return "OVERSOLD"
        elif rsi_value >= cls.RSI_THRESHOLDS["overbought_extreme"]:
            return "OVERBOUGHT_EXTREME"
        elif rsi_value >= cls.RSI_THRESHOLDS["overbought"]:
            return "OVERBOUGHT"
        else:
            return "NEUTRAL"


class CalculationConfig:
    """🧮 Configuración centralizada de constantes de cálculo"""

    # Constantes Matemáticas
    PARABOLIC_SAR_STEP = 0.015
    PARABOLIC_SAR_MAX = 0.2

    # Períodos de Cálculo
    DEFAULT_PERIODS = {"short": 5, "medium": 14, "long": 34, "very_long": 55}

    # Factores de Suavizado
    SMOOTHING_FACTORS = {"alpha": 2.0, "beta": 0.5, "gamma": 0.1}

    # Multiplicadores Estándar
    STANDARD_MULTIPLIERS = {
        "bollinger_std": 2.0,
        "atr_multiplier": 1.5,
        "volume_multiplier": 1.2,
    }

    @classmethod
    def get_period(cls, period_type: str) -> int:
        """Obtener período según tipo"""
        return cls.DEFAULT_PERIODS.get(period_type, 14)


# ============================================================================
# VALIDACIÓN DE CONFIGURACIÓN
# ============================================================================


class ConfigValidator:
    """Validador de parámetros de configuración para asegurar valores válidos."""

    # Rangos válidos para parámetros críticos
    VALID_RANGES = {
        "max_position_size": (0.01, 1.0),
        "max_total_exposure": (0.1, 1.0),
        "min_trade_value": (1.0, 1000.0),
        "max_slippage": (0.001, 0.1),
        "stop_loss_percentage": (0.01, 0.5),
        "take_profit_percentage": (0.01, 1.0),
        "trailing_stop_activation": (0.006, 0.5),
        "trailing_stop_distance": (0.005, 0.2),
        "max_drawdown_threshold": (0.05, 0.5),
        "min_confidence_score": (30, 95),
        "analysis_interval": (1, 3600),
        "position_check_interval": (10, 300),
        "connection_timeout": (5, 120),
        "max_retries": (1, 10),
        "retry_delay": (0.5, 30.0),
        "max_consecutive_losses": (1, 20),
    }

    @classmethod
    def validate_profile(cls, profile_name: str, profile_config: dict) -> bool:
        """Validar que un perfil tenga parámetros en rangos válidos."""
        errors = []

        for param, value in profile_config.items():
            if param in cls.VALID_RANGES:
                min_val, max_val = cls.VALID_RANGES[param]
                if not (min_val <= value <= max_val):
                    errors.append(
                        f"Perfil '{profile_name}': {param}={value} fuera del rango válido [{min_val}, {max_val}]"
                    )

        if errors:
            logger.error(f"Errores de validación en perfil '{profile_name}':")
            for error in errors:
                logger.error(f"  - {error}")
            return False

        logger.info(f"Perfil '{profile_name}' validado correctamente")
        return True

    @classmethod
    def validate_all_profiles(cls) -> bool:
        """Validar todos los perfiles de trading."""
        all_valid = True

        for profile_name, profile_config in TradingProfiles.PROFILES.items():
            if not cls.validate_profile(profile_name, profile_config):
                all_valid = False

        return all_valid

    @classmethod
    def get_safe_value(
        cls, param_name: str, value: float, default: float = None
    ) -> float:
        """Obtener un valor seguro dentro del rango válido."""
        if param_name not in cls.VALID_RANGES:
            return value


# ============================================================================
# INICIALIZACIÓN Y VALIDACIÓN AUTOMÁTICA
# ============================================================================


def initialize_config() -> bool:
    """Inicializar y validar toda la configuración del sistema."""
    logger.info("Inicializando configuración del sistema de trading...")

    # Validar todos los perfiles
    if not ConfigValidator.validate_all_profiles():
        logger.error("Falló la validación de perfiles. Revise la configuración.")
        return False

    # Validar perfil actual mediante getters
    try:
        current_profile = TradingProfiles.get_current_profile()
    except ValueError:
        logger.error(
            f"Perfil actual no existe. Perfiles disponibles: {list(TradingProfiles.PROFILES.keys())}"
        )
        return False

    # Mostrar configuración actual
    profile_name = current_profile.get("name", "DESCONOCIDO")
    logger.info(f"Perfil activo: {profile_name}")
    logger.info(f"Timeframes: {current_profile['timeframes']}")
    logger.info(f"Intervalo de análisis: {current_profile['analysis_interval']} min")
    logger.info(f"Confianza mínima: {current_profile['min_confidence']}%")

    logger.info("✅ Configuración inicializada correctamente")
    return True


# ============================================================================
# 🔄 FUNCIONES UTILITARIAS PARA SÍMBOLOS
# ============================================================================
# Las funciones de conversión fueron eliminadas porque GLOBAL_SYMBOLS
# ya contiene los nombres exactos de Capital.com


def get_all_capital_symbols() -> List[str]:
    """
    Obtiene todos los símbolos (ya están en formato Capital.com)

    Returns:
        Lista de símbolos de Capital.com
    """
    return GLOBAL_SYMBOLS.copy()


def validate_symbol_mapping() -> bool:
    """
    Valida que GLOBAL_SYMBOLS contenga símbolos válidos

    Returns:
        True si los símbolos son válidos
    """
    if not GLOBAL_SYMBOLS:
        logger.warning("⚠️ GLOBAL_SYMBOLS está vacío")
        return False

    logger.info(f"✅ GLOBAL_SYMBOLS configurado con {len(GLOBAL_SYMBOLS)} símbolos")
    return True


# Validar configuración al importar el módulo
try:
    if not initialize_config():
        logger.warning("⚠️ Configuración inicializada con advertencias")

    # Validar mapeo de símbolos
    validate_symbol_mapping()

except Exception as e:
    logger.error(f"❌ Error al inicializar configuración: {e}")
