"""Configuration manager for the crypto trading analyzer.

This module provides centralized configuration management for the entire
trading system, handling different environments and validation.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TradingConfig:
    """Trading configuration data class."""
    default_risk_percentage: float
    max_positions: int
    stop_loss_percentage: float
    take_profit_percentage: float
    trading_pairs: list
    timeframe: str
    strategy_name: str
    
@dataclass
class ExchangeConfig:
    """Exchange configuration data class."""
    name: str
    api_key: str
    secret_key: str
    testnet: bool
    rate_limit: int

class ConfigManager:
    """Manages configuration for the trading system."""
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or "src/config/trading_config.json"
        self.config_data = {}
        self._load_config()
        self._load_env_variables()
    
    def _load_config(self) -> None:
        """Load configuration from JSON file."""
        config_path = Path(self.config_file)
        
        if not config_path.exists():
            logger.warning(f"Config file not found: {self.config_file}")
            self._create_default_config()
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            logger.info(f"Configuration loaded from {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            self._create_default_config()
    
    def _load_env_variables(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'BINANCE_API_KEY': ['exchange', 'binance', 'api_key'],
            'BINANCE_SECRET_KEY': ['exchange', 'binance', 'secret_key'],
            'BINANCE_TESTNET': ['exchange', 'binance', 'testnet'],
            'TRADING_MODE': ['trading', 'mode'],
            'RISK_LEVEL': ['trading', 'risk_level'],
            'MAX_POSITIONS': ['trading', 'max_positions'],
            'DEFAULT_TIMEFRAME': ['trading', 'timeframe']
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                self._set_nested_value(config_path, value)
    
    def _set_nested_value(self, path: list, value: str) -> None:
        """Set a nested configuration value.
        
        Args:
            path: List representing the nested path
            value: Value to set
        """
        current = self.config_data
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if value.lower() in ('true', 'false'):
            value = value.lower() == 'true'
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        current[path[-1]] = value
    
    def _create_default_config(self) -> None:
        """Create default configuration."""
        self.config_data = {
            "trading": {
                "mode": "paper",
                "risk_level": "conservative",
                "default_risk_percentage": 0.02,
                "max_positions": 5,
                "stop_loss_percentage": 0.05,
                "take_profit_percentage": 0.10,
                "timeframe": "1h",
                "strategy_name": "rsi_strategy",
                "trading_pairs": ["BTC/USDT", "ETH/USDT"]
            },
            "exchange": {
                "binance": {
                    "api_key": "",
                    "secret_key": "",
                    "testnet": True,
                    "rate_limit": 1200
                }
            },
            "database": {
                "url": "sqlite:///data/trading_bot.db",
                "echo": False
            },
            "logging": {
                "level": "INFO",
                "file": "logs/trading.log",
                "max_size_mb": 100,
                "backup_count": 5
            },
            "strategies": {
                "rsi_strategy": {
                    "rsi_period": 14,
                    "oversold_threshold": 30,
                    "overbought_threshold": 70
                },
                "ma_strategy": {
                    "fast_period": 10,
                    "slow_period": 20
                },
                "bollinger_strategy": {
                    "period": 20,
                    "std_dev": 2
                }
            }
        }
        
        # Save default config
        self.save_config()
        logger.info("Default configuration created")
    
    def get_trading_config(self) -> TradingConfig:
        """Get trading configuration.
        
        Returns:
            TradingConfig object
        """
        trading_data = self.config_data.get('trading', {})
        
        return TradingConfig(
            default_risk_percentage=trading_data.get('default_risk_percentage', 0.02),
            max_positions=trading_data.get('max_positions', 5),
            stop_loss_percentage=trading_data.get('stop_loss_percentage', 0.05),
            take_profit_percentage=trading_data.get('take_profit_percentage', 0.10),
            trading_pairs=trading_data.get('trading_pairs', ['BTC/USDT']),
            timeframe=trading_data.get('timeframe', '1h'),
            strategy_name=trading_data.get('strategy_name', 'rsi_strategy')
        )
    
    def get_exchange_config(self, exchange_name: str = 'binance') -> ExchangeConfig:
        """Get exchange configuration.
        
        Args:
            exchange_name: Name of the exchange
        
        Returns:
            ExchangeConfig object
        """
        exchange_data = self.config_data.get('exchange', {}).get(exchange_name, {})
        
        return ExchangeConfig(
            name=exchange_name,
            api_key=exchange_data.get('api_key', ''),
            secret_key=exchange_data.get('secret_key', ''),
            testnet=exchange_data.get('testnet', True),
            rate_limit=exchange_data.get('rate_limit', 1200)
        )
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration.
        
        Returns:
            Database configuration dictionary
        """
        return self.config_data.get('database', {
            'url': 'sqlite:///data/trading_bot.db',
            'echo': False
        })
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration.
        
        Returns:
            Logging configuration dictionary
        """
        return self.config_data.get('logging', {
            'level': 'INFO',
            'file': 'logs/trading.log',
            'max_size_mb': 100,
            'backup_count': 5
        })
    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        """Get configuration for a specific strategy.
        
        Args:
            strategy_name: Name of the strategy
        
        Returns:
            Strategy configuration dictionary
        """
        strategies = self.config_data.get('strategies', {})
        return strategies.get(strategy_name, {})
    
    def get_config(self, key_path: str, default: Any = None) -> Any:
        """Get a configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., 'trading.risk_level')
            default: Default value if key not found
        
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        current = self.config_data
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def set_config(self, key_path: str, value: Any) -> None:
        """Set a configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., 'trading.risk_level')
            value: Value to set
        """
        keys = key_path.split('.')
        self._set_nested_value(keys, value)
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")
    
    def validate_config(self) -> bool:
        """Validate the current configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []
        
        # Validate trading config
        trading = self.config_data.get('trading', {})
        if not isinstance(trading.get('default_risk_percentage'), (int, float)):
            errors.append("Invalid default_risk_percentage")
        
        if not isinstance(trading.get('max_positions'), int):
            errors.append("Invalid max_positions")
        
        # Validate exchange config
        exchange = self.config_data.get('exchange', {})
        binance = exchange.get('binance', {})
        
        if not binance.get('api_key'):
            errors.append("Missing Binance API key")
        
        if not binance.get('secret_key'):
            errors.append("Missing Binance secret key")
        
        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False
        
        logger.info("Configuration validation passed")
        return True
    
    def is_paper_trading(self) -> bool:
        """Check if paper trading is enabled.
        
        Returns:
            True if paper trading is enabled
        """
        return self.get_config('trading.mode', 'paper') == 'paper'
    
    def get_risk_level(self) -> str:
        """Get the current risk level.
        
        Returns:
            Risk level string
        """
        return self.get_config('trading.risk_level', 'conservative')