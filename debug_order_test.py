#!/usr/bin/env python3
"""
Script de debug para probar el endpoint /api/v3/order/test de Binance
Probará diferentes combinaciones de parámetros para identificar el problema
"""

import os
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode

# Intentar cargar dotenv si está disponible
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  python-dotenv no está instalado, usando variables de entorno del sistema")

# Cargar variables de entorno
API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')

if not API_KEY or not SECRET_KEY:
    print("❌ Error: BINANCE_API_KEY y BINANCE_SECRET_KEY deben estar configuradas")
    exit(1)

def generate_signature(query_string, secret):
    """Genera la firma HMAC SHA256"""
    return hmac.new(
        secret.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_order_endpoint(params, method='POST', description=""):
    """Prueba el endpoint con diferentes parámetros y métodos"""
    print(f"\n🧪 Probando: {description}")
    print(f"   Método: {method}")
    print(f"   Parámetros: {params}")
    
    # Agregar timestamp
    timestamp = int(time.time() * 1000)
    params['timestamp'] = timestamp
    params['recvWindow'] = 5000
    
    # Crear query string y firma
    query_string = urlencode(params)
    signature = generate_signature(query_string, SECRET_KEY)
    params['signature'] = signature
    
    # Headers
    headers = {
        'X-MBX-APIKEY': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    url = 'https://api.binance.com/api/v3/order/test'
    
    try:
        if method == 'POST':
            response = requests.post(url, data=params, headers=headers, timeout=10)
        else:  # GET
            final_url = f"{url}?{urlencode(params)}"
            response = requests.get(final_url, headers=headers, timeout=10)
            
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ ÉXITO")
        else:
            print(f"   ❌ ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ EXCEPCIÓN: {e}")

def main():
    print("🔍 Debug del endpoint /api/v3/order/test de Binance")
    print("=" * 60)
    
    # Test 1: Orden MARKET básica con POST (sin computeCommissionRates)
    test_order_endpoint({
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.001'
    }, 'POST', "Orden MARKET básica con POST")
    
    # Test 2: Orden MARKET con quoteOrderQty
    test_order_endpoint({
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': '10.0'
    }, 'POST', "Orden MARKET con quoteOrderQty")
    
    # Test 3: Orden MARKET con computeCommissionRates
    test_order_endpoint({
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.001',
        'computeCommissionRates': 'true'
    }, 'POST', "Orden MARKET con computeCommissionRates")
    
    # Test 4: Orden LIMIT básica
    test_order_endpoint({
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': '0.001',
        'price': '30000.00'
    }, 'POST', "Orden LIMIT básica")
    
    # Test 5: Probar con GET (para ver si es problema de método)
    test_order_endpoint({
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': '0.001'
    }, 'GET', "Orden MARKET con GET (debería fallar)")
    
    print("\n" + "=" * 60)
    print("🏁 Debug completado")

if __name__ == "__main__":
    main()