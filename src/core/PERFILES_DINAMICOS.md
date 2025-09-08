# 🎯 Sistema de Perfiles Dinámicos de Trading

## 📋 Descripción

El sistema de perfiles dinámicos permite cambiar rápidamente entre diferentes configuraciones de trading (Rápido, Agresivo, Óptimo) modificando una sola variable. Todos los parámetros del bot se ajustan automáticamente según el perfil seleccionado.

## 🚀 Uso Rápido

### Cambiar Perfil

Para cambiar el perfil de trading, simplemente modifica la variable `TRADING_PROFILE` en `config.py`:

```python
# En config.py
TRADING_PROFILE = "AGRESIVO"  # Opciones: "RAPIDO", "AGRESIVO", "OPTIMO"
```

### Perfiles Disponibles

| Perfil | Emoji | Descripción | Timeframes | Riesgo |
|--------|-------|-------------|------------|--------|
| **RAPIDO** | 🚀 | Ultra-Rápido | 1m, 5m, 15m | Alto |
| **AGRESIVO** | ⚡ | Agresivo | 15m, 30m, 1h | Medio |
| **OPTIMO** | 🛡️ | Óptimo | 1h, 4h, 1d | Bajo |

## 📊 Comparación de Perfiles

### Parámetros Principales

| Parámetro | RAPIDO 🚀 | AGRESIVO ⚡ | OPTIMO 🛡️ |
|-----------|-----------|-------------|------------|
| **Intervalo Análisis** | 5s | 15s | 30s |
| **Confianza Mínima** | 60% | 65% | 70% |
| **Trades Diarios Máx** | 20 | 12 | 8 |
| **Posiciones Máx** | 8 | 6 | 4 |
| **Riesgo por Trade** | 2.0% | 1.5% | 1.0% |
| **Riesgo Diario Máx** | 8.0% | 6.0% | 4.0% |

### Paper Trader

| Parámetro | RAPIDO 🚀 | AGRESIVO ⚡ | OPTIMO 🛡️ |
|-----------|-----------|-------------|------------|
| **Tamaño Máx Posición** | 10.0% | 8.0% | 6.0% |
| **Exposición Total Máx** | 85.0% | 75.0% | 60.0% |
| **Valor Mín Trade** | $15 | $10 | $5 |
| **Slippage Máximo** | 0.12% | 0.08% | 0.05% |
| **Liquidez Mínima** | 3M USDT | 5M USDT | 8M USDT |

### Risk Manager

| Parámetro | RAPIDO 🚀 | AGRESIVO ⚡ | OPTIMO 🛡️ |
|-----------|-----------|-------------|------------|
| **Drawdown Máximo** | 15.0% | 12.0% | 8.0% |
| **Correlación Máx** | 0.8 | 0.7 | 0.6 |
| **ATR Por Defecto** | 2.0x | 2.5x | 3.0x |
| **ATR Volátil** | 3.0x | 4.0x | 5.0x |
| **Trailing Stop** | 1.0% | 1.5% | 2.0% |

## 🔧 Implementación Técnica

### Estructura del Sistema

```python
# config.py
TRADING_PROFILE = "AGRESIVO"  # Variable principal

class TradingProfiles:
    PROFILES = {
        "RAPIDO": { ... },
        "AGRESIVO": { ... },
        "OPTIMO": { ... }
    }
    
    @classmethod
    def get_current_profile(cls):
        return cls.PROFILES[TRADING_PROFILE]
```

### Clases Dinámicas

Todas las clases de configuración obtienen sus valores dinámicamente:

```python
class TradingBotConfig:
    @classmethod
    def get_min_confidence_threshold(cls):
        return TradingProfiles.get_current_profile()["min_confidence"]

class PaperTraderConfig:
    @classmethod
    def get_max_position_size(cls):
        return TradingProfiles.get_current_profile()["max_position_size"]

class RiskManagerConfig:
    @classmethod
    def get_max_risk_per_trade(cls):
        return TradingProfiles.get_current_profile()["max_risk_per_trade"]
```

