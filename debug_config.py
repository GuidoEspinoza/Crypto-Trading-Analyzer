#!/usr/bin/env python3

from src.config.paper_trader_config import get_paper_trader_config
import traceback

print('Testing get_paper_trader_config directly:')
try:
    paper_config = get_paper_trader_config('AGRESIVO')
    print(f'Direct call success: {paper_config.get("min_trade_value", "NOT_FOUND")}')
except Exception as e:
    print(f'Direct call error: {e}')
    traceback.print_exc()

print('\nTesting within get_consolidated_config:')
try:
    from src.config.config import get_consolidated_config
    config = get_consolidated_config('AGRESIVO')
    print('Success!')
    print(f'Paper trader config: {config.get("paper_trader", {})}')
    print(f'Min trade value: {config.get("paper_trader", {}).get("min_trade_value", "NOT_FOUND")}')
except Exception as e:
    print(f'Error: {e}')
    traceback.print_exc()