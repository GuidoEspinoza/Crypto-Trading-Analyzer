#!/bin/bash

# 📊 Smart Trading Bot - Script de Monitoreo y Mantenimiento
# Versión: 1.0
# Compatible con: Hostinger VPS

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.yml"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
BACKUP_DIR="$PROJECT_DIR/backups"

# Crear directorio de logs si no existe
mkdir -p "$(dirname "$LOG_FILE")"
mkdir -p "$BACKUP_DIR"

# Función para logging
log_message() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Función para mostrar banner
show_banner() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           📊 SMART TRADING BOT - MONITOR & CONTROL          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Función para verificar si Docker está corriendo
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker no está corriendo${NC}"
        return 1
    fi
    return 0
}

# Función para verificar si el bot está corriendo
check_bot_running() {
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        return 0
    else
        return 1
    fi
}

# Función para mostrar estado del sistema
show_system_status() {
    echo -e "${CYAN}=== 🖥️  ESTADO DEL SISTEMA ===${NC}"
    
    # Información básica del sistema
    echo -e "${BLUE}Sistema:${NC} $(lsb_release -d 2>/dev/null | cut -f2 || echo "Unknown")"
    echo -e "${BLUE}Uptime:${NC} $(uptime -p 2>/dev/null || echo "Unknown")"
    echo -e "${BLUE}Fecha:${NC} $(date)"
    
    # CPU
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 2>/dev/null || echo "0")
    if (( $(echo "$CPU_USAGE > 80" | bc -l 2>/dev/null || echo 0) )); then
        echo -e "${BLUE}CPU:${NC} ${RED}${CPU_USAGE}%${NC} ⚠️"
    elif (( $(echo "$CPU_USAGE > 60" | bc -l 2>/dev/null || echo 0) )); then
        echo -e "${BLUE}CPU:${NC} ${YELLOW}${CPU_USAGE}%${NC}"
    else
        echo -e "${BLUE}CPU:${NC} ${GREEN}${CPU_USAGE}%${NC}"
    fi
    
    # RAM
    RAM_INFO=$(free | grep Mem)
    RAM_USED=$(echo $RAM_INFO | awk '{printf("%.1f", $3/$2 * 100.0)}')
    RAM_TOTAL=$(echo $RAM_INFO | awk '{printf("%.1f", $2/1024/1024)}')
    RAM_USED_GB=$(echo $RAM_INFO | awk '{printf("%.1f", $3/1024/1024)}')
    
    if (( $(echo "$RAM_USED > 85" | bc -l 2>/dev/null || echo 0) )); then
        echo -e "${BLUE}RAM:${NC} ${RED}${RAM_USED}%${NC} (${RAM_USED_GB}GB/${RAM_TOTAL}GB) ⚠️"
    elif (( $(echo "$RAM_USED > 70" | bc -l 2>/dev/null || echo 0) )); then
        echo -e "${BLUE}RAM:${NC} ${YELLOW}${RAM_USED}%${NC} (${RAM_USED_GB}GB/${RAM_TOTAL}GB)"
    else
        echo -e "${BLUE}RAM:${NC} ${GREEN}${RAM_USED}%${NC} (${RAM_USED_GB}GB/${RAM_TOTAL}GB)"
    fi
    
    # Disco
    DISK_USAGE=$(df -h / | awk 'NR==2{print $5}' | sed 's/%//')
    DISK_INFO=$(df -h / | awk 'NR==2{print $3"/"$2}')
    
    if (( DISK_USAGE > 85 )); then
        echo -e "${BLUE}Disco:${NC} ${RED}${DISK_USAGE}%${NC} (${DISK_INFO}) ⚠️"
    elif (( DISK_USAGE > 70 )); then
        echo -e "${BLUE}Disco:${NC} ${YELLOW}${DISK_USAGE}%${NC} (${DISK_INFO})"
    else
        echo -e "${BLUE}Disco:${NC} ${GREEN}${DISK_USAGE}%${NC} (${DISK_INFO})"
    fi
    
    # Load Average
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    echo -e "${BLUE}Load Avg:${NC} ${LOAD_AVG}"
    
    echo ""
}

# Función para mostrar estado de Docker
show_docker_status() {
    echo -e "${CYAN}=== 🐳 ESTADO DE DOCKER ===${NC}"
    
    if check_docker; then
        echo -e "${GREEN}✅ Docker está corriendo${NC}"
        
        # Mostrar contenedores del trading bot
        if [ -f "$COMPOSE_FILE" ]; then
            echo -e "\n${BLUE}Contenedores del Trading Bot:${NC}"
            docker-compose -f "$COMPOSE_FILE" ps
        else
            echo -e "${YELLOW}⚠️ Archivo docker-compose.yml no encontrado en $COMPOSE_FILE${NC}"
        fi
        
        # Estadísticas de Docker
        echo -e "\n${BLUE}Estadísticas de recursos:${NC}"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}" 2>/dev/null | head -10
        
    else
        echo -e "${RED}❌ Docker no está corriendo${NC}"
    fi
    
    echo ""
}

