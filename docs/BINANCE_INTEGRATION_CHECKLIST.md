# 🔗 Checklist de Integración con Binance API

## 📋 Lista de Verificación Completa

### 🔐 1. Configuración de Cuenta Binance

#### Requisitos Previos
- [ ] Cuenta Binance verificada (KYC completo)
- [ ] Autenticación 2FA habilitada
- [ ] Fondos suficientes en cuenta Spot
- [ ] Términos y condiciones de API aceptados

#### Configuración de API Key

**🧪 PASO 1: Testnet Spot (Pruebas)**
- [ ] Crear cuenta en Binance Testnet: https://testnet.binance.vision
- [ ] Crear API Key para Testnet Spot
  - Permisos: ✅ Spot Trading únicamente
  - Fondos virtuales para pruebas
- [ ] Probar todas las funcionalidades sin riesgo

**🚀 PASO 2: Binance Spot Real (Producción)**
- [ ] Crear nueva API Key en Binance Real
  - Ir a: Account → API Management
  - Nombre: "Crypto Trading Analyzer - Spot"
  - Permisos: ✅ Spot Trading, ❌ Futures, ❌ Margin, ❌ Options
- [ ] Configurar restricciones de IP
  - Agregar IP del servidor de trading
  - Habilitar "Restrict access to trusted IPs only"
- [ ] Configurar límites de trading
  - Daily trading limit: $2,000 USD (conservador para inicio)
  - Order rate limit: 5 orders/second (suficiente para swing trading)
- [ ] Guardar API Key y Secret de forma segura

### 🛡️ 2. Configuración de Seguridad

#### Variables de Entorno
- [ ] Crear archivo `.env` con:
```bash
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
BINANCE_TESTNET=false  # true para testnet
TRADING_MODE=live  # live o paper
```

#### Medidas de Seguridad
- [ ] Nunca commitear API keys al repositorio
- [ ] Usar variables de entorno para credenciales
- [ ] Implementar rate limiting
- [ ] Configurar timeouts de conexión
- [ ] Habilitar logging de seguridad

### 💻 3. Configuración Técnica

#### Dependencias
- [ ] Instalar python-binance:
```bash
pip install python-binance
```

#### Configuración de Red
- [ ] Verificar conectividad a Binance API
- [ ] Configurar proxy si es necesario
- [ ] Establecer timeouts apropiados (30 segundos)
- [ ] Configurar retry logic para fallos de red

#### Sincronización de Tiempo
- [ ] Verificar sincronización de tiempo del servidor
- [ ] Configurar NTP si es necesario
- [ ] Timestamp accuracy < 1000ms

### 🎯 4. Configuración de Trading

#### Parámetros de Producción
```yaml
# Configuración recomendada para Binance Live
trading_config:
  initial_balance: 1000.0  # USD mínimo
  max_position_size: 0.10  # 10% máximo por posición
  max_daily_trades: 15
  commission_rate: 0.001  # 0.1% Binance Spot
  max_slippage: 0.001
  min_trade_value: 20.0  # Mínimo $20 por trade
```

#### Símbolos Soportados
- [ ] Verificar símbolos disponibles en Binance Spot
- [ ] Configurar lista de símbolos activos:
```python
BINANCE_SYMBOLS = [
    'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 
    'XRPUSDT', 'ADAUSDT', 'SOLUSDT',
    'DOTUSDT', 'LINKUSDT'
]
```

#### Filtros de Mercado
- [ ] Configurar filtros de Binance:
  - MIN_NOTIONAL: Valor mínimo de orden
  - LOT_SIZE: Tamaño mínimo de lote
  - PRICE_FILTER: Precisión de precio
  - PERCENT_PRICE: Límites de precio

### 🔄 5. Implementación del Conector

#### Estructura del Código
- [ ] Crear módulo `src/integrations/binance_spot_connector.py`
- [ ] Implementar clase `BinanceSpotConnector`
- [ ] Configurar URLs base:
  - **Testnet**: `https://testnet.binance.vision`
  - **Producción**: `https://api.binance.com`
- [ ] Métodos principales para Spot Trading:
  - `connect()`: Establecer conexión
  - `get_account_info()`: Info de cuenta Spot
  - `get_spot_balance()`: Balance de activos Spot
  - `place_spot_order()`: Órdenes BUY/SELL en Spot
  - `get_order_status()`: Estado de orden
  - `cancel_order()`: Cancelar orden
  - `get_ticker_price()`: Precio actual
  - `get_24hr_ticker()`: Estadísticas 24h para análisis

