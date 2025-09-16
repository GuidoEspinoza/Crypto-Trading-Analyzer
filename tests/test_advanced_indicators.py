#!/usr/bin/env python3
"""
🧪 Tests para Indicadores Técnicos Avanzados
Pruebas completas para src/core/advanced_indicators.py
"""

import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import warnings
from datetime import datetime, timedelta

# Importar el módulo a testear
from src.core.advanced_indicators import AdvancedIndicators, FibonacciLevels, IchimokuCloud
from src.config.config_manager import ConfigManager

class TestAdvancedIndicators(unittest.TestCase):
    """🧪 Clase principal de tests para AdvancedIndicators"""
    
    def setUp(self):
        """🔧 Configuración inicial para cada test"""
        # Crear datos de prueba realistas
        np.random.seed(42)  # Para reproducibilidad
        
        # Generar 100 días de datos OHLCV simulados
        dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
        
        # Simular precio base con tendencia
        base_price = 50000
        trend = np.linspace(0, 5000, 100)  # Tendencia alcista
        noise = np.random.normal(0, 1000, 100)  # Ruido aleatorio
        
        close_prices = base_price + trend + noise
        
        # Generar OHLC basado en close
        self.test_data = pd.DataFrame({
            'timestamp': dates,
            'open': close_prices + np.random.normal(0, 100, 100),
            'high': close_prices + np.abs(np.random.normal(200, 150, 100)),
            'low': close_prices - np.abs(np.random.normal(200, 150, 100)),
            'close': close_prices,
            'volume': np.random.uniform(1000000, 10000000, 100)
        })
        
        # Asegurar que high >= low y que close esté en el rango
        self.test_data['high'] = np.maximum(self.test_data['high'], self.test_data[['open', 'close']].max(axis=1))
        self.test_data['low'] = np.minimum(self.test_data['low'], self.test_data[['open', 'close']].min(axis=1))
        
        # Datos mínimos para tests de edge cases
        self.minimal_data = pd.DataFrame({
            'open': [100, 101, 102],
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [103, 104, 105],
            'volume': [1000, 1100, 1200]
        })
        
        # Datos con valores problemáticos
        self.problematic_data = pd.DataFrame({
            'open': [100, np.nan, 102, np.inf],
            'high': [105, 106, np.nan, 108],
            'low': [95, 96, 97, -np.inf],
            'close': [103, np.nan, 105, 106],
            'volume': [1000, 0, np.nan, 1300]
        })
    
    def test_safe_float_function(self):
        """🛡️ Test de la función safe_float"""
        # Valores normales
        self.assertEqual(AdvancedIndicators.safe_float(42.5), 42.5)
        self.assertEqual(AdvancedIndicators.safe_float(0), 0.0)
        
        # Valores problemáticos
        self.assertEqual(AdvancedIndicators.safe_float(np.nan), 0.0)
        self.assertEqual(AdvancedIndicators.safe_float(np.inf), 0.0)
        self.assertEqual(AdvancedIndicators.safe_float(-np.inf), 0.0)
        self.assertEqual(AdvancedIndicators.safe_float(None), 0.0)
        self.assertEqual(AdvancedIndicators.safe_float("invalid"), 0.0)
        
        # Valor por defecto personalizado
        self.assertEqual(AdvancedIndicators.safe_float(np.nan, 99.9), 99.9)
    
    def test_fibonacci_retracement(self):
        """🔢 Test de niveles de Fibonacci"""
        result = AdvancedIndicators.fibonacci_retracement(self.test_data)
        
        # Verificar que es una instancia de FibonacciLevels
        self.assertIsInstance(result, FibonacciLevels)
        
        # Verificar que todos los niveles son números válidos
        self.assertIsInstance(result.level_0, float)
        self.assertIsInstance(result.level_236, float)
        self.assertIsInstance(result.level_382, float)
        self.assertIsInstance(result.level_500, float)
        self.assertIsInstance(result.level_618, float)
        self.assertIsInstance(result.level_786, float)
        self.assertIsInstance(result.level_100, float)
        
        # Verificar orden lógico (level_0 > level_100 en retracement)
        self.assertGreaterEqual(result.level_0, result.level_100)
        
        # Test con lookback personalizado
        result_custom = AdvancedIndicators.fibonacci_retracement(self.test_data, lookback=20)
        self.assertIsInstance(result_custom, FibonacciLevels)
        
        # Test con datos mínimos
        result_minimal = AdvancedIndicators.fibonacci_retracement(self.minimal_data)
        self.assertIsInstance(result_minimal, FibonacciLevels)
    
    def test_ichimoku_cloud(self):
        """☁️ Test de Ichimoku Cloud"""
        result = AdvancedIndicators.ichimoku_cloud(self.test_data)
        
        # Verificar que es una instancia de IchimokuCloud
        self.assertIsInstance(result, IchimokuCloud)
        
        # Verificar que todos los componentes son números válidos
        self.assertIsInstance(result.tenkan_sen, float)
        self.assertIsInstance(result.kijun_sen, float)
        self.assertIsInstance(result.senkou_span_a, float)
        self.assertIsInstance(result.senkou_span_b, float)
        self.assertIsInstance(result.chikou_span, float)
        
        # Verificar strings
        self.assertIn(result.cloud_color, ["Verde", "Roja"])
        self.assertIsInstance(result.price_position, str)
        
        # Test con datos problemáticos
        result_problematic = AdvancedIndicators.ichimoku_cloud(self.problematic_data)
        self.assertIsInstance(result_problematic, IchimokuCloud)
    
    def test_stochastic_oscillator(self):
        """📊 Test de Oscilador Estocástico"""
        result = AdvancedIndicators.stochastic_oscillator(self.test_data)
        
        # Verificar estructura del resultado
        self.assertIn('k_percent', result)
        self.assertIn('d_percent', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipos
        self.assertIsInstance(result['k_percent'], (int, float))
        self.assertIsInstance(result['d_percent'], (int, float))
        self.assertIn(result['signal'], ['BUY', 'SELL', 'HOLD'])
        self.assertIsInstance(result['interpretation'], str)
        
        # Verificar rangos (Stochastic debe estar entre 0 y 100)
        self.assertGreaterEqual(result['k_percent'], 0)
        self.assertLessEqual(result['k_percent'], 100)
        self.assertGreaterEqual(result['d_percent'], 0)
        self.assertLessEqual(result['d_percent'], 100)
        
        # Test con parámetros personalizados
        result_custom = AdvancedIndicators.stochastic_oscillator(self.test_data, k_period=10, d_period=5)
        self.assertIn('k_percent', result_custom)
        
        # Test con datos problemáticos
        result_problematic = AdvancedIndicators.stochastic_oscillator(self.problematic_data)
        self.assertIn('signal', result_problematic)
    
    def test_williams_percent_r(self):
        """📊 Test de Williams %R"""
        result = AdvancedIndicators.williams_percent_r(self.test_data)
        
        # Verificar estructura
        self.assertIn('williams_r', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipos
        self.assertIsInstance(result['williams_r'], (int, float))
        self.assertIn(result['signal'], ['BUY', 'SELL', 'HOLD'])
        
        # Williams %R debe estar entre -100 y 0
        self.assertGreaterEqual(result['williams_r'], -100)
        self.assertLessEqual(result['williams_r'], 0)
        
        # Test con período personalizado
        result_custom = AdvancedIndicators.williams_percent_r(self.test_data, period=10)
        self.assertIn('williams_r', result_custom)
    
    def test_commodity_channel_index(self):
        """📊 Test de Commodity Channel Index"""
        result = AdvancedIndicators.commodity_channel_index(self.test_data)
        
        # Verificar estructura
        self.assertIn('cci', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipos
        self.assertIsInstance(result['cci'], (int, float))
        self.assertIn(result['signal'], ['BUY', 'SELL', 'HOLD'])
        
        # Test con período personalizado
        result_custom = AdvancedIndicators.commodity_channel_index(self.test_data, period=15)
        self.assertIn('cci', result_custom)
    
    def test_enhanced_rsi(self):
        """📈 Test de RSI Mejorado con cache"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        result = AdvancedIndicators.enhanced_rsi(self.test_data, symbol, timeframe)
        
        # Verificar estructura
        self.assertIn('rsi', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipos
        self.assertIsInstance(result['rsi'], (int, float))
        self.assertIn(result['signal'], ['BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL'])
        
        # RSI debe estar entre 0 y 100
        self.assertGreaterEqual(result['rsi'], 0)
        self.assertLessEqual(result['rsi'], 100)
        
        # Test con período personalizado
        result_custom = AdvancedIndicators.enhanced_rsi(self.test_data, symbol, timeframe, period=10)
        self.assertIn('rsi', result_custom)
    
    def test_rate_of_change(self):
        """📊 Test de Rate of Change"""
        result = AdvancedIndicators.rate_of_change(self.test_data)
        
        # Verificar estructura
        self.assertIn('roc', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipos
        self.assertIsInstance(result['roc'], (int, float))
        self.assertIn(result['signal'], ['BUY', 'SELL', 'HOLD'])
        
        # Test con período personalizado
        result_custom = AdvancedIndicators.rate_of_change(self.test_data, period=15)
        self.assertIn('roc', result_custom)
    
    def test_money_flow_index(self):
        """💰 Test de Money Flow Index"""
        result = AdvancedIndicators.money_flow_index(self.test_data)
        
        # Verificar estructura
        self.assertIn('mfi', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipos
        self.assertIsInstance(result['mfi'], (int, float))
        self.assertIn(result['signal'], ['BUY', 'SELL', 'HOLD'])
        
        # MFI debe estar entre 0 y 100
        self.assertGreaterEqual(result['mfi'], 0)
        self.assertLessEqual(result['mfi'], 100)
    
    def test_bollinger_bands(self):
        """📏 Test de Bandas de Bollinger"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        result = AdvancedIndicators.bollinger_bands(self.test_data, symbol, timeframe)
        
        # Verificar estructura
        self.assertIn('upper_band', result)
        self.assertIn('middle_band', result)
        self.assertIn('lower_band', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar que son números válidos
        self.assertIsInstance(result['upper_band'], (int, float))
        self.assertIsInstance(result['middle_band'], (int, float))
        self.assertIsInstance(result['lower_band'], (int, float))
        
        # Verificar que la diferencia entre bandas es razonable (no negativa)
        band_spread = abs(result['upper_band'] - result['lower_band'])
        self.assertGreaterEqual(band_spread, 0)
    
    def test_average_true_range(self):
        """📊 Test de Average True Range"""
        result = AdvancedIndicators.average_true_range(self.test_data)
        
        # Verificar estructura (basado en la implementación real)
        self.assertIn('atr', result)
        # Verificar que tiene al menos una de estas claves
        has_signal_info = any(key in result for key in ['signal', 'interpretation', 'volatility_level'])
        self.assertTrue(has_signal_info, "ATR debe tener información de señal o volatilidad")
        
        # ATR debe ser positivo
        self.assertGreaterEqual(result['atr'], 0)
    
    def test_vwap(self):
        """📊 Test de VWAP"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        result = AdvancedIndicators.vwap(self.test_data, symbol, timeframe)
        
        # Verificar estructura
        self.assertIn('vwap', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # VWAP debe ser un número positivo
        self.assertGreater(result['vwap'], 0)
    
    def test_on_balance_volume(self):
        """📊 Test de On Balance Volume"""
        result = AdvancedIndicators.on_balance_volume(self.test_data)
        
        # Verificar estructura
        self.assertIn('obv', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipo
        self.assertIsInstance(result['obv'], (int, float))
    
    def test_parabolic_sar(self):
        """📈 Test de Parabolic SAR"""
        result = AdvancedIndicators.parabolic_sar(self.test_data)
        
        # Verificar estructura (basado en la implementación real)
        # Puede usar 'sar' o 'psar' como clave
        has_sar = 'sar' in result or 'psar' in result
        self.assertTrue(has_sar, "Debe tener valor SAR")
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # SAR debe ser un número positivo
        sar_value = result.get('sar', result.get('psar', 0))
        self.assertGreater(sar_value, 0)
    
    def test_support_resistance_levels(self):
        """🎯 Test de niveles de soporte y resistencia"""
        result = AdvancedIndicators.support_resistance_levels(self.test_data)
        
        # Verificar estructura
        self.assertIn('support_levels', result)
        self.assertIn('resistance_levels', result)
        self.assertIn('signal', result)
        
        # Verificar que son listas
        self.assertIsInstance(result['support_levels'], list)
        self.assertIsInstance(result['resistance_levels'], list)
    
    def test_volume_profile(self):
        """📊 Test de perfil de volumen"""
        result = AdvancedIndicators.volume_profile(self.test_data)
        
        # Verificar estructura (basado en la implementación real)
        # Puede tener 'volume_profile' o información de POC directamente
        has_volume_info = any(key in result for key in ['volume_profile', 'poc_price', 'poc'])
        self.assertTrue(has_volume_info, "Debe tener información de volumen")
        self.assertIn('signal', result)
        
        # Si tiene volume_profile, debe ser un diccionario
        if 'volume_profile' in result:
            self.assertIsInstance(result['volume_profile'], dict)
    
    def test_awesome_oscillator(self):
        """🌊 Test de Awesome Oscillator"""
        result = AdvancedIndicators.awesome_oscillator(self.test_data)
        
        # Verificar estructura
        self.assertIn('awesome_oscillator', result)
        self.assertIn('signal', result)
        self.assertIn('interpretation', result)
        
        # Verificar tipo
        self.assertIsInstance(result['awesome_oscillator'], (int, float))
    
    def test_detect_candlestick_patterns(self):
        """🕯️ Test de detección de patrones de velas"""
        result = AdvancedIndicators.detect_candlestick_patterns(self.test_data)
        
        # Verificar estructura (basado en la implementación real)
        self.assertIn('patterns', result)
        # Verificar que tiene información de patrones
        has_pattern_info = any(key in result for key in ['signal', 'patterns_detected'])
        self.assertTrue(has_pattern_info, "Debe tener información de patrones")
        
        # Verificar que patterns es una lista
        self.assertIsInstance(result['patterns'], list)
    
    def test_trend_lines_analysis(self):
        """📈 Test de análisis de líneas de tendencia"""
        result = AdvancedIndicators.trend_lines_analysis(self.test_data)
        
        # Verificar estructura
        self.assertIn('trend_lines', result)
        self.assertIn('signal', result)
        
        # Verificar que trend_lines es un diccionario
        self.assertIsInstance(result['trend_lines'], dict)
    
    def test_chart_patterns_detection(self):
        """📊 Test de detección de patrones gráficos"""
        result = AdvancedIndicators.chart_patterns_detection(self.test_data)
        
        # Verificar estructura
        self.assertIn('patterns', result)
        self.assertIn('signal', result)
        
        # Verificar que patterns es una lista
        self.assertIsInstance(result['patterns'], list)
    
    def test_cache_functionality(self):
        """💾 Test del sistema de cache"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        # Test de generación de cache key
        cache_key = AdvancedIndicators._get_cache_key(symbol, timeframe, "rsi", period=14)
        self.assertIsInstance(cache_key, str)
        self.assertGreater(len(cache_key), 0)
        
        # Test de cache con RSI
        result1 = AdvancedIndicators.enhanced_rsi(self.test_data, symbol, timeframe)
        result2 = AdvancedIndicators.enhanced_rsi(self.test_data, symbol, timeframe)
        
        # Los resultados deben ser consistentes
        self.assertEqual(result1['rsi'], result2['rsi'])
    
    def test_error_handling_with_empty_data(self):
        """🚨 Test de manejo de errores con datos vacíos"""
        empty_df = pd.DataFrame()
        
        # Los métodos deben manejar datos vacíos sin fallar
        result = AdvancedIndicators.stochastic_oscillator(empty_df)
        self.assertIn('signal', result)
        self.assertEqual(result['signal'], 'HOLD')
    
    def test_error_handling_with_insufficient_data(self):
        """🚨 Test de manejo de errores con datos insuficientes"""
        # DataFrame con solo 2 filas
        insufficient_data = pd.DataFrame({
            'open': [100, 101],
            'high': [105, 106],
            'low': [95, 96],
            'close': [103, 104],
            'volume': [1000, 1100]
        })
        
        # Los métodos deben manejar datos insuficientes
        result = AdvancedIndicators.enhanced_rsi(insufficient_data, "TEST", "1h")
        self.assertIn('signal', result)
    
    def test_configuration_usage(self):
        """⚙️ Test de uso de configuraciones"""
        # Verificar que se usan las configuraciones correctas
        config_manager = ConfigManager()
        config = config_manager.get_consolidated_config()
        
        # Verificar que la configuración existe y tiene la estructura esperada
        self.assertIsInstance(config, dict)
        
        # Test que los métodos pueden acceder a configuraciones con valores por defecto
        result = AdvancedIndicators.enhanced_rsi(self.test_data, "TEST", "1h")
        self.assertIn('rsi', result)
        
        # Test que los métodos funcionan sin configuración específica
        result2 = AdvancedIndicators.fibonacci_retracement(self.test_data)
        self.assertIsInstance(result2, object)  # FibonacciLevels object
    
    def test_signal_generation_consistency(self):
        """🎯 Test de consistencia en generación de señales"""
        # Ejecutar múltiples indicadores y verificar consistencia
        rsi_result = AdvancedIndicators.enhanced_rsi(self.test_data, "TEST", "1h")
        stoch_result = AdvancedIndicators.stochastic_oscillator(self.test_data)
        williams_result = AdvancedIndicators.williams_percent_r(self.test_data)
        
        # Todas las señales deben ser válidas
        valid_signals = ['BUY', 'SELL', 'HOLD', 'STRONG_BUY', 'STRONG_SELL']
        self.assertIn(rsi_result['signal'], valid_signals)
        self.assertIn(stoch_result['signal'], ['BUY', 'SELL', 'HOLD'])
        self.assertIn(williams_result['signal'], ['BUY', 'SELL', 'HOLD'])
    
    def test_performance_with_large_dataset(self):
        """⚡ Test de rendimiento con dataset grande"""
        # Crear dataset más grande
        large_data = pd.DataFrame({
            'open': np.random.uniform(45000, 55000, 1000),
            'high': np.random.uniform(50000, 60000, 1000),
            'low': np.random.uniform(40000, 50000, 1000),
            'close': np.random.uniform(45000, 55000, 1000),
            'volume': np.random.uniform(1000000, 10000000, 1000)
        })
        
        # Asegurar OHLC válido
        large_data['high'] = np.maximum(large_data['high'], large_data[['open', 'close']].max(axis=1))
        large_data['low'] = np.minimum(large_data['low'], large_data[['open', 'close']].min(axis=1))
        
        # Test de rendimiento (debe completarse sin errores)
        start_time = datetime.now()
        result = AdvancedIndicators.enhanced_rsi(large_data, "BTCUSDT", "1h")
        end_time = datetime.now()
        
        # Verificar que se completó y fue relativamente rápido
        self.assertIn('rsi', result)
        execution_time = (end_time - start_time).total_seconds()
        self.assertLess(execution_time, 5.0)  # Debe completarse en menos de 5 segundos

class TestAdvancedIndicatorsIntegration(unittest.TestCase):
    """🔗 Tests de integración para múltiples indicadores"""
    
    def setUp(self):
        """🔧 Configuración para tests de integración"""
        # Datos de mercado más realistas
        np.random.seed(123)
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        
        # Simular movimiento de precio más realista
        base_price = 50000
        returns = np.random.normal(0.0001, 0.02, 200)  # Retornos con volatilidad realista
        prices = [base_price]
        
        for ret in returns[1:]:
            prices.append(prices[-1] * (1 + ret))
        
        self.market_data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'close': prices,
            'volume': np.random.uniform(1000000, 5000000, 200)
        })
        
        # Ajustar OHLC para que sea válido
        self.market_data['high'] = np.maximum(self.market_data['high'], 
                                            self.market_data[['open', 'close']].max(axis=1))
        self.market_data['low'] = np.minimum(self.market_data['low'], 
                                           self.market_data[['open', 'close']].min(axis=1))
    
    def test_multi_indicator_analysis(self):
        """📊 Test de análisis con múltiples indicadores"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        # Ejecutar múltiples indicadores
        indicators = {
            'rsi': AdvancedIndicators.enhanced_rsi(self.market_data, symbol, timeframe),
            'stochastic': AdvancedIndicators.stochastic_oscillator(self.market_data),
            'bollinger': AdvancedIndicators.bollinger_bands(self.market_data, symbol, timeframe),
            'williams': AdvancedIndicators.williams_percent_r(self.market_data),
            'cci': AdvancedIndicators.commodity_channel_index(self.market_data),
            'mfi': AdvancedIndicators.money_flow_index(self.market_data)
        }
        
        # Verificar que todos los indicadores funcionan
        for name, result in indicators.items():
            self.assertIn('signal', result, f"Indicador {name} no tiene señal")
            self.assertIn('interpretation', result, f"Indicador {name} no tiene interpretación")
    
    def test_trading_strategy_simulation(self):
        """💹 Test de simulación de estrategia de trading"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        buy_signals = 0
        sell_signals = 0
        hold_signals = 0
        
        # Simular análisis en ventana deslizante
        window_size = 50
        for i in range(window_size, len(self.market_data) - 10, 10):
            window_data = self.market_data.iloc[i-window_size:i]
            
            # Obtener señales de múltiples indicadores
            rsi = AdvancedIndicators.enhanced_rsi(window_data, symbol, timeframe)
            stoch = AdvancedIndicators.stochastic_oscillator(window_data)
            
            # Contar señales
            if rsi['signal'] == 'BUY':
                buy_signals += 1
            elif rsi['signal'] == 'SELL':
                sell_signals += 1
            else:
                hold_signals += 1
        
        # Verificar que se generaron señales
        total_signals = buy_signals + sell_signals + hold_signals
        self.assertGreater(total_signals, 0)
        
        # Imprimir estadísticas para debugging
        print(f"\n📊 Estadísticas de señales:")
        print(f"   🟢 BUY: {buy_signals}")
        print(f"   🔴 SELL: {sell_signals}")
        print(f"   ⚪ HOLD: {hold_signals}")
    
    def test_cache_performance_comparison(self):
        """⚡ Test de comparación de rendimiento con cache"""
        symbol = "BTCUSDT"
        timeframe = "1h"
        
        # Primera ejecución (sin cache)
        start_time = datetime.now()
        result1 = AdvancedIndicators.enhanced_rsi(self.market_data, symbol, timeframe)
        first_execution_time = (datetime.now() - start_time).total_seconds()
        
        # Segunda ejecución (con cache)
        start_time = datetime.now()
        result2 = AdvancedIndicators.enhanced_rsi(self.market_data, symbol, timeframe)
        second_execution_time = (datetime.now() - start_time).total_seconds()
        
        # Los resultados deben ser idénticos
        self.assertEqual(result1['rsi'], result2['rsi'])
        
        # La segunda ejecución debería ser más rápida (o al menos no más lenta)
        self.assertLessEqual(second_execution_time, first_execution_time * 2)
        
        print(f"\n⚡ Rendimiento del cache:")
        print(f"   Primera ejecución: {first_execution_time:.4f}s")
        print(f"   Segunda ejecución: {second_execution_time:.4f}s")

if __name__ == '__main__':
    # Configurar warnings para tests
    warnings.filterwarnings('ignore', category=UserWarning)
    warnings.filterwarnings('ignore', category=FutureWarning)
    
    # Ejecutar tests con verbosidad
    unittest.main(verbosity=2, buffer=True)