#!/usr/bin/env python3
"""
Script para debuggear la función get_global_initial_balance()
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.config.main_config import get_global_initial_balance, _get_env_float, PAPER_GLOBAL_INITIAL_BALANCE

def debug_balance():
    print("=== DEBUG BALANCE ===")
    
    # Verificar ENABLE_REAL_TRADING
    enable_real_trading = _get_env_float("ENABLE_REAL_TRADING", 0.0)
    print(f"ENABLE_REAL_TRADING: {enable_real_trading} (type: {type(enable_real_trading)})")
    print(f"ENABLE_REAL_TRADING == 1.0: {enable_real_trading == 1.0}")
    
    # Verificar PAPER_GLOBAL_INITIAL_BALANCE
    print(f"PAPER_GLOBAL_INITIAL_BALANCE: {PAPER_GLOBAL_INITIAL_BALANCE}")
    
    # Obtener balance global
    balance = get_global_initial_balance()
    print(f"get_global_initial_balance(): {balance}")
    
    print("=== FIN DEBUG ===")

if __name__ == "__main__":
    debug_balance()