# 🛡️ Sistema de Manejo de Errores Avanzado

## Descripción General

El módulo `error_handler.py` proporciona un sistema robusto y especializado para el manejo de errores en aplicaciones de trading. Incluye decoradores inteligentes, excepciones personalizadas y utilidades para garantizar la estabilidad y confiabilidad del sistema de trading.

## Características Principales

### ✨ Funcionalidades Clave

- **Excepciones Especializadas**: Errores específicos para trading, indicadores y datos
- **Decoradores Inteligentes**: Manejo automático de errores con valores por defecto
- **Logging Estructurado**: Registro detallado de errores con contexto
- **Valores de Retorno Seguros**: Fallbacks inteligentes basados en el contexto
- **Validación de Datos**: Verificaciones automáticas para DataFrames y valores numéricos
- **Monitoreo de Rendimiento**: Alertas por tiempo de ejecución excesivo

## Arquitectura del Sistema

### Jerarquía de Excepciones

```python
Exception
└── TradingError (base)
    ├── IndicatorError
    └── DataError
```

#### Excepciones Personalizadas

```python
class TradingError(Exception):
    """Excepción base para errores de trading"""
    def __init__(self, message: str, error_code: str = None, context: Dict = None)

class IndicatorError(TradingError):
    """Error específico de cálculo de indicadores"""
    
class DataError(TradingError):
    """Error relacionado con datos de mercado"""
```

### Estructura de Contexto de Error

```python
{
    'error_code': 'INDICATOR_ERROR',
    'context': {
        'indicator': 'RSI',
        'symbol': 'BTCUSDT',
        'timeframe': '1h',
        'timestamp': '2024-01-15T10:30:00'
    },
    'function': 'calculate_rsi',
    'traceback': '...',
    'args': '...',
    'kwargs': '...'
}
```

## API de Uso

### Decorador Principal: `handle_errors`

```python
from src.utils.error_handler import handle_errors

@handle_errors(
    default_return={'value': 0.0, 'signal': 'HOLD'},
    log_errors=True,
    raise_on_critical=False,
    error_context={'operation': 'rsi_calculation'}
)
def calculate_rsi(prices, period=14):
    # Cálculo que puede fallar
    if len(prices) < period:
        raise ValueError("Insufficient data")
    return rsi_result
```

**Parámetros del Decorador:**
- `default_return`: Valor por defecto en caso de error
- `log_errors`: Si registrar errores en el log (default: True)
- `raise_on_critical`: Si re-lanzar errores críticos (default: False)
- `error_context`: Contexto adicional para el error

### Decoradores Especializados

#### Para Indicadores

```python
from src.utils.error_handler import indicator_error_handler

@indicator_error_handler('RSI')
def calculate_rsi(data, period=14):
    # Implementación del RSI
    return result

# En caso de error, retorna automáticamente:
# {
#     'value': 0.0,
#     'signal': 'HOLD',
#     'confidence': 0.0,
#     'interpretation': 'Error calculating RSI',
#     'error': True
# }
```

#### Para Operaciones de Datos

```python
from src.utils.error_handler import data_error_handler

@data_error_handler('price_data_fetch')
def fetch_price_data(symbol, timeframe):
    # Obtener datos de precios
    return price_data
```

### Validación de Datos

#### Validación de DataFrames

```python
from src.utils.error_handler import safe_dataframe_operation
import pandas as pd

def process_market_data(df):
    # Verificar que el DataFrame es válido
    safe_dataframe_operation(df, 'technical_analysis')
    
    # Proceder con el análisis
    return analysis_result

# Verificaciones automáticas:
# - DataFrame no es None o vacío
# - Contiene columnas requeridas: ['open', 'high', 'low', 'close']
# - No contiene valores nulos
# - Tiene al menos 2 filas de datos
```

#### Validación de Valores Numéricos

```python
from src.utils.error_handler import validate_numeric_input

def calculate_moving_average(prices, period):
    # Validar período
    period = validate_numeric_input(
        period, 
        name='period', 
        min_val=1, 
        max_val=200
    )
    
    # Calcular promedio móvil
    return moving_average
```

### Manejo de Excepciones Personalizadas

#### Lanzar Errores Específicos

