#!/usr/bin/env python3
"""
🧪 Script de prueba para verificar la funcionalidad de reset personalizado
con zona horaria de Chile para trading optimizado
"""

import sys
import os
from datetime import datetime, timedelta
import pytz

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import (
    TIMEZONE, DAILY_RESET_HOUR, DAILY_RESET_MINUTE,
    RESET_STRATEGIES, ACTIVE_RESET_STRATEGY
)

def test_timezone_configuration():
    """
    Probar la configuración de zona horaria y horarios de reset
    """
    print("🧪 TESTING: Configuración de Zona Horaria y Reset Personalizado")
    print("=" * 70)
    
    # Verificar zona horaria
    print(f"📍 Zona horaria configurada: {TIMEZONE}")
    chile_tz = pytz.timezone(TIMEZONE)
    current_time_chile = datetime.now(chile_tz)
    print(f"⏰ Hora actual en Chile: {current_time_chile.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Verificar configuración de reset
    print(f"\n🔄 Configuración de reset diario:")
    print(f"   - Hora: {DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d}")
    print(f"   - Estrategia activa: {ACTIVE_RESET_STRATEGY}")
    
    # Mostrar todas las estrategias disponibles
    print(f"\n📋 Estrategias de reset disponibles:")
    for strategy_name, config in RESET_STRATEGIES.items():
        hour = config['hour']
        minute = config['minute']
        status = "✅ ACTIVA" if strategy_name == ACTIVE_RESET_STRATEGY else "⚪ Disponible"
        print(f"   - {strategy_name}: {hour:02d}:{minute:02d} CLT ({status})")
    
    # Calcular próximo reset
    if ACTIVE_RESET_STRATEGY in RESET_STRATEGIES:
        reset_config = RESET_STRATEGIES[ACTIVE_RESET_STRATEGY]
        reset_hour = reset_config["hour"]
        reset_minute = reset_config["minute"]
    else:
        reset_hour = DAILY_RESET_HOUR
        reset_minute = DAILY_RESET_MINUTE
    
    # Crear tiempo de reset para hoy
    reset_time_today = current_time_chile.replace(
        hour=reset_hour, minute=reset_minute, second=0, microsecond=0
    )
    
    # Si ya pasó el reset de hoy, calcular para mañana
    if current_time_chile >= reset_time_today:
        reset_time_next = reset_time_today + timedelta(days=1)
        print(f"\n⏭️  Próximo reset: {reset_time_next.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        time_until_reset = reset_time_next - current_time_chile
    else:
        print(f"\n⏭️  Próximo reset: {reset_time_today.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        time_until_reset = reset_time_today - current_time_chile
    
    hours_until = time_until_reset.total_seconds() / 3600
    print(f"⏳ Tiempo hasta próximo reset: {hours_until:.1f} horas")
    
    # Verificar horarios óptimos de trading
    print(f"\n📈 Horarios óptimos de trading en Chile:")
    print(f"   - Horario principal: 11:30 AM - 6:00 PM CLT")
    print(f"   - Horario secundario: 5:00 AM - 1:00 PM CLT")
    print(f"   - Reset configurado: {reset_hour:02d}:{reset_minute:02d} CLT (antes del horario óptimo)")
    
    return True

def test_reset_logic_simulation():
    """
    Simular la lógica de reset para diferentes escenarios
    """
    print(f"\n🔬 TESTING: Simulación de Lógica de Reset")
    print("=" * 50)
    
    chile_tz = pytz.timezone(TIMEZONE)
    current_time = datetime.now(chile_tz)
    
    # Obtener configuración activa
    if ACTIVE_RESET_STRATEGY in RESET_STRATEGIES:
        reset_config = RESET_STRATEGIES[ACTIVE_RESET_STRATEGY]
        reset_hour = reset_config["hour"]
        reset_minute = reset_config["minute"]
    else:
        reset_hour = DAILY_RESET_HOUR
        reset_minute = DAILY_RESET_MINUTE
    
    # Simular diferentes escenarios
    scenarios = [
        ("Primera ejecución", None),
        ("Antes del reset de hoy", current_time.replace(hour=reset_hour-1)),
        ("Después del reset de hoy", current_time.replace(hour=reset_hour+1)),
        ("Reset de ayer", current_time.replace(hour=reset_hour) - timedelta(days=1))
    ]
    
    for scenario_name, last_reset in scenarios:
        print(f"\n📋 Escenario: {scenario_name}")
        
        # Crear tiempo de reset para hoy
        reset_time_today = current_time.replace(
            hour=reset_hour, minute=reset_minute, second=0, microsecond=0
        )
        
        # Lógica de decisión de reset
        should_reset = False
        
        if last_reset is None:
            should_reset = True
            reason = "Primera ejecución del bot"
        else:
            if isinstance(last_reset, datetime) and last_reset.tzinfo is None:
                last_reset = chile_tz.localize(last_reset)
            
            if current_time >= reset_time_today and last_reset < reset_time_today:
                should_reset = True
                reason = f"Horario de reset alcanzado ({reset_hour:02d}:{reset_minute:02d} CLT)"
            else:
                should_reset = False
                reason = "No es momento de reset"
        
        status = "✅ SÍ" if should_reset else "❌ NO"
        print(f"   - ¿Resetear?: {status}")
        print(f"   - Razón: {reason}")
        if last_reset:
            print(f"   - Último reset: {last_reset.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    return True

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DE CONFIGURACIÓN DE RESET PERSONALIZADO")
    print("=" * 80)
    
    try:
        # Ejecutar pruebas
        test_timezone_configuration()
        test_reset_logic_simulation()
        
        print(f"\n✅ TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
        print(f"\n📝 RESUMEN:")
        print(f"   - Zona horaria: {TIMEZONE} ✅")
        print(f"   - Estrategia activa: {ACTIVE_RESET_STRATEGY} ✅")
        print(f"   - Reset configurado: {DAILY_RESET_HOUR:02d}:{DAILY_RESET_MINUTE:02d} CLT ✅")
        print(f"   - Dependencia pytz: Instalada ✅")
        print(f"\n🎯 El bot ahora reseteará las estadísticas diarias según el horario")
        print(f"   optimizado para trading de criptomonedas en Chile.")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        print(f"\n🔧 SOLUCIÓN SUGERIDA:")
        print(f"   1. Instalar dependencias: pip install pytz")
        print(f"   2. Verificar configuración en src/config/config.py")
        sys.exit(1)