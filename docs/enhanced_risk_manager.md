# Enhanced Risk Manager - Documentación

## Descripción General

El `EnhancedRiskManager` es un componente crítico del sistema de trading que proporciona gestión avanzada de riesgo con capacidades dinámicas de evaluación, posicionamiento y protección de capital.

## Características Principales

### 🎯 Gestión de Riesgo Dinámica
- **Evaluación de riesgo en tiempo real** basada en múltiples factores de mercado
- **Position sizing inteligente** con métodos adaptativos (Kelly Criterion, volatilidad)
- **Stop loss y take profit dinámicos** que se ajustan a las condiciones del mercado
- **Trailing stops inteligentes** con lógica de protección de ganancias

### 📊 Niveles de Riesgo

```python
class RiskLevel(Enum):
    VERY_LOW = "very_low"     # Riesgo muy bajo
    LOW = "low"               # Riesgo bajo  
    MEDIUM = "medium"         # Riesgo medio
    HIGH = "high"             # Riesgo alto
    VERY_HIGH = "very_high"   # Riesgo muy alto
```

### 💰 Métodos de Position Sizing

#### 1. Fixed Risk
- Riesgo fijo basado en porcentaje del capital
- Configuración centralizada desde `global_config`

#### 2. Kelly Criterion
- Cálculo matemático óptimo del tamaño de posición
- Basado en probabilidad de éxito y ratio riesgo/recompensa
- Límites de seguridad configurables

#### 3. Volatility Adjusted
- Ajuste del tamaño según la volatilidad del mercado (ATR)
- Protección automática en mercados volátiles

## Configuración

### Parámetros Centralizados

Todos los parámetros críticos se obtienen de la configuración centralizada:

```python
# Configuración de risk management desde config.py
risk_config = global_config.get('risk_management', {})

# Ejemplos de parámetros configurables:
- max_position_size: Tamaño máximo de posición
- default_stop_loss: Stop loss por defecto
- atr_multiplier: Multiplicador ATR para stops dinámicos
- kelly_max_position: Límite máximo para Kelly Criterion
- volatility_threshold: Umbral de volatilidad
```

### Perfiles de Riesgo

El sistema soporta diferentes perfiles de trading:
- **RAPIDO**: Configuración para trading rápido
- **AGRESIVO**: Configuración agresiva con mayor riesgo
- **OPTIMO**: Configuración balanceada (recomendada)

## Uso Básico

### Inicialización

```python
from src.core.enhanced_risk_manager import EnhancedRiskManager

# Inicialización con configuración centralizada
risk_manager = EnhancedRiskManager()
```

### Evaluación de Riesgo

```python
# Evaluar riesgo de un trade
risk_assessment = risk_manager.assess_trade_risk(
    symbol="BTC/USDT",
    entry_price=50000,
    stop_loss=48000,
    take_profit=55000,
    position_size=0.1,
    confidence_score=0.8
)

print(f"Nivel de riesgo: {risk_assessment.risk_level}")
print(f"Score de riesgo: {risk_assessment.risk_score}")
```

### Cálculo de Position Size

```python
# Calcular tamaño óptimo de posición
position_size = risk_manager.calculate_position_size(
    symbol="BTC/USDT",
    entry_price=50000,
    stop_loss=48000,
    method=PositionSizing.KELLY_CRITERION,
    confidence_score=0.75
)
```

### Stop Loss Dinámico

```python
# Configurar stop loss dinámico
stop_loss = risk_manager.calculate_dynamic_stop_loss(
    symbol="BTC/USDT",
    entry_price=50000,
    position_type="long",
    confidence_score=0.8
)
```

## Algoritmos Avanzados

### 🔄 Trailing Stop Inteligente

- **Activación progresiva**: Se activa cuando la posición está en ganancia
- **Ajuste dinámico**: Se ajusta según la volatilidad del mercado
- **Protección de ganancias**: Protege un porcentaje mínimo de ganancias

### 📈 Take Profit Dinámico

- **Múltiples niveles**: Soporta take profit parcial en diferentes niveles
- **Ajuste por volatilidad**: Se adapta a las condiciones del mercado
- **Maximización de ganancias**: Optimiza la salida según momentum

### ⚖️ Gestión de Portfolio

- **Límites de exposición**: Control del riesgo total del portfolio
- **Correlación de activos**: Evita sobre-exposición en activos correlacionados
- **Diversificación automática**: Sugerencias de diversificación

## Métricas de Riesgo

### Factores Evaluados

1. **Volatilidad del mercado** (ATR)
2. **Volumen de trading**
3. **Fuerza de la tendencia**
4. **Nivel de confianza de la señal**
5. **Exposición actual del portfolio**
6. **Condiciones generales del mercado**

### Score de Riesgo

- **0.0 - 0.2**: Riesgo muy bajo
- **0.2 - 0.4**: Riesgo bajo
- **0.4 - 0.6**: Riesgo medio
- **0.6 - 0.8**: Riesgo alto
- **0.8 - 1.0**: Riesgo muy alto

## Recomendaciones del Sistema

El risk manager proporciona recomendaciones automáticas:

- **Reducir posición**: Cuando el riesgo es alto
- **Ajustar stop loss**: Para optimizar protección
- **Tomar ganancias parciales**: En niveles de resistencia
- **Evitar nuevas posiciones**: En condiciones adversas

## Integración con Otros Componentes

### Trading Bot
- Evaluación automática antes de cada trade
- Ajustes dinámicos durante la ejecución

### Position Monitor
- Monitoreo continuo de posiciones abiertas
- Alertas de riesgo en tiempo real

### Paper Trader
- Simulación de estrategias de riesgo
- Backtesting de configuraciones

## Optimizaciones Implementadas

### ✅ Configuración Centralizada
- Eliminación de valores hardcodeados
- Parámetros configurables por perfil
- Fácil mantenimiento y ajuste

### ✅ Performance
- Cache de cálculos costosos
- Optimización de consultas de mercado
- Procesamiento asíncrono cuando es posible

### ✅ Robustez
- Manejo de errores comprehensivo
- Valores por defecto seguros
- Validación de parámetros

## Logging y Monitoreo

El sistema incluye logging detallado para:
- Decisiones de riesgo
- Cálculos de position sizing
- Ajustes de stops y targets
- Alertas y recomendaciones

## Consideraciones de Seguridad

- **Límites máximos**: Protección contra posiciones excesivas
- **Validación de datos**: Verificación de precios y volúmenes
- **Circuit breakers**: Parada automática en condiciones extremas
- **Auditoría**: Registro completo de todas las decisiones

## Próximas Mejoras

- [ ] Machine Learning para predicción de riesgo
- [ ] Integración con análisis de sentimiento
- [ ] Optimización multi-objetivo
- [ ] Dashboard de riesgo en tiempo real

---

**Nota**: Esta documentación corresponde a la versión optimizada del Enhanced Risk Manager con configuración centralizada y eliminación de parámetros hardcodeados.