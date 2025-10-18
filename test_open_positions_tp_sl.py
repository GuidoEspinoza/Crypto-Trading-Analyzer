#!/usr/bin/env python3
"""
🧪 Script para probar la apertura real de posiciones con TP y SL
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
from src.core.paper_trader import PaperTrader
from src.database.database import DatabaseManager
from src.config.main_config import TradingProfiles
from src.core.enhanced_strategies import TradingSignal

async def test_real_position_opening():
    """Probar la apertura real de posiciones con TP y SL"""
    print("🧪 Probando apertura REAL de posiciones con TP y SL...")
    print("=" * 60)
    
    # Inicializar componentes
    print("🔧 Inicializando componentes...")
    trading_bot = TradingBot()
    paper_trader = PaperTrader(initial_balance=10000.0)  # $10,000 inicial
    
    # Resetear portfolio para asegurar balance inicial
    reset_result = paper_trader.reset_portfolio()
    if reset_result['success']:
        print(f"💰 Portfolio inicializado con ${reset_result['initial_balance']:,.2f}")
    else:
        print(f"❌ Error inicializando portfolio: {reset_result['message']}")
    
    db = DatabaseManager()
    
    # Obtener perfil activo
    profile = TradingProfiles.get_current_profile()
    print(f"📋 Perfil activo: {profile['name']}")
    print(f"   TP min: {profile['tp_min_percentage']*100:.1f}%")
    print(f"   TP max: {profile['tp_max_percentage']*100:.1f}%")
    print(f"   SL min: {profile['sl_min_percentage']*100:.1f}%")
    print(f"   SL max: {profile['sl_max_percentage']*100:.1f}%")
    print()
    
    # Precio de prueba
    current_price = 50000.0
    print(f"💰 Precio de prueba: ${current_price:,.2f}")
    print()
    
    # Test 1: Crear y ejecutar señal LONG
    print("🔵 Test 1: Creando posición LONG")
    print("-" * 40)
    
    try:
        # Crear señal de compra con TP y SL
        buy_signal = TradingSignal(
            symbol='BITCOIN',
            signal_type='BUY',
            price=current_price,
            confidence_score=85.0,
            strength='Strong',
            strategy_name='Test Strategy',
            timestamp=datetime.now(),
            notes='Test LONG position with TP/SL'
        )
        
        # Agregar TP y SL como atributos adicionales
        buy_signal.take_profit = current_price * 1.03  # 3% arriba
        buy_signal.stop_loss = current_price * 0.98    # 2% abajo
        
        print(f"   📊 Señal creada:")
        print(f"      Símbolo: {buy_signal.symbol}")
        print(f"      Tipo: {buy_signal.signal_type}")
        print(f"      Precio: ${buy_signal.price:,.2f}")
        print(f"      Take Profit: ${buy_signal.take_profit:,.2f} (+{((buy_signal.take_profit / buy_signal.price) - 1) * 100:.2f}%)")
        print(f"      Stop Loss: ${buy_signal.stop_loss:,.2f} ({((buy_signal.stop_loss / buy_signal.price) - 1) * 100:.2f}%)")
        print(f"      Confianza: {buy_signal.confidence_score:.1f}%")
        
        # Ejecutar la señal usando paper trader
        result = paper_trader.execute_signal(buy_signal)
        
        if result and result.success:
            print(f"   ✅ Posición LONG creada exitosamente")
            print(f"      Trade ID: {result.trade_id}")
            print(f"      Cantidad: {result.quantity}")
            print(f"      Valor: ${result.entry_value:.2f}")
        else:
            print(f"   ❌ Error creando posición LONG: {result.message if result else 'Sin resultado'}")
        
    except Exception as e:
        print(f"   ❌ Error en test LONG: {e}")
    
    print()
    
    # Test 2: Crear y ejecutar señal SHORT
    print("🔴 Test 2: Creando posición SHORT")
    print("-" * 40)
    
    try:
        # Crear señal de venta con TP y SL
        sell_signal = TradingSignal(
            symbol='BITCOIN',
            signal_type='SELL',
            price=current_price,
            confidence_score=85.0,
            strength='Strong',
            strategy_name='Test Strategy',
            timestamp=datetime.now(),
            notes='Test SHORT position with TP/SL'
        )
        
        # Agregar TP y SL como atributos adicionales
        sell_signal.take_profit = current_price * 0.97  # 3% abajo
        sell_signal.stop_loss = current_price * 1.02    # 2% arriba
        
        print(f"   📊 Señal creada:")
        print(f"      Símbolo: {sell_signal.symbol}")
        print(f"      Tipo: {sell_signal.signal_type}")
        print(f"      Precio: ${sell_signal.price:,.2f}")
        print(f"      Take Profit: ${sell_signal.take_profit:,.2f} ({((sell_signal.take_profit / sell_signal.price) - 1) * 100:.2f}%)")
        print(f"      Stop Loss: ${sell_signal.stop_loss:,.2f} (+{((sell_signal.stop_loss / sell_signal.price) - 1) * 100:.2f}%)")
        print(f"      Confianza: {sell_signal.confidence_score:.1f}%")
        
        # Ejecutar la señal usando paper trader
        result = paper_trader.execute_signal(sell_signal)
        
        if result and result.success:
            print(f"   ✅ Posición SHORT creada exitosamente")
            print(f"      Trade ID: {result.trade_id}")
            print(f"      Cantidad: {result.quantity}")
            print(f"      Valor: ${result.entry_value:.2f}")
        else:
            print(f"   ❌ Error creando posición SHORT: {result.message if result else 'Sin resultado'}")
        
    except Exception as e:
        print(f"   ❌ Error en test SHORT: {e}")
    
    print()
    
    # Verificar posiciones creadas en la base de datos
    print("🔍 Verificando posiciones creadas...")
    print("-" * 40)
    
    try:
        # Obtener posiciones abiertas
        open_positions = db.get_active_trades(is_paper=True)
        print(f"📊 Posiciones abiertas: {len(open_positions)}")
        
        if open_positions:
            for i, pos in enumerate(open_positions, 1):
                print(f"\n📍 Posición #{i} (ID: {pos['id']})")
                print(f"   Símbolo: {pos['symbol']}")
                print(f"   Tipo: {pos['side']}")  # 'side' en lugar de 'trade_type'
                print(f"   Precio entrada: ${pos['entry_price']:,.2f}")
                print(f"   Cantidad: {pos['quantity']}")
                print(f"   Valor: ${pos['entry_price'] * pos['quantity']:,.2f}")  # Calcular valor
                print(f"   Estado: {pos['status']}")
                
                # Verificar TP y SL
                if pos['take_profit']:
                    tp_direction = "arriba" if pos['take_profit'] > pos['entry_price'] else "abajo"
                    tp_pct = ((pos['take_profit'] - pos['entry_price']) / pos['entry_price']) * 100
                    print(f"   Take Profit: ${pos['take_profit']:,.2f} ({tp_pct:+.2f}% - {tp_direction})")
                else:
                    print("   Take Profit: ❌ No configurado")
                
                if pos['stop_loss']:
                    sl_direction = "arriba" if pos['stop_loss'] > pos['entry_price'] else "abajo"
                    sl_pct = ((pos['stop_loss'] - pos['entry_price']) / pos['entry_price']) * 100
                    print(f"   Stop Loss: ${pos['stop_loss']:,.2f} ({sl_pct:+.2f}% - {sl_direction})")
                else:
                    print("   Stop Loss: ❌ No configurado")
                
                # Validar configuración según tipo de posición
                if pos['side'] == 'BUY':  # Posición LONG
                    tp_ok = pos['take_profit'] and pos['take_profit'] > pos['entry_price']
                    sl_ok = pos['stop_loss'] and pos['stop_loss'] < pos['entry_price']
                    expected_tp = "por encima"
                    expected_sl = "por debajo"
                elif pos['side'] == 'SELL':  # Posición SHORT
                    tp_ok = pos['take_profit'] and pos['take_profit'] < pos['entry_price']
                    sl_ok = pos['stop_loss'] and pos['stop_loss'] > pos['entry_price']
                    expected_tp = "por debajo"
                    expected_sl = "por encima"
                else:
                    tp_ok = sl_ok = False
                    expected_tp = expected_sl = "N/A"
                
                print(f"   Validación:")
                print(f"      TP {expected_tp}: {'✅' if tp_ok else '❌'}")
                print(f"      SL {expected_sl}: {'✅' if sl_ok else '❌'}")
                
                status = "✅ CORRECTA" if (tp_ok and sl_ok) else "❌ INCORRECTA"
                print(f"   Configuración: {status}")
                
                # Calcular ratio riesgo/recompensa
                if pos['take_profit'] and pos['stop_loss']:
                    if pos['side'] == 'BUY':
                        risk = abs(pos['entry_price'] - pos['stop_loss'])
                        reward = abs(pos['take_profit'] - pos['entry_price'])
                    else:
                        risk = abs(pos['stop_loss'] - pos['entry_price'])
                        reward = abs(pos['entry_price'] - pos['take_profit'])
                    
                    if risk > 0:
                        rr_ratio = reward / risk
                        print(f"   Risk/Reward: 1:{rr_ratio:.2f}")
        else:
            print("   ℹ️ No se encontraron posiciones abiertas")
        
    except Exception as e:
        print(f"❌ Error verificando posiciones: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 Prueba de apertura de posiciones completada")

if __name__ == "__main__":
    asyncio.run(test_real_position_opening())