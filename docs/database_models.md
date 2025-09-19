# 📊 Modelos de Base de Datos - Crypto Trading Analyzer

Documentación completa de los modelos de datos utilizados en el sistema de trading.

## Descripción General

El sistema utiliza SQLAlchemy como ORM para gestionar la base de datos SQLite. Los modelos están diseñados para soportar tanto trading en papel (paper trading) como trading real, proporcionando un sistema completo de tracking y análisis.

### Características Principales

- **Dual Mode**: Soporte para paper trading y trading real
- **Auditoría**: Timestamps automáticos para tracking de cambios
- **Performance**: Índices optimizados para consultas frecuentes
- **Flexibilidad**: Campos opcionales para diferentes estrategias
- **Integridad**: Constraints y validaciones a nivel de base de datos

## Modelos de Datos

### 1. Trade - Registro de Operaciones

```python
class Trade(Base):
    __tablename__ = "trades"
```

**Propósito**: Almacena todas las operaciones de trading ejecutadas, tanto virtuales como reales.

#### Campos Principales

##### Información Básica
- `id`: Identificador único (Primary Key)
- `symbol`: Par de trading (ej: "BTC/USDT")
- `strategy_name`: Nombre de la estrategia que generó el trade
- `trade_type`: Tipo de operación ("BUY", "SELL")

##### Precios y Cantidades
- `entry_price`: Precio de entrada
- `exit_price`: Precio de salida (NULL si está abierto)
- `quantity`: Cantidad operada
- `entry_value`: Valor total de entrada (entry_price * quantity)
- `exit_value`: Valor total de salida (exit_price * quantity)

##### Métricas Financieras
- `pnl`: Profit/Loss realizado en valor absoluto
- `pnl_percentage`: Retorno en porcentaje

##### Estado y Control
- `status`: Estado del trade ("OPEN", "CLOSED", "CANCELLED")
- `is_paper_trade`: Indica si es trading virtual (True) o real (False)

##### Risk Management
- `stop_loss`: Nivel de stop loss
- `take_profit`: Nivel de take profit


##### Metadatos
- `timeframe`: Marco temporal ("1h", "4h", "1d")
- `confidence_score`: Puntuación de confianza de la señal
- `notes`: Notas adicionales

##### Timestamps
- `entry_time`: Momento de entrada
- `exit_time`: Momento de salida (NULL si abierto)
- `created_at`: Timestamp de creación
- `updated_at`: Timestamp de última actualización

#### Casos de Uso

```python
# Crear nuevo trade
trade = Trade(
    symbol="BTC/USDT",
    strategy_name="RSI_Basic",
    trade_type="BUY",
    entry_price=45000.0,
    quantity=0.1,
    entry_value=4500.0,
    timeframe="4h",
    is_paper_trade=True,
    stop_loss=43000.0,
    take_profit=47000.0
)

# Cerrar trade
trade.exit_price = 46500.0
trade.exit_value = 4650.0
trade.pnl = 150.0
trade.pnl_percentage = 3.33
trade.status = "CLOSED"
trade.exit_time = datetime.now()
```

### 2. Portfolio - Estado del Portfolio

```python
class Portfolio(Base):
    __tablename__ = "portfolio"
```

**Propósito**: Mantiene el estado actual del portfolio, tanto virtual como real.

#### Campos Principales

##### Asset Information
- `id`: Identificador único
- `symbol`: Símbolo del asset ("BTC", "USDT", "ETH")
- `quantity`: Cantidad actual en posesión
- `avg_price`: Precio promedio de adquisición

##### Valores Calculados
- `current_price`: Último precio conocido del mercado
- `current_value`: Valor actual (quantity * current_price)
- `unrealized_pnl`: Ganancia/pérdida no realizada
- `unrealized_pnl_percentage`: Porcentaje de ganancia/pérdida no realizada

##### Tipo de Portfolio
- `is_paper`: Indica si es portfolio virtual (True) o real (False)

##### Timestamps
- `last_updated`: Última actualización de precios
- `created_at`: Timestamp de creación

#### Casos de Uso

```python
# Actualizar portfolio después de compra
portfolio_btc = Portfolio(
    symbol="BTC",
    quantity=0.5,
    avg_price=45000.0,
    current_price=46000.0,
    current_value=23000.0,
    unrealized_pnl=500.0,
    unrealized_pnl_percentage=2.22,
    is_paper=True
)

# Portfolio de USDT (cash)
portfolio_usdt = Portfolio(
    symbol="USDT",
    quantity=5000.0,
    avg_price=1.0,
    current_price=1.0,
    current_value=5000.0,
    is_paper=True
)
```

### 3. Strategy - Estrategias y Performance

```python
class Strategy(Base):
    __tablename__ = "strategies"
```

**Propósito**: Almacena información y métricas de rendimiento de las estrategias de trading.

#### Campos Principales

##### Información de la Estrategia
- `id`: Identificador único
- `name`: Nombre único de la estrategia
- `description`: Descripción detallada
- `parameters`: Parámetros en formato JSON

