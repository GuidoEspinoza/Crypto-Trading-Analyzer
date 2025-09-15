#!/usr/bin/env python3
"""
🛡️ Sistema de Manejo de Errores Avanzado
Decorador y utilidades para manejo robusto de errores en trading
"""

import logging
import traceback
import functools
from typing import Any, Callable, Dict, Optional, Union
from datetime import datetime
import pandas as pd
import numpy as np

# Configurar logger específico para errores
error_logger = logging.getLogger('trading_errors')
error_logger.setLevel(logging.ERROR)

class TradingError(Exception):
    """
    🚨 Excepción base para errores de trading
    """
    def __init__(self, message: str, error_code: str = None, context: Dict = None):
        self.message = message
        self.error_code = error_code or 'TRADING_ERROR'
        self.context = context or {}
        self.timestamp = datetime.now()
        super().__init__(self.message)

class IndicatorError(TradingError):
    """
    📊 Error específico de cálculo de indicadores
    """
    def __init__(self, message: str, indicator_name: str = None, **kwargs):
        super().__init__(message, 'INDICATOR_ERROR', {'indicator': indicator_name, **kwargs})

class DataError(TradingError):
    """
    📈 Error relacionado con datos de mercado
    """
    def __init__(self, message: str, symbol: str = None, timeframe: str = None, **kwargs):
        super().__init__(message, 'DATA_ERROR', {'symbol': symbol, 'timeframe': timeframe, **kwargs})

