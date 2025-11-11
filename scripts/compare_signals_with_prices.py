import os
import json
import glob
import argparse
from datetime import datetime, timedelta, timezone

# Ajustar sys.path para permitir importaciones de src/* cuando se ejecuta desde scripts/
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.core.capital_client import create_capital_client_from_env

# Mapeo de resolución a minutos para ventanas por señal
RESOLUTION_MINUTES = {
    "MINUTE": 1,
    "MINUTE_2": 2,
    "MINUTE_3": 3,
    "MINUTE_5": 5,
    "MINUTE_10": 10,
    "MINUTE_15": 15,
    "MINUTE_30": 30,
    "HOUR": 60,
    "HOUR_2": 120,
    "HOUR_3": 180,
    "HOUR_4": 240,
    "DAY": 60 * 24,
    "WEEK": 60 * 24 * 7,
}

# Fallback RR y horizonte por clase de activo
RR_FALLBACK_BY_CLASS = {
    "CURRENCIES": 1.3,
    "INDICES": 1.1,
    "COMMODITIES": 1.2,
    "CRYPTOCURRENCIES": 1.7,
    "SHARES": 1.3,
}

HORIZON_BARS_BY_CLASS = {
    "CURRENCIES": 20,
    "INDICES": 15,
    "COMMODITIES": 20,
    "CRYPTOCURRENCIES": 20,
    "SHARES": 30,
}


def find_latest_paper_output(outputs_dir: str) -> str:
    pattern = os.path.join(outputs_dir, "test_FULLBOT_PAPER_*.json")
    files = glob.glob(pattern)
    if not files:
        raise FileNotFoundError("No se encontró ningún archivo test_FULLBOT_PAPER_*.json en outputs.")
    files.sort()
    return files[-1]


def load_order_previews(path: str):
    with open(path, "r") as f:
        data = json.load(f)
    previews = data.get("order_previews") or []
    trade_history = data.get("paper_trader", {}).get("trade_history", [])
    return previews, trade_history


def derive_side_from_trade_type(trade_type: str) -> str:
    if not trade_type:
        return ""
    return "BUY" if trade_type.upper().startswith("BUY") else "SELL"


def find_matching_preview(previews: list, symbol: str, side: str, entry_price: float):
    """
    Busca el preview que más se aproxima al trade ejecutado (por símbolo, lado y precio).
    """
    candidates = [p for p in previews if (p.get("symbol") == symbol and (p.get("side") or p.get("signal_type")) == side)]
    if not candidates:
        return None
    # Elegir por mínima diferencia de precio de entrada
    best = None
    best_diff = float("inf")
    for p in candidates:
        ep = p.get("entry_price")
        if ep is None:
            continue
        diff = abs(ep - entry_price)
        if diff < best_diff:
            best_diff = diff
            best = p
    return best or candidates[0]


def evaluate_signal_against_prices(signal_side: str, entry_price: float, sl_final: float, tp_final: float, prices: list, horizon_bars: int = 10, rr_fallback: float = 1.5, start_index: int = 0) -> dict:
    """
    Para cada barra en la serie, simula entrada en el open y evalúa
    si se alcanzaría primero el TP o el SL dentro del horizonte.
    Devuelve conteos agregados.
    """
    successes = 0
    failures = 0
    neutral = 0

    if entry_price is None or sl_final is None:
        return {"success": successes, "failure": failures, "neutral": neutral}

    # SL distance is mandatory; TP distance can fallback to RR multipliers
    tp_distance = abs(tp_final - entry_price) if tp_final is not None else None
    sl_distance = abs(entry_price - sl_final)
    if sl_distance <= 0:
        return {"success": successes, "failure": failures, "neutral": neutral}

    # Fallback RR multiplier if TP not provided
    if tp_distance is None or tp_distance <= 0:
        tp_distance = sl_distance * rr_fallback

    total_points = len(prices)
    # Evaluar desde el índice cercano a la entrada
    for i in range(max(0, start_index), total_points):
        open_price = prices[i].get("open")
        if not open_price:
            continue

        if signal_side == "BUY":
            tp_level = open_price + tp_distance
            sl_level = open_price - sl_distance
        else:  # SELL
            tp_level = open_price - tp_distance
            sl_level = open_price + sl_distance

        tp_hit_index = None
        sl_hit_index = None

        end_index = min(total_points, i + horizon_bars)
        for j in range(i, end_index):
            high = prices[j].get("high")
            low = prices[j].get("low")
            if high is None or low is None:
                continue

            if signal_side == "BUY":
                if tp_hit_index is None and high >= tp_level:
                    tp_hit_index = j
                if sl_hit_index is None and low <= sl_level:
                    sl_hit_index = j
            else:  # SELL
                if tp_hit_index is None and low <= tp_level:
                    tp_hit_index = j
                if sl_hit_index is None and high >= sl_level:
                    sl_hit_index = j

            if tp_hit_index is not None and sl_hit_index is not None:
                break

        if tp_hit_index is None and sl_hit_index is None:
            neutral += 1
        elif tp_hit_index is not None and sl_hit_index is None:
            successes += 1
        elif sl_hit_index is not None and tp_hit_index is None:
            failures += 1
        else:
            # Si ambos ocurren, cuenta el que ocurra primero
            if tp_hit_index < sl_hit_index:
                successes += 1
            elif sl_hit_index < tp_hit_index:
                failures += 1
            else:
                neutral += 1

    return {"success": successes, "failure": failures, "neutral": neutral}


