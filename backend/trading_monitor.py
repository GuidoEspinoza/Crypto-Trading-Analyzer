#!/usr/bin/env python3
"""🔍 Monitor Integral del Sistema de Trading

Este script unifica las funcionalidades de:
- check_missed_executions.py: Verificación de ejecuciones perdidas de TP/SL
- check_monitoring_status.py: Estado del sistema de monitoreo

Funcionalidades:
- Análisis detallado de posiciones activas
- Verificación de ejecuciones perdidas
- Estado del sistema de monitoreo
- Configuración de TP/SL
- Precios actuales vs objetivos
- Estadísticas del position manager
"""

import sys
import os
import argparse
import requests
from datetime import datetime
from typing import List, Dict, Any

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_engine.market_validator import market_validator
from trading_engine.position_manager import PositionManager
from trading_engine.paper_trader import PaperTrader
from trading_engine.config import RiskManagerConfig
from database.database import db_manager
from database.models import Trade

def main():
    """🚀 Función principal"""
    parser = argparse.ArgumentParser(
        description="Monitor Integral del Sistema de Trading",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modos de operación:
  --status          Verificar estado general del sistema (default)
  --missed          Verificar solo ejecuciones perdidas
  --detailed        Análisis detallado completo
  --summary         Solo resumen sin detalles

Ejemplos de uso:
  python3 trading_monitor.py                           # Estado general
  python3 trading_monitor.py --detailed                # Análisis completo
  python3 trading_monitor.py --missed --hours 12       # Ejecuciones perdidas (12h)
  python3 trading_monitor.py --summary                 # Solo resumen
        """
    )
    
    # Modos de operación
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--status',
        action='store_true',
        default=True,
        help='Verificar estado general del sistema (default)'
    )
    mode_group.add_argument(
        '--missed',
        action='store_true',
        help='Verificar solo ejecuciones perdidas'
    )
    mode_group.add_argument(
        '--detailed',
        action='store_true',
        help='Análisis detallado completo'
    )
    
    # Opciones adicionales
    parser.add_argument(
        '--hours', 
        type=int, 
        default=24,
        help='Horas hacia atrás para verificar ejecuciones perdidas (default: 24)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Mostrar solo resumen sin detalles'
    )
    
    args = parser.parse_args()
    
    # Determinar modo de operación
    if args.missed:
        mode = 'missed'
    elif args.detailed:
        mode = 'detailed'
    else:
        mode = 'status'
    
    print("🔍 MONITOR INTEGRAL DEL SISTEMA DE TRADING")
    print("=" * 55)
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Modo: {mode.upper()}")
    print()
    
    try:
        if mode == 'missed':
            run_missed_executions_check(args.hours, args.summary)
        elif mode == 'detailed':
            run_detailed_analysis(args.hours, args.summary)
        else:
            run_status_check()
        
        print("\n" + "=" * 55)
        print("✅ Verificación completada")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        sys.exit(1)

def run_status_check():
    """📊 Ejecutar verificación de estado general"""
    print("📊 VERIFICACIÓN DE ESTADO GENERAL")
    print("-" * 40)
    
    # Mostrar posiciones activas básicas
    show_active_positions_summary()
    
    # Verificar configuración de TP/SL
    check_tp_sl_configuration()
    
    # Verificar sistema de monitoreo
    check_monitoring_system()
    
    # Verificar precios actuales
    check_current_prices()

def run_missed_executions_check(hours: int, summary_only: bool):
    """🔍 Ejecutar verificación de ejecuciones perdidas"""
    print(f"🔍 VERIFICACIÓN DE EJECUCIONES PERDIDAS")
    print(f"📅 Analizando últimas {hours} horas...")
    print("-" * 50)
    
    # Mostrar posiciones activas
    show_active_positions_summary()
    
    # Verificar ejecuciones perdidas
    print("\n🔍 Verificando ejecuciones perdidas...")
    missed_executions = market_validator.check_missed_executions(hours)
    
    if not missed_executions:
        print(f"✅ No se detectaron ejecuciones perdidas en las últimas {hours} horas")
        print("🎯 Todas las posiciones están siendo monitoreadas correctamente")
    else:
        print(f"⚠️ Se detectaron {len(missed_executions)} ejecuciones perdidas:")
        print()
        
        if summary_only:
            show_missed_executions_summary(missed_executions)
        else:
            show_missed_executions_detailed(missed_executions)

def run_detailed_analysis(hours: int, summary_only: bool):
    """📊 Ejecutar análisis detallado completo"""
    print("📊 ANÁLISIS DETALLADO COMPLETO")
    print("-" * 40)
    
    # Análisis detallado de posiciones
    check_active_positions_detailed()
    
    # Verificar configuración
    check_tp_sl_configuration()
    
    # Verificar sistema de monitoreo
    check_monitoring_system()
    
    # Verificar precios actuales
    check_current_prices()
    
    # Verificar ejecuciones perdidas
    print(f"\n🔍 VERIFICACIÓN DE EJECUCIONES PERDIDAS ({hours}h)")
    print("-" * 50)
    
    missed_executions = market_validator.check_missed_executions(hours)
    
    if not missed_executions:
        print(f"✅ No se detectaron ejecuciones perdidas en las últimas {hours} horas")
    else:
        print(f"⚠️ Se detectaron {len(missed_executions)} ejecuciones perdidas:")
        print()
        
        if summary_only:
            show_missed_executions_summary(missed_executions)
        else:
            show_missed_executions_detailed(missed_executions)

def show_active_positions_summary():
    """📊 Mostrar resumen de posiciones activas"""
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
                return
            
            for trade in active_trades:
                # Obtener precio actual
                current_price = get_current_price(trade.symbol.replace('/', ''))
                
                # Formatear TP y SL
                tp_str = f"${trade.take_profit:.4f}" if trade.take_profit else "N/A"
                sl_str = f"${trade.stop_loss:.4f}" if trade.stop_loss else "N/A"
                
                print(f"   #{trade.id} {trade.symbol} {trade.trade_type}")
                print(f"      Entry: ${trade.entry_price:.4f} | Current: ${current_price:.4f}")
                print(f"      TP: {tp_str} | SL: {sl_str}")
                
                # Calcular distancias a TP/SL
                if current_price > 0:
                    if trade.take_profit:
                        if trade.trade_type == "BUY":
                            tp_distance = ((trade.take_profit - current_price) / current_price) * 100
                            tp_status = "📈" if tp_distance > 0 else "✅"
                        else:
                            tp_distance = ((current_price - trade.take_profit) / current_price) * 100
                            tp_status = "📈" if tp_distance > 0 else "✅"
                        print(f"      {tp_status} TP Distance: {abs(tp_distance):.2f}%")
                    
                    if trade.stop_loss:
                        if trade.trade_type == "BUY":
                            sl_distance = ((current_price - trade.stop_loss) / current_price) * 100
                            sl_status = "🛡️" if sl_distance > 0 else "⚠️"
                        else:
                            sl_distance = ((trade.stop_loss - current_price) / current_price) * 100
                            sl_status = "🛡️" if sl_distance > 0 else "⚠️"
                        print(f"      {sl_status} SL Distance: {abs(sl_distance):.2f}%")
                    
                    # Calcular PnL actual
                    if trade.trade_type == "BUY":
                        pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    else:
                        pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                    
                    pnl_status = "💚" if pnl_pct > 0 else "❤️" if pnl_pct < 0 else "💛"
                    print(f"      {pnl_status} PnL: {pnl_pct:+.2f}%")
                
                print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M')}")
                print()  # Línea en blanco entre trades
            
    except Exception as e:
        print(f"❌ Error mostrando posiciones activas: {e}")

def check_active_positions_detailed():
    """📊 Verificar posiciones activas con análisis detallado"""
    try:
        with db_manager.get_db_session() as session:
            active_trades = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).all()
            
            print(f"📊 ANÁLISIS DETALLADO DE POSICIONES: {len(active_trades)}")
            print("-" * 50)
            
            if not active_trades:
                print("   No hay posiciones activas")
                return
            
            positions_with_tp_sl = 0
            positions_without_tp_sl = 0
            total_pnl = 0.0
            
            for trade in active_trades:
                has_tp = trade.take_profit is not None
                has_sl = trade.stop_loss is not None
                
                if has_tp or has_sl:
                    positions_with_tp_sl += 1
                else:
                    positions_without_tp_sl += 1
                
                # Obtener precio actual
                current_price = get_current_price(trade.symbol.replace('/', ''))
                
                # Calcular PnL actual
                if current_price > 0:
                    if trade.trade_type == "BUY":
                        pnl = (current_price - trade.entry_price) * trade.quantity
                        pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                    else:
                        pnl = (trade.entry_price - current_price) * trade.quantity
                        pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                    total_pnl += pnl
                else:
                    pnl = 0
                    pnl_pct = 0
                    current_price = 0
                
                print(f"\n   🎯 Trade #{trade.id} - {trade.symbol} ({trade.trade_type})")
                print(f"      Strategy: {trade.strategy_name}")
                print(f"      Entry: ${trade.entry_price:.4f} | Current: ${current_price:.4f}")
                print(f"      PnL: ${pnl:.2f} ({pnl_pct:.2f}%)")
                print(f"      Quantity: {trade.quantity:.4f}")
                
                if has_tp:
                    tp_distance = abs(current_price - trade.take_profit) / trade.take_profit * 100
                    print(f"      ✅ Take Profit: ${trade.take_profit:.4f} (Distance: {tp_distance:.2f}%)")
                else:
                    print(f"      ❌ Take Profit: No configurado")
                
                if has_sl:
                    sl_distance = abs(current_price - trade.stop_loss) / trade.stop_loss * 100
                    print(f"      ✅ Stop Loss: ${trade.stop_loss:.4f} (Distance: {sl_distance:.2f}%)")
                else:
                    print(f"      ❌ Stop Loss: No configurado")
                
                print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Verificar si debería haberse ejecutado
                if has_tp and trade.trade_type == "BUY" and current_price >= trade.take_profit:
                    print(f"      ⚠️  ALERTA: TP debería haberse ejecutado!")
                elif has_tp and trade.trade_type == "SELL" and current_price <= trade.take_profit:
                    print(f"      ⚠️  ALERTA: TP debería haberse ejecutado!")
                
                if has_sl and trade.trade_type == "BUY" and current_price <= trade.stop_loss:
                    print(f"      ⚠️  ALERTA: SL debería haberse ejecutado!")
                elif has_sl and trade.trade_type == "SELL" and current_price >= trade.stop_loss:
                    print(f"      ⚠️  ALERTA: SL debería haberse ejecutado!")
            
            print(f"\n📊 RESUMEN DE CONFIGURACIÓN:")
            print(f"   Posiciones con TP/SL: {positions_with_tp_sl}")
            print(f"   Posiciones sin TP/SL: {positions_without_tp_sl}")
            print(f"   PnL total actual: ${total_pnl:.2f}")
            
            if positions_without_tp_sl > 0:
                print(f"   ⚠️  {positions_without_tp_sl} posiciones sin protección!")
            
    except Exception as e:
        print(f"❌ Error verificando posiciones: {e}")

def check_tp_sl_configuration():
    """🎯 Verificar configuración de TP/SL"""
    print(f"\n🎯 VERIFICACIÓN DE CONFIGURACIÓN TP/SL")
    print("-" * 40)
    
    try:
        print(f"   ATR Multiplier Min: {RiskManagerConfig.ATR_MULTIPLIER_MIN}x")
        print(f"   ATR Multiplier Max: {RiskManagerConfig.ATR_MULTIPLIER_MAX}x")
        print(f"   ATR Default: {RiskManagerConfig.ATR_DEFAULT}x")
        print(f"   Trailing Stop Activation: {RiskManagerConfig.TRAILING_STOP_ACTIVATION}%")
        print(f"   Breakeven Threshold: {RiskManagerConfig.BREAKEVEN_THRESHOLD}%")
        print(f"   Max riesgo por trade: {RiskManagerConfig.MAX_RISK_PER_TRADE}%")
        print(f"   Max riesgo diario: {RiskManagerConfig.MAX_DAILY_RISK}%")
        print(f"   Max drawdown: {RiskManagerConfig.MAX_DRAWDOWN_THRESHOLD}%")
        
        print(f"\n   ✅ Configuración de Risk Manager encontrada")
        
    except Exception as e:
        print(f"   ❌ Error verificando configuración: {e}")

def check_current_prices():
    """💰 Verificar precios actuales"""
    print(f"\n💰 VERIFICACIÓN DE PRECIOS ACTUALES")
    print("-" * 40)
    
    try:
        with db_manager.get_db_session() as session:
            active_trades = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).all()
            
            if not active_trades:
                print("   No hay posiciones activas para verificar precios")
                return
            
            symbols = list(set(trade.symbol.replace('/', '') for trade in active_trades))
            
            print(f"   Verificando precios para {len(symbols)} símbolos...")
            
            for symbol in symbols:
                price = get_current_price(symbol)
                if price > 0:
                    print(f"   ✅ {symbol}: ${price:.4f}")
                else:
                    print(f"   ❌ {symbol}: Error obteniendo precio")
                    
    except Exception as e:
        print(f"   ❌ Error verificando precios: {e}")

def check_monitoring_system():
    """🔄 Verificar sistema de monitoreo"""
    print(f"\n🔄 VERIFICACIÓN DEL SISTEMA DE MONITOREO")
    print("-" * 45)
    
    try:
        # Verificar si el position manager está funcionando
        paper_trader = PaperTrader()
        position_manager = PositionManager(paper_trader)
        
        # Obtener posiciones activas
        active_positions = position_manager.get_active_positions()
        
        print(f"   ✅ Position Manager: Activo")
        print(f"   📊 Posiciones monitoreadas: {len(active_positions)}")
        
        # Verificar cache de posiciones
        cache_size = len(getattr(position_manager, 'positions_cache', {}))
        print(f"   💾 Cache de posiciones: {cache_size} entradas")
        
        # Verificar estadísticas
        stats = position_manager.get_statistics()
        print(f"   📈 TP ejecutados: {stats.get('take_profits_executed', 0)}")
        print(f"   📉 SL ejecutados: {stats.get('stop_losses_executed', 0)}")
        print(f"   🔄 Trailing stops activos: {stats.get('trailing_stops_activated', 0)}")
        
    except Exception as e:
        print(f"   ❌ Error verificando sistema de monitoreo: {e}")

def show_missed_executions_summary(missed_executions: List[Any]):
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

def show_missed_executions_detailed(missed_executions: List[Any]):
    """📊 Mostrar reporte detallado de ejecuciones perdidas"""
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

def get_current_price(symbol: str) -> float:
    """💰 Obtener precio actual de Binance"""
    try:
        url = "https://api.binance.com/api/v3/ticker/price"
        params = {'symbol': symbol}
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return float(data['price'])
        
    except Exception:
        return 0.0

if __name__ == "__main__":
    main()