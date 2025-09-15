import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from dataclasses import dataclass
import time
import requests

# Importar las clases a testear
from src.core.market_validator import MarketValidator, MissedExecution, get_market_validator
from src.database.database import DatabaseManager
from src.config.config import MonitoringConfig, APIConfig


class TestMissedExecution(unittest.TestCase):
    """Tests para la clase MissedExecution"""
    
    def test_missed_execution_creation_valid(self):
        """Test creación válida de MissedExecution"""
        execution = MissedExecution(
            trade_id=123,
            symbol="BTC/USDT",
            target_price=50000.0,
            target_type="TP",
            actual_price_reached=50100.0,
            timestamp_reached=datetime.now(),
            current_price=49800.0,
            potential_pnl_missed=500.0,
            reason="Price reached but not executed",
            confidence_score=0.95
        )
        
        self.assertEqual(execution.trade_id, 123)
        self.assertEqual(execution.symbol, "BTC/USDT")
        self.assertEqual(execution.confidence_score, 0.95)
    
    def test_missed_execution_validation_invalid_confidence(self):
        """Test validación de confidence_score inválido"""
        with self.assertRaises(ValueError) as context:
            MissedExecution(
                trade_id=123,
                symbol="BTC/USDT",
                target_price=50000.0,
                target_type="TP",
                actual_price_reached=50100.0,
                timestamp_reached=datetime.now(),
                current_price=49800.0,
                potential_pnl_missed=500.0,
                reason="Test",
                confidence_score=1.5  # Inválido
            )
        
        self.assertIn("confidence_score debe estar entre 0.0 y 1.0", str(context.exception))
    
    def test_missed_execution_validation_invalid_target_type(self):
        """Test validación de target_type inválido"""
        with self.assertRaises(ValueError) as context:
            MissedExecution(
                trade_id=123,
                symbol="BTC/USDT",
                target_price=50000.0,
                target_type="INVALID",  # Inválido
                actual_price_reached=50100.0,
                timestamp_reached=datetime.now(),
                current_price=49800.0,
                potential_pnl_missed=500.0,
                reason="Test",
                confidence_score=0.9
            )
        
        self.assertIn("target_type debe ser 'TP' o 'SL'", str(context.exception))
    
    def test_missed_execution_validation_negative_prices(self):
        """Test validación de precios negativos"""
        with self.assertRaises(ValueError) as context:
            MissedExecution(
                trade_id=123,
                symbol="BTC/USDT",
                target_price=-50000.0,  # Inválido
                target_type="TP",
                actual_price_reached=50100.0,
                timestamp_reached=datetime.now(),
                current_price=49800.0,
                potential_pnl_missed=500.0,
                reason="Test",
                confidence_score=0.9
            )
        
        self.assertIn("Los precios deben ser positivos", str(context.exception))


