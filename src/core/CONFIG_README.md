# Configuración Centralizada del Sistema de Trading

## 📋 Descripción

Este sistema utiliza un archivo de configuración centralizado (`config.py`) que contiene todos los parámetros importantes del bot de trading. Cada variable incluye:

- **Descripción clara** de qué hace el parámetro
- **Valor óptimo por defecto** entre paréntesis
- **Comentarios explicativos** para facilitar el mantenimiento

## 🎯 Beneficios

### ✅ Ventajas de la Configuración Centralizada

1. **Consistencia**: Todos los módulos usan los mismos valores
2. **Mantenimiento fácil**: Cambios en un solo lugar
3. **Documentación integrada**: Cada parámetro está documentado
4. **Valores de referencia**: Siempre sabes el valor óptimo original
5. **Testing simplificado**: Fácil cambiar configuraciones para pruebas
6. **Coherencia entre paper y live trading**: Mismos parámetros excepto capital

### 🔧 Estructura de Configuraciones

```python
# Ejemplo de parámetro documentado
# Descripción de qué hace - propósito del parámetro (valor_óptimo)
PARAMETER_NAME: type = valor_óptimo
```

## 📁 Configuraciones Disponibles

### 1. `TradingBotConfig` - Bot Principal
- Símbolos a analizar
- Intervalos de análisis
- Umbrales de confianza
- Límites de trades y posiciones
- Timeframes profesionales

### 2. `RiskManagerConfig` - Gestión de Riesgo
- Riesgo por trade y diario
- Umbrales de drawdown
- Position sizing
- Stop-loss dinámico
- Trailing stops

### 3. `PaperTraderConfig` - Simulación
- Balance inicial
- Tamaños de posición
- Exposición máxima
- Slippage y liquidez

### 4. `StrategyConfig` - Estrategias
- Parámetros RSI profesional
- Configuración multi-timeframe
- Pesos del ensemble

### 5. `DatabaseConfig` - Base de Datos
- Configuración de persistencia
- Retención de datos
- Limpieza automática

### 6. `LoggingConfig` - Logging
- Niveles de log
- Formatos y archivos
- Rotación de logs

### 7. `LiveTradingConfig` - Trading Real
- Configuraciones específicas para trading en vivo
- Timeouts y reintentos
- Comisiones

## 🚀 Cómo Usar

### Importar Configuraciones

```python
from .config import TradingBotConfig, RiskManagerConfig, PaperTraderConfig

# Usar en tu clase
class MiBot:
    def __init__(self):
        self.config = TradingBotConfig()
        self.symbols = self.config.SYMBOLS
        self.min_confidence = self.config.MIN_CONFIDENCE_THRESHOLD
```

### Función de Utilidad

```python
from .config import get_config

# Obtener configuración específica
bot_config = get_config('bot')
risk_config = get_config('risk')
paper_config = get_config('paper')
```

### Configuración de Desarrollo

```python
from .config import DEV_CONFIG

# Para testing rápido
symbols = DEV_CONFIG['symbols']  # Solo 3 símbolos
interval = DEV_CONFIG['analysis_interval']  # 5 minutos
```

## 🔄 Modificar Configuraciones

### ⚠️ Reglas Importantes

1. **Siempre lee el comentario** antes de cambiar un valor
2. **Anota el valor original** antes de modificar
3. **Usa los valores óptimos** como referencia para volver
4. **Testa los cambios** en paper trading primero

### 📝 Ejemplo de Modificación Segura

```python
# ❌ MAL - Sin documentar el cambio
MIN_CONFIDENCE_THRESHOLD: float = 65.0

# ✅ BIEN - Documentando el cambio
# Umbral mínimo de confianza para ejecutar trades en % (óptimo: 72.0)
# MODIFICADO: Reducido a 65.0 para testing - VOLVER A 72.0 después
MIN_CONFIDENCE_THRESHOLD: float = 65.0
```

## 🧪 Testing y Desarrollo

### Configuración de Testing

```python
# Para pruebas rápidas, modifica DEV_CONFIG
DEV_CONFIG = {
    'symbols': ['BTCUSDT', 'ETHUSDT'],  # Solo 2 símbolos
    'analysis_interval': 1,  # Análisis cada minuto
    'min_confidence': 50.0,  # Umbral más bajo
    'paper_balance': 100.0,  # Balance menor
}
```

### Paper vs Live Trading

```python
# Paper Trading
paper_config = PaperTraderConfig()
balance = paper_config.INITIAL_BALANCE  # 1000 USDT para testing

# Live Trading
live_config = LiveTradingConfig()
balance = live_config.INITIAL_BALANCE  # Ajustar según capital real
```

## 📊 Valores Óptimos por Defecto

### Trading Bot
- **Análisis**: 30 minutos (balance calidad/frecuencia)
- **Confianza**: 72% (selectivo pero no excesivo)
- **Trades diarios**: 8 (calidad > cantidad)
- **Posiciones**: 5 simultáneas (diversificación controlada)

### Gestión de Riesgo
- **Riesgo por trade**: 1.5% (conservador)
- **Riesgo diario**: 4% (protección)
- **Drawdown máximo**: 12% (límite estricto)
- **Position sizing**: 0.5% - 8% (rango profesional)

### Estrategias
- **RSI**: 25/75 (niveles estrictos)
- **Confluencia**: 3 indicadores (alta calidad)
- **Multi-timeframe**: Pesos 0.2/0.3/0.5 (favor a largo plazo)

## 🔍 Troubleshooting

### Problemas Comunes

1. **ImportError**: Verifica que `config.py` esté en el path correcto
2. **AttributeError**: Revisa que el nombre del parámetro sea correcto
3. **Valores inesperados**: Confirma que estés usando la configuración correcta

### Debugging

```python
# Verificar configuración cargada
config = TradingBotConfig()
print(f"Símbolos: {config.SYMBOLS}")
print(f"Confianza mínima: {config.MIN_CONFIDENCE_THRESHOLD}%")
```

## 📚 Mejores Prácticas

1. **Documenta cambios temporales** con comentarios
2. **Usa DEV_CONFIG** para desarrollo
3. **Testa en paper trading** antes de live
4. **Mantén valores óptimos** como referencia
5. **Revisa configuraciones** antes de cada sesión de trading

---

**💡 Tip**: Siempre que modifiques un valor, añade un comentario explicando por qué y cuándo volver al valor óptimo.