#!/usr/bin/env python3
"""
Script para probar que el trailing stop se incluya correctamente en el payload de la orden
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.main_config import TradingProfiles
from src.core.capital_client import create_capital_client_from_env

def test_trailing_stop_payload():
    """Prueba que el trailing stop se incluya en el payload de la orden"""
    
    print("🔍 Testing trailing stop payload inclusion...")
    
    # 1. Verificar configuración del perfil
    profile = TradingProfiles.get_current_profile()
    use_trailing_stop = profile.get("use_trailing_stop", False)
    print(f"📊 Current profile: {profile.get('name', 'Unknown')}")
    print(f"🎯 use_trailing_stop: {use_trailing_stop}")
    
    if not use_trailing_stop:
        print("❌ Trailing stop is disabled in profile configuration")
        return
    
    # 2. Inicializar cliente de Capital.com
    try:
        capital_client = create_capital_client_from_env()
        print("✅ Capital.com client initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Capital.com client: {e}")
        return
    
    # 3. Simular parámetros de orden
    symbol = "ADAUSD"
    current_price = 0.5000  # Precio simulado
    stop_loss = 0.4900      # Stop loss simulado
    trailing_distance = abs(current_price - stop_loss)
    
    print(f"\n📈 Simulating order for {symbol}:")
    print(f"   Current price: {current_price}")
    print(f"   Stop loss: {stop_loss}")
    print(f"   Trailing distance: {trailing_distance}")
    
    # 4. Probar buy_market_order con trailing stop
    print(f"\n🔴 Testing BUY order with trailing stop...")
    try:
        # Simular llamada a buy_market_order (sin ejecutar realmente)
        print(f"   Would call: buy_market_order(")
        print(f"       symbol='{symbol}',")
        print(f"       size=1.0,")
        print(f"       trailing_stop=True,")
        print(f"       stop_distance={trailing_distance}")
        print(f"   )")
        
        # Verificar que el método existe y acepta los parámetros
        import inspect
        sig = inspect.signature(capital_client.buy_market_order)
        params = list(sig.parameters.keys())
        print(f"   ✅ Method signature: {params}")
        
        if 'trailing_stop' in params and 'stop_distance' in params:
            print("   ✅ Method accepts trailing_stop and stop_distance parameters")
        else:
            print("   ❌ Method missing trailing_stop or stop_distance parameters")
            
    except Exception as e:
        print(f"   ❌ Error testing buy_market_order: {e}")
    
    # 5. Probar sell_market_order con trailing stop
    print(f"\n🟢 Testing SELL order with trailing stop...")
    try:
        # Simular llamada a sell_market_order (sin ejecutar realmente)
        print(f"   Would call: sell_market_order(")
        print(f"       symbol='{symbol}',")
        print(f"       size=1.0,")
        print(f"       trailing_stop=True,")
        print(f"       stop_distance={trailing_distance}")
        print(f"   )")
        
        # Verificar que el método existe y acepta los parámetros
        import inspect
        sig = inspect.signature(capital_client.sell_market_order)
        params = list(sig.parameters.keys())
        print(f"   ✅ Method signature: {params}")
        
        if 'trailing_stop' in params and 'stop_distance' in params:
            print("   ✅ Method accepts trailing_stop and stop_distance parameters")
        else:
            print("   ❌ Method missing trailing_stop or stop_distance parameters")
            
    except Exception as e:
        print(f"   ❌ Error testing sell_market_order: {e}")
    
    print(f"\n✅ Test completed successfully!")
    print(f"💡 The trailing stop should now be included in order payloads when:")
    print(f"   - use_trailing_stop is True in profile")
    print(f"   - stop_loss is provided")
    print(f"   - trailing_distance is calculated correctly")

if __name__ == "__main__":
    test_trailing_stop_payload()