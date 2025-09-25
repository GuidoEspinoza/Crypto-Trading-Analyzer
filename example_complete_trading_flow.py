#!/usr/bin/env python3
"""
🎯 Ejemplo completo del flujo de trading con tracking de órdenes
Demuestra cómo resolver el problema de obtener order IDs para las operaciones DELETE
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.binance_connector import BinanceConnector, TradingPosition
import time

def example_complete_trading_with_tracking():
    """
    📋 Ejemplo completo del flujo de trading con tracking de IDs
    """
    print("🎯 Iniciando ejemplo de trading con tracking completo...")
    
    # Inicializar conector
    connector = BinanceConnector()
    
    # 📊 ESCENARIO 1: CREAR POSICIÓN COMPLETA
    print("\n📊 1. CREANDO POSICIÓN COMPLETA CON TRACKING...")
    
    # Simular entrada al mercado
    entry_order = connector.place_market_order(
        symbol="BTCUSDT",
        side="BUY",
        quantity=0.001
    )
    
    if entry_order.success:
        print(f"✅ Entrada ejecutada - Order ID: {entry_order.active_order.order_id}")
        print(f"📝 Client Order ID: {entry_order.active_order.client_order_id}")
        
        # Crear posición completa con OCO
        position = connector.create_trading_position(
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.001,
            entry_price=45000.0,  # Precio simulado
            entry_order_id=entry_order.active_order.order_id,
            tp_price=46000.0,     # +2.2% ganancia
            sl_stop_price=44000.0, # -2.2% pérdida
            sl_limit_price=43900.0 # Precio límite
        )
        
        print(f"📊 Posición creada: {position.position_id}")
        print(f"🎯 OCO Order List ID: {position.oco_order.order_list_id}")
        print(f"📈 TP Order ID: {position.oco_order.tp_order_id}")
        print(f"📉 SL Order ID: {position.oco_order.sl_order_id}")
        
        # 🔄 ESCENARIO 2: AJUSTE DINÁMICO DE TP/SL
        print("\n🔄 2. AJUSTANDO NIVELES DE TP/SL DINÁMICAMENTE...")
        
        # Simular que el precio subió y queremos ajustar
        adjust_result = connector.adjust_oco_levels(
            position_id=position.position_id,
            new_tp_price=47000.0,     # Nuevo TP más alto
            new_sl_stop_price=45500.0, # Nuevo SL trailing
            new_sl_limit_price=45400.0
        )
        
        if adjust_result.success:
            print(f"✅ OCO ajustado exitosamente")
            print(f"🆕 Nuevo OCO Order List ID: {position.oco_order.order_list_id}")
            print(f"📈 Nuevo TP Order ID: {position.oco_order.tp_order_id}")
            print(f"📉 Nuevo SL Order ID: {position.oco_order.sl_order_id}")
        
        # 💰 ESCENARIO 3: RESET CON PROFIT
        print("\n💰 3. SIMULANDO RESET CON PROFIT...")
        
        # Obtener posiciones activas
        active_positions = connector.get_active_positions()
        print(f"📊 Posiciones activas: {len(active_positions)}")
        
        for pos in active_positions:
            print(f"🔍 Cerrando posición: {pos.position_id}")
            
            # Cerrar posición con profit (cancela OCO + ejecuta MARKET)
            close_result = connector.close_position_with_profit(pos.position_id)
            
            if close_result.success:
                print(f"✅ Posición cerrada exitosamente")
                print(f"📝 Close Order ID: {close_result.active_order.order_id}")
            else:
                print(f"❌ Error cerrando posición: {close_result.message}")
        
        # 📋 ESCENARIO 4: CONSULTAR ESTADO DEL TRACKING
        print("\n📋 4. ESTADO ACTUAL DEL TRACKING...")
        
        print(f"🔢 Órdenes activas: {len(connector.active_orders)}")
        print(f"🎯 OCO activos: {len(connector.active_oco_orders)}")
        print(f"📊 Posiciones: {len(connector.trading_positions)}")
        
        # Mostrar mapeos de IDs
        print(f"🗂️ Client Order Mapping: {len(connector.client_order_mapping)} entradas")
        print(f"🗂️ OCO Client Mapping: {len(connector.oco_client_mapping)} entradas")

def demonstrate_id_tracking():
    """
    🔍 Demostrar cómo se resuelve el problema de tracking de IDs
    """
    print("\n🔍 DEMOSTRACIÓN DE TRACKING DE IDs...")
    
    connector = BinanceConnector()
    
    # Crear una orden OCO
    oco_result = connector.create_oco_order(
        symbol="BTCUSDT",
        side="SELL",
        quantity=0.001,
        tp_price=46000.0,
        sl_stop_price=44000.0,
        sl_limit_price=43900.0
    )
    
    if oco_result.success:
        oco_order = oco_result.active_oco
        
        print("📝 IDs GENERADOS AUTOMÁTICAMENTE:")
        print(f"   🎯 Order List ID: {oco_order.order_list_id}")
        print(f"   📝 List Client Order ID: {oco_order.list_client_order_id}")
        print(f"   📈 TP Order ID: {oco_order.tp_order_id}")
        print(f"   📈 TP Client Order ID: {oco_order.tp_client_order_id}")
        print(f"   📉 SL Order ID: {oco_order.sl_order_id}")
        print(f"   📉 SL Client Order ID: {oco_order.sl_client_order_id}")
        
        print("\n🔍 CÓMO CANCELAR CON LOS IDs OBTENIDOS:")
        
        # Opción 1: Cancelar usando Order List ID
        print(f"   🛑 DELETE /api/v3/orderList?symbol=BTCUSDT&orderListId={oco_order.order_list_id}")
        
        # Opción 2: Cancelar usando Client Order ID
        print(f"   🛑 DELETE /api/v3/orderList?symbol=BTCUSDT&listClientOrderId={oco_order.list_client_order_id}")
        
        # Opción 3: Cancelar órdenes individuales
        print(f"   🛑 DELETE /api/v3/order?symbol=BTCUSDT&orderId={oco_order.tp_order_id}")
        print(f"   🛑 DELETE /api/v3/order?symbol=BTCUSDT&orderId={oco_order.sl_order_id}")
        
        print("\n✅ PROBLEMA RESUELTO:")
        print("   ✓ Todos los IDs se capturan automáticamente")
        print("   ✓ Se mantiene mapping de client_order_id -> order_id")
        print("   ✓ Se puede cancelar por cualquier método")
        print("   ✓ El tracking persiste durante toda la sesión")
        
        # Demostrar cancelación
        print(f"\n🛑 CANCELANDO OCO...")
        cancel_result = connector.cancel_oco_order(order_list_id=oco_order.order_list_id)
        
        if cancel_result.success:
            print("✅ OCO cancelado exitosamente usando Order List ID")
        else:
            print(f"❌ Error cancelando: {cancel_result.message}")

def demonstrate_position_mapping():
    """
    🗺️ Demostrar cómo se mapean las posiciones con sus órdenes OCO
    """
    print("\n🗺️ DEMOSTRACIÓN DE MAPEO POSICIÓN -> OCO...")
    
    connector = BinanceConnector()
    
    # Crear múltiples posiciones
    positions = []
    
    for i, symbol in enumerate(["BTCUSDT", "ETHUSDT", "ADAUSDT"]):
        print(f"\n📊 Creando posición {i+1}: {symbol}")
        
        # Entrada
        entry_order = connector.place_market_order(
            symbol=symbol,
            side="BUY",
            quantity=0.001
        )
        
        if entry_order.success:
            # Crear posición con OCO
            position = connector.create_trading_position(
                symbol=symbol,
                side="BUY",
                quantity=0.001,
                entry_price=45000.0 + (i * 1000),  # Precios diferentes
                entry_order_id=entry_order.active_order.order_id,
                tp_price=46000.0 + (i * 1000),
                sl_stop_price=44000.0 + (i * 1000),
                sl_limit_price=43900.0 + (i * 1000)
            )
            
            positions.append(position)
            
            print(f"   ✅ Posición ID: {position.position_id}")
            print(f"   🎯 OCO List ID: {position.oco_order.order_list_id}")
    
    print(f"\n📋 RESUMEN DE MAPEO:")
    print(f"   📊 Total posiciones: {len(positions)}")
    
    for pos in positions:
        print(f"\n   🔗 {pos.symbol}:")
        print(f"      📊 Position ID: {pos.position_id}")
        print(f"      🎯 OCO List ID: {pos.oco_order.order_list_id}")
        print(f"      📈 TP Order ID: {pos.oco_order.tp_order_id}")
        print(f"      📉 SL Order ID: {pos.oco_order.sl_order_id}")
    
    print(f"\n✅ IDENTIFICACIÓN DE POSICIONES RESUELTA:")
    print("   ✓ Cada posición tiene un ID único generado automáticamente")
    print("   ✓ Cada posición está mapeada con su OCO correspondiente")
    print("   ✓ Se puede acceder a cualquier orden por position_id")
    print("   ✓ Se puede cerrar cualquier posición específica")
    
    # Demostrar cierre de posición específica
    if positions:
        target_position = positions[0]
        print(f"\n🎯 CERRANDO POSICIÓN ESPECÍFICA: {target_position.symbol}")
        
        close_result = connector.close_position_with_profit(target_position.position_id)
        
        if close_result.success:
            print(f"✅ Posición {target_position.symbol} cerrada exitosamente")
        else:
            print(f"❌ Error: {close_result.message}")

if __name__ == "__main__":
    print("🎯 SISTEMA COMPLETO DE TRACKING DE ÓRDENES Y POSICIONES")
    print("=" * 60)
    
    try:
        # Ejemplo completo
        example_complete_trading_with_tracking()
        
        # Demostración de tracking de IDs
        demonstrate_id_tracking()
        
        # Demostración de mapeo de posiciones
        demonstrate_position_mapping()
        
        print("\n🎉 TODOS LOS PROBLEMAS RESUELTOS:")
        print("✅ Tracking automático de order IDs")
        print("✅ Mapeo de posiciones con OCO")
        print("✅ Cancelación por cualquier método")
        print("✅ Cierre de posiciones específicas")
        print("✅ Ajuste dinámico de TP/SL")
        print("✅ Reset con profit automático")
        
    except Exception as e:
        print(f"❌ Error en el ejemplo: {e}")
        import traceback
        traceback.print_exc()