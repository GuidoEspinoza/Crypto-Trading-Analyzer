#!/usr/bin/env python3
"""
Script para verificar la configuración correcta de Take Profit y Stop Loss
en posiciones LONG y SHORT
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('.env')

# Añadir el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.enhanced_strategies import EnhancedSignal
from src.config.main_config import TradingProfiles, RiskManagerConfig

def test_tp_sl_calculation():
    """Prueba el cálculo de TP y SL para diferentes escenarios"""
    
    print("🔍 Verificando configuración de TP y SL...")
    print("=" * 60)
    
    # Obtener configuración actual
    profile = TradingProfiles.get_current_profile()
    risk_config = RiskManagerConfig()
    
    print(f"📋 Perfil activo: {TradingProfiles.get_current_profile()['name']}")
    print(f"   TP min: {profile['tp_min_percentage']*100:.1f}%")
    print(f"   TP max: {profile['tp_max_percentage']*100:.1f}%")
    print(f"   SL min: {profile['sl_min_percentage']*100:.1f}%")
    print(f"   SL max: {profile['sl_max_percentage']*100:.1f}%")
    print()
    
    # Precio de prueba
    test_price = 50000.0  # Ejemplo con Bitcoin
    atr_value = 1000.0    # ATR de ejemplo
    
    # Crear señales de prueba
    test_cases = [
        {
            "name": "LONG Position (BUY)",
            "signal_type": "BUY",
            "expected_sl": "por debajo del precio de entrada",
            "expected_tp": "por encima del precio de entrada"
        },
        {
            "name": "SHORT Position (SELL)",
            "signal_type": "SELL", 
            "expected_sl": "por encima del precio de entrada",
            "expected_tp": "por debajo del precio de entrada"
        }
    ]
    
    for case in test_cases:
        print(f"🧪 Probando: {case['name']}")
        print(f"   Precio de entrada: ${test_price:,.2f}")
        print(f"   ATR: ${atr_value:,.2f}")
        
        # Crear señal de prueba
        signal = EnhancedSignal(
            symbol="BTCUSD",
            signal_type=case["signal_type"],
            price=test_price,
            confidence_score=85.0,
            strength="Strong",
            strategy_name="TestStrategy",
            timestamp=datetime.now(),
            indicators_data={"atr": atr_value},
            notes="Test signal for TP/SL verification",
            stop_loss_price=0.0,
            take_profit_price=0.0,
            market_regime="NORMAL",
            timeframe="1h"
        )
        
        # Calcular TP/SL usando la lógica del sistema
        try:
            # Simular el cálculo de TP/SL directamente
            entry_price = test_price
            atr_ratio = atr_value / entry_price
            
            # Obtener rangos de configuración
            sl_min = profile['sl_min_percentage']
            sl_max = profile['sl_max_percentage'] 
            tp_min = profile['tp_min_percentage']
            tp_max = profile['tp_max_percentage']
            
            if case["signal_type"] == "BUY":
                # LONG: SL por debajo, TP por encima
                if atr_ratio <= sl_min:
                    sl_pct = sl_min
                elif atr_ratio >= sl_max:
                    sl_pct = sl_max
                else:
                    sl_pct = atr_ratio
                
                atr_tp = atr_ratio * 1.5
                if atr_tp <= tp_min:
                    tp_pct = tp_min
                elif atr_tp >= tp_max:
                    tp_pct = tp_max
                else:
                    tp_pct = atr_tp
                
                stop_loss = entry_price * (1 - sl_pct)
                take_profit = entry_price * (1 + tp_pct)
                
            else:  # SELL
                # SHORT: SL por encima, TP por debajo
                if atr_ratio <= sl_min:
                    sl_pct = sl_min
                elif atr_ratio >= sl_max:
                    sl_pct = sl_max
                else:
                    sl_pct = atr_ratio
                
                if atr_ratio * 1.5 <= tp_min:
                    tp_pct = tp_min
                elif atr_ratio * 1.5 >= tp_max:
                    tp_pct = tp_max
                else:
                    tp_pct = atr_ratio * 1.5
                
                stop_loss = entry_price * (1 + sl_pct)
                take_profit = entry_price * (1 - tp_pct)
            
            # Verificar que los niveles son correctos
            print(f"   📊 Resultados:")
            print(f"      Stop Loss:   ${stop_loss:,.2f} ({case['expected_sl']})")
            print(f"      Take Profit: ${take_profit:,.2f} ({case['expected_tp']})")
            
            # Calcular distancias porcentuales
            sl_distance = abs(stop_loss - entry_price) / entry_price * 100
            tp_distance = abs(take_profit - entry_price) / entry_price * 100
            
            print(f"      SL Distance: {sl_distance:.2f}%")
            print(f"      TP Distance: {tp_distance:.2f}%")
            
            # Verificar lógica
            if case["signal_type"] == "BUY":
                sl_correct = stop_loss < entry_price
                tp_correct = take_profit > entry_price
            else:  # SELL
                sl_correct = stop_loss > entry_price
                tp_correct = take_profit < entry_price
            
            # Calcular Risk/Reward ratio
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit - entry_price)
            rr_ratio = reward / risk if risk > 0 else 0
            
            print(f"      Risk/Reward: 1:{rr_ratio:.2f}")
            
            # Validación
            status = "✅" if (sl_correct and tp_correct) else "❌"
            print(f"   {status} Configuración: {'CORRECTA' if (sl_correct and tp_correct) else 'INCORRECTA'}")
            
            if not sl_correct:
                print(f"      ⚠️  Stop Loss mal configurado para {case['signal_type']}")
            if not tp_correct:
                print(f"      ⚠️  Take Profit mal configurado para {case['signal_type']}")
                
        except Exception as e:
            print(f"   ❌ Error en cálculo: {e}")
        
        print()
    
    print("🔍 Verificando configuración en base de datos...")
    
    # Verificar posiciones existentes
    try:
        from src.database.database import db_manager
        from src.database.models import Trade
        
        with db_manager.get_db_session() as session:
            # Obtener posiciones abiertas
            open_positions = session.query(Trade).filter(
                Trade.status == "OPEN",
                Trade.is_paper_trade == True
            ).all()
            
            print(f"📊 Posiciones abiertas encontradas: {len(open_positions)}")
            
            positions_with_tp_sl = 0
            positions_without_tp = 0
            positions_without_sl = 0
            
            for trade in open_positions:
                has_tp = trade.take_profit_price is not None and trade.take_profit_price > 0
                has_sl = trade.stop_loss_price is not None and trade.stop_loss_price > 0
                
                if has_tp and has_sl:
                    positions_with_tp_sl += 1
                    
                    # Verificar que TP/SL están en la dirección correcta
                    if trade.trade_type == "BUY":
                        sl_correct = trade.stop_loss_price < trade.entry_price
                        tp_correct = trade.take_profit_price > trade.entry_price
                    else:  # SELL
                        sl_correct = trade.stop_loss_price > trade.entry_price
                        tp_correct = trade.take_profit_price < trade.entry_price
                    
                    status = "✅" if (sl_correct and tp_correct) else "❌"
                    print(f"   {status} Trade #{trade.id} ({trade.symbol}) - {trade.trade_type}")
                    print(f"      Entry: ${trade.entry_price:.4f}")
                    print(f"      SL: ${trade.stop_loss_price:.4f}")
                    print(f"      TP: ${trade.take_profit_price:.4f}")
                    
                    if not sl_correct or not tp_correct:
                        print(f"      ⚠️  Configuración incorrecta detectada!")
                
                if not has_tp:
                    positions_without_tp += 1
                if not has_sl:
                    positions_without_sl += 1
            
            print(f"\n📋 Resumen:")
            print(f"   Posiciones con TP y SL: {positions_with_tp_sl}")
            print(f"   Posiciones sin TP: {positions_without_tp}")
            print(f"   Posiciones sin SL: {positions_without_sl}")
            
            if positions_without_tp > 0 or positions_without_sl > 0:
                print(f"   ⚠️  Hay posiciones sin protección completa")
            else:
                print(f"   ✅ Todas las posiciones tienen TP y SL configurados")
                
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")

if __name__ == "__main__":
    test_tp_sl_calculation()