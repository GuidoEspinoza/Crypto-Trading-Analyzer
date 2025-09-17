# 📊 Position Manager - Guía Completa

## Descripción General

El `PositionManager` es el componente central para la gestión de posiciones activas en el sistema de trading. Proporciona funcionalidades avanzadas para el seguimiento, actualización y análisis de posiciones, con optimizaciones de rendimiento y configuración dinámica.

## 🚀 Características Principales

### 1. Gestión Centralizada de Posiciones
- Coordinación entre `position_monitor` y `paper_trader`
- Tracking automático de Take Profit y Stop Loss
- Gestión inteligente de trailing stops
- Análisis de performance en tiempo real

### 2. Sistema de Cache Optimizado
- Cache inteligente con invalidación selectiva
- Métodos optimizados para actualización de cache
- Estadísticas de rendimiento del cache
- Configuración dinámica de intervalos

### 3. Configuración Dinámica
- Parámetros configurables desde perfiles de trading
- Eliminación de valores hardcodeados
- Adaptación automática a diferentes estrategias

## 📋 Configuraciones Disponibles

### Configuraciones del Perfil de Trading

```python
# Ejemplo de configuración en perfil de trading
profile_config = {
    # Cache y rendimiento
    'position_check_interval': 30,  # segundos
    'seconds_per_day': 86400,       # configurable para tests
    
    # Trailing stops
    'default_trailing_distance': 1.0,  # porcentaje
    'atr_multiplier': 2.0,             # multiplicador ATR
    'atr_estimation_percentage': 2.0,   # estimación conservadora
    
    # Profit scaling ratios
    'tp_max_ratio': 0.67,  # 2/3 del máximo
    'tp_mid_ratio': 0.5,   # 1/2 del máximo
    'tp_min_ratio': 0.67   # 2/3 del mínimo
}
```

## 🔧 API Principal

### Inicialización

```python
from src.core.position_manager import PositionManager

# Inicializar con configuración automática
position_manager = PositionManager()
```

### Gestión de Posiciones

```python
# Obtener posiciones activas
positions = position_manager.get_active_positions()

# Forzar actualización del cache
positions = position_manager.get_active_positions(refresh_cache=True)

# Obtener posición específica
position = position_manager.get_position_by_id(trade_id=123)

# Obtener posiciones por símbolo
btc_positions = position_manager.get_positions_by_symbol('BTCUSDT')
```

### Actualización de Precios

```python
# Actualizar precio de posición
success = position_manager.update_position_price(
    trade_id=123,
    new_price=45000.0
)

# Actualizar múltiples posiciones
market_data = {
    'BTCUSDT': 45000.0,
    'ETHUSDT': 3000.0
}
updated_count = position_manager.update_trailing_stops(market_data)
```

### Gestión de Cache

```python
# Verificar validez del cache
if position_manager.is_cache_valid():
    print("Cache válido")

# Invalidar cache específico
position_manager.invalidate_cache(trade_id=123)

# Invalidar todo el cache
position_manager.invalidate_cache()

# Obtener estadísticas del cache
stats = position_manager.get_cache_stats()
print(f"Tamaño del cache: {stats['cache_size']}")
print(f"Edad del cache: {stats['cache_age_seconds']} segundos")
```

### Análisis de Exposición

```python
# Obtener exposición del portfolio
exposure = position_manager.get_portfolio_exposure()
print(f"Exposición total: ${exposure['total_exposure']:.2f}")
print(f"PnL no realizado: ${exposure['total_unrealized_pnl']:.2f}")

# Exposición por símbolo
for symbol, data in exposure['symbol_exposure'].items():
    print(f"{symbol}: ${data['value']:.2f} ({data['percentage']:.1f}%)")
```

### Trailing Stops Dinámicos

```python
# Calcular trailing stop basado en ATR
trailing_stop = position_manager.calculate_atr_trailing_stop(
    symbol='BTCUSDT',
    current_price=45000.0,
    trade_type='BUY'
    # atr_multiplier se toma del perfil automáticamente
)

# Con multiplicador personalizado
trailing_stop = position_manager.calculate_atr_trailing_stop(
    symbol='BTCUSDT',
    current_price=45000.0,
    trade_type='BUY',
    atr_multiplier=1.5
)
```

## 📊 Estructuras de Datos

### PositionInfo

```python
@dataclass
class PositionInfo:
    trade_id: int
    symbol: str
    trade_type: str  # 'BUY' o 'SELL'
    entry_price: float
    current_price: float
    quantity: float
    entry_value: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_percentage: float
    take_profit: Optional[float]
    stop_loss: Optional[float]
    trailing_stop: Optional[float]
    entry_time: datetime
    notes: str
    days_held: float
    max_profit: float
    max_loss: float
    risk_reward_ratio: float
```

