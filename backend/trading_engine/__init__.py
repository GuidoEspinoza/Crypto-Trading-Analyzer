"""
🤖 Universal Trading Analyzer - Trading Engine
Motor de trading automático con estrategias inteligentes
"""

# Estrategias de trading (clases base)
from .strategies import TradingStrategy, TradingSignal

# Estrategias mejoradas
from .enhanced_strategies import (
    EnhancedTradingStrategy, 
    ProfessionalRSIStrategy, 
    MultiTimeframeStrategy, 
    EnsembleStrategy
)

# Gestión de riesgo
from .enhanced_risk_manager import EnhancedRiskManager

# Trading y backtesting
from .paper_trader import PaperTrader
from .trading_bot import TradingBot
from .backtesting_engine import BacktestingEngine, BacktestConfig
from .data_fetcher import DataFetcher

__all__ = [
    # Estrategias base
    'TradingStrategy',
    'RSIStrategy', 
    'MACDStrategy',
    'IchimokuStrategy',
    
    # Estrategias mejoradas
    'EnhancedTradingStrategy',
    'ProfessionalRSIStrategy',
    'MultiTimeframeStrategy',
    'EnsembleStrategy',
    
    # Gestión de riesgo
    'RiskManager',
    'EnhancedRiskManager',
    
    # Trading y backtesting
    'PaperTrader',
    'TradingBot',
    'BacktestingEngine',
    'BacktestConfig',
    'DataFetcher'
]