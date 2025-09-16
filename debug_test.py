#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.paper_trader import PaperTrader
from src.core.enhanced_strategies import TradingSignal

def main():
    # Crear trader
    trader = PaperTrader(initial_balance=1000.0)
    print(f'Initial balance: {trader.initial_balance}')
    print(f'Min trade value: {trader.min_trade_value}')
    print(f'Min confidence threshold: {trader.min_confidence_threshold}')
    print(f'Max position size: {trader.max_position_size}')

    # Crear señal
    from datetime import datetime
    signal = TradingSignal(
        symbol='BTC/USDT',
        signal_type='BUY',
        price=50000.0,
        confidence_score=85.0,
        strategy_name='test_strategy',
        strength=0.8,
        indicators_data={},
        timestamp=datetime.now()
    )

    # Verificar balance USDT
    try:
        usdt_balance = trader._get_usdt_balance()
        print(f'USDT balance from DB: {usdt_balance}')
    except Exception as e:
        print(f'Error getting USDT balance: {e}')

    # Verificar validación
    is_valid, message = trader._validate_signal(signal)
    print(f'Signal validation: {is_valid}, message: {message}')
    
    # Calcular valores de trade
    usdt_balance = trader._get_usdt_balance()
    max_trade_value = usdt_balance * trader.max_position_size
    print(f'USDT balance: {usdt_balance}')
    print(f'Max trade value: {max_trade_value}')
    print(f'Min trade value required: {trader.min_trade_value}')

if __name__ == "__main__":
    main()