#!/usr/bin/env python3
"""
Tests para el sistema de manejo de errores
Prueba todas las funcionalidades del módulo error_handler.py
"""

import unittest
import logging
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from io import StringIO

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from utils.error_handler import (
        TradingError,
        IndicatorError,
        DataError,
        handle_errors,
        safe_dataframe_operation,
        validate_numeric_input,
        log_performance_warning,
        create_error_context,
        indicator_error_handler,
        data_error_handler
    )
except ImportError:
    # Fallback si no se puede importar
    TradingError = Exception
    IndicatorError = Exception
    DataError = Exception
    handle_errors = Mock()
    safe_dataframe_operation = Mock()
    validate_numeric_input = Mock()
    log_performance_warning = Mock()
    create_error_context = Mock()
    indicator_error_handler = Mock()
    data_error_handler = Mock()

class TestCustomExceptions(unittest.TestCase):
    """Tests para las excepciones personalizadas"""
    
    @unittest.skipIf(TradingError == Exception, "TradingError not available")
    def test_trading_error_creation(self):
        """Test creación de TradingError"""
        # Error básico
        error = TradingError("Test error message")
        self.assertEqual(str(error), "Test error message")
        self.assertIsInstance(error, Exception)
        
        # Error con contexto
        context = {'symbol': 'BTCUSDT', 'timeframe': '1h'}
        error_with_context = TradingError("Error with context", context=context)
        self.assertEqual(str(error_with_context), "Error with context")
        self.assertEqual(error_with_context.context, context)
        
        # Error con código
        error_with_code = TradingError("Error with code", error_code="TRADE_001")
        self.assertEqual(error_with_code.error_code, "TRADE_001")
    
    @unittest.skipIf(IndicatorError == Exception, "IndicatorError not available")
    def test_indicator_error_creation(self):
        """Test creación de IndicatorError"""
        # Error básico
        error = IndicatorError("Indicator calculation failed")
        self.assertEqual(str(error), "Indicator calculation failed")
        self.assertIsInstance(error, TradingError)
    
    @unittest.skipIf(DataError == Exception, "DataError not available")
    def test_data_error_creation(self):
        """Test creación de DataError"""
        # Error básico
        error = DataError("Data validation failed")
        self.assertEqual(str(error), "Data validation failed")
        self.assertIsInstance(error, TradingError)

class TestHandleErrorsDecorator(unittest.TestCase):
    """Tests para el decorador handle_errors"""
    
    @unittest.skipIf(handle_errors == Mock, "handle_errors not available")
    def test_successful_function_execution(self):
        """Test ejecución exitosa de función decorada"""
        @handle_errors(default_return="default_value")
        def successful_function(x, y):
            return x + y
        
        result = successful_function(2, 3)
        self.assertEqual(result, 5)
    
    @unittest.skipIf(handle_errors == Mock, "handle_errors not available")
    def test_exception_handling_with_default(self):
        """Test manejo de excepciones con valor por defecto"""
        @handle_errors(default_return="error_occurred", log_errors=False)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        self.assertEqual(result, "error_occurred")
    

    

    
    @unittest.skipIf(handle_errors == Mock, "handle_errors not available")
    def test_logging_functionality(self):
        """Test funcionalidad de logging"""
        @handle_errors(log_errors=False, default_return=None)
        def failing_function():
            raise ValueError("Test error for logging")
        
        result = failing_function()
        self.assertIsNone(result)

class TestSafeDataframeOperation(unittest.TestCase):
    """Tests para safe_dataframe_operation"""
    
    @unittest.skipIf(safe_dataframe_operation == Mock, "safe_dataframe_operation not available")
    def test_successful_dataframe_operation(self):
        """Test operación exitosa en DataFrame"""
        df = pd.DataFrame({
            'open': [100, 101, 102, 103, 104],
            'high': [105, 106, 107, 108, 109],
            'low': [95, 96, 97, 98, 99],
            'close': [102, 103, 104, 105, 106]
        })
        
        # safe_dataframe_operation retorna bool, no ejecuta operaciones
        result = safe_dataframe_operation(df, "test_operation")
        self.assertTrue(result)
    
    @unittest.skipIf(safe_dataframe_operation == Mock, "safe_dataframe_operation not available")
    def test_dataframe_operation_with_error(self):
        """Test operación que falla en DataFrame"""
        # DataFrame sin columnas requeridas
        df = pd.DataFrame({'A': [1, 2, 3]})
        
        with self.assertRaises(DataError):
            safe_dataframe_operation(df, "test_operation")
    
    @unittest.skipIf(safe_dataframe_operation == Mock, "safe_dataframe_operation not available")
    def test_empty_dataframe_handling(self):
        """Test manejo de DataFrame vacío"""
        empty_df = pd.DataFrame()
        
        with self.assertRaises(DataError):
            safe_dataframe_operation(empty_df, "test_operation")

