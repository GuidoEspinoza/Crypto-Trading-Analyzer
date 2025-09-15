# Documentación de la API Principal (main.py)

## Descripción General

Este archivo contiene la API principal del sistema de análisis de trading de criptomonedas, construida con FastAPI. Proporciona endpoints para gestión del bot de trading, análisis de estrategias, paper trading y monitoreo del sistema.

## Configuración

La aplicación utiliza un sistema de configuración centralizado a través de `main_config.py` que permite:

- **Configuración de API**: Puerto, host, CORS, metadatos
- **Configuración de Exchange**: Configuración de Binance
- **Configuración de Trading**: Modos, límites, confirmaciones
- **Configuración de Análisis**: Timeframes, símbolos por defecto, umbrales
- **Configuración de Estrategias**: Estrategias disponibles y sus características
- **Configuración de Paper Trading**: Balance inicial, límites de posición, stop loss/take profit

## Endpoints Principales

### 🏠 Endpoints Básicos

#### `GET /`
- **Descripción**: Página de bienvenida de la API
- **Respuesta**: Información básica de la API y enlaces útiles

#### `GET /health`
- **Descripción**: Health check del sistema
- **Respuesta**: Estado del sistema, conectividad del exchange, versión de la API

### 🤖 Gestión del Bot

#### `GET /bot/status`
- **Descripción**: Obtener estado actual del bot de trading
- **Respuesta**: Estado, configuración, estadísticas de trading

#### `POST /bot/start`
- **Descripción**: Iniciar el bot de trading
- **Body**: `BotStartRequest` (símbolos, intervalo de análisis, trading habilitado)
- **Respuesta**: Confirmación de inicio y configuración aplicada

#### `POST /bot/stop`
- **Descripción**: Detener el bot de trading
- **Respuesta**: Confirmación de parada y estadísticas finales

#### `GET /bot/report`
- **Descripción**: Obtener reporte detallado del bot
- **Respuesta**: Estadísticas de trading, rendimiento, análisis de riesgo

#### `GET /bot/config`
- **Descripción**: Obtener configuración actual del bot
- **Respuesta**: Configuración completa del sistema

### 📊 Trading y Modos

#### `GET /bot/trading-mode`
- **Descripción**: Obtener modo de trading actual
- **Respuesta**: Modo actual, disponibilidad de live trading

#### `POST /bot/trading-mode`
- **Descripción**: Configurar modo de trading
- **Body**: `TradingModeRequest` (modo, confirmación para live trading)
- **Respuesta**: Confirmación del modo configurado

#### `GET /bot/trading-capabilities`
- **Descripción**: Obtener capacidades de trading disponibles
- **Respuesta**: Estrategias, modos disponibles, recomendaciones

### 🚨 Gestión de Emergencias

#### `POST /bot/force-analysis`
- **Descripción**: Forzar análisis inmediato
- **Respuesta**: Resultados del análisis forzado

#### `POST /bot/emergency-stop`
- **Descripción**: Parada de emergencia del sistema
- **Respuesta**: Confirmación de parada de emergencia

### 🔍 Estrategias Mejoradas

#### `GET /enhanced/strategies/list`
- **Descripción**: Listar estrategias mejoradas disponibles
- **Respuesta**: Lista de estrategias con descripciones y características

#### `GET /enhanced/analyze/{strategy_name}/{symbol}`
- **Descripción**: Analizar símbolo con estrategia específica
- **Parámetros**:
  - `strategy_name`: Nombre de la estrategia
  - `symbol`: Símbolo a analizar
  - `timeframe`: Timeframe (opcional, por defecto desde configuración)
- **Respuesta**: Análisis detallado con señales y recomendaciones

#### `GET /test/strategy/{strategy_name}/{symbol}`
- **Descripción**: Prueba comprehensiva de estrategia
- **Parámetros**:
  - `strategy_name`: Nombre de la estrategia
  - `symbol`: Símbolo a analizar
  - `timeframe`: Timeframe (opcional)
  - `test_mode`: Modo de prueba (signal_only, backtest, etc.)
