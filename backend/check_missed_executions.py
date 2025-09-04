#!/usr/bin/env python3
"""🔍 Script para verificar ejecuciones perdidas de TP/SL

Este script:
- Analiza las posiciones activas
- Verifica si los precios han tocado TP/SL sin ejecutarse
- Genera un reporte detallado
- Permite especificar el período de análisis
"""

import sys
import os
import argparse
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_engine.market_validator import market_validator
from trading_engine.position_manager import PositionManager
from database.database import db_manager
from database.models import Trade

def main():
    """🚀 Función principal"""
    parser = argparse.ArgumentParser(
        description="Verificar ejecuciones perdidas de TP/SL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python3 check_missed_executions.py                    # Últimas 24 horas
  python3 check_missed_executions.py --hours 12         # Últimas 12 horas
  python3 check_missed_executions.py --hours 48         # Últimas 48 horas
  python3 check_missed_executions.py --summary          # Solo resumen
        """
    )
    
    parser.add_argument(
        '--hours', 
        type=int, 
        default=24,
        help='Horas hacia atrás para verificar (default: 24)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Mostrar solo resumen sin detalles'
    )
    
    args = parser.parse_args()
    
    print("🔍 VERIFICADOR DE EJECUCIONES PERDIDAS")
    print("=" * 50)
    print(f"📅 Analizando últimas {args.hours} horas...")
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Mostrar posiciones activas primero
        show_active_positions()
        
        # Verificar ejecuciones perdidas
        print("🔍 Verificando ejecuciones perdidas...")
        missed_executions = market_validator.check_missed_executions(args.hours)
        
        if not missed_executions:
            print(f"✅ No se detectaron ejecuciones perdidas en las últimas {args.hours} horas")
            print("🎯 Todas las posiciones están siendo monitoreadas correctamente")
        else:
            print(f"⚠️ Se detectaron {len(missed_executions)} ejecuciones perdidas:")
            print()
            
            if args.summary:
                show_summary(missed_executions)
            else:
                show_detailed_report(missed_executions)
        
        print("\n" + "=" * 50)
        print("✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        sys.exit(1)

def show_active_positions():
    """📊 Mostrar posiciones activas"""
    try:
        with db_manager.get_db_session() as session:
            active_trades = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).all()
            
            print(f"📊 POSICIONES ACTIVAS: {len(active_trades)}")
            print("-" * 30)
            
            if not active_trades:
                print("   No hay posiciones activas")
            else:
                for trade in active_trades:
                    tp_str = f"${trade.take_profit:.4f}" if trade.take_profit else "N/A"
                    sl_str = f"${trade.stop_loss:.4f}" if trade.stop_loss else "N/A"
                    
                    print(f"   #{trade.id} {trade.symbol} {trade.trade_type}")
                    print(f"      Entry: ${trade.entry_price:.4f} | TP: {tp_str} | SL: {sl_str}")
                    print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M')}")
            
            print()
            
    except Exception as e:
        print(f"❌ Error mostrando posiciones activas: {e}")

def show_summary(missed_executions):
    """📋 Mostrar resumen de ejecuciones perdidas"""
    total_missed_pnl = sum(missed.potential_pnl_missed for missed in missed_executions)
    
    tp_count = sum(1 for missed in missed_executions if missed.target_type == "TP")
    sl_count = sum(1 for missed in missed_executions if missed.target_type == "SL")
    
    print("📋 RESUMEN:")
    print(f"   Total ejecuciones perdidas: {len(missed_executions)}")
    print(f"   Take Profits perdidos: {tp_count}")
    print(f"   Stop Losses perdidos: {sl_count}")
    print(f"   PnL total perdido: ${total_missed_pnl:.2f}")
    
    if missed_executions:
        print("\n📊 POR SÍMBOLO:")
        symbols = {}
        for missed in missed_executions:
            if missed.symbol not in symbols:
                symbols[missed.symbol] = {'count': 0, 'pnl': 0.0}
            symbols[missed.symbol]['count'] += 1
            symbols[missed.symbol]['pnl'] += missed.potential_pnl_missed
        
        for symbol, data in symbols.items():
            print(f"   {symbol}: {data['count']} ejecuciones, ${data['pnl']:.2f} PnL perdido")

def show_detailed_report(missed_executions):
    """📊 Mostrar reporte detallado"""
    total_missed_pnl = 0.0
    
    for i, missed in enumerate(missed_executions, 1):
        print(f"{i}. 🎯 {missed.symbol} (Trade #{missed.trade_id})")
        print(f"   Tipo: {'🟢 Take Profit' if missed.target_type == 'TP' else '🔴 Stop Loss'}")
        print(f"   Precio objetivo: ${missed.target_price:.4f}")
        print(f"   Precio alcanzado: ${missed.actual_price_reached:.4f}")
        print(f"   Timestamp: {missed.timestamp_reached.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Precio actual: ${missed.current_price:.4f}")
        print(f"   PnL perdido: ${missed.potential_pnl_missed:.2f}")
        print(f"   Razón: {missed.reason}")
        print()
        
        total_missed_pnl += missed.potential_pnl_missed
    
    print(f"💰 TOTAL PnL PERDIDO: ${total_missed_pnl:.2f}")
    print(f"📊 EJECUCIONES PERDIDAS: {len(missed_executions)}")

if __name__ == "__main__":
    main()