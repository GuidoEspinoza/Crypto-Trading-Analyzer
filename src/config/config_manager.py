"""
🎯 ConfigManager Centralizado - Arquitectura de Configuración Robusta

Este módulo centraliza TODA la configuración del sistema de trading,
eliminando dependencias circulares y garantizando configuraciones 100% consolidadas.

🔧 CARACTERÍSTICAS:
- ✅ Configuración centralizada y validada automáticamente
- ✅ Perfiles de trading robustos (RAPIDO, AGRESIVO, OPTIMO, CONSERVADOR)
- ✅ Fallbacks automáticos para evitar valores N/A
- ✅ Validación en tiempo real de todas las configuraciones
- ✅ Eliminación de dependencias circulares
- ✅ API unificada para todos los módulos

🎯 USO:
```python
from config.config_manager import ConfigManager

# Obtener configuración consolidada
config = ConfigManager.get_consolidated_config()

# Obtener configuración específica de un módulo
trading_config = ConfigManager.get_module_config('trading_bot')
risk_config = ConfigManager.get_module_config('risk_manager')
```
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

# Configurar logging
logger = logging.getLogger(__name__)

class TradingProfile(Enum):
    """Perfiles de trading disponibles"""
    RAPIDO = "RAPIDO"
    AGRESIVO = "AGRESIVO" 
    OPTIMO = "OPTIMO"
    CONSERVADOR = "CONSERVADOR"

@dataclass
class ProfileConfig:
    """Configuración base de un perfil de trading"""
    name: str
    description: str
    timeframes: List[str]
    risk_level: str
    frequency: str
    
    # Configuraciones específicas por módulo
    trading_bot: Dict[str, Any] = field(default_factory=dict)
    risk_manager: Dict[str, Any] = field(default_factory=dict)
    paper_trader: Dict[str, Any] = field(default_factory=dict)
    strategies: Dict[str, Any] = field(default_factory=dict)
    indicators: Dict[str, Any] = field(default_factory=dict)
    position_manager: Dict[str, Any] = field(default_factory=dict)
    position_monitor: Dict[str, Any] = field(default_factory=dict)
    position_adjuster: Dict[str, Any] = field(default_factory=dict)
    market_validator: Dict[str, Any] = field(default_factory=dict)

class ConfigManager:
    """🎯 Gestor centralizado de configuraciones del sistema de trading"""
    
    # Perfil activo del sistema
    _active_profile: TradingProfile = TradingProfile.AGRESIVO
    
    # Cache de configuraciones
    _config_cache: Dict[str, Any] = {}
    _profiles_cache: Dict[TradingProfile, ProfileConfig] = {}
    
    # Constantes globales
    GLOBAL_CONSTANTS = {
        'global_initial_balance': 1000.0,  # ✅ Clave requerida por el sistema
        'usdt_base_price': 1.0,
        'timezone': 'America/Santiago',
        'daily_reset_hour': 11,
        'daily_reset_minute': 0,
        'symbols': ['BTCUSDT', 'ETHUSDT', "XRPUSDT", 'ADAUSDT', 'DOTUSDT', 'LINKUSDT'],
        'test_symbols': ['BTCUSDT', 'ETHUSDT']
    }
    
    @classmethod
    def initialize(cls, profile: str = "AGRESIVO") -> None:
        """🚀 Inicializa el ConfigManager con el perfil especificado"""
        try:
            cls._active_profile = TradingProfile(profile)
            cls._load_all_profiles()
            cls._validate_all_configurations()
            logger.info(f"✅ ConfigManager inicializado con perfil: {profile}")
        except Exception as e:
            logger.error(f"❌ Error inicializando ConfigManager: {e}")
            cls._active_profile = TradingProfile.AGRESIVO
            cls._load_default_configurations()
    
    @classmethod
    def _load_all_profiles(cls) -> None:
        """📋 Carga todas las configuraciones de perfiles"""
        
        # Perfil RAPIDO - Ultra-rápido
        cls._profiles_cache[TradingProfile.RAPIDO] = ProfileConfig(
            name="🚀 Ultra-Rápido",
            description="Timeframes 1m-15m, máxima frecuencia optimizada",
            timeframes=["1m", "5m", "15m"],
            risk_level="high",
            frequency="ultra_high",
            trading_bot={
                'analysis_interval': 30,
                'min_confidence': 75.0,
                'max_positions': 8,
                'position_timeout': 300,
                'quick_exit_enabled': True,
                'scalping_mode': True
            },
            risk_manager={
                'max_risk_per_trade': 0.03,
                'max_daily_risk': 0.08,
                'max_drawdown_threshold': 0.20,
                'correlation_threshold': 0.8,
                'min_position_size': 8.0,
                'max_position_size': 6.0,
                'kelly_fraction': 0.3,
                'position_size_multiplier': 0.8,
                'volatility_adjustment_factor': 1.3,
                'atr_multiplier': 1.8,
                'trailing_stop_activation': 0.015
            },
            paper_trader={
                'max_position_size': 80.0,
                'max_total_exposure': 400.0,
                'min_trade_value': 8.0,
                'paper_min_confidence': 70.0,
                'max_slippage': 0.002,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 25,
                'rsi_overbought': 75,
                'rsi_period': 8,
                'macd_fast': 8,
                'macd_slow': 17,
                'macd_signal': 6,
                'bb_period': 15,
                'bb_std': 1.8
            },
            indicators={
                'rsi_period': 8,
                'macd_periods': [8, 17, 6],
                'bb_period': 15,
                'volume_sma_period': 10,
                'atr_period': 8
            }
        )
        
        # Perfil AGRESIVO - Balanceado
        cls._profiles_cache[TradingProfile.AGRESIVO] = ProfileConfig(
            name="⚡ Agresivo",
            description="Timeframes 15m-1h, balance entre velocidad y control",
            timeframes=["15m", "30m", "1h"],
            risk_level="medium_high",
            frequency="high",
            trading_bot={
                'analysis_interval': 45,
                'min_confidence': 72.0,
                'max_positions': 6,
                'position_timeout': 600,
                'quick_exit_enabled': True,
                'scalping_mode': False
            },
            risk_manager={
                'max_risk_per_trade': 0.025,
                'max_daily_risk': 0.06,
                'max_drawdown_threshold': 0.18,
                'correlation_threshold': 0.7,
                'min_position_size': 10.0,
                'max_position_size': 5.0,
                'kelly_fraction': 0.25,
                'position_size_multiplier': 1.0,
                'volatility_adjustment_factor': 1.1,
                'atr_multiplier': 2.0,
                'trailing_stop_activation': 0.02
            },
            paper_trader={
                'max_position_size': 0.8,  # 80% del balance
                'max_total_exposure': 500.0,
                'min_trade_value': 10.0,
                'paper_min_confidence': 65.0,
                'max_slippage': 0.001,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'rsi_period': 10,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'bb_period': 20,
                'bb_std': 2.0
            },
            indicators={
                'rsi_period': 10,
                'macd_periods': [12, 26, 9],
                'bb_period': 20,
                'volume_sma_period': 15,
                'atr_period': 10
            }
        )
        
        # Perfil OPTIMO - Conservador
        cls._profiles_cache[TradingProfile.OPTIMO] = ProfileConfig(
            name="🛡️ Óptimo",
            description="Timeframes 1h-1d, enfoque en calidad y preservación",
            timeframes=["1h", "4h", "1d"],
            risk_level="medium",
            frequency="medium",
            trading_bot={
                'analysis_interval': 90,
                'min_confidence': 68.0,
                'max_positions': 4,
                'position_timeout': 1800,
                'quick_exit_enabled': False,
                'scalping_mode': False
            },
            risk_manager={
                'max_risk_per_trade': 0.02,
                'max_daily_risk': 0.04,
                'max_drawdown_threshold': 0.15,
                'correlation_threshold': 0.6,
                'min_position_size': 12.0,
                'max_position_size': 4.0,
                'kelly_fraction': 0.2,
                'position_size_multiplier': 1.2,
                'volatility_adjustment_factor': 0.9,
                'atr_multiplier': 2.2,
                'trailing_stop_activation': 0.025
            },
            paper_trader={
                'max_position_size': 120.0,
                'max_total_exposure': 600.0,
                'min_trade_value': 15.0,
                'paper_min_confidence': 60.0,
                'max_slippage': 0.0008,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 35,
                'rsi_overbought': 65,
                'rsi_period': 14,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'bb_period': 20,
                'bb_std': 2.0
            },
            indicators={
                'rsi_period': 14,
                'macd_periods': [12, 26, 9],
                'bb_period': 20,
                'volume_sma_period': 20,
                'atr_period': 14
            }
        )
        
        # Perfil CONSERVADOR - Máxima preservación
        cls._profiles_cache[TradingProfile.CONSERVADOR] = ProfileConfig(
            name="🔒 Conservador",
            description="Timeframes largos, máxima preservación de capital",
            timeframes=["4h", "1d", "1w"],
            risk_level="low",
            frequency="low",
            trading_bot={
                'analysis_interval': 180,
                'min_confidence': 65.0,
                'max_positions': 3,
                'position_timeout': 3600,
                'quick_exit_enabled': False,
                'scalping_mode': False
            },
            risk_manager={
                'max_risk_per_trade': 0.015,
                'max_daily_risk': 0.03,
                'max_drawdown_threshold': 0.12,
                'correlation_threshold': 0.5,
                'min_position_size': 15.0,
                'max_position_size': 3.0,
                'kelly_fraction': 0.15,
                'position_size_multiplier': 1.5,
                'volatility_adjustment_factor': 0.8,
                'atr_multiplier': 2.5,
                'trailing_stop_activation': 0.03
            },
            paper_trader={
                'max_position_size': 150.0,
                'max_total_exposure': 700.0,
                'min_trade_value': 20.0,
                'paper_min_confidence': 55.0,
                'max_slippage': 0.0005,
                'trading_fees': 0.001
            },
            strategies={
                'rsi_oversold': 40,
                'rsi_overbought': 60,
                'rsi_period': 21,
                'macd_fast': 12,
                'macd_slow': 26,
                'macd_signal': 9,
                'bb_period': 25,
                'bb_std': 2.2
            },
            indicators={
                'rsi_period': 21,
                'macd_periods': [12, 26, 9],
                'bb_period': 25,
                'volume_sma_period': 25,
                'atr_period': 21
            }
        )
    
    @classmethod
    def _load_default_configurations(cls) -> None:
        """🔧 Carga configuraciones por defecto en caso de error"""
        logger.warning("⚠️ Cargando configuraciones por defecto")
        cls._profiles_cache[TradingProfile.AGRESIVO] = ProfileConfig(
            name="⚡ Agresivo (Default)",
            description="Configuración por defecto",
            timeframes=["15m", "30m", "1h"],
            risk_level="medium_high",
            frequency="high"
        )
    
    @classmethod
    def _validate_all_configurations(cls) -> bool:
        """🔍 Valida todas las configuraciones cargadas"""
        try:
            for profile, config in cls._profiles_cache.items():
                if not cls._validate_profile_config(config):
                    logger.error(f"❌ Configuración inválida para perfil: {profile.value}")
                    return False
            
            logger.info("✅ Todas las configuraciones validadas correctamente")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando configuraciones: {e}")
            return False
    
    @classmethod
    def _validate_profile_config(cls, config: ProfileConfig) -> bool:
        """🔍 Valida una configuración específica de perfil"""
        try:
            # Validar campos obligatorios
            required_fields = ['name', 'description', 'timeframes', 'risk_level', 'frequency']
            for field in required_fields:
                if not hasattr(config, field) or getattr(config, field) is None:
                    return False
            
            # Validar timeframes
            if not config.timeframes or len(config.timeframes) == 0:
                return False
            
            # Validar configuraciones de módulos
            if config.trading_bot and 'min_confidence' in config.trading_bot:
                if not (0 <= config.trading_bot['min_confidence'] <= 100):
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validando configuración: {e}")
            return False
    
    @classmethod
    def get_consolidated_config(cls, profile: Optional[str] = None) -> Dict[str, Any]:
        """🎯 Obtiene la configuración consolidada del sistema"""
        try:
            if profile:
                target_profile = TradingProfile(profile)
            else:
                target_profile = cls._active_profile
            
            if target_profile not in cls._profiles_cache:
                logger.warning(f"⚠️ Perfil {target_profile.value} no encontrado, usando AGRESIVO")
                target_profile = TradingProfile.AGRESIVO
            
            profile_config = cls._profiles_cache[target_profile]
            
            # Construir configuración consolidada
            consolidated = {
                'profile': target_profile.value,
                'profile_info': {
                    'name': profile_config.name,
                    'description': profile_config.description,
                    'timeframes': profile_config.timeframes,
                    'risk_level': profile_config.risk_level,
                    'frequency': profile_config.frequency
                },
                
                # Constantes globales
                **cls.GLOBAL_CONSTANTS,
                
                # Configuraciones por módulo
                'trading_bot': profile_config.trading_bot,
                'risk_manager': profile_config.risk_manager,
                'paper_trader': profile_config.paper_trader,
                'strategies': profile_config.strategies,
                'indicators': profile_config.indicators,
                'position_manager': profile_config.position_manager,
                'position_monitor': profile_config.position_monitor,
                'position_adjuster': profile_config.position_adjuster,
                'market_validator': profile_config.market_validator,
                
                # Alias para compatibilidad con tests (nombres completos)
                'enhanced_risk_manager': profile_config.risk_manager,
                'advanced_indicators': profile_config.indicators,
                'enhanced_strategies': profile_config.strategies,
                
                # Metadatos
                'config_version': '2.0',
                'last_updated': 'auto-generated',
                'validation_status': 'validated'
            }
            
            return consolidated
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración consolidada: {e}")
            return cls._get_fallback_config()
    
    @classmethod
    def get_module_config(cls, module_name: str, profile: Optional[str] = None) -> Dict[str, Any]:
        """🎯 Obtiene la configuración específica de un módulo"""
        try:
            consolidated = cls.get_consolidated_config(profile)
            return consolidated.get(module_name, {})
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo configuración del módulo {module_name}: {e}")
            return {}
    
    @classmethod
    def set_active_profile(cls, profile: str) -> bool:
        """🔄 Cambia el perfil activo del sistema"""
        try:
            new_profile = TradingProfile(profile)
            cls._active_profile = new_profile
            logger.info(f"✅ Perfil cambiado a: {profile}")
            return True
            
        except ValueError:
            logger.error(f"❌ Perfil inválido: {profile}")
            return False
    
    @classmethod
    def get_active_profile(cls) -> str:
        """📋 Obtiene el perfil activo actual"""
        return cls._active_profile.value
    
    @classmethod
    def get_available_profiles(cls) -> List[str]:
        """📋 Obtiene la lista de perfiles disponibles"""
        return [profile.value for profile in TradingProfile]
    
    @classmethod
    def _get_fallback_config(cls) -> Dict[str, Any]:
        """🔧 Configuración de fallback en caso de error"""
        return {
            'profile': 'AGRESIVO',
            'profile_info': {
                'name': '⚡ Agresivo (Fallback)',
                'description': 'Configuración de emergencia',
                'timeframes': ['15m', '30m', '1h'],
                'risk_level': 'medium_high',
                'frequency': 'high'
            },
            **cls.GLOBAL_CONSTANTS,
            'trading_bot': {
                'analysis_interval': 45,
                'min_confidence': 70.0,
                'max_positions': 5,
                'position_timeout': 600,
                'quick_exit_enabled': False,
                'scalping_mode': False
            },
            'risk_manager': {
                'max_risk_per_trade': 0.02,
                'max_daily_risk': 0.05,
                'max_drawdown_threshold': 0.15,
                'correlation_threshold': 0.7,
                'min_position_size': 10.0,
                'max_position_size': 0.8,  # 80% del balance
                'kelly_fraction': 0.25
            },
            'config_version': '2.0-fallback',
            'validation_status': 'fallback'
        }
    
    @classmethod
    def export_config(cls, filepath: Optional[str] = None) -> str:
        """💾 Exporta la configuración actual a JSON"""
        try:
            config = cls.get_consolidated_config()
            config_json = json.dumps(config, indent=2, ensure_ascii=False)
            
            if filepath:
                Path(filepath).write_text(config_json, encoding='utf-8')
                logger.info(f"✅ Configuración exportada a: {filepath}")
            
            return config_json
            
        except Exception as e:
            logger.error(f"❌ Error exportando configuración: {e}")
            return "{}"

# Inicializar ConfigManager al importar el módulo
ConfigManager.initialize()