# Función para mostrar estado del trading bot
show_bot_status() {
    echo -e "${CYAN}=== 🤖 ESTADO DEL TRADING BOT ===${NC}"
    
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ docker-compose.yml no encontrado${NC}"
        return 1
    fi
    
    if check_bot_running; then
        echo -e "${GREEN}✅ Trading Bot está corriendo${NC}"
        
        # Health check
        echo -e "\n${BLUE}Health Check:${NC}"
        HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
        
        case $HEALTH_STATUS in
            200)
                echo -e "${GREEN}✅ API respondiendo correctamente (HTTP $HEALTH_STATUS)${NC}"
                ;;
            000)
                echo -e "${RED}❌ No se puede conectar a la API${NC}"
                ;;
            *)
                echo -e "${YELLOW}⚠️ API respondiendo con código $HEALTH_STATUS${NC}"
                ;;
        esac
        
        # Mostrar logs recientes
        echo -e "\n${BLUE}Últimas 5 líneas de logs:${NC}"
        docker-compose -f "$COMPOSE_FILE" logs --tail=5 trading-bot 2>/dev/null | sed 's/^/  /'
        
    else
        echo -e "${RED}❌ Trading Bot NO está corriendo${NC}"
    fi
    
    echo ""
}

# Función para mostrar conectividad
show_connectivity() {
    echo -e "${CYAN}=== 🌐 CONECTIVIDAD ===${NC}"
    
    # Test de conectividad básica
    if ping -c 1 google.com >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Conectividad a Internet${NC}"
    else
        echo -e "${RED}❌ Sin conectividad a Internet${NC}"
    fi
    
    # Test de Capital.com API
    if curl -s --max-time 5 https://api-capital.backend-capital.com >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Capital.com API accesible${NC}"
    else
        echo -e "${RED}❌ Capital.com API no accesible${NC}"
    fi
    
    # Puertos abiertos
    echo -e "\n${BLUE}Puertos abiertos:${NC}"
    netstat -tlnp 2>/dev/null | grep -E ':(80|443|8000)' | while read line; do
        echo "  $line"
    done
    
    echo ""
}

# Función para mostrar logs
show_logs() {
    local lines=${1:-50}
    echo -e "${CYAN}=== 📝 LOGS DEL TRADING BOT (últimas $lines líneas) ===${NC}"
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" logs --tail=$lines trading-bot
    else
        echo -e "${RED}❌ docker-compose.yml no encontrado${NC}"
    fi
}

# Función para reiniciar el bot
restart_bot() {
    echo -e "${YELLOW}🔄 Reiniciando Trading Bot...${NC}"
    log_message "Reiniciando Trading Bot..."
    
    if [ -f "$COMPOSE_FILE" ]; then
        docker-compose -f "$COMPOSE_FILE" restart
        sleep 5
        
        if check_bot_running; then
            echo -e "${GREEN}✅ Trading Bot reiniciado correctamente${NC}"
            log_message "Trading Bot reiniciado correctamente"
        else
            echo -e "${RED}❌ Error al reiniciar Trading Bot${NC}"
            log_message "Error al reiniciar Trading Bot"
        fi
    else
        echo -e "${RED}❌ docker-compose.yml no encontrado${NC}"
    fi
}

# Función para actualizar el bot
update_bot() {
    echo -e "${YELLOW}📥 Actualizando Trading Bot...${NC}"
    log_message "Iniciando actualización del Trading Bot..."
    
    cd "$PROJECT_DIR"
    
    # Verificar si es un repositorio git
    if [ ! -d ".git" ]; then
        echo -e "${RED}❌ No es un repositorio Git${NC}"
        return 1
    fi
    
    # Hacer backup antes de actualizar
    echo -e "${BLUE}📦 Creando backup antes de actualizar...${NC}"
    backup_bot
    
    # Actualizar código
    echo -e "${BLUE}📥 Descargando últimos cambios...${NC}"
    git fetch origin
    git pull origin main
    
    # Reconstruir contenedores
    echo -e "${BLUE}🔨 Reconstruyendo contenedores...${NC}"
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Reiniciar servicios
    echo -e "${BLUE}🚀 Reiniciando servicios...${NC}"
    docker-compose -f "$COMPOSE_FILE" up -d
    
    sleep 10
    
    if check_bot_running; then
        echo -e "${GREEN}✅ Trading Bot actualizado correctamente${NC}"
        log_message "Trading Bot actualizado correctamente"
    else
        echo -e "${RED}❌ Error en la actualización${NC}"
        log_message "Error en la actualización del Trading Bot"
    fi
}

