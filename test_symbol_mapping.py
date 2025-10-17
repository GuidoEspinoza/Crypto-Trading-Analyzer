#!/usr/bin/env python3
"""
Script de prueba para verificar el mapeo correcto de símbolos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tools.trading_monitor import map_trade_symbol_to_global_symbol
from config.global_symbols import GLOBAL_SYMBOLS

def test_symbol_mapping():
    """Prueba el mapeo de símbolos de trading a GLOBAL_SYMBOLS"""
    
    print("🧪 PRUEBA DE MAPEO DE SÍMBOLOS")
    print("=" * 50)
    
    # Casos de prueba
    test_cases = [
        "GOLD/USD",
        "SILVER/USD", 
        "PALLADIUM/USD",
        "PLATINUM/USD",
        "Bitcoin/USD",
        "Ethereum/USD",
        "Ripple/USD",
        "Crude Oil/USD",
        "Natural Gas/USD",
        "UNKNOWN/USD"
    ]
    
    print(f"📋 GLOBAL_SYMBOLS disponibles:")
    for symbol in GLOBAL_SYMBOLS:
        print(f"   - {symbol}")
    
    print(f"\n🔄 Probando mapeo de símbolos:")
    print("-" * 30)
    
    for trade_symbol in test_cases:
        mapped_symbol = map_trade_symbol_to_global_symbol(trade_symbol)
        is_in_global = mapped_symbol in GLOBAL_SYMBOLS
        status = "✅" if is_in_global else "❌"
        
        print(f"{status} {trade_symbol:15} -> {mapped_symbol:15} (En GLOBAL_SYMBOLS: {is_in_global})")
    
    print(f"\n✅ Prueba de mapeo completada")

if __name__ == "__main__":
    test_symbol_mapping()