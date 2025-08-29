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
    
    # Intervalo de análisis en minutos - tiempo entre análisis automáticos (óptimo: 30)
    ANALYSIS_INTERVAL: int = 30
    
    # Umbral mínimo de confianza para ejecutar trades en % (óptimo: 75.0)
    MIN_CONFIDENCE_THRESHOLD: float = 75.0
    
    # Número máximo de trades por día - control de sobreoperación (óptimo: 6)
    MAX_DAILY_TRADES: int = 6
    
    # Límite de posiciones concurrentes - diversificación controlada (óptimo: 4)
    MAX_CONCURRENT_POSITIONS: int = 4
    
    # Timeframes para análisis profesional - marcos temporales múltiples (óptimo: ["1h", "4h", "1d"])
    PROFESSIONAL_TIMEFRAMES: List[str] = ["1h", "4h", "1d"]
    
    # Timeframe principal para análisis - marco temporal base (óptimo: "1h")
    PRIMARY_TIMEFRAME: str = "1h"
    
    # Timeframe para confirmación - validación de señales (óptimo: "4h")
    CONFIRMATION_TIMEFRAME: str = "4h"
    
    # Timeframe para análisis de tendencia - dirección general (óptimo: "1d")
    TREND_TIMEFRAME: str = "1d"
    
    # Descripción del bot - identificación del perfil (óptimo: "Profesional")
    BOT_DESCRIPTION: str = "Profesional"


# ============================================================================
# CONFIGURACIÓN DEL PAPER TRADER
# ============================================================================

class PaperTraderConfig:
    """Configuración del simulador de trading (paper trading)."""
    
    # Balance inicial en USDT para simulación (óptimo: 1000)
    INITIAL_BALANCE: float = 100.0
    
    # Tamaño máximo de posición como % del portfolio (óptimo: 6.0)
    MAX_POSITION_SIZE: float = 6.0  # Formato: porcentaje (6.0 = 6%)
    
    # Exposición total máxima del portfolio en % (óptimo: 60.0)
    MAX_TOTAL_EXPOSURE: float = 60.0
    
    # Valor mínimo por trade en USDT (óptimo: 5.0)
    MIN_TRADE_VALUE: float = 5.0
    
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
    
    # Riesgo máximo diario como % del portfolio (óptimo: 3.0)
    MAX_DAILY_RISK: float = 3.0
    
    # Umbral de drawdown máximo antes de parar trading en % (óptimo: 8.0)
    MAX_DRAWDOWN_THRESHOLD: float = 8.0
    
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
    
    # ---- Estrategia RSI Profesional ----
    class ProfessionalRSI:
        """Parámetros para la estrategia RSI profesional."""
        
        # Confianza mínima requerida en % (óptimo: 72.0)
        MIN_CONFIDENCE: float = 72.0
        
        # Nivel de sobreventa del RSI - señal de compra (óptimo: 20)
        RSI_OVERSOLD: int = 20
        
        # Nivel de sobrecompra del RSI - señal de venta (óptimo: 80)
        RSI_OVERBOUGHT: int = 80
        
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
        
        # Confianza mínima requerida en % (óptimo: 70.0)
        MIN_CONFIDENCE: float = 70.0
        
        # Timeframes utilizados para análisis (óptimo: ["1h", "4h", "1d"])
        TIMEFRAMES: List[str] = ["1h", "4h", "1d"]
        
        # Configuración RSI por timeframe - niveles de sobreventa/sobrecompra
        RSI_CONFIG: Dict[str, Dict[str, int]] = {
            "1h": {"oversold": 20, "overbought": 80},   # Timeframe corto - más estricto
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
        
        # Pesos de cada estrategia en el ensemble (óptimo: RSI=0.4, MultiTF=0.6)
        STRATEGY_WEIGHTS: Dict[str, float] = {
            "Professional_RSI": 0.4,
            "Multi_Timeframe": 0.6
        }
        
        # Umbral mínimo de consenso entre estrategias (óptimo: 0.7)
        MIN_CONSENSUS_THRESHOLD: float = 0.7
        
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
        config_type: Tipo de configuración ('bot', 'risk', 'paper', 'strategy', 'db', 'log', 'live')
    
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
        'live': LiveTradingConfig
    }
    
    if config_type not in configs:
        raise ValueError(f"Tipo de configuración '{config_type}' no válido. Opciones: {list(configs.keys())}")
    
    return configs[config_type]


# ============================================================================
# CONFIGURACIÓN POR DEFECTO PARA DESARROLLO
# ============================================================================

# Configuración rápida para desarrollo y testing
DEV_CONFIG = {
    'symbols': TradingBotConfig.SYMBOLS[:3],  # Solo 3 símbolos para testing
    'analysis_interval': 5,  # Análisis cada 5 minutos para testing
    'min_confidence': 60.0,  # Umbral más bajo para testing
    'paper_balance': 100.0,  # Balance menor para testing
}