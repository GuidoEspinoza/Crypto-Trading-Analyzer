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
# Clonar repositorio en el directorio correcto
git clone https://github.com/GuidoEspinoza/Smart-Trading-Bot.git ~/trading-bot

# Ir al directorio de trabajo
cd ~/trading-bot

# Verificar archivos (deben estar directamente en ~/trading-bot)
ls -la

# Verificar estructura correcta
echo "✅ Verificando estructura de archivos:"
ls -la | grep -E "(main.py|docker-compose.yml|requirements.txt|src/)"
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

#### **Problema: Directorios anidados (~/trading-bot/Smart-Trading-Bot)**

**Síntomas del problema:**
- Los archivos están en `~/trading-bot/Smart-Trading-Bot/` en lugar de `~/trading-bot/`
- Al ejecutar `docker-compose up` aparece error "No such file or directory"
- El comando `ls ~/trading-bot/` muestra una carpeta "Smart-Trading-Bot"

**Solución paso a paso:**

```bash
# 1. Verificar si tienes el problema
echo "🔍 Verificando estructura actual:"
ls -la ~/trading-bot/

# Si ves una carpeta "Smart-Trading-Bot", tienes el problema
echo "❌ Estructura incorrecta detectada"

# 2. Hacer backup por seguridad (opcional)
cp -r ~/trading-bot ~/trading-bot-backup-$(date +%Y%m%d)

# 3. Mover todos los archivos al directorio correcto
echo "📦 Moviendo archivos a la ubicación correcta..."

# Mover archivos visibles
mv ~/trading-bot/Smart-Trading-Bot/* ~/trading-bot/ 2>/dev/null

# Mover archivos ocultos (como .env, .gitignore, etc.)
find ~/trading-bot/Smart-Trading-Bot -name ".*" -maxdepth 1 -type f -exec mv {} ~/trading-bot/ \; 2>/dev/null

# 4. Eliminar directorio vacío
rmdir ~/trading-bot/Smart-Trading-Bot 2>/dev/null

# 5. Verificar estructura correcta
echo "✅ Verificando estructura corregida:"
cd ~/trading-bot
ls -la

# 6. Verificar archivos críticos
echo "🔍 Verificando archivos críticos del proyecto:"
for file in main.py docker-compose.yml requirements.txt Dockerfile .env.example; do
    if [ -f "$file" ]; then
        echo "✅ $file - Encontrado"
    else
        echo "❌ $file - FALTANTE"
    fi
done

# 7. Verificar directorio src/
if [ -d "src/" ]; then
    echo "✅ Directorio src/ - Encontrado"
    echo "📁 Contenido de src/:"
    ls -la src/
else
    echo "❌ Directorio src/ - FALTANTE"
fi

# 8. Verificar que Docker puede leer los archivos
echo "🐳 Verificando configuración de Docker:"
docker-compose config --quiet && echo "✅ docker-compose.yml válido" || echo "❌ Error en docker-compose.yml"
```

**Verificación final:**
```bash
# La estructura correcta debe verse así:
cd ~/trading-bot
tree -L 2 -a  # Si tienes tree instalado

# O usar ls para verificar:
echo "📋 Estructura final esperada:"
ls -la | head -20
echo ""
echo "📁 Debe contener directamente:"
echo "  ✅ main.py"
echo "  ✅ docker-compose.yml" 
echo "  ✅ requirements.txt"
echo "  ✅ Dockerfile"
echo "  ✅ src/ (directorio)"
echo "  ✅ .env.example"
echo "  ✅ README.md"
```

**Si algo sale mal:**
```bash
# Restaurar desde backup
rm -rf ~/trading-bot
mv ~/trading-bot-backup-$(date +%Y%m%d) ~/trading-bot

# O empezar desde cero
rm -rf ~/trading-bot
git clone https://github.com/GuidoEspinoza/Smart-Trading-Bot.git ~/trading-bot
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

---

## 🔄 Actualización del Bot tras Cambios de Código

Cuando realices cambios en el repositorio (por ejemplo: presupuestos por sesión, modificación de horarios, o actualización de símbolos), sigue este procedimiento para aplicarlos en Hostinger.

### ✅ Paso A: Confirmar que el código está en GitHub

```bash
# En tu máquina local
cd /ruta/a/tu/proyecto
git status
git add -A
git commit -m "Session budgets + horarios + remove USDJPY/EURGBP/USDCHF + docs"
git push origin main
```

### 🚀 Paso B: Aplicar actualización en Hostinger

```bash
# 1) Conectar al servidor
ssh root@TU_IP_VPS   # o ssh tradingbot@TU_IP_VPS

# 2) Ir al proyecto
cd ~/trading-bot

# 3) Opcional: backup de .env
cp .env .env.backup_$(date +%Y%m%d)

# 4) Ver estado y descartar cambios locales si existen
git status
# Si hay cambios locales no deseados:
git reset --hard HEAD

# 5) Traer últimos cambios del repositorio
git pull origin main

# 6) Reconstruir y reiniciar contenedores
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d

# 7) Verificar contenedores y logs
docker ps
docker logs -f smart-trading-bot-hostinger
```

### 🧪 Paso C: Verificar la actualización

```bash
# Health del bot (API)
curl -s http://localhost:8000/health | python3 -m json.tool

# Configuración del bot (revisar symbols)
curl -s http://localhost:8000/bot/config | python3 -m json.tool
# Buscar que no esté USDJPY/EURGBP/USDCHF
curl -s http://localhost:8000/bot/config | python3 - <<'PY'
import sys, json
cfg = json.load(sys.stdin)
symbols = cfg.get('configuration',{}).get('symbols', [])
print('✅ Verificación de símbolos:')
for bad in ['USDJPY','EURGBP','USDCHF']:
    print(f" - {bad}: {'PRESENTE' if bad in symbols else 'NO PRESENTE'}")
PY
```

### 📈 Qué esperar en los logs
- Durante `london_open`/`ny_open`, el bot limitará operaciones según `SESSION_BUDGETS`.
- Verás mensajes tipo: `⏸️ Session budget reached for ny_open (8/8)` cuando se alcance el cupo.
- A medianoche UTC, verás: `📅 Daily stats reset at 00:00 (UTC) ...` y los contadores vuelven a cero.

### 🧯 Troubleshooting de actualización

```bash
# Conflictos de git por cambios locales
cd ~/trading-bot
# Opción rápida: descartar y traer remoto
git reset --hard HEAD && git pull origin main

# Reconstrucción limpia si hay errores de dependencia
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d

# Nginx no levanta por puerto 80 ocupado (servicio del sistema)
# Puedes usar directamente el puerto 8000 del bot:
curl -s http://localhost:8000/health | python3 -m json.tool
# O cambiar el puerto en nginx (ej. 8080) y reiniciar nginx en Docker
```

### 🧭 Comando único (actualización end-to-end)

```bash
ssh root@TU_IP_VPS <<'EOS'
set -e
cd ~/trading-bot
cp .env .env.backup_$(date +%Y%m%d) || true
git reset --hard HEAD
git pull origin main

# Verificaciones
grep -n "USDJPY\|EURGBP\|USDCHF" src/config/symbols_config.py || echo "✅ Símbolos removidos"
grep -n "SESSION_BUDGETS" src/config/time_trading_config.py || echo "⚠️ Revisar presupuestos por sesión"

docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d

echo "📋 Containers:" && docker ps

echo "🔎 Health:" && curl -s http://localhost:8000/health | python3 -m json.tool
EOS
```