# 📊 Indicadores Técnicos - Documentación Técnica

## Descripción General

El módulo `advanced_indicators.py` implementa una suite completa de indicadores técnicos avanzados para análisis de mercado. Utiliza optimizaciones de caché, manejo robusto de errores y configuraciones centralizadas para proporcionar análisis técnico de nivel profesional.

## Arquitectura del Sistema

### Clase Principal: `AdvancedIndicators`

La clase principal gestiona todos los indicadores técnicos con las siguientes características:

- **Sistema de Caché Inteligente**: TTL configurable para optimizar rendimiento
- **Manejo Robusto de Errores**: Validaciones exhaustivas y fallbacks seguros
- **Configuración Centralizada**: Parámetros desde `main_config.py`
- **Compatibilidad Multi-Timeframe**: Soporte para diferentes marcos temporales

### Configuración de Caché

```python
# Configuración automática desde CacheConfig
_cache_ttl = CacheConfig.get_ttl_for_operation("indicators")
MAX_CACHE_ENTRIES = CacheConfig.MAX_CACHE_ENTRIES
```

## Indicadores Implementados

### 1. Retrocesos de Fibonacci (`calculate_fibonacci_retracements`)

**Propósito**: Identifica niveles de soporte y resistencia basados en retrocesos de Fibonacci.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período para identificar máximos y mínimos (default: 50)

**Niveles Calculados**:
- 23.6%, 38.2%, 50%, 61.8%, 78.6%

**Retorna**:
```python
{
    "levels": {
        "23.6": float,
        "38.2": float,
        "50.0": float,
        "61.8": float,
        "78.6": float
    },
    "trend_direction": "BULLISH" | "BEARISH",
    "high_price": float,
    "low_price": float,
    "current_level": str  # Nivel más cercano al precio actual
}
```

### 2. Nube de Ichimoku (`calculate_ichimoku_cloud`)

**Propósito**: Análisis completo de tendencia, momentum y niveles de soporte/resistencia.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `tenkan_period`: Período Tenkan-sen (default: 9)
- `kijun_period`: Período Kijun-sen (default: 26)
- `senkou_span_b_period`: Período Senkou Span B (default: 52)

**Componentes Calculados**:
- **Tenkan-sen**: Línea de conversión
- **Kijun-sen**: Línea base
- **Senkou Span A**: Primera línea de la nube
- **Senkou Span B**: Segunda línea de la nube
- **Chikou Span**: Línea de retraso

**Retorna**:
```python
{
    "tenkan_sen": float,
    "kijun_sen": float,
    "senkou_span_a": float,
    "senkou_span_b": float,
    "chikou_span": float,
    "cloud_color": "BULLISH" | "BEARISH",
    "price_vs_cloud": "ABOVE" | "BELOW" | "INSIDE",
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG"
}
```

### 3. Bandas de Bollinger (`calculate_bollinger_bands`)

**Propósito**: Identificar condiciones de sobrecompra/sobreventa y volatilidad.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período de la media móvil (default: 20)
- `std_dev`: Desviaciones estándar (default: 2)

**Retorna**:
```python
{
    "upper_band": float,
    "middle_band": float,  # SMA
    "lower_band": float,
    "bandwidth": float,    # Ancho de las bandas
    "percent_b": float,    # Posición del precio en las bandas
    "squeeze": bool,       # Compresión de volatilidad
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG"
}
```

### 4. MACD (Moving Average Convergence Divergence) (`calculate_macd`)

**Propósito**: Análisis de momentum y cambios de tendencia.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `fast_period`: EMA rápida (default: 12)
- `slow_period`: EMA lenta (default: 26)
- `signal_period`: Línea de señal (default: 9)

**Retorna**:
```python
{
    "macd_line": float,
    "signal_line": float,
    "histogram": float,
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG",
    "divergence": "BULLISH" | "BEARISH" | "NONE"
}
```

### 5. RSI (Relative Strength Index) (`calculate_rsi`)

**Propósito**: Identificar condiciones de sobrecompra y sobreventa.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período de cálculo (default: 14)

**Retorna**:
```python
{
    "rsi": float,
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG",
    "overbought": bool,    # RSI > 70
    "oversold": bool,      # RSI < 30
    "divergence": "BULLISH" | "BEARISH" | "NONE"
}
```

### 6. Stochastic Oscillator (`calculate_stochastic`)

**Propósito**: Momentum oscillator para identificar puntos de reversión.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `k_period`: Período %K (default: 14)
- `d_period`: Período %D (default: 3)

**Retorna**:
```python
{
    "k_percent": float,
    "d_percent": float,
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG",
    "overbought": bool,    # %K > 80
    "oversold": bool       # %K < 20
}
```

