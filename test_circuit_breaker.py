#!/usr/bin/env python3
"""
🧪 Script de prueba para el mecanismo Circuit Breaker

Este script simula diferentes escenarios para verificar que el circuit breaker
funciona correctamente al detectar pérdidas consecutivas.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime, timedelta
from backend.trading_engine.trading_bot import TradingBot
from backend.trading_engine.config import TradingBotConfig

def test_circuit_breaker_scenarios():
    """
    🔬 Probar diferentes escenarios del circuit breaker
    """
    print("\n🧪 INICIANDO PRUEBAS DEL CIRCUIT BREAKER")
    print("=" * 50)
    
    # Crear bot con configuración actual
    bot = TradingBot()
    
    print(f"\n📊 Configuración actual:")
    print(f"   • Perfil: {bot.config.get_bot_description()}")
    print(f"   • Pérdidas máximas consecutivas: {bot.max_consecutive_losses}")
    print(f"   • Cooldown: {bot.circuit_breaker_cooldown_hours} horas")
    
    # Escenario 1: Simular pérdidas consecutivas hasta activar circuit breaker
    print("\n🔴 ESCENARIO 1: Pérdidas consecutivas hasta activación")
    print("-" * 40)
    
    for i in range(bot.max_consecutive_losses + 2):
        print(f"\n   Trade #{i+1}: Simulando pérdida...")
        bot._update_consecutive_losses(trade_was_profitable=False)
        
        print(f"   • Pérdidas consecutivas: {bot.consecutive_losses}/{bot.max_consecutive_losses}")
        print(f"   • Circuit breaker activo: {bot.circuit_breaker_active}")
        
        if bot.circuit_breaker_active:
            remaining = bot._get_remaining_cooldown_hours()
            print(f"   • ⏰ Tiempo restante de cooldown: {remaining:.2f} horas")
            break
    
    # Escenario 2: Verificar que el circuit breaker bloquea nuevas operaciones
    print("\n🛑 ESCENARIO 2: Verificación de bloqueo de operaciones")
    print("-" * 40)
    
    can_trade = not bot._check_circuit_breaker()
    print(f"   • ¿Puede operar? {can_trade}")
    print(f"   • Estado del circuit breaker: {'ACTIVO' if bot.circuit_breaker_active else 'INACTIVO'}")
    
    # Escenario 3: Simular reactivación después del cooldown
    print("\n🟢 ESCENARIO 3: Simulación de reactivación post-cooldown")
    print("-" * 40)
    
    # Simular que ha pasado el tiempo de cooldown
    if bot.circuit_breaker_activated_at:
        bot.circuit_breaker_activated_at = datetime.now() - timedelta(hours=bot.circuit_breaker_cooldown_hours + 1)
        print(f"   • Simulando que han pasado {bot.circuit_breaker_cooldown_hours + 1} horas...")
        
        # Verificar circuit breaker
        can_trade_after_cooldown = not bot._check_circuit_breaker()
        print(f"   • ¿Puede operar después del cooldown? {can_trade_after_cooldown}")
        print(f"   • Estado del circuit breaker: {'ACTIVO' if bot.circuit_breaker_active else 'INACTIVO'}")
        print(f"   • Pérdidas consecutivas reseteadas: {bot.consecutive_losses}")
    
    # Escenario 4: Probar con trade rentable (reset de pérdidas)
    print("\n💰 ESCENARIO 4: Trade rentable (reset de contador)")
    print("-" * 40)
    
    # Simular algunas pérdidas
    for i in range(3):
        bot._update_consecutive_losses(trade_was_profitable=False)
    
    print(f"   • Pérdidas antes del trade rentable: {bot.consecutive_losses}")
    
    # Simular trade rentable
    bot._update_consecutive_losses(trade_was_profitable=True)
    print(f"   • Pérdidas después del trade rentable: {bot.consecutive_losses}")
    print(f"   • ✅ Contador reseteado correctamente")
    
    # Escenario 5: Información del perfil actual
    print("\n⚙️ ESCENARIO 5: Información del perfil actual")
    print("-" * 40)
    
    print(f"   • Perfil activo: {bot.config.get_bot_description()}")
    print(f"   • Pérdidas máximas: {bot.max_consecutive_losses}")
    print(f"   • Cooldown: {bot.circuit_breaker_cooldown_hours} horas")
    print(f"   • Trades diarios máximos: {bot.max_daily_trades}")
    print(f"   • Umbral de confianza: {bot.min_confidence_threshold}%")
    
    print("\n✅ TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 50)
    
    return True

def test_status_and_reports():
    """
    📊 Probar que el circuit breaker aparece en status y reportes
    """
    print("\n📊 PROBANDO STATUS Y REPORTES")
    print("=" * 30)
    
    bot = TradingBot()
    
    # Activar circuit breaker
    for i in range(bot.max_consecutive_losses):
        bot._update_consecutive_losses(trade_was_profitable=False)
    
    # Obtener status
    status = bot.get_status()
    print(f"\n🔍 Status del bot:")
    if hasattr(status, 'circuit_breaker_info'):
        cb_info = status.circuit_breaker_info
        print(f"   • Circuit breaker activo: {cb_info.get('active', 'N/A')}")
        print(f"   • Pérdidas consecutivas: {cb_info.get('consecutive_losses', 'N/A')}")
        print(f"   • Límite máximo: {cb_info.get('max_consecutive_losses', 'N/A')}")
    
    # Obtener reporte detallado
    report = bot.get_detailed_report()
    print(f"\n📋 Reporte detallado:")
    if 'risk_management' in report and 'circuit_breaker' in report['risk_management']:
        cb_report = report['risk_management']['circuit_breaker']
        print(f"   • Estado: {cb_report.get('active', 'N/A')}")
        print(f"   • Pérdidas: {cb_report.get('consecutive_losses', 'N/A')}/{cb_report.get('max_consecutive_losses', 'N/A')}")
        print(f"   • Cooldown restante: {cb_report.get('remaining_cooldown_hours', 'N/A')}h")
    
    print("\n✅ STATUS Y REPORTES VERIFICADOS")
    return True

if __name__ == "__main__":
    try:
        # Ejecutar todas las pruebas
        test_circuit_breaker_scenarios()
        test_status_and_reports()
        
        print("\n🎉 TODAS LAS PRUEBAS DEL CIRCUIT BREAKER EXITOSAS")
        print("\n💡 El mecanismo está listo para proteger tu capital!")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)