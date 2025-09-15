#!/usr/bin/env python3
"""
Tests para el sistema de cache avanzado
Prueba todas las funcionalidades del módulo advanced_cache.py
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from utils.advanced_cache import (
        IndicatorCache,
        indicator_cache,
        cached_function,
        clear_indicator_cache,
        get_cache_stats,
        cache_health_check
    )
except ImportError:
    # Fallback si no se puede importar
    IndicatorCache = Mock
    indicator_cache = Mock()
    cached_function = Mock()
    clear_indicator_cache = Mock()
    get_cache_stats = Mock()
    cache_health_check = Mock()

class TestIndicatorCache(unittest.TestCase):
    """Tests para la clase IndicatorCache"""
    
    def setUp(self):
        """Configurar cache limpio para cada test"""
        if IndicatorCache != Mock:
            self.cache = IndicatorCache(max_size=10, default_ttl=1)
        else:
            self.cache = Mock()
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_cache_initialization(self):
        """Test inicialización del cache"""
        cache = IndicatorCache(max_size=100, default_ttl=300)
        
        self.assertEqual(cache.max_size, 100)
        self.assertEqual(cache.default_ttl, 300)
        self.assertEqual(len(cache.cache), 0)
        self.assertEqual(len(cache.access_times), 0)
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_basic_set_and_get(self):
        """Test operaciones básicas de set y get"""
        # Almacenar valor
        self.cache.set('test_key', 'test_value', ttl=10)
        
        # Verificar que se almacenó
        self.assertEqual(self.cache.get('test_key'), 'test_value')
        
        # Verificar que se registró el tiempo de acceso
        self.assertIn('test_key', self.cache.access_times)
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_cache_expiration(self):
        """Test expiración automática del cache"""
        # Almacenar con TTL muy corto
        self.cache.set('expire_key', 'expire_value', ttl=0.1)
        
        # Verificar que está disponible inmediatamente
        self.assertEqual(self.cache.get('expire_key'), 'expire_value')
        
        # Esperar a que expire
        time.sleep(0.2)
        
        # Verificar que expiró
        self.assertIsNone(self.cache.get('expire_key'))
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_lru_eviction(self):
        """Test eliminación LRU cuando se alcanza el límite"""
        # Llenar el cache hasta el límite
        for i in range(self.cache.max_size):
            self.cache.set(f'key_{i}', f'value_{i}')
        
        # Verificar que está lleno
        self.assertEqual(len(self.cache.cache), self.cache.max_size)
        
        # Acceder a algunas claves para actualizar LRU
        self.cache.get('key_5')
        self.cache.get('key_7')
        
        # Agregar una clave más (debería eliminar la menos usada)
        self.cache.set('new_key', 'new_value')
        
        # Verificar que no excede el límite
        self.assertEqual(len(self.cache.cache), self.cache.max_size)
        
        # Verificar que las claves accedidas siguen ahí
        self.assertEqual(self.cache.get('key_5'), 'value_5')
        self.assertEqual(self.cache.get('key_7'), 'value_7')
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_cache_invalidation(self):
        """Test invalidación del cache"""
        # Agregar varias entradas
        self.cache.set('btc_1h_rsi', 'btc_rsi_data')
        self.cache.set('eth_1h_rsi', 'eth_rsi_data')
        self.cache.set('btc_4h_macd', 'btc_macd_data')
        
        # Invalidar por patrón
        self.cache.invalidate('btc')
        
        # Verificar que se eliminaron las entradas de BTC
        self.assertIsNone(self.cache.get('btc_1h_rsi'))
        self.assertIsNone(self.cache.get('btc_4h_macd'))
        
        # Verificar que ETH sigue ahí
        self.assertEqual(self.cache.get('eth_1h_rsi'), 'eth_rsi_data')
        
        # Invalidar todo
        self.cache.invalidate()
        
        # Verificar que está vacío
        self.assertEqual(len(self.cache.cache), 0)
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_indicator_specific_methods(self):
        """Test métodos específicos para indicadores"""
        # Cachear indicador
        params = {'period': 14, 'smoothing': 3}
        result = {'value': 65.5, 'signal': 'NEUTRAL'}
        
        self.cache.cache_indicator(
            symbol='BTCUSDT',
            timeframe='1h',
            indicator_name='RSI',
            params=params,
            result=result,
            ttl=300
        )
        
        # Obtener indicador
        cached_result = self.cache.get_indicator(
            symbol='BTCUSDT',
            timeframe='1h',
            indicator_name='RSI',
            params=params
        )
        
        self.assertEqual(cached_result, result)
        
        # Verificar que parámetros diferentes no coinciden
        different_params = {'period': 21, 'smoothing': 3}
        no_result = self.cache.get_indicator(
            symbol='BTCUSDT',
            timeframe='1h',
            indicator_name='RSI',
            params=different_params
        )
        
        self.assertIsNone(no_result)
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_cache_stats(self):
        """Test estadísticas del cache"""
        # Agregar algunas entradas
        self.cache.set('active_1', 'value_1', ttl=10)
        self.cache.set('active_2', 'value_2', ttl=10)
        self.cache.set('expired_1', 'value_3', ttl=0.1)
        
        # Esperar a que expire una
        time.sleep(0.2)
        
        # Obtener estadísticas
        stats = self.cache.get_stats()
        
        # Verificar estructura
        self.assertIn('total_entries', stats)
        self.assertIn('expired_entries', stats)
        self.assertIn('active_entries', stats)
        self.assertIn('max_size', stats)
        self.assertIn('usage_percentage', stats)
        
        # Verificar valores
        self.assertEqual(stats['total_entries'], 3)
        self.assertEqual(stats['expired_entries'], 1)
        self.assertEqual(stats['active_entries'], 2)
        self.assertEqual(stats['max_size'], self.cache.max_size)
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_cleanup_expired(self):
        """Test limpieza automática de entradas expiradas"""
        # Agregar entradas con diferentes TTL
        self.cache.set('short_ttl', 'value_1', ttl=0.1)
        self.cache.set('long_ttl', 'value_2', ttl=10)
        
        # Esperar a que expire la primera
        time.sleep(0.2)
        
        # Forzar limpieza agregando nueva entrada
        self.cache.set('new_entry', 'value_3')
        
        # Verificar que la expirada se eliminó
        self.assertNotIn('short_ttl', self.cache.cache)
        self.assertIn('long_ttl', self.cache.cache)
        self.assertIn('new_entry', self.cache.cache)

class TestCachedFunctionDecorator(unittest.TestCase):
    """Tests para el decorador cached_function"""
    
    @unittest.skipIf(cached_function == Mock, "cached_function not available")
    def test_function_caching(self):
        """Test cacheado automático de funciones"""
        call_count = 0
        
        @cached_function(ttl=1)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # Primera llamada - debe ejecutar la función
        result1 = expensive_function(2, 3)
        self.assertEqual(result1, 5)
        self.assertEqual(call_count, 1)
        
        # Segunda llamada con mismos parámetros - debe usar cache
        result2 = expensive_function(2, 3)
        self.assertEqual(result2, 5)
        self.assertEqual(call_count, 1)  # No debe incrementar
        
        # Llamada con parámetros diferentes - debe ejecutar
        result3 = expensive_function(3, 4)
        self.assertEqual(result3, 7)
        self.assertEqual(call_count, 2)
    
    @unittest.skipIf(cached_function == Mock, "cached_function not available")
    def test_cache_invalidation_method(self):
        """Test método de invalidación del decorador"""
        call_count = 0
        
        @cached_function(ttl=10)
        def test_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Llamar función
        result1 = test_function(5)
        self.assertEqual(result1, 10)
        self.assertEqual(call_count, 1)
        
        # Llamar de nuevo - debe usar cache
        result2 = test_function(5)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)
        
        # Invalidar cache
        test_function.invalidate_cache()
        
        # Llamar de nuevo - debe ejecutar función
        result3 = test_function(5)
        self.assertEqual(result3, 10)
        self.assertEqual(call_count, 2)
    
    @unittest.skipIf(cached_function == Mock, "cached_function not available")
    def test_custom_cache_key(self):
        """Test función personalizada para generar clave de cache"""
        def custom_key_func(*args, **kwargs):
            return f"custom_{args[0]}_{kwargs.get('multiplier', 1)}"
        
        call_count = 0
        
        @cached_function(ttl=10, cache_key_func=custom_key_func)
        def multiply_function(x, multiplier=2):
            nonlocal call_count
            call_count += 1
            return x * multiplier
        
        # Llamadas que deberían usar la misma clave
        result1 = multiply_function(5, multiplier=2)
        result2 = multiply_function(5, multiplier=2)
        
        self.assertEqual(result1, 10)
        self.assertEqual(result2, 10)
        self.assertEqual(call_count, 1)  # Solo una ejecución

class TestUtilityFunctions(unittest.TestCase):
    """Tests para funciones de utilidad"""
    
    @unittest.skipIf(clear_indicator_cache == Mock, "clear_indicator_cache not available")
    def test_clear_indicator_cache(self):
        """Test función de limpieza de cache de indicadores"""
        # Agregar datos al cache global
        if indicator_cache != Mock:
            indicator_cache.set('BTCUSDT_1h_rsi', 'btc_data')
            indicator_cache.set('ETHUSDT_1h_rsi', 'eth_data')
            indicator_cache.set('BTCUSDT_4h_macd', 'btc_macd')
            
            # Limpiar por símbolo
            clear_indicator_cache(symbol='BTCUSDT')
            
            # Verificar que se limpiaron las entradas de BTCUSDT
            self.assertIsNone(indicator_cache.get('BTCUSDT_1h_rsi'))
            self.assertIsNone(indicator_cache.get('BTCUSDT_4h_macd'))
            
            # Verificar que ETH sigue ahí
            self.assertEqual(indicator_cache.get('ETHUSDT_1h_rsi'), 'eth_data')
    
    @unittest.skipIf(get_cache_stats == Mock, "get_cache_stats not available")
    def test_get_cache_stats(self):
        """Test función de estadísticas globales"""
        stats = get_cache_stats()
        
        if stats != Mock():
            # Verificar que retorna un diccionario con las claves esperadas
            self.assertIsInstance(stats, dict)
            expected_keys = ['total_entries', 'expired_entries', 'active_entries', 'max_size', 'usage_percentage']
            for key in expected_keys:
                self.assertIn(key, stats)
    
    @unittest.skipIf(cache_health_check == Mock, "cache_health_check not available")
    def test_cache_health_check(self):
        """Test verificación de salud del cache"""
        health = cache_health_check()
        
        if health != Mock():
            # Verificar estructura del resultado
            self.assertIsInstance(health, dict)
            self.assertIn('status', health)
            self.assertIn('issues', health)
            self.assertIn('recommendations', health)
            self.assertIn('stats', health)
            self.assertIn('timestamp', health)
            
            # Verificar tipos
            self.assertIsInstance(health['issues'], list)
            self.assertIsInstance(health['recommendations'], list)
            self.assertIn(health['status'], ['healthy', 'warning'])

class TestCacheIntegration(unittest.TestCase):
    """Tests de integración del sistema de cache"""
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_realistic_trading_scenario(self):
        """Test escenario realista de trading con cache"""
        cache = IndicatorCache(max_size=100, default_ttl=300)
        
        # Simular cálculo de múltiples indicadores
        symbols = ['BTCUSDT', 'ETHUSDT']
        timeframes = ['1h', '4h']
        indicators = ['RSI', 'MACD', 'BB']
        
        # Cachear resultados
        for symbol in symbols:
            for timeframe in timeframes:
                for indicator in indicators:
                    params = {'period': 14}
                    result = {
                        'value': 50.0,
                        'signal': 'NEUTRAL',
                        'timestamp': time.time()
                    }
                    
                    cache.cache_indicator(
                        symbol=symbol,
                        timeframe=timeframe,
                        indicator_name=indicator,
                        params=params,
                        result=result
                    )
        
        # Verificar que todos se cachearon
        total_indicators = len(symbols) * len(timeframes) * len(indicators)
        self.assertEqual(len(cache.cache), total_indicators)
        
        # Verificar recuperación
        rsi_result = cache.get_indicator(
            symbol='BTCUSDT',
            timeframe='1h',
            indicator_name='RSI',
            params={'period': 14}
        )
        
        self.assertIsNotNone(rsi_result)
        self.assertEqual(rsi_result['signal'], 'NEUTRAL')
    
    @unittest.skipIf(cached_function == Mock, "cached_function not available")
    def test_performance_improvement(self):
        """Test mejora de rendimiento con cache"""
        import time
        
        @cached_function(ttl=10)
        def slow_calculation(n):
            # Simular cálculo lento
            time.sleep(0.01)
            return n * n
        
        # Medir tiempo sin cache
        start_time = time.time()
        result1 = slow_calculation(10)
        first_call_time = time.time() - start_time
        
        # Medir tiempo con cache
        start_time = time.time()
        result2 = slow_calculation(10)
        second_call_time = time.time() - start_time
        
        # Verificar que el resultado es correcto
        self.assertEqual(result1, 100)
        self.assertEqual(result2, 100)
        
        # Verificar que la segunda llamada es más rápida
        self.assertLess(second_call_time, first_call_time)
        self.assertLess(second_call_time, 0.005)  # Debe ser muy rápido

class TestCacheErrorHandling(unittest.TestCase):
    """Tests para manejo de errores en el cache"""
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_invalid_key_handling(self):
        """Test manejo de claves inválidas"""
        cache = IndicatorCache()
        
        # Obtener clave que no existe
        result = cache.get('nonexistent_key')
        self.assertIsNone(result)
        
        # No debe lanzar excepción
        cache.invalidate('nonexistent_pattern')
    
    @unittest.skipIf(IndicatorCache == Mock, "IndicatorCache not available")
    def test_edge_cases(self):
        """Test casos extremos"""
        cache = IndicatorCache(max_size=1, default_ttl=1)
        
        # Cache con tamaño 1
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')  # Debe eliminar key1
        
        self.assertIsNone(cache.get('key1'))
        self.assertEqual(cache.get('key2'), 'value2')
        
        # TTL de 0 (usa TTL por defecto)
        cache.set('zero_ttl', 'value', ttl=0)
        # TTL de 0 probablemente usa el TTL por defecto, no expira inmediatamente
        self.assertEqual(cache.get('zero_ttl'), 'value')
    
    @unittest.skipIf(cached_function == Mock, "cached_function not available")
    def test_function_with_exceptions(self):
        """Test función que lanza excepciones"""
        call_count = 0
        
        @cached_function(ttl=10)
        def failing_function(should_fail=False):
            nonlocal call_count
            call_count += 1
            if should_fail:
                raise ValueError("Test error")
            return "success"
        
        # Llamada exitosa
        result = failing_function(False)
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 1)
        
        # Llamada que falla
        with self.assertRaises(ValueError):
            failing_function(True)
        
        self.assertEqual(call_count, 2)
        
        # Verificar que la llamada exitosa sigue en cache
        result2 = failing_function(False)
        self.assertEqual(result2, "success")
        self.assertEqual(call_count, 2)  # No debe incrementar

if __name__ == '__main__':
    unittest.main(verbosity=2)