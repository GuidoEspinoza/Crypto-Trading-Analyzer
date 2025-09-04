#!/usr/bin/env python3
"""📊 Script para verificar el estado del sistema de monitoreo

Este script:
- Verifica el estado del position monitor
- Muestra precios actuales vs TP/SL
- Analiza la configuración de las posiciones
- Detecta posibles problemas de configuración
"""

import sys
import os
import requests
from datetime import datetime

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_engine.position_manager import PositionManager
from trading_engine.paper_trader import PaperTrader
from database.database import db_manager
from database.models import Trade

def main():
    """🚀 Función principal"""
    print("📊 VERIFICADOR DEL SISTEMA DE MONITOREO")
    print("=" * 50)
    print(f"🕐 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Verificar posiciones activas con detalles
        check_active_positions_detailed()
        
        # Verificar configuración de TP/SL
        check_tp_sl_configuration()
        
        # Verificar precios actuales
        check_current_prices()
        
        # Verificar sistema de monitoreo
        check_monitoring_system()
        
        print("\n" + "=" * 50)
        print("✅ Verificación del sistema completada")
        
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        sys.exit(1)

def check_active_positions_detailed():
    """📊 Verificar posiciones activas con detalles"""
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
            
            if positions_without_tp_sl > 0:
                print(f"   ⚠️  {positions_without_tp_sl} posiciones sin protección!")
            
    except Exception as e:
        print(f"❌ Error verificando posiciones: {e}")

def check_tp_sl_configuration():
    """🎯 Verificar configuración de TP/SL"""
    print(f"\n🎯 VERIFICACIÓN DE CONFIGURACIÓN TP/SL")
    print("-" * 40)
    
    try:
        # Verificar configuración en el código
        from trading_engine.config import RiskManagerConfig
        
        print(f"   ATR Multiplier Min: {RiskManagerConfig.ATR_MULTIPLIER_MIN}x")
        print(f"   ATR Multiplier Max: {RiskManagerConfig.ATR_MULTIPLIER_MAX}x")
        print(f"   ATR Default: {RiskManagerConfig.ATR_DEFAULT}x")
        print(f"   Trailing Stop Activation: {RiskManagerConfig.TRAILING_STOP_ACTIVATION}%")
        print(f"   Breakeven Threshold: {RiskManagerConfig.BREAKEVEN_THRESHOLD}%")
        print(f"   Max riesgo por trade: {RiskManagerConfig.MAX_RISK_PER_TRADE}%")
        
        # Verificar si el risk manager está activo
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