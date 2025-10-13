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
import ccxt

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

def rank_symbols_performance():
    """
    📈 Ranking de performance por símbolo usando datos OHLCV de Binance (ccxt)
    Métricas:
    - Retorno total últimos 60 días
    - Volatilidad (std de retornos diarios)
    - Sharpe ratio simple (media/std * sqrt(n))
    """
    print("\n=== Ranking de Símbolos por Performance (ccxt/Binance) ===")
    exchange = ccxt.binance()
    candidates = [
        'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT', 'LINK/USDT',
        'MATIC/USDT', 'ADA/USDT', 'XRP/USDT', 'NEAR/USDT', 'BNB/USDT'
    ]
    timeframe = '1d'
    limit = 60

    results = []
    for sym in candidates:
        try:
            ohlcv = exchange.fetch_ohlcv(sym, timeframe=timeframe, limit=limit)
            closes = [c[4] for c in ohlcv]
            if len(closes) < 2:
                raise ValueError('insufficient data')
            total_return = (closes[-1] - closes[0]) / closes[0]
            # Retornos diarios
            daily_returns = []
            for i in range(1, len(closes)):
                if closes[i-1] > 0:
                    daily_returns.append((closes[i] - closes[i-1]) / closes[i-1])
            if len(daily_returns) == 0:
                raise ValueError('no daily returns')
            mean_ret = sum(daily_returns) / len(daily_returns)
            # std
            variance = sum((r - mean_ret) ** 2 for r in daily_returns) / max(1, (len(daily_returns) - 1))
            std_ret = variance ** 0.5
            sharpe = (mean_ret / std_ret) * (len(daily_returns) ** 0.5) if std_ret > 0 else 0.0
            results.append({
                'symbol': sym,
                'total_return_pct': total_return * 100,
                'sharpe': sharpe,
                'volatility': std_ret * 100
            })
        except Exception as e:
            print(f"⚠️ {sym}: error obteniendo OHLCV ({e})")

    # Ordenar por retorno, desempate por sharpe
    results.sort(key=lambda x: (x['total_return_pct'], x['sharpe']), reverse=True)
    for i, r in enumerate(results, start=1):
        print(f"{i:2d}. {r['symbol']:10s} | Return: {r['total_return_pct']:+6.2f}% | Sharpe: {r['sharpe']:.2f} | Vol: {r['volatility']:.2f}%")

    top5 = [r['symbol'] for r in results[:5]]
    print("\n🏆 Top 5 sugeridos por performance (últimos 60d):", ', '.join(top5))
    return top5

if __name__ == '__main__':
    smoke_test_prices()
    simulate_paper_trader()
    run_ranking = os.getenv('RUN_RANKING', '0').lower() in ('1', 'true', 'yes', 'y')
    if run_ranking:
        try:
            rank_symbols_performance()
        except Exception as e:
            print(f"⚠️ Ranking de símbolos omitido: {e}")
    else:
        print("ℹ️ Ranking de símbolos omitido: establece RUN_RANKING=1 para ejecutarlo.")