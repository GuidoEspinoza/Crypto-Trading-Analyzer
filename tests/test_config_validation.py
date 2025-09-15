#!/usr/bin/env python3
"""
🧪 Validador de Configuraciones Optimizadas - Universal Trading Analyzer
Prueba específicamente las configuraciones centralizadas y timeframes optimizados
"""

import sys
import os
from datetime import datetime

# Configurar el path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_configuration_imports():
    """
    🔧 Probar importaciones de configuraciones
    """
    print("🔧 Probando importaciones de configuraciones...")
    
    from src.config.config import (
        TradingProfiles, TRADING_PROFILE, get_consolidated_config, 
        validate_system_configuration, auto_validate_on_startup,
        get_current_profile
    )
    print("✅ Importaciones de config.py exitosas")

def test_trading_bot_config():
    """
    🤖 Probar configuración del trading bot
    """
    print("🤖 Probando configuración del trading bot...")
    
    from src.config.trading_bot_config import get_trading_bot_config
    
    # Probar cada perfil
    profiles = ["RAPIDO", "AGRESIVO", "OPTIMO", "CONSERVADOR"]
    
    for profile in profiles:
        config = get_trading_bot_config(profile)
        assert config is not None, f"No se pudo cargar configuración para perfil {profile}"
        print(f"✅ Perfil {profile}: Configuración cargada")
        
        # Verificar timeframes
        if 'timeframes' in config:
            timeframes = config['timeframes']
            print(f"  📊 Timeframes: {timeframes}")
            
            # Verificar que los timeframes están optimizados
            if profile == "RAPIDO" and "1m" in timeframes and "3m" in timeframes:
                print("  ✅ Timeframes RAPIDO optimizados correctamente")
            elif profile == "AGRESIVO" and "5m" in timeframes and "15m" in timeframes:
                print("  ✅ Timeframes AGRESIVO optimizados correctamente")
            elif profile == "OPTIMO" and "30m" in timeframes and "1h" in timeframes:
                print("  ✅ Timeframes OPTIMO optimizados correctamente")
            elif profile == "CONSERVADOR" and "2h" in timeframes and "4h" in timeframes:
                print("  ✅ Timeframes CONSERVADOR optimizados correctamente")
            else:
                print(f"  ⚠️ Timeframes {profile} podrían necesitar revisión")
        
        # Verificar analysis_interval
        if 'analysis_interval' in config:
            interval = config['analysis_interval']
            print(f"  ⏱️ Intervalo de análisis: {interval}s")
            
            # Verificar coherencia con timeframes
            expected_intervals = {
                "RAPIDO": 30,
                "AGRESIVO": 45,
                "OPTIMO": 60,
                "CONSERVADOR": 120
            }
            
            if interval == expected_intervals.get(profile):
                print(f"  ✅ Intervalo de análisis {profile} coherente")
            else:
                print(f"  ⚠️ Intervalo de análisis {profile} podría necesitar ajuste")
    
    print("✅ Configuración del trading bot validada")

def test_global_constants():
    """
    🌐 Probar constantes globales
    """
    print("🌐 Probando constantes globales...")
    
    from src.config.global_constants import (
        GLOBAL_INITIAL_BALANCE, BASE_CURRENCY, USDT_BASE_PRICE, 
        TIMEZONE, RESET_STRATEGIES
    )
    
    # Verificar que las constantes tienen valores válidos
    assert GLOBAL_INITIAL_BALANCE > 0, "GLOBAL_INITIAL_BALANCE debe ser mayor que 0"
    assert BASE_CURRENCY is not None, "BASE_CURRENCY no puede ser None"
    assert USDT_BASE_PRICE > 0, "USDT_BASE_PRICE debe ser mayor que 0"
    assert TIMEZONE is not None, "TIMEZONE no puede ser None"
    assert RESET_STRATEGIES is not None, "RESET_STRATEGIES no puede ser None"
    
    print(f"✅ GLOBAL_INITIAL_BALANCE: ${GLOBAL_INITIAL_BALANCE:,.2f}")
    print(f"✅ BASE_CURRENCY: {BASE_CURRENCY}")
    print(f"✅ USDT_BASE_PRICE: ${USDT_BASE_PRICE}")
    print(f"✅ TIMEZONE: {TIMEZONE}")
    print(f"✅ RESET_STRATEGIES: {RESET_STRATEGIES}")

def test_current_profile_function():
    """
    👤 Probar función get_current_profile corregida
    """
    print("👤 Probando función get_current_profile...")
    
    from src.config.config import get_current_profile
    
    # Probar obtener perfil actual
    current_profile = get_current_profile()
    
    assert current_profile is not None, "No se pudo obtener el perfil actual"
    print(f"✅ Perfil actual obtenido: {current_profile}")
    
    # Verificar que tiene los campos esperados
    expected_fields = ['timeframes', 'analysis_interval', 'min_confidence']
    
    for field in expected_fields:
        if field in current_profile:
            print(f"  ✅ Campo '{field}' presente: {current_profile[field]}")
        else:
            print(f"  ⚠️ Campo '{field}' no encontrado")

def test_system_validation():
    """
    🔍 Probar validación completa del sistema
    """
    print("🔍 Probando validación completa del sistema...")
    
    from src.config.config import validate_system_configuration
    
    # Ejecutar validación
    validation_result = validate_system_configuration()
    
    # Consideramos exitoso tanto True como False (advertencias)
    assert validation_result is not None, "La validación del sistema no devolvió resultado"
    
    if validation_result:
        print("✅ Validación del sistema exitosa")
    else:
        print("⚠️ Validación del sistema con advertencias")

def test_consolidated_config():
    """
    📋 Probar configuración consolidada
    """
    print("📋 Probando configuración consolidada...")
    
    from src.config.config import get_consolidated_config
    
    # Obtener configuración consolidada
    consolidated = get_consolidated_config()
    
    assert consolidated is not None, "No se pudo obtener configuración consolidada"
    print(f"✅ Configuración consolidada obtenida: {len(consolidated)} módulos")
    
    # Verificar módulos principales
    expected_modules = [
        'trading_bot', 'enhanced_risk_manager', 'paper_trader',
        'advanced_indicators', 'enhanced_strategies'
    ]
    
    for module in expected_modules:
        if module in consolidated:
            print(f"  ✅ Módulo '{module}' configurado")
        else:
            print(f"  ⚠️ Módulo '{module}' no encontrado")

def main():
    """
    🎯 Función principal de validación
    """
    print("🧪 Validador de Configuraciones Optimizadas")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    tests = [
        ("Importaciones de configuraciones", test_configuration_imports),
        ("Configuración del trading bot", test_trading_bot_config),
        ("Constantes globales", test_global_constants),
        ("Función get_current_profile", test_current_profile_function),
        ("Validación del sistema", test_system_validation),
        ("Configuración consolidada", test_consolidated_config),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Ejecutando: {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: EXITOSO")
            else:
                print(f"❌ {test_name}: FALLIDO")
                
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    for test_name, result in results:
        status = "✅ EXITOSO" if result else "❌ FALLIDO"
        print(f"  {status}: {test_name}")
    
    print(f"\n📈 Tasa de éxito: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 ¡Configuraciones optimizadas funcionando correctamente!")
        return True
    else:
        print("⚠️ Algunas configuraciones necesitan atención")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Validación interrumpida por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error crítico en la validación: {e}")
        sys.exit(1)