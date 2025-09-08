# Guía de Despliegue - Crypto Trading Analyzer

## 🚀 Opciones de Despliegue

### 1. Despliegue Local

#### Requisitos del Sistema
- **OS**: Linux, macOS, Windows
- **Python**: 3.8 o superior
- **RAM**: Mínimo 2GB, recomendado 4GB
- **Almacenamiento**: Mínimo 1GB libre
- **Red**: Conexión estable a internet

#### Instalación Paso a Paso

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd crypto-trading-analyzer

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# 3. Instalar dependencias
pip install -r src/config/requirements.txt

# 4. Configurar variables de entorno
cp src/config/.env.example .env
# Editar .env con tus configuraciones

# 5. Inicializar base de datos
python src/database/db_manager_cli.py migrate

# 6. Ejecutar el sistema
python main.py
```

### 2. Despliegue con Docker

#### Usando Docker Compose (Recomendado)

```bash
# 1. Clonar el repositorio
git clone <repository-url>
cd crypto-trading-analyzer

# 2. Configurar variables de entorno
cp src/config/.env.example .env
# Editar .env con tus configuraciones

# 3. Construir y ejecutar
docker-compose -f deployment/docker-compose.yml up -d

# 4. Verificar estado
docker-compose -f deployment/docker-compose.yml ps

# 5. Ver logs
docker-compose -f deployment/docker-compose.yml logs -f
```

#### Usando Docker Manual

```bash
# 1. Construir imagen
docker build -f deployment/Dockerfile -t crypto-trading-analyzer .

# 2. Ejecutar contenedor
docker run -d \
  --name trading-bot \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  crypto-trading-analyzer
```

### 3. Despliegue en Servidor (VPS)

#### Preparación del Servidor

```bash
# Actualizar sistema (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3 python3-pip python3-venv git docker.io docker-compose

# Configurar Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

#### Configuración de Producción

```bash
# 1. Crear usuario dedicado
sudo useradd -m -s /bin/bash trading
sudo su - trading

# 2. Clonar y configurar
git clone <repository-url>
cd crypto-trading-analyzer

# 3. Configurar variables de entorno para producción
cp src/config/.env.example .env
# Configurar con valores de producción

# 4. Configurar como servicio systemd
sudo cp deployment/trading-bot.service /etc/systemd/system/
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
```

## ⚙️ Configuración de Producción

### Variables de Entorno Críticas

```env
# Configuración de API (OBLIGATORIO para trading real)
BINANCE_API_KEY=your_production_api_key
BINANCE_SECRET_KEY=your_production_secret_key
BINANCE_TESTNET=false  # false para producción

# Configuración de Trading
TRADING_MODE=live  # live para trading real
TRADING_PROFILE=conservative  # Perfil de riesgo

# Base de Datos
DATABASE_URL=sqlite:///data/trading_bot.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/trading.log

# Seguridad
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=your-domain.com,localhost

# Monitoreo
MONITORING_ENABLED=true
ALERT_EMAIL=your-email@domain.com
```

### Configuración de Seguridad

#### 1. Firewall

```bash
# Configurar UFW (Ubuntu)
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

#### 2. SSL/TLS (si usas interfaz web)

```bash
# Instalar Certbot
sudo apt install certbot

# Obtener certificado
sudo certbot certonly --standalone -d your-domain.com
```

#### 3. Backup Automático

```bash
# Crear script de backup
cat > /home/trading/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/trading/backups"
mkdir -p $BACKUP_DIR

# Backup de base de datos
python /home/trading/crypto-trading-analyzer/src/database/db_manager_cli.py backup $BACKUP_DIR/db_backup_$DATE.sql

# Backup de configuración
cp /home/trading/crypto-trading-analyzer/.env $BACKUP_DIR/env_backup_$DATE

# Limpiar backups antiguos (mantener últimos 30 días)
find $BACKUP_DIR -name "*backup*" -mtime +30 -delete
EOF

chmod +x /home/trading/backup.sh

# Configurar cron para backup diario
echo "0 2 * * * /home/trading/backup.sh" | crontab -
```

## 📊 Monitoreo y Mantenimiento

### Comandos de Monitoreo

```bash
# Estado del sistema
python src/database/db_manager_cli.py stats

# Logs en tiempo real
tail -f logs/trading.log

# Estado de Docker
docker-compose -f deployment/docker-compose.yml ps

# Uso de recursos
docker stats

# Verificar conectividad API
python -c "from src.core.trading_bot import TradingBot; bot = TradingBot(); print('API OK' if bot.test_connection() else 'API ERROR')"
```

### Mantenimiento Regular

#### Diario
- Verificar logs de errores
- Comprobar estado de conexiones API
- Revisar métricas de trading

#### Semanal
- Actualizar dependencias de seguridad
- Verificar backups
- Analizar rendimiento del sistema

#### Mensual
- Actualizar el sistema operativo
- Revisar y optimizar configuraciones
- Análisis completo de rendimiento

### Scripts de Mantenimiento

```bash
# Script de salud del sistema
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "=== Health Check $(date) ==="

# Verificar proceso
if pgrep -f "python main.py" > /dev/null; then
    echo "✅ Trading bot is running"
else
    echo "❌ Trading bot is NOT running"
fi

# Verificar base de datos
if python src/database/db_manager_cli.py stats > /dev/null 2>&1; then
    echo "✅ Database is accessible"
else
    echo "❌ Database connection failed"
fi

# Verificar espacio en disco
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "✅ Disk usage: ${DISK_USAGE}%"
else
    echo "⚠️  Disk usage high: ${DISK_USAGE}%"
fi

echo "========================"
EOF

chmod +x health_check.sh
```

## 🚨 Solución de Problemas

### Problemas Comunes

#### 1. Error de Conexión API
```bash
# Verificar configuración
echo $BINANCE_API_KEY
echo $BINANCE_SECRET_KEY

# Probar conexión
python -c "import ccxt; exchange = ccxt.binance({'apiKey': 'your_key', 'secret': 'your_secret', 'sandbox': True}); print(exchange.fetch_balance())"
```

#### 2. Base de Datos Corrupta
```bash
# Verificar integridad
sqlite3 trading_bot.db "PRAGMA integrity_check;"

# Restaurar desde backup
python src/database/db_manager_cli.py restore backup_file.sql
```

#### 3. Alto Uso de CPU/Memoria
```bash
# Verificar procesos
top -p $(pgrep -f "python main.py")

# Reiniciar servicio
sudo systemctl restart trading-bot
```

#### 4. Logs de Error
```bash
# Buscar errores recientes
grep -i error logs/trading.log | tail -20

# Filtrar por fecha
grep "$(date +%Y-%m-%d)" logs/trading.log | grep -i error
```

### Contacto de Soporte

Para problemas críticos:
1. Revisar logs detallados
2. Ejecutar health check
3. Crear issue en GitHub con información completa
4. Incluir configuración (sin claves sensibles)

---

**Nota**: Siempre prueba en modo paper trading antes de desplegar en producción con dinero real.