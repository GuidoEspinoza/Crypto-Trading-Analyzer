#!/usr/bin/env python3
"""
Script de depuración para diagnosticar problemas con trailing stop en órdenes reales
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.capital_client import create_capital_client_from_env
from src.config.main_config import TradingProfiles

def debug_trailing_stop_for_symbol(symbol="ADAUSD"):
    """Depurar el trailing stop para un símbolo específico"""
    
    print(f"🔍 Depurando trailing stop para {symbol}")
    print("=" * 60)
    
    # 1. Verificar configuración del perfil
    print("\n1. 📋 Verificando configuración del perfil:")
    current_profile = TradingProfiles.get_current_profile()
    profile_name = current_profile.get("name", "UNKNOWN")
    use_trailing_stop = current_profile.get("use_trailing_stop", False)
    
    print(f"   ✅ Perfil actual: {profile_name}")
    print(f"   ✅ use_trailing_stop: {use_trailing_stop}")
    
    if not use_trailing_stop:
        print("   ❌ PROBLEMA: Trailing stop está deshabilitado en el perfil")
        return
    
    # 2. Inicializar cliente de Capital.com
    print("\n2. 🔌 Inicializando cliente de Capital.com:")
    try:
        capital_client = create_capital_client_from_env()
        print("   ✅ Cliente inicializado correctamente")
    except Exception as e:
        print(f"   ❌ Error al inicializar cliente: {e}")
        return
    
    # 3. Verificar disponibilidad de trailing stop
    print(f"\n3. 🎯 Verificando disponibilidad de trailing stop para {symbol}:")
    try:
        trailing_availability = capital_client.is_trailing_stop_available(symbol)
        print(f"   📊 Respuesta completa: {trailing_availability}")
        
        success = trailing_availability.get("success", False)
        available = trailing_availability.get("available", False)
        reason = trailing_availability.get("reason", "No reason provided")
        
        print(f"   ✅ Success: {success}")
        print(f"   ✅ Available: {available}")
        print(f"   ✅ Reason: {reason}")
        
        if not success:
            print("   ❌ PROBLEMA: La verificación de trailing stop falló")
            return
            
        if not available:
            print(f"   ❌ PROBLEMA: Trailing stop no disponible - {reason}")
            return
            
    except Exception as e:
        print(f"   ❌ Error al verificar trailing stop: {e}")
        return
    
    # 4. Obtener precio actual
    print(f"\n4. 💰 Obteniendo precio actual para {symbol}:")
    try:
        market_data = capital_client.get_market_data([symbol])
        if symbol in market_data:
            current_price = market_data[symbol].get("bid", 0)
            print(f"   ✅ Precio actual: {current_price}")
        else:
            print(f"   ❌ No se pudo obtener precio para {symbol}")
            return
    except Exception as e:
        print(f"   ❌ Error al obtener precio: {e}")
        return
    
    # 5. Simular cálculo de trailing distance
    print(f"\n5. 📏 Simulando cálculo de trailing distance:")
    
    # Simular un stop loss típico (2% por debajo del precio actual para BUY)
    stop_loss_percentage = 0.02  # 2%
    simulated_stop_loss = current_price * (1 - stop_loss_percentage)
    trailing_distance = abs(current_price - simulated_stop_loss)
    
    print(f"   ✅ Precio actual: {current_price}")
    print(f"   ✅ Stop loss simulado (2%): {simulated_stop_loss}")
    print(f"   ✅ Trailing distance calculada: {trailing_distance}")
    
    if trailing_distance <= 0:
        print("   ❌ PROBLEMA: Trailing distance es 0 o negativa")
        return
    
    # 6. Simular construcción del payload
    print(f"\n6. 📦 Simulando construcción del payload de orden:")
    
    # Simular parámetros de orden
    epic = symbol
    direction = "BUY"
    size = 100.0
    take_profit = current_price * 1.02  # 2% arriba
    
    print(f"   📋 Parámetros de orden:")
    print(f"      - Epic: {epic}")
    print(f"      - Direction: {direction}")
    print(f"      - Size: {size}")
    print(f"      - Take Profit: {take_profit}")
    print(f"      - Trailing Stop: True")
    print(f"      - Stop Distance: {trailing_distance}")
    
    # Simular el payload que se enviaría
    order_payload = {
        "epic": epic,
        "direction": direction.upper(),
        "size": size,
        "guaranteedStop": False,
        "trailingStop": True,
        "stopDistance": trailing_distance,
        "profitLevel": take_profit
    }
    
    print(f"\n   📦 Payload simulado:")
    print(f"      {order_payload}")
    
    # 7. Verificar si el payload incluye trailingStop
    print(f"\n7. ✅ Verificación final:")
    has_trailing_stop = "trailingStop" in order_payload and order_payload["trailingStop"]
    has_stop_distance = "stopDistance" in order_payload and order_payload["stopDistance"] > 0
    
    print(f"   ✅ Payload incluye trailingStop: {has_trailing_stop}")
    print(f"   ✅ Payload incluye stopDistance válida: {has_stop_distance}")
    
    if has_trailing_stop and has_stop_distance:
        print("\n🎉 ¡TODO CORRECTO! El trailing stop debería funcionar.")
        print("   Si aún no funciona, el problema podría estar en:")
        print("   - La lógica de condiciones en trading_bot.py")
        print("   - El momento de la verificación (precio/stop loss)")
        print("   - La respuesta de la API de Capital.com")
    else:
        print("\n❌ PROBLEMA IDENTIFICADO en la construcción del payload")
    
    return {
        "profile_ok": use_trailing_stop,
        "client_ok": True,
        "availability_ok": available,
        "distance_ok": trailing_distance > 0,
        "payload_ok": has_trailing_stop and has_stop_distance
    }

if __name__ == "__main__":
    print("🔧 Script de depuración de Trailing Stop")
    print("=" * 60)
    
    # Depurar para ADAUSD (el símbolo del ejemplo)
    result = debug_trailing_stop_for_symbol("ADAUSD")
    
    print(f"\n📊 Resumen de resultados:")
    if result:
        for key, value in result.items():
            status = "✅" if value else "❌"
            print(f"   {status} {key}: {value}")
    
    print("\n🔍 Si todos los checks están OK pero el trailing stop no funciona,")
    print("   revisa los logs del bot para ver qué condición específica falla.")