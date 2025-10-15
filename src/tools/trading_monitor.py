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
import time
from datetime import datetime
from typing import List, Dict, Any

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.market_validator import market_validator
from src.core.position_manager import PositionManager
from src.config.main_config import TradingBotConfig, APIConfig
from src.core.paper_trader import PaperTrader
from src.config.main_config import TradingProfiles
from src.config.main_config import TradingBotConfig, APIConfig, MonitoringConfig, CacheConfig
from src.database.database import db_manager
from src.database.models import Trade

class TradingMonitor:
    """Monitor de trading para supervisar el bot"""
    
    def __init__(self, trading_bot):
        self.trading_bot = trading_bot
        print("📊 Trading Monitor inicializado")
    
    def start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        print("🔍 Iniciando monitoreo del sistema...")
        # Aquí se puede agregar lógica de monitoreo en tiempo real
        
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
        default=MonitoringConfig.DEFAULT_HOURS_BACK,
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
    
    # Mostrar resumen de portfolio (balance inicial y métricas actuales)
    try:
        try:
            initial_balance_db = db_manager.get_global_initial_balance()
        except Exception:
            initial_balance_db = 0.0
        
        paper = PaperTrader()
        perf = paper.calculate_portfolio_performance()
        total_value = perf.get('total_value', 0.0)
        total_pnl = perf.get('total_pnl', 0.0)
        total_return_pct = perf.get('total_return_percentage', 0.0)
        
        print("💼 RESUMEN DEL PORTFOLIO")
        print(f"   💰 Balance inicial (DB): ${initial_balance_db:,.2f}")
        print(f"   📈 Valor actual del portfolio: ${total_value:,.2f}")
        print(f"   💵 PnL total: ${total_pnl:,.2f} ({total_return_pct:+.2f}%)")
        print("-" * 40)
    except Exception as e:
        print(f"⚠️ No se pudo obtener el resumen del portfolio: {e}")
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
            
            total_pnl_usdt = 0.0
            
            for trade in active_trades:
                # Obtener precio actual
                current_price = get_current_price(trade.symbol.replace('/', ''))
                
                # Calcular porcentajes de TP y SL configurados
                tp_pct_str = "N/A"
                sl_pct_str = "N/A"
                
                if trade.take_profit and trade.entry_price > 0:
                    if trade.trade_type == "BUY":
                        tp_pct = ((trade.take_profit - trade.entry_price) / trade.entry_price) * 100
                    else:
                        tp_pct = ((trade.entry_price - trade.take_profit) / trade.entry_price) * 100
                    tp_pct_str = f"{tp_pct:.2f}%"
                
                if trade.stop_loss and trade.entry_price > 0:
                    if trade.trade_type == "BUY":
                        sl_pct = ((trade.stop_loss - trade.entry_price) / trade.entry_price) * 100
                    else:
                        sl_pct = ((trade.entry_price - trade.stop_loss) / trade.entry_price) * 100
                    sl_pct_str = f"{abs(sl_pct):.2f}%"
                
                # Formatear TP y SL
                tp_str = f"${trade.take_profit:.4f}" if trade.take_profit else "N/A"
                sl_str = f"${trade.stop_loss:.4f}" if trade.stop_loss else "N/A"
                
                print(f"   #{trade.id} {trade.symbol} {trade.trade_type}")
                print(f"      Entry: ${trade.entry_price:.4f} | Current: ${current_price:.4f}")
                print(f"      TP: {tp_str} ({tp_pct_str}) | SL: {sl_str} ({sl_pct_str})")
                
                # Calcular ganancias y pérdidas potenciales
                if current_price > 0:
                    # Calcular ganancia potencial en TP
                    if trade.take_profit:
                        if trade.trade_type == "BUY":
                            tp_gain_usdt = (trade.take_profit - trade.entry_price) * trade.quantity
                        else:
                            tp_gain_usdt = (trade.entry_price - trade.take_profit) * trade.quantity
                        print(f"      Ganancia potencial: ${tp_gain_usdt:.2f} USDT")
                    
                    # Calcular pérdida potencial en SL
                    if trade.stop_loss:
                        if trade.trade_type == "BUY":
                            sl_loss_usdt = (trade.stop_loss - trade.entry_price) * trade.quantity
                        else:
                            sl_loss_usdt = (trade.entry_price - trade.stop_loss) * trade.quantity
                        print(f"      Pérdida potencial: ${sl_loss_usdt:.2f} USDT")
                    
                    # Calcular distancias a TP/SL
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
                        pnl_usdt = (current_price - trade.entry_price) * trade.quantity
                    else:
                        pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                        pnl_usdt = (trade.entry_price - current_price) * trade.quantity
                    
                    pnl_status = "💚" if pnl_pct > 0 else "❤️" if pnl_pct < 0 else "💛"
                    print(f"      {pnl_status} PnL: {pnl_pct:+.2f}% ({pnl_usdt:+.2f} USDT)")
                    
                    # Sumar al total
                    total_pnl_usdt += pnl_usdt
                
                print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M')}")
                print()  # Línea en blanco entre trades
            
            # Mostrar total del portafolio
            print("-" * 30)
            total_status = "💚" if total_pnl_usdt > 0 else "❤️" if total_pnl_usdt < 0 else "💛"
            print(f"💼 TOTAL PORTAFOLIO: {total_status} {total_pnl_usdt:+.2f} USDT")
            print()
            
    except Exception as e:
        print(f"❌ Error mostrando posiciones activas: {e}")

