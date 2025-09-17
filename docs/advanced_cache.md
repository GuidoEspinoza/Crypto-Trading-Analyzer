# 🚀 Sistema de Cache Avanzado para Indicadores

## Descripción General

El módulo `advanced_cache.py` proporciona un sistema de cache inteligente diseñado específicamente para optimizar el rendimiento de cálculos de indicadores técnicos en trading. Implementa un cache LRU (Least Recently Used) con TTL (Time To Live) automático y funcionalidades especializadas para el contexto de trading.

## Características Principales

### ✨ Funcionalidades Clave

- **Cache LRU con TTL**: Gestión automática de memoria con expiración temporal
- **Invalidación Inteligente**: Limpieza automática de entradas expiradas
- **Cache Específico para Indicadores**: Claves optimizadas para símbolo, timeframe e indicador
- **Decoradores de Cache**: Funciones automáticamente cacheables
- **Monitoreo de Salud**: Estadísticas y verificaciones de rendimiento
- **Gestión de Memoria**: Evicción automática cuando se alcanza el límite

## Arquitectura del Sistema

### Clase Principal: `IndicatorCache`

```python
class IndicatorCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300)
```

**Parámetros de Configuración:**
- `max_size`: Número máximo de entradas en cache (default: 1000)
- `default_ttl`: Tiempo de vida por defecto en segundos (default: 300 = 5 minutos)

### Estructura de Datos

```python
# Estructura interna del cache
cache = {
    'key_hash': {
        'value': Any,           # Resultado cacheado
        'expires_at': float,    # Timestamp de expiración
        'created_at': float     # Timestamp de creación
    }
}

access_times = {
    'key_hash': float       # Último acceso para LRU
}
```

## API de Uso

### Operaciones Básicas

#### Almacenar en Cache

```python
from src.utils.advanced_cache import indicator_cache

# Almacenar valor con TTL por defecto
indicator_cache.set('mi_clave', resultado, ttl=600)

# Almacenar indicador específico
indicator_cache.cache_indicator(
    symbol='BTCUSDT',
    timeframe='1h',
    indicator_name='RSI',
    params={'period': 14},
    result={'value': 65.5, 'signal': 'NEUTRAL'},
    ttl=300
)
```

#### Recuperar del Cache

```python
# Obtener valor por clave
resultado = indicator_cache.get('mi_clave')

# Obtener indicador específico
rsi_result = indicator_cache.get_indicator(
    symbol='BTCUSDT',
    timeframe='1h',
    indicator_name='RSI',
    params={'period': 14}
)
```

### Decorador de Cache Automático

```python
from src.utils.advanced_cache import cached_function

@cached_function(ttl=600)
def calcular_rsi(prices, period=14):
    # Cálculo costoso del RSI
    return resultado

# Uso automático del cache
rsi = calcular_rsi(price_data, period=14)  # Se cachea automáticamente
rsi2 = calcular_rsi(price_data, period=14) # Se obtiene del cache

# Invalidar cache específico
calcular_rsi.invalidate_cache('rsi')
```

### Gestión de Cache

#### Invalidación

```python
# Limpiar todo el cache
indicator_cache.invalidate()

# Limpiar por patrón
indicator_cache.invalidate('BTCUSDT')  # Todo lo de BTCUSDT
indicator_cache.invalidate('1h')       # Todo de timeframe 1h

# Funciones de utilidad
from src.utils.advanced_cache import clear_indicator_cache

clear_indicator_cache(symbol='BTCUSDT', timeframe='1h')
clear_indicator_cache(symbol='ETHUSDT')  # Solo símbolo
clear_indicator_cache(timeframe='5m')    # Solo timeframe
```

#### Estadísticas y Monitoreo

```python
from src.utils.advanced_cache import get_cache_stats, cache_health_check

# Obtener estadísticas
stats = get_cache_stats()
print(f"Entradas activas: {stats['active_entries']}")
print(f"Uso del cache: {stats['usage_percentage']:.1f}%")

# Verificar salud del sistema
health = cache_health_check()
if health['status'] == 'warning':
    print(f"Problemas detectados: {health['issues']}")
    print(f"Recomendaciones: {health['recommendations']}")
```

## Casos de Uso Comunes

### 1. Cache de Indicadores Técnicos

```python
# Ejemplo con múltiples indicadores
indicators = ['RSI', 'MACD', 'BB', 'SMA']
symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT']
timeframes = ['1h', '4h', '1d']

for symbol in symbols:
    for timeframe in timeframes:
        for indicator in indicators:
            # Verificar cache antes de calcular
            cached_result = indicator_cache.get_indicator(
                symbol, timeframe, indicator, {'period': 14}
            )
            
            if cached_result is None:
                # Calcular y cachear
                result = calculate_indicator(symbol, timeframe, indicator)
                indicator_cache.cache_indicator(
                    symbol, timeframe, indicator, 
                    {'period': 14}, result, ttl=300
                )
            else:
                result = cached_result
```

### 2. Cache con Decorador Personalizado

