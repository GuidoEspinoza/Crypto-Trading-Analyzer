#!/usr/bin/env python3
"""
Test para verificar que el paper_trader asigna automáticamente TP/SL
cuando faltan en las señales de trading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.paper_trader import PaperTrader
from core.enhanced_strategies import TradingSignal, EnhancedSignal
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tp_sl_assignment():
    """Test que verifica la asignación automática de TP/SL"""
    print("🧪 TESTING: Asignación automática de TP/SL")
    print("=" * 50)
    
    # Inicializar paper trader
    paper_trader = PaperTrader()
    
    # Test 1: Señal sin TP/SL - debería asignarlos automáticamente
    print("\n📋 Test 1: Señal básica sin TP/SL")
    signal_without_tp_sl = TradingSignal(
        symbol="BTCUSDT",
        signal_type="BUY",
        price=50000.0,
        confidence_score=80.0,  # Usar 80% en lugar de 0.8
        strength="Strong",
        strategy_name="test_strategy",
        timestamp=datetime.now()
    )
    
    print(f"   Señal original - TP: {getattr(signal_without_tp_sl, 'take_profit_price', None)}")
    print(f"   Señal original - SL: {getattr(signal_without_tp_sl, 'stop_loss_price', None)}")
    
    # Ejecutar trade
    result = paper_trader.execute_signal(signal_without_tp_sl)
    
    if result.success:
        print(f"   ✅ Trade ejecutado exitosamente")
        print(f"   Trade ID: {result.trade_id}")
        print(f"   Entry Price: ${result.entry_price:.2f}")
        print(f"   Quantity: {result.quantity}")
        
        if result.trade_id:
            print(f"   🎯 SUCCESS: Trade creado con ID {result.trade_id}")
        else:
            print(f"   ❌ FAIL: No se generó trade_id")
    else:
        print(f"   ❌ Error ejecutando trade: {result.message}")
    
    # Test 2: Señal con TP/SL ya configurados
    print("\n📋 Test 2: Señal con TP/SL preconfigurados")
    signal_with_tp_sl = EnhancedSignal(
        symbol="ETHUSDT",
        signal_type="BUY",
        price=3000.0,
        confidence_score=90.0,  # Usar 90% en lugar de 0.9
        strength="Strong",
        strategy_name="test_strategy",
        timestamp=datetime.now(),
        take_profit_price=3150.0,  # +5%
        stop_loss_price=2850.0     # -5%
    )
    
    print(f"   Señal original - TP: ${signal_with_tp_sl.take_profit_price}")
    print(f"   Señal original - SL: ${signal_with_tp_sl.stop_loss_price}")
    
    # Ejecutar trade
    result = paper_trader.execute_signal(signal_with_tp_sl)
    
    if result.success:
        print(f"   ✅ Trade ejecutado exitosamente")
        print(f"   Trade ID: {result.trade_id}")
        print(f"   Entry Price: ${result.entry_price:.2f}")
        print(f"   Quantity: {result.quantity}")
        
        if result.trade_id:
            print(f"   🎯 SUCCESS: Trade creado con ID {result.trade_id}")
        else:
            print(f"   ❌ FAIL: No se generó trade_id")
    else:
        print(f"   ❌ Error ejecutando trade: {result.message}")
    
    # Test 3: Verificar que las posiciones aparecen en el portfolio
    print("\n📋 Test 3: Verificación del portfolio")
    portfolio = paper_trader.get_portfolio_summary()
    print(f"   Posiciones activas: {len(portfolio.get('active_positions', []))}")
    print(f"   Balance total: ${portfolio.get('total_balance', 0):.2f}")
    
    active_positions = portfolio.get('active_positions', [])
    for i, pos in enumerate(active_positions, 1):
        print(f"   Posición {i}: {pos.get('symbol')} - TP: {pos.get('take_profit', 'N/A')} - SL: {pos.get('stop_loss', 'N/A')}")
    
    print("\n🎯 RESUMEN DEL TEST:")
    print("=" * 30)
    
    # Contar posiciones con TP/SL
    positions_with_tp_sl = 0
    positions_without_tp_sl = 0
    
    for pos in active_positions:
        if pos.get('take_profit') and pos.get('stop_loss'):
            positions_with_tp_sl += 1
        else:
            positions_without_tp_sl += 1
    
    print(f"   Posiciones con TP/SL: {positions_with_tp_sl}")
    print(f"   Posiciones sin TP/SL: {positions_without_tp_sl}")
    
    if positions_without_tp_sl == 0:
        print(f"   ✅ SUCCESS: Todas las posiciones tienen TP/SL")
        return True
    else:
        print(f"   ❌ FAIL: {positions_without_tp_sl} posiciones sin TP/SL")
        return False

if __name__ == "__main__":
    try:
        success = test_tp_sl_assignment()
        if success:
            print("\n🎉 TODOS LOS TESTS PASARON")
            sys.exit(0)
        else:
            print("\n💥 ALGUNOS TESTS FALLARON")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR EN EL TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)