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

# Criptomonedas principales - Máxima liquidez y estabilidad relativa
CRYPTO_MAJOR = [
    "BTCUSD",  # Bitcoin - Líder del mercado, máxima liquidez
    "ETHUSD",  # Ethereum - Smart contracts, DeFi líder
    "BNBUSD",  # Binance Coin - Exchange token líder
    "XRPUSD",  # Ripple - Pagos institucionales
    "ADAUSD",  # Cardano - Blockchain académica
    "SOLUSD",  # Solana - High performance blockchain
]

# Criptomonedas de alta capitalización - Buena liquidez, mayor volatilidad
CRYPTO_LARGE_CAP = [
    "DOTUSD",  # Polkadot - Interoperabilidad blockchain
    "AVAXUSD",  # Avalanche - Competidor de Ethereum
    "MATICUSD",  # Polygon - Scaling solution para Ethereum
    "LINKUSD",  # Chainlink - Oracle network líder
    "UNIUSD",  # Uniswap - DEX líder
    "LTCUSD",  # Litecoin - Silver to Bitcoin's gold
]

# Criptomonedas emergentes - Alta volatilidad, oportunidades de crecimiento
CRYPTO_EMERGING = [
    "ATOMUSD",  # Cosmos - Internet of blockchains
    "ALGOUSD",  # Algorand - Pure proof-of-stake
    "VETUSD",  # VeChain - Supply chain blockchain
    "FILUSD",  # Filecoin - Decentralized storage
    "SANDUSD",  # The Sandbox - Gaming metaverse
    "MANAUSD",  # Decentraland - Virtual reality platform
]

# ============================================================================
# 💱 FOREX - PARES DE DIVISAS PRINCIPALES Y EXÓTICOS
# ============================================================================

# Pares mayores - Máxima liquidez, spreads bajos
FOREX_MAJOR = [
    "EURUSD",  # Euro/Dólar - Par más líquido del mundo
    "GBPUSD",  # Libra/Dólar - Cable, alta volatilidad
    "USDJPY",  # Dólar/Yen - Par asiático principal
    "USDCHF",  # Dólar/Franco - Safe haven pair
    "AUDUSD",  # Dólar Australiano - Commodity currency
    "USDCAD",  # Dólar Canadiense - Petro currency
    "NZDUSD",  # Dólar Neozelandés - Risk-on currency
]

# Pares menores - Buena liquidez, mayor volatilidad
FOREX_MINOR = [
    "EURGBP",  # Euro/Libra - European cross
    "EURJPY",  # Euro/Yen - Carry trade popular
    "GBPJPY",  # Libra/Yen - Muy volátil
    "EURCHF",  # Euro/Franco - Low volatility
    "AUDCAD",  # Dólar Australiano/Canadiense
    "AUDNZD",  # Dólar Australiano/Neozelandés
]

# Pares exóticos - Alta volatilidad, spreads más amplios
FOREX_EXOTIC = [
    "USDZAR",  # Dólar/Rand Sudafricano
    "USDTRY",  # Dólar/Lira Turca - Muy volátil
    "USDSEK",  # Dólar/Corona Sueca
    "USDNOK",  # Dólar/Corona Noruega
    "USDPLN",  # Dólar/Zloty Polaco
    "USDHUF",  # Dólar/Forint Húngaro
]

# ============================================================================
# 🥇 COMMODITIES - MATERIAS PRIMAS Y METALES PRECIOSOS
# ============================================================================

# Metales preciosos - Safe haven assets
METALS_PRECIOUS = [
    "GOLD",  # Oro - Rey de los metales preciosos
    "SILVER",  # Plata - Más volátil que el oro
    "PLATINUM",  # Platino - Metal industrial y joyería
    "PALLADIUM",  # Paladio - Demanda automotriz
]

# Energía - Commodities energéticos
ENERGY_COMMODITIES = [
    "OIL_CRUDE",  # Petróleo crudo - WTI
    "OIL_BRENT",  # Petróleo Brent - Benchmark europeo
    "NATURALGAS",  # Gas natural - Energía limpia
    "GASOLINE",  # Gasolina - Derivado del petróleo
]

# Agricultura - Soft commodities
AGRICULTURAL = [
    "WHEAT",  # Trigo - Commodity alimentario básico
    "CORN",  # Maíz - Grano más comercializado
    "SOYBEAN",  # Soja - Proteína vegetal
    "SB",  # Azúcar - Commodity dulce
    "LRC",  # Café - Bebida global
    "USCOTTON",  # Algodón - Fibra textil
]

