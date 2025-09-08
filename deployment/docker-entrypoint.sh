#!/bin/bash
# Crypto Trading Analyzer - Docker Entrypoint Script
# Versión: 2.0.0
# Script de inicialización para contenedor Docker

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función de logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
}

# Banner de inicio
echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════"
echo "🚀 CRYPTO TRADING ANALYZER v2.0.0"
echo "   Sistema Profesional de Trading Automatizado"
echo "═══════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Verificar variables de entorno críticas
log "Verificando configuración del sistema..."

# Verificar Python
if ! command -v python &> /dev/null; then
    log_error "Python no encontrado"
    exit 1
fi
log_success "Python $(python --version | cut -d' ' -f2) detectado"

# Verificar estructura de directorios
log "Verificando estructura de directorios..."
for dir in "data" "logs" "config"; do
    if [ ! -d "/app/$dir" ]; then
        log "Creando directorio: $dir"
        mkdir -p "/app/$dir"
    fi
done
log_success "Estructura de directorios verificada"

# Configurar permisos
log "Configurando permisos..."
chmod -R 755 /app/src
chmod -R 755 /app/scripts
chmod 644 /app/main.py
log_success "Permisos configurados"

# Verificar conectividad de red (opcional)
if [ "$SKIP_NETWORK_CHECK" != "true" ]; then
    log "Verificando conectividad de red..."
    if ping -c 1 8.8.8.8 &> /dev/null; then
        log_success "Conectividad de red OK"
    else
        log_warning "Sin conectividad de red externa"
    fi
fi

# Verificar dependencias críticas
log "Verificando dependencias críticas..."
critical_packages=("numpy" "pandas" "requests" "sqlalchemy")
for package in "${critical_packages[@]}"; do
    if python -c "import $package" &> /dev/null; then
        log_success "$package disponible"
    else
        log_error "$package no encontrado"
        exit 1
    fi
done

# Inicializar base de datos si es necesario
if [ "$INIT_DATABASE" = "true" ]; then
    log "Inicializando base de datos..."
    python -c "
from src.database.database import Database
try:
    db = Database()
    db.initialize()
    print('✅ Base de datos inicializada')
except Exception as e:
    print(f'❌ Error inicializando BD: {e}')
    exit(1)
"
fi

# Verificar configuración de trading
log "Verificando configuración de trading..."
if [ -z "$BINANCE_API_KEY" ] && [ "$TESTNET" != "true" ]; then
    log_warning "BINANCE_API_KEY no configurada - usando modo demo"
fi

# Configurar timezone
if [ -n "$TZ" ]; then
    log "Configurando timezone: $TZ"
    ln -snf "/usr/share/zoneinfo/$TZ" /etc/localtime
    echo "$TZ" > /etc/timezone
fi

# Configurar logging
log "Configurando sistema de logging..."
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Función de cleanup para señales
cleanup() {
    log "Recibida señal de terminación, cerrando sistema..."
    if [ -n "$MAIN_PID" ]; then
        kill -TERM "$MAIN_PID" 2>/dev/null || true
        wait "$MAIN_PID" 2>/dev/null || true
    fi
    log_success "Sistema cerrado correctamente"
    exit 0
}

# Configurar manejo de señales
trap cleanup SIGTERM SIGINT SIGQUIT

# Función de health check
start_health_check() {
    if [ "$ENABLE_HEALTH_CHECK" = "true" ]; then
        (
            sleep 30  # Esperar a que el sistema inicie
            while true; do
                if ! python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" &> /dev/null; then
                    log_error "Health check falló"
                fi
                sleep 30
            done
        ) &
        HEALTH_PID=$!
        log_success "Health check iniciado (PID: $HEALTH_PID)"
    fi
}

# Mostrar información del sistema
log "Información del sistema:"
echo "  - Hostname: $(hostname)"
echo "  - Usuario: $(whoami)"
echo "  - Directorio: $(pwd)"
echo "  - Python: $(python --version)"
echo "  - Timezone: $(date +%Z)"
echo "  - Memoria: $(free -h | grep Mem | awk '{print $2}') disponible"

# Verificar modo de ejecución
if [ "$1" = "--test" ]; then
    log "Ejecutando en modo TEST"
    python -m pytest tests/ -v
    exit $?
elif [ "$1" = "--monitor" ]; then
    log "Ejecutando en modo MONITOR"
    exec python src/monitoring/trading_monitor.py
elif [ "$1" = "--shell" ]; then
    log "Iniciando shell interactivo"
    exec /bin/bash
fi

# Iniciar health check en background
start_health_check

# Mensaje final antes de iniciar
log_success "Sistema inicializado correctamente"
log "Iniciando aplicación principal..."
echo ""

# Ejecutar comando principal
if [ $# -eq 0 ]; then
    # Sin argumentos, ejecutar aplicación principal
    exec python main.py
else
    # Con argumentos, ejecutar comando especificado
    exec "$@"
fi