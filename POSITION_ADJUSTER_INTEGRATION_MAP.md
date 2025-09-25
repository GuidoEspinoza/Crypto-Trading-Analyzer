# 🗺️ Mapeo de Integración: PositionAdjuster + Sistema de Tracking de IDs

## 📋 Estado Actual vs Estado Objetivo

### 🔍 Análisis del PositionAdjuster Actual

**Archivo:** `src/core/position_adjuster.py`

#### 🚫 Limitaciones Actuales:
1. **Línea 496-500**: Modo simulación solamente
2. **Línea 502-510**: TODO comentado para modo real
3. **Línea 532-540**: Sin conexión real con Binance API
4. **Línea 542-550**: Actualización de BD simulada

#### 🎯 Métodos que Necesitan Modificación:

### 1. **Constructor `__init__` (Línea 82)**
```python
# ACTUAL:
def __init__(self, config=None, simulation_mode=True):

# NECESITA:
def __init__(self, config=None, simulation_mode=True, binance_connector=None):
    self.binance_connector = binance_connector  # ← AGREGAR
```

### 2. **Método `_execute_adjustment` (Línea 451-529)**
```python
# ACTUAL (Línea 496-500):
# Simular cancelación de órdenes OCO existentes
logger.info(f"🔄 {symbol}: Simulando cancelación de órdenes OCO existentes")
await asyncio.sleep(config.get("api", {}).get("latency_simulation_sleep", 0.1))

# NECESITA REEMPLAZAR CON:
if not self.simulation_mode and self.binance_connector:
    # 1. Obtener position_id desde el símbolo
    position_id = self._get_position_id_by_symbol(symbol)
    
    # 2. Cancelar OCO existente usando IDs reales
    cancel_result = self.binance_connector.cancel_oco_order_by_position(position_id)
    
    # 3. Crear nuevo OCO con niveles actualizados
    adjust_result = self.binance_connector.adjust_oco_levels(
        position_id=position_id,
        new_tp_price=new_tp,
        new_sl_stop_price=new_sl,
        new_sl_limit_price=new_sl * 0.999  # Precio límite
    )
```

### 3. **Método `get_active_positions` (Línea 240-280)**
```python
# ACTUAL (Línea 245-250):
positions_data = db_manager.get_active_positions()

# NECESITA REEMPLAZAR CON:
if not self.simulation_mode and self.binance_connector:
    # Obtener posiciones desde BinanceConnector con tracking real
    active_positions = self.binance_connector.get_active_positions()
    positions_data = self._convert_trading_positions_to_db_format(active_positions)
else:
    # Modo simulación: usar BD como antes
    positions_data = db_manager.get_active_positions()
```

### 4. **Nuevo Método Necesario: `_get_position_id_by_symbol`**
```python
def _get_position_id_by_symbol(self, symbol: str) -> Optional[str]:
    """🔍 Obtener position_id desde el símbolo"""
    if self.binance_connector:
        active_positions = self.binance_connector.get_active_positions()
        for position in active_positions:
            if position.symbol == symbol:
                return position.position_id
    return None
```

### 5. **Nuevo Método Necesario: `_convert_trading_positions_to_db_format`**
```python
def _convert_trading_positions_to_db_format(self, trading_positions: List[TradingPosition]) -> List[Dict]:
    """🔄 Convertir TradingPosition a formato de BD"""
    converted = []
    for pos in trading_positions:
        converted.append({
            'symbol': pos.symbol,
            'side': pos.side,
            'quantity': pos.quantity,
            'entry_price': pos.entry_price,
            'current_tp': pos.oco_order.tp_price if pos.oco_order else 0,
            'current_sl': pos.oco_order.sl_stop_price if pos.oco_order else 0
        })
    return converted
```

## 🔗 Dependencias Nuevas Requeridas

### 1. **Import Statements (Línea 1-15)**
```python
# AGREGAR:
from typing import Optional
from src.core.binance_connector import BinanceConnector, TradingPosition
```