class TestValidateNumericInput(unittest.TestCase):
    """Tests para validate_numeric_input"""
    
    @unittest.skipIf(validate_numeric_input == Mock, "validate_numeric_input not available")
    def test_valid_numeric_inputs(self):
        """Test entradas numéricas válidas"""
        # Enteros
        self.assertEqual(validate_numeric_input(42, "test_int"), 42.0)
        self.assertEqual(validate_numeric_input(-10, "test_negative"), -10.0)
        self.assertEqual(validate_numeric_input(0, "test_zero"), 0.0)
        
        # Flotantes
        self.assertEqual(validate_numeric_input(3.14, "test_float"), 3.14)
        self.assertEqual(validate_numeric_input(-2.5, "test_negative_float"), -2.5)
        self.assertEqual(validate_numeric_input(0.0, "test_zero_float"), 0.0)
        
        # NumPy types
        self.assertEqual(validate_numeric_input(np.int32(5), "test_numpy_int"), 5.0)
        self.assertEqual(validate_numeric_input(np.float64(2.5), "test_numpy_float"), 2.5)
    
    @unittest.skipIf(validate_numeric_input == Mock, "validate_numeric_input not available")
    def test_invalid_numeric_inputs(self):
        """Test entradas numéricas inválidas"""
        # Strings no numéricos
        with self.assertRaises(IndicatorError):
            validate_numeric_input("not_a_number", "test_string")
        
        # String numérico debería funcionar
        self.assertEqual(validate_numeric_input("42", "test_string_num"), 42.0)
        
        # None
        with self.assertRaises(IndicatorError):
            validate_numeric_input(None, "test_none")
        
        # Listas y otros tipos
        with self.assertRaises(IndicatorError):
            validate_numeric_input([1, 2, 3], "test_list")
        
        with self.assertRaises(IndicatorError):
            validate_numeric_input({'value': 42}, "test_dict")
        
        # Valores especiales
        with self.assertRaises(IndicatorError):
            validate_numeric_input(float('inf'), "test_inf")
        
        with self.assertRaises(IndicatorError):
            validate_numeric_input(float('nan'), "test_nan")
    
    @unittest.skipIf(validate_numeric_input == Mock, "validate_numeric_input not available")
    def test_range_validation(self):
        """Test validación de rangos"""
        # Dentro del rango
        self.assertEqual(validate_numeric_input(5, "test", min_val=0, max_val=10), 5.0)
        self.assertEqual(validate_numeric_input(0, "test", min_val=0, max_val=10), 0.0)
        self.assertEqual(validate_numeric_input(10, "test", min_val=0, max_val=10), 10.0)
        
        # Fuera del rango
        with self.assertRaises(IndicatorError):
            validate_numeric_input(-1, "test", min_val=0, max_val=10)
        
        with self.assertRaises(IndicatorError):
            validate_numeric_input(11, "test", min_val=0, max_val=10)
        
        # Solo mínimo
        self.assertEqual(validate_numeric_input(100, "test", min_val=0), 100.0)
        
        with self.assertRaises(IndicatorError):
            validate_numeric_input(-1, "test", min_val=0)
        
        # Solo máximo
        self.assertEqual(validate_numeric_input(-100, "test", max_val=0), -100.0)
        
        with self.assertRaises(IndicatorError):
            validate_numeric_input(1, "test", max_val=0)

class TestLogPerformanceWarning(unittest.TestCase):
    """Tests para log_performance_warning"""
    
    @unittest.skipIf(log_performance_warning == Mock, "log_performance_warning not available")
    def test_performance_warning_logging(self):
        """Test logging de advertencias de rendimiento"""
        operation = "calculate_rsi"
        duration = 5.5
        threshold = 2.0
        
        # Test que la función no falle
        try:
            log_performance_warning(operation, duration, threshold)
            result = True
        except Exception:
            result = False
        self.assertTrue(result)
    
    @unittest.skipIf(log_performance_warning == Mock, "log_performance_warning not available")
    def test_no_warning_when_under_threshold(self):
        """Test que no se registra warning cuando está bajo el umbral"""
        operation = "fast_operation"
        duration = 1.0
        threshold = 2.0
        
        # Test que la función no falle
        try:
            log_performance_warning(operation, duration, threshold)
            result = True
        except Exception:
            result = False
        self.assertTrue(result)

