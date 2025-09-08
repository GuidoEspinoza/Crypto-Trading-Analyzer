#!/usr/bin/env python3
"""
🧪 Script de prueba integral para TradingBot
"""

import sys
import os
import asyncio
import time
# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.core.trading_bot import TradingBot
from src.core.config import TradingBotConfig
import traceback

def test_trading_bot_initialization():
    """Probar inicialización del TradingBot"""
    print("🔍 Probando inicialización del TradingBot...")
    try:
        bot = TradingBot()
        print("✅ TradingBot inicializado correctamente")
        return bot
    except Exception as e:
        print(f"❌ Error inicializando TradingBot: {e}")
        traceback.print_exc()
        return None

def test_trading_bot_config():
    """Probar configuración del TradingBot"""
    print("\n🔍 Probando configuración del TradingBot...")
    try:
        # Verificar que la configuración se carga correctamente
        config = TradingBotConfig()
        symbols = config.SYMBOLS
        
        print(f"✅ Símbolos configurados: {len(symbols)}")
        print(f"✅ Símbolos: {symbols[:3]}...")  # Mostrar primeros 3
        
        if symbols:
            print("✅ Configuración válida")
            return True
        else:
            print("❌ Configuración incompleta")
            return False
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
        traceback.print_exc()
        return False

def test_trading_bot_analysis():
    """Probar análisis del TradingBot"""
    print("\n🔍 Probando análisis del TradingBot...")
    try:
        bot = TradingBot()
        
        print("📊 Ejecutando ciclo de análisis...")
        # Probar un ciclo de análisis completo
        bot._run_analysis_cycle()
        
        print("✅ Análisis completado")
        return True
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        traceback.print_exc()
        return False

def test_trading_bot_strategies():
    """Probar estrategias del TradingBot"""
    print("\n🔍 Probando estrategias del TradingBot...")
    try:
        bot = TradingBot()
        
        # Verificar que las estrategias se cargan
        if hasattr(bot, 'strategies') and bot.strategies:
            print(f"✅ Estrategias cargadas: {list(bot.strategies.keys())}")
            
            # Probar una estrategia
            test_symbol = "BTCUSDT"
            for strategy_name, strategy in bot.strategies.items():
                try:
                    print(f"🧠 Probando estrategia: {strategy_name}")
                    # Aquí podríamos probar la estrategia si tiene un método de prueba
                    print(f"✅ Estrategia {strategy_name} disponible")
                    break  # Solo probar una para no sobrecargar
                except Exception as e:
                    print(f"❌ Error en estrategia {strategy_name}: {e}")
            
            return True
        else:
            print("❌ No se encontraron estrategias")
            return False
    except Exception as e:
        print(f"❌ Error probando estrategias: {e}")
        traceback.print_exc()
        return False

def test_trading_bot_paper_trader():
    """Probar integración con PaperTrader"""
    print("\n🔍 Probando integración con PaperTrader...")
    try:
        bot = TradingBot()
        
        # Verificar que el paper trader está disponible
        if hasattr(bot, 'paper_trader') and bot.paper_trader:
            print("✅ PaperTrader integrado correctamente")
            return True
        else:
            print("❌ PaperTrader no encontrado")
            return False
    except Exception as e:
        print(f"❌ Error verificando PaperTrader: {e}")
        traceback.print_exc()
        return False

def main():
    """Ejecutar todas las pruebas del TradingBot"""
    print("🧪 INICIANDO PRUEBAS INTEGRALES DEL TRADING BOT")
    print("=" * 50)
    
    # Todas las pruebas son síncronas
    tests = [
        ("Inicialización", test_trading_bot_initialization),
        ("Configuración", test_trading_bot_config),
        ("Integración PaperTrader", test_trading_bot_paper_trader),
        ("Análisis de símbolos", test_trading_bot_analysis),
        ("Estrategias", test_trading_bot_strategies)
    ]
    
    results = []
    
    # Ejecutar todas las pruebas
    for test_name, test_func in tests:
        try:
            result = test_func()
            # Si retorna un objeto (como TradingBot), considerarlo exitoso
            if result is not None and not isinstance(result, bool):
                result = True
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas del TradingBot pasaron!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar errores arriba.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Pruebas interrumpidas por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        traceback.print_exc()
        sys.exit(1)