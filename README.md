# 🤖 Smart Trading Bot - Sistema de Trading Automatizado Inteligente

## 🎯 ¿Qué es Smart Trading Bot?

**Smart Trading Bot** es un asistente de trading automatizado que analiza los mercados financieros las 24 horas del día y ejecuta operaciones de compra y venta de manera inteligente. Piensa en él como un trader profesional que nunca duerme, nunca se emociona y siempre sigue las reglas establecidas.

### 🚀 ¿Qué hace exactamente?

El bot **observa constantemente** los precios de un portafolio core sin Forex, compuesto por **Oro (GOLD), S&P500 (US500), UK100, CAC40 (FR40) y Hang Seng 50 (HK50)**, y **busca oportunidades de trading** basándose en patrones técnicos probados. Cuando encuentra una oportunidad con alta probabilidad de éxito, **abre una posición automáticamente** con límites de ganancia y pérdida predefinidos.

## 🧠 ¿Cómo funciona la inteligencia del bot?

### 📊 Análisis Multi-Indicador
El bot utiliza varios "ojos" para ver el mercado:

- **RSI (Índice de Fuerza Relativa)**: Detecta si un activo está "sobrevalorado" o "subvalorado"
- **MACD**: Identifica cambios en la tendencia del precio
- **Bandas de Bollinger**: Mide la volatilidad y detecta movimientos extremos
- **CCI (Índice de Canal de Commodities)**: Confirma la fuerza de las tendencias

### 🎯 Estrategias de Trading Inteligentes

**1. Seguimiento de Tendencias**
- Identifica cuando un activo está en una tendencia alcista o bajista fuerte
- Se "sube al tren" de la tendencia para capturar ganancias

**2. Reversión a la Media**
- Detecta cuando un precio se ha alejado demasiado de su valor "normal"
- Apuesta a que el precio regresará a su nivel equilibrado

**3. Ruptura de Niveles**
- Identifica cuando el precio rompe niveles importantes de resistencia o soporte
- Aprovecha el impulso que genera estas rupturas

### ⚡ Proceso de Decisión Inteligente

1. **Análisis Continuo**: Cada 12 minutos, el bot examina todos los activos
2. **Confluencia de Señales**: Solo actúa cuando múltiples indicadores coinciden
3. **Filtro de Confianza**: Solo ejecuta operaciones con 80%+ de probabilidad de éxito
4. **Gestión Automática**: Establece automáticamente límites de ganancia y pérdida

## ⏰ Horarios y Programación

- Zona horaria base: `UTC` (el bot convierte internamente al horario local de Chile para eventos programados).
- Intervalo de análisis:
  - Perfil `INTRADAY` (por defecto): cada `12` minutos.
  - Perfil `SCALPING`: cada `1` minuto.
- Ventana principal de trading (UTC): `11:00` → `02:30`.
- Ventana extendida (UTC): `09:00` → `02:59`.
- Ventana nocturna (sesión asiática, UTC): `01:00` → `11:00`.
- Sesiones de alta volatilidad (UTC):
  - `asian_open`: `22:00` → `02:00`
  - `london_open`: `08:00` → `12:00`
  - `ny_open`: `14:30` → `18:30`
  - `overlap_london_ny`: `14:30` → `17:00`
- Reinicio diario: `00:00 UTC` (el bot agenda y registra el equivalente en `America/Santiago`).
- Cierre preventivo: toma ganancias 15 minutos antes del reinicio diario si aplica.
- Fines de semana:
  - Habilitado para `CRYPTO` 24/7.
  - Parámetros específicos por perfil (Scalping/Intraday) con límites y umbrales ajustados.
- Límites temporales del sistema:
  - Máximo de horas consecutivas: `8`.
  - Descanso obligatorio cada `4` horas: `15` minutos.
  - Máximo diario: `12` horas; máximo semanal: `60` horas.
  - Cooldown tras pérdida: `15` minutos.
  - Parada de emergencia: `02:00 UTC`.

