#!/usr/bin/env python3
"""
🔧 Script para corregir posiciones sin TP/SL configurados

Este script:
1. Identifica posiciones abiertas sin TP/SL
2. Calcula TP/SL apropiados basados en ATR y configuración actual
3. Actualiza las posiciones en la base de datos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.database import db_manager
from src.database.models import Trade
from src.config.config import RiskManagerConfig
from src.core.enhanced_strategies import ProfessionalRSIStrategy
import pandas_ta as ta
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_tp_sl_for_position(trade, current_price, atr_value):
    """Calcular TP/SL para una posición específica"""
    risk_config = RiskManagerConfig()
    
    # Obtener rangos dinámicos
    tp_min = risk_config.get_tp_min_percentage()
    tp_max = risk_config.get_tp_max_percentage()
    sl_min = risk_config.get_sl_min_percentage()
    sl_max = risk_config.get_sl_max_percentage()
    
    # Calcular porcentaje ATR
    atr_percentage = (atr_value / trade.entry_price) * 100
    
    if trade.trade_type == "BUY":
        # Stop Loss: usar ATR o mínimo configurado
        if atr_percentage <= sl_min:
            sl_pct = sl_min
        elif atr_percentage >= sl_max:
            sl_pct = sl_max
        else:
            sl_pct = atr_percentage
        
        # Take Profit: 1.5x ATR o configuración
        if atr_percentage * 1.5 <= tp_min:
            tp_pct = tp_min
        elif atr_percentage * 1.5 >= tp_max:
            tp_pct = tp_max
        else:
            tp_pct = atr_percentage * 1.5
        
        stop_loss = trade.entry_price * (1 - sl_pct / 100)
        take_profit = trade.entry_price * (1 + tp_pct / 100)
        
    else:  # SELL
        # Stop Loss: usar ATR o mínimo configurado
        if atr_percentage <= sl_min:
            sl_pct = sl_min
        elif atr_percentage >= sl_max:
            sl_pct = sl_max
        else:
            sl_pct = atr_percentage
        
        # Take Profit: 1.5x ATR o configuración
        if atr_percentage * 1.5 <= tp_min:
            tp_pct = tp_min
        elif atr_percentage * 1.5 >= tp_max:
            tp_pct = tp_max
        else:
            tp_pct = atr_percentage * 1.5
        
        stop_loss = trade.entry_price * (1 + sl_pct / 100)
        take_profit = trade.entry_price * (1 - tp_pct / 100)
    
    return stop_loss, take_profit, sl_pct, tp_pct

def get_atr_for_symbol(symbol, timeframe="1h", period=14):
    """Obtener ATR actual para un símbolo"""
    try:
        strategy = ProfessionalRSIStrategy()
        df = strategy.get_market_data(symbol, timeframe, limit=50)
        
        if df.empty:
            logger.warning(f"No data for {symbol}, using default ATR")
            return None
        
        # Calcular ATR
        atr = ta.atr(df['high'], df['low'], df['close'], length=period)
        return atr.iloc[-1] if atr is not None else None
        
    except Exception as e:
        logger.error(f"Error getting ATR for {symbol}: {e}")
        return None

def fix_missing_tp_sl():
    """Función principal para corregir posiciones sin TP/SL"""
    logger.info("🔧 Iniciando corrección de posiciones sin TP/SL...")
    
    updated_count = 0
    
    try:
        with db_manager.get_db_session() as session:
            # Buscar posiciones abiertas sin TP/SL
            positions_without_tp_sl = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True,
                (Trade.stop_loss.is_(None) | Trade.take_profit.is_(None))
            ).all()
            
            logger.info(f"📊 Encontradas {len(positions_without_tp_sl)} posiciones sin TP/SL completo")
            
            for trade in positions_without_tp_sl:
                try:
                    # Obtener ATR actual
                    atr_value = get_atr_for_symbol(trade.symbol)
                    
                    if atr_value is None:
                        # Usar ATR por defecto (2% del precio de entrada)
                        atr_value = trade.entry_price * 0.02
                        logger.warning(f"Usando ATR por defecto para {trade.symbol}: {atr_value:.4f}")
                    
                    # Calcular TP/SL
                    stop_loss, take_profit, sl_pct, tp_pct = calculate_tp_sl_for_position(
                        trade, trade.entry_price, atr_value
                    )
                    
                    # Actualizar solo si no están configurados
                    updated_fields = []
                    if trade.stop_loss is None:
                        trade.stop_loss = stop_loss
                        updated_fields.append(f"SL: ${stop_loss:.4f} ({sl_pct:.2f}%)")
                    
                    if trade.take_profit is None:
                        trade.take_profit = take_profit
                        updated_fields.append(f"TP: ${take_profit:.4f} ({tp_pct:.2f}%)")
                    
                    if updated_fields:
                        updated_count += 1
                        logger.info(
                            f"✅ Actualizada posición #{trade.id} {trade.symbol} {trade.trade_type}: "
                            f"{', '.join(updated_fields)}"
                        )
                
                except Exception as e:
                    logger.error(f"❌ Error procesando posición #{trade.id}: {e}")
                    continue
            
            # Confirmar cambios
            session.commit()
            
            logger.info(f"🎯 Corrección completada: {updated_count} posiciones actualizadas")
            
            # Mostrar resumen de posiciones actualizadas
            if updated_count > 0:
                logger.info("\n📋 RESUMEN DE POSICIONES ACTUALIZADAS:")
                updated_positions = session.query(Trade).filter(
                    Trade.status == "OPEN",
                    Trade.is_paper_trade == True,
                    Trade.stop_loss.isnot(None),
                    Trade.take_profit.isnot(None)
                ).all()
                
                for trade in updated_positions:
                    logger.info(
                        f"   #{trade.id} {trade.symbol} {trade.trade_type} - "
                        f"Entry: ${trade.entry_price:.4f} | "
                        f"SL: ${trade.stop_loss:.4f} | "
                        f"TP: ${trade.take_profit:.4f}"
                    )
            
    except Exception as e:
        logger.error(f"❌ Error en la corrección: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Script de Corrección de TP/SL")
    print("=" * 50)
    
    success = fix_missing_tp_sl()
    
    if success:
        print("\n✅ Corrección completada exitosamente")
    else:
        print("\n❌ Error durante la corrección")
        sys.exit(1)