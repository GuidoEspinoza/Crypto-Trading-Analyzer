"""Configuración centralizada para el sistema de trading.

Este archivo contiene todas las configuraciones principales del bot de trading,
con tres niveles de configuración disponibles:

🚀 RÁPIDA (Ultra-corta): Timeframes de 1m-15m, máxima frecuencia de trades, mayor riesgo
⚡ AGRESIVA: Timeframes de 15m-1h, balance entre velocidad y control de riesgo  
🛡️ ÓPTIMA (Conservadora): Timeframes de 1h-1d, enfoque en calidad y preservación de capital

Para cambiar entre configuraciones, simplemente comenta/descomenta las líneas correspondientes.
Cada parámetro incluye las tres opciones claramente marcadas.
"""

from typing import List, Dict, Any

# ============================================================================
# CONFIGURACIÓN DEL TRADING BOT PRINCIPAL
# ============================================================================

# Balance inicial global para todas las posiciones en USDT
GLOBAL_INITIAL_BALANCE = 500.0

class TradingBotConfig:
    """Configuración principal del bot de trading."""
    
    # Lista de símbolos a analizar - criptomonedas de alta volatilidad y liquidez para ganancias rápidas
    SYMBOLS: List[str] = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT",
        "ADAUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "ATOMUSDT",
        "NEARUSDT", "FTMUSDT", "SANDUSDT", "MANAUSDT", "GALAUSDT"
    ]

    # Símbolos a usar en el bot de trading en vivo (agregar [:X] para limitar cantidad)
    SYMBOLS_LIVE_BOT = SYMBOLS
    
    # Intervalo de análisis en minutos - tiempo entre análisis automáticos (rápido: 5 - agresivo: 15 - óptimo: 30)
    ANALYSIS_INTERVAL: int = 5 
    
    # Umbral mínimo de confianza para ejecutar trades en % (rápido: 60.0 - agresivo: 65.0 - óptimo: 70.0)
    MIN_CONFIDENCE_THRESHOLD: float = 60.0
    
    # Número máximo de trades por día - control de sobreoperación (rápido: 20 - agresivo: 12 - óptimo: 8)
    MAX_DAILY_TRADES: int = 20
    
    # Límite de posiciones concurrentes - diversificación controlada (rápido: 8 - agresivo: 6 - óptimo: 4)
    MAX_CONCURRENT_POSITIONS: int = 8
    
    # Timeframes para análisis profesional - marcos temporales (rápido: ["1m", "5m", "15m"] - agresivo: ["15m", "30m", "1h"] - óptimo: ["1h", "4h", "1d"])
    PROFESSIONAL_TIMEFRAMES: List[str] = ["1m", "5m", "15m"]  
    
    # Timeframe principal para análisis - marco temporal base (rápido: "1m" - agresivo: "15m" - óptimo: "1h")
    PRIMARY_TIMEFRAME: str = "1m"  
    
    # Valor por defecto del portfolio para cálculos cuando no hay datos
    DEFAULT_PORTFOLIO_VALUE: float = GLOBAL_INITIAL_BALANCE
    
    # Timeframe para confirmación - validación de señales (rápido: "5m" - agresivo: "30m" - óptimo: "4h")
    CONFIRMATION_TIMEFRAME: str = "5m"  
    
    # Timeframe para análisis de tendencia - dirección general (rápido: "15m" - agresivo: "1h" - óptimo: "1d")
    TREND_TIMEFRAME: str = "15m"  
    
    # Descripción del bot - identificación del perfil (óptimo: "Profesional")
    BOT_DESCRIPTION: str = "Profesional"
    
    # Configuración específica para Live Trading Bot
    # Intervalo de actualización en segundos para live bot (rápido: 10 - agresivo: 20 - óptimo: 30)
    LIVE_UPDATE_INTERVAL: int = 10  
    
    # Umbral mínimo de confianza para live trading (rápido: 60.0 - agresivo: 65.0 - óptimo: 70.0)
    LIVE_MIN_CONFIDENCE_THRESHOLD: float = 60.0  
    
    # Delay en segundos para el primer análisis al iniciar (rápido: 15 - agresivo: 30 - óptimo: 60)
    FIRST_ANALYSIS_DELAY: int = 15


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USDT para simulación
    INITIAL_BALANCE: float = GLOBAL_INITIAL_BALANCE
    
    # Tamaño máximo de posición como % del portfolio (rápido: 10.0 - agresivo: 8.0 - óptimo: 6.0)
    MAX_POSITION_SIZE: float = 10.0
    
    # Exposición total máxima del portfolio en % (rápido: 85.0 - agresivo: 75.0 - óptimo: 60.0)
    MAX_TOTAL_EXPOSURE: float = 85.0
    
    # Valor mínimo por trade en USDT (rápido: 15.0 - agresivo: 10.0 - óptimo: 5.0)
    MIN_TRADE_VALUE: float = 15.0
    
    # Umbral mínimo de confianza para ejecutar trades (rápido: 58.0 - agresivo: 62.0 - óptimo: 60.0)
    MIN_CONFIDENCE_THRESHOLD: float = 58.0
    
    # Slippage máximo permitido en % (rápido: 0.12 - agresivo: 0.08 - óptimo: 0.05)
    MAX_SLIPPAGE: float = 0.12  
    
    # Liquidez mínima requerida en % (rápido: 3.0 - agresivo: 5.0 - óptimo: 8.0)
    MIN_LIQUIDITY: float = 3.0  
    
    # Máximo % del balance disponible para trading (reserva para fees) (óptimo: 95.0)
    MAX_BALANCE_USAGE: float = 95.0