```python
from src.utils.error_handler import IndicatorError, DataError

def calculate_bollinger_bands(prices, period=20):
    if len(prices) < period:
        raise IndicatorError(
            f"Insufficient data for Bollinger Bands: need {period}, got {len(prices)}",
            indicator_name='BollingerBands',
            required_period=period,
            actual_length=len(prices)
        )
    
    return bollinger_result

def validate_market_data(symbol, data):
    if data is None:
        raise DataError(
            f"No market data available for {symbol}",
            symbol=symbol,
            data_source='exchange_api'
        )
    
    return True
```

#### Capturar y Procesar Errores

```python
try:
    result = calculate_complex_indicator(data)
except IndicatorError as e:
    print(f"Error en indicador: {e.message}")
    print(f"Contexto: {e.context}")
    print(f"Código: {e.error_code}")
    # Usar valor por defecto
    result = default_indicator_value
except DataError as e:
    print(f"Error de datos: {e.message}")
    # Intentar obtener datos de fuente alternativa
    result = fetch_from_backup_source()
```

## Casos de Uso Avanzados

### 1. Sistema de Trading Robusto

```python
from src.utils.error_handler import handle_errors, create_error_context

class TradingBot:
    @handle_errors(
        default_return={'action': 'HOLD', 'confidence': 0.0},
        error_context={'component': 'trading_bot'}
    )
    def generate_signal(self, symbol, timeframe):
        context = create_error_context(
            symbol=symbol, 
            timeframe=timeframe,
            strategy='multi_indicator'
        )
        
        try:
            # Calcular múltiples indicadores
            rsi = self.calculate_rsi(symbol, timeframe)
            macd = self.calculate_macd(symbol, timeframe)
            bb = self.calculate_bollinger_bands(symbol, timeframe)
            
            # Generar señal combinada
            return self.combine_signals(rsi, macd, bb)
            
        except Exception as e:
            # Log con contexto completo
            self.logger.error(f"Error generating signal: {e}", extra=context)
            raise
    
    @indicator_error_handler('RSI')
    def calculate_rsi(self, symbol, timeframe):
        # Implementación con manejo automático de errores
        return rsi_calculation()
```

### 2. Pipeline de Datos con Validación

```python
from src.utils.error_handler import (
    safe_dataframe_operation, 
    validate_numeric_input,
    data_error_handler
)

class DataPipeline:
    @data_error_handler('data_ingestion')
    def ingest_market_data(self, symbol, start_date, end_date):
        # Obtener datos crudos
        raw_data = self.fetch_raw_data(symbol, start_date, end_date)
        
        # Validar DataFrame
        safe_dataframe_operation(raw_data, 'data_ingestion')
        
        return raw_data
    
    @handle_errors(default_return=None)
    def clean_and_validate(self, df):
        # Validaciones específicas
        for column in ['open', 'high', 'low', 'close', 'volume']:
            if column in df.columns:
                df[column] = df[column].apply(
                    lambda x: validate_numeric_input(x, column, min_val=0)
                )
        
        # Verificar consistencia de precios
        invalid_rows = df[df['high'] < df['low']]
        if not invalid_rows.empty:
            raise DataError(
                f"Invalid price data: high < low in {len(invalid_rows)} rows",
                invalid_rows_count=len(invalid_rows)
            )
        
        return df
```

### 3. Monitoreo de Rendimiento

```python
from src.utils.error_handler import log_performance_warning
import time

class PerformanceMonitor:
    def __init__(self):
        self.performance_threshold = 1.0  # 1 segundo
    
    def monitor_function(self, func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                execution_time = time.time() - start_time
                log_performance_warning(
                    func.__name__, 
                    execution_time, 
                    self.performance_threshold
                )
        
        return wrapper

# Uso
monitor = PerformanceMonitor()

@monitor.monitor_function
def expensive_calculation(data):
    # Cálculo que puede ser lento
    return complex_result
```

## Configuración de Logging

### Setup Básico

```python
import logging
from src.utils.error_handler import error_logger

# Configurar handler para archivo
file_handler = logging.FileHandler('trading_errors.log')
file_handler.setLevel(logging.ERROR)

# Configurar formato
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

# Agregar handler
error_logger.addHandler(file_handler)
```

### Logging Estructurado

```python
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'function': getattr(record, 'function', None),
            'error_code': getattr(record, 'error_code', None),
            'context': getattr(record, 'context', None)
        }
        return json.dumps(log_entry)

# Aplicar formatter JSON
json_handler = logging.StreamHandler()
json_handler.setFormatter(JSONFormatter())
error_logger.addHandler(json_handler)
```

## Valores por Defecto Inteligentes

El sistema incluye valores por defecto específicos según el contexto:

### Para Indicadores Generales

