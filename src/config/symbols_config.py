# ============================================================================
# 🪙 CONFIGURACIÓN OPTIMIZADA DE SÍMBOLOS DE TRADING
# ============================================================================
"""
Configuración centralizada y optimizada de símbolos para el sistema de trading automatizado.
Incluye criptomonedas, forex, commodities e índices organizados por volatilidad y liquidez.
"""

# ============================================================================
# 🚀 CRIPTOMONEDAS - ALTA VOLATILIDAD Y LIQUIDEZ 24/7
# ============================================================================

# Criptomonedas principales (no usadas en core actual)
CRYPTO_MAJOR = []

# Criptomonedas de alta capitalización - Buena liquidez, mayor volatilidad
CRYPTO_LARGE_CAP = []

# Criptomonedas emergentes - Alta volatilidad, oportunidades de crecimiento
CRYPTO_EMERGING = []

# ============================================================================
# 💱 FOREX - PARES DE DIVISAS PRINCIPALES Y EXÓTICOS
# ============================================================================

# Pares mayores - Máxima liquidez, spreads bajos
FOREX_MAJOR = []

# Pares menores - Buena liquidez, mayor volatilidad
FOREX_MINOR = []

# Pares exóticos - Alta volatilidad, spreads más amplios
FOREX_EXOTIC = []

# ============================================================================
# 🥇 COMMODITIES - MATERIAS PRIMAS Y METALES PRECIOSOS
# ============================================================================

# Metales preciosos - Safe haven assets
METALS_PRECIOUS = [
    "GOLD",
]

# Energía - Commodities energéticos
ENERGY_COMMODITIES = []

# Agricultura - Soft commodities
AGRICULTURAL = [
    # Eliminado: sin soft commodities en el portafolio actual
]

# Metales industriales
METALS_INDUSTRIAL = [
    # Eliminado: sin metales industriales en el portafolio actual
]

# ============================================================================
# 📊 ÍNDICES - REPRESENTAN MERCADOS Y SECTORES
# ============================================================================

# Índices americanos
INDICES_US = [
    "US500",
]

# Índices europeos
INDICES_EUROPE = [
    "UK100",
    "FR40",
]

# Índices asiáticos
INDICES_ASIA = [
    "HK50",
]

# ============================================================================
# 🎯 CONFIGURACIÓN GLOBAL OPTIMIZADA
# ============================================================================

# Portafolio core definitivo (v1) sin forex: índices, metales y commodities
CORE_SYMBOLS_V1 = [
    # Metales
    "GOLD",
    # Índices
    "US500", "UK100", "FR40", "HK50",
]

# Lista principal de símbolos para el bot: usar el portafolio core
GLOBAL_SYMBOLS = CORE_SYMBOLS_V1