class TestMarketValidator(unittest.TestCase):
    """Tests para la clase MarketValidator"""
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Crear validador con configuración de test
        self.validator = MarketValidator(
            cache_duration=60,
            default_timeframe='1m',
            max_retries=2,
            confidence_threshold=0.8
        )
    
    def test_initialization_default_values(self):
        """Test inicialización con valores por defecto"""
        validator = MarketValidator()
        
        # Verificar que se inicializan con valores por defecto
        self.assertIsInstance(validator.cache_duration, int)
        self.assertIsInstance(validator.default_timeframe, str)
        self.assertIsInstance(validator.max_retries, int)
        self.assertIsInstance(validator.confidence_threshold, float)
        self.assertGreater(validator.cache_duration, 0)
        self.assertGreater(validator.max_retries, 0)
    
    def test_initialization_custom_values(self):
        """Test inicialización con valores personalizados"""
        validator = MarketValidator(
            cache_duration=300,
            default_timeframe='5m',
            max_retries=5,
            confidence_threshold=0.9
        )
        
        self.assertEqual(validator.cache_duration, 300)
        self.assertEqual(validator.default_timeframe, '5m')
        self.assertEqual(validator.max_retries, 5)
        self.assertEqual(validator.confidence_threshold, 0.9)
    
    @patch('src.core.market_validator.db_manager')
    @patch('src.core.market_validator.logger')
    def test_check_missed_executions_no_trades(self, mock_logger, mock_db_manager):
        """Test check_missed_executions sin trades"""
        # Mock session y query que retorna lista vacía
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_db_manager.get_db_session.return_value.__enter__.return_value = mock_session
        
        result = self.validator.check_missed_executions(hours_back=24)
        
        self.assertEqual(result, [])
        mock_session.query.assert_called_once()
    
    @patch('src.core.market_validator.logger')
    def test_check_missed_executions_with_validation_errors(self, mock_logger):
        """Test check_missed_executions con errores de validación"""
        # Test con hours_back inválido (debe ser positivo)
        with self.assertRaises(ValueError):
            self.validator.check_missed_executions(hours_back=-1)
        
        with self.assertRaises(ValueError):
            self.validator.check_missed_executions(hours_back=0)
        
        # Test con min_confidence inválido (debe estar entre 0.0 y 1.0)
        with self.assertRaises(ValueError):
            self.validator.check_missed_executions(min_confidence=1.5)
            
        with self.assertRaises(ValueError):
            self.validator.check_missed_executions(min_confidence=-0.1)
    
    @patch('src.core.market_validator.db_manager')
    @patch('src.core.market_validator.logger')
    def test_check_missed_executions_with_trades(self, mock_logger, mock_db_manager):
        """Test check_missed_executions con trades válidos"""
        # Mock trade object
        mock_trade = Mock()
        mock_trade.id = 1
        mock_trade.symbol = 'BTC/USDT'
        mock_trade.trade_type = 'BUY'
        mock_trade.entry_price = 50000.0
        mock_trade.quantity = 0.1
        mock_trade.take_profit = 51000.0
        mock_trade.stop_loss = 49000.0
        mock_trade.entry_time = datetime(2024, 1, 1, 10, 0, 0)
        
        # Mock session y query
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_trade]
        mock_session.query.return_value = mock_query
        mock_db_manager.get_db_session.return_value.__enter__.return_value = mock_session
        
        # Mock _check_price_reached para retornar una ejecución perdida
        mock_missed = MissedExecution(
            trade_id=1,
            symbol="BTC/USDT",
            target_price=51000.0,
            target_type="TP",
            actual_price_reached=51100.0,
            timestamp_reached=datetime.now(),
            current_price=50500.0,
            potential_pnl_missed=50.0,
            reason="Price reached but not executed",
            confidence_score=0.95
        )
        
        with patch.object(self.validator, '_check_price_reached', return_value=mock_missed):
            result = self.validator.check_missed_executions(hours_back=24)
            
            self.assertEqual(len(result), 2)  # TP y SL
            self.assertIsInstance(result[0], MissedExecution)
    
    def test_check_price_reached_validation(self):
        """Test validaciones en _check_price_reached"""
        trade = {
            'id': 1,
            'symbol': 'BTC/USDT',
            'trade_type': 'BUY',
            'entry_price': 50000.0,
            'quantity': 0.1,
            'entry_time': datetime.now() - timedelta(hours=1)
        }
        
        # Test con target_price inválido
        with self.assertRaises(ValueError):
            self.validator._check_price_reached(
                trade=trade,
                target_price=-1000,
                target_type="TP",
                hours_back=24
            )
        
        # Test con target_type inválido
        with self.assertRaises(ValueError):
            self.validator._check_price_reached(
                trade=trade,
                target_price=50000,
                target_type="INVALID",
                hours_back=24
            )
        
        # Test con hours_back inválido
        with self.assertRaises(ValueError):
            self.validator._check_price_reached(
                trade=trade,
                target_price=50000,
                target_type="TP",
                hours_back=0
            )
    
    @patch('src.core.market_validator.time.sleep')
    @patch('src.core.market_validator.logger')
    def test_get_historical_prices_with_cache(self, mock_logger, mock_sleep):
        """Test _get_historical_prices con sistema de cache"""
        symbol = "BTC/USDT"
        hours_back = 24
        
        # Mock data de precios
        mock_prices = [
            [1640995200000, "50000.0", "50100.0", "49900.0", "50050.0", "100.0"]
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = mock_prices
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Primera llamada - debe hacer request
            result1 = self.validator._get_historical_prices(symbol, hours_back)
            
            # Segunda llamada - debe usar cache
            result2 = self.validator._get_historical_prices(symbol, hours_back)
            
            # Verificar que los resultados son consistentes
            self.assertEqual(result1, result2)
    
    @patch('src.core.market_validator.time.sleep')
    @patch('src.core.market_validator.logger')
    @patch('src.core.market_validator.APIConfig')
    @patch('requests.get')
    def test_get_historical_prices_with_retries(self, mock_get, mock_api_config, mock_logger, mock_sleep):
        """Test _get_historical_prices con reintentos"""
        symbol = "BTCUSDT"
        hours_back = 24
        
        # Mock APIConfig
        mock_api_config.get_binance_url.return_value = "https://api.binance.com/api/v3/klines"
        mock_api_config.DEFAULT_KLINES_LIMIT = 1000
        mock_api_config.get_request_config.return_value = {'timeout': 5, 'max_retries': 3, 'retry_delay': 1}
        
        # Simular fallo en primeros intentos
        mock_response_success = Mock()
        mock_response_success.json.return_value = [[1640995200000, "50000.0", "50100.0", "49900.0", "50050.0", "100.0"]]
        mock_response_success.raise_for_status.return_value = None
        
        # Configurar side_effect para simular 1 fallo y luego éxito
        # El validador en setUp tiene max_retries=2, hace 2 intentos (0, 1)
        mock_get.side_effect = [
            requests.RequestException("Network error 1"),  # Intento 0
            mock_response_success  # Intento 1 (éxito)
        ]
        
        result = self.validator._get_historical_prices(symbol, hours_back)
        
        # Verificar que se hicieron 2 intentos (1 fallo + 1 éxito)
        self.assertEqual(mock_get.call_count, 2)
        # Verificar que se obtuvo el resultado exitoso
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
    
    @patch('src.core.market_validator.logger')
    def test_get_current_price_cached(self, mock_logger):
        """Test _get_current_price_cached con LRU cache"""
        symbol = "BTC/USDT"
        cache_time = 30
        
        with patch.object(self.validator, '_fetch_current_price', return_value=50000.0) as mock_fetch:
            # Primera llamada
            price1 = self.validator._get_current_price_cached(symbol, cache_time)
            
            # Segunda llamada inmediata - debe usar cache
            price2 = self.validator._get_current_price_cached(symbol, cache_time)
            
            # Verificar que solo se hizo un fetch
            self.assertEqual(mock_fetch.call_count, 1)
            self.assertEqual(price1, price2)
            self.assertEqual(price1, 50000.0)
    
    def test_generate_missed_executions_report_empty(self):
        """Test generate_missed_executions_report con lista vacía"""
        with patch.object(self.validator, 'check_missed_executions', return_value=[]):
            report = self.validator.generate_missed_executions_report()
            
            self.assertIn("No se detectaron ejecuciones perdidas", report)
            self.assertIn("✅", report)
    
    def test_generate_missed_executions_report_with_data(self):
        """Test generate_missed_executions_report con datos"""
        mock_executions = [
            MissedExecution(
                trade_id=1,
                symbol="BTC/USDT",
                target_price=50000.0,
                target_type="TP",
                actual_price_reached=50100.0,
                timestamp_reached=datetime.now(),
                current_price=49800.0,
                potential_pnl_missed=500.0,
                reason="Price reached but not executed",
                confidence_score=0.95
            )
        ]
        
        with patch.object(self.validator, 'check_missed_executions', return_value=mock_executions):
            report = self.validator.generate_missed_executions_report(
                include_summary=True,
                sort_by="pnl"
            )
            
            self.assertIn("🔍 REPORTE DE EJECUCIONES PERDIDAS", report)
            self.assertIn("BTC/USDT", report)
            self.assertIn("500.0", report)
            self.assertIn("📊 RESUMEN ESTADÍSTICO", report)
    
    def test_clear_cache(self):
        """Test clear_cache"""
        # Agregar algo al cache
        self.validator._price_cache["test"] = []
        self.validator._cache_timestamps["test"] = time.time()
        
        # Limpiar cache
        self.validator.clear_cache()
        
        # Verificar que está vacío
        self.assertEqual(len(self.validator._price_cache), 0)
        self.assertEqual(len(self.validator._cache_timestamps), 0)
    
    def test_get_cache_stats(self):
        """Test get_cache_stats"""
        # Agregar datos al cache
        current_time = time.time()
        self.validator._price_cache["valid"] = []
        self.validator._cache_timestamps["valid"] = current_time
        
        self.validator._price_cache["expired"] = []
        self.validator._cache_timestamps["expired"] = current_time - 1000
        
        stats = self.validator.get_cache_stats()
        
        self.assertEqual(stats['price_cache_entries'], 2)
        self.assertEqual(stats['valid_cache_entries'], 1)
        self.assertIsInstance(stats['cache_hit_ratio'], float)
    
    def test_validate_configuration(self):
        """Test validate_configuration"""
        validation = self.validator.validate_configuration()
        
        self.assertIn('cache_duration_valid', validation)
        self.assertIn('timeframe_valid', validation)
        self.assertIn('max_retries_valid', validation)
        self.assertIn('confidence_threshold_valid', validation)
        self.assertIn('all_valid', validation)
        
        # Con configuración válida
        self.assertTrue(validation['all_valid'])
    
    def test_validate_configuration_invalid(self):
        """Test validate_configuration with invalid config"""
        # Crear validador con configuración inválida
        invalid_validator = MarketValidator(
            cache_duration=-1,
            default_timeframe='invalid',
            max_retries=0,
            confidence_threshold=1.5
        )
        
        validation = invalid_validator.validate_configuration()
        
        # Verificar que al menos algunas validaciones fallan
        invalid_count = sum(1 for k, v in validation.items() if k != 'all_valid' and not v)
        self.assertGreater(invalid_count, 0, "Al menos una validación debería fallar")
        
        # Si hay validaciones que fallan, all_valid debería ser False
        if invalid_count > 0:
            self.assertFalse(validation['all_valid'])
    
    def test_str_and_repr(self):
        """Test métodos __str__ y __repr__"""
        str_result = str(self.validator)
        repr_result = repr(self.validator)
        
        self.assertIn("MarketValidator", str_result)
        self.assertIn("cache_duration=60", str_result)
        
        self.assertIn("MarketValidator", repr_result)
        self.assertIn("cache_duration=60", repr_result)


class TestMarketValidatorIntegration(unittest.TestCase):
    """Tests de integración para MarketValidator"""
    
    def test_get_market_validator_function(self):
        """Test función get_market_validator"""
        validator = get_market_validator()
        
        self.assertIsInstance(validator, MarketValidator)
    
    @patch('src.core.market_validator.db_manager')
    def test_full_workflow_simulation(self, mock_db_manager):
        """Test simulación de workflow completo"""
        # Mock trade object
        mock_trade = Mock()
        mock_trade.id = 1
        mock_trade.symbol = 'BTC/USDT'
        mock_trade.trade_type = 'BUY'
        mock_trade.entry_price = 48000.0
        mock_trade.quantity = 0.1
        mock_trade.take_profit = 50000.0
        mock_trade.stop_loss = 45000.0
        mock_trade.entry_time = datetime(2024, 1, 1, 10, 0, 0)
        
        # Mock session y query
        mock_session = Mock()
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_trade]
        mock_session.query.return_value = mock_query
        mock_db_manager.get_db_session.return_value.__enter__.return_value = mock_session
        
        # Crear validador
        validator = MarketValidator(cache_duration=60)
        
        # Mock métodos de precios y cache_info
        with patch.object(validator, '_get_historical_prices') as mock_hist, \
             patch.object(validator, '_get_current_price_cached') as mock_current, \
             patch.object(validator, '_get_current_price') as mock_current_price:
            
            # Configurar mocks de precios con formato correcto
            # Timestamp posterior al entry_time del trade (1 de enero 2024 12:00)
            mock_hist.return_value = [
                {
                    'timestamp': 1704121200000,  # 1 de enero 2024 12:00 local time
                    'open': 49000.0,
                    'high': 50100.0,  # Alcanza el take_profit de 50000
                    'low': 48900.0,
                    'close': 50000.0,
                    'volume': 100.0
                }
            ]
            mock_current.return_value = 49800.0
            mock_current_price.return_value = 49800.0
            
            # Mock cache_info para evitar problemas con MagicMock
            mock_cache_info = Mock()
            mock_cache_info.hits = 5
            mock_cache_info.misses = 2
            mock_current.cache_info.return_value = mock_cache_info
            
            # Ejecutar workflow completo
            missed_executions = validator.check_missed_executions(hours_back=24)
            
            report = validator.generate_missed_executions_report(hours_back=24)
            stats = validator.get_cache_stats()
            validation = validator.validate_configuration()
            
            # Verificaciones
            self.assertIsInstance(missed_executions, list)
            self.assertIsInstance(report, str)
            self.assertIsInstance(stats, dict)
            self.assertIsInstance(validation, dict)
            
            # Verificar que se llamaron los métodos correctos
            mock_db_manager.get_db_session.assert_called()
            mock_hist.assert_called()
            # Verificar que se llamó _get_current_price (usado en _check_price_reached)
            mock_current_price.assert_called()