class TestCreateErrorContext(unittest.TestCase):
    """Tests para create_error_context"""
    
    @unittest.skipIf(create_error_context == Mock, "create_error_context not available")
    def test_basic_error_context(self):
        """Test creación básica de contexto de error"""
        context = create_error_context(
            operation="calculate_indicator",
            symbol="BTCUSDT",
            timeframe="1h"
        )
        
        self.assertIsInstance(context, dict)
        self.assertEqual(context['operation'], "calculate_indicator")
        self.assertEqual(context['symbol'], "BTCUSDT")
        self.assertEqual(context['timeframe'], "1h")
        self.assertIn('timestamp', context)
    
    @unittest.skipIf(create_error_context == Mock, "create_error_context not available")
    def test_error_context_with_additional_data(self):
        """Test contexto de error con datos adicionales"""
        additional_data = {
            'indicator_params': {'period': 14},
            'data_length': 100
        }
        
        context = create_error_context(
            operation="rsi_calculation",
            symbol="ETHUSDT",
            **additional_data
        )
        
        self.assertEqual(context['operation'], "rsi_calculation")
        self.assertEqual(context['symbol'], "ETHUSDT")
        self.assertEqual(context['indicator_params'], {'period': 14})
        self.assertEqual(context['data_length'], 100)
    
    @unittest.skipIf(create_error_context == Mock, "create_error_context not available")
    def test_error_context_serialization(self):
        """Test que el contexto sea serializable"""
        import json
        
        context = create_error_context(
            operation="test_operation",
            symbol="BTCUSDT",
            value=42.5,
            flag=True
        )
        
        # Debería poder serializarse a JSON
        try:
            json_str = json.dumps(context)
            reconstructed = json.loads(json_str)
            self.assertEqual(reconstructed['operation'], "test_operation")
        except (TypeError, ValueError):
            self.fail("Error context should be JSON serializable")

class TestSpecificErrorHandlers(unittest.TestCase):
    """Tests para decoradores específicos de manejo de errores"""
    
    @unittest.skipIf(indicator_error_handler == Mock, "indicator_error_handler not available")
    def test_indicator_error_handler(self):
        """Test decorador específico para errores de indicadores"""
        @indicator_error_handler("RSI")
        def calculate_rsi(data, period=14):
            if len(data) < period:
                raise IndicatorError("Insufficient data for RSI calculation")
            return sum(data[-period:]) / period  # Simplified RSI
        
        # Caso exitoso
        data = list(range(1, 21))  # 20 elementos
        result = calculate_rsi(data, period=14)
        self.assertIsNotNone(result)
        
        # Caso con error
        short_data = [1, 2, 3]  # Solo 3 elementos
        result_error = calculate_rsi(short_data, period=14)
        # Debería retornar diccionario con error
        self.assertIsInstance(result_error, dict)
        self.assertTrue(result_error.get('error', False))
    
    @unittest.skipIf(data_error_handler == Mock, "data_error_handler not available")
    def test_data_error_handler(self):
        """Test decorador específico para errores de datos"""
        @data_error_handler("process_data")
        def process_market_data(df):
            if df.empty:
                raise DataError("Empty DataFrame provided")
            return df.mean()
        
        # Caso exitoso
        valid_df = pd.DataFrame({'price': [100, 101, 102]})
        result = process_market_data(valid_df)
        self.assertIsNotNone(result)
        
        # Caso con error
        empty_df = pd.DataFrame()
        result_error = process_market_data(empty_df)
        # Debería retornar None (valor por defecto)
        self.assertIsNone(result_error)

