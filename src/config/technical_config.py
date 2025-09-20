"""
Configuración técnica centralizada para indicadores y estrategias.
Centraliza todos los parámetros técnicos para evitar valores hardcodeados dispersos.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from enum import Enum


class TradingProfile(Enum):
    """Perfiles de trading disponibles"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    SCALPING = "scalping"
    SWING = "swing"


@dataclass
class RSIConfig:
    """Configuración para RSI (Relative Strength Index)"""
    period: int = 14
    oversold_threshold: float = 30.0
    overbought_threshold: float = 70.0
    extreme_oversold: float = 20.0
    extreme_overbought: float = 80.0


@dataclass
class StochasticConfig:
    """Configuración para Oscilador Estocástico"""
    k_period: int = 14
    d_period: int = 3
    smooth_k: int = 3
    oversold_threshold: float = 20.0
    overbought_threshold: float = 80.0


@dataclass
class MACDConfig:
    """Configuración para MACD"""
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9


@dataclass
class BollingerBandsConfig:
    """Configuración para Bandas de Bollinger"""
    period: int = 20
    std_dev: float = 2.0
    squeeze_threshold: float = 0.1


@dataclass
class MovingAverageConfig:
    """Configuración para Medias Móviles"""
    short_period: int = 20
    medium_period: int = 50
    long_period: int = 200
    ema_alpha: float = 0.1


@dataclass
class FibonacciConfig:
    """Configuración para Fibonacci"""
    lookback_period: int = 100
    retracement_levels: list = field(default_factory=lambda: [0.236, 0.382, 0.5, 0.618, 0.786])
    extension_levels: list = field(default_factory=lambda: [1.272, 1.414, 1.618, 2.0])


@dataclass
class IchimokuConfig:
    """Configuración para Ichimoku Cloud"""
    tenkan_period: int = 9
    kijun_period: int = 26
    senkou_span_b_period: int = 52
    displacement: int = 26


@dataclass
class VolumeConfig:
    """Configuración para indicadores de volumen"""
    sma_period: int = 20
    volume_spike_threshold: float = 2.0
    volume_dry_threshold: float = 0.5


@dataclass
class RiskConfig:
    """Configuración para gestión de riesgo"""
    max_position_size: float = 0.1
    stop_loss_percentage: float = 0.02
    take_profit_percentage: float = 0.04
    max_drawdown_threshold: float = 0.15
    risk_reward_ratio: float = 2.0


@dataclass
class StrategyConfig:
    """Configuración para estrategias de trading"""
    base_confidence: float = 0.5
    hold_confidence: float = 0.4
    min_confidence_threshold: float = 0.6
    max_confidence_threshold: float = 0.9
    signal_decay_factor: float = 0.95


class TechnicalConfig:
    """
    Configuración técnica centralizada que adapta parámetros según el perfil de trading.
    """
    
    def __init__(self, profile: TradingProfile = TradingProfile.MODERATE):
        self.profile = profile
        self._load_profile_configs()
    
    def _load_profile_configs(self):
        """Carga configuraciones específicas según el perfil"""
        
        # Configuraciones base (perfil moderado)
        base_configs = {
            'rsi': RSIConfig(),
            'stochastic': StochasticConfig(),
            'macd': MACDConfig(),
            'bollinger': BollingerBandsConfig(),
            'ma': MovingAverageConfig(),
            'fibonacci': FibonacciConfig(),
            'ichimoku': IchimokuConfig(),
            'volume': VolumeConfig(),
            'risk': RiskConfig(),
            'strategy': StrategyConfig()
        }
        
        # Ajustes por perfil
        profile_adjustments = {
            TradingProfile.CONSERVATIVE: {
                'rsi': {'oversold_threshold': 25, 'overbought_threshold': 75},
                'risk': {'max_position_size': 0.05, 'stop_loss_percentage': 0.015},
                'strategy': {'min_confidence_threshold': 0.7}
            },
            TradingProfile.AGGRESSIVE: {
                'rsi': {'oversold_threshold': 35, 'overbought_threshold': 65},
                'risk': {'max_position_size': 0.15, 'stop_loss_percentage': 0.03},
                'strategy': {'min_confidence_threshold': 0.5}
            },
            TradingProfile.SCALPING: {
                'rsi': {'period': 7},
                'ma': {'short_period': 5, 'medium_period': 10, 'long_period': 20},
                'risk': {'stop_loss_percentage': 0.005, 'take_profit_percentage': 0.01}
            },
            TradingProfile.SWING: {
                'rsi': {'period': 21},
                'ma': {'short_period': 50, 'medium_period': 100, 'long_period': 200},
                'fibonacci': {'lookback_period': 200}
            }
        }
        
        # Aplicar configuraciones base
        self.rsi = base_configs['rsi']
        self.stochastic = base_configs['stochastic']
        self.macd = base_configs['macd']
        self.bollinger = base_configs['bollinger']
        self.ma = base_configs['ma']
        self.fibonacci = base_configs['fibonacci']
        self.ichimoku = base_configs['ichimoku']
        self.volume = base_configs['volume']
        self.risk = base_configs['risk']
        self.strategy = base_configs['strategy']
        
        # Aplicar ajustes específicos del perfil
        if self.profile in profile_adjustments:
            adjustments = profile_adjustments[self.profile]
            
            for config_name, params in adjustments.items():
                config_obj = getattr(self, config_name)
                for param_name, value in params.items():
                    setattr(config_obj, param_name, value)
    
    def get_indicator_params(self, indicator_name: str) -> Dict[str, Any]:
        """
        Obtiene parámetros de un indicador específico como diccionario.
        
        Args:
            indicator_name: Nombre del indicador ('rsi', 'macd', etc.)
            
        Returns:
            Diccionario con los parámetros del indicador
        """
        if hasattr(self, indicator_name):
            config_obj = getattr(self, indicator_name)
            return {
                field.name: getattr(config_obj, field.name)
                for field in config_obj.__dataclass_fields__.values()
            }
        return {}
    
    def update_parameter(self, indicator: str, parameter: str, value: Any):
        """
        Actualiza un parámetro específico de un indicador.
        
        Args:
            indicator: Nombre del indicador
            parameter: Nombre del parámetro
            value: Nuevo valor
        """
        if hasattr(self, indicator):
            config_obj = getattr(self, indicator)
            if hasattr(config_obj, parameter):
                setattr(config_obj, parameter, value)
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Retorna todas las configuraciones como diccionario"""
        return {
            'profile': self.profile.value,
            'rsi': self.get_indicator_params('rsi'),
            'stochastic': self.get_indicator_params('stochastic'),
            'macd': self.get_indicator_params('macd'),
            'bollinger': self.get_indicator_params('bollinger'),
            'ma': self.get_indicator_params('ma'),
            'fibonacci': self.get_indicator_params('fibonacci'),
            'ichimoku': self.get_indicator_params('ichimoku'),
            'volume': self.get_indicator_params('volume'),
            'risk': self.get_indicator_params('risk'),
            'strategy': self.get_indicator_params('strategy')
        }


# Instancia global por defecto
DEFAULT_TECHNICAL_CONFIG = TechnicalConfig()


def get_technical_config(profile: Optional[TradingProfile] = None) -> TechnicalConfig:
    """
    Factory function para obtener configuración técnica.
    
    Args:
        profile: Perfil de trading opcional
        
    Returns:
        Instancia de TechnicalConfig
    """
    if profile is None:
        return DEFAULT_TECHNICAL_CONFIG
    return TechnicalConfig(profile)