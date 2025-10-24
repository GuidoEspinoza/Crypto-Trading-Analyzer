# 🤖 Módulos Core - Sistema de Trading Automático

## 📋 Descripción General

Los módulos core constituyen el núcleo del sistema de trading automático, proporcionando funcionalidades esenciales para la ejecución, gestión de riesgo, monitoreo de balance y operaciones de trading tanto en modo paper como real.

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
📦 Core Modules
├── 🤖 TradingBot (trading_bot.py)          # Motor principal de trading
├── 💰 BalanceManager (balance_manager.py)  # Gestión de balance en tiempo real
├── 🛡️ EnhancedRiskManager (enhanced_risk_manager.py)  # Gestión avanzada de riesgo
├── 📊 PaperTrader (paper_trader.py)        # Simulación de trading
├── 🔍 PositionMonitor (position_monitor.py) # Monitoreo de posiciones
└── 🌐 CapitalClient (capital_client.py)    # Cliente API Capital.com
```

## 🤖 TradingBot - Motor Principal

### Características Principales

- **Ejecución Multi-Estrategia**: Soporte para múltiples estrategias profesionales
- **Trading Automático**: Ejecución automática con intervalos configurables
- **Paper Trading**: Simulación completa antes del trading real
- **Gestión de Riesgo**: Integración con sistema avanzado de riesgo
- **Monitoreo en Tiempo Real**: Seguimiento continuo de posiciones
- **Sistema de Eventos**: Comunicación asíncrona entre componentes

### Funcionalidades Clave

#### Inicialización y Configuración
```python
# Configuración desde archivo centralizado
self.config = TradingBotConfig()
self.min_confidence_threshold = self.config.get_min_confidence_threshold()
self.max_daily_trades = self.config.get_max_daily_trades()
self.max_concurrent_positions = self.config.get_max_concurrent_positions()
```

#### Estrategias Disponibles
- **TrendFollowingProfessional**: Seguimiento de tendencia institucional
- **MeanReversionProfessional**: Reversión a la media con divergencias
- **BreakoutProfessional**: Detección de breakouts con filtros

#### Sistema de Caché Inteligente
- **TTL Configurable**: Tiempo de vida basado en configuración
- **Limpieza Automática**: Eliminación de datos expirados
- **Optimización de Rendimiento**: Reducción de llamadas API

#### Análisis Multi-Timeframe
- **Timeframe Primario**: Análisis principal
- **Timeframe de Confirmación**: Validación de señales
- **Timeframe de Tendencia**: Contexto de mercado

### Flujo de Ejecución

1. **Inicialización**
   - Configuración de componentes
   - Sincronización con Capital.com
   - Inicialización de estrategias

2. **Ciclo de Análisis**
   - Obtención de datos de mercado
   - Análisis con estrategias
   - Evaluación de riesgo
   - Ejecución de trades

3. **Monitoreo Continuo**
   - Seguimiento de posiciones
   - Ajustes de stop-loss/take-profit
   - Gestión de drawdown

## 💰 BalanceManager - Gestión de Balance

### Características Principales

- **Actualización Automática**: Balance en tiempo real cada 30 segundos
- **Conexión Persistente**: Mantiene sesión activa con Capital.com
- **Renovación de Sesión**: Refresh automático cada hora
- **Sincronización**: Balance real para paper trading

### Funcionalidades

#### Gestión de Conexión
```python
async def _connect_to_capital(self):
    """Establece conexión con Capital.com"""
    self.capital_client = create_capital_client_from_env()
    account_info = self.capital_client.get_accounts()
