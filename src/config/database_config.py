#!/usr/bin/env python3
"""
🗄️ Universal Trading Analyzer - Database Configuration
Configuración parametrizada para el gestor de base de datos
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import os
import logging
from .global_constants import GLOBAL_INITIAL_BALANCE, USDT_BASE_PRICE, BASE_CURRENCY


@dataclass
class ConnectionConfig:
    """
    🔗 Configuración de conexión a la base de datos
    """
    database_name: str = "trading_bot.db"
    database_url: Optional[str] = None
    check_same_thread: bool = False  # Para SQLite
    echo_sql: bool = False  # Mostrar queries SQL en logs
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600  # 1 hora
    
    def get_database_url(self) -> str:
        """
        🔗 Obtener URL de la base de datos
        """
        if self.database_url:
            return self.database_url
            
        # Crear ruta por defecto
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(current_dir, "database", self.database_name)
        return f"sqlite:///{db_path}"


@dataclass
class SessionConfig:
    """
    🔄 Configuración de sesiones de base de datos
    """
    autocommit: bool = False
    autoflush: bool = False
    expire_on_commit: bool = True
    

@dataclass
class PortfolioConfig:
    """
    💼 Configuración del portfolio inicial
    """
    initial_usdt_amount: float = GLOBAL_INITIAL_BALANCE
    base_currency: str = BASE_CURRENCY
    base_price: float = USDT_BASE_PRICE
    auto_initialize: bool = True
    min_quantity_threshold: float = 0.00001  # Filtrar cantidades muy pequeñas
    

@dataclass
class LoggingConfig:
    """
    📝 Configuración de logging para database
    """
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_sql_logging: bool = False
    log_file: Optional[str] = None
    
    def get_logging_level(self) -> int:
        """
        📝 Convertir string level a logging level
        """
        return getattr(logging, self.level.upper(), logging.INFO)


@dataclass
class QueryConfig:
    """
    🔍 Configuración de consultas y filtros
    """
    default_trade_status: str = "OPEN"
    max_results_limit: int = 1000
    default_order_by: str = "entry_time"
    order_direction: str = "desc"  # asc o desc
    

@dataclass
class PerformanceConfig:
    """
    ⚡ Configuración de rendimiento
    """
    enable_query_cache: bool = True
    cache_ttl_seconds: int = 300  # 5 minutos
    batch_size: int = 100
    connection_pool_pre_ping: bool = True
    

@dataclass
class DatabaseConfig:
    """
    🗄️ Configuración principal del gestor de base de datos
    """
    connection: ConnectionConfig = field(default_factory=ConnectionConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    portfolio: PortfolioConfig = field(default_factory=PortfolioConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    query: QueryConfig = field(default_factory=QueryConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        📋 Convertir configuración a diccionario
        """
        return {
            "connection": {
                "database_name": self.connection.database_name,
                "database_url": self.connection.database_url,
                "check_same_thread": self.connection.check_same_thread,
                "echo_sql": self.connection.echo_sql,
                "pool_size": self.connection.pool_size,
                "max_overflow": self.connection.max_overflow,
                "pool_timeout": self.connection.pool_timeout,
                "pool_recycle": self.connection.pool_recycle
            },
            "session": {
                "autocommit": self.session.autocommit,
                "autoflush": self.session.autoflush,
                "expire_on_commit": self.session.expire_on_commit
            },
            "portfolio": {
                "initial_usdt_amount": self.portfolio.initial_usdt_amount,
                "base_currency": self.portfolio.base_currency,
                "base_price": self.portfolio.base_price,
                "auto_initialize": self.portfolio.auto_initialize,
                "min_quantity_threshold": self.portfolio.min_quantity_threshold
            },
            "logging": {
                "level": self.logging.level,
                "format": self.logging.format,
                "enable_sql_logging": self.logging.enable_sql_logging,
                "log_file": self.logging.log_file
            },
            "query": {
                "default_trade_status": self.query.default_trade_status,
                "max_results_limit": self.query.max_results_limit,
                "default_order_by": self.query.default_order_by,
                "order_direction": self.query.order_direction
            },
            "performance": {
                "enable_query_cache": self.performance.enable_query_cache,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "batch_size": self.performance.batch_size,
                "connection_pool_pre_ping": self.performance.connection_pool_pre_ping
            }
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'DatabaseConfig':
        """
        📋 Crear configuración desde diccionario
        """
        connection_config = ConnectionConfig(**config_dict.get("connection", {}))
        session_config = SessionConfig(**config_dict.get("session", {}))
        portfolio_config = PortfolioConfig(**config_dict.get("portfolio", {}))
        logging_config = LoggingConfig(**config_dict.get("logging", {}))
        query_config = QueryConfig(**config_dict.get("query", {}))
        performance_config = PerformanceConfig(**config_dict.get("performance", {}))
        
        return cls(
            connection=connection_config,
            session=session_config,
            portfolio=portfolio_config,
            logging=logging_config,
            query=query_config,
            performance=performance_config
        )


# Configuración por defecto
DEFAULT_DATABASE_CONFIG = DatabaseConfig()

# Configuración para desarrollo (con más logging)
DEVELOPMENT_DATABASE_CONFIG = DatabaseConfig(
    connection=ConnectionConfig(
        echo_sql=True,
        database_name="trading_bot_dev.db"
    ),
    logging=LoggingConfig(
        level="DEBUG",
        enable_sql_logging=True
    ),
    performance=PerformanceConfig(
        enable_query_cache=False  # Desactivar cache en desarrollo
    )
)

# Configuración para producción (optimizada)
PRODUCTION_DATABASE_CONFIG = DatabaseConfig(
    connection=ConnectionConfig(
        echo_sql=False,
        pool_size=10,
        max_overflow=20,
        database_name="trading_bot_prod.db"
    ),
    logging=LoggingConfig(
        level="WARNING",
        enable_sql_logging=False
    ),
    performance=PerformanceConfig(
        enable_query_cache=True,
        cache_ttl_seconds=600,  # 10 minutos
        batch_size=200
    )
)

# Configuración para testing
TEST_DATABASE_CONFIG = DatabaseConfig(
    connection=ConnectionConfig(
        database_name=":memory:",  # Base de datos en memoria para tests
        echo_sql=False
    ),
    portfolio=PortfolioConfig(
        initial_usdt_amount=1000.0,  # Menor cantidad para tests
        auto_initialize=True
    ),
    logging=LoggingConfig(
        level="ERROR"  # Solo errores en tests
    ),
    performance=PerformanceConfig(
        enable_query_cache=False  # Sin cache en tests
    )
)


def get_database_config(profile: str = "default") -> DatabaseConfig:
    """
    🗄️ Obtener configuración de base de datos según el perfil
    
    Args:
        profile: Perfil de configuración (default, development, production, test)
        
    Returns:
        DatabaseConfig: Configuración de base de datos
    """
    profiles = {
        "default": DEFAULT_DATABASE_CONFIG,
        "development": DEVELOPMENT_DATABASE_CONFIG,
        "production": PRODUCTION_DATABASE_CONFIG,
        "test": TEST_DATABASE_CONFIG
    }
    
    config = profiles.get(profile, DEFAULT_DATABASE_CONFIG)
    
    # Log de configuración seleccionada
    logger = logging.getLogger(__name__)
    logger.info(f"🗄️ Database config loaded: {profile}")
    
    return config