def handle_errors(default_return: Any = None, 
                 log_errors: bool = True,
                 raise_on_critical: bool = False,
                 error_context: Dict = None):
    """
    🛡️ Decorador para manejo robusto de errores
    
    Args:
        default_return: Valor por defecto a retornar en caso de error
        log_errors: Si registrar errores en el log
        raise_on_critical: Si re-lanzar errores críticos
        error_context: Contexto adicional para el error
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except (KeyboardInterrupt, SystemExit) as e:
                # Errores críticos del sistema - siempre re-lanzar
                if log_errors:
                    error_logger.critical(f"Critical system error in {func.__name__}: {str(e)}")
                raise
            
            except (IndicatorError, DataError, TradingError) as e:
                # Errores específicos de trading
                if log_errors:
                    error_logger.error(
                        f"Trading error in {func.__name__}: {e.message}",
                        extra={
                            'error_code': e.error_code,
                            'context': e.context,
                            'function': func.__name__,
                            'timestamp': e.timestamp.isoformat()
                        }
                    )
                
                if raise_on_critical:
                    raise
                
                return _get_safe_default_return(default_return, func.__name__)
            
            except Exception as e:
                # Errores generales
                error_info = {
                    'function': func.__name__,
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                    'traceback': traceback.format_exc(),
                    'args': str(args)[:200],  # Limitar tamaño
                    'kwargs': str(kwargs)[:200],
                    'timestamp': datetime.now().isoformat()
                }
                
                if error_context:
                    error_info.update(error_context)
                
                if log_errors:
                    error_logger.error(
                        f"Unexpected error in {func.__name__}: {str(e)}",
                        extra=error_info
                    )
                
                if raise_on_critical and _is_critical_error(e):
                    raise
                
                return _get_safe_default_return(default_return, func.__name__)
        
        return wrapper
    return decorator

def _is_critical_error(error: Exception) -> bool:
    """
    🔍 Determinar si un error es crítico
    """
    critical_errors = (
        MemoryError,
        SystemError,
        OSError,
        ImportError,
        AttributeError  # Puede indicar problemas de configuración
    )
    
    return isinstance(error, critical_errors)

def _get_safe_default_return(default_return: Any, function_name: str) -> Any:
    """
    🔒 Obtener valor de retorno seguro basado en el tipo esperado
    """
    if default_return is not None:
        return default_return
    
    # Valores por defecto inteligentes basados en el nombre de la función
    if 'indicator' in function_name.lower() or 'calculate' in function_name.lower():
        return {
            'value': 0.0,
            'signal': 'HOLD',
            'confidence': 0.0,
            'interpretation': f'Error in {function_name} - using safe defaults',
            'error': True
        }
    
    if 'fibonacci' in function_name.lower():
        return {
            'level_0': 0.0,
            'level_236': 0.0,
            'level_382': 0.0,
            'level_500': 0.0,
            'level_618': 0.0,
            'level_786': 0.0,
            'level_100': 0.0
        }
    
    if 'ichimoku' in function_name.lower():
        return {
            'tenkan_sen': 0.0,
            'kijun_sen': 0.0,
            'senkou_span_a': 0.0,
            'senkou_span_b': 0.0,
            'chikou_span': 0.0,
            'cloud_color': 'NEUTRAL',
            'price_position': 'UNKNOWN'
        }
    
    # Valor por defecto genérico
    return None

def safe_dataframe_operation(df: pd.DataFrame, operation: str) -> bool:
    """
    🛡️ Verificar si un DataFrame es seguro para operaciones
    """
    if df is None or df.empty:
        raise DataError(f"DataFrame is None or empty for operation: {operation}")
    
    required_columns = ['open', 'high', 'low', 'close']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise DataError(
            f"Missing required columns for {operation}: {missing_columns}",
            missing_columns=missing_columns
        )
    
    # Verificar datos válidos
    if df[required_columns].isnull().any().any():
        raise DataError(f"DataFrame contains null values for operation: {operation}")
    
    if len(df) < 2:
        raise DataError(f"Insufficient data points for operation: {operation} (need at least 2, got {len(df)})")
    
    return True

def validate_numeric_input(value: Any, name: str, min_val: float = None, max_val: float = None) -> float:
    """
    🔢 Validar entrada numérica
    """
    try:
        numeric_value = float(value)
        
        if pd.isna(numeric_value) or not np.isfinite(numeric_value):
            raise ValueError(f"Invalid numeric value for {name}: {value}")
        
        if min_val is not None and numeric_value < min_val:
            raise ValueError(f"{name} must be >= {min_val}, got {numeric_value}")
        
        if max_val is not None and numeric_value > max_val:
            raise ValueError(f"{name} must be <= {max_val}, got {numeric_value}")
        
        return numeric_value
    
    except (ValueError, TypeError) as e:
        raise IndicatorError(f"Invalid input for {name}: {str(e)}")

def log_performance_warning(func_name: str, execution_time: float, threshold: float = 1.0):
    """
    ⚡ Registrar advertencias de rendimiento
    """
    if execution_time > threshold:
        error_logger.warning(
            f"Performance warning: {func_name} took {execution_time:.2f}s (threshold: {threshold}s)",
            extra={
                'function': func_name,
                'execution_time': execution_time,
                'threshold': threshold,
                'performance_issue': True
            }
        )

def create_error_context(symbol: str = None, timeframe: str = None, **kwargs) -> Dict:
    """
    📝 Crear contexto de error estandarizado
    """
    context = {
        'timestamp': datetime.now().isoformat()
    }
    
    if symbol:
        context['symbol'] = symbol
    if timeframe:
        context['timeframe'] = timeframe
    
    context.update(kwargs)
    return context

# Decorador específico para indicadores
def indicator_error_handler(indicator_name: str):
    """
    📊 Decorador específico para funciones de indicadores
    """
    return handle_errors(
        default_return={
            'value': 0.0,
            'signal': 'HOLD',
            'confidence': 0.0,
            'interpretation': f'Error calculating {indicator_name}',
            'error': True
        },
        error_context={'indicator': indicator_name}
    )

# Decorador para operaciones de datos
def data_error_handler(operation: str):
    """
    📈 Decorador específico para operaciones de datos
    """
    return handle_errors(
        default_return=None,
        error_context={'operation': operation}
    )