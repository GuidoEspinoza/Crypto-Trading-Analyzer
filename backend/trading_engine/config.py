"""Configuración centralizada para el sistema de trading.

Este archivo contiene todas las configuraciones principales del bot de trading,
incluye valores óptimos por defecto y descripciones para facilitar el mantenimiento.
"""

from typing import List, Dict, Any

# ============================================================================
# CONFIGURACIÓN DEL TRADING BOT PRINCIPAL
# ============================================================================

class TradingBotConfig:
    """Configuración principal del bot de trading."""
    
    # Lista de símbolos a analizar - criptomonedas de alta liquidez (óptimo: 8-10 símbolos)
    SYMBOLS: List[str] = [
        "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT",
        "SOLUSDT", "AVAXUSDT", "DOTUSDT", "LINKUSDT", "UNIUSDT"
    ]

    # Símbolos a usar en el bot de trading en vivo (agregar [:X] para limitar cantidad)
    SYMBOLS_LIVE_BOT = SYMBOLS
    
    # Intervalo de análisis en minutos - tiempo entre análisis automáticos (óptimo: 30)
    ANALYSIS_INTERVAL: int = 30
    
    # Umbral mínimo de confianza para ejecutar trades en % (óptimo: 70.0)
    MIN_CONFIDENCE_THRESHOLD: float = 70.0
    # Parámetro para prueba rápida: 50.0 (permite más señales para testing)
    
    # Número máximo de trades por día - control de sobreoperación (óptimo: 8)
    MAX_DAILY_TRADES: int = 8
    # Parámetro para prueba rápida: 20 (permite más actividad para testing)
    
    # Límite de posiciones concurrentes - diversificación controlada (óptimo: 4)
    MAX_CONCURRENT_POSITIONS: int = 4
    # Parámetro para prueba rápida: 8 (permite más posiciones simultáneas)
    
    # Timeframes para análisis profesional - marcos temporales múltiples (óptimo: ["1h", "4h", "1d"])
    PROFESSIONAL_TIMEFRAMES: List[str] = ["1h", "4h", "1d"]
    
    # Timeframe principal para análisis - marco temporal base (óptimo: "1h")
    PRIMARY_TIMEFRAME: str = "1h"
    
    # Valor por defecto del portfolio para cálculos cuando no hay datos (óptimo: 10000)
    DEFAULT_PORTFOLIO_VALUE: float = 10000.0
    
    # Timeframe para confirmación - validación de señales (óptimo: "4h")
    CONFIRMATION_TIMEFRAME: str = "4h"
    
    # Timeframe para análisis de tendencia - dirección general (óptimo: "1d")
    TREND_TIMEFRAME: str = "1d"
    
    # Descripción del bot - identificación del perfil (óptimo: "Profesional")
    BOT_DESCRIPTION: str = "Profesional"
    
    # Configuración específica para Live Trading Bot
    # Intervalo de actualización en segundos para live bot (óptimo: 30)
    LIVE_UPDATE_INTERVAL: int = 30
    
    # Umbral mínimo de confianza para live trading (óptimo: 65.0)
    LIVE_MIN_CONFIDENCE_THRESHOLD: float = 65.0
    
    # Delay en segundos para el primer análisis al iniciar (óptimo: 30)
    FIRST_ANALYSIS_DELAY: int = 30


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USDT para simulación (óptimo: 1000)
    INITIAL_BALANCE: float = 1000.0
    # Parámetro para prueba rápida: 1000.0 (balance mayor para testing)
    
    # Tamaño máximo de posición como % del portfolio (óptimo: 6.0)
    MAX_POSITION_SIZE: float = 6.0  # Formato: porcentaje (6.0 = 6%)
    # Parámetro para prueba rápida: 10.0 (posiciones más grandes para testing)
    
    # Exposición total máxima del portfolio en % (óptimo: 60.0)
    MAX_TOTAL_EXPOSURE: float = 60.0
    # Parámetro para prueba rápida: 80.0 (mayor exposición para testing)
    
    # Valor mínimo por trade en USDT (óptimo: 5.0)
    MIN_TRADE_VALUE: float = 5.0
    # Parámetro para prueba rápida: 1.0 (trades más pequeños para testing)
    
    # Umbral mínimo de confianza para ejecutar trades (óptimo: 60.0)
    MIN_CONFIDENCE_THRESHOLD: float = 60.0
    # Parámetro para prueba rápida: 50.0 (umbral más bajo para testing)
    
    # Slippage máximo permitido en % (óptimo: 0.08)
    MAX_SLIPPAGE: float = 0.08
    
    # Liquidez mínima requerida en % (óptimo: 5.0)
    MIN_LIQUIDITY: float = 5.0
    
    # Máximo % del balance disponible para trading (reserva para fees) (óptimo: 95.0)
    MAX_BALANCE_USAGE: float = 95.0