```python
{
    'value': 0.0,
    'signal': 'HOLD',
    'confidence': 0.0,
    'interpretation': 'Error in calculation - using safe defaults',
    'error': True
}
```

### Para Fibonacci

```python
{
    'level_0': 0.0,
    'level_236': 0.0,
    'level_382': 0.0,
    'level_500': 0.0,
    'level_618': 0.0,
    'level_786': 0.0,
    'level_100': 0.0
}
```

### Para Ichimoku

```python
{
    'tenkan_sen': 0.0,
    'kijun_sen': 0.0,
    'senkou_span_a': 0.0,
    'senkou_span_b': 0.0,
    'chikou_span': 0.0,
    'cloud_color': 'NEUTRAL',
    'price_position': 'UNKNOWN'
}
```

## Mejores Prácticas

### 1. Uso de Decoradores

```python
# ✅ Correcto: Usar decorador específico
@indicator_error_handler('MACD')
def calculate_macd(prices):
    return macd_result

# ❌ Incorrecto: Manejo manual repetitivo
def calculate_macd(prices):
    try:
        return macd_calculation()
    except Exception:
        return {'value': 0.0, 'signal': 'HOLD'}
```

### 2. Contexto de Error Rico

```python
# ✅ Correcto: Contexto detallado
@handle_errors(
    error_context={
        'component': 'risk_manager',
        'operation': 'position_sizing',
        'version': '1.2.0'
    }
)
def calculate_position_size(account_balance, risk_percent):
    return position_size

# ❌ Incorrecto: Sin contexto
@handle_errors()
def calculate_position_size(account_balance, risk_percent):
    return position_size
```

### 3. Validación Temprana

```python
# ✅ Correcto: Validar al inicio
def process_trading_data(df, symbol, timeframe):
    # Validar inmediatamente
    safe_dataframe_operation(df, 'trading_analysis')
    
    # Proceder con confianza
    return analysis_result

# ❌ Incorrecto: Validar tarde
def process_trading_data(df, symbol, timeframe):
    # Mucho procesamiento...
    if df is None:  # Muy tarde
        return None
```

## Integración con Otros Módulos

### Con Sistema de Cache

```python
from src.utils.advanced_cache import cached_function
from src.utils.error_handler import indicator_error_handler

@cached_function(ttl=300)
@indicator_error_handler('RSI')
def calculate_cached_rsi(prices, period=14):
    # Cálculo con cache y manejo de errores
    return rsi_result
```

### Con Indicadores Avanzados

```python
from src.core.advanced_indicators import AdvancedIndicators
from src.utils.error_handler import handle_errors, safe_dataframe_operation

class RobustAdvancedIndicators(AdvancedIndicators):
    @handle_errors(default_return={'error': True})
    def calculate_all_indicators(self, df, symbol):
        # Validar datos primero
        safe_dataframe_operation(df, 'indicator_calculation')
        
        # Calcular todos los indicadores
        return super().calculate_all_indicators(df, symbol)
```

## Troubleshooting

### Problemas Comunes

1. **Errores No Capturados**: Verificar que el decorador esté aplicado correctamente
2. **Logging Excesivo**: Ajustar nivel de logging según el entorno
3. **Valores por Defecto Incorrectos**: Personalizar `default_return` según el contexto
4. **Pérdida de Contexto**: Asegurar que se pase contexto relevante

### Debugging

```python
# Habilitar logging detallado
import logging
logging.getLogger('trading_errors').setLevel(logging.DEBUG)

# Verificar configuración de decoradores
def debug_error_handler(func):
    print(f"Function: {func.__name__}")
    print(f"Has error handler: {hasattr(func, '__wrapped__')}")
    return func

@debug_error_handler
@indicator_error_handler('TEST')
def test_function():
    pass
```

### Monitoreo en Producción

```python
from src.utils.error_handler import error_logger
import time

class ErrorMetrics:
    def __init__(self):
        self.error_counts = {}
        self.last_reset = time.time()
    
    def log_error(self, error_type, context):
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Reset cada hora
        if time.time() - self.last_reset > 3600:
            self.report_metrics()
            self.error_counts.clear()
            self.last_reset = time.time()
    
    def report_metrics(self):
        error_logger.info(f"Error metrics: {self.error_counts}")
```

Este sistema de manejo de errores está diseñado para proporcionar máxima robustez y confiabilidad en aplicaciones de trading, donde la estabilidad es crítica y los errores pueden tener consecuencias financieras significativas.