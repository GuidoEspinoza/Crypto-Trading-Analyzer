# 🚀 Guía Completa: Smart Trading Bot en Hostinger VPS

## 📋 Tabla de Contenidos
1. [Preparación en Hostinger](#1-preparación-en-hostinger)
2. [Configuración Inicial del VPS](#2-configuración-inicial-del-vps)
3. [Instalación Automatizada](#3-instalación-automatizada)
4. [Configuración del Trading Bot](#4-configuración-del-trading-bot)
5. [Configuración SSL y Dominio](#5-configuración-ssl-y-dominio)
6. [Despliegue y Monitoreo](#6-despliegue-y-monitoreo)
7. [Mantenimiento y Troubleshooting](#7-mantenimiento-y-troubleshooting)

---

## 1. Preparación en Hostinger

### 🛒 **Paso 1.1: Contratar VPS en Hostinger**

1. **Accede a Hostinger**: [https://www.hostinger.com/vps-hosting](https://www.hostinger.com/vps-hosting)

2. **Plan Recomendado para Trading Bot**:
   ```
   📦 VPS Plan 2 o VPS Plan 3
   ├── 2-4 vCPUs
   ├── 4-8 GB RAM
   ├── 80-160 GB SSD
   ├── Ubicación: Europa (Países Bajos)
   └── Precio: ~$7-15/mes
   ```

3. **Configuración durante la compra**:
   - **Sistema Operativo**: Ubuntu 22.04 LTS
   - **Ubicación**: Amsterdam, Netherlands (mejor latencia para mercados europeos)
   - **Configuración adicional**: Ninguna (lo haremos manualmente)

### 🔑 **Paso 1.2: Acceso SSH**

1. **Obtener credenciales**:
   - Ve a tu panel de Hostinger
   - Sección "VPS" → Tu VPS → "Información de acceso"
   - Anota: IP, Usuario (root), Contraseña

2. **Conectar por SSH**:
   ```bash
   # Desde tu Mac/Linux
   ssh root@TU_IP_VPS
   
   # Desde Windows (usar PuTTY o Windows Terminal)
   ```

---

## 2. Configuración Inicial del VPS

### 🔐 **Paso 2.1: Seguridad Básica**

```bash
# Cambiar contraseña de root (recomendado)
passwd

# Crear usuario no-root para mayor seguridad
adduser tradingbot
usermod -aG sudo tradingbot

# Configurar SSH key (opcional pero recomendado)
mkdir -p /home/tradingbot/.ssh
# Copiar tu clave pública aquí
```

### 🌐 **Paso 2.2: Configuración de Red**

```bash
# Verificar conectividad
ping -c 4 google.com

# Verificar timezone
timedatectl status

# Si necesitas cambiar timezone
sudo timedatectl set-timezone Europe/Amsterdam
```

---

## 3. Instalación Automatizada

### 🤖 **Paso 3.1: Ejecutar Script de Instalación**

```bash
# Descargar y ejecutar el script de instalación
wget https://raw.githubusercontent.com/TU_USUARIO/Smart-Trading-Bot/main/deployment/hostinger-setup.sh

# Dar permisos de ejecución
chmod +x hostinger-setup.sh

# Ejecutar instalación (tomará 10-15 minutos)
./hostinger-setup.sh
```

**¿Qué hace este script?**
- ✅ Actualiza Ubuntu
- ✅ Instala Docker y Docker Compose
- ✅ Configura firewall UFW
- ✅ Optimiza sistema para trading
- ✅ Configura swap y límites
- ✅ Instala certificados SSL
- ✅ Crea scripts de monitoreo

### 🔄 **Paso 3.2: Reiniciar Sesión**

```bash
# Salir y volver a conectar para aplicar cambios de Docker
exit

# Reconectar
ssh root@TU_IP_VPS  # o ssh tradingbot@TU_IP_VPS
```

---

## 4. Configuración del Trading Bot

### 📁 **Paso 4.1: Clonar Repositorio**

```bash
# Ir al directorio de trabajo
cd ~/trading-bot

# Clonar tu repositorio
git clone https://github.com/TU_USUARIO/Smart-Trading-Bot.git .

# Verificar archivos
ls -la
```

### ⚙️ **Paso 4.2: Configurar Variables de Entorno**

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar configuración
nano .env
```

**Configuración del archivo .env**:
```bash
# === CAPITAL API ===
CAPITAL_LIVE_URL=https://api-capital.backend-capital.com/api/v1
CAPITAL_DEMO_URL=https://demo-api-capital.backend-capital.com/api/v1

# ⚠️ IMPORTANTE: Configurar según tu cuenta
IS_DEMO=True  # Cambiar a False para trading real
ENABLE_REAL_TRADING=True

# 🔐 TUS CREDENCIALES DE CAPITAL.COM
identifier=tu_email@ejemplo.com
password=tu_contraseña_segura

# 🔑 API KEY de Capital.com
X-CAP-API-KEY=tu_api_key_aqui
X-SECURITY-TOKEN=null
CST=null

# === CONFIGURACIÓN ADICIONAL ===
# Timezone para logs
TZ=Europe/Amsterdam

# Configuración de trading (opcional)
MAX_RISK_PER_TRADE=2.0
DEFAULT_POSITION_SIZE=1000
```

### 🔧 **Paso 4.3: Verificar Configuración**

```bash
# Verificar que Docker funciona
docker --version
docker-compose --version

# Verificar archivos de configuración
cat docker-compose.yml
cat nginx/nginx.conf
```

---

## 5. Configuración SSL y Dominio

### 🌐 **Paso 5.1: Configurar Dominio (Opcional)**

Si tienes un dominio:

```bash
# Editar configuración de nginx
nano nginx/nginx.conf

# Cambiar "server_name _;" por:
# server_name tu-dominio.com www.tu-dominio.com;
```

### 🔒 **Paso 5.2: Obtener Certificado SSL**

```bash
# Si tienes dominio
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# Si NO tienes dominio (usar IP)
# Crear certificado auto-firmado para desarrollo
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/key.pem \
    -out /etc/nginx/ssl/cert.pem \
    -subj "/C=NL/ST=Amsterdam/L=Amsterdam/O=TradingBot/CN=TU_IP_VPS"
```

---

## 6. Despliegue y Monitoreo

### 🚀 **Paso 6.1: Lanzar el Trading Bot**

```bash
# Construir y lanzar contenedores
docker-compose up -d

# Verificar que están corriendo
docker-compose ps

# Ver logs en tiempo real
docker-compose logs -f trading-bot
```

### 📊 **Paso 6.2: Verificar Funcionamiento**

```bash
# Verificar salud del bot
curl http://localhost:8000/health

# Verificar nginx
curl http://localhost:80

# Verificar puertos abiertos
sudo netstat -tlnp | grep -E ':(80|443|8000)'
```

### 🔍 **Paso 6.3: Monitoreo Continuo**

```bash
# Ejecutar script de monitoreo
~/trading-bot/monitor.sh

# Ver estadísticas de Docker
docker stats

# Ver logs específicos
docker logs smart-trading-bot-hostinger --tail 50
```

---

## 7. Mantenimiento y Troubleshooting

### 🔧 **Comandos Útiles**

```bash
# Reiniciar trading bot
docker-compose restart trading-bot

# Actualizar código
git pull origin main
docker-compose build --no-cache
docker-compose up -d

# Backup manual
~/trading-bot/backup.sh

# Ver uso de recursos
htop
df -h
free -h
```

### 🚨 **Troubleshooting Común**

#### **Problema: Bot no inicia**
```bash
# Ver logs detallados
docker-compose logs trading-bot

# Verificar configuración
docker-compose config

# Reconstruir contenedor
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### **Problema: Sin conexión a Capital.com**
```bash
# Verificar conectividad
curl -I https://api-capital.backend-capital.com

# Verificar configuración .env
cat .env | grep -E "(identifier|password|API-KEY)"

# Probar autenticación manualmente
docker exec -it smart-trading-bot-hostinger python -c "
from src.core.capital_client import CapitalClient
client = CapitalClient.from_env()
print('Conexión exitosa!' if client else 'Error de conexión')
"
```

#### **Problema: Poco espacio en disco**
```bash
# Limpiar Docker
docker system prune -a

# Limpiar logs antiguos
sudo logrotate -f /etc/logrotate.d/trading-bot

# Ver uso de espacio
du -sh ~/trading-bot/*
```

### 📈 **Optimización de Rendimiento**

```bash
# Ajustar límites de memoria si es necesario
# Editar docker-compose.yml:
nano docker-compose.yml

# Cambiar:
# mem_limit: 1g    # Para VPS con más RAM
# cpus: 2.0        # Para VPS con más CPU
```

### 🔄 **Actualizaciones Automáticas**

```bash
# Configurar actualización automática del sistema
echo 'APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";' | sudo tee /etc/apt/apt.conf.d/20auto-upgrades

# Configurar cron para actualizar el bot (opcional)
crontab -e
# Agregar: 0 3 * * 0 cd ~/trading-bot && git pull && docker-compose up -d --build
```

---

## 🎯 **URLs de Acceso Final**

Una vez completada la instalación:

- **Trading Bot API**: `https://TU_IP_VPS:8000` o `https://tu-dominio.com`
- **Health Check**: `https://TU_IP_VPS:8000/health`
- **Documentación API**: `https://TU_IP_VPS:8000/docs`
- **Monitoreo**: SSH + `~/trading-bot/monitor.sh`

---

## 🆘 **Soporte y Contacto**

Si encuentras problemas:

1. **Revisa los logs**: `docker-compose logs trading-bot`
2. **Verifica la configuración**: `docker-compose config`
3. **Consulta esta guía**: Especialmente la sección de troubleshooting
4. **Contacta soporte**: [Información de contacto]

---

## ✅ **Checklist Final**

- [ ] VPS contratado en Hostinger
- [ ] SSH configurado y funcionando
- [ ] Script de instalación ejecutado exitosamente
- [ ] Repositorio clonado
- [ ] Archivo .env configurado con credenciales reales
- [ ] SSL configurado (dominio o auto-firmado)
- [ ] Trading bot desplegado con `docker-compose up -d`
- [ ] Health check respondiendo correctamente
- [ ] Monitoreo configurado y funcionando
- [ ] Backup automático configurado

**🎉 ¡Felicidades! Tu Smart Trading Bot está corriendo en Hostinger VPS.**