```python
def custom_cache_key(*args, **kwargs):
    """Generar clave personalizada para el cache"""
    symbol = kwargs.get('symbol', 'UNKNOWN')
    period = kwargs.get('period', 14)
    return f"custom_{symbol}_{period}"

@cached_function(ttl=900, cache_key_func=custom_cache_key)
def calculate_complex_indicator(data, symbol=None, period=14, **params):
    # Cálculo complejo que se beneficia del cache
    return complex_calculation(data, period, **params)
```

### 3. Gestión de Memoria en Producción

```python
import time
from src.utils.advanced_cache import indicator_cache, cache_health_check

def monitor_cache_health():
    """Monitoreo periódico del cache"""
    while True:
        health = cache_health_check()
        
        if health['status'] == 'warning':
            # Limpiar entradas expiradas
            indicator_cache._cleanup_expired()
            
            # Si sigue con problemas, limpiar cache antiguo
            if health['stats']['usage_percentage'] > 95:
                indicator_cache.invalidate()
                print("Cache limpiado por uso excesivo")
        
        time.sleep(60)  # Verificar cada minuto
```

## Configuración y Optimización

### Parámetros Recomendados

```python
# Para trading de alta frecuencia
hf_cache = IndicatorCache(max_size=5000, default_ttl=60)

# Para análisis a largo plazo
lt_cache = IndicatorCache(max_size=1000, default_ttl=3600)

# Para backtesting
bt_cache = IndicatorCache(max_size=10000, default_ttl=7200)
```

### Mejores Prácticas

1. **TTL Apropiado**: Ajustar según la frecuencia de actualización de datos
2. **Tamaño de Cache**: Balancear memoria disponible vs. hit rate
3. **Claves Específicas**: Usar parámetros relevantes en las claves
4. **Monitoreo Regular**: Verificar estadísticas periódicamente
5. **Invalidación Inteligente**: Limpiar cache cuando cambien los datos subyacentes

## Consideraciones de Rendimiento

### Métricas Importantes

- **Hit Rate**: Porcentaje de accesos exitosos al cache
- **Memory Usage**: Uso de memoria del cache
- **Eviction Rate**: Frecuencia de eliminación de entradas
- **Cleanup Frequency**: Frecuencia de limpieza de entradas expiradas

### Optimizaciones

```python
# Precalentar cache con indicadores comunes
def warm_cache_for_session():
    common_symbols = ['BTCUSDT', 'ETHUSDT']
    common_timeframes = ['1h', '4h']
    common_indicators = ['RSI', 'MACD']
    
    for symbol in common_symbols:
        for timeframe in common_timeframes:
            for indicator in common_indicators:
                # Precalcular y cachear
                result = calculate_indicator(symbol, timeframe, indicator)
                indicator_cache.cache_indicator(
                    symbol, timeframe, indicator, 
                    {'period': 14}, result
                )
```

## Integración con Otros Módulos

### Con Indicadores Avanzados

```python
from src.core.advanced_indicators import AdvancedIndicators
from src.utils.advanced_cache import cached_function

class CachedAdvancedIndicators(AdvancedIndicators):
    @cached_function(ttl=300)
    def calculate_rsi(self, *args, **kwargs):
        return super().calculate_rsi(*args, **kwargs)
    
    @cached_function(ttl=600)
    def calculate_ichimoku(self, *args, **kwargs):
        return super().calculate_ichimoku(*args, **kwargs)
```

### Con Sistema de Trading

```python
from src.utils.advanced_cache import indicator_cache

class TradingStrategy:
    def get_signals(self, symbol, timeframe):
        # Verificar cache antes de calcular señales
        cache_key = f"signals_{symbol}_{timeframe}"
        cached_signals = indicator_cache.get(cache_key)
        
        if cached_signals is None:
            signals = self._calculate_signals(symbol, timeframe)
            indicator_cache.set(cache_key, signals, ttl=180)
            return signals
        
        return cached_signals
```

## Troubleshooting

### Problemas Comunes

1. **Cache Miss Alto**: Verificar TTL y patrones de acceso
2. **Uso Excesivo de Memoria**: Reducir max_size o TTL
3. **Datos Obsoletos**: Ajustar TTL o implementar invalidación por eventos
4. **Rendimiento Lento**: Verificar frecuencia de cleanup

### Debugging

```python
# Habilitar logging detallado
import logging
logging.getLogger('advanced_cache').setLevel(logging.DEBUG)

# Inspeccionar estado del cache
stats = indicator_cache.get_stats()
print(f"Estado del cache: {stats}")

# Verificar claves específicas
for key in list(indicator_cache.cache.keys())[:10]:
    entry = indicator_cache.cache[key]
    print(f"Clave: {key[:16]}... Expira: {entry['expires_at']}")
```

Este sistema de cache está diseñado para maximizar el rendimiento en aplicaciones de trading donde los cálculos de indicadores pueden ser costosos y repetitivos. Su implementación inteligente de TTL y LRU asegura un uso eficiente de la memoria mientras mantiene los datos más relevantes disponibles para acceso rápido.