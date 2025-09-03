"""Configuración centralizada para el sistema de trading.

Este archivo contiene todas las configuraciones principales del bot de trading,
incluye valores óptimos por defecto y descripciones para facilitar el mantenimiento.
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
    
    # Intervalo de análisis en minutos - tiempo entre análisis automáticos (agresivo: 15 - óptimo: 30)
    ANALYSIS_INTERVAL: int = 15
    # ANALYSIS_INTERVAL: int = 30  # Configuración óptima conservadora
    
    # Umbral mínimo de confianza para ejecutar trades en % (agresivo: 65.0 - óptimo: 70.0)
    MIN_CONFIDENCE_THRESHOLD: float = 65.0
    # MIN_CONFIDENCE_THRESHOLD: float = 70.0  # Configuración óptima conservadora
    # Parámetro optimizado para ganancias rápidas con riesgo controlado
    
    # Número máximo de trades por día - control de sobreoperación (agresivo: 12 - óptimo: 8)
    MAX_DAILY_TRADES: int = 12
    # MAX_DAILY_TRADES: int = 8  # Configuración óptima conservadora
    # Parámetro optimizado para maximizar oportunidades diarias
    
    # Límite de posiciones concurrentes - diversificación controlada (agresivo: 6 - óptimo: 4)
    MAX_CONCURRENT_POSITIONS: int = 6
    # MAX_CONCURRENT_POSITIONS: int = 4  # Configuración óptima conservadora
    # Parámetro optimizado para diversificación sin sobreexposición
    
    # Timeframes para análisis profesional - marcos temporales (agresivo: ["15m", "1h", "4h"] - óptimo: ["1h", "4h", "1d"])
    PROFESSIONAL_TIMEFRAMES: List[str] = ["15m", "1h", "4h"]
    # PROFESSIONAL_TIMEFRAMES: List[str] = ["1h", "4h", "1d"]  # Configuración óptima conservadora
    
    # Timeframe principal para análisis - marco temporal base (agresivo: "15m" - óptimo: "1h")
    PRIMARY_TIMEFRAME: str = "15m"
    # PRIMARY_TIMEFRAME: str = "1h"  # Configuración óptima conservadora
    
    # Valor por defecto del portfolio para cálculos cuando no hay datos
    DEFAULT_PORTFOLIO_VALUE: float = GLOBAL_INITIAL_BALANCE
    
    # Timeframe para confirmación - validación de señales (agresivo: "1h" - óptimo: "4h")
    CONFIRMATION_TIMEFRAME: str = "1h"
    # CONFIRMATION_TIMEFRAME: str = "4h"  # Configuración óptima conservadora
    
    # Timeframe para análisis de tendencia - dirección general (agresivo: "4h" - óptimo: "1d")
    TREND_TIMEFRAME: str = "4h"
    # TREND_TIMEFRAME: str = "1d"  # Configuración óptima conservadora
    
    # Descripción del bot - identificación del perfil (óptimo: "Profesional")
    BOT_DESCRIPTION: str = "Profesional"
    
    # Configuración específica para Live Trading Bot
    # Intervalo de actualización en segundos para live bot (agresivo: 20 - óptimo: 30)
    LIVE_UPDATE_INTERVAL: int = 20
    # LIVE_UPDATE_INTERVAL: int = 30  # Configuración óptima conservadora
    
    # Umbral mínimo de confianza para live trading (óptimo: 65.0)
    LIVE_MIN_CONFIDENCE_THRESHOLD: float = 65.0
    
    # Delay en segundos para el primer análisis al iniciar (óptimo: 30)
    FIRST_ANALYSIS_DELAY: int = 30


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USDT para simulación
    INITIAL_BALANCE: float = GLOBAL_INITIAL_BALANCE
    
    # Tamaño máximo de posición como % del portfolio (agresivo: 8.0 - óptimo: 6.0)
    MAX_POSITION_SIZE: float = 8.0  # Formato: porcentaje (8.0 = 8%)
    # MAX_POSITION_SIZE: float = 6.0  # Configuración óptima conservadora
    # Parámetro optimizado para maximizar ganancias con riesgo controlado
    
    # Exposición total máxima del portfolio en % (agresivo: 75.0 - óptimo: 60.0)
    MAX_TOTAL_EXPOSURE: float = 75.0
    # MAX_TOTAL_EXPOSURE: float = 60.0  # Configuración óptima conservadora
    # Parámetro optimizado para mayor exposición con diversificación
    
    # Valor mínimo por trade en USDT (agresivo: 10.0 - óptimo: 5.0)
    MIN_TRADE_VALUE: float = 10.0
    # MIN_TRADE_VALUE: float = 5.0  # Configuración óptima conservadora
    # Parámetro optimizado para trades más significativos
    
    # Umbral mínimo de confianza para ejecutar trades (agresivo: 62.0 - óptimo: 60.0)
    MIN_CONFIDENCE_THRESHOLD: float = 62.0
    # MIN_CONFIDENCE_THRESHOLD: float = 60.0  # Configuración óptima conservadora
    # Parámetro optimizado para balance entre oportunidades y calidad
    
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
    
    # Riesgo máximo por trade como % del portfolio (agresivo: 1.5 - óptimo: 1.0)
    MAX_RISK_PER_TRADE: float = 1.5
    # MAX_RISK_PER_TRADE: float = 1.0  # Configuración óptima conservadora
    # Parámetro optimizado para ganancias rápidas con riesgo controlado
    
    # Riesgo máximo diario como % del portfolio (agresivo: 4.5 - óptimo: 3.0)
    MAX_DAILY_RISK: float = 4.5
    # MAX_DAILY_RISK: float = 3.0  # Configuración óptima conservadora
    # Parámetro optimizado para maximizar oportunidades diarias
    
    # Umbral de drawdown máximo antes de parar trading en % (agresivo: 10.0 - óptimo: 8.0)
    MAX_DRAWDOWN_THRESHOLD: float = 10.0
    # MAX_DRAWDOWN_THRESHOLD: float = 8.0  # Configuración óptima conservadora
    # Parámetro optimizado para mayor tolerancia en mercados volátiles
    
    # Umbral de correlación máxima entre posiciones (óptimo: 0.6)
    CORRELATION_THRESHOLD: float = 0.6
    
    # Tamaño mínimo de posición como % del portfolio (óptimo: 0.005)
    MIN_POSITION_SIZE: float = 0.005
    
    # Tamaño máximo de posición como % del portfolio (agresivo: 8.0 - óptimo: 6.0)
    MAX_POSITION_SIZE: float = 8.0  # Formato: porcentaje (8.0 = 8%)
    # MAX_POSITION_SIZE: float = 6.0  # Configuración óptima conservadora
    
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
    
    # Umbral de ganancia para activar trailing stop en % (agresivo: 1.5 - óptimo: 2.0)
    TRAILING_STOP_ACTIVATION: float = 1.5
    # TRAILING_STOP_ACTIVATION: float = 2.0  # Configuración óptima conservadora
    
    # Umbral para mover stop-loss a breakeven en % (agresivo: 1.0 - óptimo: 1.2)
    BREAKEVEN_THRESHOLD: float = 1.0
    # BREAKEVEN_THRESHOLD: float = 1.2  # Configuración óptima conservadora
    
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
        
        # Confianza mínima requerida en % (agresivo: 68.0 - óptimo: 72.0)
        MIN_CONFIDENCE: float = 68.0
        # MIN_CONFIDENCE: float = 72.0  # Configuración óptima conservadora
        # Parámetro optimizado para balance entre calidad y oportunidades
        
        # Nivel de sobreventa del RSI - señal de compra (agresivo: 30 - óptimo: 25)
        RSI_OVERSOLD: int = 30
        # RSI_OVERSOLD: int = 25  # Configuración óptima conservadora
        # Parámetro optimizado para capturar más oportunidades de compra
        
        # Nivel de sobrecompra del RSI - señal de venta (agresivo: 70 - óptimo: 75)
        RSI_OVERBOUGHT: int = 70
        # RSI_OVERBOUGHT: int = 75  # Configuración óptima conservadora
        # Parámetro optimizado para capturar más oportunidades de venta
        
        # Período del RSI - ventana de cálculo (óptimo: 14)
        RSI_PERIOD: int = 14
        
        # Ratio mínimo de volumen vs promedio (agresivo: 1.5 - óptimo: 1.8)
        MIN_VOLUME_RATIO: float = 1.5
        # MIN_VOLUME_RATIO: float = 1.8  # Configuración óptima conservadora
        
        # Confluencia mínima de indicadores requerida (agresivo: 3 - óptimo: 4)
        MIN_CONFLUENCE: int = 3
        # MIN_CONFLUENCE: int = 4  # Configuración óptima conservadora
        
        # Umbral de fuerza de tendencia ADX (agresivo: 30 - óptimo: 35)
        TREND_STRENGTH_THRESHOLD: float = 30
        # TREND_STRENGTH_THRESHOLD: float = 35  # Configuración óptima conservadora
        
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
        
        # Confianza mínima requerida en % (agresivo: 65.0 - óptimo: 70.0)
        MIN_CONFIDENCE: float = 65.0
        # MIN_CONFIDENCE: float = 70.0  # Configuración óptima conservadora
        # Parámetro optimizado para balance entre calidad y frecuencia
        
        # Timeframes utilizados para análisis (agresivo: ["15m", "1h", "4h"] - óptimo: ["1h", "4h", "1d"])
        TIMEFRAMES: List[str] = ["15m", "1h", "4h"]
        # TIMEFRAMES: List[str] = ["1h", "4h", "1d"]  # Configuración óptima conservadora
        
        # Configuración RSI por timeframe - niveles de sobreventa/sobrecompra (agresivo)
        RSI_CONFIG: Dict[str, Dict[str, int]] = {
            "15m": {"oversold": 35, "overbought": 65},  # Timeframe muy corto - más agresivo
            "1h": {"oversold": 30, "overbought": 70},   # Timeframe corto - agresivo
            "4h": {"oversold": 25, "overbought": 75}    # Timeframe medio - balanceado
        }
        
        # Pesos por timeframe - balance entre corto y medio plazo (agresivo: suma = 1.0)
        TIMEFRAME_WEIGHTS: Dict[str, float] = {
            "15m": 0.3,  # Peso significativo para oportunidades rápidas
            "1h": 0.4,   # Peso principal para decisiones a corto plazo
            "4h": 0.3    # Peso para confirmación de tendencia
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
        
        # Umbral mínimo de consenso entre estrategias (agresivo: 0.6 - óptimo: 0.7)
        MIN_CONSENSUS_THRESHOLD: float = 0.6
        # MIN_CONSENSUS_THRESHOLD: float = 0.7  # Configuración óptima conservadora
        # Parámetro optimizado para balance entre consenso y oportunidades
        
        # Factor de boost de confianza cuando hay consenso (agresivo: 1.2 - óptimo: 1.15)
        CONFIDENCE_BOOST_FACTOR: float = 1.2
        # CONFIDENCE_BOOST_FACTOR: float = 1.15  # Configuración óptima conservadora


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
# CONFIGURACIÓN OPTIMIZADA PARA TRADING AGRESIVO PERO SEGURO
# ============================================================================
"""
CONFIGURACIÓN ACTUAL OPTIMIZADA PARA GANANCIAS RÁPIDAS Y SEGURAS:

