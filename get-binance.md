# 📊 Correlación de Datos: Dashboard ↔ Binance Connector

Este documento mapea la correlación entre los datos mostrados en el dashboard y los datos disponibles del conector de Binance, distinguiendo entre datos directos y cálculos necesarios.

## 🔗 DATOS DIRECTOS (Correlación directa)

| Campo Dashboard | Fuente Binance | Comentario |
|---|---|---|
| **USDT Disponibles** | `balances.usdt_available` | Balance libre en USDT |
| **Valor Portfolio (USDT)** | `balance.total_balance_usdt` | Valor total del portfolio |
| **Comisiones Totales** | `account_info.maker_commission` / `taker_commission` | Tasas de comisión actuales |

## 🧮 CÁLCULOS NECESARIOS (Requieren implementación)

| Campo Dashboard | Cálculo a Realizar | Datos Base Necesarios |
|---|---|---|
| **Retorno Total** | `((valor_actual - balance_inicial) / balance_inicial) * 100` | `total_balance_usdt` + balance inicial guardado |
| **PnL No Realizado** | Suma de PnL de posiciones abiertas | Posiciones activas + precios actuales |
| **PnL Realizado** | Suma de PnL de trades cerrados | Historial de trades completados |
| **Volatilidad** | Desviación estándar de retornos históricos | Historial de valores del portfolio |
| **Drawdown Actual** | `((valor_actual - pico_máximo) / pico_máximo) * 100` | Historial de equity + pico máximo |
| **Max Drawdown** | Peor drawdown histórico registrado | Historial completo de equity |
| **Trades Totales** | Conteo de trades ejecutados | Base de datos de trades |
| **Trades Hoy** | Conteo de trades del día actual | Trades filtrados por fecha |
| **Tasa de Ganancia (Win Rate)** | `(trades_ganadores / total_trades) * 100` | Trades cerrados con PnL > 0 |
| **Sharpe Ratio** | `(retorno - tasa_libre_riesgo) / volatilidad` | Retorno total + volatilidad calculada |

## 📋 DATOS ADICIONALES DISPONIBLES EN BINANCE

| Dato Binance | Uso Potencial en Dashboard |
|---|---|
| `account_info.can_trade` | Indicador de estado de trading |
| `account_info.can_withdraw` | Indicador de capacidad de retiro |
| `account_info.can_deposit` | Indicador de capacidad de depósito |
| `account_info.account_type` | Tipo de cuenta (SPOT, etc.) |
| `balances` (todos los activos) | Distribución del portfolio por activos |

## 🔄 DATOS QUE REQUIEREN INTEGRACIÓN EXTERNA

| Campo Dashboard | Fuente Necesaria | Comentario |
|---|---|---|
| **Precios Actuales** | API de precios de Binance | Para calcular PnL no realizado |
| **Historial de Equity** | Base de datos local | Para cálculos de volatilidad y drawdown |
| **Historial de Trades** | Base de datos local | Para métricas de performance |

## 💡 RESUMEN DE IMPLEMENTACIÓN

### ✅ Datos Listos para Usar
- **USDT Disponibles**: `balances.usdt_available`
- **Valor Portfolio (USDT)**: `balance.total_balance_usdt`
- **Tasas de Comisión**: `account_info.maker_commission` / `taker_commission`

### 🧮 Requieren Cálculos
- **Retorno Total**: Cálculo basado en balance inicial vs actual
- **PnL No Realizado**: Suma de PnL de posiciones abiertas
- **PnL Realizado**: Suma de PnL de trades cerrados
- **Volatilidad**: Desviación estándar de retornos históricos
- **Drawdown Actual/Máximo**: Cálculos basados en historial de equity
- **Métricas de Trading**: Win Rate, Sharpe Ratio, etc.

### 📊 Requieren Datos Adicionales
- **Precios en tiempo real**: Para PnL no realizado
- **Historial de equity**: Para volatilidad y drawdown
- **Base de datos de trades**: Para métricas de performance

## 🔧 ESTRUCTURA DE DATOS DEL CONECTOR BINANCE

### AccountInfo
```python
account_info = {
    'account_type': str,           # Tipo de cuenta
    'can_trade': bool,             # Puede hacer trading
    'can_withdraw': bool,          # Puede retirar
    'can_deposit': bool,           # Puede depositar
    'maker_commission': float,     # Comisión maker
    'taker_commission': float,     # Comisión taker
    'buyer_commission': float,     # Comisión comprador
    'seller_commission': float     # Comisión vendedor
}
```

### Balances
```python
balances = {
    'usdt_available': float,       # USDT disponible
    'usdt_locked': float,          # USDT bloqueado
    'total_balance_usdt': float,   # Balance total en USDT
    'assets': [                    # Lista de todos los activos
        {
            'asset': str,          # Símbolo del activo
            'free': float,         # Cantidad libre
            'locked': float        # Cantidad bloqueada
        }
    ]
}
```

### Portfolio Summary
```python
portfolio_summary = {
    'total_balance_usdt': float,   # Valor total del portfolio
    'usdt_available': float,       # USDT disponible
    'asset_count': int,            # Número de activos con balance
    'last_updated': datetime       # Última actualización
}
```

## 📝 NOTAS DE IMPLEMENTACIÓN

1. **Datos Directos**: Pueden ser utilizados inmediatamente del conector
2. **Cálculos Simples**: Requieren operaciones matemáticas básicas
3. **Cálculos Complejos**: Necesitan historial y datos adicionales
4. **Integración**: Algunos datos requieren APIs adicionales o base de datos local

## 🎯 PRÓXIMOS PASOS

1. Implementar métodos de cálculo para métricas complejas
2. Integrar API de precios en tiempo real
3. Conectar con base de datos de trades históricos
4. Crear sistema de cache para optimizar performance
5. Implementar actualización en tiempo real del dashboard

---

**Fecha de creación**: $(date)
**Versión**: 1.0
**Estado**: Documentación inicial completa