# ============================================================================
# CONFIGURACIÓN DEL GESTOR DE RIESGO
# ============================================================================

class RiskManagerConfig:
    """Configuración del gestor de riesgo avanzado."""
    
    # Riesgo máximo por trade como % del portfolio (rápido: 2.0 - agresivo: 1.5 - óptimo: 1.0)
    MAX_RISK_PER_TRADE: float = 2.0
    
    # Riesgo máximo diario como % del portfolio (rápido: 6.0 - agresivo: 4.5 - óptimo: 3.0)
    MAX_DAILY_RISK: float = 6.0
    
    # Umbral de drawdown máximo antes de parar trading en % (rápido: 12.0 - agresivo: 10.0 - óptimo: 8.0)
    MAX_DRAWDOWN_THRESHOLD: float = 12.0
    
    # Umbral de correlación máxima entre posiciones (rápido: 0.8 - agresivo: 0.6 - óptimo: 0.4)
    CORRELATION_THRESHOLD: float = 0.8
    
    # Tamaño mínimo de posición como % del portfolio (rápido: 0.008 - agresivo: 0.005 - óptimo: 0.003)
    MIN_POSITION_SIZE: float = 0.008
    
    # Tamaño máximo de posición como % del portfolio (rápido: 10.0 - agresivo: 8.0 - óptimo: 6.0)
    MAX_POSITION_SIZE: float = 10.0
    
    # Fracción Kelly conservadora para sizing (rápido: 0.25 - agresivo: 0.15 - óptimo: 0.10)
    KELLY_FRACTION: float = 0.25
    
    # Factor de ajuste por volatilidad del mercado (rápido: 0.6 - agresivo: 0.4 - óptimo: 0.2)
    VOLATILITY_ADJUSTMENT: float = 0.6
    
    # Multiplicador ATR mínimo para stop-loss dinámico (rápido: 1.5 - agresivo: 2.5 - óptimo: 3.0)
    ATR_MULTIPLIER_MIN: float = 1.5
    
    # Multiplicador ATR máximo para stop-loss dinámico (rápido: 3.0 - agresivo: 4.0 - óptimo: 5.0)
    ATR_MULTIPLIER_MAX: float = 3.0
    
    # Multiplicadores ATR por defecto para diferentes condiciones de mercado
    ATR_DEFAULT: float = 2.0  # Multiplicador por defecto
    ATR_VOLATILE: float = 3.0  # Para mercados volátiles
    ATR_SIDEWAYS: float = 1.5  # Para mercados laterales
    
    # Umbral de ganancia para activar trailing stop en % (rápido: 1.0 - agresivo: 1.5 - óptimo: 2.0)
    TRAILING_STOP_ACTIVATION: float = 1.0
    
    # Umbral para mover stop-loss a breakeven en % (rápido: 0.8 - agresivo: 1.0 - óptimo: 1.2)
    BREAKEVEN_THRESHOLD: float = 0.8
    
    # Valor inicial del portfolio para cálculos de riesgo en USDT - Se alimenta del PaperTrader para consistencia
    INITIAL_PORTFOLIO_VALUE: float = PaperTraderConfig.INITIAL_BALANCE  # Mantiene consistencia automática