# Configuración específica por símbolo (versión CORE utilizada por el bot)
SYMBOL_SPECIFIC_CONFIG_CORE = {
    "GOLD": {
        "category": "metals_precious",
        "volatility": "medium",
        "avg_daily_range": 1.5,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.05,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "US500": {
        "category": "indices_us",
        "volatility": "medium",
        "avg_daily_range": 1.2,
        "optimal_hours": ["14:30-21:00"],
        "spread_typical": 0.1,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "UK100": {
        "category": "indices_europe",
        "volatility": "medium",
        "avg_daily_range": 1.2,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.3,
        "min_confidence_adjustment": 1,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "FR40": {
        "category": "indices_europe",
        "volatility": "medium",
        "avg_daily_range": 1.3,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.2,
        "min_confidence_adjustment": 1,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "HK50": {
        "category": "indices_asia",
        "volatility": "high",
        "avg_daily_range": 2.0,
        "optimal_hours": ["01:00-08:00"],
        "spread_typical": 2.0,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "medium",
    },
}

# Alias para compatibilidad: usar siempre la versión CORE
SYMBOL_SPECIFIC_CONFIG = SYMBOL_SPECIFIC_CONFIG_CORE

# Símbolos por sesión de mercado óptima
MARKET_SESSION_SYMBOLS = {
    "asian": [
        "HK50",
        "GOLD",
    ],
    "european": [
        "UK100",
        "FR40",
        "GOLD",
    ],
    "american": [
        "US500",
        "GOLD",
    ],
}

# ============================================================================
# 🎯 FUNCIONES AUXILIARES PARA CONFIGURACIÓN DINÁMICA
# ============================================================================

# (Se usa el alias definido arriba para compatibilidad)


def get_symbol_config(symbol: str) -> dict:
    """
    Obtiene la configuración específica de un símbolo.

    Args:
        symbol: Símbolo a consultar (ej: 'BTCUSD')

    Returns:
        dict: Configuración del símbolo o configuración por defecto
    """
    default_config = {
        "category": "unknown",
        "volatility": "medium",
        "avg_daily_range": 2.0,
        "optimal_hours": ["09:00-17:00"],
        "spread_typical": 0.1,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "medium",
    }

    return SYMBOL_SPECIFIC_CONFIG_CORE.get(symbol, default_config)


# Sobrescribimos categorías de volatilidad y liquidez para reflejar únicamente el portafolio core.
# Esto evita referencias a símbolos fuera del core aunque existan definiciones históricas arriba.
VOLATILITY_CATEGORIES = {
    "very_low": [],
    "low": [],
    "medium": ["GOLD", "US500", "UK100", "FR40"],
    "high": ["HK50"],
    "very_high": [],
}

LIQUIDITY_CATEGORIES = {
    "very_high": ["GOLD", "US500"],
    "high": ["UK100", "FR40"],
    "medium": ["HK50"],
    "low": [],
}

def get_symbols_by_volatility(volatility_level: str) -> list:
    """
    Obtiene símbolos filtrados por nivel de volatilidad.

    Args:
        volatility_level: 'very_low', 'low', 'medium', 'high', 'very_high'

    Returns:
        list: Lista de símbolos del nivel de volatilidad especificado
    """
    return VOLATILITY_CATEGORIES.get(volatility_level, [])


def get_symbols_by_liquidity(liquidity_level: str) -> list:
    """
    Obtiene símbolos filtrados por nivel de liquidez.

    Args:
        liquidity_level: 'very_high', 'high', 'medium', 'low'

    Returns:
        list: Lista de símbolos del nivel de liquidez especificado
    """
    return LIQUIDITY_CATEGORIES.get(liquidity_level, [])


def get_symbols_by_session(session: str) -> list:
    """
    Obtiene símbolos óptimos para una sesión de mercado específica.

    Args:
        session: 'asian', 'european', 'american', 'crypto_24_7'

    Returns:
        list: Lista de símbolos óptimos para la sesión
    """
    return MARKET_SESSION_SYMBOLS.get(session, [])


def get_active_symbols_for_current_time() -> list:
    """
    Obtiene símbolos activos según la hora actual y sesiones de mercado.

    Returns:
        list: Lista de símbolos recomendados para trading actual
    """
    from datetime import datetime
    import pytz

    # Usar UTC para consistencia global
    current_hour = datetime.now(pytz.UTC).hour

    # Lógica simplificada por sesiones
    if 0 <= current_hour < 8:  # Sesión asiática
        return get_symbols_by_session("asian")
    elif 8 <= current_hour < 16:  # Sesión europea
        return get_symbols_by_session("european")
    else:  # Sesión americana
        return get_symbols_by_session("american")


# ============================================================================
# 📈 CONFIGURACIÓN DE PORTFOLIO BALANCEADO
# ============================================================================

# Portfolio conservador - Baja volatilidad, alta liquidez
CONSERVATIVE_PORTFOLIO = (
    get_symbols_by_volatility("low")
    + get_symbols_by_volatility("medium")[:3]
    # + ["BTCUSD", "ETHUSD"]  # Core crypto (eliminado temporalmente)
)

# Portfolio agresivo - Alta volatilidad, mayores oportunidades
AGGRESSIVE_PORTFOLIO = (
    get_symbols_by_volatility("high")
    + get_symbols_by_volatility("very_high")
    # + CRYPTO_EMERGING[:4]  # Eliminado temporalmente
)

# Portfolio balanceado - Mix óptimo de riesgo/recompensa
BALANCED_PORTFOLIO = GLOBAL_SYMBOLS  # Ya está balanceado
