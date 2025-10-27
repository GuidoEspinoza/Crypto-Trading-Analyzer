# 🌐 API Endpoints - Sistema de Trading Automático

## 📋 Descripción General

La API REST del sistema de trading automático proporciona una interfaz completa para gestionar, monitorear y controlar el bot de trading. Construida con FastAPI, ofrece documentación automática, validación de datos y endpoints robustos para todas las funcionalidades del sistema.

## 🏗️ Arquitectura de la API

### Información General
- **Framework**: FastAPI 0.104.1
- **Servidor**: Uvicorn con soporte ASGI
- **Documentación**: Swagger UI (`/docs`) y ReDoc (`/redoc`)
- **Validación**: Pydantic para modelos de datos
- **CORS**: Configurado para permitir requests desde cualquier origen

### URL Base
```
http://localhost:8000
```

### Documentación Interactiva
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔧 Endpoints de Utilidades

### GET `/` - Información de la API
**Descripción**: Endpoint raíz que proporciona información general de la API y lista de endpoints disponibles.

**Respuesta**:
```json
{
  "message": "🤖 Universal Trading Analyzer API v4.0 + Autonomous Trading Bot",
  "status": "active",
  "endpoints": {
    "utilities": { ... },
    "trading_bot": { ... },
    "real_time_analysis": { ... }
  },
  "timestamp": "2025-01-XX...",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

### GET `/health` - Estado de Salud
**Descripción**: Verifica el estado de salud del servidor y componentes principales.

**Respuesta**:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "components": {
    "trading_bot": "operational",
    "balance_manager": "connected",
    "capital_client": "authenticated"
  },
  "uptime": "2h 30m 15s"
}
```

## 🤖 Endpoints del Trading Bot

### GET `/bot/dashboard` - Dashboard Unificado
**Descripción**: Dashboard principal con información completa del bot.

**Parámetros**:
- `detailed` (query, opcional): `boolean` - Información detallada

**Respuesta**:
```json
{
  "status": "success",
  "bot_status": {
    "is_running": true,
    "uptime": "2h 30m",
    "current_balance": 10000.0,
    "total_pnl": 150.75,
    "active_positions": 3,
    "daily_trades": 5
  },
  "performance_metrics": {
    "win_rate": 65.5,
    "profit_factor": 1.45,
    "sharpe_ratio": 1.23
  },
  "timestamp": "2025-01-XX..."
}
```

### POST `/bot/start` - Iniciar Trading Bot
**Descripción**: Inicia el trading bot con la configuración actual.

**Respuesta**:
```json
{
  "status": "success",
  "message": "🚀 Trading bot started successfully!",
  "bot_status": {
    "is_running": true,
    "analysis_interval_minutes": 60,
    "strategies": ["TrendFollowingProfessional", "MeanReversionProfessional"],
    "symbols": ["GOLD", "SILVER", "BTCUSD"],
    "min_confidence_threshold": 50
  },
  "timestamp": "2025-01-XX..."
}
```

### POST `/bot/stop` - Detener Trading Bot
**Descripción**: Detiene el trading bot de forma segura.

**Respuesta**:
```json
{
  "status": "success",
  "message": "🛑 Trading bot stopped successfully",
  "bot_status": false,
  "final_stats": {
    "total_signals": 25,
    "total_trades": 8,
    "successful_trades": 5
  },
  "timestamp": "2025-01-XX..."
}
```

### GET `/bot/config` - Obtener Configuración
**Descripción**: Obtiene la configuración completa actual del bot.

