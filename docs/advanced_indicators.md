# 📊 Documentación de Indicadores Técnicos Avanzados

## Descripción General

El módulo `advanced_indicators.py` es una biblioteca completa de indicadores técnicos profesionales para análisis de trading de criptomonedas. Está completamente optimizado con sistema de cache avanzado, parámetros configurables y manejo robusto de errores.

## 🚀 Características Principales

### ✅ Optimizaciones Implementadas

- **Parámetros Configurables**: Todos los indicadores utilizan configuraciones centralizadas desde `AdvancedIndicatorsConfig` y `OscillatorConfig`
- **Sistema de Cache Avanzado**: Implementación eficiente con `indicator_cache` para mejorar rendimiento
- **Manejo de Errores Robusto**: Función `safe_float()` y bloques try-catch en todos los métodos
- **Sin Valores Hardcodeados**: Eliminación completa de valores fijos, reemplazados por configuraciones
- **Compatibilidad con pandas_ta**: Integración optimizada con supresión de warnings

## 📋 Indicadores Disponibles

### 🔢 Indicadores de Fibonacci

#### `fibonacci_retracement(df, lookback=None)`
Calcula niveles de retroceso de Fibonacci para identificar soportes y resistencias.

**Parámetros:**
- `df`: DataFrame con datos OHLCV
- `lookback`: Períodos hacia atrás (usa `FibonacciConfig.LOOKBACK_PERIOD`)

**Retorna:** `FibonacciLevels` con niveles 0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%

### 📈 Indicadores de Tendencia

#### `ichimoku_cloud(df)`
Genera el sistema completo Ichimoku Kinko Hyo para análisis de tendencia.

**Componentes:**
- Tenkan-sen (línea de conversión)
- Kijun-sen (línea base) 
- Senkou Span A y B (nube)
- Chikou Span (línea rezagada)
- Análisis de posición del precio vs nube

#### `parabolic_sar(df)`
Calcula el Parabolic SAR para identificar puntos de reversión de tendencia.

**Configuración:** Utiliza `AdvancedIndicatorsConfig.PSAR_AF_START` y `PSAR_AF_MAX`

### 📊 Osciladores

#### `stochastic_oscillator(df, k_period=None, d_period=None)`
Oscilador estocástico para identificar condiciones de sobrecompra/sobreventa.

**Parámetros configurables:**
- `k_period`: `AdvancedIndicatorsConfig.STOCHASTIC_K_PERIOD`
- `d_period`: `AdvancedIndicatorsConfig.STOCHASTIC_D_PERIOD`
- Umbrales: `OscillatorConfig.STOCHASTIC_THRESHOLDS`

#### `williams_percent_r(df, period=None)`
Indicador Williams %R para momentum y reversiones.

**Configuración:**
- Período: `AdvancedIndicatorsConfig.WILLIAMS_R_PERIOD`
- Umbrales: `OscillatorConfig.WILLIAMS_R_THRESHOLDS`

#### `commodity_channel_index(df, period=None)`
Commodity Channel Index (CCI) para identificar tendencias cíclicas.

**Configuración:**
- Período: `AdvancedIndicatorsConfig.CCI_PERIOD`
- Constante: `CalculationConfig.CCI_CONSTANT`
- Umbrales: `OscillatorConfig.CCI_THRESHOLDS`

#### `enhanced_rsi(df, symbol, timeframe, period=None)`
RSI mejorado con análisis de divergencias y cache optimizado.

**Características:**
- Cache inteligente por símbolo y timeframe
- Detección de divergencias alcistas/bajistas
- RSI rápido (7) y lento (21) para confirmación
- Umbrales configurables desde `TradingProfiles`

#### `rate_of_change(df, period=None)`
Rate of Change (ROC) para medir momentum de precios.

**Configuración:**
- Período: `AdvancedIndicatorsConfig.ROC_PERIOD`
- Umbrales: `OscillatorConfig.ROC_THRESHOLDS`

#### `money_flow_index(df, period=None)`
Money Flow Index que combina precio y volumen.

**Configuración:**
- Período: `AdvancedIndicatorsConfig.MFI_PERIOD`
- Umbrales: `OscillatorConfig.RSI_THRESHOLDS` (reutiliza configuración RSI)

### 📏 Indicadores de Volatilidad

#### `bollinger_bands(df, symbol, timeframe, period=None, std_dev=None)`
Bandas de Bollinger con cache optimizado.

**Configuración:**
- Período: `AdvancedIndicatorsConfig.BOLLINGER_PERIOD`
- Desviación estándar: `AdvancedIndicatorsConfig.BOLLINGER_STD_DEV`

#### `average_true_range(df, period=None)`
Average True Range (ATR) para medir volatilidad.

**Configuración:**
- Período: `AdvancedIndicatorsConfig.ATR_PERIOD`

### 📊 Indicadores de Volumen

#### `vwap(df, symbol, timeframe)`
Volume Weighted Average Price con cache.

#### `on_balance_volume(df)`
On Balance Volume para análisis de flujo de volumen.

#### `volume_profile(df, bins=None)`
Perfil de volumen por niveles de precio.

**Configuración:**
- Bins: `AdvancedIndicatorsConfig.VOLUME_PROFILE_BINS`

### 🎯 Análisis de Patrones

#### `support_resistance_levels(df, window=None, min_touches=2)`
Detección automática de soportes y resistencias.

**Configuración:**
- Ventana: `AdvancedIndicatorsConfig.SUPPORT_RESISTANCE_WINDOW`

#### `detect_candlestick_patterns(df)`
Detección de patrones de velas japonesas.

