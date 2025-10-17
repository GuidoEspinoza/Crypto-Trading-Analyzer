#!/usr/bin/env python3
"""
Smoke test de normalización de símbolos y simulación de PaperTrader

Este script verifica:
1) Normalización de precios en distintas fuentes para símbolos en formato ticker (BTCUSD) y con slash (BTC/USD),
   además de la stable USD.
2) Ejecución de BUY/SELL en PaperTrader usando formatos ticker y slash,
   validando que el asset_symbol se maneje correctamente en el portfolio.
3) Validación de la función validate_trade con SELL en formato ticker con símbolo inválido (no USD).

Nota: Para precios en tiempo real, se usa Capital.com API (integración pendiente).
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

# Importar configuración global
from src.config.main_config import GLOBAL_SYMBOLS


def smoke_test_prices():
    print("\n=== Smoke Test de Precios ===")
    # Usar símbolos globales más USD para pruebas
    symbols = GLOBAL_SYMBOLS + ['USD']
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

    # BUY ticker GOLD
    s1 = make_signal('GOLD', 'BUY', 2000.0)
    r1 = pt.execute_signal(s1)
    print('BUY ticker GOLD ->', r1)

    # SELL ticker GOLD
    s2 = make_signal('GOLD', 'SELL', 2010.0)
    r2 = pt.execute_signal(s2)
    print('SELL ticker GOLD ->', r2)

    # BUY slash SILVER/USD
    s3 = make_signal('SILVER/USD', 'BUY', 25.0)
    r3 = pt.execute_signal(s3)
    print('BUY slash SILVER/USD ->', r3)

    # SELL slash SILVER/USD
    s4 = make_signal('SILVER/USD', 'SELL', 24.5)
    r4 = pt.execute_signal(s4)
    print('SELL slash SILVER/USD ->', r4)

    # Resumen de portfolio
    summary = pt.get_portfolio_summary()
    print('Portfolio summary assets:', summary.get('assets'))

    # validate_trade con SELL PLATINUM
    res_validate = pt.validate_trade({'symbol': 'PLATINUM', 'side': 'SELL', 'quantity': 1.0, 'price': 1000.0})
    print('validate_trade SELL PLATINUM ->', res_validate)

def rank_symbols_performance():
    """
    📈 Ranking de performance por símbolo (simulado - Capital.com integration pending)
    Nota: Esta función ahora muestra un ranking simulado ya que se eliminó la dependencia de Binance/ccxt.
    Para datos reales, se necesitaría implementar la integración con Capital.com.
    """
    print("\n=== Ranking de Símbolos por Performance (Simulado) ===")
    print("ℹ️ Nota: Ranking simulado - integración con Capital.com pendiente")
    
    # Ranking simulado basado en los símbolos globales
    simulated_results = []
    for i, symbol in enumerate(GLOBAL_SYMBOLS):
        # Simular métricas de performance
        import random
        random.seed(hash(symbol))  # Seed consistente por símbolo
        
        total_return = random.uniform(-15.0, 25.0)  # Retorno entre -15% y +25%
        sharpe = random.uniform(0.5, 2.5)  # Sharpe ratio entre 0.5 y 2.5
        volatility = random.uniform(10.0, 40.0)  # Volatilidad entre 10% y 40%
        
        simulated_results.append({
            'symbol': f"{symbol}/USD",
            'total_return_pct': total_return,
            'sharpe': sharpe,
            'volatility': volatility
        })
    
    # Ordenar por retorno, desempate por sharpe
    simulated_results.sort(key=lambda x: (x['total_return_pct'], x['sharpe']), reverse=True)
    
    for i, r in enumerate(simulated_results, start=1):
        print(f"{i:2d}. {r['symbol']:10s} | Return: {r['total_return_pct']:+6.2f}% | Sharpe: {r['sharpe']:.2f} | Vol: {r['volatility']:.2f}%")
    
    top5 = [r['symbol'] for r in simulated_results[:5]]
    print("\n🏆 Top 5 sugeridos por performance (simulado):", ', '.join(top5))
    print("💡 Para datos reales, implementar integración con Capital.com API")
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