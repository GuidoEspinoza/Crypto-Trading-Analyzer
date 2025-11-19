"""
Test: Ejecuta el funcionamiento completo del bot en modo papel (sin enviar
trades reales a Capital.com). Corre uno o más ciclos de análisis, procesa
señales, aplica políticas (antiflip, riesgo, límites) y registra un resumen
en JSON dentro de scripts/outputs.

Uso:
  python scripts/test_full_bot_paper.py --cycles 1 --sleep 0

Argumentos:
  --cycles   Número de ciclos completos a ejecutar (por defecto: 1)
  --sleep    Segundos entre ciclos cuando cycles > 1 (por defecto: 0)

Nota:
- El trading REAL queda desactivado explícitamente.
- El trading en PAPEL queda activado para simular entradas/salidas.
"""

import argparse
import json
import os
import time
import sys
from datetime import datetime, date

# Asegurar que el proyecto esté en sys.path para importar 'src.*'
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.core.trading_bot import TradingBot
from src.config.time_trading_config import UTC_TZ
from src.config.time_trading_config import SMART_TRADING_HOURS


def ensure_outputs_dir() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    outputs_dir = os.path.join(base_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    return outputs_dir


def run_cycle(bot: TradingBot):
    """Ejecuta un ciclo de análisis completo del bot con ejecución inmediata.

    Usa el flujo de producción del bot: aplica límites diarios, cache cuando
    corresponda y análisis secuencial con ejecución inmediata, que llama al
    procesamiento de señales y ejecución en papel.
    """
    bot._run_analysis_cycle()


def build_summary(bot: TradingBot, cycles_run: int) -> dict:
    """Construye un resumen del estado del bot y del PaperTrader."""
    paper = bot.paper_trader

    portfolio_summary = paper.get_portfolio_summary()
    paper_stats = paper.get_statistics()
    trade_history = paper.get_trade_history()

    # Métricas del tope diario desde el bot
    bot_daily_cap = {
        "mode": getattr(bot, "daily_profit_cap_mode", "equity"),
        "max_daily_profit_percent": getattr(bot, "max_daily_profit_percent", 0.0),
        "baseline_capital": getattr(bot, "daily_start_value", None),
        "baseline_fonds": getattr(bot, "daily_start_funds", None),
        "pause_active": getattr(bot, "daily_pause_active", False),
    }

    # Cálculo explícito de porcentajes para modo compuesto
    try:
        baseline_capital = bot_daily_cap.get("baseline_capital")
        baseline_fonds = bot_daily_cap.get("baseline_fonds")

        current_equity = portfolio_summary.get("total_value")
        current_funds = portfolio_summary.get("funds_balance")

        def _pct(current, baseline):
            try:
                if baseline is None or baseline == 0:
                    return None
                return ((float(current) - float(baseline)) / float(baseline)) * 100.0
            except Exception:
                return None

        equity_pct = _pct(current_equity, baseline_capital)
        realized_pct = _pct(current_funds, baseline_fonds)

        # pnl% del portfolio (ya normalizado por el PaperTrader); si falta, calcularlo
        pnl_pct = portfolio_summary.get("total_pnl_percentage")
        if pnl_pct is None:
            pnl = portfolio_summary.get("total_pnl")
            # Si no hay baseline capital, intentar usar initial_balance del portfolio
            baseline_for_pnl = portfolio_summary.get("initial_balance") or baseline_capital or baseline_fonds
            pnl_pct = _pct(float(baseline_for_pnl) + float(pnl or 0.0), baseline_for_pnl)

        # Determinar métrica que predomina (para composite_or)
        candidates = {
            "equity_pct": equity_pct,
            "pnl_pct": pnl_pct,
            "realized_pct": realized_pct,
        }
        # Filtrar None y obtener máximo
        max_metric = None
        max_value = None
        for k, v in candidates.items():
            if v is None:
                continue
            if (max_value is None) or (v > max_value):
                max_metric = k
                max_value = v

        bot_daily_cap_metrics = {
            "equity_pct": equity_pct,
            "pnl_pct": pnl_pct,
            "realized_pct": realized_pct,
            "max_pct": max_value,
            "trigger_metric": max_metric,
            "trigger_reached": (
                (max_value is not None)
                and (bot_daily_cap.get("max_daily_profit_percent") is not None)
                and (max_value >= bot_daily_cap.get("max_daily_profit_percent"))
            ),
        }
    except Exception:
        bot_daily_cap_metrics = {
            "equity_pct": None,
            "pnl_pct": None,
            "realized_pct": None,
            "max_pct": None,
            "trigger_metric": None,
            "trigger_reached": False,
        }

    # Estado antiflip útil para análisis post-run
    antiflip_state = {
        "last_signal_confidences": getattr(bot, "last_signal_confidences", {}),
        "antiflip_opposite_counts": getattr(bot, "antiflip_opposite_counts", {}),
        "last_exit_times": {
            k: v.isoformat() if hasattr(v, "isoformat") else str(v)
            for k, v in getattr(bot, "last_exit_times", {}).items()
        },
    }

    summary = {
        "meta": {
            "timestamp": datetime.now(UTC_TZ).isoformat(),
            "cycles_run": cycles_run,
            "enable_real_trading": False,
            "enable_trading_paper": True,
            "analysis_interval_minutes": bot.analysis_interval,
        },
        "bot": {
            "symbols": bot.symbols,
            "strategies": list(bot.strategies.keys()),
            "stats": bot.stats,
            "daily_cap": bot_daily_cap,
            "daily_cap_metrics": bot_daily_cap_metrics,
        },
        "paper_trader": {
            "portfolio_summary": portfolio_summary,
            "statistics": paper_stats,
            "trade_history": trade_history,
        },
        "antiflip": antiflip_state,
    }
    # Incluir previews de órdenes (SL/TSL aplicados por reglas del instrumento)
    try:
        summary["order_previews"] = getattr(bot, "order_previews", [])
    except Exception:
        summary["order_previews"] = []
    return summary


def _json_safe(obj):
    """Convierte objetos a formas serializables en JSON.

    - datetime/date -> isoformat()
    - dict/list/tuple -> recursivo
    - set -> lista
    - otros tipos desconocidos -> str(obj) como último recurso
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, tuple):
        return [_json_safe(v) for v in obj]
    if isinstance(obj, set):
        return [_json_safe(v) for v in list(obj)]
    # Evitar problemas con tipos no serializables devolviendo su representación
    try:
        json.dumps(obj)
        return obj
    except Exception:
        return str(obj)


def print_console_summary(summary: dict):
    meta = summary["meta"]
    bot_stats = summary["bot"]["stats"]
    paper_stats = summary["paper_trader"]["statistics"]
    daily_cap = summary["bot"].get("daily_cap", {})
    daily_cap_metrics = summary["bot"].get("daily_cap_metrics", {})
    portfolio = summary["paper_trader"]["portfolio_summary"]

    print("\n===== Resumen de ejecución del bot (modo papel) =====")
    print(f"Timestamp: {meta['timestamp']}")
    print(f"Ciclos ejecutados: {meta['cycles_run']}")
    print(f"Trading real: {meta['enable_real_trading']}")
    print(f"Trading en papel: {meta['enable_trading_paper']}")
    print("- Estrategias:", ", ".join(summary["bot"]["strategies"]))
    print("- Símbolos:", ", ".join(summary["bot"]["symbols"]))
    print("- Estadísticas del bot:")
    for k, v in bot_stats.items():
        print(f"  * {k}: {v}")
    print("- Tope diario:")
    print(
        f"  * modo: {daily_cap.get('mode')} | umbral: {daily_cap.get('max_daily_profit_percent')}% | pausa: {daily_cap.get('pause_active')}"
    )
    print(
        f"  * baseline Capital: {daily_cap.get('baseline_capital')} | baseline Fondos: {daily_cap.get('baseline_fonds')}"
    )
    print("  * métricas (%):")
    print(
        f"    - equity%: {daily_cap_metrics.get('equity_pct')} | pnl%: {daily_cap_metrics.get('pnl_pct')} | realized%: {daily_cap_metrics.get('realized_pct')}"
    )
    print(
        f"    - max%: {daily_cap_metrics.get('max_pct')} | trigger: {daily_cap_metrics.get('trigger_metric')} | reached: {daily_cap_metrics.get('trigger_reached')}"
    )
    print("- Estadísticas del PaperTrader:")
    for k, v in paper_stats.items():
        print(f"  * {k}: {v}")
    print("- Portfolio (paper):")
    print(
        f"  * Fondos: {portfolio.get('funds_balance')} | Capital: {portfolio.get('total_value')} | P&L: {portfolio.get('total_pnl')} | Disponible: {portfolio.get('available_balance')}"
    )
    print("====================================================\n")


def main():
    parser = argparse.ArgumentParser(
        description="Ejecuta el flujo completo del bot en modo papel"
    )
    parser.add_argument("--cycles", type=int, default=1, help="Número de ciclos a ejecutar")
    parser.add_argument(
        "--sleep",
        type=int,
        default=0,
        help="Segundos a dormir entre ciclos cuando cycles > 1",
    )
    args = parser.parse_args()

    # Inicializa el bot con el intervalo de 2 minutos
    bot = TradingBot(analysis_interval_minutes=2)

    # Asegurar configuración de prueba: SIN trading real, CON trading en papel.
    bot.enable_real_trading = False
    bot.enable_trading = True

    # Ajuste temporal para esta prueba: umbral del tope diario a 0.1%
    # Esto fuerza la validación end-to-end de cierre y pausa cuando cualquier
    # métrica (equity/pnl/realized) alcance el 0.1% en modo composite_or.
    try:
        bot.max_daily_profit_percent = 0.001
    except Exception:
        pass

    # Mantener horarios inteligentes tal como en configuración inicial

    outputs_dir = ensure_outputs_dir()
    cycles_run = 0

    for i in range(args.cycles):
        run_cycle(bot)
        cycles_run += 1
        if i < args.cycles - 1 and args.sleep > 0:
            time.sleep(args.sleep)

    summary = build_summary(bot, cycles_run)
    summary_safe = _json_safe(summary)

    # Guardar JSON con timestamp
    ts = datetime.now(UTC_TZ).strftime("%Y%m%d_%H%M%S")
    outfile = os.path.join(outputs_dir, f"test_FULLBOT_PAPER_{ts}.json")
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(summary_safe, f, ensure_ascii=False, indent=2, default=str)

    print_console_summary(summary_safe)
    print(f"✅ Resumen guardado en: {outfile}")


if __name__ == "__main__":
    main()