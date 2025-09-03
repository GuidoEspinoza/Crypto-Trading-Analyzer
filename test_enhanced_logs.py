#!/usr/bin/env python3
"""
🧪 Prueba de Logs Mejorados

Esta prueba demuestra las mejoras implementadas en los logs:
1. Balance de USDT después de cada compra/venta
2. Logs detallados del cierre automático (TP/SL/Trailing Stop)
"""

import sys
import os
sys.path.append('backend')

import logging
from trading_engine.paper_trader import PaperTrader
from trading_engine.position_manager import PositionManager
from trading_engine.enhanced_strategies import TradingSignal
from database.database import db_manager
from database.models import Trade
from datetime import datetime

# Configurar logging para ver todos los mensajes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_enhanced_logs():
    """🧪 Probar los logs mejorados"""
    print("\n🧪 PRUEBA DE LOGS MEJORADOS")
    print("═" * 60)
    
    # Inicializar componentes
    paper_trader = PaperTrader(1000.0)
    position_manager = PositionManager(paper_trader)
    
    print("\n1️⃣ PROBANDO LOGS DE COMPRA CON BALANCE USDT")
    print("-" * 50)
    
    # Crear señal de compra
    buy_signal = TradingSignal(
        symbol="BTC/USDT",
        signal_type="BUY",
        price=50000.0,
        confidence_score=0.85,
        strength="Strong",
        strategy_name="test_strategy",
        timestamp=datetime.now(),
        notes="Test buy with enhanced logging"
    )
    
    # Ejecutar compra
    result = paper_trader.execute_signal(buy_signal)
    print(f"Resultado: {result.message}")
    
    print("\n2️⃣ PROBANDO LOGS DE VENTA CON BALANCE USDT")
    print("-" * 50)
    
    # Crear señal de venta
    sell_signal = TradingSignal(
        symbol="BTC/USDT",
        signal_type="SELL",
        price=52000.0,
        confidence_score=0.80,
        strength="Moderate",
        strategy_name="test_strategy",
        timestamp=datetime.now(),
        notes="Test sell with enhanced logging"
    )
    
    # Ejecutar venta
    result = paper_trader.execute_signal(sell_signal)
    print(f"Resultado: {result.message}")
    
    print("\n3️⃣ PROBANDO LOGS DE CIERRE AUTOMÁTICO")
    print("-" * 50)
    
    # Crear un trade manual para simular cierre automático
    try:
        with db_manager.get_db_session() as session:
            # Crear trade de prueba
            test_trade = Trade(
                symbol="ETH/USDT",
                strategy_name="test_strategy",
                trade_type="BUY",
                entry_price=3000.0,
                quantity=0.1,
                entry_value=300.0,
                stop_loss=2850.0,  # -5%
                take_profit=3150.0,  # +5%
                status="OPEN",
                is_paper_trade=True,
                timeframe="1h",
                confidence_score=0.8,
                notes="Test trade for auto-close logging"
            )
            
            session.add(test_trade)
            session.commit()
            
            trade_id = test_trade.id
            print(f"✅ Trade de prueba creado: ID {trade_id}")
            
            # Simular activación de Take Profit
            print("\n📈 SIMULANDO ACTIVACIÓN DE TAKE PROFIT")
            success = position_manager.close_position(trade_id, 3150.0, "TAKE_PROFIT")
            print(f"Resultado del cierre: {'✅ Éxito' if success else '❌ Error'}")
            
            # Crear otro trade para simular Stop Loss
            test_trade2 = Trade(
                symbol="ADA/USDT",
                strategy_name="test_strategy",
                trade_type="BUY",
                entry_price=1.0,
                quantity=100.0,
                entry_value=100.0,
                stop_loss=0.95,  # -5%
                take_profit=1.05,  # +5%
                status="OPEN",
                is_paper_trade=True,
                timeframe="1h",
                confidence_score=0.7,
                notes="Test trade for stop loss logging"
            )
            
            session.add(test_trade2)
            session.commit()
            
            trade_id2 = test_trade2.id
            print(f"\n✅ Segundo trade de prueba creado: ID {trade_id2}")
            
            # Simular activación de Stop Loss
            print("\n📉 SIMULANDO ACTIVACIÓN DE STOP LOSS")
            success = position_manager.close_position(trade_id2, 0.95, "STOP_LOSS")
            print(f"Resultado del cierre: {'✅ Éxito' if success else '❌ Error'}")
            
            # Crear tercer trade para simular Trailing Stop
            test_trade3 = Trade(
                symbol="DOT/USDT",
                strategy_name="test_strategy",
                trade_type="BUY",
                entry_price=20.0,
                quantity=5.0,
                entry_value=100.0,
                stop_loss=19.0,  # -5%
                take_profit=21.0,  # +5%
                status="OPEN",
                is_paper_trade=True,
                timeframe="1h",
                confidence_score=0.9,
                notes="Test trade for trailing stop logging"
            )
            
            session.add(test_trade3)
            session.commit()
            
            trade_id3 = test_trade3.id
            print(f"\n✅ Tercer trade de prueba creado: ID {trade_id3}")
            
            # Simular activación de Trailing Stop
            print("\n🎯 SIMULANDO ACTIVACIÓN DE TRAILING STOP")
            success = position_manager.close_position(trade_id3, 20.5, "TRAILING_STOP")
            print(f"Resultado del cierre: {'✅ Éxito' if success else '❌ Error'}")
            
    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
    
    print("\n🎉 PRUEBA DE LOGS MEJORADOS COMPLETADA")
    print("═" * 60)
    print("\n📋 RESUMEN DE MEJORAS IMPLEMENTADAS:")
    print("✅ Balance de USDT mostrado después de cada compra/venta")
    print("✅ Logs detallados de cierre automático con:")
    print("   • Tipo de activación (TP/SL/Trailing Stop)")
    print("   • Información completa de la operación")
    print("   • Resultado (ganancia/pérdida) con porcentaje")
    print("   • Balance actual de USDT")
    print("   • Valor total del portafolio")
    print("   • Formato visual mejorado con emojis y separadores")

if __name__ == "__main__":
    test_enhanced_logs()