"""Logging utilities for the crypto trading analyzer.

This module provides centralized logging configuration and utilities
for the entire trading system.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with consistent formatting.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        log_file: Optional log file path
        format_string: Optional custom format string
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Default format
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        # Create logs directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_trading_logger(paper_trading: bool = True) -> logging.Logger:
    """Get a logger specifically configured for trading operations.
    
    Args:
        paper_trading: Whether this is paper trading or live trading
    
    Returns:
        Configured trading logger
    """
    mode = "paper" if paper_trading else "live"
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/trading_{mode}_{timestamp}.log"
    
    format_string = (
        '%(asctime)s - %(name)s - %(levelname)s - '
        f'[{mode.upper()}] - %(message)s'
    )
    
    return setup_logger(
        f'trading_{mode}',
        level=logging.INFO,
        log_file=log_file,
        format_string=format_string
    )

def get_strategy_logger(strategy_name: str) -> logging.Logger:
    """Get a logger for a specific trading strategy.
    
    Args:
        strategy_name: Name of the trading strategy
    
    Returns:
        Configured strategy logger
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/strategy_{strategy_name}_{timestamp}.log"
    
    format_string = (
        '%(asctime)s - %(levelname)s - '
        f'[{strategy_name.upper()}] - %(message)s'
    )
    
    return setup_logger(
        f'strategy_{strategy_name}',
        level=logging.INFO,
        log_file=log_file,
        format_string=format_string
    )

def get_database_logger() -> logging.Logger:
    """Get a logger for database operations.
    
    Returns:
        Configured database logger
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = f"logs/database_{timestamp}.log"
    
    format_string = (
        '%(asctime)s - %(levelname)s - '
        '[DATABASE] - %(message)s'
    )
    
    return setup_logger(
        'database',
        level=logging.INFO,
        log_file=log_file,
        format_string=format_string
    )

class TradingLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds trading context to log messages."""
    
    def process(self, msg, kwargs):
        """Process the logging record."""
        symbol = self.extra.get('symbol', 'UNKNOWN')
        strategy = self.extra.get('strategy', 'UNKNOWN')
        return f'[{symbol}|{strategy}] {msg}', kwargs

def get_trading_adapter(
    logger: logging.Logger,
    symbol: str,
    strategy: str
) -> TradingLoggerAdapter:
    """Get a trading logger adapter with context.
    
    Args:
        logger: Base logger
        symbol: Trading symbol
        strategy: Strategy name
    
    Returns:
        Logger adapter with trading context
    """
    return TradingLoggerAdapter(
        logger,
        {'symbol': symbol, 'strategy': strategy}
    )

# Convenience function for quick setup
def quick_setup(name: str = 'crypto_trading') -> logging.Logger:
    """Quick logger setup for development and testing.
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger
    """
    return setup_logger(
        name,
        level=logging.INFO,
        log_file=f"logs/{name}.log"
    )