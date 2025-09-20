"""
🚀 Configuración Optimizada para Producción
Configuración completa para despliegue en servidor.

Desarrollado por: Experto en Trading & Programación
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import logging

@dataclass
class ProductionConfig:
    """Configuración para producción."""
    
    # === CONFIGURACIÓN DEL SERVIDOR ===
    SERVER_TYPE: str = "production"  # production, staging, development
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    WORKERS: int = 4
    MAX_CONNECTIONS: int = 1000
    
    # === BASE DE DATOS ===
    DATABASE_URL: str = "postgresql://trading_user:secure_password@localhost:5432/trading_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 3600
    
    # === REDIS CACHE ===
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
    
    # === SEGURIDAD ===
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hora
    CORS_ORIGINS: List[str] = field(default_factory=lambda: ["https://yourdomain.com"])
    RATE_LIMIT: str = "100/minute"
    
    # === TRADING ===
    BINANCE_API_KEY: str = ""
    BINANCE_SECRET_KEY: str = ""
    BINANCE_TESTNET: bool = False  # False para producción
    MAX_CONCURRENT_TRADES: int = 10
    POSITION_SIZE_LIMIT: float = 0.02  # 2% del balance por trade
    DAILY_LOSS_LIMIT: float = 0.05  # 5% pérdida diaria máxima
    
    # === MONITOREO ===
    ENABLE_MONITORING: bool = True
    METRICS_INTERVAL: int = 30  # segundos
    ALERT_WEBHOOK_URL: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # === BACKUP ===
    ENABLE_BACKUP: bool = True
    BACKUP_DIRECTORY: str = "/var/backups/trading"
    S3_BUCKET: Optional[str] = None
    AWS_ACCESS_KEY: Optional[str] = None
    AWS_SECRET_KEY: Optional[str] = None
    
    # === PERFORMANCE ===
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 300  # 5 minutos
    ASYNC_WORKERS: int = 8
    MAX_MEMORY_USAGE: float = 0.8  # 80% de RAM máxima

class ProductionOptimizer:
    """Optimizador para entorno de producción."""
    
    def __init__(self, config: ProductionConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def get_database_config(self) -> Dict[str, Any]:
        """Configuración optimizada de base de datos."""
        return {
            'url': self.config.DATABASE_URL,
            'pool_size': self.config.DATABASE_POOL_SIZE,
            'max_overflow': self.config.DATABASE_MAX_OVERFLOW,
            'pool_timeout': self.config.DATABASE_POOL_TIMEOUT,
            'pool_recycle': self.config.DATABASE_POOL_RECYCLE,
            'pool_pre_ping': True,
            'echo': False,  # Desactivar en producción
            'connect_args': {
                'connect_timeout': 10,
                'command_timeout': 60,
                'server_settings': {
                    'jit': 'off',  # Optimización para consultas frecuentes
                    'shared_preload_libraries': 'pg_stat_statements',
                }
            }
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Configuración optimizada de Redis."""
        return {
            'url': self.config.REDIS_URL,
            'max_connections': self.config.REDIS_MAX_CONNECTIONS,
            'socket_timeout': self.config.REDIS_SOCKET_TIMEOUT,
            'socket_connect_timeout': self.config.REDIS_SOCKET_CONNECT_TIMEOUT,
            'retry_on_timeout': True,
            'health_check_interval': 30,
            'decode_responses': True
        }
    
    def get_trading_config(self) -> Dict[str, Any]:
        """Configuración optimizada de trading."""
        return {
            'api_key': self.config.BINANCE_API_KEY,
            'secret_key': self.config.BINANCE_SECRET_KEY,
            'testnet': self.config.BINANCE_TESTNET,
            'max_concurrent_trades': self.config.MAX_CONCURRENT_TRADES,
            'position_size_limit': self.config.POSITION_SIZE_LIMIT,
            'daily_loss_limit': self.config.DAILY_LOSS_LIMIT,
            'request_timeout': 10,
            'recv_window': 5000,
            'rate_limit': {
                'orders_per_second': 10,
                'orders_per_day': 200000,
                'weight_per_minute': 1200
            }
        }
    
    def get_monitoring_config(self) -> Dict[str, Any]:
        """Configuración de monitoreo."""
        return {
            'enabled': self.config.ENABLE_MONITORING,
            'metrics_interval': self.config.METRICS_INTERVAL,
            'webhook_url': self.config.ALERT_WEBHOOK_URL,
            'log_level': self.config.LOG_LEVEL,
            'alerts': {
                'cpu_threshold': 80,
                'memory_threshold': 85,
                'disk_threshold': 90,
                'response_time_threshold': 2.0,
                'error_rate_threshold': 0.05
            }
        }
    
    def get_backup_config(self) -> Dict[str, Any]:
        """Configuración de backup."""
        return {
            'enabled': self.config.ENABLE_BACKUP,
            'backup_directory': self.config.BACKUP_DIRECTORY,
            's3_bucket': self.config.S3_BUCKET,
            'aws_access_key': self.config.AWS_ACCESS_KEY,
            'aws_secret_key': self.config.AWS_SECRET_KEY,
            'schedules': {
                'database': 'daily',
                'config': 'daily',
                'logs': 'daily',
                'trading_data': 'hourly',
                'full_system': 'weekly'
            }
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Configuración de seguridad."""
        return {
            'secret_key': self.config.SECRET_KEY,
            'jwt_secret': self.config.JWT_SECRET_KEY,
            'jwt_expires': self.config.JWT_ACCESS_TOKEN_EXPIRES,
            'cors_origins': self.config.CORS_ORIGINS,
            'rate_limit': self.config.RATE_LIMIT,
            'ssl_required': True,
            'secure_headers': True,
            'api_key_rotation_days': 30
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """Configuración de rendimiento."""
        return {
            'caching_enabled': self.config.ENABLE_CACHING,
            'cache_ttl': self.config.CACHE_TTL,
            'async_workers': self.config.ASYNC_WORKERS,
            'max_memory_usage': self.config.MAX_MEMORY_USAGE,
            'compression': {
                'enabled': True,
                'level': 6,
                'min_size': 1024
            },
            'connection_pooling': {
                'enabled': True,
                'max_size': 100,
                'timeout': 30
            }
        }
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Configuración de logging."""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'detailed': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                },
                'json': {
                    'format': '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.config.LOG_LEVEL,
                    'formatter': 'detailed'
                },
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/trading_system.log',
                    'maxBytes': 10485760,  # 10MB
                    'backupCount': 5,
                    'level': self.config.LOG_LEVEL,
                    'formatter': 'json'
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': 'logs/errors.log',
                    'maxBytes': 10485760,
                    'backupCount': 5,
                    'level': 'ERROR',
                    'formatter': 'json'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': self.config.LOG_LEVEL,
                    'propagate': False
                },
                'trading': {
                    'handlers': ['console', 'file', 'error_file'],
                    'level': 'INFO',
                    'propagate': False
                }
            }
        }
    
    def validate_config(self) -> bool:
        """Validar configuración de producción."""
        errors = []
        
        # Validar variables críticas
        if not self.config.BINANCE_API_KEY:
            errors.append("BINANCE_API_KEY no configurada")
        
        if not self.config.BINANCE_SECRET_KEY:
            errors.append("BINANCE_SECRET_KEY no configurada")
        
        if self.config.SECRET_KEY == "your-super-secret-key-change-in-production":
            errors.append("SECRET_KEY debe cambiarse en producción")
        
        if not self.config.DATABASE_URL or "localhost" in self.config.DATABASE_URL:
            errors.append("DATABASE_URL debe configurarse para producción")
        
        # Validar límites de seguridad
        if self.config.POSITION_SIZE_LIMIT > 0.1:
            errors.append("POSITION_SIZE_LIMIT muy alto para producción (>10%)")
        
        if self.config.DAILY_LOSS_LIMIT > 0.1:
            errors.append("DAILY_LOSS_LIMIT muy alto para producción (>10%)")
        
        if errors:
            for error in errors:
                self.logger.error(f"❌ Error de configuración: {error}")
            return False
        
        self.logger.info("✅ Configuración de producción validada")
        return True
    
    def setup_environment(self):
        """Configurar variables de entorno."""
        env_vars = {
            'PYTHONPATH': '/app/src',
            'PYTHONUNBUFFERED': '1',
            'TZ': 'UTC',
            'LANG': 'en_US.UTF-8',
            'LC_ALL': 'en_US.UTF-8'
        }
        
        for key, value in env_vars.items():
            os.environ.setdefault(key, value)
    
    def get_docker_config(self) -> Dict[str, Any]:
        """Configuración para Docker."""
        return {
            'image': 'crypto-trading-analyzer:latest',
            'restart': 'unless-stopped',
            'environment': {
                'SERVER_TYPE': self.config.SERVER_TYPE,
                'DATABASE_URL': self.config.DATABASE_URL,
                'REDIS_URL': self.config.REDIS_URL,
                'LOG_LEVEL': self.config.LOG_LEVEL
            },
            'volumes': [
                './logs:/app/logs',
                './data:/app/data',
                './backups:/app/backups'
            ],
            'ports': [f"{self.config.PORT}:8080"],
            'healthcheck': {
                'test': ['CMD', 'curl', '-f', 'http://localhost:8080/health'],
                'interval': '30s',
                'timeout': '10s',
                'retries': 3,
                'start_period': '40s'
            },
            'deploy': {
                'resources': {
                    'limits': {
                        'cpus': '2.0',
                        'memory': '4G'
                    },
                    'reservations': {
                        'cpus': '1.0',
                        'memory': '2G'
                    }
                }
            }
        }

