# Position Adjuster - Documentación Técnica

## 📋 Descripción General

El `PositionAdjuster` es un componente crítico del sistema de trading que se encarga de monitorear y ajustar automáticamente las posiciones abiertas para optimizar ganancias y minimizar pérdidas. Implementa estrategias avanzadas de gestión de riesgo como trailing stops, protección de ganancias y ajustes dinámicos de Take Profit (TP) y Stop Loss (SL).

## 🏗️ Arquitectura

### Clases Principales

#### `AdjustmentReason` (Enum)
Define las razones por las cuales se puede ajustar una posición:
- `PROFIT_SCALING`: Escalado de ganancias
- `TRAILING_STOP`: Trailing stop activado
- `PROFIT_PROTECTION`: Protección de ganancias
- `RISK_MANAGEMENT`: Gestión de riesgo por pérdidas

#### `AdjustmentResult` (Dataclass)
Contiene el resultado de un ajuste de posición:
```python
@dataclass
class AdjustmentResult:
    symbol: str
    reason: AdjustmentReason
    success: bool
    old_tp: float
    new_tp: float
    old_sl: float
    new_sl: float
    timestamp: datetime
    message: str
```

#### `PositionInfo` (Dataclass)
Información de una posición:
```python
@dataclass
class PositionInfo:
    symbol: str
    side: str
    size: float
    entry_price: float
    current_tp: float
    current_sl: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
```

#### `PositionAdjuster` (Clase Principal)
Clase principal que gestiona el monitoreo y ajuste de posiciones.

## 🔧 Configuración

El sistema utiliza configuraciones específicas por perfil de trading (RAPIDO, AGRESIVO, OPTIMO):

### Parámetros de Configuración

| Parámetro | Descripción | RAPIDO | AGRESIVO | OPTIMO |
|-----------|-------------|---------|----------|--------|
| `position_monitoring_interval` | Intervalo de monitoreo (segundos) | 30 | 60 | 120 |
| `profit_scaling_threshold` | Umbral para escalado de ganancias (%) | 2.0 | 2.5 | 3.0 |
| `trailing_stop_activation` | Activación de trailing stop (%) | 5.0 | 6.0 | 8.0 |
| `trailing_stop_sl_pct` | SL dinámico para trailing stop (%) | 2.0 | 2.2 | 1.5 |
| `trailing_stop_tp_pct` | TP dinámico para trailing stop (%) | 5.0 | 5.5 | 4.0 |
| `profit_protection_sl_pct` | SL para protección de ganancias (%) | 1.0 | 1.2 | 0.8 |
| `profit_protection_tp_pct` | TP para protección de ganancias (%) | 3.0 | 3.5 | 2.5 |
| `risk_management_threshold` | Umbral para gestión de riesgo (%) | -1.0 | -1.2 | -0.8 |
| `risk_management_sl_pct` | SL conservador para pérdidas (%) | 1.5 | 1.8 | 1.2 |
| `risk_management_tp_pct` | TP conservador para pérdidas (%) | 2.0 | 2.5 | 1.8 |
| `price_simulation_variation` | Variación de precio para simulación (%) | 2.0 | 1.5 | 1.0 |
| `simulation_fallback_price` | Precio base para simulación | 50000.0 | 50000.0 | 50000.0 |
| `stats_recent_adjustments_count` | Ajustes recientes en estadísticas | 15 | 12 | 8 |

## 🚀 Uso

### Inicialización

```python
from src.core.position_adjuster import PositionAdjuster
from src.config.config import TradingProfiles

# Obtener perfil de configuración
profile = TradingProfiles.get_profile('RAPIDO')

# Crear instancia del position adjuster
adjuster = PositionAdjuster(profile=profile, db_manager=db_manager)

# Configurar callback para notificaciones
def adjustment_callback(result):
    print(f"Ajuste realizado: {result}")

adjuster.set_adjustment_callback(adjustment_callback)
```

### Monitoreo de Posiciones

```python
# Iniciar monitoreo
await adjuster.start_monitoring()

# Pausar monitoreo temporalmente
adjuster.pause_monitoring()

# Reanudar monitoreo
adjuster.resume_monitoring()

# Detener monitoreo
await adjuster.stop_monitoring()
```

### Configuración Dinámica

```python
# Actualizar intervalo de monitoreo
adjuster.update_monitoring_interval(45)  # 45 segundos

# Actualizar máximo de ajustes por posición
adjuster.update_max_adjustments(8)

# Obtener configuración actual
config = adjuster.get_current_config()
print(config)
```

### Estadísticas

```python
# Obtener estadísticas de ajustes
stats = adjuster.get_adjustment_stats()
print(f"Tasa de éxito: {stats['success_rate']:.2f}%")
print(f"Total de ajustes: {stats['total_adjustments']}")

# Resetear contadores
adjuster.reset_adjustment_counts()
```

