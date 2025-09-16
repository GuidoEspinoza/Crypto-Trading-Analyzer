#!/usr/bin/env python3
"""🔍 Monitor Integral del Sistema de Trading - Versión Optimizada

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

Optimizaciones aplicadas:
- Configuración completamente parametrizada
- Eliminación de parámetros hardcodeados
- Soporte para múltiples perfiles de configuración
- Formatos de display personalizables
- Precisión numérica configurable
- Sistema de emojis activable/desactivable
- Configuración de alertas personalizable
"""

import sys
import os
import argparse
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

# Agregar el directorio raíz del proyecto al path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.core.market_validator import market_validator
from src.core.position_manager import PositionManager
from src.config.config import TradingBotConfig, APIConfig, TradingProfiles, MonitoringConfig
from src.core.paper_trader import PaperTrader
from src.database.database import db_manager
from src.database.models import Trade
from src.config.trading_monitor_config import (
    TradingMonitorConfig,
    get_trading_monitor_config,
    DEFAULT_TRADING_MONITOR_CONFIG,
    COMPACT_PROFILE,
    DETAILED_PROFILE,
    NO_EMOJI_PROFILE
)

class TradingMonitor:
    """Monitor de trading para supervisar el bot - Versión Optimizada"""
    
    def __init__(self, trading_bot, config: Optional[TradingMonitorConfig] = None):
        self.trading_bot = trading_bot
        self.config = config or DEFAULT_TRADING_MONITOR_CONFIG
        self.price_cache = {} if self.config.api.enable_price_cache else None
        self.cache_timestamps = {} if self.config.api.enable_price_cache else None
        
        emoji = self.config.emojis.chart
        print(f"{emoji} Trading Monitor inicializado")
    
    def start_monitoring(self):
        """Iniciar monitoreo del sistema"""
        emoji = self.config.emojis.monitor
        print(f"{emoji} Iniciando monitoreo del sistema...")
        # Aquí se puede agregar lógica de monitoreo en tiempo real
    
    def update_config(self, new_config: TradingMonitorConfig):
        """Actualizar configuración del monitor"""
        self.config = new_config
        if not self.config.api.enable_price_cache:
            self.price_cache = None
            self.cache_timestamps = None
        elif self.price_cache is None:
            self.price_cache = {}
            self.cache_timestamps = {}
    
    def get_cached_price(self, symbol: str) -> Optional[float]:
        """Obtener precio desde cache si está disponible y válido"""
        if not self.config.api.enable_price_cache or not self.price_cache:
            return None
        
        if symbol in self.price_cache and symbol in self.cache_timestamps:
            cache_age = time.time() - self.cache_timestamps[symbol]
            if cache_age < self.config.api.price_cache_ttl:
                return self.price_cache[symbol]
        
        return None
    
    def cache_price(self, symbol: str, price: float):
        """Guardar precio en cache"""
        if self.config.api.enable_price_cache and self.price_cache is not None:
            self.price_cache[symbol] = price
            self.cache_timestamps[symbol] = time.time()
        
