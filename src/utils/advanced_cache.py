#!/usr/bin/env python3
"""
🚀 Sistema de Cache Avanzado para Indicadores
Optimiza el rendimiento almacenando resultados de cálculos costosos
"""

import time
import hashlib
import pickle
from typing import Dict, Any, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta

class IndicatorCache:
    """
    📦 Cache inteligente para indicadores técnicos
    Almacena resultados con TTL y invalidación automática
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl  # 5 minutos por defecto
        self.access_times: Dict[str, float] = {}
    
    def _generate_key(self, *args, **kwargs) -> str:
        """
        🔑 Generar clave única para el cache
        """
        key_data = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """
        ⏰ Verificar si una entrada del cache ha expirado
        """
        if key not in self.cache:
            return True
        
        entry = self.cache[key]
        if 'expires_at' not in entry:
            return True
        
        return time.time() > entry['expires_at']
    
    def _cleanup_expired(self):
        """
        🧹 Limpiar entradas expiradas del cache
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if 'expires_at' in entry and current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
    
    def _evict_lru(self):
        """
        🗑️ Eliminar la entrada menos recientemente usada
        """
        if not self.access_times:
            return
        
        lru_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[lru_key]
        del self.access_times[lru_key]
    
    def get(self, key: str) -> Optional[Any]:
        """
        📖 Obtener valor del cache
        """
        if self._is_expired(key):
            if key in self.cache:
                del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]['value']
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        💾 Almacenar valor en el cache
        """
        # Limpiar entradas expiradas
        self._cleanup_expired()
        
        # Si el cache está lleno, eliminar LRU
        if len(self.cache) >= self.max_size:
            self._evict_lru()
        
        # Calcular tiempo de expiración
        ttl = ttl or self.default_ttl
        expires_at = time.time() + ttl
        
        # Almacenar entrada
        self.cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        self.access_times[key] = time.time()
    
    def invalidate(self, pattern: str = None) -> None:
        """
        🔄 Invalidar entradas del cache
        """
        if pattern is None:
            # Limpiar todo el cache
            self.cache.clear()
            self.access_times.clear()
        else:
            # Limpiar entradas que coincidan con el patrón
            keys_to_remove = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_remove:
                del self.cache[key]
                if key in self.access_times:
                    del self.access_times[key]
    
    def get_indicator(self, symbol: str, timeframe: str, indicator_name: str, params: Dict) -> Optional[Any]:
        """
        📖 Obtener indicador específico del cache
        """
        key = self._generate_indicator_key(symbol, timeframe, indicator_name, params)
        return self.get(key)
    
    def cache_indicator(self, symbol: str, timeframe: str, indicator_name: str, params: Dict, result: Any, ttl: Optional[int] = None) -> None:
        """
        💾 Almacenar indicador específico en el cache
        """
        key = self._generate_indicator_key(symbol, timeframe, indicator_name, params)
        self.set(key, result, ttl)
    
    def _generate_indicator_key(self, symbol: str, timeframe: str, indicator_name: str, params: Dict) -> str:
        """
        🔑 Generar clave específica para indicadores
        """
        params_str = "_".join([f"{k}_{v}" for k, v in sorted(params.items())])
        key_data = f"{symbol}_{timeframe}_{indicator_name}_{params_str}"
        return hashlib.md5(key_data.encode()).hexdigest()[:16]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        📊 Obtener estadísticas del cache
        """
        current_time = time.time()
        expired_count = sum(
            1 for entry in self.cache.values()
            if 'expires_at' in entry and current_time > entry['expires_at']
        )
        
        return {
            'total_entries': len(self.cache),
            'expired_entries': expired_count,
            'active_entries': len(self.cache) - expired_count,
            'max_size': self.max_size,
            'usage_percentage': (len(self.cache) / self.max_size) * 100
        }

# Instancia global del cache
indicator_cache = IndicatorCache(max_size=1000, default_ttl=300)

def cached_function(ttl: int = 300, cache_key_func: Optional[Callable] = None):
    """
    🎯 Decorador para cachear funciones automáticamente
    
    Args:
        ttl: Tiempo de vida en segundos
        cache_key_func: Función personalizada para generar la clave del cache
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave del cache
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{indicator_cache._generate_key(*args, **kwargs)}"
            
            # Intentar obtener del cache
            cached_result = indicator_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = func(*args, **kwargs)
            indicator_cache.set(cache_key, result, ttl)
            
            return result
        
        # Agregar método para invalidar cache específico de esta función
        wrapper.invalidate_cache = lambda pattern=None: indicator_cache.invalidate(
            pattern or func.__name__
        )
        
        return wrapper
    
    return decorator

def clear_indicator_cache(symbol: str = None, timeframe: str = None):
    """
    🧹 Limpiar cache de indicadores específicos
    
    Args:
        symbol: Símbolo específico a limpiar (opcional)
        timeframe: Timeframe específico a limpiar (opcional)
    """
    if symbol and timeframe:
        pattern = f"{symbol}_{timeframe}"
    elif symbol:
        pattern = symbol
    elif timeframe:
        pattern = timeframe
    else:
        pattern = None
    
    indicator_cache.invalidate(pattern)

def get_cache_stats() -> Dict[str, Any]:
    """
    📈 Obtener estadísticas del cache de indicadores
    """
    return indicator_cache.get_stats()

# Funciones de utilidad adicionales
def warm_cache(symbols: list, timeframes: list, indicators: list):
    """
    🔥 Pre-calentar el cache con indicadores comunes
    """
    # Esta función se puede implementar para pre-calcular indicadores comunes
    pass

def cache_health_check() -> Dict[str, Any]:
    """
    🏥 Verificar la salud del sistema de cache
    """
    stats = get_cache_stats()
    
    health_status = {
        'status': 'healthy',
        'issues': [],
        'recommendations': []
    }
    
    # Verificar uso excesivo
    if stats['usage_percentage'] > 90:
        health_status['status'] = 'warning'
        health_status['issues'].append('Cache usage above 90%')
        health_status['recommendations'].append('Consider increasing cache size or reducing TTL')
    
    # Verificar muchas entradas expiradas
    if stats['expired_entries'] > stats['active_entries']:
        health_status['issues'].append('High number of expired entries')
        health_status['recommendations'].append('Run cache cleanup more frequently')
    
    return {
        **health_status,
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    }