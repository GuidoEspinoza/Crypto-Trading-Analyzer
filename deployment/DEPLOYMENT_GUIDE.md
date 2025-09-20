# 🚀 Guía de Despliegue en Servidor

## 📋 Requisitos del Servidor

### Especificaciones Mínimas Recomendadas
- **CPU**: 4 cores (8 cores recomendado)
- **RAM**: 8GB (16GB recomendado)
- **Almacenamiento**: 100GB SSD (500GB recomendado)
- **Ancho de banda**: 100 Mbps
- **Sistema Operativo**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+

### Proveedores Recomendados
1. **DigitalOcean** - Droplet 4GB ($24/mes)
2. **AWS EC2** - t3.large ($67/mes)
3. **Google Cloud** - e2-standard-2 ($49/mes)
4. **Vultr** - High Performance 4GB ($24/mes)
5. **Linode** - Dedicated 4GB ($30/mes)

## 🔧 Preparación del Servidor

### 1. Configuración Inicial
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y curl wget git vim htop unzip

# Configurar firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8080
```

### 2. Instalar Docker y Docker Compose
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalación
docker --version
docker-compose --version
```

### 3. Configurar Nginx (Proxy Reverso)
```bash
# Instalar Nginx
sudo apt install -y nginx

# Configurar sitio
sudo tee /etc/nginx/sites-available/trading-bot << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
EOF

# Habilitar sitio
sudo ln -s /etc/nginx/sites-available/trading-bot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. Configurar SSL con Let's Encrypt
```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL
sudo certbot --nginx -d your-domain.com

# Verificar renovación automática
sudo certbot renew --dry-run
```

## 📦 Despliegue de la Aplicación

### 1. Clonar Repositorio
```bash
# Crear directorio de aplicación
sudo mkdir -p /opt/trading-bot
sudo chown $USER:$USER /opt/trading-bot
cd /opt/trading-bot

# Clonar código
git clone https://github.com/your-username/crypto-trading-analyzer.git .
```

### 2. Configurar Variables de Entorno
```bash
# Crear archivo de configuración
cp .env.example .env.production

# Editar configuración
nano .env.production
```

**Contenido del archivo `.env.production`:**
```env
# === CONFIGURACIÓN DEL SERVIDOR ===
SERVER_TYPE=production
HOST=0.0.0.0
PORT=8080
WORKERS=4

# === BASE DE DATOS ===
DATABASE_URL=postgresql://trading_user:SECURE_PASSWORD@postgres:5432/trading_db
POSTGRES_USER=trading_user
POSTGRES_PASSWORD=SECURE_PASSWORD
POSTGRES_DB=trading_db

# === REDIS ===
REDIS_URL=redis://redis:6379/0

# === SEGURIDAD ===
SECRET_KEY=your-super-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
CORS_ORIGINS=["https://your-domain.com"]

# === TRADING ===
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret_key
BINANCE_TESTNET=false

# === MONITOREO ===
LOG_LEVEL=INFO
ALERT_WEBHOOK_URL=https://hooks.slack.com/your-webhook-url

# === BACKUP ===
S3_BUCKET=your-backup-bucket
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
```

### 3. Configurar Docker Compose para Producción
```bash
# Crear docker-compose.production.yml
cat > docker-compose.production.yml << 'EOF'
version: '3.8'

services:
  trading-bot:
    build: .
    restart: unless-stopped
    env_file: .env.production
    ports:
      - "8080:8080"
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
      - ./backups:/app/backups
    depends_on:
      - postgres
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G

  postgres:
    image: postgres:15
    restart: unless-stopped
    env_file: .env.production
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
EOF
```

### 4. Construir y Desplegar
```bash
# Construir imágenes
docker-compose -f docker-compose.production.yml build

# Iniciar servicios
docker-compose -f docker-compose.production.yml up -d

# Verificar estado
docker-compose -f docker-compose.production.yml ps
```

## 🔍 Verificación del Despliegue

### 1. Health Checks
```bash
# Verificar aplicación principal
curl http://localhost:8080/health

# Verificar base de datos
docker-compose -f docker-compose.production.yml exec postgres pg_isready

# Verificar Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli ping

# Verificar logs
docker-compose -f docker-compose.production.yml logs -f trading-bot
```

### 2. Pruebas de Funcionalidad
```bash
# Probar API
curl -X GET http://localhost:8080/api/v1/status

# Probar dashboard
curl -X GET http://localhost:8080/dashboard