##### Performance Metrics
- `total_trades`: Número total de trades ejecutados
- `winning_trades`: Número de trades ganadores
- `losing_trades`: Número de trades perdedores
- `win_rate`: Porcentaje de trades ganadores

##### Financial Metrics
- `total_pnl`: PnL total acumulado
- `total_return_percentage`: Retorno total en porcentaje
- `max_drawdown`: Máxima pérdida desde el pico
- `sharpe_ratio`: Ratio de Sharpe
- `profit_factor`: Factor de beneficio (ganancia bruta / pérdida bruta)

##### Risk Metrics
- `avg_win`: Ganancia promedio por trade ganador
- `avg_loss`: Pérdida promedio por trade perdedor
- `max_win`: Mayor ganancia en un solo trade
- `max_loss`: Mayor pérdida en un solo trade

##### Estado
- `is_active`: Indica si la estrategia está activa
- `is_paper_only`: Indica si solo opera en modo papel

##### Timestamps
- `created_at`: Timestamp de creación
- `last_trade_at`: Timestamp del último trade
- `updated_at`: Timestamp de última actualización

#### Casos de Uso

```python
# Crear nueva estrategia
strategy = Strategy(
    name="RSI_MACD_Combo",
    description="Estrategia combinando RSI y MACD",
    parameters='{"rsi_period": 14, "macd_fast": 12, "macd_slow": 26}',
    is_active=True,
    is_paper_only=True
)

# Actualizar métricas después de trades
strategy.total_trades += 1
strategy.winning_trades += 1
strategy.total_pnl += 150.0
strategy.win_rate = strategy.winning_trades / strategy.total_trades * 100
```

### 4. BacktestResult - Resultados de Backtesting

```python
class BacktestResult(Base):
    __tablename__ = "backtest_results"
```

**Propósito**: Almacena resultados detallados de backtesting para análisis histórico.

#### Campos Principales

##### Información del Backtest
- `id`: Identificador único
- `strategy_name`: Nombre de la estrategia probada
- `symbol`: Par de trading analizado
- `timeframe`: Marco temporal utilizado

##### Período del Backtest
- `start_date`: Fecha de inicio del período
- `end_date`: Fecha de fin del período
- `total_days`: Duración total en días

##### Capital y Retornos
- `initial_capital`: Capital inicial del backtest
- `final_capital`: Capital final obtenido
- `total_return`: Retorno total en valor absoluto
- `total_return_percentage`: Retorno total en porcentaje
- `annualized_return`: Retorno anualizado

##### Estadísticas de Trading
- `total_trades`: Número total de trades en el backtest
- `winning_trades`: Número de trades ganadores
- `losing_trades`: Número de trades perdedores
- `win_rate`: Tasa de éxito

##### Risk Metrics
- `max_drawdown`: Máximo drawdown en valor absoluto
- `max_drawdown_percentage`: Máximo drawdown en porcentaje
- `sharpe_ratio`: Ratio de Sharpe
- `sortino_ratio`: Ratio de Sortino
- `calmar_ratio`: Ratio de Calmar

##### Trading Metrics
- `avg_trade_duration_hours`: Duración promedio de trades
- `profit_factor`: Factor de beneficio
- `avg_win`: Ganancia promedio
- `avg_loss`: Pérdida promedio
- `largest_win`: Mayor ganancia
- `largest_loss`: Mayor pérdida

##### Metadatos
- `strategy_parameters`: Parámetros utilizados (JSON)
- `notes`: Notas adicionales
- `created_at`: Timestamp de creación

#### Casos de Uso

```python
# Guardar resultado de backtest
backtest = BacktestResult(
    strategy_name="RSI_Basic",
    symbol="BTC/USDT",
    timeframe="4h",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 12, 31),
    total_days=365,
    initial_capital=10000.0,
    final_capital=12500.0,
    total_return=2500.0,
    total_return_percentage=25.0,
    total_trades=150,
    winning_trades=90,
    losing_trades=60,
    win_rate=60.0,
    max_drawdown_percentage=-8.5,
    sharpe_ratio=1.45
)
```

### 5. TradingSignal - Señales de Trading

```python
class TradingSignal(Base):
    __tablename__ = "trading_signals"
```

**Propósito**: Registra todas las señales generadas por las estrategias, ejecutadas o no.

#### Campos Principales

##### Signal Information
- `id`: Identificador único
- `symbol`: Par de trading
- `strategy_name`: Estrategia que generó la señal
- `signal_type`: Tipo de señal ("BUY", "SELL", "HOLD")
- `timeframe`: Marco temporal

##### Signal Data
- `price`: Precio al momento de la señal
- `confidence_score`: Puntuación de confianza (0-100)
- `strength`: Fuerza de la señal ("Weak", "Moderate", "Strong", "Very Strong")
- `indicators_data`: Datos de indicadores en formato JSON

##### Action Taken
- `action_taken`: Acción tomada ("EXECUTED", "IGNORED", "NONE")
- `trade_id`: ID del trade ejecutado (si aplica)

##### Timestamps
- `generated_at`: Momento de generación
- `expires_at`: Momento de expiración (opcional)

#### Casos de Uso

