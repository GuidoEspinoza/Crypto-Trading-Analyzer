# Crypto Trading Analyzer - Sistema de Trading Automatizado

## 🚀 Descripción

Sistema profesional de trading automatizado para criptomonedas con capacidades de análisis técnico avanzado, gestión de riesgo dinámica y monitoreo en tiempo real.

## 📁 Estructura del Proyecto

```
crypto-trading-analyzer/
├── src/                          # Código fuente principal
│   ├── config/                   # Configuraciones del sistema
│   │   ├── production_config.py  # Configuración de producción
│   │   └── settings.py          # Configuraciones base
│   ├── core/                    # Motor de trading principal
│   │   ├── trading_bot.py       # Bot de trading principal
│   │   ├── enhanced_strategies.py # Estrategias avanzadas
│   │   ├── enhanced_risk_manager.py # Gestión de riesgo
│   │   └── ...
│   ├── database/                # Capa de base de datos
│   │   ├── models.py           # Modelos de datos
│   │   ├── database.py         # Gestor de base de datos
│   │   ├── migrations.py       # Sistema de migraciones
│   │   └── db_manager_cli.py   # CLI de gestión de BD
│   ├── monitoring/             # Sistema de monitoreo
│   │   └── trading_monitor.py  # Monitor de trading
│   └── utils/                  # Utilidades comunes
├── tests/                      # Tests del sistema
├── deployment/                 # Archivos de despliegue
│   ├── Dockerfile             # Imagen Docker
│   ├── docker-compose.yml     # Orquestación
│   └── docker-entrypoint.sh   # Script de entrada
├── docs/                      # Documentación
└── main.py                    # Punto de entrada principal
```

## 🛠️ Instalación

### Requisitos Previos
- Python 3.8+
- Docker (opcional)
- API Keys de Binance (para trading real)

### Instalación Local

```bash
# Clonar el repositorio
git clone <repository-url>
cd crypto-trading-analyzer

# Instalar dependencias
pip install -r src/config/requirements.txt

# Configurar variables de entorno
cp src/config/.env.example .env
# Editar .env con tus configuraciones

# Inicializar base de datos
python src/database/db_manager_cli.py migrate
```

### Instalación con Docker

```bash
# Construir y ejecutar con Docker Compose
docker-compose -f deployment/docker-compose.yml up -d
```

## 🚀 Uso

### Modo Paper Trading (Simulación)

```bash
# Ejecutar el sistema en modo simulación
python main.py
```

### Monitoreo del Sistema

```bash
# Monitor de trading en tiempo real
python src/monitoring/trading_monitor.py

# Estadísticas de base de datos
python src/database/db_manager_cli.py stats

# Estado de migraciones
python src/database/db_manager_cli.py migration-status
```

### Gestión de Base de Datos

```bash
# Aplicar migraciones
python src/database/db_manager_cli.py migrate

# Backup de base de datos
python src/database/db_manager_cli.py backup

# Restaurar backup
python src/database/db_manager_cli.py restore backup_file.sql

# Limpiar datos antiguos
python src/database/db_manager_cli.py cleanup --days 30
```

## ⚙️ Configuración

### Variables de Entorno

Crea un archivo `.env` basado en `src/config/.env.example`:

```env
# API Configuration
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
BINANCE_TESTNET=true

# Trading Configuration
TRADING_MODE=paper  # paper | live
TRADING_PROFILE=conservative  # conservative | moderate | aggressive

# Database
DATABASE_URL=sqlite:///trading_bot.db

# Logging
LOG_LEVEL=INFO
```

### Perfiles de Trading

- **Conservative**: Bajo riesgo, ganancias estables
- **Moderate**: Riesgo medio, balance riesgo/ganancia
- **Aggressive**: Alto riesgo, potencial de altas ganancias

## 🧪 Testing

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Tests específicos
python -m pytest tests/test_circuit_breaker.py -v
```

## 📊 Características

### Trading
- ✅ Paper Trading (simulación)
- ✅ Estrategias de trading avanzadas
- ✅ Gestión de riesgo dinámica
- ✅ Take Profit y Stop Loss adaptativos
- ✅ Análisis técnico con múltiples indicadores
- ✅ Circuit breakers para protección

### Monitoreo
- ✅ Monitor en tiempo real
- ✅ Alertas de sistema
- ✅ Métricas de rendimiento
- ✅ Logs estructurados

### Base de Datos
- ✅ Sistema de migraciones
- ✅ Backup automático
- ✅ CLI de gestión
- ✅ Optimización de rendimiento

### Despliegue
- ✅ Dockerización completa
- ✅ Docker Compose para orquestación
- ✅ Configuración de producción
- ✅ Scripts de automatización

## 🔧 Desarrollo

### Estructura de Código
- **src/core/**: Lógica principal de trading
- **src/config/**: Configuraciones y perfiles
- **src/database/**: Persistencia y migraciones
- **src/monitoring/**: Monitoreo y alertas
- **tests/**: Suite de pruebas

### Contribuir
1. Fork el proyecto
2. Crear una rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit los cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear un Pull Request

## 📈 Roadmap

- [ ] Integración con más exchanges
- [ ] Dashboard web en tiempo real
- [ ] Backtesting avanzado
- [ ] Machine Learning para predicciones
- [ ] API REST para integración externa
- [ ] Notificaciones móviles

## ⚠️ Disclaimer

Este software es para fines educativos y de investigación. El trading de criptomonedas conlleva riesgos significativos. Siempre usa el modo paper trading para probar estrategias antes de usar dinero real.

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles.

## 🤝 Soporte

Para soporte y preguntas:
- Crear un issue en GitHub
- Revisar la documentación en `/docs`
- Consultar los logs del sistema

---

**Desarrollado con ❤️ para la comunidad de trading**