# Verificar métricas
curl -X GET http://localhost:8080/metrics
```

## 📊 Configuración de Monitoreo

### 1. Configurar Prometheus
```bash
# Crear configuración de Prometheus
mkdir -p monitoring
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'trading-bot'
    static_configs:
      - targets: ['trading-bot:8080']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
```

### 2. Configurar Alertas
```bash
# Crear reglas de alerta
cat > monitoring/alert_rules.yml << 'EOF'
groups:
  - name: trading_bot_alerts
    rules:
      - alert: HighCPUUsage
        expr: cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alto uso de CPU"

      - alert: HighMemoryUsage
        expr: memory_usage_percent > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alto uso de memoria"

      - alert: TradingSystemDown
        expr: up{job="trading-bot"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Sistema de trading caído"
EOF
```

## 🔒 Configuración de Seguridad

### 1. Configurar Fail2Ban
```bash
# Instalar Fail2Ban
sudo apt install -y fail2ban

# Configurar para SSH
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 3
EOF

sudo systemctl restart fail2ban
```

### 2. Configurar Backup Automático
```bash
# Crear script de backup
sudo tee /opt/trading-bot/backup.sh << 'EOF'
#!/bin/bash
cd /opt/trading-bot

# Backup de base de datos
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U trading_user trading_db | gzip > backups/db_$(date +%Y%m%d_%H%M%S).sql.gz

# Backup de configuración
tar -czf backups/config_$(date +%Y%m%d_%H%M%S).tar.gz src/config/ .env.production

# Limpiar backups antiguos (más de 7 días)
find backups/ -name "*.gz" -mtime +7 -delete
find backups/ -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /opt/trading-bot/backup.sh

# Configurar cron para backup diario
echo "0 2 * * * /opt/trading-bot/backup.sh" | sudo crontab -
```

## 📈 Optimización de Rendimiento

### 1. Configurar Límites del Sistema
```bash
# Aumentar límites de archivos abiertos
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimizar kernel para red
sudo tee -a /etc/sysctl.conf << 'EOF'
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
EOF

sudo sysctl -p
```

### 2. Configurar Swap
```bash
# Crear archivo swap de 4GB
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Hacer permanente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🚨 Solución de Problemas

### Problemas Comunes

1. **Error de conexión a base de datos**
   ```bash
   # Verificar logs
   docker-compose -f docker-compose.production.yml logs postgres
   
   # Reiniciar servicio
   docker-compose -f docker-compose.production.yml restart postgres
   ```

2. **Alto uso de memoria**
   ```bash
   # Verificar uso de memoria
   docker stats
   
   # Reiniciar aplicación
   docker-compose -f docker-compose.production.yml restart trading-bot
   ```

3. **Problemas de SSL**
   ```bash
   # Renovar certificado
   sudo certbot renew
   
   # Verificar configuración Nginx
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.production.yml logs -f

# Acceder al contenedor
docker-compose -f docker-compose.production.yml exec trading-bot bash

# Backup manual
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U trading_user trading_db > backup.sql

# Restaurar backup
docker-compose -f docker-compose.production.yml exec -T postgres psql -U trading_user trading_db < backup.sql

# Actualizar aplicación
git pull
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d
```

## 📞 Soporte y Mantenimiento

### Monitoreo Continuo
- **Grafana Dashboard**: http://your-domain.com:3000
- **Prometheus Metrics**: http://your-domain.com:9090
- **Application Health**: http://your-domain.com/health

### Mantenimiento Programado
- **Backups**: Diarios a las 2:00 AM
- **Actualizaciones**: Semanales los domingos
- **Limpieza de logs**: Diaria
- **Renovación SSL**: Automática cada 60 días

### Contacto de Emergencia
- **Alertas críticas**: Configurar webhook a Slack/Discord
- **Monitoreo 24/7**: Configurar UptimeRobot o similar
- **Logs centralizados**: Considerar ELK Stack para producción

---

## ✅ Checklist de Despliegue

- [ ] Servidor configurado con especificaciones mínimas
- [ ] Docker y Docker Compose instalados
- [ ] Nginx configurado como proxy reverso
- [ ] SSL configurado con Let's Encrypt
- [ ] Variables de entorno configuradas
- [ ] Base de datos PostgreSQL funcionando
- [ ] Redis funcionando
- [ ] Aplicación desplegada y funcionando
- [ ] Health checks pasando
- [ ] Monitoreo configurado (Prometheus + Grafana)
- [ ] Backups automáticos configurados
- [ ] Seguridad configurada (Fail2Ban, Firewall)
- [ ] Alertas configuradas
- [ ] Documentación actualizada

**¡Tu sistema de trading está listo para producción! 🚀**