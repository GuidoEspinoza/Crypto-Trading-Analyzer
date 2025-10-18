#!/usr/bin/env python3
"""
🚀 Test Real Trading Setup
Script para verificar que el trading real está configurado correctamente
"""

import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_environment_variables():
    """Verificar que las variables de entorno estén configuradas correctamente"""
    print("🔍 Verificando variables de entorno...")
    
    enable_real_trading = os.getenv('ENABLE_REAL_TRADING', 'False').lower() == 'true'
    is_demo = os.getenv('IS_DEMO', 'True').lower() == 'true'
    
    print(f"   • ENABLE_REAL_TRADING: {enable_real_trading}")
    print(f"   • IS_DEMO: {is_demo}")
    
    if enable_real_trading:
        print("   ✅ Trading real habilitado")
    else:
        print("   ❌ Trading real deshabilitado")
        return False
    
    # Verificar credenciales de Capital.com
    required_vars = [
        'CAPITAL_DEMO_URL',
        'identifier', 
        'password',
        'X-CAP-API-KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ Todas las credenciales de Capital.com están configuradas")
    
    return True

def test_trading_bot_configuration():
    """Verificar que el TradingBot esté configurado para trading real"""
    print("\n🤖 Verificando configuración del TradingBot...")
    
    try:
        from src.core.trading_bot import TradingBot
        from src.config.main_config import ENABLE_REAL_TRADING
        
        print(f"   • ENABLE_REAL_TRADING desde config: {ENABLE_REAL_TRADING}")
        
        # Crear instancia del bot
        bot = TradingBot()
        
        print(f"   • Bot enable_real_trading: {bot.enable_real_trading}")
        print(f"   • Bot tiene capital_client: {bot.capital_client is not None}")
        
        if bot.enable_real_trading:
            print("   ✅ TradingBot configurado para trading real")
            return True
        else:
            print("   ❌ TradingBot configurado para paper trading")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al verificar TradingBot: {e}")
        return False

def test_capital_connection():
    """Verificar conexión con Capital.com"""
    print("\n🔗 Verificando conexión con Capital.com...")
    
    try:
        from src.core.capital_client import create_capital_client_from_env
        
        # Crear cliente
        client = create_capital_client_from_env()
        
        # Crear sesión
        client.create_session()
        print("   ✅ Sesión creada exitosamente")
        
        # Verificar ping
        ping_result = client.ping()
        if ping_result and (ping_result.get('status') == 'OK' or ping_result.get('status') == 'connected'):
            print("   ✅ Ping exitoso")
        else:
            print(f"   ⚠️ Ping con resultado: {str(ping_result)}")
            # No fallar por el ping, continuar con el balance
        
        # Verificar balance
        balance_result = client.get_available_balance()
        if balance_result.get("success"):
            available_balance = balance_result.get("available", 0)
            print(f"   ✅ Balance obtenido: ${available_balance:,.2f}")
        else:
            print(f"   ⚠️ Error obteniendo balance: {balance_result.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")
        return False

def test_main_py_endpoint():
    """Verificar que main.py esté configurado correctamente"""
    print("\n🌐 Verificando configuración de main.py...")
    
    try:
        # Importar las funciones de main.py
        import main
        
        # Verificar que get_trading_bot funcione
        bot = main.get_trading_bot()
        print(f"   • Bot desde main.py enable_real_trading: {bot.enable_real_trading}")
        
        if bot.enable_real_trading:
            print("   ✅ main.py configurado para trading real")
            return True
        else:
            print("   ❌ main.py configurado para paper trading")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al verificar main.py: {e}")
        return False

def test_live_trading_bot():
    """Verificar que live_trading_bot.py esté configurado correctamente"""
    print("\n🔴 Verificando configuración de live_trading_bot.py...")
    
    try:
        from src.tools.live_trading_bot import LiveTradingBot
        
        # Crear instancia
        live_bot = LiveTradingBot()
        
        # Verificar configuración del bot interno
        internal_bot = live_bot.trading_bot
        print(f"   • LiveTradingBot internal bot enable_real_trading: {internal_bot.enable_real_trading}")
        
        if internal_bot.enable_real_trading:
            print("   ✅ live_trading_bot.py configurado para trading real")
            return True
        else:
            print("   ❌ live_trading_bot.py configurado para paper trading")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al verificar live_trading_bot.py: {e}")
        return False

def main():
    """Ejecutar todas las pruebas"""
    print("🚀 VERIFICACIÓN DE CONFIGURACIÓN DE TRADING REAL")
    print("=" * 60)
    
    tests = [
        ("Variables de entorno", test_environment_variables),
        ("Configuración TradingBot", test_trading_bot_configuration),
        ("Conexión Capital.com", test_capital_connection),
        ("Configuración main.py", test_main_py_endpoint),
        ("Configuración live_trading_bot.py", test_live_trading_bot)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ Error en {test_name}: {e}")
            results[test_name] = False
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} {test_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        print("🚀 El sistema está listo para trading real")
        print("\n📋 INSTRUCCIONES:")
        print("   1. Para usar main.py: python3 main.py y luego POST /bot/start")
        print("   2. Para usar live_trading_bot: python3 src/tools/live_trading_bot.py")
        print("   3. Ambos ejecutarán trades reales en Capital.com")
    else:
        print("⚠️ ALGUNAS PRUEBAS FALLARON")
        print("🔧 Revisa la configuración antes de continuar")
    
    return all_passed

if __name__ == "__main__":
    main()