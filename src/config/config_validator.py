"""
Validador centralizado para configuraciones técnicas.
Garantiza que todas las configuraciones sean válidas y seguras.
"""

from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import fields
import warnings

from .technical_config import TechnicalConfig, TradingProfile


class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass


class ValidationWarning(UserWarning):
    """Warning para configuraciones subóptimas"""
    pass


class ConfigValidator:
    """
    Validador centralizado para configuraciones técnicas.
    Valida rangos, relaciones entre parámetros y coherencia general.
    """
    
    def __init__(self):
        self._validation_rules = self._load_validation_rules()
    
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """
        Define reglas de validación para cada indicador.
        
        Returns:
            Diccionario con reglas de validación
        """
        return {
            'rsi': {
                'period': {'min': 2, 'max': 100, 'type': int},
                'oversold_threshold': {'min': 0, 'max': 50, 'type': (int, float)},
                'overbought_threshold': {'min': 50, 'max': 100, 'type': (int, float)},
                'extreme_oversold': {'min': 0, 'max': 30, 'type': (int, float)},
                'extreme_overbought': {'min': 70, 'max': 100, 'type': (int, float)},
                'relationships': [
                    ('extreme_oversold', '<', 'oversold_threshold'),
                    ('oversold_threshold', '<', 'overbought_threshold'),
                    ('overbought_threshold', '<', 'extreme_overbought')
                ]
            },
            'stochastic': {
                'k_period': {'min': 1, 'max': 50, 'type': int},
                'd_period': {'min': 1, 'max': 20, 'type': int},
                'smooth_k': {'min': 1, 'max': 10, 'type': int},
                'oversold_threshold': {'min': 0, 'max': 50, 'type': (int, float)},
                'overbought_threshold': {'min': 50, 'max': 100, 'type': (int, float)},
                'relationships': [
                    ('oversold_threshold', '<', 'overbought_threshold')
                ]
            },
            'macd': {
                'fast_period': {'min': 1, 'max': 50, 'type': int},
                'slow_period': {'min': 1, 'max': 200, 'type': int},
                'signal_period': {'min': 1, 'max': 50, 'type': int},
                'relationships': [
                    ('fast_period', '<', 'slow_period')
                ]
            },
            'bollinger': {
                'period': {'min': 2, 'max': 100, 'type': int},
                'std_dev': {'min': 0.1, 'max': 5.0, 'type': (int, float)},
                'squeeze_threshold': {'min': 0.01, 'max': 1.0, 'type': (int, float)}
            },
            'ma': {
                'short_period': {'min': 1, 'max': 100, 'type': int},
                'medium_period': {'min': 1, 'max': 200, 'type': int},
                'long_period': {'min': 1, 'max': 500, 'type': int},
                'ema_alpha': {'min': 0.01, 'max': 1.0, 'type': (int, float)},
                'relationships': [
                    ('short_period', '<', 'medium_period'),
                    ('medium_period', '<', 'long_period')
                ]
            },
            'fibonacci': {
                'lookback_period': {'min': 10, 'max': 1000, 'type': int}
            },
            'ichimoku': {
                'tenkan_period': {'min': 1, 'max': 50, 'type': int},
                'kijun_period': {'min': 1, 'max': 100, 'type': int},
                'senkou_span_b_period': {'min': 1, 'max': 200, 'type': int},
                'displacement': {'min': 1, 'max': 100, 'type': int},
                'relationships': [
                    ('tenkan_period', '<', 'kijun_period'),
                    ('kijun_period', '<', 'senkou_span_b_period')
                ]
            },
            'volume': {
                'sma_period': {'min': 1, 'max': 100, 'type': int},
                'volume_spike_threshold': {'min': 1.1, 'max': 10.0, 'type': (int, float)},
                'volume_dry_threshold': {'min': 0.1, 'max': 0.9, 'type': (int, float)}
            },
            'risk': {
                'max_position_size': {'min': 0.001, 'max': 1.0, 'type': (int, float)},
                'stop_loss_percentage': {'min': 0.001, 'max': 0.5, 'type': (int, float)},
                'take_profit_percentage': {'min': 0.001, 'max': 1.0, 'type': (int, float)},
                'max_drawdown_threshold': {'min': 0.01, 'max': 0.5, 'type': (int, float)},
                'risk_reward_ratio': {'min': 0.5, 'max': 10.0, 'type': (int, float)},
                'relationships': [
                    ('stop_loss_percentage', '<', 'take_profit_percentage')
                ]
            },
            'strategy': {
                'base_confidence': {'min': 0.0, 'max': 1.0, 'type': (int, float)},
                'hold_confidence': {'min': 0.0, 'max': 1.0, 'type': (int, float)},
                'min_confidence_threshold': {'min': 0.0, 'max': 1.0, 'type': (int, float)},
                'max_confidence_threshold': {'min': 0.0, 'max': 1.0, 'type': (int, float)},
                'signal_decay_factor': {'min': 0.1, 'max': 1.0, 'type': (int, float)},
                'relationships': [
                    ('min_confidence_threshold', '<', 'max_confidence_threshold')
                ]
            }
        }
    
    def validate_config(self, config: TechnicalConfig, strict: bool = True) -> Tuple[bool, List[str], List[str]]:
        """
        Valida una configuración técnica completa.
        
        Args:
            config: Configuración a validar
            strict: Si True, lanza excepción en errores críticos
            
        Returns:
            Tupla (es_válido, errores, warnings)
        """
        errors = []
        warnings_list = []
        
        # Validar cada indicador
        for indicator_name in self._validation_rules.keys():
            if hasattr(config, indicator_name):
                indicator_config = getattr(config, indicator_name)
                indicator_errors, indicator_warnings = self._validate_indicator(
                    indicator_name, indicator_config
                )
                errors.extend(indicator_errors)
                warnings_list.extend(indicator_warnings)
        
        # Validaciones cruzadas
        cross_errors, cross_warnings = self._validate_cross_relationships(config)
        errors.extend(cross_errors)
        warnings_list.extend(cross_warnings)
        
        # Validaciones de perfil
        profile_warnings = self._validate_profile_coherence(config)
        warnings_list.extend(profile_warnings)
        
        is_valid = len(errors) == 0
        
        if strict and not is_valid:
            raise ValidationError(f"Configuración inválida: {'; '.join(errors)}")
        
        # Emitir warnings
        for warning_msg in warnings_list:
            warnings.warn(warning_msg, ValidationWarning)
        
        return is_valid, errors, warnings_list
    
    def _validate_indicator(self, indicator_name: str, indicator_config: Any) -> Tuple[List[str], List[str]]:
        """
        Valida un indicador específico.
        
        Args:
            indicator_name: Nombre del indicador
            indicator_config: Configuración del indicador
            
        Returns:
            Tupla (errores, warnings)
        """
        errors = []
        warnings_list = []
        
        if indicator_name not in self._validation_rules:
            return errors, warnings_list
        
        rules = self._validation_rules[indicator_name]
        
        # Validar cada parámetro
        for field in fields(indicator_config):
            param_name = field.name
            param_value = getattr(indicator_config, param_name)
            
            if param_name in rules:
                param_rules = rules[param_name]
                
                # Validar tipo
                if 'type' in param_rules:
                    expected_type = param_rules['type']
                    if not isinstance(param_value, expected_type):
                        errors.append(
                            f"{indicator_name}.{param_name}: Tipo inválido. "
                            f"Esperado {expected_type}, obtenido {type(param_value)}"
                        )
                        continue
                
                # Validar rango
                if 'min' in param_rules and param_value < param_rules['min']:
                    errors.append(
                        f"{indicator_name}.{param_name}: Valor {param_value} menor que mínimo {param_rules['min']}"
                    )
                
                if 'max' in param_rules and param_value > param_rules['max']:
                    errors.append(
                        f"{indicator_name}.{param_name}: Valor {param_value} mayor que máximo {param_rules['max']}"
                    )
                
                # Warnings para valores subóptimos
                if 'optimal_range' in param_rules:
                    opt_min, opt_max = param_rules['optimal_range']
                    if not (opt_min <= param_value <= opt_max):
                        warnings_list.append(
                            f"{indicator_name}.{param_name}: Valor {param_value} fuera del rango óptimo [{opt_min}, {opt_max}]"
                        )
        
        # Validar relaciones entre parámetros
        if 'relationships' in rules:
            for relationship in rules['relationships']:
                param1, operator, param2 = relationship
                
                if hasattr(indicator_config, param1) and hasattr(indicator_config, param2):
                    value1 = getattr(indicator_config, param1)
                    value2 = getattr(indicator_config, param2)
                    
                    if operator == '<' and not (value1 < value2):
                        errors.append(
                            f"{indicator_name}: {param1} ({value1}) debe ser menor que {param2} ({value2})"
                        )
                    elif operator == '>' and not (value1 > value2):
                        errors.append(
                            f"{indicator_name}: {param1} ({value1}) debe ser mayor que {param2} ({value2})"
                        )
                    elif operator == '<=' and not (value1 <= value2):
                        errors.append(
                            f"{indicator_name}: {param1} ({value1}) debe ser menor o igual que {param2} ({value2})"
                        )
                    elif operator == '>=' and not (value1 >= value2):
                        errors.append(
                            f"{indicator_name}: {param1} ({value1}) debe ser mayor o igual que {param2} ({value2})"
                        )
        
        return errors, warnings_list
    
    def _validate_cross_relationships(self, config: TechnicalConfig) -> Tuple[List[str], List[str]]:
        """
        Valida relaciones entre diferentes indicadores.
        
        Args:
            config: Configuración completa
            
        Returns:
            Tupla (errores, warnings)
        """
        errors = []
        warnings_list = []
        
        # Validar coherencia entre RSI y Stochastic
        if hasattr(config, 'rsi') and hasattr(config, 'stochastic'):
            rsi_oversold = config.rsi.oversold_threshold
            stoch_oversold = config.stochastic.oversold_threshold
            
            if abs(rsi_oversold - stoch_oversold) > 20:
                warnings_list.append(
                    f"RSI oversold ({rsi_oversold}) y Stochastic oversold ({stoch_oversold}) "
                    "tienen valores muy diferentes"
                )
        
        # Validar coherencia entre medias móviles y otros indicadores
        if hasattr(config, 'ma') and hasattr(config, 'bollinger'):
            if config.ma.short_period > config.bollinger.period:
                warnings_list.append(
                    f"Período de MA corta ({config.ma.short_period}) mayor que "
                    f"período de Bollinger ({config.bollinger.period})"
                )
        
        # Validar coherencia de risk management
        if hasattr(config, 'risk'):
            risk_reward = config.risk.take_profit_percentage / config.risk.stop_loss_percentage
            if risk_reward < 1.5:
                warnings_list.append(
                    f"Risk/Reward ratio ({risk_reward:.2f}) es menor que 1.5, "
                    "considerado subóptimo"
                )
        
        return errors, warnings_list
    
    def _validate_profile_coherence(self, config: TechnicalConfig) -> List[str]:
        """
        Valida coherencia con el perfil de trading.
        
        Args:
            config: Configuración a validar
            
        Returns:
            Lista de warnings
        """
        warnings_list = []
        
        profile = config.profile
        
        # Validaciones específicas por perfil
        if profile == TradingProfile.CONSERVADOR:
            if hasattr(config, 'risk') and config.risk.max_position_size > 0.1:
                warnings_list.append(
                    f"Perfil conservador con posición máxima alta ({config.risk.max_position_size})"
                )
        
        elif profile == TradingProfile.AGRESIVO:
            if hasattr(config, 'risk') and config.risk.max_position_size < 0.05:
                warnings_list.append(
                    f"Perfil agresivo con posición máxima baja ({config.risk.max_position_size})"
                )
        
        elif profile == TradingProfile.OPTIMO:
            if hasattr(config, 'strategy') and config.strategy.min_confidence_threshold < 0.5:
                warnings_list.append(
                    f"Perfil óptimo con umbral de confianza muy bajo ({config.strategy.min_confidence_threshold})"
                )
        
        return warnings_list
    
    def validate_parameter_update(self, 
                                indicator: str, 
                                parameter: str, 
                                new_value: Any,
                                current_config: TechnicalConfig) -> Tuple[bool, List[str]]:
        """
        Valida una actualización específica de parámetro.
        
        Args:
            indicator: Nombre del indicador
            parameter: Nombre del parámetro
            new_value: Nuevo valor
            current_config: Configuración actual
            
        Returns:
            Tupla (es_válido, errores)
        """
        errors = []
        
        if indicator not in self._validation_rules:
            errors.append(f"Indicador '{indicator}' no reconocido")
            return False, errors
        
        rules = self._validation_rules[indicator]
        
        if parameter not in rules:
            errors.append(f"Parámetro '{parameter}' no reconocido para {indicator}")
            return False, errors
        
        param_rules = rules[parameter]
        
        # Validar tipo
        if 'type' in param_rules:
            expected_type = param_rules['type']
            if not isinstance(new_value, expected_type):
                errors.append(
                    f"Tipo inválido para {indicator}.{parameter}. "
                    f"Esperado {expected_type}, obtenido {type(new_value)}"
                )
                return False, errors
        
        # Validar rango
        if 'min' in param_rules and new_value < param_rules['min']:
            errors.append(
                f"Valor {new_value} menor que mínimo {param_rules['min']} "
                f"para {indicator}.{parameter}"
            )
        
        if 'max' in param_rules and new_value > param_rules['max']:
            errors.append(
                f"Valor {new_value} mayor que máximo {param_rules['max']} "
                f"para {indicator}.{parameter}"
            )
        
        return len(errors) == 0, errors
    
    def suggest_optimal_values(self, indicator: str, profile: TradingProfile) -> Dict[str, Any]:
        """
        Sugiere valores óptimos para un indicador según el perfil.
        
        Args:
            indicator: Nombre del indicador
            profile: Perfil de trading
            
        Returns:
            Diccionario con valores sugeridos
        """
        suggestions = {}
        
        # Sugerencias específicas por perfil e indicador
        profile_suggestions = {
            TradingProfile.CONSERVADOR: {
                'rsi': {'period': 21, 'oversold_threshold': 25, 'overbought_threshold': 75},
                'risk': {'max_position_size': 0.05, 'stop_loss_percentage': 0.015}
            },
            TradingProfile.OPTIMO: {
                'rsi': {'period': 14, 'oversold_threshold': 30, 'overbought_threshold': 70},
                'risk': {'max_position_size': 0.10, 'stop_loss_percentage': 0.02}
            },
            TradingProfile.AGRESIVO: {
                'rsi': {'period': 10, 'oversold_threshold': 35, 'overbought_threshold': 65},
                'risk': {'max_position_size': 0.15, 'stop_loss_percentage': 0.03}
            }
        }
        
        if profile in profile_suggestions and indicator in profile_suggestions[profile]:
            suggestions = profile_suggestions[profile][indicator]
        
        return suggestions


# Instancia global del validador
config_validator = ConfigValidator()


def validate_config(config: TechnicalConfig, strict: bool = True) -> Tuple[bool, List[str], List[str]]:
    """
    Función de conveniencia para validar configuraciones.
    
    Args:
        config: Configuración a validar
        strict: Si True, lanza excepción en errores
        
    Returns:
        Tupla (es_válido, errores, warnings)
    """
    return config_validator.validate_config(config, strict)