def check_active_positions_detailed():
    """📊 Verificar posiciones activas con análisis detallado"""
    try:
        with db_manager.get_db_session() as session:
            active_trades = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).order_by(Trade.entry_time.desc()).all()
            
            print(f"📊 ANÁLISIS DETALLADO DE POSICIONES: {len(active_trades)}")
            print("-" * 50)
            
            if not active_trades:
                print("   No hay posiciones activas")
                return
            
            positions_with_tp_sl = 0
            positions_without_tp = 0
            positions_without_sl = 0
            positions_without_both = 0
            pending_executions = 0
            total_pnl = 0.0
            trades_without_tp = []
            trades_without_sl = []
            
            for trade in active_trades:
                has_tp = trade.take_profit is not None and trade.take_profit > 0
                has_sl = trade.stop_loss is not None and trade.stop_loss > 0
                
                # Contar posiciones sin TP/SL
                if not has_tp:
                    positions_without_tp += 1
                    trades_without_tp.append(trade)
                if not has_sl:
                    positions_without_sl += 1
                    trades_without_sl.append(trade)
                if not has_tp and not has_sl:
                    positions_without_both += 1
                if has_tp or has_sl:
                    positions_with_tp_sl += 1
                
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
                
                # Verificar ejecuciones pendientes
                tp_alert = ""
                sl_alert = ""
                
                if has_tp:
                    if (trade.trade_type == "BUY" and current_price >= trade.take_profit) or \
                       (trade.trade_type == "SELL" and current_price <= trade.take_profit):
                        tp_alert = " 🚨 TP PENDIENTE"
                        pending_executions += 1
                
                if has_sl:
                    if (trade.trade_type == "BUY" and current_price <= trade.stop_loss) or \
                       (trade.trade_type == "SELL" and current_price >= trade.stop_loss):
                        sl_alert = " 🚨 SL PENDIENTE"
                        pending_executions += 1
                
                print(f"\n   🎯 Trade #{trade.id} - {trade.symbol} ({trade.trade_type})")
                print(f"      Strategy: {trade.strategy_name}")
                print(f"      Entry: ${trade.entry_price:.4f} | Current: ${current_price:.4f}")
                print(f"      PnL: ${pnl:.2f} ({pnl_pct:.2f}%)")
                print(f"      Quantity: {trade.quantity:.4f}")
                
                if has_tp:
                    tp_distance = abs(current_price - trade.take_profit) / trade.take_profit * 100
                    print(f"      ✅ Take Profit: ${trade.take_profit:.4f} (Distance: {tp_distance:.2f}%){tp_alert}")
                else:
                    print(f"      ❌ Take Profit: No configurado")
                
                if has_sl:
                    sl_distance = abs(current_price - trade.stop_loss) / trade.stop_loss * 100
                    print(f"      ✅ Stop Loss: ${trade.stop_loss:.4f} (Distance: {sl_distance:.2f}%){sl_alert}")
                else:
                    print(f"      ❌ Stop Loss: No configurado")
                
                print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            print(f"\n📊 RESUMEN DE CONFIGURACIÓN:")
            print(f"   Total posiciones: {len(active_trades)}")
            print(f"   Posiciones con TP/SL: {positions_with_tp_sl}")
            print(f"   Sin TP configurado: {positions_without_tp}")
            print(f"   Sin SL configurado: {positions_without_sl}")
            print(f"   Sin TP ni SL: {positions_without_both}")
            print(f"   Ejecuciones pendientes: {pending_executions}")
            print(f"   PnL total actual: ${total_pnl:.2f}")
            
            # Alertas específicas para TP/SL faltantes
            if positions_without_tp > 0 or positions_without_sl > 0:
                print(f"\n⚠️  ADVERTENCIA: Posiciones sin protección adecuada")
                
                if positions_without_both > 0:
                    print(f"   🔴 CRÍTICO: {positions_without_both} posiciones sin TP ni SL")
                    print(f"   Estas posiciones están completamente desprotegidas")
                
                if positions_without_tp > 0:
                    print(f"   🟡 {positions_without_tp} posiciones sin Take Profit")
                    print(f"   No se capturarán ganancias automáticamente")
                
                if positions_without_sl > 0:
                    print(f"   🟠 {positions_without_sl} posiciones sin Stop Loss")
                    print(f"   No hay protección contra pérdidas")
                
                print(f"\n💡 RECOMENDACIÓN:")
                print(f"   Ejecuta: python src/tools/fix_missing_tp_sl.py")
                print(f"   Para configurar automáticamente TP/SL faltantes")
            
            if pending_executions > 0:
                print(f"\n🚨 ALERTA CRÍTICA: {pending_executions} ejecuciones pendientes")
                print(f"   El sistema de ejecución automática puede tener problemas")
                print(f"   Revisa los logs del position_manager")
            
    except Exception as e:
        print(f"❌ Error verificando posiciones: {e}")
        import traceback
        print(f"   Detalles: {traceback.format_exc()}")

