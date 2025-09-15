# 📊 PaperTrader - Documentación Completa

## 🎯 Descripción General

El `PaperTrader` es un simulador de trading avanzado que replica el comportamiento de un exchange real sin usar dinero real. Está diseñado para proporcionar una experiencia de trading lo más realista posible, incluyendo simulación de slippage, comisiones, y delays de ejecución.

## 🏗️ Arquitectura

### Componentes Principales

1. **Simulador de Órdenes**: Maneja la ejecución de órdenes BUY/SELL
2. **Gestor de Portfolio**: Rastrea balances y posiciones
3. **Simulador de Mercado**: Simula condiciones reales de mercado
4. **Gestor de Riesgo**: Integra con el sistema de gestión de riesgo

### Flujo de Ejecución

```
Señal de Trading → Validación → Simulación de Slippage → Cálculo de Fees → Ejecución → Actualización de Portfolio
```

## 🔧 Configuración

### Parámetros Principales

Todos los parámetros están centralizados en `src/config/config.py` bajo la clase `PaperTraderConfig`:

```python
# Balance inicial
INITIAL_BALANCE: float = 1000.0  # USDT

# Límites de posición
max_position_size: float = 0.8    # 80% del balance máximo por posición
max_total_exposure: float = 0.75  # 75% exposición total máxima
min_trade_value: float = 10.0     # Valor mínimo por trade

# Simulación realista
max_slippage: float = 0.1         # 10% slippage máximo
trading_fees: float = 0.001       # 0.1% comisión por trade
max_balance_usage: float = 95.0   # 95% del balance utilizable
```

### Perfiles de Trading

El comportamiento se adapta automáticamente según el perfil activo:

- **🚀 RÁPIDO**: Timeframes cortos (1m-15m), mayor frecuencia
- **⚡ AGRESIVO**: Timeframes medios (15m-1h), balance riesgo/velocidad
- **🛡️ ÓPTIMO**: Timeframes largos (1h-1d), enfoque conservador

## 📋 API Principal

### Métodos Públicos

#### `execute_signal(signal: TradingSignal) -> TradeResult`

Ejecuta una señal de trading (compra o venta).

**Parámetros:**
- `signal`: Objeto TradingSignal con la información del trade

**Retorna:**
- `TradeResult`: Resultado de la ejecución con detalles del trade

**Ejemplo:**
```python
trader = PaperTrader()
result = trader.execute_signal(buy_signal)
if result.success:
    print(f"Trade ejecutado: {result.message}")
```

#### `get_portfolio_summary() -> Dict`

Obtiene un resumen completo del portfolio.

**Retorna:**
```python
{
    'total_value': 1250.50,
    'usdt_balance': 850.25,
    'positions': [
        {
            'symbol': 'BTC',
            'quantity': 0.01,
            'value': 400.25,
            'pnl': 50.25
        }
    ],
    'total_pnl': 250.50,
    'total_pnl_percentage': 25.05
}
```

#### `get_balance(symbol: str = "USDT") -> float`

Obtiene el balance de un símbolo específico.

#### `reset_portfolio() -> Dict`

Reinicia el portfolio al estado inicial.

### Métodos de Análisis

#### `calculate_portfolio_performance() -> Dict`

Calcula métricas de rendimiento del portfolio.

#### `get_trade_history() -> List[Dict]`

Obtiene el historial completo de trades.

#### `get_open_positions() -> List[Dict]`

Obtiene todas las posiciones abiertas.

## 🎯 Simulación Realista

### Simulación de Slippage

El sistema simula slippage realista basado en:

- **Tipo de orden**: BUY (aumenta precio) vs SELL (disminuye precio)
- **Volatilidad del mercado**: Mayor slippage en mercados volátiles
- **Liquidez**: Menor slippage en mercados líquidos

```python
def _simulate_slippage(self, price: float, order_type: str) -> float:
    max_slippage = PaperTraderConfig.get_max_slippage()
    slippage_factor = random.uniform(0.1, 1.0) * max_slippage
    
    if order_type == "BUY":
        return price * (1 + slippage_factor)
    else:
        return price * (1 - slippage_factor)
```

### Simulación de Comisiones

Las comisiones se calculan de forma realista:

- **Comisión base**: Configurable por perfil (típicamente 0.1%)
- **Variación**: ±5% para simular variaciones reales
- **Aplicación**: Se descuenta del balance en cada trade

### Delays de Ejecución

Simula delays típicos de exchanges reales (0.1-2.0 segundos).

## 🛡️ Gestión de Riesgo Integrada

### Stop Loss y Take Profit Automáticos

Si una señal no incluye SL/TP, el sistema los calcula automáticamente:

1. **Prioridad 1**: Usar EnhancedRiskManager para cálculo dinámico
2. **Fallback**: Usar porcentajes fijos desde configuración

### Validaciones de Seguridad

