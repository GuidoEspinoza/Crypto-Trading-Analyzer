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
    "AUDUSD",  # Dólar Australiano - Commodity currency
    "USDCAD",  # Dólar Canadiense - Petro currency
    "NZDUSD",  # Dólar Neozelandés - Risk-on currency
]

# Pares menores - Buena liquidez, mayor volatilidad
FOREX_MINOR = [
    # "EURJPY",  # Euro/Yen - Carry trade popular (comentado por pérdidas)
    "GBPJPY",  # Libra/Yen - Muy volátil
    "EURCHF",  # Euro/Franco - Low volatility
    "AUDCAD",  # Dólar Australiano/Canadiense
    "AUDNZD",  # Dólar Australiano/Neozelandés
]

# Pares exóticos - Alta volatilidad, spreads más amplios
FOREX_EXOTIC = [
    # "USDZAR",  # Dólar/Rand Sudafricano (comentado por pérdidas)
    # "USDTRY",  # Dólar/Lira Turca - Muy volátil (comentado por pérdidas)
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
    # "OIL_CRUDE",  # Petróleo crudo - WTI (comentado por pérdidas)
    "OIL_BRENT",  # Petróleo Brent - Benchmark europeo
    "NATURALGAS",  # Gas natural - Energía limpia
    "GASOLINE",  # Gasolina - Derivado del petróleo
]

# Agricultura - Soft commodities
AGRICULTURAL = [
    # "WHEAT",  # Trigo - Commodity alimentario básico (comentado por pérdidas)
    # "CORN",  # Maíz - Grano más comercializado (comentado por pérdidas)
    "SOYBEAN",  # Soja - Proteína vegetal
    "SB",  # Azúcar - Commodity dulce
    "LRC",  # Café - Bebida global
    "USCOTTON",  # Algodón - Fibra textil
]

# Metales industriales
METALS_INDUSTRIAL = [
    # "COPPER",  # Cobre - Barómetro económico (comentado por pérdidas)
    # "ALUMINUM",  # Aluminio - Metal ligero (comentado por pérdidas)
    "MZN3",  # Zinc - Galvanización
    "NICKEL",  # Níquel - Baterías y acero inoxidable
]

# ============================================================================
# 📊 ÍNDICES - REPRESENTAN MERCADOS Y SECTORES
# ============================================================================

# Índices americanos
INDICES_US = [
    "US500",  # S&P 500 - Mercado americano amplio
    # "US30",  # Dow Jones - Blue chips americanas (comentado por pérdidas)
    "US100",  # Nasdaq 100 - Tecnología americana
]

# Índices europeos
INDICES_EUROPE = [
    "DE40",  # DAX - Alemania
    # "UK100",  # FTSE 100 - Reino Unido (comentado por pérdidas)
    "FR40",  # CAC 40 - Francia
    "IT40",  # FTSE MIB - Italia
    "EU50",  # Euro Stoxx 50 - Eurozona
]

# Índices asiáticos
INDICES_ASIA = [
    "J225",  # Nikkei 225 - Japón
    # "HK50",  # Hang Seng - Hong Kong (comentado por pérdidas)
    "AU200",  # ASX 200 - Australia
    "SG25",  # STI - Singapur
]

# ============================================================================
# 🎯 CONFIGURACIÓN GLOBAL OPTIMIZADA
# ============================================================================

