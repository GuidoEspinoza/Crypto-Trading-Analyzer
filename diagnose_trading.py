#!/usr/bin/env python3
"""
🔍 Script de Diagnóstico de Trading
Simula el proceso de trading para identificar por qué no se ejecutan trades
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.config_manager import ConfigManager
from src.database.database import DatabaseManager
from src.database.models import TradingSignal, Trade
from datetime import datetime, timedelta

def main():
    print("🔍 DIAGNÓSTICO DE TRADING")
    print("=" * 50)
    
    # 1. Verificar configuración
    print("\n1. VERIFICANDO CONFIGURACIÓN...")
    config = ConfigManager.get_consolidated_config()
    trading_config = config.get('trading_bot', {})
    
    enable_trading = trading_config.get('enable_trading', False)
    min_confidence = trading_config.get('min_confidence_threshold', 0)
    max_daily_trades = trading_config.get('max_daily_trades', 0)
    
    print(f"   ✅ enable_trading: {enable_trading}")
    print(f"   ✅ min_confidence_threshold: {min_confidence}")
    print(f"   ✅ max_daily_trades: {max_daily_trades}")
    
    if not enable_trading:
        print("   ❌ PROBLEMA: Trading está deshabilitado!")
        return
    
    # 2. Verificar señales recientes
    print("\n2. VERIFICANDO SEÑALES RECIENTES...")
    db = DatabaseManager()
    
    try:
        with db.get_db_session() as session:
            # Últimas 10 señales
            recent_signals = session.query(TradingSignal).order_by(TradingSignal.generated_at.desc()).limit(10).all()
            
            if not recent_signals:
                print("   ❌ No hay señales en la base de datos")
                return
            
            print(f"   ✅ Encontradas {len(recent_signals)} señales recientes")
            
            # Analizar señales por confianza
            high_confidence_signals = [s for s in recent_signals if hasattr(s, 'confidence_score') and s.confidence_score >= min_confidence]
            
            print(f"   📊 Señales con confianza >= {min_confidence}: {len(high_confidence_signals)}")
            
            # Mostrar últimas 5 señales
            print("\n   ÚLTIMAS 5 SEÑALES:")
            for i, signal in enumerate(recent_signals[:5]):
                confidence = getattr(signal, 'confidence_score', 'N/A')
                print(f"   {i+1}. {signal.symbol} - Tipo: {signal.signal_type} - Confianza: {confidence} - {signal.generated_at}")
            
            # 3. Verificar trades del día
            print("\n3. VERIFICANDO TRADES DEL DÍA...")
            today = datetime.now().date()
            today_trades = session.query(Trade).filter(
                Trade.entry_time >= datetime.combine(today, datetime.min.time())
            ).all()
            
            print(f"   📈 Trades ejecutados hoy: {len(today_trades)}")
            
            if len(today_trades) >= max_daily_trades:
                print(f"   ⚠️ LÍMITE ALCANZADO: Ya se ejecutaron {len(today_trades)} trades (máximo: {max_daily_trades})")
            
            # 4. Simular decisión de trading
            print("\n4. SIMULANDO DECISIÓN DE TRADING...")
            
            if high_confidence_signals:
                latest_signal = high_confidence_signals[0]
                print(f"   🎯 Señal candidata: {latest_signal.symbol}")
                print(f"   📊 Confianza: {getattr(latest_signal, 'confidence_score', 'N/A')}")
                print(f"   🕐 Generada: {latest_signal.generated_at}")
                
                # Verificar si ya hay trade para este símbolo
                existing_trade = session.query(Trade).filter(
                    Trade.symbol == latest_signal.symbol,
                    Trade.status == 'active'
                ).first()
                
                if existing_trade:
                    print(f"   ⚠️ Ya existe trade activo para {latest_signal.symbol}")
                else:
                    print(f"   ✅ No hay trade activo para {latest_signal.symbol}")
                    print(f"   🚀 DEBERÍA EJECUTAR TRADE!")
            else:
                print("   ❌ No hay señales con suficiente confianza")
                
    except Exception as e:
        print(f"   ❌ Error accediendo a la base de datos: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 DIAGNÓSTICO COMPLETADO")

if __name__ == "__main__":
    main()