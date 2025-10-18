#!/usr/bin/env python3
"""
Script de prueba para verificar el balance real de la cuenta demo de Capital.com
"""

import asyncio
import os
from dotenv import load_dotenv
from src.core.capital_client import create_capital_client_from_env

def test_balance():
    """Prueba para obtener el balance real de Capital.com"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    # Inicializar cliente de Capital.com
    capital_client = create_capital_client_from_env()
    
    try:
        print("🔗 Conectando a Capital.com (modo demo)...")
        
        # Obtener balance disponible
        balance_info = capital_client.get_available_balance()
        
        if balance_info:
            print(f"✅ Balance obtenido exitosamente:")
            print(f"   💰 Balance disponible: ${balance_info['available']:,.2f}")
            print(f"   🏦 Cuenta ID: {balance_info['account_id']}")
            print(f"   💱 Moneda: {balance_info['currency']}")
            print(f"   📊 Balance total: ${balance_info['balance']:,.2f}")
            print(f"   🔒 Depósito: ${balance_info['deposit']:,.2f}")
            print(f"   📈 PnL: ${balance_info['profitLoss']:,.2f}")
        else:
            print("❌ No se pudo obtener el balance")
            
        # También obtener información completa de cuentas
        print("\n📋 Información completa de cuentas:")
        accounts = capital_client.get_accounts()
        if accounts and 'accounts' in accounts:
            for account in accounts['accounts']:
                print(f"   🏦 Cuenta: {account.get('accountId', 'N/A')}")
                print(f"   💰 Disponible: ${account.get('available', 0):,.2f}")
                print(f"   📊 Balance: ${account.get('balance', 0):,.2f}")
                print(f"   💱 Moneda: {account.get('currency', 'N/A')}")
                print(f"   🔒 Depósito: ${account.get('deposit', 0):,.2f}")
                print(f"   📈 PnL: ${account.get('profitLoss', 0):,.2f}")
                print("   ---")
        
    except Exception as e:
        print(f"❌ Error al obtener balance: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_balance()