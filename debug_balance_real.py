#!/usr/bin/env python3
"""
Script para debuggear el balance real de Capital.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.capital_client import create_capital_client_from_env
import json

def main():
    print("🔍 Debuggeando balance de Capital.com...")
    
    try:
        # Crear cliente de Capital.com
        capital_client = create_capital_client_from_env()
        
        # Obtener información de cuentas
        print("\n1. Obteniendo información de cuentas...")
        accounts_result = capital_client.get_accounts()
        print(f"Resultado de cuentas: {json.dumps(accounts_result, indent=2)}")
        
        # Obtener balance disponible
        print("\n2. Obteniendo balance disponible...")
        balance_result = capital_client.get_available_balance()
        print(f"Resultado de balance: {json.dumps(balance_result, indent=2)}")
        
        if balance_result.get("success"):
            available = balance_result.get("available", 0)
            balance = balance_result.get("balance", 0)
            currency = balance_result.get("currency", "USD")
            symbol = balance_result.get("symbol", "$")
            
            print(f"\n📊 RESUMEN DEL BALANCE:")
            print(f"   💰 Balance disponible: {symbol}{available:.2f}")
            print(f"   💵 Balance total: {symbol}{balance:.2f}")
            print(f"   🌍 Moneda: {currency}")
            
            # Calcular 15% del balance disponible
            position_15_percent = available * 0.15
            print(f"\n🎯 CÁLCULO DE POSICIÓN (15%):")
            print(f"   📈 15% del balance disponible: {symbol}{position_15_percent:.2f}")
            
            # Calcular cuántas unidades de XRP se pueden comprar con $2.35
            xrp_price = 2.35
            xrp_units = position_15_percent / xrp_price
            print(f"   🪙 Unidades de XRP a ${xrp_price}: {xrp_units:.2f}")
            
        else:
            print(f"❌ Error obteniendo balance: {balance_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()