# ============================================================================
# CONFIGURACIÓN DE ESTRATEGIAS DE TRADING
# ============================================================================

class StrategyConfig:
    """Configuración de las estrategias de trading."""
    
    # ---- Configuración Base de Estrategias ----
    class Base:
        """Parámetros base para todas las estrategias."""
        
        # Confianza mínima por defecto para estrategias base (rápido: 55.0 - agresivo: 60.0 - óptimo: 65.0)
        DEFAULT_MIN_CONFIDENCE: float = 55.0
        
        # Valores de confianza por defecto para diferentes señales
        HOLD_CONFIDENCE: float = 45.0
        BASE_CONFIDENCE: float = 50.0
        ENHANCED_CONFIDENCE: float = 60.0
        
        # Período ATR por defecto para cálculos de stop-loss (rápido: 10 - agresivo: 14 - óptimo: 20)
        DEFAULT_ATR_PERIOD: int = 10
    
    # ---- Estrategia RSI Profesional ----
    class ProfessionalRSI:
        """Parámetros para la estrategia RSI profesional."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Confianza mínima requerida en % (rápido: 65.0 - agresivo: 68.0 - óptimo: 72.0)
        MIN_CONFIDENCE: float = 65.0
        
        # Nivel de sobreventa del RSI - señal de compra (rápido: 35 - agresivo: 30 - óptimo: 25)
        RSI_OVERSOLD: int = 35
        
        # Nivel de sobrecompra del RSI - señal de venta (rápido: 65 - agresivo: 70 - óptimo: 75)
        RSI_OVERBOUGHT: int = 65
        
        # Período del RSI - ventana de cálculo (rápido: 10 - agresivo: 14 - óptimo: 21)
        RSI_PERIOD: int = 10
        
        # Ratio mínimo de volumen vs promedio (rápido: 1.2 - agresivo: 1.5 - óptimo: 1.8)
        MIN_VOLUME_RATIO: float = 1.2
        
        # Confluencia mínima de indicadores requerida (rápido: 2 - agresivo: 3 - óptimo: 4)
        MIN_CONFLUENCE: int = 2
        
        # Umbral de fuerza de tendencia ADX (rápido: 25 - agresivo: 30 - óptimo: 35)
        TREND_STRENGTH_THRESHOLD: float = 25
        
        # Ratio ATR mínimo para volatilidad (rápido: 0.8 - agresivo: 1.0 - óptimo: 1.2)
        MIN_ATR_RATIO: float = 0.8
        
        # Spread máximo permitido en % (rápido: 0.0025 - agresivo: 0.0015 - óptimo: 0.0010)
        MAX_SPREAD_THRESHOLD: float = 0.0025
    
    # ---- Estrategia Multi-Timeframe ----
    class MultiTimeframe:
        """Parámetros para la estrategia multi-timeframe."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Confianza mejorada para señales (rápido: 60.0 - agresivo: 65.0 - óptimo: 70.0)
        ENHANCED_CONFIDENCE: float = 60.0
        
        # Confianza mínima requerida en % (rápido: 62.0 - agresivo: 65.0 - óptimo: 70.0)
        MIN_CONFIDENCE: float = 62.0
        
        # Timeframes utilizados para análisis (rápido: ["1m", "5m", "15m"] - agresivo: ["15m", "30m", "1h"] - óptimo: ["1h", "4h", "1d"])
        TIMEFRAMES: List[str] = ["1m", "5m", "15m"]
        
        # Configuración RSI por timeframe - niveles de sobreventa/sobrecompra (rápido)
        RSI_CONFIG: Dict[str, Dict[str, int]] = {
            "1m": {"oversold": 40, "overbought": 60},   # Timeframe ultra-corto - muy sensible
            "5m": {"oversold": 35, "overbought": 65},   # Timeframe muy corto - sensible
            "15m": {"oversold": 30, "overbought": 70}   # Timeframe corto - rápido
        }
        

        
        # Pesos por timeframe - balance entre ultra-corto plazo (rápido: suma = 1.0)
        TIMEFRAME_WEIGHTS: Dict[str, float] = {
            "1m": 0.4,   # Peso principal para oportunidades inmediatas
            "5m": 0.4,   # Peso principal para decisiones ultra-rápidas
            "15m": 0.2   # Peso menor para confirmación rápida
        }
        

        
        # Consenso mínimo de timeframes requerido (rápido: 1 - agresivo: 2 - óptimo: 3)
        MIN_CONSENSUS: int = 1
        
        # Requiere alineación de tendencias entre timeframes (rápido: False - agresivo: True - óptimo: True)
        REQUIRE_TREND_ALIGNMENT: bool = False
        
        # Consenso mínimo de timeframes para señal válida (rápido: 1 - agresivo: 2 - óptimo: 3)
        MIN_TIMEFRAME_CONSENSUS: int = 1
        
        # Requiere alineación de tendencias entre timeframes (rápido: False - agresivo: True - óptimo: True)
        TREND_ALIGNMENT_REQUIRED: bool = False
    
    # ---- Estrategia Ensemble ----
    class Ensemble:
        """Parámetros para la estrategia ensemble (combinación de estrategias)."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Pesos de cada estrategia en el ensemble (óptimo: RSI=0.4, MultiTF=0.6)
        STRATEGY_WEIGHTS: Dict[str, float] = {
            "Professional_RSI": 0.4,
            "Multi_Timeframe": 0.6
        }
        
        # Umbral mínimo de consenso entre estrategias (rápido: 0.55 - agresivo: 0.6 - óptimo: 0.7)
        MIN_CONSENSUS_THRESHOLD: float = 0.55
        
        # Factor de boost de confianza cuando hay consenso (rápido: 1.25 - agresivo: 1.2 - óptimo: 1.15)
        CONFIDENCE_BOOST_FACTOR: float = 1.25


# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================

class DatabaseConfig:
    """Configuración de la base de datos."""
    
    # Nombre del archivo de base de datos SQLite (óptimo: "trading_data.db")
    DATABASE_NAME: str = "trading_data.db"
    
    # Días de retención de datos históricos (óptimo: 90)
    DATA_RETENTION_DAYS: int = 90
    
    # Intervalo de limpieza automática en horas (óptimo: 24)
    CLEANUP_INTERVAL_HOURS: int = 24


# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

class LoggingConfig:
    """Configuración del sistema de logging."""
    
    # Nivel de logging por defecto (óptimo: "INFO")
    LOG_LEVEL: str = "INFO"
    
    # Formato de logs con timestamp (óptimo: incluir timestamp y nivel)
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Archivo de logs (óptimo: "trading_bot.log")
    LOG_FILE: str = "trading_bot.log"
    
    # Tamaño máximo del archivo de log en MB (óptimo: 10)
    MAX_LOG_SIZE_MB: int = 10
    
    # Número de archivos de backup de logs (óptimo: 5)
    LOG_BACKUP_COUNT: int = 5


# ============================================================================
# CONFIGURACIÓN DE TRADING EN VIVO (LIVE TRADING)
# ============================================================================

class LiveTradingConfig:
    """Configuración específica para trading en vivo."""
    
    # Balance inicial real en USDT - Se alimenta automáticamente del PaperTrader para consistencia
    INITIAL_BALANCE: float = PaperTraderConfig.INITIAL_BALANCE  # Mantiene consistencia automática
    
    # Comisiones de Binance en % por trade (rápido: 0.1 - agresivo: 0.1 - óptimo: 0.075)
    TRADING_FEES: float = 0.1
    
    # Timeout para órdenes en segundos (rápido: 15 - agresivo: 30 - óptimo: 60)
    ORDER_TIMEOUT: int = 15
    
    # Reintentos máximos para órdenes fallidas (rápido: 2 - agresivo: 3 - óptimo: 5)
    MAX_ORDER_RETRIES: int = 2
    
    # Intervalo de verificación de órdenes en segundos (rápido: 2 - agresivo: 5 - óptimo: 10)
    ORDER_CHECK_INTERVAL: int = 2


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
        'bot': TradingBotConfig,
        'risk': RiskManagerConfig,
        'paper': PaperTraderConfig,
        'strategy': StrategyConfig,
        'db': DatabaseConfig,
        'log': LoggingConfig,
        'live': LiveTradingConfig,
        'testing': TestingConfig,
        'indicators': AdvancedIndicatorsConfig
    }
    
    if config_type not in configs:
        raise ValueError(f"Tipo de configuración '{config_type}' no válido. Opciones: {list(configs.keys())}")
    
    return configs[config_type]


# ============================================================================
# CONFIGURACIÓN DE INDICADORES AVANZADOS
# ============================================================================

class AdvancedIndicatorsConfig:
    """Configuración de períodos y umbrales para indicadores técnicos avanzados."""
    
    # Períodos para Ichimoku Cloud
    ICHIMOKU_TENKAN_PERIOD: int = 9   # Tenkan-sen (línea de conversión)
    ICHIMOKU_KIJUN_PERIOD: int = 26   # Kijun-sen (línea base)
    ICHIMOKU_SENKOU_PERIOD: int = 52  # Senkou Span A
    ICHIMOKU_SENKOU_B_PERIOD: int = 52  # Senkou Span B
    ICHIMOKU_SHIFT: int = 26          # Desplazamiento para proyección
    
    # Períodos para osciladores
    STOCHASTIC_K_PERIOD: int = 14     # Período para %K del Estocástico
    STOCHASTIC_D_PERIOD: int = 3      # Período para %D del Estocástico
    WILLIAMS_R_PERIOD: int = 14       # Período para Williams %R
    
    # Umbrales para osciladores
    STOCHASTIC_OVERSOLD: float = 20.0    # Umbral de sobreventa
    STOCHASTIC_OVERBOUGHT: float = 80.0  # Umbral de sobrecompra
    WILLIAMS_R_OVERSOLD: float = -80.0   # Umbral de sobreventa Williams %R
    WILLIAMS_R_OVERBOUGHT: float = -20.0 # Umbral de sobrecompra Williams %R
    
    # Períodos para otros indicadores
    RSI_PERIOD: int = 14              # Período para RSI
    CCI_PERIOD: int = 20              # Período para CCI
    BOLLINGER_PERIOD: int = 20        # Período para Bandas de Bollinger
    BOLLINGER_STD_DEV: float = 2.0    # Desviación estándar para Bollinger
    MFI_PERIOD: int = 14              # Período para Money Flow Index
    ATR_PERIOD: int = 14              # Período para Average True Range
    ROC_PERIOD: int = 12              # Período para Rate of Change
    
    # Configuración para análisis de soporte/resistencia
    SUPPORT_RESISTANCE_WINDOW: int = 20    # Ventana para S/R
    SUPPORT_RESISTANCE_MIN_TOUCHES: int = 2 # Mínimo de toques para validar nivel
    
    # Configuración para análisis de volumen
    VOLUME_PROFILE_BINS: int = 20     # Número de bins para perfil de volumen
    
    # Configuración para Fibonacci
    FIBONACCI_LOOKBACK: int = 50      # Período de lookback para Fibonacci
    
    # Configuración para análisis de tendencias
    TREND_ANALYSIS_LOOKBACK: int = 50 # Período para análisis de líneas de tendencia
    CHART_PATTERNS_WINDOW: int = 20   # Ventana para detección de patrones


# ============================================================================
# CONFIGURACIÓN DE TESTING
# ============================================================================

class TestingConfig:
    """Configuración específica para testing y desarrollo."""
    
    # Símbolos para testing - subset reducido para pruebas rápidas
    TEST_SYMBOLS: List[str] = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]
    
    # Configuración de trading bot para testing
    TEST_MIN_CONFIDENCE: float = 70.0
    TEST_MAX_DAILY_TRADES: int = 5
    
    # Configuración de análisis para testing
    TEST_ANALYSIS_INTERVAL: int = 5  # minutos
    
    # Balance para testing
    TEST_PAPER_BALANCE: float = 100.0

# ============================================================================
# CONFIGURACIÓN POR DEFECTO PARA DESARROLLO
# ============================================================================

# Configuración rápida para desarrollo y testing
DEV_CONFIG = {
    'symbols': TradingBotConfig.SYMBOLS[:3],  # Solo 3 símbolos para testing
    'analysis_interval': TestingConfig.TEST_ANALYSIS_INTERVAL,  # Análisis cada 5 minutos para testing
    'min_confidence': 60.0,  # Umbral más bajo para testing
    'paper_balance': TestingConfig.TEST_PAPER_BALANCE,  # Balance menor para testing
}

# ============================================================================
# CONFIGURACIÓN COMPLETA CON TRES PERFILES DE TRADING
# ============================================================================
"""
CONFIGURACIÓN ACTUAL: SISTEMA COMPLETO DE TRES PERFILES