def create_production_config() -> ProductionConfig:
    """Crear configuración de producción desde variables de entorno."""
    return ProductionConfig(
        # Servidor
        SERVER_TYPE=os.getenv('SERVER_TYPE', 'production'),
        HOST=os.getenv('HOST', '0.0.0.0'),
        PORT=int(os.getenv('PORT', '8080')),
        WORKERS=int(os.getenv('WORKERS', '4')),
        
        # Base de datos
        DATABASE_URL=os.getenv('DATABASE_URL', 'postgresql://trading_user:password@localhost:5432/trading_db'),
        DATABASE_POOL_SIZE=int(os.getenv('DATABASE_POOL_SIZE', '20')),
        
        # Redis
        REDIS_URL=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        
        # Seguridad
        SECRET_KEY=os.getenv('SECRET_KEY', 'change-me-in-production'),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'change-me-too'),
        
        # Trading
        BINANCE_API_KEY=os.getenv('BINANCE_API_KEY', ''),
        BINANCE_SECRET_KEY=os.getenv('BINANCE_SECRET_KEY', ''),
        BINANCE_TESTNET=os.getenv('BINANCE_TESTNET', 'false').lower() == 'true',
        
        # Monitoreo
        ALERT_WEBHOOK_URL=os.getenv('ALERT_WEBHOOK_URL'),
        LOG_LEVEL=os.getenv('LOG_LEVEL', 'INFO'),
        
        # Backup
        S3_BUCKET=os.getenv('S3_BUCKET'),
        AWS_ACCESS_KEY=os.getenv('AWS_ACCESS_KEY'),
        AWS_SECRET_KEY=os.getenv('AWS_SECRET_KEY')
    )

def get_production_optimizer() -> ProductionOptimizer:
    """Obtener optimizador configurado para producción."""
    config = create_production_config()
    optimizer = ProductionOptimizer(config)
    
    # Validar configuración
    if not optimizer.validate_config():
        raise ValueError("Configuración de producción inválida")
    
    # Configurar entorno
    optimizer.setup_environment()
    
    return optimizer

if __name__ == "__main__":
    # Ejemplo de uso
    optimizer = get_production_optimizer()
    
    print("🚀 Configuración de Producción:")
    print(f"  - Base de datos: {optimizer.get_database_config()}")
    print(f"  - Redis: {optimizer.get_redis_config()}")
    print(f"  - Trading: {optimizer.get_trading_config()}")
    print(f"  - Monitoreo: {optimizer.get_monitoring_config()}")
    print(f"  - Backup: {optimizer.get_backup_config()}")
    print(f"  - Seguridad: {optimizer.get_security_config()}")
    print(f"  - Rendimiento: {optimizer.get_performance_config()}")