## 🎮 Ejemplo de Uso

### Archivo de Demostración

Ejecuta `profile_example.py` para ver el sistema en acción:

```bash
python profile_example.py
```

### Cambio Programático

```python
from config import TradingProfiles, TradingBotConfig
import config

# Cambiar a perfil rápido
config.TRADING_PROFILE = "RAPIDO"
print(f"Confianza mínima: {TradingBotConfig.get_min_confidence_threshold()}%")
# Output: Confianza mínima: 60.0%

# Cambiar a perfil óptimo
config.TRADING_PROFILE = "OPTIMO"
print(f"Confianza mínima: {TradingBotConfig.get_min_confidence_threshold()}%")
# Output: Confianza mínima: 70.0%
```

## 🎯 Casos de Uso

### 1. Trading Intradía (RAPIDO 🚀)
- **Cuándo usar**: Mercados con alta volatilidad y oportunidades frecuentes
- **Ventajas**: Máxima frecuencia de trades, aprovecha movimientos pequeños
- **Riesgos**: Mayor exposición al ruido del mercado, más comisiones

### 2. Trading Swing (AGRESIVO ⚡)
- **Cuándo usar**: Balance entre frecuencia y calidad de señales
- **Ventajas**: Buen equilibrio riesgo/recompensa, menos ruido
- **Riesgos**: Puede perder oportunidades muy rápidas

### 3. Trading Posicional (OPTIMO 🛡️)
- **Cuándo usar**: Preservación de capital, mercados inciertos
- **Ventajas**: Máxima calidad de señales, menor riesgo
- **Riesgos**: Menos oportunidades, puede ser lento en mercados rápidos

## ⚙️ Personalización

### Crear Perfil Personalizado

Puedes agregar tu propio perfil modificando `TradingProfiles.PROFILES`:

```python
"MI_PERFIL": {
    "name": "🎯 Mi Perfil",
    "description": "Configuración personalizada",
    "timeframes": ["5m", "15m", "1h"],
    "analysis_interval": 10,
    "min_confidence": 67.5,
    # ... más parámetros
}
```

### Modificar Perfil Existente

Puedes ajustar los valores de cualquier perfil según tus necesidades:

```python
# Hacer el perfil AGRESIVO más conservador
TradingProfiles.PROFILES["AGRESIVO"]["min_confidence"] = 70.0
TradingProfiles.PROFILES["AGRESIVO"]["max_risk_per_trade"] = 1.0
```

## 🔄 Migración desde Configuración Estática

Si tienes código que usa las configuraciones estáticas anteriores, el sistema mantiene compatibilidad:

```python
# Código anterior (sigue funcionando)
max_risk = RiskManagerConfig.MAX_RISK_PER_TRADE

# Código nuevo (recomendado)
max_risk = RiskManagerConfig.get_max_risk_per_trade()
```

## 📈 Monitoreo y Logs

El sistema registra automáticamente los cambios de perfil:

```python
# Los logs mostrarán:
# [INFO] Perfil cambiado a AGRESIVO - Confianza: 65%, Riesgo: 1.5%
# [INFO] Configuraciones actualizadas para perfil AGRESIVO
```

## 🚨 Consideraciones Importantes

1. **Cambios en Vivo**: Los cambios de perfil se aplican inmediatamente
2. **Posiciones Abiertas**: Las posiciones existentes mantienen sus parámetros originales
3. **Backtesting**: Asegúrate de usar el mismo perfil para comparaciones válidas
4. **Logs**: Todos los cambios quedan registrados para auditoría

## 🎉 Beneficios

✅ **Simplicidad**: Un solo parámetro controla todo el comportamiento
✅ **Consistencia**: Todos los módulos usan la misma configuración
✅ **Flexibilidad**: Fácil cambio entre estrategias
✅ **Mantenibilidad**: Configuración centralizada
✅ **Escalabilidad**: Fácil agregar nuevos perfiles

---

*Para más información, consulta el código en `config.py` y ejecuta `profile_example.py` para ver el sistema en acción.*