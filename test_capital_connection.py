#!/usr/bin/env python3
"""
Test simple de conexión con Capital.com
Diagnostica problemas de conexión y endpoints
"""

import sys
import os
import time
import logging
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.capital_client import create_capital_client_from_env

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_connection():
    """Test básico de conexión"""
    print("🔌 Probando conexión básica con Capital.com...")
    
    try:
        # Crear cliente
        client = create_capital_client_from_env()
        print(f"✅ Cliente creado exitosamente")
        print(f"📍 URL base: {client.base_url}")
        print(f"🔧 Modo demo: {client.config.use_demo}")
        
        return client
    except Exception as e:
        print(f"❌ Error creando cliente: {e}")
        return None

def test_session_creation(client):
    """Test de creación de sesión"""
    print("\n🔐 Probando creación de sesión...")
    
    try:
        # Crear sesión con timeout
        start_time = time.time()
        session_result = client.create_session()
        end_time = time.time()
        
        print(f"⏱️ Tiempo de respuesta: {end_time - start_time:.2f} segundos")
        print(f"📊 Resultado: {session_result}")
        
        if session_result.get("success"):
            print("✅ Sesión creada exitosamente")
            return True
        else:
            print(f"❌ Error en sesión: {session_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en creación de sesión: {e}")
        return False

def test_ping(client):
    """Test de ping"""
    print("\n🏓 Probando ping...")
    
    try:
        start_time = time.time()
        ping_result = client.ping()
        end_time = time.time()
        
        print(f"⏱️ Tiempo de respuesta: {end_time - start_time:.2f} segundos")
        print(f"📊 Resultado: {ping_result}")
        
        if ping_result.get("success"):
            print("✅ Ping exitoso")
            return True
        else:
            print(f"❌ Error en ping: {ping_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en ping: {e}")
        return False

def test_market_data_simple(client):
    """Test simple de datos de mercado"""
    print("\n📊 Probando obtención de datos de mercado...")
    
    try:
        # Probar con un símbolo simple
        symbols = ["BTCUSD"]
        print(f"🎯 Probando con símbolos: {symbols}")
        
        start_time = time.time()
        market_data = client.get_market_data(symbols)
        end_time = time.time()
        
        print(f"⏱️ Tiempo de respuesta: {end_time - start_time:.2f} segundos")
        print(f"📊 Datos obtenidos: {market_data}")
        
        if market_data:
            print("✅ Datos de mercado obtenidos")
            return True
        else:
            print("❌ No se obtuvieron datos de mercado")
            return False
            
    except Exception as e:
        print(f"❌ Excepción obteniendo datos de mercado: {e}")
        return False

def test_markets_endpoint(client):
    """Test del endpoint de markets"""
    print("\n🏪 Probando endpoint de markets...")
    
    try:
        start_time = time.time()
        markets_result = client.get_markets(search_term="BTC")
        end_time = time.time()
        
        print(f"⏱️ Tiempo de respuesta: {end_time - start_time:.2f} segundos")
        print(f"📊 Resultado: {markets_result}")
        
        if markets_result.get("success"):
            print("✅ Endpoint de markets funciona")
            return True
        else:
            print(f"❌ Error en markets: {markets_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción en markets: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🚀 Iniciando diagnóstico de conexión con Capital.com")
    print(f"📅 Fecha: {datetime.now()}")
    print("=" * 60)
    
    # Test 1: Conexión básica
    client = test_basic_connection()
    if not client:
        print("\n❌ FALLO CRÍTICO: No se pudo crear el cliente")
        return
    
    # Test 2: Creación de sesión
    session_ok = test_session_creation(client)
    if not session_ok:
        print("\n❌ FALLO CRÍTICO: No se pudo crear la sesión")
        return
    
    # Test 3: Ping
    ping_ok = test_ping(client)
    if not ping_ok:
        print("\n⚠️ ADVERTENCIA: Ping falló")
    
    # Test 4: Markets endpoint
    markets_ok = test_markets_endpoint(client)
    if not markets_ok:
        print("\n⚠️ ADVERTENCIA: Endpoint de markets falló")
    
    # Test 5: Market data simple
    market_data_ok = test_market_data_simple(client)
    if not market_data_ok:
        print("\n⚠️ ADVERTENCIA: Obtención de datos de mercado falló")
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN DEL DIAGNÓSTICO:")
    print(f"   🔌 Conexión básica: {'✅' if client else '❌'}")
    print(f"   🔐 Sesión: {'✅' if session_ok else '❌'}")
    print(f"   🏓 Ping: {'✅' if ping_ok else '❌'}")
    print(f"   🏪 Markets: {'✅' if markets_ok else '❌'}")
    print(f"   📊 Market Data: {'✅' if market_data_ok else '❌'}")
    
    if all([client, session_ok, ping_ok, markets_ok, market_data_ok]):
        print("\n🎉 DIAGNÓSTICO EXITOSO: Todos los tests pasaron")
    else:
        print("\n⚠️ DIAGNÓSTICO PARCIAL: Algunos tests fallaron")

if __name__ == "__main__":
    main()