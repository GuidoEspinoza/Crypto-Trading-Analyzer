#!/usr/bin/env python3
"""
🗄️ Tests para Database Manager Optimizado
Suite de tests para verificar las optimizaciones y configuraciones del DatabaseManager
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Imports del sistema
from src.config.database_config import (
    DatabaseConfig, ConnectionConfig, SessionConfig, PortfolioConfig,
    LoggingConfig, QueryConfig, PerformanceConfig,
    get_database_config, DEFAULT_DATABASE_CONFIG, DEVELOPMENT_DATABASE_CONFIG,
    PRODUCTION_DATABASE_CONFIG, TEST_DATABASE_CONFIG
)
from src.config.global_constants import GLOBAL_INITIAL_BALANCE
from src.database.database import DatabaseManager, get_database_manager


class TestDatabaseConfig(unittest.TestCase):
    """
    🧪 Tests para configuración de base de datos
    """
    
    def test_default_config_creation(self):
        """Test creación de configuración por defecto"""
        config = DatabaseConfig()
        
        # Verificar valores por defecto
        self.assertEqual(config.connection.database_name, "trading_bot.db")
        self.assertEqual(config.portfolio.initial_usdt_amount, GLOBAL_INITIAL_BALANCE)
        self.assertEqual(config.portfolio.base_currency, "USDT")
        self.assertTrue(config.performance.enable_query_cache)
        self.assertEqual(config.performance.cache_ttl_seconds, 300)
        
    def test_custom_config_creation(self):
        """Test creación de configuración personalizada"""
        custom_config = DatabaseConfig(
            connection=ConnectionConfig(
                database_name="custom.db",
                pool_size=15
            ),
            portfolio=PortfolioConfig(
                initial_usdt_amount=5000.0,
                base_currency="USDC"
            ),
            performance=PerformanceConfig(
                enable_query_cache=False,
                cache_ttl_seconds=600
            )
        )
        
        self.assertEqual(custom_config.connection.database_name, "custom.db")
        self.assertEqual(custom_config.connection.pool_size, 15)
        self.assertEqual(custom_config.portfolio.initial_usdt_amount, 5000.0)
        self.assertEqual(custom_config.portfolio.base_currency, "USDC")
        self.assertFalse(custom_config.performance.enable_query_cache)
        self.assertEqual(custom_config.performance.cache_ttl_seconds, 600)
        
    def test_config_to_dict(self):
        """Test conversión de configuración a diccionario"""
        config = DatabaseConfig()
        config_dict = config.to_dict()
        
        # Verificar estructura del diccionario
        self.assertIn("connection", config_dict)
        self.assertIn("session", config_dict)
        self.assertIn("portfolio", config_dict)
        self.assertIn("logging", config_dict)
        self.assertIn("query", config_dict)
        self.assertIn("performance", config_dict)
        
        # Verificar valores específicos
        self.assertEqual(config_dict["connection"]["database_name"], "trading_bot.db")
        self.assertEqual(config_dict["portfolio"]["initial_usdt_amount"], GLOBAL_INITIAL_BALANCE)
        
    def test_config_from_dict(self):
        """Test creación de configuración desde diccionario"""
        config_dict = {
            "connection": {
                "database_name": "test.db",
                "pool_size": 8
            },
            "portfolio": {
                "initial_usdt_amount": 2000.0,
                "base_currency": "BTC"
            },
            "performance": {
                "enable_query_cache": False
            }
        }
        
        config = DatabaseConfig.from_dict(config_dict)
        
        self.assertEqual(config.connection.database_name, "test.db")
        self.assertEqual(config.connection.pool_size, 8)
        self.assertEqual(config.portfolio.initial_usdt_amount, 2000.0)
        self.assertEqual(config.portfolio.base_currency, "BTC")
        self.assertFalse(config.performance.enable_query_cache)
        
    def test_predefined_profiles(self):
        """Test perfiles predefinidos"""
        # Test default profile
        default_config = get_database_config("default")
        self.assertIsInstance(default_config, DatabaseConfig)
        self.assertEqual(default_config.connection.database_name, "trading_bot.db")
        
        # Test development profile
        dev_config = get_database_config("development")
        self.assertTrue(dev_config.connection.echo_sql)
        self.assertEqual(dev_config.logging.level, "DEBUG")
        self.assertFalse(dev_config.performance.enable_query_cache)
        
        # Test production profile
        prod_config = get_database_config("production")
        self.assertFalse(prod_config.connection.echo_sql)
        self.assertEqual(prod_config.logging.level, "WARNING")
        self.assertTrue(prod_config.performance.enable_query_cache)
        self.assertEqual(prod_config.performance.cache_ttl_seconds, 600)
        
        # Test test profile
        test_config = get_database_config("test")
        self.assertEqual(test_config.connection.database_name, ":memory:")
        self.assertEqual(test_config.portfolio.initial_usdt_amount, GLOBAL_INITIAL_BALANCE)
        self.assertEqual(test_config.logging.level, "ERROR")
        
    def test_connection_config_database_url(self):
        """Test generación de URL de base de datos"""
        # Test con URL personalizada
        config = ConnectionConfig(database_url="sqlite:///custom.db")
        self.assertEqual(config.get_database_url(), "sqlite:///custom.db")
        
        # Test con nombre de archivo
        config = ConnectionConfig(database_name="test.db")
        url = config.get_database_url()
        self.assertTrue(url.startswith("sqlite:///"))
        self.assertTrue(url.endswith("test.db"))
        
    def test_logging_config_level_conversion(self):
        """Test conversión de nivel de logging"""
        import logging
        
        config = LoggingConfig(level="DEBUG")
        self.assertEqual(config.get_logging_level(), logging.DEBUG)
        
        config = LoggingConfig(level="INFO")
        self.assertEqual(config.get_logging_level(), logging.INFO)
        
        config = LoggingConfig(level="WARNING")
        self.assertEqual(config.get_logging_level(), logging.WARNING)
        
        config = LoggingConfig(level="ERROR")
        self.assertEqual(config.get_logging_level(), logging.ERROR)


class TestDatabaseManagerOptimizations(unittest.TestCase):
    """
    🧪 Tests para DatabaseManager optimizado
    """
    
    def setUp(self):
        """Configuración inicial para cada test"""
        # Usar configuración de test con base de datos en memoria
        self.test_config = TEST_DATABASE_CONFIG
        self.db_manager = DatabaseManager(config=self.test_config)
        
    def tearDown(self):
        """Limpieza después de cada test"""
        if hasattr(self.db_manager, 'close'):
            self.db_manager.close()
            
    def test_database_manager_initialization(self):
        """Test inicialización del DatabaseManager"""
        # Verificar que se inicializa correctamente
        self.assertIsNotNone(self.db_manager.config)
        self.assertIsNotNone(self.db_manager.engine)
        self.assertIsNotNone(self.db_manager.SessionLocal)
        self.assertIsNotNone(self.db_manager.logger)
        
        # Verificar configuración aplicada
        self.assertEqual(self.db_manager.config.portfolio.initial_usdt_amount, GLOBAL_INITIAL_BALANCE)
        
    def test_database_manager_with_profile(self):
        """Test creación con perfil específico"""
        # Test con perfil de desarrollo
        dev_manager = get_database_manager("development")
        self.assertTrue(dev_manager.config.connection.echo_sql)
        
        # Test con perfil de producción
        prod_manager = get_database_manager("production")
        self.assertFalse(prod_manager.config.connection.echo_sql)
        self.assertTrue(prod_manager.config.performance.enable_query_cache)
        
        # Limpiar
        dev_manager.close()
        prod_manager.close()
        
    def test_cache_functionality(self):
        """Test funcionalidad de cache"""
        # Configurar manager con cache habilitado
        cache_config = DatabaseConfig(
            connection=ConnectionConfig(database_name=":memory:"),
            performance=PerformanceConfig(
                enable_query_cache=True,
                cache_ttl_seconds=60
            )
        )
        cache_manager = DatabaseManager(config=cache_config)
        
        # Test cache válido
        cache_manager._set_cache("test_key", "test_value")
        self.assertTrue(cache_manager._is_cache_valid("test_key"))
        self.assertEqual(cache_manager._get_cache("test_key"), "test_value")
        
        # Test cache inválido (clave no existe)
        self.assertFalse(cache_manager._is_cache_valid("nonexistent_key"))
        self.assertIsNone(cache_manager._get_cache("nonexistent_key"))
        
        # Test estadísticas de cache
        stats = cache_manager.get_cache_stats()
        self.assertTrue(stats["cache_enabled"])
        self.assertEqual(stats["cached_queries"], 1)
        self.assertIn("test_key", stats["cache_keys"])
        
        # Test limpiar cache
        cache_manager.clear_cache()
        stats = cache_manager.get_cache_stats()
        self.assertEqual(stats["cached_queries"], 0)
        
        cache_manager.close()
        
    def test_cache_ttl_expiration(self):
        """Test expiración de cache por TTL"""
        # Configurar cache con TTL muy corto
        cache_config = DatabaseConfig(
            connection=ConnectionConfig(database_name=":memory:"),
            performance=PerformanceConfig(
                enable_query_cache=True,
                cache_ttl_seconds=1  # 1 segundo
            )
        )
        cache_manager = DatabaseManager(config=cache_config)
        
        # Establecer cache
        cache_manager._set_cache("test_key", "test_value")
        self.assertTrue(cache_manager._is_cache_valid("test_key"))
        
        # Simular expiración modificando timestamp
        old_time = datetime.now() - timedelta(seconds=2)
        cache_manager._cache_timestamps["test_key"] = old_time
        
        # Verificar que el cache ha expirado
        self.assertFalse(cache_manager._is_cache_valid("test_key"))
        self.assertIsNone(cache_manager._get_cache("test_key"))
        
        cache_manager.close()
        
    def test_cache_disabled(self):
        """Test comportamiento con cache deshabilitado"""
        # Configurar manager sin cache
        no_cache_config = DatabaseConfig(
            connection=ConnectionConfig(database_name=":memory:"),
            performance=PerformanceConfig(enable_query_cache=False)
        )
        no_cache_manager = DatabaseManager(config=no_cache_config)
        
        # Verificar que el cache está deshabilitado
        self.assertIsNone(no_cache_manager._query_cache)
        self.assertIsNone(no_cache_manager._cache_timestamps)
        
        # Test estadísticas con cache deshabilitado
        stats = no_cache_manager.get_cache_stats()
        self.assertFalse(stats["cache_enabled"])
        
        no_cache_manager.close()
        
    @patch('src.database.database.Portfolio')
    def test_portfolio_initialization(self, mock_portfolio):
        """Test inicialización de portfolio con configuración"""
        # Configurar mock
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # No existe portfolio
        
        with patch.object(self.db_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            # Llamar inicialización
            self.db_manager.initialize_base_portfolio()
            
            # Verificar que se intentó crear portfolio
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            
    def test_session_configuration(self):
        """Test configuración de sesiones"""
        # Verificar configuración de sesión aplicada
        session = self.db_manager.get_session()
        
        # Verificar que la sesión se crea correctamente
        self.assertIsNotNone(session)
        
        # Limpiar
        session.close()
        
    def test_context_manager_session(self):
        """Test context manager para sesiones"""
        # Test uso normal
        with self.db_manager.get_db_session() as session:
            self.assertIsNotNone(session)
            
        # Test con excepción
        try:
            with self.db_manager.get_db_session() as session:
                raise Exception("Test exception")
        except Exception:
            pass  # Esperado
            
    def test_logging_configuration(self):
        """Test configuración de logging"""
        # Verificar que el logger se configura
        self.assertIsNotNone(self.db_manager.logger)
        
        # Test con configuración de desarrollo
        dev_config = DEVELOPMENT_DATABASE_CONFIG
        dev_manager = DatabaseManager(config=dev_config)
        
        # Verificar nivel de logging
        import logging
        self.assertEqual(dev_manager.logger.level, logging.DEBUG)
        
        dev_manager.close()


class TestDatabaseManagerMethods(unittest.TestCase):
    """
    🧪 Tests para métodos específicos del DatabaseManager
    """
    
    def setUp(self):
        """Configuración inicial"""
        self.db_manager = DatabaseManager(config=TEST_DATABASE_CONFIG)
        
    def tearDown(self):
        """Limpieza"""
        self.db_manager.close()
        
    @patch('src.database.database.Portfolio')
    def test_get_portfolio_summary_with_cache(self, mock_portfolio):
        """Test get_portfolio_summary con cache"""
        # Configurar cache habilitado
        cache_config = TEST_DATABASE_CONFIG
        cache_config.performance.enable_query_cache = True
        cache_manager = DatabaseManager(config=cache_config)
        
        # Mock de datos
        mock_portfolio_item = MagicMock()
        mock_portfolio_item.current_value = 1000.0
        mock_portfolio_item.unrealized_pnl = 50.0
        mock_portfolio_item.symbol = "BTC"
        mock_portfolio_item.quantity = 0.1
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = [mock_portfolio_item]
        
        with patch.object(cache_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            # Primera llamada - debe consultar DB
            result1 = cache_manager.get_portfolio_summary()
            self.assertIn("total_value", result1)
            
            # Segunda llamada - debe usar cache
            result2 = cache_manager.get_portfolio_summary()
            self.assertEqual(result1, result2)
            
        cache_manager.close()
        
    @patch('src.database.database.Trade')
    def test_get_active_trades_with_limit(self, mock_trade):
        """Test get_active_trades con límite configurado"""
        # Mock de datos
        mock_trade_item = MagicMock()
        mock_trade_item.id = 1
        mock_trade_item.symbol = "BTCUSDT"
        mock_trade_item.trade_type = "BUY"
        mock_trade_item.quantity = 0.1
        mock_trade_item.entry_price = 50000.0
        mock_trade_item.stop_loss = 48000.0
        mock_trade_item.take_profit = 55000.0
        mock_trade_item.pnl = 100.0
        mock_trade_item.status = "OPEN"
        mock_trade_item.entry_time = datetime.now()
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [mock_trade_item]
        
        with patch.object(self.db_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            # Test con límite personalizado
            result = self.db_manager.get_active_trades(limit=10)
            
            # Verificar que se aplicó el límite
            mock_query.limit.assert_called_with(10)
            
            # Verificar estructura del resultado
            self.assertIsInstance(result, list)
            if result:
                trade = result[0]
                self.assertIn('id', trade)
                self.assertIn('symbol', trade)
                self.assertIn('side', trade)
                
    @patch('src.database.database.Trade')
    def test_get_last_trade_for_symbol_with_cache(self, mock_trade):
        """Test get_last_trade_for_symbol con cache"""
        # Configurar cache
        cache_config = TEST_DATABASE_CONFIG
        cache_config.performance.enable_query_cache = True
        cache_manager = DatabaseManager(config=cache_config)
        
        # Mock de trade
        mock_trade_item = MagicMock()
        mock_trade_item.exit_price = None
        mock_trade_item.entry_price = 50000.0
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = mock_trade_item
        
        with patch.object(cache_manager, 'get_db_session') as mock_get_session:
            mock_get_session.return_value.__enter__.return_value = mock_session
            
            # Primera llamada
            price1 = cache_manager.get_last_trade_for_symbol("BTCUSDT")
            self.assertEqual(price1, 50000.0)
            
            # Segunda llamada - debe usar cache
            price2 = cache_manager.get_last_trade_for_symbol("BTCUSDT")
            self.assertEqual(price1, price2)
            
        cache_manager.close()


def run_comprehensive_test():
    """
    🧪 Ejecutar suite completa de tests para database optimizations
    """
    print("\n🧪 === EJECUTANDO TESTS DE DATABASE OPTIMIZATIONS ===")
    
    # Test configuraciones
    print("\n📋 Testing configuraciones...")
    config_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseConfig)
    config_result = unittest.TextTestRunner(verbosity=2).run(config_suite)
    
    # Test optimizaciones
    print("\n⚡ Testing optimizaciones...")
    opt_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseManagerOptimizations)
    opt_result = unittest.TextTestRunner(verbosity=2).run(opt_suite)
    
    # Test métodos específicos
    print("\n🔧 Testing métodos específicos...")
    methods_suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseManagerMethods)
    methods_result = unittest.TextTestRunner(verbosity=2).run(methods_suite)
    
    # Resumen
    total_tests = (config_result.testsRun + opt_result.testsRun + methods_result.testsRun)
    total_failures = len(config_result.failures) + len(opt_result.failures) + len(methods_result.failures)
    total_errors = len(config_result.errors) + len(opt_result.errors) + len(methods_result.errors)
    
    print(f"\n📊 === RESUMEN DE TESTS ===")
    print(f"✅ Tests ejecutados: {total_tests}")
    print(f"❌ Fallos: {total_failures}")
    print(f"💥 Errores: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("🎉 ¡Todos los tests pasaron exitosamente!")
        return True
    else:
        print("⚠️ Algunos tests fallaron. Revisar detalles arriba.")
        return False


if __name__ == "__main__":
    # Ejecutar tests
    success = run_comprehensive_test()
    
    if success:
        print("\n🚀 Database optimizations funcionando correctamente!")
    else:
        print("\n🔧 Revisar y corregir errores en database optimizations.")
        exit(1)