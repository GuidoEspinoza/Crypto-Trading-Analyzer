#!/usr/bin/env python3
"""
Script de depuración mejorado para trailing stops con verificaciones de disponibilidad
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.capital_client import create_capital_client_from_env
from src.core.trading_bot import TradingBot
from src.core.enhanced_strategies import TradingSignal
from src.config.main_config import TradingProfiles
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_trailing_stop_availability():
    """Prueba la verificación de disponibilidad de trailing stops"""
    print("=" * 80)
    print("🧪 PRUEBA DE DISPONIBILIDAD DE TRAILING STOPS")
    print("=" * 80)
    
    try:
        # 1. Inicializar cliente de Capital.com
        print("\n1️⃣ Inicializando cliente de Capital.com...")
        capital_client = create_capital_client_from_env()
        
        if not capital_client:
            print("❌ Error: No se pudo crear el cliente de Capital.com")
            return False
            
        print("✅ Cliente de Capital.com inicializado correctamente")
        
        # 2. Crear sesión
        print("\n2️⃣ Creando sesión...")
        session_result = capital_client.create_session()
        
        if not session_result.get("success"):
            print(f"❌ Error creando sesión: {session_result.get('error')}")
            return False
            
        print("✅ Sesión creada exitosamente")
        print(f"📊 Trailing stops habilitados en cuenta: {capital_client.trailing_stops_enabled}")
        print(f"📋 Información de cuenta: {capital_client.account_info}")
        
        # 3. Probar verificación de trailing stops para diferentes instrumentos
        test_symbols = ["BITCOIN", "ETHEREUM", "CS.D.EURUSD.CFD.IP"]
        
        print(f"\n3️⃣ Probando disponibilidad de trailing stops para {len(test_symbols)} instrumentos...")
        
        for symbol in test_symbols:
            print(f"\n🔍 Verificando {symbol}:")
            availability = capital_client.is_trailing_stop_available(symbol)
            
            print(f"   ✅ Éxito: {availability.get('success', False)}")
            print(f"   📊 Disponible: {availability.get('available', False)}")
            print(f"   📝 Razón: {availability.get('reason', 'N/A')}")
            print(f"   🏦 Cuenta habilitada: {availability.get('account_enabled', 'N/A')}")
            print(f"   🎯 Instrumento soportado: {availability.get('instrument_supported', 'N/A')}")
            
            if 'trailing_preference' in availability:
                print(f"   ⚙️ Preferencia: {availability['trailing_preference']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de disponibilidad: {str(e)}")
        return False

def test_trading_bot_integration():
    """Prueba la integración del trailing stop en el trading bot"""
    print("\n" + "=" * 80)
    print("🤖 PRUEBA DE INTEGRACIÓN CON TRADING BOT")
    print("=" * 80)
    
    try:
        # 1. Inicializar TradingBot
        print("\n1️⃣ Inicializando TradingBot...")
        bot = TradingBot()
        
        if not bot.capital_client:
            print("❌ Error: TradingBot no tiene cliente de Capital.com")
            return False
            
        print("✅ TradingBot inicializado correctamente")
        
        # 2. Verificar configuración del perfil
        current_profile = TradingProfiles.get_current_profile()
        # Obtener el nombre del perfil buscando en PROFILES
        profile_name = current_profile.get("name", "DESCONOCIDO")
        use_trailing_stop = current_profile.get("use_trailing_stop", False)
        
        print(f"\n2️⃣ Configuración del perfil actual:")
        print(f"   📋 Perfil: {profile_name}")
        print(f"   🎯 Trailing stop configurado: {use_trailing_stop}")
        
        if use_trailing_stop:
            trailing_config = current_profile.get("trailing_stop_activation", {})
            print(f"   ⚙️ Configuración trailing stop: {trailing_config}")
        
        # 3. Simular señal de trading
        print(f"\n3️⃣ Simulando señal de trading...")
        
        test_signal = TradingSignal(
            symbol="BITCOIN",
            signal_type="BUY",
            price=50000.0,
            confidence_score=0.8,
            strength="Strong",
            strategy_name="TestStrategy",
            timestamp=datetime.now()
        )
        
        print(f"   📊 Señal: {test_signal.signal_type} {test_signal.symbol}")
        print(f"   💰 Precio entrada: {test_signal.price}")
        print(f"   💪 Fuerza: {test_signal.strength}")
        print(f"   📈 Estrategia: {test_signal.strategy_name}")
        
        # 4. Verificar disponibilidad de trailing stop para el símbolo
        print(f"\n4️⃣ Verificando disponibilidad de trailing stop para {test_signal.symbol}...")
        
        capital_symbol = bot._normalize_symbol_for_capital(test_signal.symbol)
        print(f"   🔄 Símbolo normalizado: {capital_symbol}")
        
        availability = bot.capital_client.is_trailing_stop_available(capital_symbol)
        print(f"   📊 Resultado verificación: {availability}")
        
        # 5. Simular lógica de decisión de trailing stop
        print(f"\n5️⃣ Simulando lógica de decisión...")
        
        # Calcular precios de ejemplo
        entry_price = test_signal.price
        stop_loss_price = entry_price * 0.98  # 2% stop loss
        
        if use_trailing_stop:
            if availability.get("success", False) and availability.get("available", False):
                trailing_distance = abs(entry_price - stop_loss_price)
                print(f"   ✅ Trailing stop DISPONIBLE - Distancia: {trailing_distance:.4f}")
                print(f"   🎯 Se usará trailing stop en la orden")
            else:
                reason = availability.get("reason", "Unknown reason")
                print(f"   ⚠️ Trailing stop NO DISPONIBLE: {reason}")
                print(f"   🔄 Se usará stop loss tradicional: {stop_loss_price}")
        else:
            print(f"   ℹ️ Trailing stop no configurado")
            print(f"   🔄 Se usará stop loss tradicional: {stop_loss_price}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de integración: {str(e)}")
        return False

def main():
    """Función principal del script de prueba"""
    print("🚀 INICIANDO PRUEBAS DE TRAILING STOP MEJORADAS")
    print("=" * 80)
    
    # Ejecutar pruebas
    test1_success = test_trailing_stop_availability()
    test2_success = test_trading_bot_integration()
    
    # Resumen final
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 80)
    print(f"✅ Prueba de disponibilidad: {'EXITOSA' if test1_success else 'FALLIDA'}")
    print(f"✅ Prueba de integración: {'EXITOSA' if test2_success else 'FALLIDA'}")
    
    total_tests = 2
    successful_tests = sum([test1_success, test2_success])
    
    print(f"\n🎯 Resultado final: {successful_tests}/{total_tests} pruebas exitosas")
    
    if successful_tests == total_tests:
        print("🎉 ¡Todas las pruebas fueron exitosas!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron. Revisar logs para más detalles.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)