#!/bin/bash

# 🚀 Smart Trading Bot - Script de Instalación Automatizada para Hostinger VPS
# Versión: 1.0
# Compatible con: Ubuntu 22.04 LTS

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🚀 SMART TRADING BOT - HOSTINGER VPS SETUP 🚀        ║
║                                                              ║
║  Este script configurará automáticamente tu VPS para        ║
║  ejecutar el Smart Trading Bot de forma segura y eficiente  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Verificar que estamos en Ubuntu
if [[ ! -f /etc/lsb-release ]] || ! grep -q "Ubuntu" /etc/lsb-release; then
    error "Este script está diseñado para Ubuntu. Hostinger VPS usa Ubuntu por defecto."
fi

log "🔍 Verificando sistema Ubuntu en Hostinger VPS..."
cat /etc/lsb-release

# Actualizar sistema
log "📦 Actualizando sistema Ubuntu..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
log "🛠️ Instalando dependencias básicas..."
sudo apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    htop \
    nano \
    ufw

# Configurar firewall UFW (específico para Hostinger)
log "🛡️ Configurando firewall UFW para Hostinger..."
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp  # Puerto del trading bot
sudo ufw --force enable

# Instalar Docker
log "🐳 Instalando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Instalar Docker Compose
log "🔧 Instalando Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configurar usuario para Docker
log "👤 Configurando permisos de Docker..."
sudo usermod -aG docker $USER

# Crear directorios necesarios
log "📁 Creando estructura de directorios..."
mkdir -p ~/trading-bot/{logs,data,nginx,backup}
mkdir -p ~/trading-bot/nginx/ssl

# Configurar timezone para Europa (Hostinger)
log "🕐 Configurando timezone para Europa..."
sudo timedatectl set-timezone Europe/Amsterdam

# Instalar certificados SSL con Let's Encrypt
log "🔒 Instalando Certbot para SSL..."
sudo apt install -y certbot python3-certbot-nginx

# Configurar límites del sistema para trading
log "⚙️ Optimizando configuración del sistema para trading..."
sudo tee -a /etc/security/limits.conf << EOF
# Límites optimizados para trading bot
* soft nofile 65536
* hard nofile 65536
* soft nproc 32768
* hard nproc 32768
EOF

# Configurar swap (importante para VPS con poca RAM)
log "💾 Configurando swap para optimizar memoria..."
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi

# Configurar logrotate para logs del trading bot
log "📝 Configurando rotación de logs..."
sudo tee /etc/logrotate.d/trading-bot << EOF
/home/$USER/trading-bot/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Crear script de monitoreo
log "📊 Creando script de monitoreo..."
tee ~/trading-bot/monitor.sh << 'EOF'
#!/bin/bash
# Script de monitoreo para Trading Bot en Hostinger

echo "=== ESTADO DEL TRADING BOT ==="
echo "Fecha: $(date)"
echo "Uptime: $(uptime)"
echo ""

echo "=== CONTENEDORES DOCKER ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "=== USO DE RECURSOS ==="
echo "CPU y Memoria:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""

echo "=== ESPACIO EN DISCO ==="
df -h /
echo ""

echo "=== LOGS RECIENTES ==="
echo "Últimas 5 líneas del trading bot:"
docker logs smart-trading-bot-hostinger --tail 5 2>/dev/null || echo "Contenedor no encontrado"
EOF

chmod +x ~/trading-bot/monitor.sh

# Crear script de backup
log "💾 Creando script de backup..."
tee ~/trading-bot/backup.sh << 'EOF'
#!/bin/bash
# Script de backup para Trading Bot

BACKUP_DIR="/home/$USER/trading-bot/backup"
DATE=$(date +%Y%m%d_%H%M%S)

echo "Creando backup: $DATE"

# Backup de configuración
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    /home/$USER/trading-bot/.env \
    /home/$USER/trading-bot/docker-compose.yml \
    /home/$USER/trading-bot/nginx/ 2>/dev/null

# Backup de datos
tar -czf "$BACKUP_DIR/data_$DATE.tar.gz" \
    /home/$USER/trading-bot/data/ \
    /home/$USER/trading-bot/logs/ 2>/dev/null

# Limpiar backups antiguos (mantener últimos 7 días)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +7 -delete

echo "Backup completado: $BACKUP_DIR"
EOF

chmod +x ~/trading-bot/backup.sh

# Configurar cron para backup automático
log "⏰ Configurando backup automático..."
(crontab -l 2>/dev/null; echo "0 2 * * * /home/$USER/trading-bot/backup.sh >> /home/$USER/trading-bot/logs/backup.log 2>&1") | crontab -

# Información final
log "✅ Instalación completada exitosamente!"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗"
echo -e "║                    🎉 INSTALACIÓN COMPLETA                  ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Próximos pasos:${NC}"
echo "1. Reinicia la sesión: ${YELLOW}exit${NC} y vuelve a conectarte"
echo "2. Clona tu repositorio en: ${YELLOW}~/trading-bot/${NC}"
echo "3. Configura tu archivo .env"
echo "4. Ejecuta: ${YELLOW}docker-compose up -d${NC}"
echo ""
echo -e "${GREEN}Scripts útiles creados:${NC}"
echo "• Monitor: ${YELLOW}~/trading-bot/monitor.sh${NC}"
echo "• Backup: ${YELLOW}~/trading-bot/backup.sh${NC}"
echo ""
echo -e "${GREEN}Puertos configurados:${NC}"
echo "• HTTP: 80"
echo "• HTTPS: 443" 
echo "• Trading Bot: 8000"
echo ""
warn "¡IMPORTANTE! Reinicia la sesión para que los cambios de Docker tengan efecto."