#### `trend_lines_analysis(df, lookback=None)`
Análisis de líneas de tendencia.

**Configuración:**
- Lookback: `AdvancedIndicatorsConfig.TREND_LINES_LOOKBACK`

#### `chart_patterns_detection(df, window=None)`
Detección de patrones gráficos (triángulos, banderas, etc.).

**Configuración:**
- Ventana: `AdvancedIndicatorsConfig.CHART_PATTERNS_WINDOW`

## 🔧 Sistema de Cache

### Implementación
```python
@classmethod
def _get_cached_indicator(cls, symbol: str, timeframe: str, indicator_name: str, params: Dict):
    return indicator_cache.get_indicator(symbol, timeframe, indicator_name, params)

@classmethod
def _cache_indicator(cls, symbol: str, timeframe: str, indicator_name: str, params: Dict, result):
    return indicator_cache.cache_indicator(symbol, timeframe, indicator_name, params, result)
```

### Beneficios
- **Rendimiento**: Evita recálculos innecesarios
- **Eficiencia**: Cache por símbolo, timeframe y parámetros
- **Memoria**: Gestión automática de expiración

## 🛡️ Manejo de Errores

### Función `safe_float()`
```python
@staticmethod
def safe_float(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value) or np.isinf(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default
```

### Características
- **Valores NaN**: Conversión automática a valores por defecto
- **Infinitos**: Manejo de valores infinitos
- **Compatibilidad JSON**: Todos los valores son serializables
- **Fallbacks**: Cálculos manuales cuando pandas_ta falla

## ⚙️ Configuración

### Archivos de Configuración
- `AdvancedIndicatorsConfig`: Períodos y parámetros principales
- `OscillatorConfig`: Umbrales de osciladores
- `FibonacciConfig`: Configuración de Fibonacci
- `CalculationConfig`: Constantes de cálculo
- `TradingProfiles`: Perfiles de trading personalizables

### Ejemplo de Uso
```python
from src.core.advanced_indicators import AdvancedIndicators

# RSI con configuración automática
rsi_result = AdvancedIndicators.enhanced_rsi(df, 'BTCUSDT', '1h')

# Bollinger Bands con cache
bb_result = AdvancedIndicators.bollinger_bands(df, 'BTCUSDT', '1h')

# Stochastic con umbrales configurables
stoch_result = AdvancedIndicators.stochastic_oscillator(df)
```

## 📊 Formato de Respuesta

Todos los indicadores retornan un diccionario con:
- **Valores calculados**: Datos numéricos del indicador
- **signal**: "BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"
- **interpretation**: Descripción textual de la señal
- **Datos adicionales**: Información específica del indicador

### Ejemplo de Respuesta
```python
{
    "rsi": 65.23,
    "rsi_fast": 68.45,
    "rsi_slow": 62.10,
    "divergence": "NONE",
    "signal": "SELL",
    "interpretation": "📉 RSI overbought (65.2 >= 70) - Señal de venta"
}
```

## 🔄 Optimizaciones de Rendimiento

### 1. Conversión de Tipos
```python
# Evita warnings de pandas_ta
high_float = df['high'].astype('float64')
low_float = df['low'].astype('float64')
close_float = df['close'].astype('float64')
```

### 2. Supresión de Warnings
```python
with warnings.catch_warnings():
    warnings.simplefilter('ignore', FutureWarning)
    warnings.simplefilter('ignore', UserWarning)
    result = ta.indicator(data)
```

### 3. Cálculos Optimizados
- Datasets pequeños (<100): Cálculo manual optimizado
- Datasets grandes: pandas_ta con fallback manual
- Cache inteligente para evitar recálculos

## 🚀 Mejores Prácticas

### Para Desarrolladores
1. **Siempre usar parámetros configurables** en lugar de valores hardcodeados
2. **Implementar cache** para indicadores computacionalmente costosos
3. **Usar safe_float()** para todos los valores numéricos
4. **Incluir fallbacks manuales** cuando pandas_ta falle
5. **Documentar interpretaciones** de señales claramente

### Para Usuarios
1. **Configurar umbrales** según estrategia de trading
2. **Combinar múltiples indicadores** para confirmación
3. **Considerar timeframes** diferentes para análisis completo
4. **Revisar divergencias** en indicadores de momentum
5. **Usar cache** para análisis en tiempo real

## 📈 Casos de Uso

### Trading Algorítmico
```python
# Estrategia multi-indicador
rsi = AdvancedIndicators.enhanced_rsi(df, symbol, timeframe)
bb = AdvancedIndicators.bollinger_bands(df, symbol, timeframe)
stoch = AdvancedIndicators.stochastic_oscillator(df)

if (rsi['signal'] == 'BUY' and 
    bb['signal'] == 'BUY' and 
    stoch['signal'] == 'BUY'):
    execute_buy_order()
```

### Análisis de Mercado
```python
# Análisis completo de tendencia
ichimoku = AdvancedIndicators.ichimoku_cloud(df)
sar = AdvancedIndicators.parabolic_sar(df)
support_resistance = AdvancedIndicators.support_resistance_levels(df)

market_analysis = {
    'trend': ichimoku['signal'],
    'reversal_points': sar,
    'key_levels': support_resistance
}
```

## 🔮 Roadmap Futuro

### Próximas Mejoras
- [ ] Indicadores de Machine Learning
- [ ] Análisis de sentimiento de mercado
- [ ] Indicadores de correlación entre activos
- [ ] Optimización con numba/cython
- [ ] Indicadores personalizados por usuario

---

**Versión:** 3.0 (Completamente Optimizada)  
**Última actualización:** Enero 2025  
**Mantenedor:** Crypto Trading Analyzer Team