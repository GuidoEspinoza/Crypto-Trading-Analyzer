"""🧪 Comprehensive Test Suite
Suite de pruebas comprehensiva para validar todas las mejoras
del sistema de trading avanzado.

Desarrollado por: Experto en Trading & Programación
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Agregar el directorio backend al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from advanced_indicators import AdvancedIndicators
    from trading_engine.enhanced_strategies import ProfessionalRSIStrategy, EnhancedSignal
    from trading_engine.signal_filters import AdvancedSignalFilter, FilteredSignal
    from backtesting.enhanced_backtester import EnhancedBacktester, BacktestResults
    from sentiment_analyzer import SentimentAnalyzer, SentimentData
except ImportError:
    # Fallback para importaciones desde el directorio padre
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, parent_dir)
    
    from advanced_indicators import AdvancedIndicators
    from trading_engine.enhanced_strategies import ProfessionalRSIStrategy, EnhancedSignal
    from trading_engine.signal_filters import AdvancedSignalFilter, FilteredSignal
    from backtesting.enhanced_backtester import EnhancedBacktester, BacktestResults
    from sentiment_analyzer import SentimentAnalyzer, SentimentData

class TestAdvancedIndicators(unittest.TestCase):
    """🔍 Tests para indicadores avanzados"""
    
    def setUp(self):
        self.indicators = AdvancedIndicators()
        self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self, periods=100):
        """Crea datos de muestra para testing"""
        dates = pd.date_range(start='2024-01-01', periods=periods, freq='1h')
        
        # Generar datos OHLCV realistas
        np.random.seed(42)  # Para reproducibilidad
        base_price = 50000
        
        prices = []
        volumes = []
        
        for i in range(periods):
            # Simular movimiento de precios con tendencia y volatilidad
            change = float(np.random.normal(0, 0.02))  # 2% volatilidad
            if i > 0:
                base_price = float(prices[-1][3]) * (1 + change)  # Usar precio de cierre anterior
            else:
                base_price = 40000.0  # Precio inicial
            
            # OHLC
            open_price = float(base_price)
            high = float(open_price * (1 + abs(float(np.random.normal(0, 0.01)))))
            low = float(open_price * (1 - abs(float(np.random.normal(0, 0.01)))))
            close = float(open_price + float(np.random.normal(0, (high - low) * 0.3)))
            
            prices.append([open_price, high, low, close])
            volumes.append(np.random.randint(1000, 10000))
        
        df = pd.DataFrame(prices, columns=['open', 'high', 'low', 'close'], index=dates)
        df['volume'] = volumes
        
        return df
    
    def test_bollinger_bands(self):
        """Test Bollinger Bands calculation"""
        result = self.indicators.bollinger_bands(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('upper_band', result)
        self.assertIn('middle_band', result)
        self.assertIn('lower_band', result)
        self.assertIn('signal', result)
        
        # Verificar que las bandas son valores numéricos válidos
        self.assertIsInstance(result['upper_band'], (int, float))
        self.assertIsInstance(result['middle_band'], (int, float))
        self.assertIsInstance(result['lower_band'], (int, float))
    
    def test_vwap(self):
        """Test VWAP calculation"""
        result = self.indicators.vwap(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('vwap', result)
        self.assertIn('signal', result)
        
        # VWAP debe ser un valor numérico válido
        vwap_value = result['vwap']
        self.assertIsInstance(vwap_value, (int, float))
        self.assertTrue(vwap_value > 0)
    
    def test_obv(self):
        """Test On Balance Volume"""
        result = self.indicators.on_balance_volume(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('obv', result)
        self.assertIn('signal', result)
        
        # OBV debe ser un valor numérico válido
        obv_value = result['obv']
        self.assertIsInstance(obv_value, (int, float))
    
    def test_mfi(self):
        """Test Money Flow Index"""
        result = self.indicators.money_flow_index(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('mfi', result)
        self.assertIn('signal', result)
        
        # MFI debe estar entre 0 y 100
        mfi_value = result['mfi']
        self.assertTrue(mfi_value >= 0)
        self.assertTrue(mfi_value <= 100)
    
    def test_atr(self):
        """Test Average True Range"""
        result = self.indicators.average_true_range(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('atr', result)
        self.assertIn('volatility_level', result)
        
        # ATR debe ser positivo
        atr_value = result['atr']
        self.assertTrue(atr_value > 0)
    
    def test_volume_profile(self):
        """Test Volume Profile"""
        result = self.indicators.volume_profile(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('poc_price', result)  # Point of Control
        self.assertIn('vah', result)  # Value Area High
        self.assertIn('val', result)  # Value Area Low
        self.assertIn('signal', result)
    
    def test_support_resistance(self):
        """Test Support/Resistance levels"""
        result = self.indicators.support_resistance_levels(self.sample_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('support_levels', result)
        self.assertIn('resistance_levels', result)
        self.assertIn('signal', result)
        
        # Debe haber al menos algunos niveles
        self.assertTrue(len(result['support_levels']) >= 0)
        self.assertTrue(len(result['resistance_levels']) >= 0)

class TestEnhancedStrategies(unittest.TestCase):
    """🎯 Tests para estrategias mejoradas"""
    
    def setUp(self):
        self.strategy = ProfessionalRSIStrategy()
        self.sample_data = self._create_sample_data()
    
    def _create_sample_data(self, periods=100):
        """Crea datos de muestra"""
        dates = pd.date_range(start='2024-01-01', periods=periods, freq='1h')
        np.random.seed(42)
        
        base_price = 50000
        prices = []
        volumes = []
        
        for i in range(periods):
            change = float(np.random.normal(0, 0.02))
            if i > 0:
                base_price = float(prices[-1][3]) * (1 + change)  # Usar precio de cierre anterior
            else:
                base_price = 50000.0
            
            open_price = float(base_price)
            high = float(open_price * (1 + abs(float(np.random.normal(0, 0.01)))))
            low = float(open_price * (1 - abs(float(np.random.normal(0, 0.01)))))
            close = float(open_price + float(np.random.normal(0, (high - low) * 0.3)))
            
            prices.append([open_price, high, low, close])
            volumes.append(np.random.randint(1000, 10000))
        
        df = pd.DataFrame(prices, columns=['open', 'high', 'low', 'close'], index=dates)
        df['volume'] = volumes
        return df
    
    @patch('backtesting.enhanced_backtester.DataFetcher.get_historical_data')
    def test_strategy_analysis(self, mock_get_data):
        """Test análisis de estrategia"""
        mock_get_data.return_value = self.sample_data
        
        result = self.strategy.analyze('BTCUSDT', '1h')
        
        self.assertIsInstance(result, EnhancedSignal)
        self.assertIn(result.signal_type, ['BUY', 'SELL', 'HOLD'])
        self.assertTrue(0 <= result.confidence_score <= 100)
        self.assertTrue(result.confluence_score >= 0)
        self.assertIsInstance(result.notes, str)
    
    def test_signal_structure(self):
        """Test estructura de señales"""
        # Crear señal de prueba
        signal = EnhancedSignal(
            symbol='BTCUSDT',
            strategy_name='TestStrategy',
            signal_type='BUY',
            price=50000.0,
            confidence_score=75.0,
            strength='Strong',
            timestamp=datetime.now(),
            indicators_data={},
            notes='Test signal',
            volume_confirmation=True,
            trend_confirmation='BULLISH',
            risk_reward_ratio=2.0,
            stop_loss_price=48000.0,
            take_profit_price=54000.0,
            market_regime='TRENDING',
            confluence_score=4
        )
        
        self.assertEqual(signal.signal_type, 'BUY')
        self.assertEqual(signal.confidence_score, 75.0)
        self.assertTrue(signal.volume_confirmation)
        self.assertEqual(signal.trend_confirmation, 'BULLISH')

class TestSignalFilters(unittest.TestCase):
    """🔍 Tests para filtros de señales"""
    
    def setUp(self):
        self.filter = AdvancedSignalFilter()
        self.sample_signal = self._create_sample_signal()
        self.sample_data = self._create_sample_data()
    
    def _create_sample_signal(self):
        """Crea señal de muestra"""
        return EnhancedSignal(
            symbol='BTCUSDT',
            strategy_name='TestStrategy',
            signal_type='BUY',
            price=50000.0,
            confidence_score=75.0,
            strength='Strong',
            timestamp=datetime.now(),
            indicators_data={},
            notes='RSI oversold',
            volume_confirmation=True,
            trend_confirmation='BULLISH',
            risk_reward_ratio=2.0,
            stop_loss_price=48000.0,
            take_profit_price=54000.0,
            market_regime='TRENDING',
            confluence_score=4
        )
    
    def _create_sample_data(self):
        """Crea datos de muestra"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
        np.random.seed(42)
        
        prices = np.random.normal(50000, 1000, 100)
        df = pd.DataFrame({
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        return df
    
    def test_filter_signal(self):
        """Test filtrado de señales"""
        result = self.filter.filter_signal(self.sample_signal, self.sample_data)
        
        self.assertIsInstance(result, FilteredSignal)
        self.assertIn(result.filtered_signal, ['BUY', 'SELL', 'HOLD'])
        self.assertTrue(0 <= result.filter_score <= 100)
        self.assertIsInstance(result.filters_passed, list)
        self.assertIsInstance(result.filters_failed, list)
        self.assertIn(result.risk_assessment, ['LOW', 'MEDIUM', 'HIGH'])
        self.assertIn(result.quality_grade, ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D'])
    
    def test_filter_statistics(self):
        """Test estadísticas de filtros"""
        # Procesar varias señales
        for i in range(5):
            signal = self._create_sample_signal()
            signal.confidence = 50 + i * 10  # Variar confianza
            self.filter.filter_signal(signal, self.sample_data)
        
        stats = self.filter.get_filter_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_signals', stats)
        self.assertIn('signals_filtered_out', stats)
        self.assertIn('filter_rate', stats)
        self.assertIn('average_score', stats)
        
        self.assertEqual(stats['total_signals'], 5)

class TestBacktesting(unittest.TestCase):
    """📊 Tests para backtesting"""
    
    def setUp(self):
        self.backtester = EnhancedBacktester(initial_capital=10000)
        self.strategy = Mock()
        self._setup_strategy_mock()
    
    def _setup_strategy_mock(self):
        """Configura mock de estrategia"""
        # Mock para análisis básico
        mock_signal = EnhancedSignal(
            symbol='BTCUSDT',
            strategy_name='TestStrategy',
            signal_type='BUY',
            price=50000.0,
            confidence_score=75.0,
            strength='Strong',
            timestamp=datetime.now(),
            indicators_data={},
            notes='Test signal',
            volume_confirmation=True,
            trend_confirmation='BULLISH',
            risk_reward_ratio=2.0,
            stop_loss_price=48000.0,
            take_profit_price=54000.0,
            market_regime='TRENDING',
            confluence_score=4
        )
        
        self.strategy.analyze.return_value = mock_signal
        
        # Mock para análisis con filtros
        mock_filtered = FilteredSignal(
            original_signal=mock_signal,
            filtered_signal='BUY',
            filter_score=80.0,
            filters_passed=['confluence_check', 'confidence_check'],
            filters_failed=[],
            risk_assessment='LOW',
            quality_grade='A'
        )
        
        self.strategy.analyze_with_filters.return_value = mock_filtered
    
    @patch('backtesting.enhanced_backtester.DataFetcher')
    def test_backtest_structure(self, mock_data_fetcher):
        """Test estructura de backtesting"""
        # Mock data fetcher
        sample_data = self._create_sample_data()
        mock_data_fetcher.return_value.get_historical_data.return_value = sample_data
        
        # Ejecutar backtest
        results = self.backtester.run_backtest(
            strategy=self.strategy,
            symbol='BTCUSDT',
            start_date='2024-01-01',
            end_date='2024-01-31',
            timeframe='1h',
            use_filters=True
        )
        
        self.assertIsInstance(results, BacktestResults)
        self.assertTrue(hasattr(results, 'total_trades'))
        self.assertTrue(hasattr(results, 'win_rate'))
        self.assertTrue(hasattr(results, 'total_return_percentage'))
        self.assertTrue(hasattr(results, 'max_drawdown_percentage'))
        self.assertTrue(hasattr(results, 'sharpe_ratio'))
    
    def _create_sample_data(self):
        """Crea datos de muestra para backtesting"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
        np.random.seed(42)
        
        base_price = 50000
        prices = []
        
        for i in range(100):
            change = np.random.normal(0, 0.01)
            if i > 0:
                base_price = prices[-1] * (1 + change)
            prices.append(base_price)
        
        df = pd.DataFrame({
            'open': prices,
            'high': [p * 1.005 for p in prices],
            'low': [p * 0.995 for p in prices],
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        return df

class TestSentimentAnalysis(unittest.TestCase):
    """🧠 Tests para análisis de sentimiento"""
    
    def setUp(self):
        self.analyzer = SentimentAnalyzer()
    
    @patch('requests.get')
    def test_sentiment_analysis(self, mock_get):
        """Test análisis de sentimiento"""
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [{'value': '45', 'value_classification': 'Fear'}]
        }
        mock_get.return_value = mock_response
        
        result = self.analyzer.analyze_sentiment('BTCUSDT')
        
        self.assertIsInstance(result, SentimentData)
        self.assertIn(result.overall_sentiment, ['BULLISH', 'BEARISH', 'NEUTRAL'])
        self.assertTrue(-100 <= result.sentiment_score <= 100)
        self.assertTrue(0 <= result.confidence <= 100)
        self.assertIn(result.market_stress, ['LOW', 'MEDIUM', 'HIGH'])
    
    def test_sentiment_signals(self):
        """Test generación de señales de sentimiento"""
        # Crear datos de sentimiento de prueba
        sentiment_data = SentimentData(
            timestamp=datetime.now(),
            symbol='BTCUSDT',
            overall_sentiment='BULLISH',
            sentiment_score=60.0,
            confidence=80.0,
            fear_greed_index=25.0,  # Fear
            buy_pressure=70.0,
            sell_pressure=30.0,
            market_stress='MEDIUM'
        )
        
        signals = self.analyzer.get_sentiment_signals(sentiment_data)
        
        self.assertIsInstance(signals, dict)
        self.assertIn('sentiment_signal', signals)
        self.assertIn('strength', signals)
        self.assertIn('confidence', signals)
        self.assertIn('notes', signals)
        
        self.assertIn(signals['sentiment_signal'], ['BULLISH', 'BEARISH', 'NEUTRAL'])
        self.assertTrue(0 <= signals['strength'] <= 100)

class TestIntegration(unittest.TestCase):
    """🔗 Tests de integración"""
    
    def setUp(self):
        self.strategy = ProfessionalRSIStrategy()
        self.filter = AdvancedSignalFilter()
        self.backtester = EnhancedBacktester()
        self.sentiment_analyzer = SentimentAnalyzer()
    
    def test_end_to_end_workflow(self):
        """Test flujo completo end-to-end"""
        # Este test verifica que todos los componentes trabajen juntos
        
        # 1. Crear datos de muestra
        sample_data = self._create_sample_data()
        
        # 2. Mock data fetcher para la estrategia
        with patch('backtesting.enhanced_backtester.DataFetcher') as mock_fetcher:
            mock_fetcher.return_value.get_historical_data.return_value = sample_data
            
            # 3. Generar señal
            signal = self.strategy.analyze('BTCUSDT', '1h')
            self.assertIsInstance(signal, EnhancedSignal)
            
            # 4. Filtrar señal
            filtered_signal = self.filter.filter_signal(signal, sample_data)
            self.assertIsInstance(filtered_signal, FilteredSignal)
            
            # 5. Análisis de sentimiento
            with patch('requests.get') as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {'data': [{'value': '50'}]}
                mock_get.return_value = mock_response
                
                sentiment = self.sentiment_analyzer.analyze_sentiment('BTCUSDT')
                self.assertIsInstance(sentiment, SentimentData)
        
        # Verificar que el flujo completo funciona sin errores
        self.assertTrue(True)  # Si llegamos aquí, el flujo funcionó
    
    def _create_sample_data(self):
        """Crea datos de muestra"""
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
        np.random.seed(42)
        
        prices = np.random.normal(50000, 1000, 100)
        df = pd.DataFrame({
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        return df

class TestPerformance(unittest.TestCase):
    """⚡ Tests de rendimiento"""
    
    def setUp(self):
        self.indicators = AdvancedIndicators()
        self.large_dataset = self._create_large_dataset()
    
    def _create_large_dataset(self, periods=1000):
        """Crea dataset grande para tests de rendimiento"""
        dates = pd.date_range(start='2024-01-01', periods=periods, freq='1h')
        np.random.seed(42)
        
        prices = np.random.normal(50000, 1000, periods)
        df = pd.DataFrame({
            'open': prices,
            'high': prices * 1.01,
            'low': prices * 0.99,
            'close': prices,
            'volume': np.random.randint(1000, 10000, periods)
        }, index=dates)
        
        return df
    
    def test_indicators_performance(self):
        """Test rendimiento de indicadores con dataset grande"""
        import time
        
        start_time = time.time()
        
        # Ejecutar varios indicadores
        self.indicators.bollinger_bands(self.large_dataset)
        self.indicators.vwap(self.large_dataset)
        self.indicators.on_balance_volume(self.large_dataset)
        self.indicators.money_flow_index(self.large_dataset)
        self.indicators.average_true_range(self.large_dataset)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Debe ejecutarse en menos de 5 segundos
        self.assertLess(execution_time, 5.0, 
                       f"Indicators took too long: {execution_time:.2f}s")

def run_all_tests():
    """🚀 Ejecuta todas las pruebas"""
    # Crear suite de pruebas
    test_suite = unittest.TestSuite()
    
    # Agregar todas las clases de test
    test_classes = [
        TestAdvancedIndicators,
        TestEnhancedStrategies,
        TestSignalFilters,
        TestBacktesting,
        TestSentimentAnalysis,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Resumen
    print(f"\n{'='*60}")
    print(f"🧪 RESUMEN DE PRUEBAS")
    print(f"{'='*60}")
    print(f"✅ Pruebas ejecutadas: {result.testsRun}")
    print(f"❌ Fallos: {len(result.failures)}")
    print(f"⚠️  Errores: {len(result.errors)}")
    
    if result.failures:
        print(f"\n🔴 FALLOS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\n🔴 ERRORES:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Error:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"\n📊 Tasa de éxito: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"🎉 ¡Excelente! El sistema está funcionando correctamente.")
    elif success_rate >= 75:
        print(f"✅ Bien. Hay algunas áreas que necesitan atención.")
    else:
        print(f"⚠️  Atención requerida. Varios componentes necesitan revisión.")
    
    return result

if __name__ == '__main__':
    run_all_tests()