def compute_atr(prices: list, period: int = 14) -> float:
    """Calcula un ATR simple sobre la lista de precios."""
    if not prices or len(prices) < 2:
        return 0.0
    trs = []
    prev_close = prices[0].get("close")
    for i in range(1, len(prices)):
        high = prices[i].get("high")
        low = prices[i].get("low")
        close = prices[i].get("close")
        if high is None or low is None or close is None or prev_close is None:
            prev_close = close
            continue
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)
        prev_close = close
    if not trs:
        return 0.0
    period = max(1, min(period, len(trs)))
    return sum(trs[-period:]) / float(period)


def find_bar_index_near_entry(prices: list, entry_time_iso: str) -> int:
    """Encuentra el índice de la barra cuyo timestamp sea igual o posterior al entry_time."""
    if not entry_time_iso:
        return 0
    try:
        entry_dt = datetime.fromisoformat(entry_time_iso)
    except Exception:
        return 0
    for i, p in enumerate(prices):
        ts = p.get("timestamp_utc") or p.get("timestamp")
        if not ts:
            continue
        try:
            ts_dt = datetime.fromisoformat(ts)
        except Exception:
            continue
        if ts_dt >= entry_dt:
            return i
    return 0


def main():
    parser = argparse.ArgumentParser(description="Comparar señales paper con precios históricos de Capital.com")
    parser.add_argument("--resolution", default="MINUTE_30")
    parser.add_argument("--max", dest="max_points", type=int, default=100)
    parser.add_argument("--from", dest="from_date", default="2025-11-01T00:00:00")
    parser.add_argument("--to", dest="to_date", default="2025-11-10T01:00:00")
    parser.add_argument("--outputs-dir", default=os.path.join("scripts", "outputs"))
    parser.add_argument("--horizon", type=int, default=10, help="Cantidad de barras a evaluar por señal (fallback)" )
    parser.add_argument("--pre-bars", type=int, default=10, help="Barras previas a la entrada para cálculo ATR y contexto")
    parser.add_argument("--post-bars", type=int, default=30, help="Barras posteriores a la entrada para evaluación")
    args = parser.parse_args()

    outputs_dir = args.outputs_dir
    latest_path = find_latest_paper_output(outputs_dir)
    previews, trade_history = load_order_previews(latest_path)
    if not previews:
        print("No hay order_previews en el archivo paper.")
        return

    client = create_capital_client_from_env()
    # Crear sesión si no está activa
    client.create_session()

    summary = {
        "source_file": os.path.basename(latest_path),
        "resolution": args.resolution,
        "from": args.from_date,
        "to": args.to_date,
        "generated_at": datetime.utcnow().isoformat(),
        "symbols": {},
        "classes": {},
    }

    # Evaluación basada en trades ejecutados (ventanas por señal)
    for trade in trade_history:
        symbol = trade.get("symbol")
        trade_type = trade.get("trade_type")
        side = derive_side_from_trade_type(trade_type)
        entry_price = trade.get("entry_price")
        entry_time = trade.get("entry_time")
        if not symbol or not side or entry_price is None or not entry_time:
            continue

        # Buscar preview correspondiente para obtener SL/TP finales
        matched_preview = find_matching_preview(previews, symbol, side, entry_price)
        sl_final = matched_preview.get("sl_final") if matched_preview else None
        tp_final = matched_preview.get("tp_final") if matched_preview else None

        # Determinar clase de activo y RR/horizonte por clase
        asset_class = client.get_asset_type_from_symbol(symbol)
        rr_fb = RR_FALLBACK_BY_CLASS.get(asset_class, 1.5)
        horizon_bars = HORIZON_BARS_BY_CLASS.get(asset_class, args.horizon)

        # Construir ventana por señal usando entry_time y resolución
        res_minutes = RESOLUTION_MINUTES.get(args.resolution, 30)
        pre_delta = timedelta(minutes=res_minutes * args.pre_bars)
        post_delta = timedelta(minutes=res_minutes * args.post_bars)
        entry_dt = datetime.fromisoformat(entry_time)
        from_dt = entry_dt - pre_delta
        to_dt = entry_dt + post_delta
        # Asegurar timezone UTC
        if from_dt.tzinfo is None:
            from_dt = from_dt.replace(tzinfo=timezone.utc)
        if to_dt.tzinfo is None:
            to_dt = to_dt.replace(tzinfo=timezone.utc)
        # No solicitar datos en el futuro
        now_utc = datetime.now(timezone.utc)
        if to_dt > now_utc:
            to_dt = now_utc

        # Capital.com prefiere timestamps sin zona horaria en formato ISO simple
        from_str = from_dt.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")
        to_str = to_dt.replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S")
        price_result = client.get_historical_prices(
            epic=symbol,
            resolution=args.resolution,
            max_points=args.max_points,
            from_date=from_str,
            to_date=to_str,
        )
        if not price_result.get("success"):
            summary["symbols"].setdefault(symbol, {})["error"] = price_result.get("error")
            continue

        prices = price_result.get("prices", [])
        if not prices:
            summary["symbols"].setdefault(symbol, {})["error"] = "Sin precios en rango"
            continue

        # Índice cercano a la entrada
        start_idx = find_bar_index_near_entry(prices, entry_time)

        # ATR para métricas y flags
        atr_value = compute_atr(prices[:start_idx] or prices, period=14)

        counts = evaluate_signal_against_prices(
            side,
            entry_price,
            sl_final,
            tp_final,
            prices,
            horizon_bars=horizon_bars,
            rr_fallback=rr_fb,
            start_index=start_idx,
        )
        sym = summary["symbols"].setdefault(
            symbol,
            {"signals": 0, "success": 0, "failure": 0, "neutral": 0, "atr": 0.0, "asset_class": asset_class},
        )
        sym["signals"] += 1
        sym["success"] += counts["success"]
        sym["failure"] += counts["failure"]
        sym["neutral"] += counts["neutral"]
        sym["atr"] = atr_value

        # Agregar KPIs por clase
        cls = summary["classes"].setdefault(
            asset_class,
            {"signals": 0, "success": 0, "failure": 0, "neutral": 0}
        )
        cls["signals"] += 1
        cls["success"] += counts["success"]
        cls["failure"] += counts["failure"]
        cls["neutral"] += counts["neutral"]

    # KPIs por símbolo
    for symbol, stats in summary["symbols"].items():
        total = stats.get("success", 0) + stats.get("failure", 0)
        stats["hit_rate_pct"] = round((stats.get("success", 0) / max(1, total)) * 100, 2)

    # KPIs por clase de activo
    for cls_name, stats in summary["classes"].items():
        total = stats.get("success", 0) + stats.get("failure", 0)
        stats["hit_rate_pct"] = round((stats.get("success", 0) / max(1, total)) * 100, 2)

    # Guardar resultado
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(outputs_dir, f"comparison_prices_vs_paper_{ts}.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Comparación guardada en {out_path}")


if __name__ == "__main__":
    main()