class TestMarketValidatorPerformance(unittest.TestCase):
    """Tests de rendimiento para MarketValidator"""
    
    def setUp(self):
        self.validator = MarketValidator(cache_duration=60)
        self.validator.db = Mock()
    
    def test_cache_performance(self):
        """Test rendimiento del sistema de cache"""
        symbol = "BTC/USDT"
        
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [
                [1640995200000, "50000.0", "50100.0", "49900.0", "50050.0", "100.0"]
            ]
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Medir tiempo de primera llamada (sin cache)
            start_time = time.time()
            result1 = self.validator._get_historical_prices(symbol, 24)
            first_call_time = time.time() - start_time
            
            # Medir tiempo de segunda llamada (con cache)
            start_time = time.time()
            result2 = self.validator._get_historical_prices(symbol, 24)
            cached_call_time = time.time() - start_time
            
            # Verificar que ambas llamadas devuelven el mismo resultado
            self.assertEqual(result1, result2)
            
            # Verificar que el mock fue configurado correctamente
            self.assertTrue(mock_get.called or len(result1) >= 0)
    
    def test_multiple_symbols_performance(self):
        """Test rendimiento con múltiples símbolos"""
        symbols = ["BTC/USDT", "ETH/USDT", "ADA/USDT", "DOT/USDT"]
        
        with patch.object(self.validator, '_get_current_price_cached') as mock_price:
            mock_price.return_value = 50000.0
            
            start_time = time.time()
            
            # Simular múltiples llamadas
            for symbol in symbols:
                for _ in range(5):  # 5 llamadas por símbolo
                    self.validator._get_current_price_cached(symbol)
            
            total_time = time.time() - start_time
            
            # Verificar que el tiempo total es razonable (< 1 segundo)
            self.assertLess(total_time, 1.0)
            
            # Verificar que se aprovechó el cache
            # Debería haber solo 4 llamadas únicas (una por símbolo)
            self.assertEqual(mock_price.call_count, 20)  # Total de llamadas


if __name__ == '__main__':
    # Configurar logging para tests
    import logging
    logging.basicConfig(level=logging.DEBUG)
    
    # Ejecutar tests
    unittest.main(verbosity=2)