### 7. ADX (Average Directional Index) (`calculate_adx`)

**Propósito**: Medir la fuerza de la tendencia.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período de cálculo (default: 14)

**Retorna**:
```python
{
    "adx": float,
    "di_plus": float,      # Indicador direccional positivo
    "di_minus": float,     # Indicador direccional negativo
    "trend_strength": "WEAK" | "MODERATE" | "STRONG" | "VERY_STRONG",
    "trend_direction": "BULLISH" | "BEARISH" | "NEUTRAL"
}
```

### 8. Williams %R (`calculate_williams_r`)

**Propósito**: Oscillator de momentum para identificar niveles de sobrecompra/sobreventa.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período de cálculo (default: 14)

**Retorna**:
```python
{
    "williams_r": float,
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG",
    "overbought": bool,    # Williams %R > -20
    "oversold": bool       # Williams %R < -80
}
```

### 9. CCI (Commodity Channel Index) (`calculate_cci`)

**Propósito**: Identificar condiciones cíclicas de sobrecompra/sobreventa.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período de cálculo (default: 20)

**Retorna**:
```python
{
    "cci": float,
    "signal": "BUY" | "SELL" | "NEUTRAL",
    "strength": "WEAK" | "MODERATE" | "STRONG",
    "overbought": bool,    # CCI > 100
    "oversold": bool       # CCI < -100
}
```

### 10. ATR (Average True Range) (`calculate_atr`)

**Propósito**: Medir la volatilidad del mercado.

**Parámetros**:
- `df`: DataFrame con datos OHLCV
- `period`: Período de cálculo (default: 14)

**Retorna**:
```python
{
    "atr": float,
    "atr_percentage": float,  # ATR como % del precio
    "volatility_level": "LOW" | "MODERATE" | "HIGH" | "EXTREME"
}
```

## Funciones de Utilidad

### `safe_float_conversion(value, default=0.0)`

Convierte valores a float de manera segura, manejando NaN, infinitos y errores.

### `get_cache_key(method_name, *args, **kwargs)`

Genera claves únicas para el sistema de caché basadas en parámetros de entrada.

### `cleanup_cache()`

Limpia automáticamente entradas expiradas del caché para optimizar memoria.

## Configuración y Personalización

### Parámetros Configurables

Los indicadores utilizan configuración centralizada desde `TechnicalAnalysisConfig`:

```python
# Períodos estándar
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BOLLINGER_PERIOD = 20
BOLLINGER_STD = 2

# Umbrales de señales
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
STOCH_OVERBOUGHT = 80
STOCH_OVERSOLD = 20
```

### Optimización de Rendimiento

1. **Caché Inteligente**: Resultados almacenados con TTL configurable
2. **Validación Temprana**: Verificación de datos antes del cálculo
3. **Manejo de Errores**: Fallbacks seguros para evitar crashes
4. **Limpieza Automática**: Gestión automática de memoria del caché

## Uso en Estrategias

Los indicadores se integran con las estrategias de trading a través de la clase `EnhancedTradingStrategy`:

```python
# Ejemplo de uso en estrategia
indicators = AdvancedIndicators()
rsi_data = indicators.calculate_rsi(df)
macd_data = indicators.calculate_macd(df)

if rsi_data["oversold"] and macd_data["signal"] == "BUY":
    # Generar señal de compra
    pass
```

## Consideraciones Técnicas

### Manejo de Datos Faltantes

- Validación automática de columnas requeridas (OHLCV)
- Manejo de períodos insuficientes de datos
- Fallbacks seguros para evitar errores de cálculo

### Compatibilidad

- Compatible con pandas DataFrames estándar
- Integración con pandas-ta para cálculos optimizados
- Soporte para múltiples timeframes

### Logging y Debugging

Todos los indicadores incluyen logging detallado para:
- Errores de cálculo
- Advertencias de datos insuficientes
- Información de rendimiento del caché

## Extensibilidad

Para agregar nuevos indicadores:

1. Implementar método en la clase `AdvancedIndicators`
2. Seguir el patrón de retorno estándar con `signal` y `strength`
3. Incluir manejo de errores y validación de datos
4. Agregar configuración en `TechnicalAnalysisConfig` si es necesario
5. Documentar parámetros y valores de retorno

## Dependencias

- `pandas`: Manipulación de datos
- `pandas-ta`: Indicadores técnicos optimizados
- `numpy`: Cálculos numéricos
- `logging`: Sistema de logs
- `hashlib`: Generación de claves de caché
- `time`: Gestión de timestamps para caché