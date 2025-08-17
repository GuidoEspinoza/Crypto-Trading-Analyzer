# 🔧 Backend - Motor de Análisis Técnico

El backend de Crypto Trading Analyzer es el corazón del sistema, responsable de procesar datos de mercado en tiempo real, ejecutar análisis técnico avanzado y generar señales de trading inteligentes.

## 📋 Responsabilidades Principales

### 🔄 Obtención de Datos
- **Conexión a múltiples exchanges** (Binance, Coinbase, Kraken, etc.)
- **Recopilación de datos históricos** para backtesting
- **Streaming de datos en tiempo real** para análisis continuo
- **Normalización y limpieza** de datos de diferentes fuentes

### 📊 Análisis Técnico
- **Indicadores técnicos clásicos** (RSI, MACD, Bollinger Bands, etc.)
- **Indicadores personalizados** adaptados a criptomonedas
- **Análisis de patrones** de velas japonesas
- **Detección de soportes y resistencias**

### 🎯 Lógica de Estrategia
- **Motor de reglas** configurable para estrategias de trading
- **Generación de señales** de compra/venta
- **Gestión de riesgo** y money management
- **Backtesting** histórico de estrategias

### 🚀 API y Comunicación
- **API RESTful** para comunicación con el frontend
- **WebSockets** para datos en tiempo real
- **Sistema de notificaciones** y alertas
- **Documentación automática** con Swagger/OpenAPI

## 🛠️ Tecnologías y Bibliotecas

### Core Libraries
```bash
pandas>=2.0.0          # Manipulación y análisis de datos
numpy>=1.24.0          # Computación numérica eficiente
ta-lib>=0.4.25         # Biblioteca de análisis técnico
ccxt>=4.0.0            # Conexión unificada a exchanges
```

### Web Framework
```bash
fastapi>=0.100.0       # Framework web moderno y rápido
uvicorn>=0.23.0        # Servidor ASGI para FastAPI
websockets>=11.0       # Comunicación en tiempo real
```

### Base de Datos y Cache
```bash
sqlalchemy>=2.0.0      # ORM para manejo de base de datos
alembic>=1.11.0        # Migraciones de base de datos
redis>=4.6.0           # Cache y almacenamiento temporal
```

### Tareas Asíncronas
```bash
celery>=5.3.0          # Procesamiento de tareas en background
flower>=2.0.0          # Monitoreo de tareas Celery
```

### Utilidades
```bash
python-dotenv>=1.0.0   # Gestión de variables de entorno
pydantic>=2.0.0        # Validación de datos
loguru>=0.7.0          # Sistema de logging avanzado
```

## ⚙️ Configuración del Entorno

### 1. Requisitos del Sistema
- **Python 3.9 o superior**
- **pip** (gestor de paquetes de Python)
- **Redis** (para cache y colas de tareas)
- **PostgreSQL** (base de datos principal)

### 2. Variables de Entorno
Crea un archivo `.env` basado en `.env.example` con las siguientes variables:

```bash
# APIs de Exchanges
BINANCE_API_KEY=tu_api_key_binance
BINANCE_SECRET_KEY=tu_secret_key_binance
COINBASE_API_KEY=tu_api_key_coinbase
COINBASE_SECRET_KEY=tu_secret_key_coinbase

# Base de Datos
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/crypto_trading
REDIS_URL=redis://localhost:6379/0

# Configuración del Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=True
SECRET_KEY=tu_clave_secreta_super_segura

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 3. Instalación de Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (macOS/Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar TA-Lib (requiere compilación)
# En macOS:
brew install ta-lib
pip install TA-Lib

# En Ubuntu/Debian:
# sudo apt-get install libta-lib-dev
# pip install TA-Lib
```

## 🚀 Ejecución del Backend

### Desarrollo Local

```bash
# Asegúrate de estar en el directorio backend
cd backend

# Activar entorno virtual
source venv/bin/activate

# Ejecutar el servidor de desarrollo
python src/main.py

# O usando uvicorn directamente
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Servicios Adicionales

```bash
# Iniciar Redis (en otra terminal)
redis-server

# Iniciar worker de Celery (en otra terminal)
celery -A src.celery_app worker --loglevel=info

# Iniciar monitor de Celery Flower (opcional)
celery -A src.celery_app flower
```

## 📝 Estructura del Código

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── config.py               # Configuración y settings
│   ├── 
│   ├── api/                    # Endpoints de la API
│   │   ├── __init__.py
│   │   ├── routes/
│   │   └── dependencies.py
│   │
│   ├── core/                   # Lógica de negocio principal
│   │   ├── __init__.py
│   │   ├── exchanges/          # Integraciones con exchanges
│   │   ├── indicators/         # Indicadores técnicos
│   │   ├── strategies/         # Estrategias de trading
│   │   └── backtesting/        # Motor de backtesting
│   │
│   ├── models/                 # Modelos de base de datos
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── services/               # Servicios y utilidades
│   │   ├── __init__.py
│   │   ├── data_service.py
│   │   └── notification_service.py
│   │
│   └── utils/                  # Funciones de utilidad
│       ├── __init__.py
│       └── helpers.py
│
├── tests/                      # Pruebas unitarias
├── scripts/                    # Scripts de utilidad
├── docs/                       # Documentación técnica
├── requirements.txt            # Dependencias de Python
└── .env.example               # Ejemplo de variables de entorno
```

## 🧪 Testing

```bash
# Ejecutar todas las pruebas
pytest tests/

# Ejecutar con cobertura
pytest tests/ --cov=src --cov-report=html

# Ejecutar pruebas específicas
pytest tests/test_indicators.py -v
```

## 📚 Documentación de la API

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔄 Estado Actual del Desarrollo

### ✅ Completado
- [x] Estructura básica del proyecto
- [x] Documentación inicial

### 🚧 En Progreso
- [ ] Configuración del entorno de desarrollo
- [ ] Estructura de archivos base
- [ ] Configuración de FastAPI

### 📋 Próximas Tareas
1. **Configurar entorno Python** y dependencias básicas
2. **Implementar conexión** con API de Binance (exchange principal)
3. **Crear modelos de datos** para precios y volúmenes
4. **Desarrollar indicadores técnicos** básicos (RSI, MACD)
5. **Implementar API endpoints** para datos de mercado

## ⚡ Comandos Rápidos

```bash
# Instalación completa desde cero
./scripts/setup.sh

# Ejecutar servidor de desarrollo
./scripts/dev.sh

# Ejecutar todas las pruebas
./scripts/test.sh

# Limpiar cache y archivos temporales
./scripts/clean.sh
```

---

**¡El backend será el motor que impulse todo el análisis técnico!** Comencemos paso a paso construyendo cada componente. 🚀📊
