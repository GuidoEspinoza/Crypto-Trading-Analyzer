"""
🗄️ Universal Trading Analyzer - Database Package
Sistema de base de datos SQLite para trading bot
"""

from .database import DatabaseManager, get_db, db_manager
from .models import Trade, Portfolio, Strategy, BacktestResult, TradingSignal

__all__ = [
    'DatabaseManager',
    'get_db',
    'db_manager',  # ¡Esta línea faltaba!
    'Trade',
    'Portfolio', 
    'Strategy',
    'BacktestResult',
    'TradingSignal'
]