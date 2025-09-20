"""
Factory pattern para configuraciones técnicas.
Proporciona una interfaz unificada para crear y gestionar configuraciones.
"""

import os
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import asdict

from .technical_config import TechnicalConfig, TradingProfile
from .config_manager import ConfigManager


class ConfigFactory:
    """
    Factory para crear y gestionar configuraciones técnicas de manera centralizada.
    Implementa el patrón Singleton para garantizar consistencia global.
    """
    
    _instance = None
    _configs_cache: Dict[str, TechnicalConfig] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.config_manager = ConfigManager()
            self._load_default_configs()
            self._initialized = True
    
    def _load_default_configs(self):
        """Carga configuraciones por defecto para todos los perfiles"""
        for profile in TradingProfile:
            profile_key = f"technical_{profile.value}"
            if profile_key not in self._configs_cache:
                self._configs_cache[profile_key] = TechnicalConfig(profile)
    
    def get_config(self, 
                   profile: Union[str, TradingProfile] = TradingProfile.MODERATE,
                   symbol: Optional[str] = None,
                   custom_params: Optional[Dict[str, Any]] = None) -> TechnicalConfig:
        """
        Obtiene configuración técnica optimizada para el contexto específico.
        
        Args:
            profile: Perfil de trading
            symbol: Símbolo específico (para optimizaciones futuras)
            custom_params: Parámetros personalizados a aplicar
            
        Returns:
            Configuración técnica optimizada
        """
        # Normalizar perfil
        if isinstance(profile, str):
            try:
                profile = TradingProfile(profile.lower())
            except ValueError:
                profile = TradingProfile.MODERATE
        
        # Crear clave de caché
        cache_key = f"technical_{profile.value}"
        if symbol:
            cache_key += f"_{symbol}"
        
        # Verificar caché
        if cache_key in self._configs_cache and not custom_params:
            return self._configs_cache[cache_key]
        
        # Crear nueva configuración
        config = TechnicalConfig(profile)
        
        # Aplicar parámetros personalizados
        if custom_params:
            config = self._apply_custom_params(config, custom_params)
        
        # Aplicar optimizaciones específicas del símbolo
        if symbol:
            config = self._apply_symbol_optimizations(config, symbol)
        
        # Guardar en caché
        self._configs_cache[cache_key] = config
        
        return config
    
    def _apply_custom_params(self, config: TechnicalConfig, custom_params: Dict[str, Any]) -> TechnicalConfig:
        """
        Aplica parámetros personalizados a la configuración.
        
        Args:
            config: Configuración base
            custom_params: Parámetros a aplicar
            
        Returns:
            Configuración modificada
        """
        for indicator, params in custom_params.items():
            if hasattr(config, indicator) and isinstance(params, dict):
                for param_name, value in params.items():
                    config.update_parameter(indicator, param_name, value)
        
        return config
    
    def _apply_symbol_optimizations(self, config: TechnicalConfig, symbol: str) -> TechnicalConfig:
        """
        Aplica optimizaciones específicas del símbolo.
        
        Args:
            config: Configuración base
            symbol: Símbolo a optimizar
            
        Returns:
            Configuración optimizada
        """
        # Optimizaciones por tipo de activo
        symbol_upper = symbol.upper()
        
        # Bitcoin y criptomonedas principales
        if symbol_upper in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
            # Ajustar para mayor volatilidad
            config.update_parameter('bollinger', 'std_dev', 2.5)
            config.update_parameter('risk', 'stop_loss_percentage', 0.025)
        
        # Altcoins (mayor volatilidad)
        elif 'USDT' in symbol_upper and symbol_upper not in ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']:
            config.update_parameter('bollinger', 'std_dev', 3.0)
            config.update_parameter('risk', 'stop_loss_percentage', 0.03)
            config.update_parameter('rsi', 'oversold_threshold', 25)
            config.update_parameter('rsi', 'overbought_threshold', 75)
        
        return config
    
    def create_custom_config(self, 
                           base_profile: Union[str, TradingProfile] = TradingProfile.MODERATE,
                           **kwargs) -> TechnicalConfig:
        """
        Crea configuración personalizada con parámetros específicos.
        
        Args:
            base_profile: Perfil base
            **kwargs: Parámetros específicos por indicador
            
        Returns:
            Configuración personalizada
        """
        config = self.get_config(base_profile)
        
        # Aplicar parámetros específicos
        for key, value in kwargs.items():
            if '.' in key:
                # Formato: 'rsi.period' = 21
                indicator, param = key.split('.', 1)
                config.update_parameter(indicator, param, value)
        
        return config
    
    def save_config_preset(self, name: str, config: TechnicalConfig, description: str = ""):
        """
        Guarda un preset de configuración para reutilización.
        
        Args:
            name: Nombre del preset
            config: Configuración a guardar
            description: Descripción del preset
        """
        preset_data = {
            'name': name,
            'description': description,
            'profile': config.profile.value,
            'config': config.get_all_configs(),
            'created_at': self._get_timestamp()
        }
        
        presets_file = Path(self.config_manager.config_dir) / 'config_presets.json'
        
        # Cargar presets existentes
        presets = {}
        if presets_file.exists():
            try:
                with open(presets_file, 'r') as f:
                    presets = json.load(f)
            except (json.JSONDecodeError, IOError):
                presets = {}
        
        # Agregar nuevo preset
        presets[name] = preset_data
        
        # Guardar
        try:
            with open(presets_file, 'w') as f:
                json.dump(presets, f, indent=2)
        except IOError as e:
            print(f"Error guardando preset: {e}")
    
    def load_config_preset(self, name: str) -> Optional[TechnicalConfig]:
        """
        Carga un preset de configuración guardado.
        
        Args:
            name: Nombre del preset
            
        Returns:
            Configuración cargada o None si no existe
        """
        presets_file = Path(self.config_manager.config_dir) / 'config_presets.json'
        
        if not presets_file.exists():
            return None
        
        try:
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            if name not in presets:
                return None
            
            preset_data = presets[name]
            profile = TradingProfile(preset_data['profile'])
            config = TechnicalConfig(profile)
            
            # Aplicar configuraciones guardadas
            saved_config = preset_data['config']
            for indicator, params in saved_config.items():
                if indicator != 'profile' and isinstance(params, dict):
                    for param_name, value in params.items():
                        config.update_parameter(indicator, param_name, value)
            
            return config
            
        except (json.JSONDecodeError, IOError, KeyError, ValueError):
            return None
    
    def list_presets(self) -> Dict[str, Dict[str, Any]]:
        """
        Lista todos los presets disponibles.
        
        Returns:
            Diccionario con información de presets
        """
        presets_file = Path(self.config_manager.config_dir) / 'config_presets.json'
        
        if not presets_file.exists():
            return {}
        
        try:
            with open(presets_file, 'r') as f:
                presets = json.load(f)
            
            # Retornar solo metadatos
            return {
                name: {
                    'description': data.get('description', ''),
                    'profile': data.get('profile', ''),
                    'created_at': data.get('created_at', '')
                }
                for name, data in presets.items()
            }
            
        except (json.JSONDecodeError, IOError):
            return {}
    
    def optimize_for_market_conditions(self, 
                                     config: TechnicalConfig,
                                     volatility: str = "normal",
                                     trend: str = "neutral") -> TechnicalConfig:
        """
        Optimiza configuración según condiciones de mercado.
        
        Args:
            config: Configuración base
            volatility: "low", "normal", "high"
            trend: "bullish", "bearish", "neutral"
            
        Returns:
            Configuración optimizada
        """
        # Ajustes por volatilidad
        if volatility == "high":
            config.update_parameter('bollinger', 'std_dev', 2.5)
            config.update_parameter('risk', 'stop_loss_percentage', 0.03)
            config.update_parameter('rsi', 'period', 10)  # Más reactivo
        elif volatility == "low":
            config.update_parameter('bollinger', 'std_dev', 1.5)
            config.update_parameter('risk', 'stop_loss_percentage', 0.015)
            config.update_parameter('rsi', 'period', 21)  # Menos reactivo
        
        # Ajustes por tendencia
        if trend == "bullish":
            config.update_parameter('rsi', 'oversold_threshold', 35)
            config.update_parameter('strategy', 'min_confidence_threshold', 0.55)
        elif trend == "bearish":
            config.update_parameter('rsi', 'overbought_threshold', 65)
            config.update_parameter('strategy', 'min_confidence_threshold', 0.65)
        
        return config
    
    def _get_timestamp(self) -> str:
        """Obtiene timestamp actual"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def clear_cache(self):
        """Limpia la caché de configuraciones"""
        self._configs_cache.clear()
        self._load_default_configs()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Obtiene información de la caché"""
        return {
            'cached_configs': list(self._configs_cache.keys()),
            'cache_size': len(self._configs_cache)
        }


# Instancia global del factory
config_factory = ConfigFactory()


def get_config_factory() -> ConfigFactory:
    """Obtiene la instancia global del ConfigFactory"""
    return config_factory