**Respuesta**:
```json
{
  "status": "success",
  "configuration": {
    "basic_settings": {
      "analysis_interval_minutes": 60,
      "max_daily_trades": 12,
      "min_confidence_threshold": 50,
      "enable_trading": true,
      "symbols": ["GOLD", "SILVER", "BTCUSD"]
    },
    "adaptive_limits": {
      "adaptive_trades_enabled": true,
      "bonus_confidence_threshold": 90.0,
      "max_bonus_trades": 3,
      "current_adaptive_limit": 12
    },
    "position_management": {
      "max_concurrent_positions": 5,
      "max_position_size": 0.15,
      "max_total_exposure": 0.6,
      "min_trade_value": 50.0
    },
    "timeframes": {
      "primary_timeframe": "1h",
      "confirmation_timeframe": "15m",
      "trend_timeframe": "4h"
    },
    "risk_management": {
      "max_risk_per_trade": 1.0,
      "max_daily_risk": 3.0,
      "max_drawdown_threshold": 0.15,
      "correlation_threshold": 0.7
    },
    "trading_mode": {
      "enable_real_trading": false,
      "real_trading_size_multiplier": 0.1
    }
  },
  "current_stats": {
    "daily_trades": 3,
    "signals_generated": 15,
    "trades_executed": 5
  },
  "timestamp": "2025-01-XX..."
}
```

### PUT `/bot/config` - Actualizar Configuración
**Descripción**: Actualiza la configuración completa del bot.

**Modelo de Datos**: `BotConfigUpdate`

**Campos Principales**:
```json
{
  "analysis_interval_minutes": 15,
  "max_daily_trades": 12,
  "min_confidence_threshold": 65,
  "enable_trading": true,
  "symbols": ["GOLD", "SILVER", "BTCUSD", "ETHUSD"],
  "trading_mode": "paper",
  "adaptive_trades_enabled": true,
  "bonus_confidence_threshold": 90.0,
  "max_bonus_trades": 3,
  "max_concurrent_positions": 5,
  "max_position_size": 0.15,
  "max_total_exposure": 0.6,
  "min_trade_value": 50.0,
  "primary_timeframe": "1h",
  "confirmation_timeframe": "15m",
  "trend_timeframe": "4h",
  "max_risk_per_trade": 1.0,
  "max_daily_risk": 3.0,
  "max_drawdown_threshold": 0.15,
  "correlation_threshold": 0.7,
  "enable_real_trading": false,
  "real_trading_size_multiplier": 0.1
}
```

### GET `/bot/trading-mode` - Obtener Modo de Trading
**Descripción**: Obtiene el modo de trading actual (paper/live).

**Respuesta**:
```json
{
  "status": "success",
  "current_mode": "paper",
  "available_modes": ["paper", "live"],
  "live_trading_enabled": false,
  "real_trading_multiplier": 0.1,
  "timestamp": "2025-01-XX..."
}
```

### PUT `/bot/trading-mode` - Cambiar Modo de Trading
**Descripción**: Cambia el modo de trading del bot.

**Modelo de Datos**: `TradingModeUpdate`
```json
{
  "trading_mode": "paper",
  "confirm_live_trading": false
}
```

### GET `/bot/trading-capabilities` - Capacidades de Trading
**Descripción**: Obtiene las capacidades y limitaciones actuales del bot.

**Respuesta**:
```json
{
  "status": "success",
  "capabilities": {
    "paper_trading": {
      "enabled": true,
      "features": ["Full simulation", "Real market data", "Risk management"]
    },
    "live_trading": {
      "enabled": false,
      "status": "Not implemented",
      "requirements": ["Additional security", "Real money management"]
    },
    "supported_exchanges": ["Capital.com"],
    "supported_instruments": ["Forex", "Commodities", "Crypto", "Indices"]
  },
  "timestamp": "2025-01-XX..."
}
```

### POST `/bot/force-analysis` - Análisis Forzado
**Descripción**: Fuerza un ciclo de análisis inmediato.

**Respuesta**:
```json
{
  "status": "success",
  "message": "🔍 Forced analysis completed",
  "analysis_results": {
    "signals_generated": 3,
    "symbols_analyzed": 8,
    "execution_time_ms": 1250
  },
  "timestamp": "2025-01-XX..."
}
```

### POST `/bot/emergency-stop` - Parada de Emergencia
**Descripción**: Detiene inmediatamente el bot y cierra todas las posiciones.

**Respuesta**:
```json
{
  "status": "success",
  "message": "🚨 Emergency stop executed",
  "actions_taken": {
    "bot_stopped": true,
    "positions_closed": 3,
    "pending_orders_cancelled": 2
  },
  "timestamp": "2025-01-XX..."
}
```

