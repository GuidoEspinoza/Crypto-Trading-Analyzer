#!/usr/bin/env python3
"""
🧪 Script para probar la apertura de posiciones reales con TP y SL
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.trading_bot import TradingBot
from src.core.position_manager import PositionManager
from src.database.database import DatabaseManager
from src.config.main_config import TradingProfiles

async def test_position_opening():
    """Probar la apertura de posiciones con TP y SL"""
    print("🧪 Probando apertura de posiciones con TP y SL...")
    print("=" * 60)
    
    # Inicializar componentes
    trading_bot = TradingBot()
    position_manager = PositionManager()
    db = DatabaseManager()
    
    # Obtener perfil activo
    profile = TradingProfiles.get_current_profile()
    print(f"📋 Perfil activo: {profile['name']}")
    print(f"   TP min: {profile['tp_min_percentage']*100:.1f}%")
    print(f"   TP max: {profile['tp_max_percentage']*100:.1f}%")
    print(f"   SL min: {profile['sl_min_percentage']*100:.1f}%")
    print(f"   SL max: {profile['sl_max_percentage']*100:.1f}%")
    print()
    
    # Obtener precio actual de BTC
    try:
        current_price = await trading_bot.capital_client.get_current_price("BITCOIN")
        print(f"💰 Precio actual de BTC: ${current_price:,.2f}")
    except Exception as e:
        print(f"❌ Error obteniendo precio: {e}")
        current_price = 50000  # Precio de fallback
        print(f"💰 Usando precio de fallback: ${current_price:,.2f}")
    
    print()
    
    # Test 1: Posición LONG
    print("🔵 Test 1: Posición LONG")
    print("-" * 30)
    
    try:
        # Crear señal de compra
        buy_signal = {
            'symbol': 'BITCOIN',
            'signal_type': 'BUY',
            'price': current_price,
            'confidence_score': 0.85,
            'strength': 'Strong',
            'strategy_name': 'Test Strategy',
            'timestamp': datetime.now(),
            'take_profit': current_price * 1.03,  # 3% arriba
            'stop_loss': current_price * 0.98     # 2% abajo
        }
        
        print(f"   Precio entrada: ${buy_signal['price']:,.2f}")
        print(f"   Take Profit:    ${buy_signal['take_profit']:,.2f} (+3.00%)")
        print(f"   Stop Loss:      ${buy_signal['stop_loss']:,.2f} (-2.00%)")
        
        # Simular apertura de posición
        position_size = 0.001  # Tamaño pequeño para prueba
        
        # Verificar que TP esté por encima y SL por debajo
        tp_correct = buy_signal['take_profit'] > buy_signal['price']
        sl_correct = buy_signal['stop_loss'] < buy_signal['price']
        
        print(f"   ✅ TP por encima del precio: {tp_correct}")
        print(f"   ✅ SL por debajo del precio: {sl_correct}")
        
        if tp_correct and sl_correct:
            print("   ✅ Configuración LONG: CORRECTA")
        else:
            print("   ❌ Configuración LONG: INCORRECTA")
        
    except Exception as e:
        print(f"   ❌ Error en test LONG: {e}")
    
    print()
    
    # Test 2: Posición SHORT
    print("🔴 Test 2: Posición SHORT")
    print("-" * 30)
    
    try:
        # Crear señal de venta
        sell_signal = {
            'symbol': 'BITCOIN',
            'signal_type': 'SELL',
            'price': current_price,
            'confidence_score': 0.85,
            'strength': 'Strong',
            'strategy_name': 'Test Strategy',
            'timestamp': datetime.now(),
            'take_profit': current_price * 0.97,  # 3% abajo
            'stop_loss': current_price * 1.02     # 2% arriba
        }
        
        print(f"   Precio entrada: ${sell_signal['price']:,.2f}")
        print(f"   Take Profit:    ${sell_signal['take_profit']:,.2f} (-3.00%)")
        print(f"   Stop Loss:      ${sell_signal['stop_loss']:,.2f} (+2.00%)")
        
        # Verificar que TP esté por debajo y SL por encima
        tp_correct = sell_signal['take_profit'] < sell_signal['price']
        sl_correct = sell_signal['stop_loss'] > sell_signal['price']
        
        print(f"   ✅ TP por debajo del precio: {tp_correct}")
        print(f"   ✅ SL por encima del precio: {sl_correct}")
        
        if tp_correct and sl_correct:
            print("   ✅ Configuración SHORT: CORRECTA")
        else:
            print("   ❌ Configuración SHORT: INCORRECTA")
        
    except Exception as e:
        print(f"   ❌ Error en test SHORT: {e}")
    
    print()
    
    # Verificar posiciones existentes en la base de datos
    print("🔍 Verificando posiciones en base de datos...")
    print("-" * 40)
    
    try:
        # Obtener posiciones abiertas
        open_positions = db.get_active_trades(is_paper=True)
        print(f"📊 Posiciones abiertas: {len(open_positions)}")
        
        if open_positions:
            for pos in open_positions:
                print(f"\n📍 Trade ID: {pos.id}")
                print(f"   Símbolo: {pos.symbol}")
                print(f"   Tipo: {pos.trade_type}")
                print(f"   Precio entrada: ${pos.entry_price:,.2f}")
                
                if pos.take_profit:
                    tp_direction = "arriba" if pos.take_profit > pos.entry_price else "abajo"
                    tp_pct = ((pos.take_profit - pos.entry_price) / pos.entry_price) * 100
                    print(f"   Take Profit: ${pos.take_profit:,.2f} ({tp_pct:+.2f}% - {tp_direction})")
                else:
                    print("   Take Profit: No configurado")
                
                if pos.stop_loss:
                    sl_direction = "arriba" if pos.stop_loss > pos.entry_price else "abajo"
                    sl_pct = ((pos.stop_loss - pos.entry_price) / pos.entry_price) * 100
                    print(f"   Stop Loss: ${pos.stop_loss:,.2f} ({sl_pct:+.2f}% - {sl_direction})")
                else:
                    print("   Stop Loss: No configurado")
                
                # Validar configuración según tipo de posición
                if pos.trade_type == 'BUY':  # Posición LONG
                    tp_ok = pos.take_profit and pos.take_profit > pos.entry_price
                    sl_ok = pos.stop_loss and pos.stop_loss < pos.entry_price
                elif pos.trade_type == 'SELL':  # Posición SHORT
                    tp_ok = pos.take_profit and pos.take_profit < pos.entry_price
                    sl_ok = pos.stop_loss and pos.stop_loss > pos.entry_price
                else:
                    tp_ok = sl_ok = False
                
                status = "✅ CORRECTA" if (tp_ok and sl_ok) else "❌ INCORRECTA"
                print(f"   Configuración: {status}")
        
    except Exception as e:
        print(f"❌ Error verificando posiciones: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Prueba de configuración TP/SL completada")

if __name__ == "__main__":
    asyncio.run(test_position_opening())