- **Respuesta**: Resultados de la prueba con métricas de rendimiento

### ⚠️ Análisis de Riesgo

#### `GET /enhanced/risk-analysis/{symbol}`
- **Descripción**: Análisis de riesgo mejorado para un símbolo
- **Parámetros**:
  - `symbol`: Símbolo a analizar
  - `timeframe`: Timeframe (opcional)
- **Respuesta**: Análisis de riesgo con recomendaciones de posición

### 💼 Paper Trading

#### `GET /paper-trading/portfolio`
- **Descripción**: Obtener estado del portafolio de paper trading
- **Respuesta**: Balance, posiciones abiertas, rendimiento

#### `POST /paper-trading/trade`
- **Descripción**: Ejecutar trade en paper trading
- **Body**: Detalles del trade (símbolo, cantidad, tipo)
- **Respuesta**: Confirmación de ejecución del trade

#### `GET /paper-trading/history`
- **Descripción**: Obtener historial de paper trading
- **Respuesta**: Historial de trades y rendimiento

#### `POST /paper-trading/reset`
- **Descripción**: Resetear portafolio de paper trading
- **Respuesta**: Confirmación de reset con nuevo balance

## Modelos de Datos

### BotStartRequest
```python
class BotStartRequest(BaseModel):
    symbols: List[str] = ["BTCUSDT", "ETHUSDT"]
    analysis_interval: int = 300  # segundos
    enable_trading: bool = False
```

### TradingModeRequest
```python
class TradingModeRequest(BaseModel):
    trading_mode: str  # "paper" o "live"
    confirm_live_trading: bool = False
```

## Configuración de Entorno

### Variables de Entorno Requeridas

```bash
# Configuración de Binance
BINANCE_API_KEY=tu_api_key
BINANCE_SECRET_KEY=tu_secret_key
BINANCE_TESTNET=true  # Para usar testnet

# Configuración de la API
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Configuración de Trading
DEFAULT_TRADING_MODE=paper
MAX_DAILY_TRADES=50
CONFIDENCE_THRESHOLD=0.6

# Configuración de Paper Trading
INITIAL_BALANCE=10000.0
MAX_POSITION_PERCENTAGE=0.1
DEFAULT_STOP_LOSS=0.02
DEFAULT_TAKE_PROFIT=0.04
```

## Manejo de Errores

La API implementa un manejo robusto de errores con:

- **Códigos de estado HTTP apropiados**
- **Mensajes de error descriptivos**
- **Logging detallado para debugging**
- **Validación de parámetros de entrada**
- **Manejo de errores de conectividad del exchange**

## Seguridad

- **CORS configurado para desarrollo**
- **Validación de parámetros de entrada**
- **Límites de trading para prevenir pérdidas**
- **Modo paper trading por defecto**
- **Confirmación requerida para live trading**

## Logging

El sistema utiliza logging estructurado con:

- **Niveles de log configurables**
- **Rotación de archivos de log**
- **Logging de todas las operaciones de trading**
- **Métricas de rendimiento**

## Uso Recomendado

1. **Desarrollo**: Usar en modo paper trading con testnet de Binance
2. **Testing**: Ejecutar tests comprehensivos antes de producción
3. **Producción**: Configurar adecuadamente las variables de entorno
4. **Monitoreo**: Usar endpoints de health check y status regularmente

## Dependencias Principales

- **FastAPI**: Framework web
- **ccxt**: Conectividad con exchanges
- **pandas**: Análisis de datos
- **numpy**: Cálculos numéricos
- **uvicorn**: Servidor ASGI

## Notas de Rendimiento

- **Análisis asíncrono**: Todos los endpoints son asíncronos
- **Cache de datos**: Implementado para mejorar rendimiento
- **Límites de rate**: Respeta los límites del exchange
- **Timeouts configurables**: Para operaciones de red

## Roadmap

- [ ] Implementación de live trading
- [ ] Más estrategias de trading
- [ ] Dashboard web integrado
- [ ] Notificaciones en tiempo real
- [ ] Análisis de sentimiento de mercado
- [ ] Integración con más exchanges