### 🕒 Horarios por tipo de mercado (resumen)
- `CRYPTO`: abierto `24/7` (UTC).
- `INDICES` (NY): `09:30` → `16:00` `America/New_York`, lunes a viernes.
- `COMMODITIES` (NY): `09:00` → `17:00` `America/New_York`, lunes a viernes.

### ⚙️ Cómo cambiar los horarios o intervalos
- Cambiar perfil activo en `src/config/profiles_config.py` usando `TRADING_PROFILE` (`INTRADAY` o `SCALPING`).
- Actualizar el intervalo de análisis en tiempo real vía API:

```bash
curl -X PUT http://localhost:8000/bot/config \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_interval_minutes": 6,
    "max_daily_trades": 20,
    "enable_trading": true
  }'
```

- Ver configuración actual, incluyendo horario del próximo análisis:

```bash
curl http://localhost:8000/bot/config | python3 -m json.tool
```

### 📝 Notas sobre zona horaria
- Todos los horarios en esta sección están expresados en `UTC`.
- El reinicio diario se agenda internamente también en hora local `America/Santiago` para el `scheduler` y se muestra en los logs.
- Si tu servidor está en otra zona horaria, considera convertir los horarios UTC para tu monitoreo externo; el bot mantiene coherencia interna usando `UTC`.

## 🛡️ Gestión de Riesgo Inteligente

### 🎯 Filosofía: "Proteger el Capital es lo Primero"

- **Tamaño Controlado**: Nunca arriesga más del 8-10% del capital en una sola operación
- **Stop Loss Automático**: Cada operación tiene un límite máximo de pérdida
- **Take Profit Inteligente**: Cierra automáticamente cuando alcanza el objetivo de ganancia
- **Diversificación**: Opera en diferentes tipos de activos para reducir riesgo

### 🚫 Lo que el Bot NO hace

- **No persigue pérdidas**: Si una operación va mal, acepta la pérdida y sigue adelante
- **No se emociona**: Nunca toma decisiones basadas en miedo o codicia
- **No interfiere**: Una vez abierta una posición, deja que se desarrolle naturalmente
- **No opera sin confirmación**: Requiere múltiples señales antes de actuar

## 💎 Activos Seleccionados (Configuración Base)

### Portafolio Core (5 activos)

**🥇 Metales Preciosos**
- **GOLD**: Refugio de valor tradicional, alta liquidez, estabilidad en crisis

**📊 Índices**
- **US500**: S&P 500, representa el mercado estadounidense
- **UK100**: FTSE 100, exposición a mercado británico
- **FR40**: CAC 40, principales empresas francesas
- **HK50**: Hang Seng 50, mercado asiático de Hong Kong

<!-- Se elimina la subsección de commodities agrícolas e industriales del portafolio base -->

### 🎯 Ventajas de esta Selección Base
- **Diversificación inteligente**: Cuatro clases de activos con comportamientos diferentes
- **Liquidez garantizada**: Todos operan con alto volumen y spreads bajos
- **Volatilidad optimizada**: Suficiente movimiento para generar oportunidades
- **Correlación balanceada**: Cuando unos bajan, otros pueden subir
- **Cobertura temporal**: Diferentes horarios de mayor actividad

### ⚙️ Configuración Flexible
> **Nota importante**: Esta es la configuración base del bot. Puedes modificar los activos desde el endpoint de configuración sin necesidad de reiniciar el sistema. El bot está diseñado para adaptarse a cualquier combinación de activos que prefieras.
> Por defecto, **Forex está deshabilitado** y el portafolio core **no incluye Crypto**; puedes habilitar Crypto de forma opcional si deseas operar 24/7.

## 📈 ¿Qué puedes esperar?

### 🎯 Objetivos Realistas
- **Operaciones selectivas**: 3-12 trades por día en promedio (con límites adaptativos)
- **Alta precisión**: 75-85% de operaciones exitosas
- **Gestión conservadora**: Máximo 35-40% del capital en riesgo simultáneo
- **Crecimiento sostenible**: Enfoque en preservar capital y crecer consistentemente

### 🧠 Sistema de Límites Adaptativos Inteligente