def main():
    """🚀 Función principal - Versión Optimizada"""
    parser = argparse.ArgumentParser(
        description="Monitor Integral del Sistema de Trading - Versión Optimizada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modos de operación:
  --status          Verificar estado general del sistema (default)
  --missed          Verificar solo ejecuciones perdidas
  --detailed        Análisis detallado completo
  --summary         Solo resumen sin detalles

Perfiles de configuración:
  --profile         Perfil de configuración (default, compact, detailed, no_emoji)
  --no-emojis       Desactivar emojis (equivale a --profile no_emoji)
  --config-file     Archivo de configuración personalizado

Ejemplos de uso:
  python3 trading_monitor.py                           # Estado general
  python3 trading_monitor.py --detailed                # Análisis completo
  python3 trading_monitor.py --missed --hours 12       # Ejecuciones perdidas (12h)
  python3 trading_monitor.py --summary                 # Solo resumen
  python3 trading_monitor.py --profile compact         # Perfil compacto
  python3 trading_monitor.py --no-emojis               # Sin emojis
  python3 trading_monitor.py --config-file config.json # Configuración personalizada
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
    
    # Argumentos de configuración
    parser.add_argument(
        '--profile',
        type=str,
        default='default',
        choices=['default', 'compact', 'detailed', 'no_emoji'],
        help='Perfil de configuración a usar'
    )
    parser.add_argument(
        '--no-emojis',
        action='store_true',
        help='Desactivar emojis (equivale a --profile no_emoji)'
    )
    parser.add_argument(
        '--config-file',
        type=str,
        help='Archivo de configuración personalizado'
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
    
    # Configurar el monitor según los argumentos
    config = None
    if args.config_file:
        try:
            config = get_trading_monitor_config(args.config_file)
        except Exception as e:
            print(f"❌ Error cargando configuración desde {args.config_file}: {e}")
            sys.exit(1)
    elif args.no_emojis or args.profile == 'no_emoji':
        config = NO_EMOJI_PROFILE
    elif args.profile == 'compact':
        config = COMPACT_PROFILE
    elif args.profile == 'detailed':
        config = DETAILED_PROFILE
    else:
        config = DEFAULT_TRADING_MONITOR_CONFIG
    
    # Determinar modo de operación
    if args.missed:
        mode = 'missed'
    elif args.detailed:
        mode = 'detailed'
    else:
        mode = 'status'
    
    # Mostrar encabezado con configuración
    separator = config.display_formats.separator
    title_emoji = config.emojis.monitor
    success_emoji = config.emojis.success
    error_emoji = config.emojis.error
    
    print(f"{title_emoji} MONITOR INTEGRAL DEL SISTEMA DE TRADING")
    print(separator)
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Modo: {mode.upper()}")
    if config != DEFAULT_TRADING_MONITOR_CONFIG:
        profile_name = {
            COMPACT_PROFILE: "Compacto",
            DETAILED_PROFILE: "Detallado", 
            NO_EMOJI_PROFILE: "Sin Emojis"
        }.get(config, "Personalizado")
        print(f"⚙️ Perfil: {profile_name}")
    print()
    
    try:
        if mode == 'missed':
            run_missed_executions_check(args.hours, args.summary, config)
        elif mode == 'detailed':
            run_detailed_analysis(args.hours, args.summary, config)
        else:
            run_status_check(config)
        
        print("\n" + separator)
        print(f"{success_emoji} Verificación completada")
        
    except Exception as e:
        print(f"{error_emoji} Error durante la verificación: {e}")
        sys.exit(1)

def run_status_check(config: TradingMonitorConfig):
    """📊 Ejecutar verificación de estado general"""
    title_emoji = config.emojis.chart
    separator = config.display_formats.separator_small
    
    print(f"{title_emoji} VERIFICACIÓN DE ESTADO GENERAL")
    print(separator)
    
    # Mostrar posiciones activas básicas
    show_active_positions_summary(config)
    
    # Verificar configuración de TP/SL
    check_tp_sl_configuration(config)
    
    # Verificar sistema de monitoreo
    check_monitoring_system(config)
    
    # Verificar precios actuales
    check_current_prices(config)

def run_missed_executions_check(hours: int, summary_only: bool, config: TradingMonitorConfig):
    """🔍 Ejecutar verificación de ejecuciones perdidas"""
    search_emoji = config.emojis.search
    calendar_emoji = config.emojis.calendar
    success_emoji = config.emojis.success
    warning_emoji = config.emojis.warning
    target_emoji = config.emojis.target
    separator = config.display_formats.separator_small
    
    print(f"{search_emoji} VERIFICACIÓN DE EJECUCIONES PERDIDAS")
    print(f"{calendar_emoji} Analizando últimas {hours} horas...")
    print(separator)
    
    # Mostrar posiciones activas
    show_active_positions_summary(config)
    
    # Verificar ejecuciones perdidas
    print(f"\n{search_emoji} Verificando ejecuciones perdidas...")
    missed_executions = market_validator.check_missed_executions(hours)
    
    if not missed_executions:
        print(f"{success_emoji} No se detectaron ejecuciones perdidas en las últimas {hours} horas")
        print(f"{target_emoji} Todas las posiciones están siendo monitoreadas correctamente")
    else:
        if config.alerts.enable_missed_execution_alerts:
            print(f"{warning_emoji} Se detectaron {len(missed_executions)} ejecuciones perdidas:")
        else:
            print(f"📊 Se detectaron {len(missed_executions)} ejecuciones perdidas:")
        print()
        
        if summary_only:
            show_missed_executions_summary(missed_executions, config)
        else:
            show_missed_executions_detailed(missed_executions, config)

def run_detailed_analysis(hours: int, summary_only: bool, config: TradingMonitorConfig):
    """📊 Ejecutar análisis detallado completo"""
    chart_emoji = config.emojis.chart
    calendar_emoji = config.emojis.calendar
    trend_emoji = config.emojis.trend_up
    search_emoji = config.emojis.search
    target_emoji = config.emojis.target
    monitor_emoji = config.emojis.monitor
    money_emoji = config.emojis.money
    success_emoji = config.emojis.success
    warning_emoji = config.emojis.warning
    separator = config.display_formats.separator_small
    
    print(f"{chart_emoji} ANÁLISIS DETALLADO COMPLETO")
    print(f"{calendar_emoji} Período de análisis: {hours} horas")
    print(separator)
    
    # Análisis de posiciones activas
    print(f"\n{trend_emoji} ANÁLISIS DE POSICIONES ACTIVAS")
    print(separator)
    check_active_positions_detailed(config)
    
    # Verificación de configuración TP/SL
    print(f"\n{target_emoji} CONFIGURACIÓN DE TP/SL")
    print(separator)
    check_tp_sl_configuration(config)
    
    # Verificación del sistema de monitoreo
    print(f"\n{monitor_emoji} SISTEMA DE MONITOREO")
    print(separator)
    check_monitoring_system(config)
    
    # Verificación de precios actuales
    print(f"\n{money_emoji} PRECIOS ACTUALES")
    print(separator)
    check_current_prices(config)
    
    # Verificación de ejecuciones perdidas
    print(f"\n{search_emoji} VERIFICACIÓN DE EJECUCIONES PERDIDAS ({hours}h)")
    print(separator)
    
    missed_executions = market_validator.check_missed_executions(hours)
    
    if not missed_executions:
        print(f"{success_emoji} No se detectaron ejecuciones perdidas en las últimas {hours} horas")
    else:
        if config.alerts.enable_missed_execution_alerts:
            print(f"{warning_emoji} Se detectaron {len(missed_executions)} ejecuciones perdidas:")
        else:
            print(f"📊 Se detectaron {len(missed_executions)} ejecuciones perdidas:")
        print()
        
        if summary_only:
            show_missed_executions_summary(missed_executions, config)
        else:
            show_missed_executions_detailed(missed_executions, config)

def show_active_positions_summary(config: TradingMonitorConfig):
    """📊 Mostrar resumen de posiciones activas"""
    chart_emoji = config.emojis.chart
    trend_emoji = config.emojis.trend_up
    money_emoji = config.emojis.money
    error_emoji = config.emojis.error
    success_emoji = config.emojis.success
    warning_emoji = config.emojis.warning
    separator = config.display_formats.separator_small
    
    try:
        with db_manager.get_db_session() as session:
            active_trades = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).all()
            
            print(f"{chart_emoji} POSICIONES ACTIVAS: {len(active_trades)}")
            print(separator)
            
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
                    tp_pct_str = f"{tp_pct:.{config.precision.percentage_decimals}f}%"
                
                if trade.stop_loss and trade.entry_price > 0:
                    if trade.trade_type == "BUY":
                        sl_pct = ((trade.stop_loss - trade.entry_price) / trade.entry_price) * 100
                    else:
                        sl_pct = ((trade.entry_price - trade.stop_loss) / trade.entry_price) * 100
                    sl_pct_str = f"{abs(sl_pct):.{config.precision.percentage_decimals}f}%"
                
                # Formatear TP y SL
                tp_str = f"${trade.take_profit:.{config.precision.price_decimals}f}" if trade.take_profit else "N/A"
                sl_str = f"${trade.stop_loss:.{config.precision.price_decimals}f}" if trade.stop_loss else "N/A"
                
                print(f"   #{trade.id} {trade.symbol} {trade.trade_type}")
                print(f"      Entry: ${trade.entry_price:.{config.precision.price_decimals}f} | Current: ${current_price:.{config.precision.price_decimals}f}")
                print(f"      TP: {tp_str} ({tp_pct_str}) | SL: {sl_str} ({sl_pct_str})")
                
                # Calcular ganancias y pérdidas potenciales
                if current_price > 0:
                    # Calcular ganancia potencial en TP
                    if trade.take_profit:
                        if trade.trade_type == "BUY":
                            tp_gain_usdt = (trade.take_profit - trade.entry_price) * trade.quantity
                        else:
                            tp_gain_usdt = (trade.entry_price - trade.take_profit) * trade.quantity
                        print(f"      Ganancia potencial: ${tp_gain_usdt:.{config.precision.value_decimals}f} USDT")
                    
                    # Calcular pérdida potencial en SL
                    if trade.stop_loss:
                        if trade.trade_type == "BUY":
                            sl_loss_usdt = (trade.stop_loss - trade.entry_price) * trade.quantity
                        else:
                            sl_loss_usdt = (trade.entry_price - trade.stop_loss) * trade.quantity
                        print(f"      Pérdida potencial: ${sl_loss_usdt:.{config.precision.value_decimals}f} USDT")
                    
                    # Calcular distancias a TP/SL
                    if trade.take_profit:
                        if trade.trade_type == "BUY":
                            tp_distance = ((trade.take_profit - current_price) / current_price) * 100
                            tp_status = config.emojis.trend_up if tp_distance > 0 else success_emoji
                        else:
                            tp_distance = ((current_price - trade.take_profit) / current_price) * 100
                            tp_status = config.emojis.trend_up if tp_distance > 0 else success_emoji
                        print(f"      {tp_status} TP Distance: {abs(tp_distance):.{config.precision.percentage_decimals}f}%")
                    
                    if trade.stop_loss:
                        if trade.trade_type == "BUY":
                            sl_distance = ((current_price - trade.stop_loss) / current_price) * 100
                            sl_status = config.emojis.shield if sl_distance > 0 else warning_emoji
                        else:
                            sl_distance = ((trade.stop_loss - current_price) / current_price) * 100
                            sl_status = config.emojis.shield if sl_distance > 0 else warning_emoji
                        print(f"      {sl_status} SL Distance: {abs(sl_distance):.{config.precision.percentage_decimals}f}%")
                    
                    # Calcular PnL actual
                    if trade.trade_type == "BUY":
                        pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
                        pnl_usdt = (current_price - trade.entry_price) * trade.quantity
                    else:
                        pnl_pct = ((trade.entry_price - current_price) / trade.entry_price) * 100
                        pnl_usdt = (trade.entry_price - current_price) * trade.quantity
                    
                    pnl_status = success_emoji if pnl_pct > 0 else error_emoji if pnl_pct < 0 else warning_emoji
                    print(f"      {pnl_status} PnL: {pnl_pct:+.{config.precision.percentage_decimals}f}% ({pnl_usdt:+.{config.precision.value_decimals}f} USDT)")
                    
                    # Sumar al total
                    total_pnl_usdt += pnl_usdt
                
                print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M')}")
                print()  # Línea en blanco entre trades
            
            # Mostrar total del portafolio
            print(separator)
            total_status = success_emoji if total_pnl_usdt > 0 else error_emoji if total_pnl_usdt < 0 else warning_emoji
            print(f"{money_emoji} TOTAL PORTAFOLIO: {total_status} {total_pnl_usdt:+.{config.precision.value_decimals}f} USDT")
            print()
            
    except Exception as e:
        print(f"{error_emoji} Error mostrando posiciones activas: {e}")

def check_active_positions_detailed(config: TradingMonitorConfig):
    """📊 Verificar posiciones activas con análisis detallado"""
    chart_emoji = config.emojis.chart
    target_emoji = config.emojis.target
    success_emoji = config.emojis.success
    error_emoji = config.emojis.error
    warning_emoji = config.emojis.warning
    shield_emoji = config.emojis.shield
    separator = config.display_formats.separator_small
    
    try:
        with db_manager.get_db_session() as session:
            active_trades = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).order_by(Trade.entry_time.desc()).all()
            
            print(f"{chart_emoji} ANÁLISIS DETALLADO DE POSICIONES: {len(active_trades)}")
            print(separator)
            
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
                        tp_alert = f" {warning_emoji} TP PENDIENTE"
                        pending_executions += 1
                
                if has_sl:
                    if (trade.trade_type == "BUY" and current_price <= trade.stop_loss) or \
                       (trade.trade_type == "SELL" and current_price >= trade.stop_loss):
                        sl_alert = f" {warning_emoji} SL PENDIENTE"
                        pending_executions += 1
                
                entry_price_str = f"{trade.entry_price:.{config.precision.price_decimals}f}"
                current_price_str = f"{current_price:.{config.precision.price_decimals}f}"
                pnl_str = f"{pnl:.{config.precision.value_decimals}f}"
                pnl_pct_str = f"{pnl_pct:.{config.precision.percentage_decimals}f}%"
                quantity_str = f"{trade.quantity:.{config.precision.size_decimals}f}"
                
                print(f"\n   {target_emoji} Trade #{trade.id} - {trade.symbol} ({trade.trade_type})")
                print(f"      Strategy: {trade.strategy_name}")
                print(f"      Entry: ${entry_price_str} | Current: ${current_price_str}")
                print(f"      PnL: ${pnl_str} ({pnl_pct_str})")
                print(f"      Quantity: {quantity_str}")
                
                if has_tp:
                    tp_distance = abs(current_price - trade.take_profit) / trade.take_profit * 100
                    tp_price_str = f"{trade.take_profit:.{config.precision.price_decimals}f}"
                    tp_distance_str = f"{tp_distance:.{config.precision.percentage_decimals}f}%"
                    print(f"      {success_emoji} Take Profit: ${tp_price_str} (Distance: {tp_distance_str}){tp_alert}")
                else:
                    print(f"      {error_emoji} Take Profit: No configurado")
                
                if has_sl:
                    sl_distance = abs(current_price - trade.stop_loss) / trade.stop_loss * 100
                    sl_price_str = f"{trade.stop_loss:.{config.precision.price_decimals}f}"
                    sl_distance_str = f"{sl_distance:.{config.precision.percentage_decimals}f}%"
                    print(f"      {success_emoji} Stop Loss: ${sl_price_str} (Distance: {sl_distance_str}){sl_alert}")
                else:
                    print(f"      {error_emoji} Stop Loss: No configurado")
                
                print(f"      Opened: {trade.entry_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            total_pnl_str = f"{total_pnl:.{config.precision.value_decimals}f}"
            
            print(f"\n{chart_emoji} RESUMEN DE CONFIGURACIÓN:")
            print(f"   Total posiciones: {len(active_trades)}")
            print(f"   Posiciones con TP/SL: {positions_with_tp_sl}")
            print(f"   Sin TP configurado: {positions_without_tp}")
            print(f"   Sin SL configurado: {positions_without_sl}")
            print(f"   Sin TP ni SL: {positions_without_both}")
            print(f"   Ejecuciones pendientes: {pending_executions}")
            print(f"   PnL total actual: ${total_pnl_str}")
            
            # Alertas específicas para TP/SL faltantes
            if positions_without_tp > 0 or positions_without_sl > 0:
                if config.alerts.enable_tp_sl_alerts:
                    print(f"\n{warning_emoji} ADVERTENCIA: Posiciones sin protección adecuada")
                else:
                    print(f"\n📊 ADVERTENCIA: Posiciones sin protección adecuada")
                
                if positions_without_both > 0:
                    print(f"   {error_emoji} CRÍTICO: {positions_without_both} posiciones sin TP ni SL")
                    print(f"   Estas posiciones están completamente desprotegidas")
                
                if positions_without_tp > 0:
                    print(f"   {warning_emoji} {positions_without_tp} posiciones sin Take Profit")
                    print(f"   No se capturarán ganancias automáticamente")
                
                if positions_without_sl > 0:
                    print(f"   {warning_emoji} {positions_without_sl} posiciones sin Stop Loss")
                    print(f"   No hay protección contra pérdidas")
                
                print(f"\n💡 RECOMENDACIÓN:")
                print(f"   Ejecuta: python src/tools/fix_missing_tp_sl.py")
                print(f"   Para configurar automáticamente TP/SL faltantes")
            
            if pending_executions > 0:
                if config.alerts.enable_missed_execution_alerts:
                    print(f"\n{warning_emoji} ALERTA CRÍTICA: {pending_executions} ejecuciones pendientes")
                else:
                    print(f"\n📊 ALERTA CRÍTICA: {pending_executions} ejecuciones pendientes")
                print(f"   El sistema de ejecución automática puede tener problemas")
                print(f"   Revisa los logs del position_manager")
            
    except Exception as e:
        print(f"{error_emoji} Error verificando posiciones: {e}")
        import traceback
        print(f"   Detalles: {traceback.format_exc()}")

def check_tp_sl_configuration(config: TradingMonitorConfig):
    """🎯 Verificar configuración de TP/SL"""
    target_emoji = config.emojis.target
    success_emoji = config.emojis.success
    error_emoji = config.emojis.error
    separator = config.display_formats.separator_small
    
    print(f"\n{target_emoji} VERIFICACIÓN DE CONFIGURACIÓN TP/SL")
    print(separator)
    
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
        
        print(f"\n   {success_emoji} Configuración de Risk Manager encontrada")
        
    except Exception as e:
        print(f"   {error_emoji} Error verificando configuración: {e}")

def check_current_prices(config: TradingMonitorConfig):
    """💰 Verificar precios actuales"""
    money_emoji = config.emojis.money
    success_emoji = config.emojis.success
    error_emoji = config.emojis.error
    separator = config.display_formats.separator_small
    
    print(f"\n{money_emoji} VERIFICACIÓN DE PRECIOS ACTUALES")
    print(separator)
    
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
                    price_str = f"{price:.{config.precision.price_decimals}f}"
                    print(f"   {success_emoji} {symbol}: ${price_str}")
                else:
                    print(f"   {error_emoji} {symbol}: Error obteniendo precio")
                    
    except Exception as e:
        print(f"   {error_emoji} Error verificando precios: {e}")

def check_monitoring_system(config: TradingMonitorConfig):
    """🔄 Verificar sistema de monitoreo"""
    monitor_emoji = config.emojis.monitor
    chart_emoji = config.emojis.chart
    success_emoji = config.emojis.success
    error_emoji = config.emojis.error
    trend_up_emoji = config.emojis.trend_up
    trend_down_emoji = config.emojis.trend_down
    separator = config.display_formats.separator_small
    
    print(f"\n{monitor_emoji} VERIFICACIÓN DEL SISTEMA DE MONITOREO")
    print(separator)
    
    try:
        # Verificar si el position manager está funcionando
        paper_trader = PaperTrader()
        position_manager = PositionManager(paper_trader)
        
        # Obtener posiciones activas
        active_positions = position_manager.get_active_positions()
        
        print(f"   {success_emoji} Position Manager: Activo")
        print(f"   {chart_emoji} Posiciones monitoreadas: {len(active_positions)}")
        
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
        
        print(f"   {trend_up_emoji} TP ejecutados: {tp_count}")
        print(f"   {trend_down_emoji} SL ejecutados: {sl_count}")
        print(f"   {monitor_emoji} Trailing stops activos: {trailing_count}")
        
    except Exception as e:
        print(f"   {error_emoji} Error verificando sistema de monitoreo: {e}")

def show_missed_executions_summary(missed_executions: List[Any], config: TradingMonitorConfig):
    """📋 Mostrar resumen de ejecuciones perdidas"""
    chart_emoji = config.emojis.chart
    
    total_missed_pnl = sum(missed.potential_pnl_missed for missed in missed_executions)
    
    tp_count = sum(1 for missed in missed_executions if missed.target_type == "TP")
    sl_count = sum(1 for missed in missed_executions if missed.target_type == "SL")
    
    total_pnl_str = f"{total_missed_pnl:.{config.precision.value_decimals}f}"
    
    print("📋 RESUMEN:")
    print(f"   Total ejecuciones perdidas: {len(missed_executions)}")
    print(f"   Take Profits perdidos: {tp_count}")
    print(f"   Stop Losses perdidos: {sl_count}")
    print(f"   PnL total perdido: ${total_pnl_str}")
    
    if missed_executions:
        print(f"\n{chart_emoji} POR SÍMBOLO:")
        symbols = {}
        for missed in missed_executions:
            if missed.symbol not in symbols:
                symbols[missed.symbol] = {'count': 0, 'pnl': 0.0}
            symbols[missed.symbol]['count'] += 1
            symbols[missed.symbol]['pnl'] += missed.potential_pnl_missed
        
        for symbol, data in symbols.items():
            pnl_str = f"{data['pnl']:.{config.precision.value_decimals}f}"
            print(f"   {symbol}: {data['count']} ejecuciones, ${pnl_str} PnL perdido")

def show_missed_executions_detailed(missed_executions: List[Any], config: TradingMonitorConfig):
    """📊 Mostrar reporte detallado de ejecuciones perdidas"""
    target_emoji = config.emojis.target
    success_emoji = config.emojis.success
    error_emoji = config.emojis.error
    money_emoji = config.emojis.money
    chart_emoji = config.emojis.chart
    
    total_missed_pnl = 0.0
    
    for i, missed in enumerate(missed_executions, 1):
        target_price_str = f"{missed.target_price:.{config.precision.price_decimals}f}"
        actual_price_str = f"{missed.actual_price_reached:.{config.precision.price_decimals}f}"
        current_price_str = f"{missed.current_price:.{config.precision.price_decimals}f}"
        pnl_str = f"{missed.potential_pnl_missed:.{config.precision.value_decimals}f}"
        
        print(f"{i}. {target_emoji} {missed.symbol} (Trade #{missed.trade_id})")
        print(f"   Tipo: {success_emoji if missed.target_type == 'TP' else error_emoji} {'Take Profit' if missed.target_type == 'TP' else 'Stop Loss'}")
        print(f"   Precio objetivo: ${target_price_str}")
        print(f"   Precio alcanzado: ${actual_price_str}")
        print(f"   Timestamp: {missed.timestamp_reached.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Precio actual: ${current_price_str}")
        print(f"   PnL perdido: ${pnl_str}")
        print(f"   Razón: {missed.reason}")
        print()
        
        total_missed_pnl += missed.potential_pnl_missed
    
    total_pnl_str = f"{total_missed_pnl:.{config.precision.value_decimals}f}"
    
    print(f"{money_emoji} TOTAL PnL PERDIDO: ${total_pnl_str}")
    print(f"{chart_emoji} EJECUCIONES PERDIDAS: {len(missed_executions)}")

def get_current_price(symbol: str, config: TradingMonitorConfig = None) -> float:
    """💰 Obtener precio actual de un símbolo con cache opcional"""
    if config is None:
        config = DEFAULT_TRADING_MONITOR_CONFIG
    
    error_emoji = config.emojis.error
    warning_emoji = config.emojis.warning
    
    # Verificar cache si está habilitado
    if hasattr(get_current_price, '_monitor_instance'):
        monitor = get_current_price._monitor_instance
        cached_price = monitor.get_cached_price(symbol)
        if cached_price is not None:
            return cached_price
    
    try:
        url = APIConfig.get_binance_url("ticker_price")
        params = {'symbol': symbol}
        
        # Hacer request a la API con timeout configurable
        response = requests.get(
            url, 
            params=params, 
            timeout=config.api.request_timeout
        )
        response.raise_for_status()
        
        data = response.json()
        price = float(data['price'])
        
        # Guardar en cache si está disponible
        if hasattr(get_current_price, '_monitor_instance'):
            monitor = get_current_price._monitor_instance
            monitor.cache_price(symbol, price)
        
        return price
        
    except requests.exceptions.Timeout:
        if config.api.show_api_errors:
            print(f"{warning_emoji} Timeout obteniendo precio de {symbol}")
        return 0.0
    except requests.exceptions.RequestException as e:
        if config.api.show_api_errors:
            print(f"🌐 Error de conexión para {symbol}: {e}")
        return 0.0
    except Exception as e:
        if config.api.show_api_errors:
            print(f"{error_emoji} Error inesperado obteniendo precio de {symbol}: {e}")
        return 0.0

# Función auxiliar para configurar la instancia del monitor en get_current_price
def set_monitor_instance_for_price_cache(monitor_instance):
    """Configurar instancia del monitor para el cache de precios"""
    get_current_price._monitor_instance = monitor_instance

if __name__ == "__main__":
    sys.exit(main())