# Lista principal de símbolos - Balanceada para máxima diversificación
GLOBAL_SYMBOLS = (
    # Criptomonedas (eliminadas temporalmente por rendimiento)
    # CRYPTO_MAJOR  # 6 símbolos - Core crypto
    # + CRYPTO_LARGE_CAP[:4]  # 4 símbolos - Growth crypto
    # + CRYPTO_EMERGING[:2]  # 2 símbolos - High risk/reward
    # +
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
    "OIL_BRENT": {
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
    
    # === CRIPTOMONEDAS ADICIONALES ===
    "XRPUSD": {
        "category": "crypto_major",
        "volatility": "high",
        "avg_daily_range": 5.8,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.0001,
        "min_confidence_adjustment": -3,
        "max_trades_multiplier": 1.2,
        "risk_level": "medium_high",
        "liquidity": "very_high",
    },
    "DOTUSD": {
        "category": "crypto_large_cap",
        "volatility": "very_high",
        "avg_daily_range": 7.2,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.001,
        "min_confidence_adjustment": -5,
        "max_trades_multiplier": 1.4,
        "risk_level": "high",
        "liquidity": "high",
    },
    "AVAXUSD": {
        "category": "crypto_large_cap",
        "volatility": "very_high",
        "avg_daily_range": 8.1,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.002,
        "min_confidence_adjustment": -6,
        "max_trades_multiplier": 1.5,
        "risk_level": "high",
        "liquidity": "medium",
    },
    "MATICUSD": {
        "category": "crypto_large_cap",
        "volatility": "very_high",
        "avg_daily_range": 9.3,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.0001,
        "min_confidence_adjustment": -7,
        "max_trades_multiplier": 1.6,
        "risk_level": "high",
        "liquidity": "medium",
    },
    "LINKUSD": {
        "category": "crypto_large_cap",
        "volatility": "very_high",
        "avg_daily_range": 8.7,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.001,
        "min_confidence_adjustment": -6,
        "max_trades_multiplier": 1.5,
        "risk_level": "high",
        "liquidity": "medium",
    },
    "ATOMUSD": {
        "category": "crypto_emerging",
        "volatility": "very_high",
        "avg_daily_range": 10.2,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.002,
        "min_confidence_adjustment": -8,
        "max_trades_multiplier": 1.7,
        "risk_level": "very_high",
        "liquidity": "low",
    },
    "ALGOUSD": {
        "category": "crypto_emerging",
        "volatility": "very_high",
        "avg_daily_range": 11.5,
        "optimal_hours": ["00:00-23:59"],
        "spread_typical": 0.0001,
        "min_confidence_adjustment": -9,
        "max_trades_multiplier": 1.8,
        "risk_level": "very_high",
        "liquidity": "low",
    },
    
    # === FOREX ADICIONALES ===
    "USDCHF": {
        "category": "forex_major",
        "volatility": "low",
        "avg_daily_range": 0.7,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.0002,
        "min_confidence_adjustment": 5,
        "max_trades_multiplier": 0.8,
        "risk_level": "low",
        "liquidity": "very_high",
    },
    "AUDUSD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 1.1,
        "optimal_hours": ["22:00-08:00", "13:00-22:00"],
        "spread_typical": 0.0002,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "USDCAD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 1.0,
        "optimal_hours": ["13:00-22:00"],
        "spread_typical": 0.0003,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "NZDUSD": {
        "category": "forex_major",
        "volatility": "medium",
        "avg_daily_range": 1.3,
        "optimal_hours": ["22:00-08:00"],
        "spread_typical": 0.0003,
        "min_confidence_adjustment": 1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "EURGBP": {
        "category": "forex_minor",
        "volatility": "low",
        "avg_daily_range": 0.6,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.0003,
        "min_confidence_adjustment": 4,
        "max_trades_multiplier": 0.8,
        "risk_level": "low",
        "liquidity": "high",
    },
    "EURJPY": {
        "category": "forex_minor",
        "volatility": "medium",
        "avg_daily_range": 1.1,
        "optimal_hours": ["08:00-17:00", "00:00-09:00"],
        "spread_typical": 0.002,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
    },
    "GBPJPY": {
        "category": "forex_minor",
        "volatility": "high",
        "avg_daily_range": 1.8,
        "optimal_hours": ["08:00-17:00", "00:00-09:00"],
        "spread_typical": 0.003,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium_high",
        "liquidity": "medium",
    },
    "USDZAR": {
        "category": "forex_exotic",
        "volatility": "very_high",
        "avg_daily_range": 2.8,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.01,
        "min_confidence_adjustment": -5,
        "max_trades_multiplier": 1.3,
        "risk_level": "high",
        "liquidity": "low",
    },
    "USDTRY": {
        "category": "forex_exotic",
        "volatility": "very_high",
        "avg_daily_range": 3.5,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.02,
        "min_confidence_adjustment": -7,
        "max_trades_multiplier": 1.4,
        "risk_level": "very_high",
        "liquidity": "low",
    },
    
    # === METALES PRECIOSOS ADICIONALES ===
    "PLATINUM": {
        "category": "metals_precious",
        "volatility": "high",
        "avg_daily_range": 2.2,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.15,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium_high",
        "liquidity": "medium",
    },
    "PALLADIUM": {
        "category": "metals_precious",
        "volatility": "very_high",
        "avg_daily_range": 3.8,
        "optimal_hours": ["08:00-17:00", "13:00-22:00"],
        "spread_typical": 0.25,
        "min_confidence_adjustment": -4,
        "max_trades_multiplier": 1.2,
        "risk_level": "high",
        "liquidity": "low",
    },
    
    # === ENERGÍA ADICIONAL ===
    "OIL_CRUDE": {
        "category": "energy",
        "volatility": "high",
        "avg_daily_range": 3.5,
        "optimal_hours": ["14:30-21:00", "08:00-17:00"],
        "spread_typical": 0.03,
        "min_confidence_adjustment": -3,
        "max_trades_multiplier": 1.2,
        "risk_level": "high",
        "liquidity": "very_high",
    },
    "OIL_BRENT": {
        "category": "energy",
        "volatility": "high",
        "avg_daily_range": 3.2,
        "optimal_hours": ["08:00-17:00", "14:30-21:00"],
        "spread_typical": 0.03,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.1,
        "risk_level": "high",
        "liquidity": "high",
    },
    
    # === AGRICULTURA ===
    "WHEAT": {
        "category": "agricultural",
        "volatility": "high",
        "avg_daily_range": 2.8,
        "optimal_hours": ["14:30-21:00"],
        "spread_typical": 0.05,
        "min_confidence_adjustment": -2,
        "max_trades_multiplier": 1.1,
        "risk_level": "medium_high",
        "liquidity": "medium",
    },
    "CORN": {
        "category": "agricultural",
        "volatility": "high",
        "avg_daily_range": 2.5,
        "optimal_hours": ["14:30-21:00"],
        "spread_typical": 0.04,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "medium",
    },
    
    # === METALES INDUSTRIALES ===
    "COPPER": {
        "category": "metals_industrial",
        "volatility": "high",
        "avg_daily_range": 2.1,
        "optimal_hours": ["08:00-17:00", "14:30-21:00"],
        "spread_typical": 0.0001,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "high",
    },
    "ALUMINUM": {
        "category": "metals_industrial",
        "volatility": "medium",
        "avg_daily_range": 1.8,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.5,
        "min_confidence_adjustment": 0,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "medium",
    },
    
    # === ÍNDICES ADICIONALES ===
    "US30": {
        "category": "indices_us",
        "volatility": "medium",
        "avg_daily_range": 1.1,
        "optimal_hours": ["14:30-21:00"],
        "spread_typical": 0.5,
        "min_confidence_adjustment": 2,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "very_high",
    },
    "US100": {
        "category": "indices_us",
        "volatility": "high",
        "avg_daily_range": 2.3,
        "optimal_hours": ["14:30-21:00"],
        "spread_typical": 0.3,
        "min_confidence_adjustment": -1,
        "max_trades_multiplier": 1.0,
        "risk_level": "medium_high",
        "liquidity": "very_high",
    },
    "DE40": {
        "category": "indices_europe",
        "volatility": "medium",
        "avg_daily_range": 1.4,
        "optimal_hours": ["08:00-17:00"],
        "spread_typical": 0.2,
        "min_confidence_adjustment": 1,
        "max_trades_multiplier": 0.9,
        "risk_level": "medium",
        "liquidity": "high",
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
    "J225": {
        "category": "indices_asia",
        "volatility": "medium",
        "avg_daily_range": 1.6,
        "optimal_hours": ["00:00-08:00"],
        "spread_typical": 1.0,
        "min_confidence_adjustment": 0,
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
     
     # === SÍMBOLOS RESTANTES DE GLOBAL_SYMBOLS ===
     "UNIUSD": {
         "category": "crypto_large_cap",
         "volatility": "very_high",
         "avg_daily_range": 8.5,
         "optimal_hours": ["00:00-23:59"],
         "spread_typical": 0.002,
         "min_confidence_adjustment": -6,
         "max_trades_multiplier": 1.5,
         "risk_level": "high",
         "liquidity": "medium",
     },
     "LTCUSD": {
         "category": "crypto_large_cap",
         "volatility": "high",
         "avg_daily_range": 4.8,
         "optimal_hours": ["00:00-23:59"],
         "spread_typical": 0.01,
         "min_confidence_adjustment": -3,
         "max_trades_multiplier": 1.2,
         "risk_level": "medium_high",
         "liquidity": "high",
     },
     "VETUSD": {
         "category": "crypto_emerging",
         "volatility": "very_high",
         "avg_daily_range": 12.1,
         "optimal_hours": ["00:00-23:59"],
         "spread_typical": 0.00001,
         "min_confidence_adjustment": -10,
         "max_trades_multiplier": 1.9,
         "risk_level": "very_high",
         "liquidity": "low",
     },
     "FILUSD": {
         "category": "crypto_emerging",
         "volatility": "very_high",
         "avg_daily_range": 11.8,
         "optimal_hours": ["00:00-23:59"],
         "spread_typical": 0.002,
         "min_confidence_adjustment": -9,
         "max_trades_multiplier": 1.8,
         "risk_level": "very_high",
         "liquidity": "low",
     },
     "SANDUSD": {
         "category": "crypto_emerging",
         "volatility": "very_high",
         "avg_daily_range": 13.5,
         "optimal_hours": ["00:00-23:59"],
         "spread_typical": 0.0001,
         "min_confidence_adjustment": -12,
         "max_trades_multiplier": 2.0,
         "risk_level": "very_high",
         "liquidity": "low",
     },
     "MANAUSD": {
         "category": "crypto_emerging",
         "volatility": "very_high",
         "avg_daily_range": 14.2,
         "optimal_hours": ["00:00-23:59"],
         "spread_typical": 0.0001,
         "min_confidence_adjustment": -13,
         "max_trades_multiplier": 2.1,
         "risk_level": "very_high",
         "liquidity": "low",
     },
     "EURCHF": {
         "category": "forex_minor",
         "volatility": "very_low",
         "avg_daily_range": 0.4,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.0004,
         "min_confidence_adjustment": 8,
         "max_trades_multiplier": 0.7,
         "risk_level": "very_low",
         "liquidity": "medium",
     },
     "AUDCAD": {
         "category": "forex_minor",
         "volatility": "medium",
         "avg_daily_range": 1.0,
         "optimal_hours": ["22:00-08:00", "13:00-22:00"],
         "spread_typical": 0.0004,
         "min_confidence_adjustment": 2,
         "max_trades_multiplier": 0.9,
         "risk_level": "medium",
         "liquidity": "medium",
     },
     "AUDNZD": {
         "category": "forex_minor",
         "volatility": "medium",
         "avg_daily_range": 1.2,
         "optimal_hours": ["22:00-08:00"],
         "spread_typical": 0.0005,
         "min_confidence_adjustment": 1,
         "max_trades_multiplier": 1.0,
         "risk_level": "medium",
         "liquidity": "medium",
     },
     "USDSEK": {
         "category": "forex_exotic",
         "volatility": "high",
         "avg_daily_range": 1.8,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.005,
         "min_confidence_adjustment": -2,
         "max_trades_multiplier": 1.1,
         "risk_level": "medium_high",
         "liquidity": "low",
     },
     "USDNOK": {
         "category": "forex_exotic",
         "volatility": "high",
         "avg_daily_range": 1.9,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.006,
         "min_confidence_adjustment": -2,
         "max_trades_multiplier": 1.1,
         "risk_level": "medium_high",
         "liquidity": "low",
     },
     "USDPLN": {
         "category": "forex_exotic",
         "volatility": "high",
         "avg_daily_range": 2.1,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.008,
         "min_confidence_adjustment": -3,
         "max_trades_multiplier": 1.2,
         "risk_level": "high",
         "liquidity": "low",
     },
     "USDHUF": {
         "category": "forex_exotic",
         "volatility": "high",
         "avg_daily_range": 2.3,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.01,
         "min_confidence_adjustment": -4,
         "max_trades_multiplier": 1.2,
         "risk_level": "high",
         "liquidity": "low",
     },
     "NATURALGAS": {
         "category": "energy",
         "volatility": "very_high",
         "avg_daily_range": 4.5,
         "optimal_hours": ["14:30-21:00"],
         "spread_typical": 0.005,
         "min_confidence_adjustment": -5,
         "max_trades_multiplier": 1.3,
         "risk_level": "high",
         "liquidity": "medium",
     },
     "GASOLINE": {
         "category": "energy",
         "volatility": "high",
         "avg_daily_range": 3.8,
         "optimal_hours": ["14:30-21:00"],
         "spread_typical": 0.0001,
         "min_confidence_adjustment": -3,
         "max_trades_multiplier": 1.2,
         "risk_level": "high",
         "liquidity": "medium",
     },
     "SOYBEAN": {
         "category": "agricultural",
         "volatility": "high",
         "avg_daily_range": 2.3,
         "optimal_hours": ["14:30-21:00"],
         "spread_typical": 0.03,
         "min_confidence_adjustment": -1,
         "max_trades_multiplier": 1.0,
         "risk_level": "medium_high",
         "liquidity": "medium",
     },
     "SB": {
         "category": "agricultural",
         "volatility": "high",
         "avg_daily_range": 3.1,
         "optimal_hours": ["14:30-21:00"],
         "spread_typical": 0.0001,
         "min_confidence_adjustment": -2,
         "max_trades_multiplier": 1.1,
         "risk_level": "medium_high",
         "liquidity": "low",
     },
     "LRC": {
         "category": "agricultural",
         "volatility": "high",
         "avg_daily_range": 2.9,
         "optimal_hours": ["14:30-21:00"],
         "spread_typical": 0.0005,
         "min_confidence_adjustment": -2,
         "max_trades_multiplier": 1.1,
         "risk_level": "medium_high",
         "liquidity": "medium",
     },
     "USCOTTON": {
         "category": "agricultural",
         "volatility": "high",
         "avg_daily_range": 2.7,
         "optimal_hours": ["14:30-21:00"],
         "spread_typical": 0.0001,
         "min_confidence_adjustment": -1,
         "max_trades_multiplier": 1.0,
         "risk_level": "medium_high",
         "liquidity": "low",
     },
     "MZN3": {
         "category": "metals_industrial",
         "volatility": "high",
         "avg_daily_range": 2.8,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.5,
         "min_confidence_adjustment": -2,
         "max_trades_multiplier": 1.1,
         "risk_level": "medium_high",
         "liquidity": "low",
     },
     "NICKEL": {
         "category": "metals_industrial",
         "volatility": "very_high",
         "avg_daily_range": 4.2,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 1.0,
         "min_confidence_adjustment": -4,
         "max_trades_multiplier": 1.3,
         "risk_level": "high",
         "liquidity": "low",
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
     "IT40": {
         "category": "indices_europe",
         "volatility": "medium",
         "avg_daily_range": 1.5,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.5,
         "min_confidence_adjustment": 0,
         "max_trades_multiplier": 0.9,
         "risk_level": "medium",
         "liquidity": "medium",
     },
     "EU50": {
         "category": "indices_europe",
         "volatility": "medium",
         "avg_daily_range": 1.2,
         "optimal_hours": ["08:00-17:00"],
         "spread_typical": 0.2,
         "min_confidence_adjustment": 1,
         "max_trades_multiplier": 0.9,
         "risk_level": "medium",
         "liquidity": "high",
     },
     "AU200": {
         "category": "indices_asia",
         "volatility": "medium",
         "avg_daily_range": 1.4,
         "optimal_hours": ["22:00-08:00"],
         "spread_typical": 0.5,
         "min_confidence_adjustment": 0,
         "max_trades_multiplier": 0.9,
         "risk_level": "medium",
         "liquidity": "medium",
     },
     "SG25": {
         "category": "indices_asia",
         "volatility": "medium",
         "avg_daily_range": 1.1,
         "optimal_hours": ["01:00-08:00"],
         "spread_typical": 1.0,
         "min_confidence_adjustment": 1,
         "max_trades_multiplier": 0.9,
         "risk_level": "medium",
         "liquidity": "low",
     },
}

# ============================================================================
# 📊 CATEGORÍAS DE VOLATILIDAD PARA FILTRADO DINÁMICO
# ============================================================================

# Símbolos por nivel de volatilidad
VOLATILITY_CATEGORIES = {
    "very_low": ["EURCHF"],  # Volatilidad < 0.5% diaria
    "low": ["EURUSD", "USDCHF", "EURGBP"],  # 0.5% - 1.0%
    "medium": [
        # Forex majors estables
        "GBPUSD", # "USDJPY", # Comentado por pérdidas
        "AUDUSD", "USDCAD", "NZDUSD",
        # Forex minors
        # "EURJPY", # Comentado por pérdidas
        "AUDCAD", "AUDNZD",
        # Metales preciosos
        "GOLD",
        # Índices estables
        "US500", # "US30", # Comentado por pérdidas
        "DE40", # "UK100", # Comentado por pérdidas
        "FR40", "IT40", "EU50", "J225", "AU200", "SG25",
        # Metales industriales
        # "ALUMINUM", # Comentado por pérdidas
        # Crypto major estable (eliminado temporalmente)
        # "BTCUSD"
    ],  # 1.0% - 2.0%
    "high": [
        # Forex exóticos
        "USDSEK", "USDNOK", "GBPJPY",
        # Metales preciosos volátiles
        "SILVER", "PLATINUM",
        # Energía
        # "OIL_CRUDE", # Comentado por pérdidas
        "OIL_BRENT", "GASOLINE",
        # Agricultura
        # "WHEAT", # Comentado por pérdidas
        # "CORN", # Comentado por pérdidas
        "SOYBEAN", "LRC", "USCOTTON",
        # Metales industriales
        # "COPPER", # Comentado por pérdidas
        "MZN3",
        # Índices volátiles
        "US100", # "HK50", # Comentado por pérdidas
        # Crypto majors (eliminados temporalmente)
        # "ETHUSD", "BNBUSD", "ADAUSD", "XRPUSD", "LTCUSD"
    ],  # 2.0% - 4.0%
    "very_high": [
        # Forex exóticos muy volátiles
        # "USDZAR", # Comentado por pérdidas
        # "USDTRY", # Comentado por pérdidas
        "USDPLN", "USDHUF",
        # Energía muy volátil
        "NATURALGAS",
        # Agricultura volátil
        "SB",
        # Metales industriales volátiles
        "NICKEL",
        # Metales preciosos muy volátiles
        "PALLADIUM",
        # Crypto large cap (eliminados temporalmente)
        # "SOLUSD", "DOTUSD", "AVAXUSD", "MATICUSD", "LINKUSD", "UNIUSD",
        # Crypto emerging (eliminados temporalmente)
        # "ATOMUSD", "ALGOUSD", "VETUSD", "FILUSD", "SANDUSD", "MANAUSD"
    ]  # > 4.0%
}

# Símbolos por nivel de liquidez
LIQUIDITY_CATEGORIES = {
    "very_high": [
        # Crypto majors con máxima liquidez (eliminados temporalmente)
        # "BTCUSD", "ETHUSD", "XRPUSD",
        # Forex majors
        "EURUSD", "GBPUSD", # "USDJPY", # Comentado por pérdidas
        "USDCHF", "AUDUSD",
        # Metales preciosos principales
        "GOLD",
        # Índices principales
        "US500", # "US30", # Comentado por pérdidas
        "US100",
        # Energía principal
        # "OIL_CRUDE" # Comentado por pérdidas
    ],
    "high": [
        # Crypto majors (eliminados temporalmente)
        # "BNBUSD", "ADAUSD", "SOLUSD", "LTCUSD",
        # Forex majors
        "USDCAD", "NZDUSD",
        # Forex minors principales
        # "EURJPY", # Comentado por pérdidas
        "EURGBP", "GBPJPY",
        # Metales preciosos
        "SILVER",
        # Índices europeos principales
        "DE40", # "UK100", # Comentado por pérdidas
        "FR40", "EU50",
        # Índices asiáticos principales
        "J225",
        # Energía
        "OIL_BRENT",
        # Metales industriales principales
        # "COPPER" # Comentado por pérdidas
    ],
    "medium": [
        # Crypto large cap (eliminados temporalmente)
        # "DOTUSD", "AVAXUSD", "MATICUSD", "LINKUSD", "UNIUSD",
        # Forex minors
        "AUDCAD", "AUDNZD", "EURCHF",
        # Metales preciosos
        "PLATINUM",
        # Índices secundarios
        "IT40", # "HK50", # Comentado por pérdidas
        "AU200",
        # Energía secundaria
        "NATURALGAS", "GASOLINE",
        # Agricultura principal
        # "WHEAT", # Comentado por pérdidas
        # "CORN", # Comentado por pérdidas
        "SOYBEAN", "LRC",
        # Metales industriales
        # "ALUMINUM" # Comentado por pérdidas
    ],
    "low": [
        # Crypto emerging (eliminados temporalmente)
        # "ATOMUSD", "ALGOUSD", "VETUSD", "FILUSD", "SANDUSD", "MANAUSD",
        # Forex exóticos
        # "USDZAR", # Comentado por pérdidas
        # "USDTRY", # Comentado por pérdidas
        "USDSEK", "USDNOK", "USDPLN", "USDHUF",
        # Metales preciosos especializados
        "PALLADIUM",
        # Índices menores
        "SG25",
        # Agricultura especializada
        "SB", "USCOTTON",
        # Metales industriales especializados
        "MZN3", "NICKEL"
    ]
}

# Símbolos por sesión de mercado óptima
MARKET_SESSION_SYMBOLS = {
    "asian": [
        # Forex con yen y monedas asiáticas/oceánicas
        # "USDJPY",  # Comentado temporalmente
        "AUDUSD", "NZDUSD", # "EURJPY", # Comentado por pérdidas
        "GBPJPY", "AUDCAD", "AUDNZD",
        # Índices asiáticos
        "J225", # "HK50",  # Comentado por pérdidas
        "AU200", "SG25"
    ],
    "european": [
        # Forex europeos
        "EURUSD", "GBPUSD", "USDCHF", "EURGBP", "EURCHF",
        # Forex exóticos europeos
        "USDSEK", "USDNOK", "USDPLN", "USDHUF",
        # Metales preciosos (Londres es centro principal)
        "GOLD", "SILVER", "PLATINUM", "PALLADIUM",
        # Metales industriales (LME en Londres)
        # "COPPER", # Comentado por pérdidas
        # "ALUMINUM", # Comentado por pérdidas
        "MZN3", "NICKEL",
        # Índices europeos
        "DE40", # "UK100", # Comentado por pérdidas
        "FR40", "IT40", "EU50"
    ],
    "american": [
        # Forex con USD como base en horario americano
        "USDCAD", # "USDZAR", # Comentado por pérdidas
        # "USDTRY", # Comentado por pérdidas
        # Índices americanos
        "US500", # "US30", # Comentado por pérdidas
        "US100",
        # Energía (mercados principales en NY)
        # "OIL_CRUDE", # Comentado por pérdidas
        "OIL_BRENT", "NATURALGAS", "GASOLINE",
        # Agricultura (Chicago/NY)
        # "WHEAT", # Comentado por pérdidas
        # "CORN", # Comentado por pérdidas
        "SOYBEAN", "SB", "LRC", "USCOTTON"
    ],
    # "crypto_24_7": [
    #     # Crypto majors
    #     "BTCUSD", "ETHUSD", "BNBUSD", "XRPUSD", "ADAUSD", "SOLUSD",
    #     # Crypto large cap
    #     "DOTUSD", "AVAXUSD", "MATICUSD", "LINKUSD", "UNIUSD", "LTCUSD",
    #     # Crypto emerging
    #     "ATOMUSD", "ALGOUSD", "VETUSD", "FILUSD", "SANDUSD", "MANAUSD"
    # ]
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
