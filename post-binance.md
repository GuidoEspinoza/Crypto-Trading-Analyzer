# 📤 Mapeo de Datos: Trading Bot → Binance API

Este documento mapea los datos que genera nuestro trading bot con los parámetros necesarios para enviar órdenes a Binance usando el endpoint `/api/v3/order/test`.

## 🎯 DATOS DEL TRADING BOT → PARÁMETROS BINANCE

### 📋 Parámetros Obligatorios

| Dato Trading Bot | Parámetro Binance | Tipo | Descripción |
|---|---|---|---|
| **Símbolo del activo** | `symbol` | STRING | Ej: "BTCUSDT", "ETHUSDT" |
| **Dirección de la orden** | `side` | ENUM | "BUY" o "SELL" |
| **Tipo de orden** | `type` | ENUM | "MARKET", "LIMIT", "STOP_LOSS", etc. |
| **Timestamp actual** | `timestamp` | LONG | Timestamp en milisegundos |

### 📊 Parámetros Según Tipo de Orden

#### 🔹 MARKET Orders
| Dato Trading Bot | Parámetro Binance | Tipo | Descripción |
|---|---|---|---|
| **Cantidad a comprar/vender** | `quantity` | DECIMAL | Cantidad del activo base |
| **Valor en USDT** | `quoteOrderQty` | DECIMAL | Alternativa a quantity |

#### 🔹 LIMIT Orders  
| Dato Trading Bot | Parámetro Binance | Tipo | Descripción |
|---|---|---|---|
| **Cantidad** | `quantity` | DECIMAL | Cantidad del activo |
| **Precio límite** | `price` | DECIMAL | Precio de la orden límite |
| **Tiempo en vigor** | `timeInForce` | ENUM | "GTC", "IOC", "FOK" |

#### 🔹 STOP_LOSS Orders
| Dato Trading Bot | Parámetro Binance | Tipo | Descripción |
|---|---|---|---|
| **Cantidad** | `quantity` | DECIMAL | Cantidad del activo |
| **Precio de Stop Loss** | `stopPrice` | DECIMAL | Precio que activa la orden |

#### 🔹 TAKE_PROFIT Orders
| Dato Trading Bot | Parámetro Binance | Tipo | Descripción |
|---|---|---|---|
| **Cantidad** | `quantity` | DECIMAL | Cantidad del activo |
| **Precio de Take Profit** | `stopPrice` | DECIMAL | Precio que activa la orden |

### 🔧 Parámetros Opcionales Útiles

| Dato Trading Bot | Parámetro Binance | Tipo | Descripción |
|---|---|---|---|
| **ID único de orden** | `newClientOrderId` | STRING | Identificador único generado |
| **Estrategia ID** | `strategyId` | LONG | ID de la estrategia usada |
| **Tipo de estrategia** | `strategyType` | INT | Tipo de estrategia (>= 1000000) |
| **Ventana de recepción** | `recvWindow` | DECIMAL | Tiempo máximo de validez (≤ 60000) |

## ✅ RESULTADOS DEL TESTING

### 🧪 Tipos de Órdenes Probados y Validados

| Tipo de Orden | Estado | Parámetros Requeridos | Notas |
|---|---|---|---|
| **MARKET** | ✅ **FUNCIONA** | `symbol`, `side`, `type`, `quantity` | Órdenes de mercado básicas |
| **LIMIT** | ✅ **FUNCIONA** | `symbol`, `side`, `type`, `quantity`, `price`, `timeInForce` | Órdenes límite estándar |
| **TAKE_PROFIT** | ✅ **FUNCIONA** | `symbol`, `side`, `type`, `quantity`, `stopPrice` | Órdenes de take profit |
| **STOP_LOSS** | ✅ **FUNCIONA** | `symbol`, `side`, `type`, `quantity`, `stopPrice` | Órdenes de stop loss |
| **STOP_LOSS_LIMIT** | ⚠️ **PARCIAL** | `symbol`, `side`, `type`, `quantity`, `price`, `stopPrice`, `timeInForce` | Puede requerir ajustes específicos |

### 🎯 Recomendaciones de Implementación

1. **Usar principalmente**: `MARKET`, `LIMIT`, `TAKE_PROFIT`, `STOP_LOSS`
2. **Validar parámetros**: Siempre verificar que los parámetros obligatorios estén presentes
3. **Manejo de errores**: Implementar manejo robusto de errores HTTP 404 y otros códigos
4. **Testing continuo**: Probar en sandbox antes de producción

## 🤖 MAPEO DESDE NUESTRO TRADING BOT

### 📈 Datos Disponibles en el Bot

```python
# Ejemplo de datos que genera nuestro trading bot
trade_signal = {
    'symbol': 'BTCUSDT',           # → symbol
    'action': 'BUY',               # → side  
    'quantity': 0.001,             # → quantity
    'price': 45000.0,              # → price (para LIMIT)
    'stop_loss': 44000.0,          # → stopPrice (para STOP_LOSS)
    'take_profit': 46000.0,        # → stopPrice (para TAKE_PROFIT)
    'strategy_name': 'RSI_MACD',   # → strategyId/strategyType
    'timestamp': 1640995200000     # → timestamp
}
```