```python
# Generar nueva señal
signal = TradingSignal(
    symbol="ETH/USDT",
    strategy_name="MACD_Cross",
    signal_type="BUY",
    timeframe="1h",
    price=2500.0,
    confidence_score=85.0,
    strength="Strong",
    indicators_data='{"macd": 15.2, "signal": 12.8, "rsi": 35.5}',
    action_taken="EXECUTED",
    trade_id=123
)

# Señal ignorada por filtros de riesgo
signal_ignored = TradingSignal(
    symbol="BTC/USDT",
    strategy_name="RSI_Oversold",
    signal_type="BUY",
    timeframe="4h",
    price=44000.0,
    confidence_score=65.0,
    strength="Moderate",
    action_taken="IGNORED"
)
```

## Relaciones entre Modelos

### Flujo de Datos

1. **Strategy** → **TradingSignal**: Las estrategias generan señales
2. **TradingSignal** → **Trade**: Las señales pueden ejecutarse como trades
3. **Trade** → **Portfolio**: Los trades actualizan el portfolio
4. **Strategy** → **BacktestResult**: Las estrategias se evalúan mediante backtesting

### Consultas Comunes

```python
# Obtener trades de una estrategia específica
trades = session.query(Trade).filter(
    Trade.strategy_name == "RSI_Basic",
    Trade.status == "CLOSED"
).all()

# Calcular PnL total por estrategia
total_pnl = session.query(func.sum(Trade.pnl)).filter(
    Trade.strategy_name == "MACD_Cross",
    Trade.is_paper_trade == True
).scalar()

# Obtener señales recientes no ejecutadas
recent_signals = session.query(TradingSignal).filter(
    TradingSignal.generated_at >= datetime.now() - timedelta(hours=24),
    TradingSignal.action_taken == "NONE"
).all()

# Portfolio actual
current_portfolio = session.query(Portfolio).filter(
    Portfolio.is_paper == True,
    Portfolio.quantity > 0
).all()
```

## Índices de Performance

### Índices Implementados

```sql
-- Trades
CREATE INDEX idx_trades_symbol_status ON trades(symbol, status);
CREATE INDEX idx_trades_entry_time ON trades(entry_time);
CREATE INDEX idx_trades_strategy_symbol ON trades(strategy_name, symbol);

-- Portfolio
CREATE INDEX idx_portfolio_symbol_paper ON portfolio(symbol, is_paper);

-- Trading Signals
CREATE INDEX idx_signals_symbol_time ON trading_signals(symbol, generated_at);
CREATE INDEX idx_signals_strategy_type ON trading_signals(strategy_name, signal_type);
```

### Optimizaciones de Consulta

1. **Filtros por símbolo**: Índices compuestos para consultas frecuentes
2. **Consultas temporales**: Índices en campos de timestamp
3. **Agrupaciones**: Índices en campos de agrupación común

## Validaciones y Constraints

### Validaciones a Nivel de Modelo

```python
# Ejemplo de validaciones personalizadas
class Trade(Base):
    # ... campos ...
    
    def validate(self):
        if self.exit_price and self.entry_price:
            if self.trade_type == "BUY" and self.exit_price < self.entry_price:
                self.pnl = (self.exit_price - self.entry_price) * self.quantity
            elif self.trade_type == "SELL" and self.exit_price > self.entry_price:
                self.pnl = (self.entry_price - self.exit_price) * self.quantity
```

### Constraints de Base de Datos

- **Unique Constraints**: Nombres de estrategias únicos
- **Check Constraints**: Validación de rangos de valores
- **Foreign Key Constraints**: Integridad referencial

## Mejores Prácticas

### 1. Manejo de Timestamps
- Usar UTC para todos los timestamps
- Aprovechar `func.now()` para timestamps automáticos
- Implementar `onupdate` para campos de actualización

### 2. Campos JSON
- Validar estructura JSON antes de guardar
- Usar esquemas consistentes para datos JSON
- Considerar campos separados para consultas frecuentes

### 3. Performance
- Usar índices apropiados para consultas frecuentes
- Evitar consultas N+1 con eager loading
- Implementar paginación para resultados grandes

### 4. Integridad de Datos
- Validar datos antes de insertar
- Usar transacciones para operaciones complejas
- Implementar soft deletes cuando sea apropiado

## Extensibilidad

### Agregar Nuevos Campos

```python
# Ejemplo: agregar campo de comisiones
class Trade(Base):
    # ... campos existentes ...
    commission = Column(Float, default=0.0)
    commission_currency = Column(String(10), default="USDT")
```

### Nuevos Modelos

```python
# Ejemplo: modelo para alertas
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False)
    condition = Column(String(100), nullable=False)
    target_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
```

## Migración y Versionado

Los cambios en los modelos deben acompañarse de migraciones apropiadas:

1. **Nuevos campos**: Agregar con valores por defecto
2. **Campos eliminados**: Usar migraciones para preservar datos
3. **Cambios de tipo**: Migrar datos existentes
4. **Nuevas tablas**: Crear con migración inicial

---

*Esta estructura de modelos proporciona una base sólida y extensible para el sistema de trading, balanceando flexibilidad, performance e integridad de datos.*