## 👤 Endpoints de Perfiles de Trading

### GET `/bot/profile` - Obtener Perfil Actual
**Descripción**: Obtiene el perfil de trading actual y perfiles disponibles.

**Respuesta**:
```json
{
  "status": "success",
  "current_profile": "CONSERVATIVE",
  "available_profiles": [
    {
      "name": "CONSERVATIVE",
      "description": "Perfil conservador con bajo riesgo",
      "risk_level": "Low",
      "max_risk_per_trade": 1.0
    },
    {
      "name": "AGGRESSIVE",
      "description": "Perfil agresivo con mayor riesgo",
      "risk_level": "High",
      "max_risk_per_trade": 3.0
    }
  ],
  "timestamp": "2025-01-XX..."
}
```

### PUT `/bot/profile` - Actualizar Perfil
**Descripción**: Cambia el perfil de trading del bot.

**Modelo de Datos**: `ProfileUpdate`
```json
{
  "profile": "INTRADAY",
  "restart_bot": true
}
```

## 📊 Endpoints de Símbolos

### GET `/bot/symbols` - Obtener Símbolos Actuales
**Descripción**: Obtiene la lista de símbolos que está monitoreando el bot.

**Respuesta**:
```json
{
  "status": "success",
  "current_symbols": ["GOLD", "SILVER", "BTCUSD", "ETHUSD"],
  "total_symbols": 4,
  "available_symbols": ["GOLD", "SILVER", "COPPER", "BTCUSD", "ETHUSD", "LTCUSD"],
  "timestamp": "2025-01-XX..."
}
```

### PUT `/bot/symbols` - Actualizar Lista de Símbolos
**Descripción**: Actualiza la lista de símbolos a monitorear.

**Modelo de Datos**: `SymbolsUpdate`
```json
{
  "symbols": ["GOLD", "SILVER", "BTCUSD", "ETHUSD"],
  "restart_bot": true
}
```

## 📊 Endpoints de Análisis en Tiempo Real

### GET `/enhanced/strategies/list` - Lista de Estrategias
**Descripción**: Obtiene la lista de estrategias mejoradas disponibles.

**Respuesta**:
```json
{
  "enhanced_strategies": [
    {
      "name": "TrendFollowingProfessional",
      "description": "🎯 Estrategia profesional de seguimiento de tendencia con filtros institucionales",
      "features": ["Institutional filters", "Trend confirmation", "Professional risk management"]
    },
    {
      "name": "MeanReversionProfessional",
      "description": "🔄 Estrategia profesional de reversión a la media con análisis de divergencias",
      "features": ["RSI & Stochastic analysis", "Bollinger & Keltner Channels", "Divergence detection"]
    },
    {
      "name": "BreakoutProfessional",
      "description": "💥 Estrategia profesional de breakout con detección de patrones de consolidación",
      "features": ["Consolidation pattern detection", "Volume breakout analysis", "False breakout filtering"]
    }
  ],
  "timestamp": "2025-01-XX..."
}
```

### GET `/enhanced/analyze/{strategy_name}/{symbol}` - Análisis con Estrategia
**Descripción**: Ejecuta análisis con una estrategia específica en un símbolo.

**Parámetros**:
- `strategy_name` (path): Nombre de la estrategia
- `symbol` (path): Símbolo a analizar
- `timeframe` (query, opcional): Timeframe (default: "1h")

**Respuesta**:
```json
{
  "status": "success",
  "analysis": {
    "symbol": "GOLD",
    "strategy": "TrendFollowingProfessional",
    "timeframe": "1h",
    "signal": {
      "action": "BUY",
      "confidence": 75.5,
      "entry_price": 2045.50,
      "stop_loss": 2035.00,
      "take_profit": 2065.00,
      "reasoning": "Strong uptrend with institutional volume"
    },
    "market_analysis": {
      "trend": "BULLISH",
      "volatility": "MODERATE",
      "volume": "HIGH"
    }
  },
  "timestamp": "2025-01-XX..."
}
```