```

#### Estado del Balance
```python
self.current_balance = {
    'available': 0.0,      # Balance disponible
    'total': 0.0,          # Balance total
    'deposit': 0.0,        # Depósitos
    'profit_loss': 0.0     # P&L actual
}
```

#### Métodos Principales
- `start()`: Inicia el servicio de gestión
- `stop()`: Detiene el servicio
- `get_current_balance()`: Obtiene balance actual
- `force_update()`: Actualización forzada
- `is_balance_fresh()`: Verifica frescura de datos

## 🛡️ EnhancedRiskManager - Gestión Avanzada de Riesgo

### Características Principales

- **Position Sizing Inteligente**: Cálculo basado en Kelly Criterion
- **Stop-Loss Dinámico**: Ajuste automático basado en ATR
- **Take-Profit Adaptativo**: Optimización de ganancias
- **Gestión de Drawdown**: Protección de capital
- **Análisis de Correlación**: Prevención de sobre-exposición

### Componentes de Riesgo

#### Niveles de Riesgo
```python
class RiskLevel(Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    EXTREME = "EXTREME"
```

#### Position Sizing
```python
@dataclass
class PositionSizing:
    recommended_size: float      # Tamaño recomendado
    max_position_size: float     # Tamaño máximo
    risk_per_trade: float        # Riesgo por trade
    position_value: float        # Valor de la posición
    leverage_used: float         # Apalancamiento usado
    risk_level: RiskLevel        # Nivel de riesgo
    reasoning: str               # Justificación
```

#### Stop-Loss Dinámico
```python
@dataclass
class DynamicStopLoss:
    initial_stop: float          # Stop inicial
    current_stop: float          # Stop actual
    trailing_stop: float         # Trailing stop
    atr_multiplier: float        # Multiplicador ATR
    stop_type: str              # Tipo de stop
    last_update: datetime        # Última actualización
```

### Algoritmos de Riesgo

#### Kelly Criterion
- Cálculo óptimo de tamaño de posición
- Basado en probabilidad de éxito
- Ajuste por volatilidad del mercado

#### ATR-Based Stop Loss
- Stop-loss basado en volatilidad
- Ajuste dinámico según condiciones
- Protección contra whipsaws

#### Correlation Analysis
- Análisis de correlación entre posiciones
- Prevención de sobre-exposición
- Diversificación automática

## 📊 PaperTrader - Simulación de Trading

### Características Principales

- **Simulación Realista**: Emula condiciones reales de mercado
- **Sincronización**: Balance inicial desde Capital.com
- **Slippage Simulation**: Simulación de deslizamiento
- **Comisiones**: Cálculo de costos reales
- **Tracking Completo**: Historial detallado de trades

### Funcionalidades

#### Ejecución de Trades
- Validación de órdenes
- Cálculo de P&L
- Gestión de posiciones
- Tracking de performance

#### Métricas de Performance
- Win Rate
- Profit Factor
- Sharpe Ratio
- Maximum Drawdown
- Average Trade Duration

## 🔍 PositionMonitor - Monitoreo de Posiciones

### Características Principales

- **Monitoreo en Tiempo Real**: Seguimiento continuo
- **Ajustes Automáticos**: Stop-loss y take-profit dinámicos
- **Alertas**: Notificaciones de eventos importantes
- **Sincronización**: Entre paper trading y real trading

### Funcionalidades

#### Monitoreo Activo
- Precios en tiempo real
- Cálculo de P&L
- Detección de niveles clave
- Gestión de riesgo continua

#### Ajustes Dinámicos
- Trailing stops
- Breakeven stops
- Take-profit escalonado
- Risk-reward optimization

## 🌐 CapitalClient - Cliente API

### Características Principales

- **Conexión Robusta**: Manejo de errores y reconexión
- **Rate Limiting**: Respeto de límites API
- **Autenticación**: Gestión segura de credenciales
- **Endpoints Completos**: Acceso a toda la funcionalidad

### Funcionalidades

#### Gestión de Datos
- Obtención de precios
- Información de cuenta
- Historial de trades
- Datos de mercado

#### Ejecución de Órdenes
- Órdenes de mercado
- Órdenes limitadas
- Stop-loss y take-profit
- Modificación de órdenes

## ⚙️ Configuración y Personalización

### Archivos de Configuración

#### main_config.py
```python
# Configuración centralizada
class TradingBotConfig:
    def get_min_confidence_threshold(self): return 0.7
    def get_max_daily_trades(self): return 10
    def get_max_concurrent_positions(self): return 5
```

#### Variables de Entorno
```bash
# Trading Configuration
ENABLE_REAL_TRADING=false
REAL_TRADING_SIZE_MULTIPLIER=0.1
IS_DEMO=true

# Risk Management
MAX_RISK_PER_TRADE=2.0
MAX_DAILY_RISK=5.0
MAX_DRAWDOWN_THRESHOLD=10.0
```

### Perfiles de Trading

#### Conservative Profile
- Riesgo bajo por trade (1%)
- Máximo 3 posiciones concurrentes
- Stop-loss estricto

#### Aggressive Profile
- Riesgo alto por trade (3%)
- Máximo 8 posiciones concurrentes
- Take-profit optimizado

## 🔄 Flujo de Integración

### Inicialización del Sistema
1. **TradingBot** se inicializa con configuración
2. **BalanceManager** establece conexión y obtiene balance
3. **EnhancedRiskManager** configura parámetros de riesgo
4. **PaperTrader** se sincroniza con balance real
5. **PositionMonitor** inicia monitoreo

### Ciclo de Trading
1. **Análisis**: TradingBot ejecuta estrategias
2. **Evaluación**: RiskManager evalúa señales
3. **Ejecución**: PaperTrader/CapitalClient ejecuta trades
4. **Monitoreo**: PositionMonitor supervisa posiciones
5. **Ajustes**: Modificaciones dinámicas según mercado

## 📈 Métricas y Monitoreo

### KPIs Principales
- **Total P&L**: Ganancia/pérdida total
- **Win Rate**: Porcentaje de trades ganadores
- **Profit Factor**: Ratio ganancia/pérdida
- **Sharpe Ratio**: Rendimiento ajustado por riesgo
- **Maximum Drawdown**: Máxima pérdida consecutiva

### Logging y Debugging
- Logs estructurados con niveles
- Tracking de performance
- Alertas de errores
- Métricas en tiempo real

## 🛠️ Desarrollo y Extensibilidad

### Añadir Nuevas Estrategias
1. Implementar interfaz `TradingStrategy`
2. Registrar en `TradingBot._initialize_strategies()`
3. Configurar parámetros en `main_config.py`

### Personalizar Risk Manager
1. Modificar parámetros en `RiskManagerConfig`
2. Implementar nuevos algoritmos de sizing
3. Añadir métricas de riesgo personalizadas

### Integrar Nuevos Brokers
1. Implementar interfaz de cliente
2. Adaptar métodos de ejecución
3. Configurar autenticación

## 🔧 Consideraciones Técnicas

### Performance
- **Caché Inteligente**: Reducción de llamadas API
- **Procesamiento Paralelo**: ThreadPoolExecutor para análisis
- **Optimización de Memoria**: Limpieza automática de caché

### Seguridad
- **Gestión Segura de Credenciales**: Variables de entorno
- **Validación de Datos**: Pydantic para validación
- **Rate Limiting**: Respeto de límites API

### Escalabilidad
- **Arquitectura Modular**: Componentes independientes
- **Sistema de Eventos**: Comunicación asíncrona
- **Configuración Centralizada**: Fácil mantenimiento

## 📚 Dependencias

### Principales
- **FastAPI**: Framework web para API
- **pandas**: Manipulación de datos financieros
- **numpy**: Cálculos numéricos
- **pandas-ta**: Indicadores técnicos
- **asyncio**: Programación asíncrona

### Específicas del Trading
- **websockets**: Comunicación en tiempo real
- **aiohttp**: Cliente HTTP asíncrono
- **python-dotenv**: Gestión de configuración

## 🚀 Próximos Desarrollos

### Funcionalidades Planificadas
- **Machine Learning**: Integración de modelos predictivos
- **Multi-Exchange**: Soporte para múltiples exchanges
- **Advanced Analytics**: Métricas avanzadas de performance
- **Mobile Alerts**: Notificaciones móviles
- **Backtesting Engine**: Motor de backtesting histórico

### Optimizaciones
- **GPU Acceleration**: Cálculos en GPU
- **Database Integration**: Persistencia de datos
- **Real-time Dashboard**: Dashboard en tiempo real
- **API Rate Optimization**: Optimización de llamadas API

---

*Documentación técnica generada para el sistema de trading automático. Última actualización: Enero 2025*