# Metales industriales
METALS_INDUSTRIAL = [
    "COPPER",  # Cobre - Barómetro económico
    "ALUMINUM",  # Aluminio - Metal ligero
    "MZN3",  # Zinc - Galvanización
    "NICKEL",  # Níquel - Baterías y acero inoxidable
]

# ============================================================================
# 📊 ÍNDICES - REPRESENTAN MERCADOS Y SECTORES
# ============================================================================

# Índices americanos
INDICES_US = [
    "US500",  # S&P 500 - Mercado americano amplio
    "US30",  # Dow Jones - Blue chips americanas
    "US100",  # Nasdaq 100 - Tecnología americana
]

# Índices europeos
INDICES_EUROPE = [
    "DE40",  # DAX - Alemania
    "UK100",  # FTSE 100 - Reino Unido
    "FR40",  # CAC 40 - Francia
    "IT40",  # FTSE MIB - Italia
    "EU50",  # Euro Stoxx 50 - Eurozona
]

# Índices asiáticos
INDICES_ASIA = [
    "J225",  # Nikkei 225 - Japón
    "HK50",  # Hang Seng - Hong Kong
    "AU200",  # ASX 200 - Australia
    "SG25",  # STI - Singapur
]

# ============================================================================
# 🎯 CONFIGURACIÓN GLOBAL OPTIMIZADA
# ============================================================================

# Lista principal de símbolos - Balanceada para máxima diversificación
GLOBAL_SYMBOLS = (
    # Criptomonedas (40% del portfolio de símbolos)
    CRYPTO_MAJOR  # 6 símbolos - Core crypto
    + CRYPTO_LARGE_CAP[:4]  # 4 símbolos - Growth crypto
    + CRYPTO_EMERGING[:2]  # 2 símbolos - High risk/reward
    +
    # Forex (30% del portfolio de símbolos)
    FOREX_MAJOR  # 7 símbolos - Major pairs
    + FOREX_MINOR[:3]  # 3 símbolos - Cross pairs
    + FOREX_EXOTIC[:2]  # 2 símbolos - High volatility
    +
    # Commodities (20% del portfolio de símbolos)
    METALS_PRECIOUS  # 4 símbolos - Safe haven
    + ENERGY_COMMODITIES[:2]  # 2 símbolos - Energy
    + AGRICULTURAL[:2]  # 2 símbolos - Soft commodities
    + METALS_INDUSTRIAL[:2]  # 2 símbolos - Industrial
    +
    # Índices (10% del portfolio de símbolos)
    INDICES_US  # 4 símbolos - US markets
    + INDICES_EUROPE[:2]  # 2 símbolos - European markets
    + INDICES_ASIA[:2]  # 2 símbolos - Asian markets
)

# ============================================================================
# ⚙️ CONFIGURACIÓN ESPECÍFICA POR SÍMBOLO
# ============================================================================

