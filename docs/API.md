# API Documentation - Crypto Trading Analyzer

## 📋 Descripción General

Esta documentación describe las interfaces y APIs internas del sistema de trading de criptomonedas, incluyendo los módulos principales, clases y métodos disponibles.

## 🏗️ Arquitectura de la API

### Módulos Principales

```
src/
├── core/           # Motor principal de trading
├── strategies/     # Estrategias de trading
├── database/       # Gestión de base de datos
├── utils/          # Utilidades y helpers
└── config/         # Configuración del sistema
```

## 🤖 Core Trading Engine

### TradingBot

**Ubicación**: `src/core/trading_bot.py`

#### Inicialización

```python
from src.core.trading_bot import TradingBot

# Inicializar bot
bot = TradingBot(
    config_file="config/trading_config.json",
    paper_trading=True  # False para trading real
)
```

#### Métodos Principales

##### `start_trading()`
```python
def start_trading() -> None:
    """Inicia el bucle principal de trading"""
```

##### `stop_trading()`
```python
def stop_trading() -> None:
    """Detiene el trading de forma segura"""
```

##### `get_portfolio_status()`
```python
def get_portfolio_status() -> Dict[str, Any]:
    """Retorna el estado actual del portfolio
    
    Returns:
        Dict con balance, posiciones abiertas, PnL, etc.
    """
```

##### `execute_trade()`
```python
def execute_trade(
    symbol: str,
    side: str,  # 'buy' o 'sell'
    amount: float,
    price: Optional[float] = None,
    order_type: str = 'market'
) -> Dict[str, Any]:
    """Ejecuta una orden de trading
    
    Args:
        symbol: Par de trading (ej: 'BTC/USDT')
        side: Dirección de la orden
        amount: Cantidad a tradear
        price: Precio límite (opcional)
        order_type: Tipo de orden ('market', 'limit')
    
    Returns:
        Dict con detalles de la orden ejecutada
    """
```

### Portfolio Manager

**Ubicación**: `src/core/portfolio_manager.py`

#### Métodos Principales

##### `get_balance()`
```python
def get_balance(currency: str = 'USDT') -> float:
    """Obtiene el balance de una moneda específica"""
```

##### `get_positions()`
```python
def get_positions() -> List[Dict[str, Any]]:
    """Retorna todas las posiciones abiertas"""
```

##### `calculate_pnl()`
```python
def calculate_pnl(symbol: str) -> Dict[str, float]:
    """Calcula PnL para un símbolo específico
    
    Returns:
        {
            'unrealized_pnl': float,
            'realized_pnl': float,
            'total_pnl': float
        }
    """
```

## 📈 Estrategias de Trading

### Base Strategy

**Ubicación**: `src/strategies/base_strategy.py`

```python
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    @abstractmethod
    def generate_signal(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera señal de trading basada en datos de mercado
        
        Args:
            data: Datos de mercado (OHLCV, indicadores, etc.)
        
        Returns:
            {
                'action': 'buy'|'sell'|'hold',
                'confidence': float,  # 0.0 - 1.0
                'stop_loss': float,
                'take_profit': float,
                'reasoning': str
            }
        """
```

### Estrategias Disponibles

#### RSI Strategy
```python
from src.strategies.rsi_strategy import RSIStrategy

strategy = RSIStrategy(
    rsi_period=14,
    oversold_threshold=30,
    overbought_threshold=70
)

signal = strategy.generate_signal(market_data)
```

#### Moving Average Strategy
```python
from src.strategies.ma_strategy import MovingAverageStrategy

strategy = MovingAverageStrategy(
    fast_period=10,
    slow_period=20
)

signal = strategy.generate_signal(market_data)
```

#### Bollinger Bands Strategy
```python
from src.strategies.bollinger_strategy import BollingerBandsStrategy

strategy = BollingerBandsStrategy(
    period=20,
    std_dev=2
)

signal = strategy.generate_signal(market_data)
```

## 🗄️ Database API

### Database Manager

**Ubicación**: `src/database/database.py`

#### Métodos Principales

##### `get_session()`
```python
def get_session() -> Session:
    """Retorna una sesión de base de datos"""
```

##### `save_trade()`
```python
def save_trade(trade_data: Dict[str, Any]) -> int:
    """Guarda un trade en la base de datos
    
    Args:
        trade_data: Datos del trade
    
    Returns:
        ID del trade guardado
    """
```

##### `get_trades()`
```python
def get_trades(
    symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None
) -> List[Trade]:
    """Obtiene trades con filtros opcionales"""
```

### Modelos de Datos

#### Trade Model
```python
class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # 'buy' or 'sell'
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='pending')
    strategy_name = Column(String(50))
    pnl = Column(Float, default=0.0)
```

#### Portfolio Model
```python
class Portfolio(Base):
    __tablename__ = 'portfolio'
    
    id = Column(Integer, primary_key=True)
    currency = Column(String(10), nullable=False)
    balance = Column(Float, nullable=False)
    locked = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

## 🛠️ Utilidades

### Market Data Utils

**Ubicación**: `src/utils/market_data.py`

#### `fetch_ohlcv()`
```python
def fetch_ohlcv(
    symbol: str,
    timeframe: str = '1h',
    limit: int = 100
) -> pd.DataFrame:
    """Obtiene datos OHLCV del mercado
    
    Args:
        symbol: Par de trading
        timeframe: Marco temporal ('1m', '5m', '1h', '1d')
        limit: Número de velas
    
    Returns:
        DataFrame con columnas: timestamp, open, high, low, close, volume
    """
