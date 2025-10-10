#!/usr/bin/env python3
"""
Smoke test de normalización de símbolos y simulación de PaperTrader

Este script verifica:
1) Normalización de precios en distintas fuentes para símbolos en formato ticker (BTCUSDT) y con slash (BTC/USDT),
   además de la stable USDT.
2) Ejecución de BUY/SELL en PaperTrader usando formatos ticker y slash,
   validando que el asset_symbol se maneje correctamente en el portfolio.
3) Validación de la función validate_trade con SELL en formato ticker con símbolo inválido (no USDT).

Nota: Para precios en tiempo real, es posible que necesites instalar dependencias (ccxt, etc.).
      Si ves errores de importación en precios, ejecuta:  pip3 install -r requirements.txt
"""
import os
import sys
import time
from datetime import datetime
from types import SimpleNamespace

# Resolver rutas del proyecto
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Helpers para cargar módulos por ruta, evitando imports de paquetes que arrastren dependencias pesadas
import importlib.util

def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Intentar cargar requests para trading_monitor; si no está, saltar trading_monitor
HAS_REQUESTS = True
try:
    import requests  # noqa: F401
except Exception:
    HAS_REQUESTS = False

# Cargar trading_monitor.get_current_price directamente por ruta SOLO si hay requests
TRADING_MONITOR_PATH = os.path.join(PROJECT_ROOT, 'src', 'tools', 'trading_monitor.py')
if HAS_REQUESTS:
    trading_monitor = load_module_from_path('trading_monitor', TRADING_MONITOR_PATH)
    get_current_price = trading_monitor.get_current_price
else:
    def get_current_price(symbol: str):
        return 'skipped: requests not installed'

# Importar db_manager de forma estándar (no debería arrastrar pandas)
from src.database.database import db_manager

# Importar PaperTrader de forma estándar (paper_trader evita importar enhanced_strategies en runtime)
from src.core.paper_trader import PaperTrader


def smoke_test_prices():
    print("\n=== Smoke Test de Precios ===")
    symbols = ['BTCUSDT', 'BTC/USDT', 'ETHUSDT', 'SOLUSDT', 'USDT']
    for sym in symbols:
        try:
            tm_price = get_current_price(sym)
        except Exception as e:
            tm_price = f'error: {e}'
        try:
            db_price = db_manager._get_current_price(sym)
        except Exception as e:
            db_price = f'error: {e}'
        print(f"{sym:10s} | trading_monitor: {tm_price} | db_manager: {db_price}")


def simulate_paper_trader():
    print("\n=== Simulación PaperTrader ===")
    pt = PaperTrader()
    try:
        pt.reset_portfolio()
    except Exception:
        # Ignorar si no existe método o falla reset
        pass

    now = datetime.now()

    def make_signal(sym, typ, price):
        # SimpleNamespace con los atributos que PaperTrader necesita
        return SimpleNamespace(
            symbol=sym,
            signal_type=typ,
            price=float(price),
            confidence_score=80.0,
            strength='Strong',
            strategy_name='TestStrategy',
            timestamp=now,
            indicators_data={},
            notes='Test',
            stop_loss_price=float(price) * 0.95,
            take_profit_price=float(price) * 1.05
        )

    # BUY ticker AVAXUSDT
    s1 = make_signal('AVAXUSDT', 'BUY', 28.39)
    r1 = pt.execute_signal(s1)
    print('BUY ticker AVAXUSDT ->', r1)

    # SELL ticker AVAXUSDT
    s2 = make_signal('AVAXUSDT', 'SELL', 28.50)
    r2 = pt.execute_signal(s2)
    print('SELL ticker AVAXUSDT ->', r2)

    # BUY slash ETH/USDT
    s3 = make_signal('ETH/USDT', 'BUY', 3400.0)
    r3 = pt.execute_signal(s3)
    print('BUY slash ETH/USDT ->', r3)

    # SELL slash ETH/USDT
    s4 = make_signal('ETH/USDT', 'SELL', 3390.0)
    r4 = pt.execute_signal(s4)
    print('SELL slash ETH/USDT ->', r4)

    # Resumen de portfolio
    summary = pt.get_portfolio_summary()
    print('Portfolio summary assets:', summary.get('assets'))

    # validate_trade con SELL SOLUSDC
    res_validate = pt.validate_trade({'symbol': 'SOLUSD', 'side': 'SELL', 'quantity': 1.0, 'price': 150.0})
    print('validate_trade SELL SOLUSD ->', res_validate)


if __name__ == '__main__':
    smoke_test_prices()
    simulate_paper_trader()