## 🔍 Estrategias de Ajuste

### 1. Escalado de Ganancias (Profit Scaling)
- **Activación**: Cuando el PnL supera el `profit_scaling_threshold`
- **Acción**: Incrementa el TP para capturar más ganancias
- **Objetivo**: Maximizar beneficios en tendencias favorables

### 2. Trailing Stop
- **Activación**: Cuando el PnL supera el `trailing_stop_activation`
- **Acción**: Ajusta dinámicamente SL y TP siguiendo el precio
- **Objetivo**: Proteger ganancias mientras permite crecimiento

### 3. Protección de Ganancias (Profit Protection)
- **Activación**: En posiciones con ganancias moderadas
- **Acción**: Ajusta SL y TP de forma conservadora
- **Objetivo**: Asegurar ganancias existentes

### 4. Gestión de Riesgo (Risk Management)
- **Activación**: Cuando el PnL cae por debajo del `risk_management_threshold`
- **Acción**: Aplica ajustes conservadores para limitar pérdidas
- **Objetivo**: Minimizar pérdidas en posiciones adversas

## 📊 Monitoreo y Logging

El sistema incluye logging detallado y métricas de rendimiento:

```python
# Logs automáticos
2024-01-15 10:30:15 - INFO - 🚀 Monitoreo de posiciones iniciado
2024-01-15 10:30:45 - INFO - 📈 Ajuste aplicado: BTCUSDT - Profit Scaling
2024-01-15 10:31:15 - INFO - ⏸️ Monitoreo pausado temporalmente
```

### Métricas Disponibles
- Tasa de éxito de ajustes
- Número total de ajustes por símbolo
- Estadísticas por tipo de ajuste
- Historial de ajustes recientes
- Configuración actual del sistema

## ⚠️ Consideraciones Importantes

### Limitaciones
1. **Máximo de ajustes**: Cada posición tiene un límite de ajustes para evitar over-trading
2. **Intervalo mínimo**: El monitoreo no puede ser menor a 5 segundos
3. **Dependencias**: Requiere conexión activa a la base de datos y API de trading

### Mejores Prácticas
1. **Configuración por perfil**: Usar configuraciones apropiadas según el estilo de trading
2. **Monitoreo de logs**: Revisar regularmente los logs para detectar problemas
3. **Pruebas en demo**: Probar configuraciones en modo demo antes de trading real
4. **Backup de configuración**: Mantener respaldos de configuraciones exitosas

### Manejo de Errores
- Reintentos automáticos en caso de errores de red
- Logging detallado de errores para debugging
- Continuidad del monitoreo ante errores puntuales
- Notificaciones de errores críticos via callback

## 🔄 Flujo de Trabajo

1. **Inicialización**: Cargar configuración y establecer conexiones
2. **Monitoreo**: Bucle continuo de evaluación de posiciones
3. **Evaluación**: Análisis de cada posición según estrategias
4. **Ajuste**: Aplicación de cambios en TP/SL si es necesario
5. **Logging**: Registro de acciones y resultados
6. **Estadísticas**: Actualización de métricas de rendimiento

## 🛠️ Troubleshooting

### Problemas Comunes

**Monitoreo no inicia**
- Verificar conexión a base de datos
- Comprobar configuración del perfil
- Revisar logs de inicialización

**Ajustes no se aplican**
- Verificar límite de ajustes por posición
- Comprobar estado de pausa
- Revisar configuración de umbrales

**Errores de conexión**
- Verificar conectividad de red
- Comprobar credenciales de API
- Revisar timeouts de configuración

### Debugging

```python
# Habilitar logging detallado
import logging
logging.getLogger('position_adjuster').setLevel(logging.DEBUG)

# Verificar estado del sistema
config = adjuster.get_current_config()
stats = adjuster.get_adjustment_stats()
print(f"Estado: {config}")
print(f"Estadísticas: {stats}")
```

## 📈 Optimización de Rendimiento

### Recomendaciones
1. **Intervalo de monitoreo**: Balancear entre responsividad y carga del sistema
2. **Límite de ajustes**: Configurar según volatilidad del mercado
3. **Umbrales**: Ajustar según condiciones de mercado y tolerancia al riesgo
4. **Recursos**: Monitorear uso de CPU y memoria durante operación

### Métricas de Rendimiento
- Tiempo promedio de evaluación por posición
- Latencia de aplicación de ajustes
- Uso de recursos del sistema
- Tasa de éxito de operaciones

Esta documentación proporciona una guía completa para el uso y mantenimiento del sistema PositionAdjuster, asegurando una implementación exitosa y un rendimiento óptimo en entornos de trading automatizado.