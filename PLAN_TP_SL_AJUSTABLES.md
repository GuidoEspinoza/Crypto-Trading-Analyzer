# Plan de Implementación: TP/SL Ajustables

## Objetivo
Implementar un sistema de Take Profit y Stop Loss ajustables dinámicamente para el bot de trading, utilizando la estrategia de cancelar y recrear órdenes OCO en lugar de cerrar y reabrir posiciones.

## Flujo de Trabajo Propuesto

### 1. Hilo Principal (Señales de Trading)
- Detectar señales de compra/venta
- Enviar órdenes a Binance con TP/SL inicial
- Usar órdenes OCO para protección automática
- Continuar análisis de mercado

### 2. Hilo Paralelo (Monitoreo y Ajuste)
- Monitorear posiciones activas cada X segundos
- Analizar condiciones de mercado (ATR, volatilidad, tendencia)
- Calcular nuevos niveles de TP/SL si es necesario
- Ejecutar ajustes hasta 5 veces por posición

## Estrategia de Ajuste

### Cancelar y Recrear Órdenes OCO
```python
# Pseudocódigo del proceso
1. Identificar posición que necesita ajuste
2. Cancelar órdenes OCO existentes (TP/SL actuales)
3. Calcular nuevos niveles de TP/SL basados en:
   - Movimiento del precio
   - ATR actualizado
   - Configuración dinámica del bot
4. Crear nueva orden OCO con nuevos niveles
5. Actualizar contador de ajustes (máximo 5)
```

### Ventajas de Este Enfoque
- ✅ Mantiene la posición original abierta
- ✅ Menores costos (solo fees de órdenes, no de trading)
- ✅ Mayor control sobre la gestión de riesgo
- ✅ No cuenta como nuevo trade para límites diarios
- ✅ Permite optimización continua

## Configuración Dinámica

### Parámetros de TP/SL (desde config.py)
```python
"stop_loss_range": {
    "atr_multiplier_min": 1.5,
    "atr_multiplier_max": 5.5
},
"take_profit_range": {
    "atr_multiplier_min": 2.0,
    "atr_multiplier_max": 8.0
}
```

### Condiciones de Ajuste
1. **Escalado de Ganancias**: Si el precio se mueve favorablemente
2. **Gestión de Riesgo**: Si aumenta la volatilidad
3. **Trailing Stop**: Seguir tendencias ganadoras
4. **Stop de Emergencia**: Condiciones adversas del mercado

## Implementación Técnica

### Estructura de Clases
```python
class PositionAdjuster:
    def __init__(self, binance_client, config):
        self.client = binance_client
        self.config = config
        self.adjustment_counts = {}  # Contador por posición
        
    async def monitor_positions(self):
        # Hilo paralelo de monitoreo
        
    def calculate_new_levels(self, position, market_data):
        # Calcular nuevos TP/SL
        
    async def adjust_orders(self, position, new_tp, new_sl):
        # Cancelar y recrear órdenes OCO
```

### Integración con Trading Bot
1. Agregar `PositionAdjuster` al TradingBot (no LiveTradingBot)
2. Iniciar hilo paralelo de monitoreo en TradingBot
3. Configurar intervalos de verificación
4. Implementar logging detallado

## Pruebas Antes de Binance

### Modo Simulación
1. Usar paper trading para probar la lógica
2. Simular órdenes OCO sin conexión real
3. Verificar cálculos de TP/SL dinámicos
4. Probar límite de 5 ajustes por posición

### Métricas a Validar
- Precisión de cálculos de TP/SL
- Timing de ajustes
- Gestión de errores
- Performance del sistema

## Arquitectura Correcta: Separación de Responsabilidades

### Principio Fundamental
- **TradingBot**: Maneja TODA la lógica de trading y ajustes
- **LiveTradingBot**: Solo MUESTRA lo que hace el TradingBot
- **PositionAdjuster**: Se integra con TradingBot, no con LiveTradingBot

### Integración con trading_bot.py (NO live_trading_bot.py)
1. **Modificar la clase `TradingBot`**:
   - Agregar instancia de `PositionAdjuster`
   - Implementar lógica de ajustes en paralelo
   - Generar eventos/logs que LiveTradingBot pueda mostrar