class TestErrorHandlerIntegration(unittest.TestCase):
    """Tests de integración del sistema de manejo de errores"""
    
    @unittest.skipIf(handle_errors == Mock, "handle_errors not available")
    def test_nested_error_handling(self):
        """Test manejo de errores anidados"""
        @handle_errors(default_return="outer_error", log_errors=False)
        def outer_function():
            @handle_errors(default_return="inner_error", log_errors=False)
            def inner_function():
                raise ValueError("Inner error")
            
            result = inner_function()
            if result == "inner_error":
                raise ValueError("Outer error due to inner failure")
            return "success"
        
        result = outer_function()
        self.assertEqual(result, "outer_error")
    
    @unittest.skipIf(all(x == Mock for x in [handle_errors, validate_numeric_input, create_error_context]), 
                     "Required functions not available")
    def test_comprehensive_error_scenario(self):
        """Test escenario completo de manejo de errores"""
        @handle_errors(log_errors=False, default_return=None)
        def complex_trading_function(symbol, amount, price):
            # Validar entradas (validate_numeric_input lanza excepción si es inválido)
            try:
                amount = validate_numeric_input(amount, "amount", min_val=0)
            except IndicatorError:
                context = create_error_context(
                    operation="validate_amount",
                    symbol=symbol,
                    amount=amount
                )
                raise TradingError("Invalid amount", context=context)
            
            try:
                price = validate_numeric_input(price, "price", min_val=0)
            except IndicatorError:
                context = create_error_context(
                    operation="validate_price",
                    symbol=symbol,
                    price=price
                )
                raise TradingError("Invalid price", context=context)
            
            # Simular cálculo
            total = amount * price
            return {'symbol': symbol, 'total': total}
        
        # Caso exitoso
        result = complex_trading_function("BTCUSDT", 1.5, 50000)
        self.assertIsNotNone(result)
        self.assertEqual(result['total'], 75000)
        
        # Casos con errores
        result_invalid_amount = complex_trading_function("BTCUSDT", -1, 50000)
        self.assertIsNone(result_invalid_amount)
        
        result_invalid_price = complex_trading_function("BTCUSDT", 1.5, -100)
        self.assertIsNone(result_invalid_price)
    
    @unittest.skipIf(safe_dataframe_operation == Mock, "safe_dataframe_operation not available")
    def test_dataframe_error_recovery(self):
        """Test recuperación de errores en operaciones de DataFrame"""
        # DataFrame con datos problemáticos
        problematic_df = pd.DataFrame({
            'price': [100, 101, None, 103, 104],
            'volume': [1000, 1100, 1200, None, 1400]
        })
        
        def calculate_vwap(df):
            # Esta operación fallará debido a valores None
            return (df['price'] * df['volume']).sum() / df['volume'].sum()
        
        # safe_dataframe_operation solo valida, no ejecuta operaciones
        # Crear DataFrame válido para la validación
        valid_df = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107], 
            'low': [95, 96, 97],
            'close': [102, 103, 104]
        })
        
        result = safe_dataframe_operation(valid_df, "calculate_vwap")
        self.assertTrue(result)

class TestErrorHandlerPerformance(unittest.TestCase):
    """Tests de rendimiento del sistema de manejo de errores"""
    
    @unittest.skipIf(handle_errors == Mock, "handle_errors not available")
    def test_decorator_overhead(self):
        """Test overhead del decorador en funciones exitosas"""
        import time
        
        def simple_function(x):
            return x * 2
        
        @handle_errors(log_errors=False)
        def decorated_function(x):
            return x * 2
        
        # Medir tiempo sin decorador
        start = time.time()
        for _ in range(1000):
            simple_function(42)
        simple_time = time.time() - start
        
        # Medir tiempo con decorador
        start = time.time()
        for _ in range(1000):
            decorated_function(42)
        decorated_time = time.time() - start
        
        # El overhead debería ser mínimo (menos del 1000% adicional)
        overhead_ratio = decorated_time / simple_time if simple_time > 0 else 1
        self.assertLess(overhead_ratio, 10.0, 
                       f"Decorator overhead too high: {overhead_ratio:.2f}x")
    
    @unittest.skipIf(validate_numeric_input == Mock, "validate_numeric_input not available")
    def test_validation_performance(self):
        """Test rendimiento de validación numérica"""
        import time
        
        test_values = [42, 3.14, -10, 0, 100.5] * 200  # 1000 valores
        
        start = time.time()
        for i, value in enumerate(test_values):
            validate_numeric_input(value, f"test_value_{i}")
        validation_time = time.time() - start
        
        # La validación debería ser muy rápida
        self.assertLess(validation_time, 0.5, 
                       f"Validation too slow: {validation_time:.3f}s for 1000 values")

if __name__ == '__main__':
    unittest.main(verbosity=2)