🎯 TIMEFRAMES AGRESIVOS:
- Análisis cada 15 minutos (captura oportunidades rápidas)
- Timeframes: 15m, 1h, 4h (balance entre velocidad y confirmación)
- Actualización live cada 20 segundos

💰 GESTIÓN DE RIESGO OPTIMIZADA:
- Riesgo por trade: 1.5% (mayor que conservador, menor que arriesgado)
- Riesgo diario: 4.5% (permite múltiples oportunidades)
- Posición máxima: 8% (significativa pero controlada)
- Exposición total: 75% (alta pero diversificada)

📊 SEÑALES OPTIMIZADAS:
- Confianza mínima: 65-68% (balance calidad/frecuencia)
- RSI: 30/70 (captura más oportunidades)
- Confluencia mínima: 3 indicadores
- Consenso estrategias: 60%

🚀 CONFIGURACIÓN AGRESIVA:
- 12 trades diarios máximo
- 6 posiciones concurrentes
- 15 símbolos de alta volatilidad
- Trailing stop desde 1.5% ganancia
- Breakeven en 1% ganancia

⚡ RESULTADO ESPERADO:
- Mayor frecuencia de trades
- Captura rápida de movimientos
- Riesgo controlado pero optimizado
- ROI mensual objetivo: 15-25%
"""