### GET `/enhanced/risk-analysis/{symbol}` - Análisis de Riesgo
**Descripción**: Obtiene análisis detallado de riesgo para un símbolo.

**Parámetros**:
- `symbol` (path): Símbolo a analizar

**Respuesta**:
```json
{
  "status": "success",
  "risk_analysis": {
    "symbol": "GOLD",
    "overall_risk_score": 65.5,
    "risk_level": "MODERATE",
    "position_sizing": {
      "recommended_size": 0.12,
      "max_position_size": 0.15,
      "risk_per_trade": 1.0,
      "reasoning": "Moderate volatility with good trend strength"
    },
    "dynamic_stop_loss": {
      "initial_stop": 2035.00,
      "atr_multiplier": 2.0,
      "stop_type": "ATR_BASED"
    },
    "market_risk_factors": {
      "volatility_risk": 0.45,
      "liquidity_risk": 0.25,
      "correlation_risk": 0.30
    }
  },
  "timestamp": "2025-01-XX..."
}
```

## 💰 Endpoints de Balance

### GET `/balance/current` - Balance Actual
**Descripción**: Obtiene el balance actual de la cuenta.

**Respuesta**:
```json
{
  "status": "success",
  "balance": {
    "available": 9850.75,
    "total": 10000.00,
    "deposit": 10000.00,
    "profit_loss": 149.25,
    "currency": "USD"
  },
  "last_update": "2025-01-XX...",
  "is_fresh": true,
  "timestamp": "2025-01-XX..."
}
```

## 🔧 Modelos de Datos

### BotConfigUpdate
Modelo para actualización de configuración del bot.

**Campos**:
- `analysis_interval_minutes`: Intervalo de análisis (1-1440 min)
- `max_daily_trades`: Límite de trades diarios (≥1)
- `min_confidence_threshold`: Umbral de confianza (0-100%)
- `enable_trading`: Habilitar ejecución de trades
- `symbols`: Lista de símbolos a monitorear
- `trading_mode`: Modo de trading ("paper" o "live")
- `max_concurrent_positions`: Posiciones concurrentes (≥1)
- `max_position_size`: Tamaño máximo de posición (0.01-1.0)
- `max_total_exposure`: Exposición total máxima (0.01-1.0)
- `min_trade_value`: Valor mínimo de trade (≥1.0 USD)
- `primary_timeframe`: Timeframe principal
- `confirmation_timeframe`: Timeframe de confirmación
- `trend_timeframe`: Timeframe de tendencia
- `max_risk_per_trade`: Riesgo máximo por trade (0.1-5.0%)
- `max_daily_risk`: Riesgo máximo diario (0.5-10.0%)
- `max_drawdown_threshold`: Umbral de drawdown (0.05-0.5)
- `correlation_threshold`: Umbral de correlación (0.1-1.0)
- `enable_real_trading`: Habilitar trading real
- `real_trading_size_multiplier`: Multiplicador para trading real (0.01-1.0)

### TradingModeUpdate
Modelo para cambio de modo de trading.

**Campos**:
- `trading_mode`: "paper" o "live"
- `confirm_live_trading`: Confirmación para trading real (opcional)

### ProfileUpdate
Modelo para cambio de perfil de trading.

**Campos**:
- `profile`: Nombre del perfil
- `restart_bot`: Reiniciar bot después del cambio (default: true)

### SymbolsUpdate
Modelo para actualización de símbolos.

**Campos**:
- `symbols`: Lista de símbolos
- `restart_bot`: Reiniciar bot después del cambio (default: true)

## 🔒 Seguridad y Autenticación

### Configuración Actual
- **CORS**: Habilitado para todos los orígenes (desarrollo)
- **Validación**: Pydantic para validación de datos
- **Rate Limiting**: No implementado (recomendado para producción)

### Recomendaciones para Producción
- Implementar autenticación JWT
- Configurar CORS específico
- Añadir rate limiting
- Logging de seguridad
- Validación adicional de permisos

## 📊 Códigos de Estado HTTP

### Códigos de Éxito
- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente

### Códigos de Error
- `400 Bad Request`: Datos de entrada inválidos
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación
- `500 Internal Server Error`: Error interno del servidor

## 🔄 Manejo de Errores

### Estructura de Error Estándar
```json
{
  "detail": "Descripción del error",
  "status_code": 400,
  "timestamp": "2025-01-XX...",
  "path": "/bot/config"
}
```

### Errores Comunes
- **Bot no inicializado**: Cuando se intenta operar sin inicializar el bot
- **Configuración inválida**: Parámetros fuera de rango
- **Conexión perdida**: Problemas con Capital.com API
- **Límites excedidos**: Superación de límites de trading

## 🚀 Uso de la API

### Ejemplo con cURL

#### Iniciar el Bot
```bash
curl -X POST "http://localhost:8000/bot/start" \
     -H "Content-Type: application/json"
```

#### Actualizar Configuración
```bash
curl -X PUT "http://localhost:8000/bot/config" \
     -H "Content-Type: application/json" \
     -d '{
       "analysis_interval_minutes": 30,
       "max_daily_trades": 15,
       "min_confidence_threshold": 70
     }'
```

#### Obtener Dashboard
```bash
curl -X GET "http://localhost:8000/bot/dashboard?detailed=true"
```

### Ejemplo con Python
```python
import requests

# Configurar base URL
BASE_URL = "http://localhost:8000"

# Iniciar bot
response = requests.post(f"{BASE_URL}/bot/start")
print(response.json())

# Obtener estado
response = requests.get(f"{BASE_URL}/bot/dashboard")
dashboard = response.json()
print(f"Bot running: {dashboard['bot_status']['is_running']}")

# Actualizar configuración
config = {
    "analysis_interval_minutes": 15,
    "max_daily_trades": 12,
    "min_confidence_threshold": 65,
    "adaptive_trades_enabled": True,
    "bonus_confidence_threshold": 90.0,
    "max_bonus_trades": 3
}
response = requests.put(f"{BASE_URL}/bot/config", json=config)
print(response.json())
```

## 🎯 Sistema de Límites Adaptativos

### Funcionalidad Inteligente
El sistema incluye límites adaptativos que permiten trades adicionales basados en la confianza de las señales:

**Configuración de Límites**:
- `max_daily_trades`: Límite base (12 por defecto)
- `adaptive_trades_enabled`: Habilita límites adaptativos
- `bonus_confidence_threshold`: Umbral de confianza para trades bonus (90%)
- `max_bonus_trades`: Máximo de trades adicionales permitidos (3)

**Cálculo Dinámico**:
```json
{
  "base_limit": 12,
  "current_trades": 8,
  "signal_confidence": 95.0,
  "adaptive_limit": 15,
  "bonus_available": true
}
```

**Beneficios**:
- 🎯 Aprovecha señales de alta calidad
- 🛡️ Mantiene protección contra overtrading
- 📊 Se adapta automáticamente a las condiciones del mercado
- ⚡ Optimiza oportunidades sin comprometer la gestión de riesgo

## 📈 Monitoreo y Métricas

### Endpoints de Monitoreo
- `/health`: Estado general del sistema
- `/bot/dashboard`: Métricas del bot
- `/balance/current`: Estado financiero
- `/bot/config`: Configuración actual

### Métricas Clave
- **Uptime**: Tiempo de funcionamiento
- **Total P&L**: Ganancia/pérdida total
- **Win Rate**: Porcentaje de trades exitosos
- **Daily Trades**: Trades ejecutados hoy
- **Adaptive Limit**: Límite dinámico actual
- **Active Positions**: Posiciones abiertas

## 🔧 Configuración del Servidor

### Desarrollo
```python
if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )
```

### Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📚 Dependencias

### Principales
- **FastAPI**: Framework web moderno
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validación de datos
- **python-dotenv**: Variables de entorno

### Integración
- **Trading Bot**: Módulos core del sistema
- **Capital.com API**: Cliente de trading
- **Balance Manager**: Gestión de balance
- **Risk Manager**: Gestión de riesgo

---

*Documentación de API generada para el sistema de trading automático. Última actualización: Enero 2025*