# Función para crear backup
backup_bot() {
    echo -e "${YELLOW}💾 Creando backup del Trading Bot...${NC}"
    
    local DATE=$(date +%Y%m%d_%H%M%S)
    local BACKUP_FILE="$BACKUP_DIR/trading-bot-backup-$DATE.tar.gz"
    
    echo "Creando backup en $BACKUP_FILE..."
    
    # Crear backup excluyendo archivos innecesarios
    tar -czf "$BACKUP_FILE" \
        --exclude='logs/*' \
        --exclude='backups/*' \
        --exclude='.git/*' \
        --exclude='__pycache__/*' \
        --exclude='*.pyc' \
        -C "$(dirname "$PROJECT_DIR")" \
        "$(basename "$PROJECT_DIR")"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Backup creado: $BACKUP_FILE${NC}"
        ls -lh "$BACKUP_FILE"
        
        # Mantener solo los últimos 7 backups
        find "$BACKUP_DIR" -name "trading-bot-backup-*.tar.gz" -type f -mtime +7 -delete
        
        log_message "Backup creado: $BACKUP_FILE"
    else
        echo -e "${RED}❌ Error al crear backup${NC}"
        log_message "Error al crear backup"
    fi
}

# Función para limpiar sistema
cleanup_system() {
    echo -e "${YELLOW}🧹 Limpiando sistema...${NC}"
    log_message "Iniciando limpieza del sistema..."
    
    # Limpiar Docker
    echo -e "${BLUE}🐳 Limpiando Docker...${NC}"
    docker system prune -f
    docker volume prune -f
    
    # Limpiar logs antiguos
    echo -e "${BLUE}📝 Limpiando logs antiguos...${NC}"
    find "$PROJECT_DIR/logs" -name "*.log" -type f -mtime +30 -delete 2>/dev/null || true
    
    # Limpiar backups antiguos
    echo -e "${BLUE}💾 Limpiando backups antiguos...${NC}"
    find "$BACKUP_DIR" -name "*.tar.gz" -type f -mtime +30 -delete 2>/dev/null || true
    
    echo -e "${GREEN}✅ Limpieza completada${NC}"
    log_message "Limpieza del sistema completada"
}

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}📖 AYUDA - Smart Trading Bot Monitor${NC}"
    echo ""
    echo "Uso: $0 [COMANDO]"
    echo ""
    echo "COMANDOS DISPONIBLES:"
    echo "  status      - Mostrar estado completo del sistema y bot"
    echo "  logs [N]    - Mostrar logs del bot (N líneas, default: 50)"
    echo "  restart     - Reiniciar el trading bot"
    echo "  update      - Actualizar código y reiniciar bot"
    echo "  backup      - Crear backup manual del bot"
    echo "  cleanup     - Limpiar sistema (Docker, logs, backups antiguos)"
    echo "  health      - Solo verificar health del bot"
    echo "  help        - Mostrar esta ayuda"
    echo ""
    echo "EJEMPLOS:"
    echo "  $0                    # Mostrar estado completo"
    echo "  $0 logs 100          # Mostrar últimas 100 líneas de logs"
    echo "  $0 restart           # Reiniciar bot"
    echo "  $0 update            # Actualizar y reiniciar"
    echo ""
}

# Función principal
main() {
    local command=${1:-status}
    
    case $command in
        "status")
            show_banner
            show_system_status
            show_docker_status
            show_bot_status
            show_connectivity
            ;;
        "logs")
            local lines=${2:-50}
            show_logs $lines
            ;;
        "restart")
            show_banner
            restart_bot
            ;;
        "update")
            show_banner
            update_bot
            ;;
        "backup")
            show_banner
            backup_bot
            ;;
        "cleanup")
            show_banner
            cleanup_system
            ;;
        "health")
            if check_bot_running; then
                HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null || echo "000")
                case $HEALTH_STATUS in
                    200)
                        echo -e "${GREEN}✅ Bot saludable (HTTP $HEALTH_STATUS)${NC}"
                        exit 0
                        ;;
                    *)
                        echo -e "${RED}❌ Bot no saludable (HTTP $HEALTH_STATUS)${NC}"
                        exit 1
                        ;;
                esac
            else
                echo -e "${RED}❌ Bot no está corriendo${NC}"
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}❌ Comando desconocido: $command${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Verificar dependencias básicas
if ! command -v docker >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    exit 1
fi

# Ejecutar función principal
main "$@"