# ============================================================================
# CONFIGURACIÓN DEL GESTOR DE RIESGO
# ============================================================================

class RiskManagerConfig:
    """Configuración del gestor de riesgo avanzado."""
    
    # Riesgo máximo por trade como % del portfolio (óptimo: 1.0)
    MAX_RISK_PER_TRADE: float = 1.0
    # Parámetro para prueba rápida: 2.0 (mayor riesgo para testing)
    
    # Riesgo máximo diario como % del portfolio (óptimo: 3.0)
    MAX_DAILY_RISK: float = 3.0
    # Parámetro para prueba rápida: 5.0 (mayor riesgo diario para testing)
    
    # Umbral de drawdown máximo antes de parar trading en % (óptimo: 8.0)
    MAX_DRAWDOWN_THRESHOLD: float = 8.0
    # Parámetro para prueba rápida: 15.0 (mayor tolerancia para testing)
    
    # Umbral de correlación máxima entre posiciones (óptimo: 0.6)
    CORRELATION_THRESHOLD: float = 0.6
    
    # Tamaño mínimo de posición como % del portfolio (óptimo: 0.005)
    MIN_POSITION_SIZE: float = 0.005
    
    # Tamaño máximo de posición como % del portfolio (óptimo: 6.0)
    MAX_POSITION_SIZE: float = 6.0  # Formato: porcentaje (6.0 = 6%)
    
    # Fracción Kelly conservadora para sizing (óptimo: 0.15)
    KELLY_FRACTION: float = 0.15
    
    # Factor de ajuste por volatilidad del mercado (óptimo: 0.4)
    VOLATILITY_ADJUSTMENT: float = 0.4
    
    # Multiplicador ATR mínimo para stop-loss dinámico (óptimo: 2.5)
    ATR_MULTIPLIER_MIN: float = 2.5
    
    # Multiplicador ATR máximo para stop-loss dinámico (óptimo: 4.0)
    ATR_MULTIPLIER_MAX: float = 4.0
    
    # Multiplicadores ATR por defecto para diferentes condiciones de mercado
    ATR_DEFAULT: float = 2.0  # Multiplicador por defecto
    ATR_VOLATILE: float = 3.0  # Para mercados volátiles
    ATR_SIDEWAYS: float = 1.5  # Para mercados laterales
    
    # Umbral de ganancia para activar trailing stop en % (óptimo: 2.0)
    TRAILING_STOP_ACTIVATION: float = 2.0
    
    # Umbral para mover stop-loss a breakeven en % (óptimo: 1.2)
    BREAKEVEN_THRESHOLD: float = 1.2
    
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
        
        # Confianza mínima por defecto para estrategias base (óptimo: 60.0)
        DEFAULT_MIN_CONFIDENCE: float = 60.0
        
        # Valores de confianza por defecto para diferentes señales
        HOLD_CONFIDENCE: float = 45.0
        BASE_CONFIDENCE: float = 50.0
        ENHANCED_CONFIDENCE: float = 60.0
        
        # Período ATR por defecto para cálculos de stop-loss (óptimo: 14)
        DEFAULT_ATR_PERIOD: int = 14
    
    # ---- Estrategia RSI Profesional ----
    class ProfessionalRSI:
        """Parámetros para la estrategia RSI profesional."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Confianza mínima requerida en % (óptimo: 72.0)
        MIN_CONFIDENCE: float = 72.0
        # Parámetro para prueba rápida: 50.0 (menor confianza para más señales)
        
        # Nivel de sobreventa del RSI - señal de compra (óptimo: 25)
        RSI_OVERSOLD: int = 25
        # Parámetro para prueba rápida: 30 (menos estricto para más señales)
        
        # Nivel de sobrecompra del RSI - señal de venta (óptimo: 75)
        RSI_OVERBOUGHT: int = 75
        # Parámetro para prueba rápida: 70 (menos estricto para más señales)
        
        # Período del RSI - ventana de cálculo (óptimo: 14)
        RSI_PERIOD: int = 14
        
        # Ratio mínimo de volumen vs promedio (óptimo: 1.8)
        MIN_VOLUME_RATIO: float = 1.8
        
        # Confluencia mínima de indicadores requerida (óptimo: 4)
        MIN_CONFLUENCE: int = 4
        
        # Umbral de fuerza de tendencia ADX (óptimo: 35)
        TREND_STRENGTH_THRESHOLD: float = 35
        
        # Ratio ATR mínimo para volatilidad (óptimo: 1.0)
        MIN_ATR_RATIO: float = 1.0
        
        # Spread máximo permitido en % (óptimo: 0.0015)
        MAX_SPREAD_THRESHOLD: float = 0.0015
    
    # ---- Estrategia Multi-Timeframe ----
    class MultiTimeframe:
        """Parámetros para la estrategia multi-timeframe."""
        
        # Confianza base para señales (óptimo: 50.0)
        BASE_CONFIDENCE: float = 50.0
        
        # Confianza para señales HOLD (óptimo: 45.0)
        HOLD_CONFIDENCE: float = 45.0
        
        # Confianza mínima requerida en % (óptimo: 70.0)
        MIN_CONFIDENCE: float = 70.0
        # Parámetro para prueba rápida: 45.0 (menor confianza para más señales)
        
        # Timeframes utilizados para análisis (óptimo: ["1h", "4h", "1d"])
        TIMEFRAMES: List[str] = ["1h", "4h", "1d"]
        
        # Configuración RSI por timeframe - niveles de sobreventa/sobrecompra
        RSI_CONFIG: Dict[str, Dict[str, int]] = {
            "1h": {"oversold": 25, "overbought": 75},   # Timeframe corto - menos estricto
            "4h": {"oversold": 25, "overbought": 75},   # Timeframe medio - balanceado
            "1d": {"oversold": 30, "overbought": 70}    # Timeframe largo - moderado
        }
        
        # Pesos por timeframe - mayor peso a timeframes largos (óptimo: suma = 1.0)
        TIMEFRAME_WEIGHTS: Dict[str, float] = {
            "1h": 0.2,   # Peso menor para decisiones a corto plazo
            "4h": 0.3,   # Peso medio para tendencia intermedia
            "1d": 0.5    # Peso mayor para tendencia principal
        }
        
        # Consenso mínimo de timeframes requerido (óptimo: 2)
        MIN_CONSENSUS: int = 2
        
        # Requiere alineación de tendencias entre timeframes (óptimo: True)
        REQUIRE_TREND_ALIGNMENT: bool = True
        
        # Consenso mínimo de timeframes para señal válida (óptimo: 2)
        MIN_TIMEFRAME_CONSENSUS: int = 2
        
        # Requiere alineación de tendencias entre timeframes (óptimo: True)
        TREND_ALIGNMENT_REQUIRED: bool = True
    
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
        
        # Umbral mínimo de consenso entre estrategias (óptimo: 0.7)
        MIN_CONSENSUS_THRESHOLD: float = 0.7
        # Parámetro para prueba rápida: 0.5 (menor consenso para más señales)
        
        # Factor de boost de confianza cuando hay consenso (óptimo: 1.15)
        CONFIDENCE_BOOST_FACTOR: float = 1.15


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
    
    # Comisiones de Binance en % por trade (óptimo: 0.1 con BNB)
    TRADING_FEES: float = 0.1
    
    # Timeout para órdenes en segundos (óptimo: 30)
    ORDER_TIMEOUT: int = 30
    
    # Reintentos máximos para órdenes fallidas (óptimo: 3)
    MAX_ORDER_RETRIES: int = 3
    
    # Intervalo de verificación de órdenes en segundos (óptimo: 5)
    ORDER_CHECK_INTERVAL: int = 5


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
# GUÍA DE PARÁMETROS PARA PRUEBAS RÁPIDAS
# ============================================================================
"""
PARA PRUEBAS RÁPIDAS, MODIFICA ESTOS VALORES:

1. MIN_CONFIDENCE_THRESHOLD: 50.0 (más señales)
2. MAX_DAILY_TRADES: 20 (más actividad)
3. MAX_CONCURRENT_POSITIONS: 8 (más posiciones)
4. INITIAL_BALANCE: 1000.0 (balance mayor)
5. MAX_POSITION_SIZE: 10.0 (posiciones más grandes)
6. MIN_TRADE_VALUE: 1.0 (trades más pequeños)
7. MAX_RISK_PER_TRADE: 2.0 (mayor riesgo)
8. RSI_OVERSOLD: 30 (menos estricto)
9. RSI_OVERBOUGHT: 70 (menos estricto)
10. MIN_CONSENSUS_THRESHOLD: 0.5 (menor consenso)

ESTOS VALORES PERMITEN MÁS ACTIVIDAD Y SEÑALES PARA VALIDAR FUNCIONALIDAD.
"""