2. **LiveTradingBot como Visualizador**:
   - Escucha eventos del TradingBot
   - Muestra análisis, órdenes y ajustes por consola
   - NO ejecuta lógica de trading
   - Solo formatea y presenta información

3. **Flujo de Comunicación**:
   ```
   TradingBot (lógica) → Eventos/Logs → LiveTradingBot (visualización)
   ```

### Implementación en TradingBot

#### 1. Modificaciones en TradingBot
```python
class TradingBot:
    def __init__(self):
        # ... código existente ...
        self.position_adjuster = PositionAdjuster(simulation_mode=True)
        self.adjustment_task = None
    
    def start_position_monitoring(self):
        # Iniciar monitoreo de posiciones en paralelo
        monitoring_thread = threading.Thread(
            target=self.position_adjuster.start_monitoring,
            daemon=True
        )
        monitoring_thread.start()
```

#### 2. Eventos para LiveTradingBot
```python
def emit_adjustment_event(self, symbol, old_tp, old_sl, new_tp, new_sl):
    """Emite evento de ajuste para que LiveTradingBot lo muestre"""
    event = {
        'type': 'position_adjustment',
        'symbol': symbol,
        'old_levels': {'tp': old_tp, 'sl': old_sl},
        'new_levels': {'tp': new_tp, 'sl': new_sl},
        'timestamp': datetime.now()
    }
    # LiveTradingBot escucha estos eventos
    self.event_queue.put(event)
```

### Flujo de Trabajo Integrado

#### En TradingBot (Lógica Real)
**Hilo Principal**:
1. **Análisis de Mercado**: `analyze_and_trade()` cada 60 segundos
2. **Generación de Señales**: Estrategias analizan símbolos
3. **Ejecución de Trades**: Ejecuta trades aprobados
4. **Emisión de Eventos**: Para que LiveTradingBot los muestre

**Hilo Paralelo (Nuevo)**:
1. **Monitoreo Continuo**: `PositionAdjuster` revisa posiciones cada 30 segundos
2. **Evaluación de Ajustes**: Calcula nuevos niveles de TP/SL según condiciones
3. **Simulación de OCO**: Simula cancelación y recreación de órdenes
4. **Emisión de Eventos**: Notifica ajustes a LiveTradingBot

#### En LiveTradingBot (Solo Visualización)
1. **Escucha Eventos**: Del TradingBot
2. **Formatea y Muestra**: Por consola:
   - Análisis de mercado
   - Órdenes BUY/SELL con TP/SL específicos
   - Ajustes de posiciones en tiempo real
   - Estadísticas actualizadas

### Configuración de Pruebas

#### Modo Simulación Completa
```python
# En trading_bot.py (NO en live_trading_bot.py)
SIMULATION_MODE = True  # Para pruebas sin Binance

if SIMULATION_MODE:
    # Usar precios simulados
    # Simular latencia de API
    # Logging detallado de todas las operaciones
    # Emitir eventos para LiveTradingBot
```

#### Parámetros de Prueba
- **Intervalo de Monitoreo**: 30 segundos (configurable)
- **Máximo Ajustes**: 5 por posición
- **Condiciones de Ajuste**:
  - Ganancia > 2%: Escalado de ganancias
  - Ganancia > 5%: Trailing stop
  - Pérdida < -1%: Gestión de riesgo

## Próximos Pasos

1. **Fase 1**: Integrar `PositionAdjuster` en `trading_bot.py` (NO en live_trading_bot.py)
2. **Fase 2**: Agregar hilo paralelo de monitoreo en TradingBot
3. **Fase 3**: Implementar sistema de eventos entre TradingBot y LiveTradingBot
4. **Fase 4**: Actualizar LiveTradingBot para mostrar eventos de ajustes
5. **Fase 5**: Pruebas extensivas en modo simulación
6. **Fase 6**: Validar lógica de cálculo de TP/SL
7. **Fase 7**: Preparar para conexión con Binance API

## Consideraciones de Riesgo

- **Rate Limits**: Respetar límites de API de Binance
- **Latencia**: Minimizar tiempo entre cancelación y recreación
- **Slippage**: Considerar movimientos rápidos del mercado
- **Fees**: Optimizar frecuencia de ajustes
- **Failsafe**: Mecanismos de emergencia si fallan los ajustes

---

**Nota**: Este documento será actualizado conforme avance la implementación.