🚀 CONFIGURACIÓN RÁPIDA (ULTRA-CORTA):
- Timeframes: 1m, 5m, 15m (máxima velocidad)
- Análisis cada 5 minutos, actualización cada 10 segundos
- Riesgo por trade: 2.0%, riesgo diario: 6.0%
- 20 trades diarios máximo, 8 posiciones concurrentes
- RSI: 35/65 (muy sensible), confianza mínima: 60%
- Trailing stop desde 1.0% ganancia
- ROI objetivo: 20-35% mensual (alto riesgo/alta recompensa)

⚡ CONFIGURACIÓN AGRESIVA (BALANCEADA):
- Timeframes: 15m, 30m, 1h (balance velocidad/confirmación)
- Análisis cada 15 minutos, actualización cada 20 segundos
- Riesgo por trade: 1.5%, riesgo diario: 4.5%
- 12 trades diarios máximo, 6 posiciones concurrentes
- RSI: 30/70 (moderado), confianza mínima: 65%
- Trailing stop desde 1.5% ganancia
- ROI objetivo: 15-25% mensual (riesgo moderado)

🛡️ CONFIGURACIÓN ÓPTIMA (CONSERVADORA):
- Timeframes: 1h, 4h, 1d (máxima confirmación)
- Análisis cada 30 minutos, actualización cada 30 segundos
- Riesgo por trade: 1.0%, riesgo diario: 3.0%
- 8 trades diarios máximo, 4 posiciones concurrentes
- RSI: 25/75 (conservador), confianza mínima: 70%
- Trailing stop desde 2.0% ganancia
- ROI objetivo: 8-15% mensual (bajo riesgo/preservación capital)

📋 PARA CAMBIAR CONFIGURACIÓN:
Simplemente comenta/descomenta las líneas correspondientes en cada parámetro.
Todos los parámetros críticos ahora incluyen las tres opciones claramente marcadas.
"""