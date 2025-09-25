#!/usr/bin/env python3
"""
Script simple para probar el endpoint /api/v3/order/test de Binance
"""

import os
import sys
import time
import hmac
import hashlib
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

def generate_signature(query_string: str, secret_key: str) -> str:
    """Generar firma HMAC SHA256"""
    return hmac.new(
        secret_key.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def test_simple_order():
    """Probar una orden simple en el endpoint /api/v3/order/test"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Error: Variables de entorno BINANCE_API_KEY y BINANCE_SECRET_KEY requeridas")
        return False
    
    print("🧪 Probando endpoint /api/v3/order/test con orden simple...")
    
    # Parámetros mínimos para una orden MARKET
    params = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': '10',  # Comprar $10 USDT de BTC
        'timestamp': int(time.time() * 1000),
        'recvWindow': 5000
    }
    
    # Generar query string y firma
    query_string = urlencode(params)
    signature = generate_signature(query_string, secret_key)
    
    # URL completa con firma
    url = f"https://api.binance.com/api/v3/order/test?{query_string}&signature={signature}"
    
    # Headers
    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print(f"📡 Enviando request a: https://api.binance.com/api/v3/order/test")
    print(f"📋 Parámetros: {params}")
    
    try:
        # Hacer request POST
        response = requests.post(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Orden de prueba exitosa!")
            try:
                response_data = response.json()
                print(f"📦 Response Data: {response_data}")
            except:
                print(f"📦 Response Text: {response.text}")
            return True
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Error Details: {error_data}")
            except:
                print(f"🔍 Error Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Exception: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_with_testnet():
    """Probar la misma orden en testnet"""
    
    # Cargar variables de entorno
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    
    if not api_key or not secret_key:
        print("❌ Error: Variables de entorno BINANCE_API_KEY y BINANCE_SECRET_KEY requeridas")
        return False
    
    print("\n🧪 Probando endpoint en TESTNET...")
    
    # Parámetros mínimos para una orden MARKET
    params = {
        'symbol': 'BTCUSDT',
        'side': 'BUY',
        'type': 'MARKET',
        'quoteOrderQty': '10',  # Comprar $10 USDT de BTC
        'timestamp': int(time.time() * 1000),
        'recvWindow': 5000
    }
    
    # Generar query string y firma
    query_string = urlencode(params)
    signature = generate_signature(query_string, secret_key)
    
    # URL de testnet
    url = f"https://testnet.binance.vision/api/v3/order/test?{query_string}&signature={signature}"
    
    # Headers
    headers = {
        'X-MBX-APIKEY': api_key,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    print(f"📡 Enviando request a: https://testnet.binance.vision/api/v3/order/test")
    print(f"📋 Parámetros: {params}")
    
    try:
        # Hacer request POST
        response = requests.post(url, headers=headers, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Orden de prueba en testnet exitosa!")
            try:
                response_data = response.json()
                print(f"📦 Response Data: {response_data}")
            except:
                print(f"📦 Response Text: {response.text}")
            return True
        else:
            print(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"🔍 Error Details: {error_data}")
            except:
                print(f"🔍 Error Text: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Exception: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test Simple de Endpoint /api/v3/order/test")
    print("=" * 50)
    
    # Probar en producción
    production_success = test_simple_order()
    
    # Probar en testnet
    testnet_success = test_with_testnet()
    
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE RESULTADOS:")
    print(f"🏭 Producción (api.binance.com): {'✅ ÉXITO' if production_success else '❌ FALLO'}")
    print(f"🧪 Testnet (testnet.binance.vision): {'✅ ÉXITO' if testnet_success else '❌ FALLO'}")
    
    if production_success or testnet_success:
        print("\n✅ Al menos uno de los endpoints funciona correctamente")
    else:
        print("\n❌ Ambos endpoints fallaron - revisar configuración")