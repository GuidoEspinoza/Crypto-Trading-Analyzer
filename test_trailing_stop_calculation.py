#!/usr/bin/env python3
"""
Script para probar el cálculo correcto del stopDistance en trailing stops
"""

def test_trailing_stop_calculation():
    """Prueba diferentes escenarios de cálculo de stopDistance"""
    
    print("🧮 Testing trailing stop distance calculation...")
    print("=" * 60)
    
    # Casos de prueba
    test_cases = [
        # BUY scenarios
        {
            "signal_type": "BUY",
            "current_price": 1000,
            "stop_loss": 900,
            "expected_distance": 100,
            "description": "BUY: Precio 1000, SL 900 → Distance 100"
        },
        {
            "signal_type": "BUY", 
            "current_price": 0.5000,
            "stop_loss": 0.4900,
            "expected_distance": 0.0100,
            "description": "BUY: Precio 0.5000, SL 0.4900 → Distance 0.0100"
        },
        {
            "signal_type": "BUY",
            "current_price": 1000,
            "stop_loss": 1100,  # SL mayor que precio actual (inválido)
            "expected_distance": -100,
            "description": "BUY: Precio 1000, SL 1100 → Distance -100 (INVÁLIDO)"
        },
        
        # SELL scenarios
        {
            "signal_type": "SELL",
            "current_price": 1000,
            "stop_loss": 1100,
            "expected_distance": 100,
            "description": "SELL: Precio 1000, SL 1100 → Distance 100"
        },
        {
            "signal_type": "SELL",
            "current_price": 0.5000,
            "stop_loss": 0.5100,
            "expected_distance": 0.0100,
            "description": "SELL: Precio 0.5000, SL 0.5100 → Distance 0.0100"
        },
        {
            "signal_type": "SELL",
            "current_price": 1000,
            "stop_loss": 900,  # SL menor que precio actual (inválido)
            "expected_distance": -100,
            "description": "SELL: Precio 1000, SL 900 → Distance -100 (INVÁLIDO)"
        }
    ]
    
    print("📊 Test Cases:")
    print("-" * 60)
    
    for i, case in enumerate(test_cases, 1):
        signal_type = case["signal_type"]
        current_price = case["current_price"]
        stop_loss = case["stop_loss"]
        expected = case["expected_distance"]
        description = case["description"]
        
        # Calcular según la nueva lógica
        if signal_type == "BUY":
            calculated_distance = current_price - stop_loss
        else:  # SELL
            calculated_distance = stop_loss - current_price
        
        # Verificar si es válido (positivo)
        is_valid = calculated_distance > 0
        
        print(f"\n{i}. {description}")
        print(f"   Signal Type: {signal_type}")
        print(f"   Current Price: {current_price}")
        print(f"   Stop Loss: {stop_loss}")
        print(f"   Expected Distance: {expected}")
        print(f"   Calculated Distance: {calculated_distance}")
        print(f"   Is Valid (>0): {'✅ YES' if is_valid else '❌ NO'}")
        
        # Verificar que el cálculo sea correcto
        if abs(calculated_distance - expected) < 0.0001:
            print(f"   Calculation: ✅ CORRECT")
        else:
            print(f"   Calculation: ❌ INCORRECT")
    
    print("\n" + "=" * 60)
    print("🎯 Trailing Stop Logic Summary:")
    print("-" * 60)
    print("• BUY orders: stopDistance = current_price - stop_loss")
    print("  - Protects against downward movement")
    print("  - Stop loss should be BELOW current price")
    print("  - Example: Price 1000, SL 900 → Distance 100")
    print()
    print("• SELL orders: stopDistance = stop_loss - current_price") 
    print("  - Protects against upward movement")
    print("  - Stop loss should be ABOVE current price")
    print("  - Example: Price 1000, SL 1100 → Distance 100")
    print()
    print("• stopDistance must ALWAYS be positive")
    print("• If negative, fall back to traditional stop loss")
    
    print("\n🔄 How Trailing Stop Works:")
    print("-" * 60)
    print("Example BUY at 1000 with stopDistance 100:")
    print("• Initial: Price 1000, Stop at 900 (1000-100)")
    print("• Price rises to 1300: Stop moves to 1200 (1300-100)")
    print("• Price falls to 1250: Stop stays at 1200 (trailing)")
    print("• If price hits 1200: Position closes")

if __name__ == "__main__":
    test_trailing_stop_calculation()