# Configuración detallada para optimizar trading por símbolo
SYMBOL_SPECIFIC_CONFIG = {
    # === CRIPTOMONEDAS PRINCIPALES ===
    "BTCUSD": {
        "category": "crypto_major",
        "volatility": "medium",
        "avg_daily_range": 3.5,  # % promedio diario
        "optimal_hours": ["00:00-23:59"],  # 24/7
        "spread_typical": 0.01,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "ETHUSD": {
        "category": "crypto_major",
        "volatility": "high",
        "avg_daily_range": 4.2,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.02,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "BNBUSD": {
        "category": "crypto_major",
        "volatility": "high",
        "avg_daily_range": 4.8,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.03,
        "min_confidence_adjustment": -3,
        "max_trades_multiplier": 1.2,
        "risk_level": "medium_high",
        "liquidity": "high",
    },
    "ADAUSD": {
        "category": "crypto_major",
        "volatility": "high",
        "avg_daily_range": 5.1,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.04,
        "min_confidence_adjustment": -3,
        "max_trades_multiplier": 1.3,
        "risk_level": "medium_high",
        "liquidity": "high",
    },
    "SOLUSD": {
        "category": "crypto_major",
        "volatility": "very_high",
        "avg_daily_range": 6.2,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.05,
        "min_confidence_adjustment": -5,
        "max_trades_multiplier": 1.4,
        "risk_level": "high",
        "liquidity": "high",
    },
    # === FOREX PRINCIPALES ===
    "EURUSD": {
        "category": "forex_major",
        "volatility": "low",
        "avg_daily_range": 0.8,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],  # London + NY overlap
        "spread_typical": 0.0001,
        "min_confidence_adjustment": 5,
        "max_trades_multiplier": 0.8,
        "risk_level": "low",
        "liquidity": "very_high",
    },
    "GBPUSD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 1.2,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.0002,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "USDJPY": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 1.0,
        "optimal_hours": ["00:00-09:00", "13:00-22:00"],  # Tokyo + NY
        "spread_typical": 0.001,
        "min_confidence_adjustment": 3,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    # === METALES PRECIOSOS ===
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
        "volatility": "high",
        "avg_daily_range": 2.8,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.08,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium_high",
        "liquidity": "high",
    },
    # === ÍNDICES PRINCIPALES ===
    "US500": {
        "category": "indices_us",
        "volatility": "medium",
        "avg_daily_range": 1.2,
        "optimal_hours": ["14:30-21:00"],  # US market hours
        "spread_typical": 0.1,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "NAS100": {
        "category": "indices_us",
        "volatility": "high",
        "avg_daily_range": 2.1,
        "optimal_hours": ["14:30-21:00"],
        "spread_typical": 0.2,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "very_high",
    },
    # === COMMODITIES ENERGÉTICOS ===
    "OIL": {
        "category": "energy",
        "volatility": "high",
        "avg_daily_range": 3.2,
        "optimal_hours": ["14:30-21:00", "08:00-17:00"],
        "spread_typical": 0.03,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.1,
        "risk_level": "high",
        "liquidity": "high",
    },
}

# ============================================================================
# 📊 CATEGORÍAS DE VOLATILIDAD PARA FILTRADO DINÁMICO
# ============================================================================

# Símbolos por nivel de volatilidad
VOLATILITY_CATEGORIES = {
    "very_low": [],  # Volatilidad < 0.5% diaria
    "low": ["EURUSD", "USDCHF", "EURCHF"],  # 0.5% - 1.0%
    "medium": ["BTCUSD", "GBPUSD", "USDJPY", "GOLD", "US500"],  # 1.0% - 2.0%
    "high": ["ETHUSD", "BNBUSD", "ADAUSD", "SILVER", "NAS100", "OIL"],  # 2.0% - 4.0%
    "very_high": ["SOLUSD", "DOTUSD", "AVAXUSD", "USDTRY"],  # > 4.0%
}

# Símbolos por nivel de liquidez
LIQUIDITY_CATEGORIES = {
    "very_high": ["BTCUSD", "ETHUSD", "EURUSD", "GBPUSD", "USDJPY", "GOLD", "US500"],
    "high": ["BNBUSD", "ADAUSD", "SOLUSD", "SILVER", "NAS100", "OIL"],
    "medium": ["DOTUSD", "AVAXUSD", "MATICUSD", "PLATINUM", "GER40"],
    "low": ["ATOMUSD", "ALGOUSD", "COPPER", "WHEAT"],
}

# Símbolos por sesión de mercado óptima
MARKET_SESSION_SYMBOLS = {
    "asian": ["USDJPY", "AUDUSD", "NZDUSD", "JPN225", "HK50", "AUS200"],
    "european": ["EURUSD", "GBPUSD", "EURGBP", "GOLD", "SILVER", "GER40", "UK100"],
    "american": ["US500", "NAS100", "US30", "OIL", "COPPER"],
    "crypto_24_7": CRYPTO_MAJOR + CRYPTO_LARGE_CAP + CRYPTO_EMERGING,
}

# ============================================================================
# 🎯 FUNCIONES AUXILIARES PARA CONFIGURACIÓN DINÁMICA
# ============================================================================


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

    return SYMBOL_SPECIFIC_CONFIG.get(symbol, default_config)


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

    current_hour = datetime.now().hour

    # Lógica simplificada por sesiones
    if 0 <= current_hour < 8:  # Sesión asiática
        return get_symbols_by_session("asian") + get_symbols_by_session("crypto_24_7")
    elif 8 <= current_hour < 16:  # Sesión europea
        return get_symbols_by_session("european") + get_symbols_by_session(
            "crypto_24_7"
        )
    else:  # Sesión americana
        return get_symbols_by_session("american") + get_symbols_by_session(
            "crypto_24_7"
        )


# ============================================================================
# 📈 CONFIGURACIÓN DE PORTFOLIO BALANCEADO
# ============================================================================

# Portfolio conservador - Baja volatilidad, alta liquidez
CONSERVATIVE_PORTFOLIO = (
    get_symbols_by_volatility("low")
    + get_symbols_by_volatility("medium")[:3]
    + ["BTCUSD", "ETHUSD"]  # Core crypto
)

# Portfolio agresivo - Alta volatilidad, mayores oportunidades
AGGRESSIVE_PORTFOLIO = (
    get_symbols_by_volatility("high")
    + get_symbols_by_volatility("very_high")
    + CRYPTO_EMERGING[:4]
)

# Portfolio balanceado - Mix óptimo de riesgo/recompensa
BALANCED_PORTFOLIO = GLOBAL_SYMBOLS  # Ya está balanceado
