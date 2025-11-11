import csv
import json
import os
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class TradeRecord:
    trade_id: str
    instrument_symbol: str
    instrument_name: str
    execution_type: str
    status: str
    source: str
    quantity: float
    price: float
    take_profit: Optional[float]
    stop_loss: Optional[float]
    gsl: Optional[bool]
    rpl: Optional[float]
    fee: Optional[float]
    timestamp: datetime


def parse_float(val: str) -> Optional[float]:
    try:
        if val is None or val == "":
            return None
        return float(val)
    except Exception:
        return None


def parse_bool(val: str) -> Optional[bool]:
    try:
        if val is None:
            return None
        return val.strip().lower() == "true"
    except Exception:
        return None


def parse_datetime_utc(val: str) -> datetime:
    # CSV usa formato "YYYY-MM-DD HH:MM:SS" en UTC
    return datetime.strptime(val.strip(), "%Y-%m-%d %H:%M:%S")


def read_trades_csv(file_path: str) -> List[TradeRecord]:
    trades: List[TradeRecord] = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                trades.append(
                    TradeRecord(
                        trade_id=row.get("Trade Id", ""),
                        instrument_symbol=row.get("Instrument Symbol", ""),
                        instrument_name=row.get("Instrument Name", ""),
                        execution_type=row.get("Execution Type", ""),
                        status=row.get("Status", ""),
                        source=row.get("Source", ""),
                        quantity=parse_float(row.get("Quantity")) or 0.0,
                        price=parse_float(row.get("Price")) or 0.0,
                        take_profit=parse_float(row.get("Take Profit")),
                        stop_loss=parse_float(row.get("Stop Loss")),
                        gsl=parse_bool(row.get("gsl")),
                        rpl=parse_float(row.get("rpl")),
                        fee=parse_float(row.get("Fee")),
                        timestamp=parse_datetime_utc(row.get("Timestamp", "1970-01-01 00:00:00")),
                    )
                )
            except Exception:
                # saltar filas mal formateadas
                continue
    return trades


def read_funds_csv(file_path: str) -> List[Dict[str, str]]:
    events: List[Dict[str, str]] = []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    return events


def side_from_quantity(qty: float) -> Optional[str]:
    if qty > 0:
        return "BUY"
    if qty < 0:
        return "SELL"
    return None


def detect_distance_mode(price: float, tp: Optional[float], sl: Optional[float]) -> bool:
    """Heurística para detectar si TP/SL están expresados como distancias.

    - Si tp y sl tienen signos opuestos, probablemente son distancias (p.ej. BUY: tp>0, sl<0).
    - Si ambos son muy pequeños respecto al precio (p.ej. <1% del precio), es probable que sean distancias.
    """
    try:
        if tp is not None and sl is not None:
            if tp * sl < 0:
                return True
        # 1% del precio como umbral de pequeñez para detectar distancias
        if price > 1.0:
            small = price * 0.01
            if (tp is not None and abs(tp) < small) and (sl is not None and abs(sl) < small):
                return True
        return False
    except Exception:
        return False


def tp_sl_orientation_ok_open(
    side: Optional[str], entry_price: float, tp: Optional[float], sl: Optional[float]
) -> bool:
    """Valida orientación TP/SL en el momento de apertura.

    - Si están expresados como niveles: BUY -> tp>entry, sl<entry; SELL -> tp<entry, sl>entry
    - Si están expresados como distancias: BUY -> tp>0, sl<0; SELL -> tp<0, sl>0
    """
    if side is None:
        return True
    distance_mode = detect_distance_mode(entry_price, tp, sl)
    if distance_mode:
        if side == "BUY":
            return (tp is None or tp > 0) and (sl is None or sl < 0)
        else:
            return (tp is None or tp < 0) and (sl is None or sl > 0)
    else:
        if side == "BUY":
            return (tp is None or tp > entry_price) and (sl is None or sl < entry_price)
        else:
            return (tp is None or tp < entry_price) and (sl is None or sl > entry_price)


def sl_distance_points_open(side: Optional[str], entry_price: float, sl: Optional[float]) -> Optional[float]:
    """Distancia del SL al precio de apertura, soportando modo distancia y niveles."""
    if sl is None or side is None:
        return None
    distance_mode = detect_distance_mode(entry_price, None, sl)
    if distance_mode:
        # si es distancia, tomamos el valor absoluto
        try:
            return abs(sl)
        except Exception:
            return None
    # niveles
    if side == "BUY":
        return max(0.0, entry_price - sl)
    else:
        return max(0.0, sl - entry_price)