**Innovación Clave**: El bot ajusta automáticamente el número máximo de trades diarios basándose en la calidad de las señales:

- **Límite Base**: 12 trades diarios máximo (configurable por perfil)
- **Límites Adaptativos**: Cuando las señales tienen muy alta confianza (≥90%), el bot puede ejecutar trades adicionales de "bonificación"
- **Protección Inteligente**: Nunca excede los límites de seguridad, incluso con señales de alta confianza
- **Optimización Automática**: Se adapta a las condiciones del mercado sin intervención manual

### ⚠️ Expectativas Importantes
- **No es una máquina de dinero**: Los mercados siempre tienen riesgo
- **Requiere paciencia**: Los mejores resultados se ven a mediano plazo
- **Necesita supervisión**: Aunque es automático, requiere monitoreo periódico
- **Comenzar conservador**: Siempre empezar con capital que puedas permitirte perder

## 🚀 Instalación y Configuración

### 📋 Requisitos Previos
- **Computadora**: Windows, Mac o Linux
- **Conexión a Internet**: Estable y continua
- **Cuenta en Capital.com**: Broker regulado para ejecutar las operaciones
- **Python 3.8 o superior**: Lenguaje de programación (se instala fácilmente)

### ⚙️ Proceso de Instalación

**1. Instalar Python**
```bash
# En Mac (usando Homebrew)
brew install python3

# En Windows: Descargar desde python.org

# En Linux (Ubuntu/Debian)
sudo apt update && sudo apt install python3 python3-pip
```

**2. Clonar el Proyecto**
```bash
# Descargar el código del bot
git clone https://github.com/tu-usuario/smart-trading-bot.git
cd smart-trading-bot
```

**3. Instalar Dependencias**
```bash
# Instalar las librerías necesarias
pip3 install -r requirements.txt
```

**4. Configurar Variables de Entorno**
```bash
# Copiar el archivo de configuración
cp .env.example .env

# Editar .env con tus credenciales de Capital.com
# Usar cualquier editor de texto (nano, vim, VSCode, etc.)
nano .env
```

**5. Configurar .env con tus Datos**
```env
# 🔐 Variables de Entorno - Universal Trading Analyzer
# Copia este archivo como .env y completa los valores

# === CAPITAL API ===
CAPITAL_LIVE_URL=https://api-capital.backend-capital.com/api/v1
CAPITAL_DEMO_URL=https://demo-api-capital.backend-capital.com/api/v1

IS_DEMO=True                     # Comenzar en modo demo
ENABLE_REAL_TRADING=True         # Habilitar trading real (pero en demo)

identifier=TU_EMAIL_AQUÍ         # Tu email de Capital.com
password=TU_CONTRASEÑA_AQUÍ      # Tu contraseña de Capital.com

X-CAP-API-KEY=TU_API_KEY_AQUÍ    # API Key de Capital.com
X-SECURITY-TOKEN=null            # Se genera automáticamente
CST=null                         # Se genera automáticamente
```

**6. Ejecutar el Bot**
```bash
# Iniciar el bot en modo seguro (paper trading)
python3 main.py
```

**7. Verificar que Funciona**
```bash
# En otra terminal, verificar el estado
curl http://localhost:8000/bot/status

# Iniciar trading (en modo paper)
curl -X POST http://localhost:8000/bot/start
```

### 🎮 Comandos Útiles

**Ver estado del bot:**
```bash
curl http://localhost:8000/bot/status
```

**Ver posiciones activas:**
```bash
curl http://localhost:8000/bot/positions
```

**Ver reporte de rendimiento:**
```bash
curl http://localhost:8000/bot/report
```

**Detener el bot:**
```bash
curl -X POST http://localhost:8000/bot/stop
```

## 🔒 Configuración de Seguridad

### 🛡️ Configuraciones Críticas de Seguridad

**Siempre comenzar en modo DEMO:**
```env
IS_DEMO=True                     # Mantener en True para modo demo
ENABLE_REAL_TRADING=True         # True para habilitar trading (pero en demo)
```

