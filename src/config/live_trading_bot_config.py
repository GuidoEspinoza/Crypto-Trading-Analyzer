#!/usr/bin/env python3
"""
🔧 Configuración específica para Live Trading Bot
Parametrización de valores hardcodeados identificados
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from colorama import Fore, Back, Style

@dataclass
class TechnicalIndicatorsConfig:
    """Configuración de indicadores técnicos"""
    rsi_period: int = 14
    sma_short_period: int = 20
    sma_long_period: int = 50
    volume_rolling_period: int = 20
    default_timeframe: str = "1h"
    market_data_limit: int = 50

@dataclass
class BinancePriceAdjustmentConfig:
    """Configuración de ajustes de precio para Binance"""
    buy_adjustment_factor: float = 0.9997  # 0.03% por debajo
    sell_adjustment_factor: float = 1.0003  # 0.03% por arriba
    
    @property
    def buy_adjustment_percentage(self) -> float:
        return (1 - self.buy_adjustment_factor) * 100
    
    @property
    def sell_adjustment_percentage(self) -> float:
        return (self.sell_adjustment_factor - 1) * 100

@dataclass
class LoggingConfig:
    """Configuración de logging"""
    level: int = logging.INFO
    format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    colors_enabled: bool = True
    propagate: bool = False
    
    # Colores para diferentes niveles
    level_colors: Dict[str, str] = None
    
    def __post_init__(self):
        if self.level_colors is None:
            self.level_colors = {
                'DEBUG': Fore.CYAN,
                'INFO': Fore.GREEN,
                'WARNING': Fore.YELLOW,
                'ERROR': Fore.RED,
                'CRITICAL': Fore.MAGENTA + Style.BRIGHT
            }

@dataclass
class SessionStatsConfig:
    """Configuración de estadísticas de sesión"""
    initial_total_trades: int = 0
    initial_successful_trades: int = 0
    initial_total_pnl: float = 0.0
    
@dataclass
class DisplayConfig:
    """Configuración de visualización y emojis"""
    emojis_enabled: bool = True
    
    # Emojis para diferentes tipos de mensajes
    emoji_mapping: Dict[str, str] = None
    
    def __post_init__(self):
        if self.emoji_mapping is None:
            base_mapping = {
                'analyzing': '📊',
                'cycle_start': '🔄',
                'price_info': '💰',
                'indicators': '📈',
                'decision': '🎯',
                'trade_executed': '✅',
                'config_strategies': '📋',
                'config_paper_trader': '💰',
                'config_bot': '⚙️',
                'warning': '⚠️',
                'error': '❌',
                'rocket': '🚀',
                'trade_executing': '💼',
                'strategy_executing': '🔍',
                'signal_arrow': '➡️',
                'adjustment': '🔧',
                'stop_loss': '🛡️',
                'take_profit': '🎯',
                'waiting': '⏱️',
                'stopped': '🛑',
                'no_signals': '⚪',
                'no_assets': '📭',
                'coin': '🪙',
                'money': '💵',
                'final_summary': '🏁',
                'statistics': '📊',
                'success': '✅',
                'up_trend': '📈',
                'down_trend': '📉',
                'neutral': '🔄',
                'shield': '🛡️',
                'briefcase': '💼',
                'separator': '═══════════════════════════════════════════════════════════'
            }
            
            if self.emojis_enabled:
                self.emoji_mapping = base_mapping
            else:
                # Deshabilitar emojis reemplazándolos por strings vacíos
                self.emoji_mapping = {key: "" if key != 'separator' else "===" for key in base_mapping.keys()}

@dataclass
class PerformanceConfig:
    """Configuración de rendimiento"""
    cycle_counter_start: int = 0
    stats_update_frequency: int = 1  # Cada cuántos ciclos actualizar stats
    
class LiveTradingBotConfig:
    """Configuración principal para Live Trading Bot"""
    
    def __init__(self):
        self.technical_indicators = TechnicalIndicatorsConfig()
        self.binance_adjustments = BinancePriceAdjustmentConfig()
        self.logging = LoggingConfig()
        self.session_stats = SessionStatsConfig()
        self.display = DisplayConfig()
        self.performance = PerformanceConfig()
    
    def get_technical_indicators_config(self) -> TechnicalIndicatorsConfig:
        """Obtener configuración de indicadores técnicos"""
        return self.technical_indicators
    
    def get_binance_adjustments_config(self) -> BinancePriceAdjustmentConfig:
        """Obtener configuración de ajustes de precio Binance"""
        return self.binance_adjustments
    
    def get_logging_config(self) -> LoggingConfig:
        """Obtener configuración de logging"""
        return self.logging
    
    def get_session_stats_config(self) -> SessionStatsConfig:
        """Obtener configuración de estadísticas de sesión"""
        return self.session_stats
    
    def get_display_config(self) -> DisplayConfig:
        """Obtener configuración de visualización"""
        return self.display
    
    def get_performance_config(self) -> PerformanceConfig:
        """Obtener configuración de rendimiento"""
        return self.performance
    
    def update_technical_indicators(self, **kwargs):
        """Actualizar configuración de indicadores técnicos"""
        for key, value in kwargs.items():
            if hasattr(self.technical_indicators, key):
                setattr(self.technical_indicators, key, value)
    
    def update_binance_adjustments(self, **kwargs):
        """Actualizar configuración de ajustes Binance"""
        for key, value in kwargs.items():
            if hasattr(self.binance_adjustments, key):
                setattr(self.binance_adjustments, key, value)
    
    def update_logging(self, **kwargs):
        """Actualizar configuración de logging"""
        for key, value in kwargs.items():
            if hasattr(self.logging, key):
                setattr(self.logging, key, value)
    
    def update_display(self, **kwargs):
        """Actualizar configuración de visualización"""
        for key, value in kwargs.items():
            if hasattr(self.display, key):
                setattr(self.display, key, value)
        # Regenerar emoji_mapping si se cambió emojis_enabled
        if 'emojis_enabled' in kwargs:
            self.display.__post_init__()
    
    def to_dict(self) -> Dict:
        """Convertir configuración a diccionario"""
        return {
            'technical_indicators': {
                'rsi_period': self.technical_indicators.rsi_period,
                'sma_short_period': self.technical_indicators.sma_short_period,
                'sma_long_period': self.technical_indicators.sma_long_period,
                'volume_rolling_period': self.technical_indicators.volume_rolling_period,
                'default_timeframe': self.technical_indicators.default_timeframe,
                'market_data_limit': self.technical_indicators.market_data_limit
            },
            'binance_adjustments': {
                'buy_adjustment_factor': self.binance_adjustments.buy_adjustment_factor,
                'sell_adjustment_factor': self.binance_adjustments.sell_adjustment_factor,
                'buy_adjustment_percentage': self.binance_adjustments.buy_adjustment_percentage,
                'sell_adjustment_percentage': self.binance_adjustments.sell_adjustment_percentage
            },
            'logging': {
                'level': self.logging.level,
                'format_string': self.logging.format_string,
                'colors_enabled': self.logging.colors_enabled,
                'propagate': self.logging.propagate
            },
            'display': {
                'emojis_enabled': self.display.emojis_enabled
            },
            'performance': {
                'cycle_counter_start': self.performance.cycle_counter_start,
                'stats_update_frequency': self.performance.stats_update_frequency
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'LiveTradingBotConfig':
        """Crear configuración desde diccionario"""
        config = cls()
        
        if 'technical_indicators' in config_dict:
            ti_config = config_dict['technical_indicators']
            config.update_technical_indicators(**ti_config)
        
        if 'binance_adjustments' in config_dict:
            ba_config = config_dict['binance_adjustments']
            # Solo actualizar los factores, no los porcentajes calculados
            config.update_binance_adjustments(
                buy_adjustment_factor=ba_config.get('buy_adjustment_factor', 0.9997),
                sell_adjustment_factor=ba_config.get('sell_adjustment_factor', 1.0003)
            )
        
        if 'logging' in config_dict:
            log_config = config_dict['logging']
            config.update_logging(**log_config)
        
        if 'display' in config_dict:
            display_config = config_dict['display']
            config.update_display(**display_config)
        
        return config

# Instancia global de configuración
live_trading_bot_config = LiveTradingBotConfig()