### 2. **Parámetros de Configuración**
```python
# AGREGAR al perfil de configuración:
{
    'use_real_trading': False,  # Flag para activar trading real
    'binance_connector_config': {
        'api_key': 'xxx',
        'api_secret': 'xxx',
        'testnet': True
    }
}
```

## 🎯 Flujo de Integración Completo

### Escenario 1: Modo Simulación (Actual)
```
PositionAdjuster → DB Manager → Simulación
```

### Escenario 2: Modo Real (Objetivo)
```
PositionAdjuster → BinanceConnector → Binance API
                ↓
            Tracking de IDs reales
                ↓
        Cancelación/Creación OCO real
```

## 📊 Puntos de Integración Específicos

### A. **Inicialización**
- **Línea 82**: Constructor debe recibir `BinanceConnector`
- **Línea 100**: Validar que connector esté disponible para modo real

### B. **Obtención de Posiciones**
- **Línea 245**: Cambiar fuente de datos según modo
- **Línea 250-280**: Adaptar formato de datos

### C. **Ejecución de Ajustes**
- **Línea 496**: Reemplazar simulación con llamadas reales
- **Línea 500**: Usar `adjust_oco_levels()` del connector
- **Línea 520**: Manejar respuestas reales de API

### D. **Manejo de Errores**
- **Línea 525-529**: Capturar errores específicos de Binance
- **Línea 515**: Rollback en caso de fallo

## 🔧 Métodos del BinanceConnector Utilizados

### Métodos Existentes (Ya Implementados):
1. `get_active_positions()` → Lista de TradingPosition
2. `adjust_oco_levels(position_id, new_tp, new_sl_stop, new_sl_limit)` → OrderResponse
3. `cancel_oco_order(order_list_id)` → OrderResponse
4. `get_oco_order_by_position(position_id)` → ActiveOCOOrder

### Métodos Nuevos Necesarios:
1. `cancel_oco_order_by_position(position_id)` → OrderResponse
2. `get_position_by_symbol(symbol)` → TradingPosition

## ✅ Checklist de Modificaciones

### 🔄 Constructor y Configuración
- [ ] Agregar parámetro `binance_connector` al constructor
- [ ] Validar connector en modo real
- [ ] Agregar imports necesarios

### 🔄 Obtención de Posiciones
- [ ] Modificar `get_active_positions()` para usar connector
- [ ] Crear método de conversión de formatos
- [ ] Mantener compatibilidad con modo simulación

### 🔄 Ejecución de Ajustes
- [ ] Reemplazar simulación con llamadas reales en `_execute_adjustment()`
- [ ] Implementar manejo de errores específicos de Binance
- [ ] Agregar logging detallado de operaciones reales

### 🔄 Métodos de Utilidad
- [ ] Crear `_get_position_id_by_symbol()`
- [ ] Crear `_convert_trading_positions_to_db_format()`
- [ ] Actualizar `_update_position_levels()` para modo real

### 🔄 Testing y Validación
- [ ] Actualizar tests para incluir modo real
- [ ] Crear mocks para BinanceConnector
- [ ] Validar flujo completo end-to-end

## 🎯 Resultado Final

Una vez implementadas estas modificaciones, el `PositionAdjuster` podrá:

✅ **Funcionar en modo simulación** (comportamiento actual)
✅ **Funcionar en modo real** con Binance API
✅ **Usar IDs reales** para cancelación de órdenes OCO
✅ **Ajustar dinámicamente** TP/SL en posiciones reales
✅ **Mantener tracking** de todas las operaciones
✅ **Manejar errores** de API de forma robusta

## 🚀 Próximos Pasos

1. **Implementar modificaciones** según este mapeo
2. **Actualizar tests** para cubrir modo real
3. **Validar integración** con sistema completo
4. **Documentar configuración** para modo real
5. **Testing en testnet** antes de producción