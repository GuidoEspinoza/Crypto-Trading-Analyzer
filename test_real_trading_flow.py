#!/usr/bin/env python3
"""
Script de prueba para verificar el flujo completo de trading real con Capital.com
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.trading_bot import TradingBot
from src.core.capital_client import create_capital_client_from_env
from src.config.main_config import GLOBAL_SYMBOLS

def test_capital_connection():
    """Prueba la conexión con Capital.com"""
    print("🔗 Probando conexión con Capital.com...")
    
    try:
        # Verificar variables de entorno primero
        required_vars = ['X-CAP-API-KEY', 'identifier', 'password']
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
            return False
        
        print("✅ Variables de entorno configuradas correctamente")
        
        client = create_capital_client_from_env()
        if client is None:
            print("❌ Error: No se pudo crear el cliente de Capital.com")
            return False
            
        print("✅ Cliente de Capital.com creado")
        
        # Probar crear sesión primero
        print("🔐 Creando sesión...")
        session_result = client.create_session()
        if not session_result.get("success"):
            print(f"❌ Error al crear sesión: {session_result.get('error')}")
            return False
            
        print("✅ Sesión creada exitosamente")
        
        # Probar obtener balance
        print("💰 Obteniendo balance...")
        balance_result = client.get_available_balance()
        if balance_result and 'available' in balance_result:
            balance = balance_result.get("available", 0)
            print(f"✅ Conexión exitosa. Balance disponible: ${balance:.2f}")
            return True
        else:
            print(f"❌ Error al obtener balance: {balance_result}")
            return False
            
    except Exception as e:
        print(f"❌ Error de conexión: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_bot_initialization():
    """Prueba la inicialización del bot con trading real"""
    print("\n🤖 Probando inicialización del bot...")
    
    try:
        # Temporalmente habilitar trading real para la prueba
        original_value = os.getenv('ENABLE_REAL_TRADING')
        os.environ['ENABLE_REAL_TRADING'] = 'true'
        
        bot = TradingBot(analysis_interval_minutes=1)
        
        print(f"✅ Bot inicializado correctamente")
        print(f"   - Trading real habilitado: {bot.enable_real_trading}")
        print(f"   - Cliente Capital.com: {'✅' if bot.capital_client else '❌'}")
        print(f"   - Símbolos configurados: {len(GLOBAL_SYMBOLS)}")
        
        # Restaurar valor original
        if original_value:
            os.environ['ENABLE_REAL_TRADING'] = original_value
        else:
            os.environ.pop('ENABLE_REAL_TRADING', None)
            
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar bot: {str(e)}")
        return False

def test_signal_generation():
    """Prueba la generación de señales"""
    print("\n📊 Probando generación de señales...")
    
    try:
        bot = TradingBot(analysis_interval_minutes=1)
        
        # Analizar un símbolo específico
        test_symbol = "BTCUSD"
        print(f"   Analizando {test_symbol}...")
        
        # Ejecutar análisis
        signals = bot._analyze_symbols_sequential()
        
        if signals:
            print(f"✅ Se generaron {len(signals)} señales:")
            for signal in signals[:3]:  # Mostrar solo las primeras 3
                confidence = getattr(signal, 'confidence_score', 0)
                print(f"   - {signal.symbol}: {signal.signal_type} (confianza: {confidence:.2f})")
                if hasattr(signal, 'stop_loss_price') and signal.stop_loss_price:
                    print(f"     SL: ${signal.stop_loss_price:.4f}")
                if hasattr(signal, 'take_profit_price') and signal.take_profit_price:
                    print(f"     TP: ${signal.take_profit_price:.4f}")
        else:
            print("⚠️ No se generaron señales en este momento")
            
        return True
        
    except Exception as e:
        print(f"❌ Error al generar señales: {str(e)}")
        return False

def show_current_config():
    """Muestra la configuración actual"""
    print("\n⚙️ Configuración actual:")
    print(f"   - IS_DEMO: {os.getenv('IS_DEMO', 'True')}")
    print(f"   - ENABLE_REAL_TRADING: {os.getenv('ENABLE_REAL_TRADING', 'False')}")
    print(f"   - CAPITAL_LIVE_URL: {os.getenv('CAPITAL_LIVE_URL', 'No configurado')}")
    print(f"   - CAPITAL_DEMO_URL: {os.getenv('CAPITAL_DEMO_URL', 'No configurado')}")
    print(f"   - X-CAP-API-KEY: {'✅ Configurado' if os.getenv('X-CAP-API-KEY') else '❌ No configurado'}")

def main():
    """Función principal de prueba"""
    print("🚀 Iniciando pruebas del flujo de trading real")
    print("=" * 50)
    
    # Mostrar configuración
    show_current_config()
    
    # Ejecutar pruebas
    tests = [
        ("Conexión Capital.com", test_capital_connection),
        ("Inicialización del Bot", test_bot_initialization),
        ("Generación de Señales", test_signal_generation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 50)
    print("📋 RESUMEN DE PRUEBAS:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("\n🎉 ¡Todas las pruebas pasaron! El sistema está listo para trading real.")
        print("\n📝 Para habilitar trading real:")
        print("   1. Cambiar ENABLE_REAL_TRADING=True en .env")
        print("   2. Verificar que IS_DEMO esté configurado correctamente")
        print("   3. Ejecutar el bot normalmente")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisar la configuración antes de continuar.")

if __name__ == "__main__":
    main()