### PositionUpdate

```python
@dataclass
class PositionUpdate:
    trade_id: int
    new_price: float
    timestamp: datetime
    reason: str  # 'PRICE_UPDATE', 'TRAILING_STOP', etc.
```

## 🎯 Condiciones de Salida

El sistema evalúa automáticamente las siguientes condiciones:

### Para Posiciones BUY
- **Take Profit**: `current_price >= take_profit`
- **Stop Loss**: `current_price <= stop_loss`
- **Trailing Stop**: `current_price <= trailing_stop`

### Para Posiciones SELL
- **Take Profit**: `current_price <= take_profit`
- **Stop Loss**: `current_price >= stop_loss`

## 📈 Optimizaciones Implementadas

### 1. Cache Inteligente
- **Invalidación selectiva**: Solo actualiza posiciones específicas
- **Validación automática**: Verifica edad del cache automáticamente
- **Estadísticas**: Monitoreo del rendimiento del cache

### 2. Configuración Dinámica
- **Eliminación de hardcoding**: Todos los parámetros son configurables
- **Perfiles adaptativos**: Configuración por estrategia de trading
- **Valores por defecto**: Fallbacks seguros para configuraciones faltantes

### 3. Gestión de Memoria
- **Cache limitado**: Evita crecimiento descontrolado
- **Limpieza automática**: Eliminación de posiciones cerradas
- **Actualización eficiente**: Solo recalcula cuando es necesario

## 🔍 Logging y Monitoreo

El sistema proporciona logging detallado:

```python
# Logs de cache
"🔄 Cache invalidated for position 123"
"🔄 Full cache invalidated"
"🔄 Cache updated for position 123"

# Logs de posiciones
"💰 Updated position 123: 44000.0000 -> 45000.0000"
"📈 Trailing stop activated for BTCUSDT: $43500.0000"
"🎯 TRAILING STOP activated for position 123"

# Logs de cierre
"🎯 ═══════════════════════════════════════════════════════════"
"🤖 CIERRE AUTOMÁTICO DE POSICIÓN"
"⚡ ACTIVACIÓN: 📈 TAKE PROFIT"
"💰 GANANCIA: $1500.00 (+3.33%)"
```

## 🧪 Testing y Validación

Para testing, el sistema permite:

```python
# Configuración de test con tiempos acelerados
test_profile = {
    'seconds_per_day': 86.4,  # 1 día = 86.4 segundos para tests
    'position_check_interval': 1,  # verificar cada segundo
    'cache_duration': 5  # cache válido por 5 segundos
}
```

## 🚨 Manejo de Errores

El sistema incluye manejo robusto de errores:

- **Validación de datos**: Verificación de parámetros de entrada
- **Fallbacks seguros**: Valores por defecto para configuraciones faltantes
- **Logging de errores**: Registro detallado de problemas
- **Recuperación automática**: Reintentos en operaciones críticas

## 📚 Ejemplos de Uso Avanzado

### Monitoreo en Tiempo Real

```python
import time

while True:
    # Obtener posiciones activas
    positions = position_manager.get_active_positions()
    
    for position in positions:
        # Verificar condiciones de salida
        exit_reason = position_manager.check_exit_conditions(position)
        
        if exit_reason:
            # Cerrar posición automáticamente
            success = position_manager.close_position(
                trade_id=position.trade_id,
                current_price=position.current_price,
                reason=exit_reason
            )
            
            if success:
                print(f"Posición {position.trade_id} cerrada: {exit_reason}")
    
    # Esperar antes de la siguiente verificación
    time.sleep(position_manager.cache_duration)
```

### Análisis de Performance

```python
# Obtener estadísticas generales
stats = position_manager.get_stats()

print(f"Posiciones activas: {stats['active_positions']}")
print(f"Take Profits ejecutados: {stats['tp_executed']}")
print(f"Stop Loss ejecutados: {stats['sl_executed']}")
print(f"PnL total realizado: ${stats['total_realized_pnl']:.2f}")

# Análisis de cache
cache_stats = position_manager.get_cache_stats()
print(f"Eficiencia del cache: {cache_stats['cache_valid']}")
print(f"Tamaño del cache: {cache_stats['cache_size']} posiciones")
```

Esta documentación proporciona una guía completa para utilizar el `PositionManager` optimizado, incluyendo todas las mejoras implementadas y ejemplos prácticos de uso.