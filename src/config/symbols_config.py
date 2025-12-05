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
FOREX_MAJOR = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "USDCHF",
    "USDCAD",
    "NZDUSD",
]

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
    "SILVER",
]

# Energía - Commodities energéticos
ENERGY_COMMODITIES = [
    "OIL_CRUDE",  # WTI (según Capital.com)
]

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
    # "US100",
    "US500",
]

# Índices europeos
INDICES_EUROPE = [
    "DE40",
    "UK100",
]

# Índices asiáticos
INDICES_ASIA = [
    "J225",
    "HK50",
]

# ============================================================================
# 🎯 CONFIGURACIÓN GLOBAL OPTIMIZADA
# ============================================================================

# Lista principal de símbolos para el bot: portafolio expandido (Forex + Commodities + Índices + Metales)
GLOBAL_SYMBOLS = [
    # Forex majors
    *FOREX_MAJOR,
    # Commodities energía
    *ENERGY_COMMODITIES,
    # Metales
    "GOLD",
    "SILVER",
    # Índices EEUU
    "US500",
    # Europa
    "DE40",
    "UK100",
    "FR40",
    # Asia
    "HK50",
    "J225",
]

# Configuración específica por símbolo (versión CORE utilizada por el bot)
SYMBOL_SPECIFIC_CONFIG_CORE = {
    # ==================== FOREX MAJORS ====================
    "EURUSD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 0.8,
        "avg_daily_range_pct": 0.008,
        "optimal_hours": ["07:00-12:00", "13:00-17:00"],
        "spread_typical": 0.00015,
        "spread_pct": 0.000136,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.2,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "GBPUSD": {
        "category": "forex_major",
        "volatility": "medium_high",
        "avg_daily_range": 1.0,
        "avg_daily_range_pct": 0.010,
        "optimal_hours": ["07:00-12:00", "13:00-17:00"],
        "spread_typical": 0.00020,
        "spread_pct": 0.000158,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.15,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "USDJPY": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 0.7,
        "avg_daily_range_pct": 0.007,
        "optimal_hours": ["00:00-05:00", "12:00-17:00"],
        "spread_typical": 0.01,
        "spread_pct": 0.000067,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "AUDUSD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 0.7,
        "avg_daily_range_pct": 0.007,
        "optimal_hours": ["23:00-05:00", "13:00-17:00"],
        "spread_typical": 0.00018,
        "spread_pct": 0.000269,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "USDCHF": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 0.7,
        "avg_daily_range_pct": 0.007,
        "optimal_hours": ["07:00-12:00", "13:00-17:00"],
        "spread_typical": 0.00020,
        "spread_pct": 0.000222,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "USDCAD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 0.8,
        "avg_daily_range_pct": 0.008,
        "optimal_hours": ["12:00-18:00"],
        "spread_typical": 0.00025,
        "spread_pct": 0.000184,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "NZDUSD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 0.7,
        "avg_daily_range_pct": 0.007,
        "optimal_hours": ["22:00-05:00", "13:00-17:00"],
        "spread_typical": 0.00022,
        "spread_pct": 0.000355,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.05,
        "risk_level": "medium",
        "liquidity": "medium",
    },

    # ==================== COMMODITIES (ENERGÍA) ====================
    "OIL_CRUDE": {
        "category": "commodities_energy",
        "volatility": "high",
        "avg_daily_range": 3.5,
        "avg_daily_range_pct": 0.035,
        "optimal_hours": ["13:00-20:00", "14:30-18:30"],
        "spread_typical": 0.03,
        "spread_pct": 0.0004,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.8,
        "risk_level": "high",
        "liquidity": "high",
    },

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
    "SILVER": {
        "category": "metals_precious",
        "volatility": "medium",
        "avg_daily_range": 1.8,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.08,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "US500": {
        "category": "indices_us",
        "volatility": "medium",
        "avg_daily_range": 1.2,
        "optimal_hours": ["15:00-20:30"],
        "spread_typical": 0.1,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "DE40": {
        "category": "indices_europe",
        "volatility": "medium",
        "avg_daily_range": 1.0,
        "optimal_hours": ["08:30-16:00"],
        "spread_typical": 1.0,
        "min_confidence_adjustment": 1,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "UK100": {
        "category": "indices_europe",
        "volatility": "medium",
        "avg_daily_range": 1.2,
        "optimal_hours": ["08:30-16:00"],
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
        "optimal_hours": ["08:30-16:00"],
        "spread_typical": 0.2,
        "min_confidence_adjustment": 1,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "J225": {
        "category": "indices_asia",
        "volatility": "medium",
        "avg_daily_range": 1.7,
        "optimal_hours": ["00:30-02:20", "03:40-05:30"],
        "spread_typical": 2.5,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "medium",
    },
    "HK50": {
        "category": "indices_asia",
        "volatility": "high",
        "avg_daily_range": 2.0,
        "optimal_hours": ["02:00-03:45", "05:05-07:30"],
        "spread_typical": 2.0,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "medium",
    }
}

# Alias para compatibilidad: usar siempre la versión CORE
SYMBOL_SPECIFIC_CONFIG = SYMBOL_SPECIFIC_CONFIG_CORE

# Símbolos por sesión de mercado óptima
MARKET_SESSION_SYMBOLS = {
    "asian": [
        "J225",
        "HK50",
        "AU200",
        # Forex actividad asiática
        "USDJPY",
        "AUDUSD",
        "NZDUSD",
    ],
    "european": [
        "DE40",
        "UK100",
        "FR40",
        # Forex actividad europea
        "EURUSD",
        "GBPUSD",
        "USDCHF",
    ],
    "american": [
        "US100",
        "US500",
        "US30",
        "RTY",
        # Forex actividad americana y commodities energía
        "USDCAD",
        "EURUSD",
        "OIL_CRUDE",
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
    "medium": [
        # Índices
        "US500", "US30", "UK100", "DE40", "FR40", "J225", "AU200",
        # Forex majors
        "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCHF", "USDCAD", "NZDUSD",
        # Metales
        "GOLD", "SILVER",
    ],
    "high": [
        "US100", "HK50", "RTY",
        # Commodities energía
        "OIL_CRUDE",
    ],
    "very_high": [],
}

LIQUIDITY_CATEGORIES = {
    "very_high": ["US100", "US500", "US30", "EURUSD", "USDJPY", "GBPUSD"],
    "high": ["UK100", "DE40", "FR40", "RTY"],
    "medium": ["J225", "HK50", "AU200", "USDCAD", "USDCHF", "AUDUSD"],
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