**Límites de protección:**
```env
MAX_DAILY_TRADES=12             # Máximo 12 operaciones por día (límite base)
MAX_RISK_PER_TRADE=1.0         # Máximo 1% de riesgo por operación
MIN_CONFIDENCE=80.0            # Solo operaciones con 80%+ confianza

# Configuración de Límites Adaptativos
ADAPTIVE_TRADES_ENABLED=True    # Habilitar trades adaptativos
BONUS_CONFIDENCE_THRESHOLD=90.0 # Umbral para trades de bonificación (90%+)
MAX_BONUS_TRADES=3             # Máximo trades adicionales por día
```

### ⚠️ Antes de Usar Dinero Real

1. **Probar en modo demo** al menos 1-2 semanas
2. **Verificar que entiendes** cómo funciona el bot
3. **Revisar todas las operaciones** que hace en demo
4. **Comenzar con capital pequeño** cuando pases a real
5. **Nunca usar dinero** que no puedas permitirte perder

## 📊 Monitoreo y Control

### 🖥️ Dashboard Web
Una vez que el bot esté ejecutándose, puedes acceder a:
```
http://localhost:8000/
```

Aquí encontrarás:
- **Estado actual** del bot
- **Posiciones abiertas** y su rendimiento
- **Historial de operaciones**
- **Métricas de rendimiento**
- **Configuración actual**

### 📱 Monitoreo Recomendado
- **Revisar diariamente** el rendimiento en Capital.com
- **Verificar semanalmente** que el bot esté funcionando
- **Ajustar configuraciones** según resultados
- **Mantener logs** para análisis posterior

## 🎯 Filosofía de Uso

### 🧘 "Set and Forget" (Configurar y Olvidar)
El bot está diseñado para funcionar de manera autónoma:
- **Configúralo una vez** correctamente
- **Déjalo trabajar** sin interferir
- **Monitorea periódicamente** pero no microgestiones
- **Confía en el proceso** a mediano plazo

### 📈 Expectativas Realistas
- **No es trading de alta frecuencia**: Busca calidad sobre cantidad
- **No garantiza ganancias**: Los mercados siempre tienen riesgo
- **Requiere paciencia**: Los mejores resultados toman tiempo
- **Es una herramienta**: Complementa, no reemplaza, tu estrategia de inversión

## ⚖️ Aviso Legal y Responsabilidades

### 🚨 Importante: Lee Antes de Usar

**Este software es para fines educativos y de investigación.** El trading automatizado conlleva riesgos significativos de pérdida de capital.

### 📋 Responsabilidades del Usuario
- **Entender los riesgos** del trading automatizado
- **Comenzar siempre en modo demo** para aprender
- **Nunca invertir más** de lo que puedes permitirte perder
- **Monitorear regularmente** el rendimiento del bot
- **Mantener actualizadas** las credenciales y configuraciones

### 🛡️ Limitaciones y Descargos
- **El rendimiento pasado** no garantiza resultados futuros
- **Los mercados pueden cambiar** y afectar la efectividad
- **Requiere supervisión humana** periódica
- **No es asesoramiento financiero** profesional

## 🆘 Soporte y Ayuda

### 📞 ¿Necesitas Ayuda?
- **Documentación**: Revisa este README completo
- **Issues en GitHub**: Para reportar problemas
- **Capital.com Support**: Para problemas con el broker

### 🤝 Comunidad
- **Issues**: Para reportes de bugs y sugerencias
- **Pull Requests**: Para contribuir mejoras

---

## 🚀 ¡Comienza Tu Viaje de Trading Automatizado!

```bash
# Instalación rápida (5 minutos)
git clone https://github.com/tu-usuario/smart-trading-bot.git
cd smart-trading-bot
pip3 install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
python3 main.py
```

### 🎯 Desarrollado para Traders Inteligentes que Valoran la Automatización

**¡Tu asistente de trading está listo para trabajar 24/7!**

---

**Versión**: 2.0.0 | **Estado**: Producción | **Última actualización**: Octubre 2024