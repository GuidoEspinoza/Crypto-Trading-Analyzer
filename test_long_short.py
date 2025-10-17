#!/usr/bin/env python3
"""
Test script para verificar funcionalidad LONG/SHORT del Paper Trader
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.paper_trader import PaperTrader
from src.core.enhanced_strategies import TradingSignal
from src.config.main_config import GLOBAL_SYMBOLS
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_test_signal(symbol: str, signal_type: str, price: float, confidence: float = 85.0) -> TradingSignal:
    """Crear señal de prueba"""
    return TradingSignal(
        symbol=symbol,
        signal_type=signal_type,
        price=price,
        confidence_score=confidence,
        strength="Strong",
        strategy_name="TEST_STRATEGY",
        timestamp=datetime.now(),
        notes=f"Test {signal_type} signal"
    )

def test_long_short_functionality():
    """Probar funcionalidad LONG/SHORT completa"""
    
    print("🧪 === INICIANDO PRUEBAS LONG/SHORT ===")
    
    # Inicializar Paper Trader
    trader = PaperTrader(initial_balance=1000.0)
    
    # Resetear portfolio para empezar limpio
    trader.reset_portfolio()
    
    print(f"\n💰 Balance inicial: ${trader.get_balance('USD'):.2f}")
    
    # === PRUEBA 1: Abrir posición LONG (BUY) ===
    print("\n🟢 === PRUEBA 1: Abrir posición LONG (BUY) ===")
    gold_price = 2000.0
    buy_signal = create_test_signal("GOLD", "BUY", gold_price, 85.0)
    
    result = trader.execute_signal(buy_signal)
    print(f"Resultado BUY: {result.message}")
    print(f"Balance después de BUY: ${trader.get_balance('USD'):.2f}")
    
    # Mostrar posiciones abiertas
    positions = trader.get_open_positions()
    print(f"Posiciones abiertas: {len(positions)}")
    for pos in positions:
        print(f"  - {pos['symbol']}: {pos['trade_type']} | Cantidad: {pos['quantity']:.6f} | Precio: ${pos['entry_price']:.2f}")
    
    # === PRUEBA 2: Intentar abrir posición SHORT (SELL) en el mismo símbolo ===
    print("\n🔴 === PRUEBA 2: Cambiar a posición SHORT (SELL) ===")
    gold_price_sell = 1980.0
    sell_signal = create_test_signal("GOLD", "SELL", gold_price_sell, 87.0)
    
    result = trader.execute_signal(sell_signal)
    print(f"Resultado SELL: {result.message}")
    print(f"Balance después de SELL: ${trader.get_balance('USD'):.2f}")
    
    # Mostrar posiciones abiertas
    positions = trader.get_open_positions()
    print(f"Posiciones abiertas: {len(positions)}")
    for pos in positions:
        print(f"  - {pos['symbol']}: {pos['trade_type']} | Cantidad: {pos['quantity']:.6f} | Precio: ${pos['entry_price']:.2f}")
    
    # === PRUEBA 3: Abrir posición en otro símbolo ===
    print("\n🟡 === PRUEBA 3: Abrir posición LONG en otro símbolo ===")
    silver_price = 25.0
    silver_buy_signal = create_test_signal("SILVER", "BUY", silver_price, 86.0)
    
    result = trader.execute_signal(silver_buy_signal)
    print(f"Resultado SILVER BUY: {result.message}")
    print(f"Balance después de SILVER BUY: ${trader.get_balance('USD'):.2f}")
    
    # Mostrar todas las posiciones
    positions = trader.get_open_positions()
    print(f"Posiciones abiertas: {len(positions)}")
    for pos in positions:
        print(f"  - {pos['symbol']}: {pos['trade_type']} | Cantidad: {pos['quantity']:.6f} | Precio: ${pos['entry_price']:.2f}")
    
    # === PRUEBA 4: Cambiar SILVER de LONG a SHORT ===
    print("\n🔄 === PRUEBA 4: Cambiar SILVER de LONG a SHORT ===")
    silver_price_sell = 24.0
    silver_sell_signal = create_test_signal("SILVER", "SELL", silver_price_sell, 88.0)
    
    result = trader.execute_signal(silver_sell_signal)
    print(f"Resultado SILVER SELL: {result.message}")
    print(f"Balance después de SILVER SELL: ${trader.get_balance('USD'):.2f}")
    
    # Mostrar todas las posiciones
    positions = trader.get_open_positions()
    print(f"Posiciones abiertas: {len(positions)}")
    for pos in positions:
        print(f"  - {pos['symbol']}: {pos['trade_type']} | Cantidad: {pos['quantity']:.6f} | Precio: ${pos['entry_price']:.2f}")
    
    # === PRUEBA 5: Cerrar todas las posiciones ===
    print("\n❌ === PRUEBA 5: Cerrar todas las posiciones ===")
    
    # Cerrar GOLD SHORT
    gold_close_price = 1970.0
    gold_close_signal = create_test_signal("GOLD", "BUY", gold_close_price, 85.0)  # BUY para cerrar SHORT
    result = trader.execute_signal(gold_close_signal)
    print(f"Cerrar GOLD SHORT: {result.message}")
    
    # Cerrar SILVER SHORT
    silver_close_price = 23.5
    silver_close_signal = create_test_signal("SILVER", "BUY", silver_close_price, 85.0)  # BUY para cerrar SHORT
    result = trader.execute_signal(silver_close_signal)
    print(f"Cerrar SILVER SHORT: {result.message}")
    
    print(f"\n💰 Balance final: ${trader.get_balance('USD'):.2f}")
    
    # Mostrar resumen del portfolio
    try:
        portfolio_summary = trader.get_portfolio_summary()
        print(f"\n📊 === RESUMEN FINAL ===")
        if 'balances' in portfolio_summary:
            print(f"Balance USD: ${portfolio_summary['balances']['USD']:.2f}")
        else:
            print(f"Balance USD: ${trader.get_balance('USD'):.2f}")
        print(f"Valor total del portfolio: ${portfolio_summary.get('total_value', 0):.2f}")
        print(f"Posiciones abiertas: {len(trader.get_open_positions())}")
    except Exception as e:
        print(f"Error en resumen del portfolio: {e}")
        print(f"Balance USD: ${trader.get_balance('USD'):.2f}")
        print(f"Posiciones abiertas: {len(trader.get_open_positions())}")
    
    # Mostrar historial de trades
    trade_history = trader.get_trade_history()
    print(f"\n📈 === HISTORIAL DE TRADES ===")
    for trade in trade_history:
        pnl_str = f"PnL: ${trade['pnl']:.2f}" if trade['pnl'] is not None else "PnL: Pendiente"
        print(f"  {trade['symbol']} | {trade['trade_type']} | {trade['status']} | {pnl_str}")
    
    print("\n✅ === PRUEBAS COMPLETADAS ===")

if __name__ == "__main__":
    test_long_short_functionality()