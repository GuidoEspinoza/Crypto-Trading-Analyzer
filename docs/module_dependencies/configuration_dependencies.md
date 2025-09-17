# 🔗 Dependencias de Configuración entre Módulos

## 📋 Resumen

Este documento mapea las dependencias de configuración entre los módulos del sistema de trading, mostrando cómo fluye la configuración desde los archivos centralizados hacia los módulos específicos.

## 🏗️ Arquitectura de Configuración

### Flujo Principal
```
global_constants.py → config.py → módulos específicos
                   ↗
archivos_*_config.py
```

### Jerarquía de Configuración

1. **Nivel 1: Constantes Globales**
   - `src/config/global_constants.py` - Constantes compartidas del sistema

2. **Nivel 2: Configuraciones Modulares**
   - `src/config/trading_bot_config.py` - Perfiles de trading
   - `src/config/database_config.py` - Configuración de base de datos
   - `src/config/api_config.py` - Configuración de APIs
   - `src/config/monitoring_config.py` - Configuración de monitoreo
   - Y otros archivos `*_config.py`

3. **Nivel 3: Consolidación**
   - `src/config/config.py` - Consolidador principal

4. **Nivel 4: Módulos de Aplicación**
   - Módulos en `src/core/`, `src/database/`, `src/tools/`, `src/utils/`

## 🔄 Mapa de Dependencias por Constante

### GLOBAL_INITIAL_BALANCE

**Definición:** `src/config/global_constants.py`

**Importadores directos:**
- `src/config/trading_bot_config.py`
- `src/config/database_config.py`
- `src/config/db_manager_cli_config.py`
- `src/config/config.py`

**Uso en módulos:**
- `src/core/paper_trader.py` - Balance inicial para simulación
- `src/database/database.py` - Configuración inicial de portfolio
- `src/tools/db_manager_cli.py` - Comandos de inicialización

### TIMEZONE, DAILY_RESET_HOUR, DAILY_RESET_MINUTE

**Definición:** `src/config/global_constants.py`

**Importadores directos:**
- `src/config/trading_bot_config.py`
- `src/config/config.py`

**Uso en módulos:**
- `src/tools/live_trading_bot.py` - Programación de reset diario
- `src/core/position_manager.py` - Gestión temporal de posiciones
- `src/utils/error_handler.py` - Timestamps en logs

### BASE_CURRENCY, USDT_BASE_PRICE

**Definición:** `src/config/global_constants.py`

**Importadores directos:**
- `src/config/database_config.py`
- `src/config/config.py`

**Uso en módulos:**
- `src/core/position_manager.py` - Conversiones de moneda
- `src/core/enhanced_risk_manager.py` - Cálculos de riesgo
- `src/database/models.py` - Definición de modelos

## 📊 Dependencias por Módulo

### src/core/

| Módulo | Configuración Importada | Fuente |
|--------|------------------------|--------|
| `paper_trader.py` | `PaperTradingConfig` | `config.py` |
| `position_manager.py` | `PositionManagerConfig` | `config.py` |
| `enhanced_risk_manager.py` | `RiskManagerConfig` | `config.py` |
| `market_validator.py` | `MarketValidatorConfig` | `config.py` |
| `position_monitor.py` | `MonitoringConfig` | `config.py` |
| `advanced_indicators.py` | `IndicatorConfig` | `config.py` |
| `enhanced_strategies.py` | `StrategyConfig` | `config.py` |
| `position_adjuster.py` | `AdjusterConfig` | `config.py` |

### src/database/

| Módulo | Configuración Importada | Fuente |
|--------|------------------------|--------|
| `database.py` | `DatabaseConfig` | `config.py` |
| `models.py` | `DatabaseConfig` | `config.py` |
| `migrations.py` | `DatabaseConfig` | `config.py` |
| `db_manager_cli.py` | `DatabaseCLIConfig` | `config.py` |

### src/tools/

| Módulo | Configuración Importada | Fuente |
|--------|------------------------|--------|
| `live_trading_bot.py` | `TradingBotConfig` | `config.py` |
| `trading_monitor.py` | `TradingMonitorConfig` | `config.py` |

### src/utils/

| Módulo | Configuración Importada | Fuente |
|--------|------------------------|--------|
| `error_handler.py` | `ErrorHandlerConfig` | `config.py` |
| `advanced_cache.py` | `CacheConfig` | `config.py` |

## 🔧 Configuraciones Específicas

### Trading Bot Profiles

**Definición:** `src/config/trading_bot_config.py`

**Perfiles disponibles:**
- `RAPIDO` - Trading de alta frecuencia
- `AGRESIVO` - Trading agresivo (recomendado)
- `OPTIMO` - Trading balanceado
- `CONSERVADOR` - Trading conservador

**Módulos dependientes:**
- `src/tools/live_trading_bot.py`
- `src/core/paper_trader.py`
- `src/core/position_manager.py`

### Database Profiles

**Definición:** `src/config/database_config.py`

**Perfiles disponibles:**
- `default` - Configuración estándar
- `development` - Desarrollo con debug
- `production` - Producción optimizada
- `test` - Testing en memoria

**Módulos dependientes:**
- `src/database/database.py`
- `src/tools/db_manager_cli.py`
- `tests/` - Módulos de testing

## 🚨 Puntos Críticos de Dependencia

### 1. GLOBAL_INITIAL_BALANCE
- **Criticidad:** Alta
- **Impacto:** Afecta simulación, base de datos y CLI
- **Recomendación:** Cambios requieren reinicio completo del sistema

### 2. TIMEZONE y configuración temporal
- **Criticidad:** Media
- **Impacto:** Afecta programación de reset y timestamps
- **Recomendación:** Cambios requieren reinicio del bot de trading

### 3. Trading Profiles
- **Criticidad:** Alta
- **Impacto:** Cambia completamente el comportamiento del bot
- **Recomendación:** Solo cambiar cuando el bot esté detenido

## 📝 Notas de Implementación

### Centralización Exitosa
- ✅ Todas las constantes globales están centralizadas en `global_constants.py`
- ✅ No se encontraron parámetros hardcodeados en módulos
- ✅ Imports actualizados para usar configuración centralizada

### Validación
- ✅ `global_constants.py` incluye función `validate_global_constants()`
- ✅ `config.py` maneja fallbacks para imports fallidos
- ✅ Tests verifican la centralización de configuración

### Mejoras Implementadas
- ✅ Archivo de constantes globales creado
- ✅ Imports actualizados en todos los archivos de configuración
- ✅ Documentación de dependencias creada

## 🔄 Flujo de Actualización de Configuración

1. **Modificar constantes globales** en `global_constants.py`
2. **Validar cambios** usando `validate_global_constants()`
3. **Actualizar configuraciones específicas** en archivos `*_config.py` si es necesario
4. **Reiniciar servicios** afectados según criticidad
5. **Verificar funcionamiento** en logs y monitoreo

---

**Última actualización:** Enero 2025  
**Versión:** 1.0  
**Mantenedor:** Sistema de Trading Automatizado