```

#### `calculate_indicators()`
```python
def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula indicadores técnicos
    
    Args:
        df: DataFrame con datos OHLCV
    
    Returns:
        DataFrame con indicadores añadidos (RSI, MA, Bollinger, etc.)
    """
```

### Risk Management

**Ubicación**: `src/utils/risk_management.py`

#### `calculate_position_size()`
```python
def calculate_position_size(
    account_balance: float,
    risk_percentage: float,
    entry_price: float,
    stop_loss_price: float
) -> float:
    """Calcula el tamaño de posición basado en gestión de riesgo
    
    Args:
        account_balance: Balance de la cuenta
        risk_percentage: Porcentaje de riesgo (0.01 = 1%)
        entry_price: Precio de entrada
        stop_loss_price: Precio de stop loss
    
    Returns:
        Tamaño de posición recomendado
    """
```

#### `validate_trade()`
```python
def validate_trade(
    trade_data: Dict[str, Any],
    portfolio: Dict[str, Any]
) -> Tuple[bool, str]:
    """Valida si un trade es seguro de ejecutar
    
    Returns:
        (is_valid, reason)
    """
```

## 📊 Monitoring API

### Trading Monitor

**Ubicación**: `src/tools/trading_monitor.py`

#### Uso desde línea de comandos
```bash
# Mostrar estado general
python src/tools/trading_monitor.py --status

# Mostrar trades recientes
python src/tools/trading_monitor.py --trades --limit 10

# Mostrar métricas de rendimiento
python src/tools/trading_monitor.py --performance

# Modo interactivo
python src/tools/trading_monitor.py --interactive
```

#### Uso programático
```python
from src.tools.trading_monitor import TradingMonitor

monitor = TradingMonitor()

# Obtener métricas
metrics = monitor.get_performance_metrics()
print(f"Total PnL: {metrics['total_pnl']}")
print(f"Win Rate: {metrics['win_rate']}%")

# Obtener trades recientes
recent_trades = monitor.get_recent_trades(limit=5)
```

## 🔧 Configuración

### Config Manager

**Ubicación**: `src/config/config_manager.py`

#### Cargar configuración
```python
from src.config.config_manager import ConfigManager

config = ConfigManager()

# Obtener configuración de trading
trading_config = config.get_trading_config()
print(trading_config['default_risk_percentage'])

# Obtener configuración de exchange
exchange_config = config.get_exchange_config()
print(exchange_config['binance']['testnet'])
```

### Variables de Entorno

```python
import os

# API Keys
api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

# Configuración de trading
trading_mode = os.getenv('TRADING_MODE', 'paper')  # 'paper' o 'live'
risk_level = os.getenv('RISK_LEVEL', 'conservative')
```

## 🚨 Manejo de Errores

### Excepciones Personalizadas

```python
from src.utils.exceptions import (
    TradingError,
    InsufficientFundsError,
    InvalidSymbolError,
    APIConnectionError
)

try:
    bot.execute_trade('BTC/USDT', 'buy', 0.001)
except InsufficientFundsError as e:
    print(f"Fondos insuficientes: {e}")
except APIConnectionError as e:
    print(f"Error de conexión: {e}")
except TradingError as e:
    print(f"Error de trading: {e}")
```

## 📝 Logging

### Configuración de Logs

```python
import logging
from src.utils.logger import setup_logger

# Configurar logger
logger = setup_logger('trading_bot', level=logging.INFO)

# Usar logger
logger.info("Iniciando bot de trading")
logger.warning("Señal de trading débil")
logger.error("Error al ejecutar orden")
```

### Niveles de Log

- **DEBUG**: Información detallada para debugging
- **INFO**: Información general del funcionamiento
- **WARNING**: Advertencias que no detienen la ejecución
- **ERROR**: Errores que pueden afectar el funcionamiento
- **CRITICAL**: Errores críticos que detienen el sistema

## 🔒 Seguridad

### Mejores Prácticas

1. **Nunca hardcodear API keys**
```python
# ❌ Incorrecto
api_key = "your_api_key_here"

# ✅ Correcto
api_key = os.getenv('BINANCE_API_KEY')
```

2. **Validar todas las entradas**
```python
def execute_trade(symbol: str, amount: float):
    if not symbol or amount <= 0:
        raise ValueError("Parámetros inválidos")
```

3. **Usar paper trading para pruebas**
```python
bot = TradingBot(paper_trading=True)  # Siempre para desarrollo
```

## 📚 Ejemplos de Uso

### Ejemplo Básico

```python
from src.core.trading_bot import TradingBot
from src.strategies.rsi_strategy import RSIStrategy

# Inicializar bot con estrategia RSI
bot = TradingBot(paper_trading=True)
strategy = RSIStrategy()
bot.add_strategy('BTC/USDT', strategy)

# Iniciar trading
bot.start_trading()
```

### Ejemplo Avanzado

```python
from src.core.trading_bot import TradingBot
from src.strategies.ma_strategy import MovingAverageStrategy
from src.utils.risk_management import RiskManager

# Configurar bot con múltiples estrategias
bot = TradingBot(paper_trading=True)
risk_manager = RiskManager(max_risk_per_trade=0.02)

# Añadir estrategias para diferentes pares
ma_strategy = MovingAverageStrategy(fast_period=10, slow_period=20)
bot.add_strategy('BTC/USDT', ma_strategy)
bot.add_strategy('ETH/USDT', ma_strategy)

# Configurar gestión de riesgo
bot.set_risk_manager(risk_manager)

# Iniciar con callback personalizado
def on_trade_executed(trade_data):
    print(f"Trade ejecutado: {trade_data}")

bot.on_trade_executed = on_trade_executed
bot.start_trading()
```

---

**Nota**: Esta API está en desarrollo activo. Consulta el código fuente para las implementaciones más actualizadas.