def summarize_trades(trades: List[TradeRecord]) -> Dict:
    by_symbol: Dict[str, Dict] = {}

    for t in trades:
        sym = t.instrument_symbol or "UNKNOWN"
        if sym not in by_symbol:
            by_symbol[sym] = {
                "count": 0,
                "opens": 0,
                "closes": 0,
                "wins": 0,
                "losses": 0,
                "total_rpl": 0.0,
                "avg_rpl": None,
                "avg_sl_distance": None,
                "orientation_issues": 0,
                "sl_closures": 0,
                "examples": [],
            }

        bucket = by_symbol[sym]
        bucket["count"] += 1

        # determinar side
        side = side_from_quantity(t.quantity)

        # Validar orientación SOLO en apertura (OPENED) usando entry_price
        if t.status.upper() == "OPENED":
            orientation_ok = tp_sl_orientation_ok_open(side, t.price, t.take_profit, t.stop_loss)
            if not orientation_ok:
                bucket["orientation_issues"] += 1
            # distancia de SL desde apertura
            if t.stop_loss is not None:
                dist = sl_distance_points_open(side, t.price, t.stop_loss)
                if dist is not None:
                    prev = bucket.get("_sl_distances", [])
                    prev.append(dist)
                    bucket["_sl_distances"] = prev

        # conteo de eventos OPEN/CLOSE
        if t.status.upper() == "OPENED":
            bucket["opens"] += 1
        if t.status.upper() == "CLOSED":
            bucket["closes"] += 1
            # SL closures (cuando Source o Execution Type indica SL)
            if (t.source or "").upper() == "SL" or (t.execution_type or "").upper() == "SL":
                bucket["sl_closures"] += 1
            # determinar win/loss por rpl
            pnl = t.rpl or 0.0
            bucket["total_rpl"] += pnl
            if pnl >= 0:
                bucket["wins"] += 1
            else:
                bucket["losses"] += 1
            if len(bucket["examples"]) < 5:
                bucket["examples"].append({
                    "timestamp": t.timestamp.isoformat(),
                    "side": side,
                    "price": t.price,
                    "tp": t.take_profit,
                    "sl": t.stop_loss,
                    "rpl": pnl,
                    "status": t.status,
                    "source": t.source,
                    "execution_type": t.execution_type,
                })

    # post proceso: promedios
    for sym, bucket in by_symbol.items():
        count = bucket["closes"]
        if count > 0:
            bucket["avg_rpl"] = bucket["total_rpl"] / count
        dists = bucket.get("_sl_distances", [])
        if dists:
            bucket["avg_sl_distance"] = sum(dists) / len(dists)
        # limpiar campos internos
        if "_sl_distances" in bucket:
            del bucket["_sl_distances"]

    # resumen global
    total_rpl = sum(b["total_rpl"] for b in by_symbol.values())
    total_closes = sum(b["closes"] for b in by_symbol.values())
    global_summary = {
        "total_symbols": len(by_symbol),
        "total_closes": total_closes,
        "total_rpl": total_rpl,
        "avg_rpl": (total_rpl / total_closes) if total_closes > 0 else None,
        "symbols": by_symbol,
    }
    return global_summary


def analyze_reports(
    trades_csv: str,
    funds_csv: Optional[str] = None,
    output_json: Optional[str] = None,
) -> Dict:
    trades = read_trades_csv(trades_csv)
    summary = summarize_trades(trades)

    # incluir algunos insights del funds report si está disponible
    funds_summary = {}
    if funds_csv and os.path.exists(funds_csv):
        funds = read_funds_csv(funds_csv)
        # cambios de balance por tipo
        changes_by_type: Dict[str, float] = {}
        for e in funds:
            amount = parse_float(e.get("Amount")) or 0.0
            typ = e.get("Type", "UNKNOWN").upper()
            changes_by_type[typ] = changes_by_type.get(typ, 0.0) + amount
        funds_summary = {
            "events": len(funds),
            "changes_by_type": changes_by_type,
        }

    result = {
        "meta": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "trades_csv": trades_csv,
            "funds_csv": funds_csv,
        },
        "summary": summary,
        "funds": funds_summary,
        "diagnostics": generate_diagnostics(summary),
    }

    if output_json:
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

    return result


def generate_diagnostics(summary: Dict) -> List[str]:
    diagnostics: List[str] = []
    symbols = summary.get("symbols", {})

    # 1) excesivos cierres por SL
    for sym, bucket in symbols.items():
        closes = bucket.get("closes", 0)
        sl_closures = bucket.get("sl_closures", 0)
        if closes >= 3 and sl_closures / max(1, closes) > 0.5:
            diagnostics.append(
                f"{sym}: alto porcentaje de cierres por SL ({sl_closures}/{closes}). Revisar distancia de SL / volatilidad."
            )

    # 2) orientación TP/SL incorrecta
    for sym, bucket in symbols.items():
        issues = bucket.get("orientation_issues", 0)
        if issues > 0:
            diagnostics.append(
                f"{sym}: {issues} eventos con orientación TP/SL incoherente respecto al lado. Validar lógica de envío."
            )

    # 3) pérdidas promedio por símbolo
    for sym, bucket in symbols.items():
        avg_rpl = bucket.get("avg_rpl")
        closes = bucket.get("closes", 0)
        if closes >= 3 and (avg_rpl is not None) and avg_rpl < 0:
            diagnostics.append(
                f"{sym}: rpl promedio negativo ({avg_rpl:.2f}) con {closes} cierres. Ajustar señales o RR."
            )

    return diagnostics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Analiza reportes live de Capital.com")
    parser.add_argument(
        "--trades",
        required=True,
        help="Ruta a leveraged_trades_history_*.csv",
    )
    parser.add_argument(
        "--funds",
        required=False,
        help="Ruta a funds_history_*.csv",
    )
    parser.add_argument(
        "--out",
        required=False,
        help="Ruta de salida JSON para el resumen",
    )

    args = parser.parse_args()
    result = analyze_reports(args.trades, args.funds, args.out)
    print(json.dumps(result, indent=2))