def check_tp_sl_configuration():
    """🎯 Verificar configuración de TP/SL"""
    print(f"\n🎯 VERIFICACIÓN DE CONFIGURACIÓN TP/SL")
    print("-" * 40)
    
    try:
        # Obtener configuración del perfil activo
        profile_config = TradingProfiles.get_current_profile()
        
        print(f"   ATR Multiplier Min: {profile_config.get('atr_multiplier_min', 'N/A')}x")
        print(f"   ATR Multiplier Max: {profile_config.get('atr_multiplier_max', 'N/A')}x")
        print(f"   TP Min: {profile_config.get('tp_min_percentage', 'N/A')}%")
        print(f"   TP Max: {profile_config.get('tp_max_percentage', 'N/A')}%")
        print(f"   SL Min: {profile_config.get('sl_min_percentage', 'N/A')}%")
        print(f"   SL Max: {profile_config.get('sl_max_percentage', 'N/A')}%")
        print(f"   Max posiciones: {profile_config.get('max_positions', 'N/A')}")
        print(f"   Max trades diarios: {profile_config.get('max_daily_trades', 'N/A')}")
        print(f"   Max drawdown: {profile_config.get('max_drawdown_threshold', 'N/A')}%")
        
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
        
        # Verificar estadísticas desde la base de datos
        with db_manager.get_db_session() as session:
            # Contar TP ejecutados
            tp_count = session.query(Trade).filter(
                Trade.status == "CLOSED",
                Trade.is_paper_trade == True,
                Trade.notes.like("%TAKE_PROFIT%")
            ).count()
            
            # Contar SL ejecutados
            sl_count = session.query(Trade).filter(
                Trade.status == "CLOSED",
                Trade.is_paper_trade == True,
                Trade.notes.like("%STOP_LOSS%")
            ).count()
            
            # Contar trailing stops
            trailing_count = session.query(Trade).filter(
                Trade.status == "CLOSED",
                Trade.is_paper_trade == True,
                Trade.notes.like("%TRAILING STOP%")
            ).count()
        
        print(f"   📈 TP ejecutados: {tp_count}")
        print(f"   📉 SL ejecutados: {sl_count}")
        print(f"   🔄 Trailing stops activos: {trailing_count}")
        
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
    """💰 Obtener precio actual usando feed unificado de db_manager con cache TTL."""
    try:
        # Manejo especial de monedas base estables
        if symbol and symbol.upper() == "USDT":
            return 1.0
        # Normalizar símbolo para formato CCXT (BTCUSDT/BTC/USDT -> BASE/USDT)
        if '/' in symbol:
            base, quote = symbol.split('/')
            norm_symbol = f"{base}/USDT" if quote.upper() != 'USDT' else symbol
        else:
            norm_symbol = symbol if not symbol.endswith(('USDT')) else (symbol[:-4] + '/USDT')
        # Delegar al gestor de base de datos que maneja cache TTL centralizada
        return float(db_manager._get_current_price(norm_symbol))
    except Exception:
        return 0.0

if __name__ == "__main__":
    main()