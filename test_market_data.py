#!/usr/bin/env python3
"""🧪 Test script para verificar la nueva funcionalidad de datos de mercado de Capital.com"""

import sys
import os

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.capital_client import create_capital_client_from_env
from src.config.main_config import GLOBAL_SYMBOLS

def test_capital_connection():
    """🔗 Probar conexión con Capital.com"""
    print("🔗 Probando conexión con Capital.com...")
    
    try:
        client = create_capital_client_from_env()
        print(f"✅ Cliente Capital.com creado exitosamente")
        
        # Probar ping
        ping_result = client.ping()
        if ping_result.get("success"):
            print(f"✅ Ping exitoso: {ping_result.get('message', 'OK')}")
        else:
            print(f"❌ Ping falló: {ping_result}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Error creando cliente Capital.com: {e}")
        return False

def test_market_data():
    """📊 Probar obtención de datos de mercado"""
    print("\n📊 Probando obtención de datos de mercado...")
    
    try:
        client = create_capital_client_from_env()
        
        # Probar con algunos símbolos de GLOBAL_SYMBOLS
        test_symbols = ['GOLD', 'SILVER', 'NATURAL_GAS']
        available_symbols = [s for s in test_symbols if s in GLOBAL_SYMBOLS]
        
        if not available_symbols:
            print("⚠️ No hay símbolos de prueba disponibles en GLOBAL_SYMBOLS")
            return False
        
        print(f"🔍 Probando con símbolos: {available_symbols}")
        
        market_data = client.get_market_data(available_symbols)
        
        if market_data:
            print(f"✅ Datos de mercado obtenidos para {len(market_data)} símbolos:")
            for symbol, data in market_data.items():
                if data:
                    bid = data.get('bid', 'N/A')
                    offer = data.get('offer', 'N/A')
                    mid = data.get('mid', 'N/A')
                    status = data.get('market_status', 'N/A')
                    print(f"   📈 {symbol}: Bid={bid}, Offer={offer}, Mid={mid}, Status={status}")
                else:
                    print(f"   ❌ {symbol}: Sin datos")
            return True
        else:
            print("❌ No se obtuvieron datos de mercado")
            return False
            
    except Exception as e:
        print(f"❌ Error obteniendo datos de mercado: {e}")
        return False

def test_price_integration():
    """💰 Probar integración con el sistema de precios"""
    print("\n💰 Probando integración con el sistema de precios...")
    
    try:
        from src.database.database import db_manager
        
        # Probar algunos símbolos
        test_symbols = ['GOLD', 'SILVER']
        
        for symbol in test_symbols:
            if symbol in GLOBAL_SYMBOLS:
                print(f"🔍 Obteniendo precio para {symbol}...")
                price = db_manager._get_current_price(symbol)
                if price > 0:
                    print(f"   ✅ {symbol}: ${price:.4f}")
                else:
                    print(f"   ❌ {symbol}: Error obteniendo precio")
            else:
                print(f"   ⚠️ {symbol}: No está en GLOBAL_SYMBOLS")
                
        return True
        
    except Exception as e:
        print(f"❌ Error en integración de precios: {e}")
        return False

def main():
    """🚀 Función principal"""
    print("🧪 PRUEBA DE FUNCIONALIDAD DE DATOS DE MERCADO")
    print("=" * 50)
    
    # Mostrar símbolos disponibles
    print(f"📋 Símbolos disponibles en GLOBAL_SYMBOLS: {len(GLOBAL_SYMBOLS)}")
    print(f"   Primeros 10: {GLOBAL_SYMBOLS[:10]}")
    
    # Ejecutar pruebas
    tests = [
        ("Conexión Capital.com", test_capital_connection),
        ("Datos de mercado", test_market_data),
        ("Integración de precios", test_price_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en prueba {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n{'='*50}")
    print("📊 RESUMEN DE PRUEBAS:")
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 Resultado: {passed}/{total} pruebas pasaron")

if __name__ == "__main__":
    main()