- **Balance suficiente**: Verifica balance incluyendo fees
- **Límites de posición**: Respeta max_position_size
- **Valor mínimo**: Rechaza trades menores al mínimo
- **Exposición total**: Controla exposición máxima

## 📊 Métricas y Reporting

### Métricas Calculadas

- **PnL Total**: Ganancia/pérdida total
- **PnL Porcentual**: Rendimiento porcentual
- **Número de trades**: Trades ejecutados
- **Tasa de éxito**: Porcentaje de trades ganadores
- **Drawdown máximo**: Pérdida máxima desde pico
- **Sharpe Ratio**: Ratio riesgo-rendimiento

### Logging Detallado

Todos los trades se registran con información completa:

```
✅ BUY executed: 0.001000 BTC @ $45,250.50 (exec: $45,275.25, fee: $0.4528)
💰 USDT Balance after purchase: $954.27
```

## 🔄 Integración con el Sistema

### Base de Datos

Todos los trades se almacenan en la base de datos con:

- **Información del trade**: Símbolo, cantidad, precios
- **Metadatos**: Estrategia, confianza, timeframe
- **Simulación**: Slippage aplicado, fees cobrados
- **Timestamps**: Tiempo de entrada y salida

### Compatibilidad

El PaperTrader es compatible con:

- **TradingSignal**: Señales del sistema de estrategias
- **EnhancedRiskManager**: Gestión de riesgo avanzada
- **Database Models**: Modelos de base de datos
- **Configuration System**: Sistema de configuración centralizado

## 🚀 Ejemplos de Uso

### Uso Básico

```python
from src.core.paper_trader import PaperTrader
from src.core.enhanced_strategies import TradingSignal

# Inicializar trader
trader = PaperTrader(initial_balance=1000.0)

# Crear señal de compra
buy_signal = TradingSignal(
    symbol="BTC/USDT",
    signal_type="BUY",
    price=45000.0,
    confidence_score=85.0,
    strategy_name="RSI_Strategy"
)

# Ejecutar trade
result = trader.execute_signal(buy_signal)
print(f"Resultado: {result.message}")

# Ver portfolio
summary = trader.get_portfolio_summary()
print(f"Valor total: ${summary['total_value']:.2f}")
```

### Uso Avanzado con Gestión de Riesgo

```python
# Señal con SL/TP personalizados
advanced_signal = TradingSignal(
    symbol="ETH/USDT",
    signal_type="BUY",
    price=3000.0,
    confidence_score=90.0,
    strategy_name="Enhanced_Strategy",
    stop_loss_price=2850.0,    # SL a -5%
    take_profit_price=3300.0   # TP a +10%
)

result = trader.execute_signal(advanced_signal)
```

### Análisis de Rendimiento

```python
# Calcular métricas de rendimiento
performance = trader.calculate_portfolio_performance()
print(f"ROI: {performance['roi_percentage']:.2f}%")
print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {performance['max_drawdown']:.2f}%")

# Obtener historial de trades
history = trader.get_trade_history()
for trade in history[-5:]:  # Últimos 5 trades
    print(f"{trade['type']}: {trade['symbol']} - PnL: ${trade['pnl']:.2f}")
```

## 🔧 Configuración Avanzada

### Personalización de Slippage

```python
# En config.py, ajustar por perfil
"max_slippage": 0.05,  # 5% slippage máximo para perfil conservador
"max_slippage": 0.15,  # 15% slippage máximo para perfil agresivo
```

### Ajuste de Comisiones

```python
# Simular diferentes tipos de exchange
"trading_fees": 0.001,  # 0.1% (Binance)
"trading_fees": 0.0025, # 0.25% (Coinbase)
"trading_fees": 0.0005, # 0.05% (exchange premium)
```

## 🐛 Troubleshooting

### Errores Comunes

1. **"Trade value too small"**
   - Aumentar el valor del trade o reducir `min_trade_value`

2. **"Insufficient balance"**
   - Verificar que hay suficiente USDT incluyendo fees

3. **"No asset balance to sell"**
   - Verificar que hay posiciones abiertas del asset

### Logs de Debug

Habilitar logging detallado:

```python
import logging
logging.getLogger('src.core.paper_trader').setLevel(logging.DEBUG)
```

## 🔮 Roadmap

### Próximas Mejoras

- [ ] Simulación de fills parciales
- [ ] Simulación de rechazos de órdenes
- [ ] Integración con datos de orderbook reales
- [ ] Simulación de latencia de red
- [ ] Backtesting histórico mejorado
- [ ] Métricas de riesgo avanzadas

### Optimizaciones Planificadas

- [ ] Cache de cálculos de portfolio
- [ ] Paralelización de simulaciones
- [ ] Optimización de queries de base de datos
- [ ] Compresión de datos históricos

---

**Última actualización**: Enero 2025  
**Versión**: 2.0  
**Autor**: Sistema de Trading Crypto Analyzer