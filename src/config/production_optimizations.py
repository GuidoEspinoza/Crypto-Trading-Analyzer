"""
🚀 Configuraciones de Optimización para Producción
Configuraciones específicas para maximizar rendimiento en servidor.

Desarrollado por: Experto en Trading & Programación
"""

import os
from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class ProductionOptimizations:
    """Configuraciones optimizadas para producción en servidor."""
    
    # 🔥 OPTIMIZACIONES DE MEMORIA
    memory_optimizations: Dict[str, Any] = field(default_factory=lambda: {
        'enable_memory_pooling': True,
        'max_memory_usage_mb': 1024,  # 1GB límite
        'garbage_collection_interval': 300,  # 5 minutos
        'cache_cleanup_threshold': 0.8,  # Limpiar al 80% de uso
        'dataframe_memory_optimization': True,
        'numpy_memory_mapping': True,
        'pandas_categorical_optimization': True
    })
    
    # ⚡ OPTIMIZACIONES DE CPU
    cpu_optimizations: Dict[str, Any] = field(default_factory=lambda: {
        'enable_multiprocessing': True,
        'max_worker_processes': min(4, os.cpu_count() or 2),
        'async_io_enabled': True,
        'vectorized_calculations': True,
        'numba_jit_compilation': True,
        'parallel_indicator_calculation': True,
        'cpu_affinity_enabled': True
    })
    
    # 🗄️ OPTIMIZACIONES DE BASE DE DATOS
    database_optimizations: Dict[str, Any] = field(default_factory=lambda: {
        'connection_pool_size': 20,
        'max_overflow': 30,
        'pool_pre_ping': True,
        'pool_recycle': 3600,  # 1 hora
        'query_cache_size': 1000,
        'batch_insert_size': 500,
        'index_optimization': True,
        'vacuum_schedule': 'daily',
        'analyze_schedule': 'hourly'
    })
    
    # 🌐 OPTIMIZACIONES DE RED
    network_optimizations: Dict[str, Any] = field(default_factory=lambda: {
        'connection_timeout': 10,
        'read_timeout': 15,
        'max_retries': 5,
        'retry_backoff_factor': 0.3,
        'keep_alive_enabled': True,
        'compression_enabled': True,
        'http2_enabled': True,
        'dns_cache_ttl': 300
    })
    
    # 📊 OPTIMIZACIONES DE MONITOREO
    monitoring_optimizations: Dict[str, Any] = field(default_factory=lambda: {
        'metrics_collection_interval': 30,  # 30 segundos
        'log_rotation_size_mb': 100,
        'log_retention_days': 30,
        'performance_profiling': False,  # Solo en debug
        'memory_profiling': False,  # Solo en debug
        'async_logging': True,
        'structured_logging': True
    })
    
    # 🔄 OPTIMIZACIONES DE CACHE
    cache_optimizations: Dict[str, Any] = field(default_factory=lambda: {
        'redis_max_memory': '256mb',
        'redis_eviction_policy': 'allkeys-lru',
        'application_cache_size': 1000,
        'price_data_cache_ttl': 60,  # 1 minuto
        'indicator_cache_ttl': 300,  # 5 minutos
        'market_data_cache_ttl': 30,  # 30 segundos
        'compression_enabled': True
    })

@dataclass
class SecurityOptimizations:
    """Configuraciones de seguridad para producción."""
    
    security_settings: Dict[str, Any] = field(default_factory=lambda: {
        'api_rate_limiting': True,
        'max_requests_per_minute': 100,
        'enable_cors': False,
        'allowed_origins': [],
        'api_key_rotation_days': 30,
        'session_timeout_minutes': 60,
        'enable_2fa': True,
        'audit_logging': True,
        'encrypt_sensitive_data': True,
        'secure_headers': True
    })

@dataclass
class AlertingOptimizations:
    """Sistema de alertas optimizado para producción."""
    
    alerting_config: Dict[str, Any] = field(default_factory=lambda: {
        'critical_alerts': {
            'max_drawdown_threshold': 0.15,  # 15%
            'system_error_threshold': 3,  # 3 errores consecutivos
            'memory_usage_threshold': 0.9,  # 90%
            'cpu_usage_threshold': 0.8,  # 80%
            'disk_usage_threshold': 0.85,  # 85%
        },
        'notification_channels': {
            'email_enabled': True,
            'webhook_enabled': True,
            'dashboard_alerts': True,
            'log_alerts': True
        },
        'alert_throttling': {
            'max_alerts_per_hour': 10,
            'duplicate_alert_suppression': True,
            'escalation_enabled': True
        }
    })

def get_production_config() -> Dict[str, Any]:
    """Obtener configuración completa de producción."""
    prod_opt = ProductionOptimizations()
    sec_opt = SecurityOptimizations()
    alert_opt = AlertingOptimizations()
    
    return {
        'production_optimizations': {
            'memory': prod_opt.memory_optimizations,
            'cpu': prod_opt.cpu_optimizations,
            'database': prod_opt.database_optimizations,
            'network': prod_opt.network_optimizations,
            'monitoring': prod_opt.monitoring_optimizations,
            'cache': prod_opt.cache_optimizations
        },
        'security': sec_opt.security_settings,
        'alerting': alert_opt.alerting_config,
        'environment': 'production',
        'debug_mode': False,
        'profiling_enabled': False
    }

def apply_production_optimizations():
    """Aplicar optimizaciones de producción al sistema."""
    config = get_production_config()
    
    # Configurar variables de entorno
    os.environ.update({
        'PYTHONOPTIMIZE': '2',  # Optimización máxima
        'PYTHONUNBUFFERED': '1',
        'MALLOC_ARENA_MAX': '2',  # Reducir fragmentación de memoria
        'PYTHONDONTWRITEBYTECODE': '1'
    })
    
    return config

# Configuración específica para diferentes tipos de servidor
SERVER_CONFIGS = {
    'small': {  # 1-2 CPU, 2-4GB RAM
        'max_positions': 4,
        'analysis_interval': 90,
        'worker_processes': 1,
        'cache_size': 500
    },
    'medium': {  # 2-4 CPU, 4-8GB RAM
        'max_positions': 6,
        'analysis_interval': 75,
        'worker_processes': 2,
        'cache_size': 1000
    },
    'large': {  # 4+ CPU, 8+ GB RAM
        'max_positions': 8,
        'analysis_interval': 60,
        'worker_processes': 4,
        'cache_size': 2000
    }
}

def get_server_config(server_type: str = 'medium') -> Dict[str, Any]:
    """Obtener configuración específica según tipo de servidor."""
    return SERVER_CONFIGS.get(server_type, SERVER_CONFIGS['medium'])