"""🔧 Configuración Principal para main.py
Centraliza todos los parámetros configurables del API principal
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

@dataclass
class APIConfig:
    """Configuración de la API FastAPI"""
    title: str = "🚀 Universal Trading Analyzer + Trading Bot"
    description: str = "API para análisis técnico de criptomonedas en tiempo real + Trading Bot automático"
    version: str = "4.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

@dataclass
class CORSConfig:
    """Configuración de CORS"""
    allow_origins: List[str] = None
    allow_credentials: bool = True
    allow_methods: List[str] = None
    allow_headers: List[str] = None
    
    def __post_init__(self):
        if self.allow_origins is None:
            self.allow_origins = ["*"]
        if self.allow_methods is None:
            self.allow_methods = ["*"]
        if self.allow_headers is None:
            self.allow_headers = ["*"]

@dataclass
class ExchangeConfig:
    """Configuración del exchange"""
    exchange_name: str = "binance"
    sandbox: bool = False
    enable_rate_limit: bool = True
    default_symbol: str = "BTC/USDT"
    
@dataclass
class TradingBotDefaults:
    """Valores por defecto del trading bot"""
    analysis_interval_minutes: int = 60
    max_daily_trades: int = 10
    min_confidence_threshold: float = 0.7
    enable_trading: bool = False
    default_symbols: List[str] = None
    initial_portfolio_value: float = 10000.0
    
    def __post_init__(self):
        if self.default_symbols is None:
            self.default_symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT"]

@dataclass
class AnalysisConfig:
    """Configuración de análisis"""
    default_timeframe: str = "1h"
    available_timeframes: List[str] = None
    backtest_default_days: int = 30
    
    def __post_init__(self):
        if self.available_timeframes is None:
            self.available_timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]

@dataclass
class HealthCheckConfig:
    """Configuración de health check"""
    check_exchange: bool = True
    check_database: bool = True
    check_trading_bot: bool = True
    timeout_seconds: int = 30

@dataclass
class ErrorConfig:
    """Configuración de manejo de errores"""
    default_error_status_code: int = 500
    service_unavailable_code: int = 503
    bad_request_code: int = 400
    not_implemented_code: int = 501

@dataclass
class TradingModeConfig:
    """Configuración de modos de trading"""
    default_mode: str = "paper"
    available_modes: List[str] = None
    live_trading_enabled: bool = False
    require_confirmation_for_live: bool = True
    
    def __post_init__(self):
        if self.available_modes is None:
            self.available_modes = ["paper", "live"]

@dataclass
class StrategyConfig:
    """Configuración de estrategias"""
    available_strategies: Dict[str, Dict[str, Any]] = None
    default_strategies: List[str] = None
    confidence_threshold: float = 0.6
    
    def __post_init__(self):
        if self.available_strategies is None:
            self.available_strategies = {
                "professionalrsi": {
                    "name": "ProfessionalRSI",
                    "description": "RSI profesional con análisis de volumen y tendencia",
                    "features": ["Volume confirmation", "Trend analysis", "Risk management"]
                },
                "multitimeframe": {
                    "name": "MultiTimeframe",
                    "description": "Análisis multi-timeframe con votación ponderada",
                    "features": ["1h, 4h, 1d analysis", "Weighted voting", "Confluence scoring"]
                },
                "ensemble": {
                    "name": "Ensemble",
                    "description": "Estrategia ensemble que combina múltiples señales",
                    "features": ["Multiple strategies", "Intelligent voting", "Advanced risk management"]
                }
            }
        if self.default_strategies is None:
            self.default_strategies = ["ProfessionalRSI", "MultiTimeframe", "Ensemble"]

@dataclass
class PaperTradingConfig:
    """Configuración de paper trading"""
    initial_balance: float = 10000.0
    max_trades_per_day: int = 10
    max_position_percentage: float = 0.1  # 10% del balance máximo por posición
    default_stop_loss: float = 0.02  # 2%
    default_take_profit: float = 0.04  # 4%
    enable_reset: bool = True
    track_performance: bool = True

class MainConfig:
    """Configuración principal que agrupa todas las configuraciones"""
    
    def __init__(self):
        self.api = APIConfig()
        self.cors = CORSConfig()
        self.exchange = ExchangeConfig()
        self.trading_bot = TradingBotDefaults()
        self.analysis = AnalysisConfig()
        self.health_check = HealthCheckConfig()
        self.error = ErrorConfig()
        self.trading_mode = TradingModeConfig()
        self.strategy = StrategyConfig()
        self.paper_trading = PaperTradingConfig()
    
    @classmethod
    def from_env(cls) -> 'MainConfig':
        """Crear configuración desde variables de entorno"""
        config = cls()
        
        # API Config desde env
        config.api.host = os.getenv('API_HOST', config.api.host)
        config.api.port = int(os.getenv('API_PORT', config.api.port))
        config.api.reload = os.getenv('API_RELOAD', 'true').lower() == 'true'
        
        # Exchange Config desde env
        config.exchange.exchange_name = os.getenv('EXCHANGE_NAME', config.exchange.exchange_name)
        config.exchange.sandbox = os.getenv('EXCHANGE_SANDBOX', 'false').lower() == 'true'
        
        # Trading Bot Config desde env
        config.trading_bot.analysis_interval_minutes = int(
            os.getenv('BOT_ANALYSIS_INTERVAL', config.trading_bot.analysis_interval_minutes)
        )
        config.trading_bot.max_daily_trades = int(
            os.getenv('BOT_MAX_DAILY_TRADES', config.trading_bot.max_daily_trades)
        )
        config.trading_bot.min_confidence_threshold = float(
            os.getenv('BOT_MIN_CONFIDENCE', config.trading_bot.min_confidence_threshold)
        )
        config.trading_bot.enable_trading = os.getenv('BOT_ENABLE_TRADING', 'false').lower() == 'true'
        
        # Analysis Config desde env
        config.analysis.default_timeframe = os.getenv('DEFAULT_TIMEFRAME', config.analysis.default_timeframe)
        config.analysis.backtest_default_days = int(
            os.getenv('BACKTEST_DEFAULT_DAYS', config.analysis.backtest_default_days)
        )
        
        # Paper Trading Config desde env
        config.paper_trading.initial_balance = float(
            os.getenv('PAPER_INITIAL_BALANCE', config.paper_trading.initial_balance)
        )
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir configuración a diccionario"""
        return {
            'api': self.api.__dict__,
            'cors': self.cors.__dict__,
            'exchange': self.exchange.__dict__,
            'trading_bot': self.trading_bot.__dict__,
            'analysis': self.analysis.__dict__,
            'health_check': self.health_check.__dict__,
            'error': self.error.__dict__,
            'trading_mode': self.trading_mode.__dict__,
            'strategy': self.strategy.__dict__,
            'paper_trading': self.paper_trading.__dict__
        }

# Instancia global de configuración
config = MainConfig.from_env()