### 🔄 Transformación de Datos

```python
def map_bot_to_binance(trade_signal):
    """Mapea datos del trading bot a parámetros de Binance"""
    
    # Parámetros base obligatorios
    binance_params = {
        'symbol': trade_signal['symbol'],
        'side': trade_signal['action'],  # BUY/SELL
        'type': 'MARKET',  # Por defecto MARKET
        'timestamp': int(time.time() * 1000)
    }
    
    # Para órdenes MARKET
    if trade_signal.get('quantity'):
        binance_params['quantity'] = str(trade_signal['quantity'])
    
    # Para órdenes LIMIT
    if trade_signal.get('price'):
        binance_params.update({
            'type': 'LIMIT',
            'price': str(trade_signal['price']),
            'timeInForce': 'GTC'
        })
    
    # ID único de orden
    binance_params['newClientOrderId'] = f"bot_{int(time.time())}"
    
    return binance_params
```

## 🎯 ESTRATEGIA DE IMPLEMENTACIÓN

### 1️⃣ **Conector como Intermediario**
```python
class BinanceConnector:
    def test_order(self, order_params):
        """Envía orden de prueba a /api/v3/order/test"""
        # Solo maneja la comunicación HTTP
        # No contiene lógica de trading
```

### 2️⃣ **Script de Mapeo y Envío**
```python
class TradingOrderMapper:
    def __init__(self, binance_connector):
        self.connector = binance_connector
    
    def send_test_order(self, trade_signal):
        # Mapea datos del bot a parámetros Binance
        binance_params = self.map_bot_to_binance(trade_signal)
        
        # Envía usando el conector
        return self.connector.test_order(binance_params)
```

### 3️⃣ **Órdenes OCO para TP/SL**
```python
def create_oco_order(symbol, quantity, price, stop_price, stop_limit_price):
    """Crea orden OCO para Take Profit y Stop Loss simultáneos"""
    return {
        'symbol': symbol,
        'side': 'SELL',  # Para cerrar posición long
        'quantity': quantity,
        'price': price,           # Take Profit
        'stopPrice': stop_price,  # Stop Loss trigger
        'stopLimitPrice': stop_limit_price,  # Stop Loss limit
        'stopLimitTimeInForce': 'GTC'
    }
```

## 📊 TIPOS DE ÓRDENES PARA EL BOT

### 🔹 Orden de Entrada (MARKET/LIMIT)
```python
entry_order = {
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'MARKET',
    'quantity': '0.001'
}
```

### 🔹 Stop Loss (STOP_LOSS)
```python
stop_loss_order = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'STOP_LOSS',
    'quantity': '0.001',
    'stopPrice': '44000.0'
}
```

### 🔹 Take Profit (TAKE_PROFIT)
```python
take_profit_order = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'type': 'TAKE_PROFIT',
    'quantity': '0.001',
    'stopPrice': '46000.0'
}
```

### 🔹 OCO (One-Cancels-Other)
```python
oco_order = {
    'symbol': 'BTCUSDT',
    'side': 'SELL',
    'quantity': '0.001',
    'price': '46000.0',        # Take Profit
    'stopPrice': '44000.0',    # Stop Loss trigger
    'stopLimitPrice': '43900.0' # Stop Loss limit
}
```

## 🧪 DATOS PARA TESTING

### 📝 Orden de Prueba Básica
```python
test_order = {
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'MARKET',
    'quantity': '0.001',
    'timestamp': int(time.time() * 1000),
    'newClientOrderId': 'test_bot_order_001'
}
```

### 📊 Con Cálculo de Comisiones
```python
test_order_with_commission = {
    'symbol': 'BTCUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'quantity': '0.001',
    'price': '45000.0',
    'timeInForce': 'GTC',
    'computeCommissionRates': True,  # Para obtener comisiones
    'timestamp': int(time.time() * 1000)
}
```

## 🔄 FLUJO DE TRABAJO

1. **Trading Bot genera señal** → `trade_signal`
2. **Mapper transforma datos** → `binance_params`
3. **Conector envía a Binance** → `/api/v3/order/test`
4. **Respuesta de validación** → Confirma parámetros correctos
5. **Si OK, enviar orden real** → `/api/v3/order`

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear método `test_order()` en BinanceConnector
- [ ] Implementar `TradingOrderMapper` class
- [ ] Agregar validación de parámetros
- [ ] Implementar manejo de errores
- [ ] Crear tests con datos simulados
- [ ] Documentar respuestas de la API
- [ ] Implementar logging de órdenes
- [ ] Agregar soporte para OCO orders

---

**Fecha de creación**: $(date)
**Versión**: 1.0
**Estado**: Documentación de mapeo completa