#### Ejemplo de Implementación
```python
# src/integrations/binance_spot_connector.py
import ccxt
from typing import Dict, Optional

class BinanceSpotConnector:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        # URLs específicas para Spot Trading
        base_url = 'https://testnet.binance.vision' if testnet else 'https://api.binance.com'
        
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'sandbox': testnet,  # True para testnet
            'enableRateLimit': True,
            'urls': {
                'api': {
                    'public': f'{base_url}/api/v3',
                    'private': f'{base_url}/api/v3',
                }
            }
        })
    
    async def get_spot_balance(self) -> Dict:
        """Obtener balance Spot de la cuenta"""
        balance = await self.exchange.fetch_balance()
        # Filtrar solo activos con balance > 0
        return {k: v for k, v in balance['free'].items() if v > 0}
    
    async def place_spot_order(self, symbol: str, side: str, amount: float, 
                              order_type: str = 'market', price: Optional[float] = None):
        """Colocar orden Spot (BUY/SELL)"""
        if order_type == 'limit' and price:
            return await self.exchange.create_limit_order(symbol, side, amount, price)
        else:
            return await self.exchange.create_market_order(symbol, side, amount)
    
    async def get_24hr_ticker(self, symbol: str) -> Dict:
        """Obtener estadísticas 24h para análisis"""
        return await self.exchange.fetch_ticker(symbol)
```

### 📊 6. Testing y Validación

#### Tests en Testnet
- [ ] Configurar Binance Testnet
- [ ] Probar conexión y autenticación
- [ ] Ejecutar órdenes de prueba
- [ ] Verificar manejo de errores
- [ ] Probar límites de rate

#### Tests de Integración
- [ ] Probar con el sistema completo
- [ ] Verificar sincronización de datos
- [ ] Probar manejo de desconexiones
- [ ] Validar logging y monitoreo

### 🚨 7. Monitoreo y Alertas

#### Sistema de Alertas
- [ ] Configurar alertas por email
- [ ] Configurar alertas por Telegram (opcional)
- [ ] Alertas por:
  - Pérdidas excesivas (>5% diario)
  - Errores de API
  - Desconexiones prolongadas
  - Órdenes fallidas

#### Logging
- [ ] Configurar logs detallados
- [ ] Separar logs por tipo:
  - `trading.log`: Órdenes y trades
  - `api.log`: Llamadas a API
  - `error.log`: Errores y excepciones
- [ ] Rotación automática de logs

### 🎛️ 8. Dashboard y Control

#### Panel de Control
- [ ] Dashboard en tiempo real funcionando
- [ ] Métricas visibles:
  - Balance actual
  - Posiciones abiertas
  - P&L del día
  - Órdenes recientes
- [ ] Botón de emergencia para detener trading

#### Controles de Seguridad
- [ ] Circuit breakers configurados
- [ ] Límites de drawdown automáticos
- [ ] Stop loss de emergencia
- [ ] Modo de pausa manual

### 🔧 9. Configuración Final

#### Variables de Configuración
```python
# src/config/binance_config.py
BINANCE_CONFIG = {
    'api_url': 'https://api.binance.com',
    'stream_url': 'wss://stream.binance.com:9443',
    'timeout': 30,
    'max_retries': 3,
    'rate_limit_buffer': 0.1,  # 10% buffer
    'order_types': ['MARKET', 'LIMIT'],
    'default_order_type': 'MARKET'
}
```

#### Archivo de Configuración
- [ ] Actualizar `config_manager.py` con configuración Binance
- [ ] Agregar validación de configuración
- [ ] Implementar fallbacks para errores

### ✅ 10. Lista de Verificación Final

#### Pre-Lanzamiento
- [ ] Todos los tests pasando
- [ ] Configuración validada
- [ ] Logs funcionando correctamente
- [ ] Dashboard operativo
- [ ] Alertas configuradas
- [ ] Backup de configuración realizado

#### Lanzamiento
- [ ] Iniciar con balance pequeño ($100-200)
- [ ] Monitorear primeras 24 horas
- [ ] Verificar métricas de rendimiento
- [ ] Ajustar parámetros si es necesario
- [ ] Escalar gradualmente

#### Post-Lanzamiento
- [ ] Monitoreo continuo 24/7
- [ ] Revisión diaria de métricas
- [ ] Backup diario de datos
- [ ] Optimización semanal de parámetros

## 🚀 Comandos de Despliegue

### Instalación de Dependencias
```bash
pip install python-binance python-telegram-bot
```

### Configuración de Variables
```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_SECRET_KEY="your_secret_key"
export TRADING_MODE="live"
```

### Ejecución en Producción
```bash
# Iniciar bot con configuración de producción
python3 -m src.tools.live_trading_bot --live --profile OPTIMO

# Iniciar dashboard
streamlit run src/dashboard/real_time_dashboard.py --server.port 8501
```

## 📞 Contactos de Emergencia

### Soporte Técnico
- **Binance Support**: https://www.binance.com/en/support
- **API Documentation**: https://binance-docs.github.io/apidocs/spot/en/

### Procedimiento de Emergencia
1. **Detener trading inmediatamente**
2. **Cerrar posiciones abiertas manualmente**
3. **Revisar logs de error**
4. **Contactar soporte si es necesario**
5. **Documentar incidente**

---

**⚠️ IMPORTANTE**: Este checklist debe ser completado paso a paso antes de activar trading en vivo. Nunca omitir pasos de seguridad.

**Última actualización**: 2025-09-19 12:55:00
**Estado**: 📋 Checklist preparado para implementación