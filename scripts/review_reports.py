#!/usr/bin/env python3
import argparse
import json
import os
import re
from typing import Dict, Any, List, Tuple


def to_code(key: str) -> str:
    """Map report keys like 'ADA/USD' -> 'ADAUSD', keep known non-FX codes as-is."""
    map_special = {
        # Índices
        'US500': 'US500', 'US100': 'US100', 'US30': 'US30',
        'DE40': 'DE40', 'FR40': 'FR40', 'IT40': 'IT40', 'EU50': 'EU50',
        'J225': 'J225', 'AU200': 'AU200', 'SG25': 'SG25',
        # Metales
        'GOLD': 'GOLD', 'SILVER': 'SILVER', 'PLATINUM': 'PLATINUM', 'PALLADIUM': 'PALLADIUM',
        'COPPER': 'COPPER', 'ALUMINUM': 'ALUMINUM', 'MZN3': 'MZN3', 'NICKEL': 'NICKEL',
        # Energía
        'OIL_CRUDE': 'OIL_CRUDE', 'OIL_BRENT': 'OIL_BRENT', 'NATURALGAS': 'NATURALGAS', 'GASOLINE': 'GASOLINE',
        # Agricultura
        'WHEAT': 'WHEAT', 'CORN': 'CORN', 'SOYBEAN': 'SOYBEAN', 'SB': 'SB', 'USCOTTON': 'USCOTTON', 'LRC': 'LRC',
        # Cripto (si aparecieran)
        'BTCUSD': 'BTCUSD', 'ETHUSD': 'ETHUSD', 'XRPUSD': 'XRPUSD', 'ADAUSD': 'ADAUSD', 'SOLUSD': 'SOLUSD',
        'BNBUSD': 'BNBUSD', 'DOTUSD': 'DOTUSD', 'AVAXUSD': 'AVAXUSD', 'MATICUSD': 'MATICUSD', 'LINKUSD': 'LINKUSD',
        'UNIUSD': 'UNIUSD', 'LTCUSD': 'LTCUSD', 'ATOMUSD': 'ATOMUSD', 'ALGOUSD': 'ALGOUSD', 'VETUSD': 'VETUSD',
        'FILUSD': 'FILUSD', 'SANDUSD': 'SANDUSD', 'MANAUSD': 'MANAUSD',
    }
    if key in map_special:
        return map_special[key]
    m = re.match(r'^([A-Z]{2,4})/([A-Z]{2,4})$', key)
    if m:
        return m.group(1) + m.group(2)
    return key


def extract_stats(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Extract stats from a report entry. Falls back to computing from closed trades."""
    stats = entry.get('stats', {}) or {}
    total_rpl = stats.get('total_rpl')
    avg_rpl = stats.get('avg_rpl')
    wins = stats.get('wins')
    losses = stats.get('losses')
    closes = stats.get('closes')

    if total_rpl is None or avg_rpl is None or wins is None or losses is None or closes is None:
        closed = entry.get('closed', []) or []
        # Compute fallback metrics
        total_rpl = sum(t.get('rpl', 0.0) for t in closed)
        closes = len(closed)
        wins = sum(1 for t in closed if t.get('rpl', 0.0) > 0)
        losses = sum(1 for t in closed if t.get('rpl', 0.0) < 0)
        avg_rpl = (total_rpl / closes) if closes else 0.0

    return {
        'total_rpl': float(total_rpl) if total_rpl is not None else 0.0,
        'avg_rpl': float(avg_rpl) if avg_rpl is not None else 0.0,
        'wins': int(wins) if wins is not None else 0,
        'losses': int(losses) if losses is not None else 0,
        'closes': int(closes) if closes is not None else 0,
        'winrate': (int(wins) / max(1, int(wins) + int(losses))) if (wins is not None and losses is not None) else 0.0,
    }


def classify_symbol(s: Dict[str, Any], thresholds: Dict[str, float]) -> str:
    """Return recommendation: 'mantener' | 'piloto' | 'pausar'."""
    closes = s['closes']
    if closes < thresholds['min_closes']:
        return 'piloto'
    if s['avg_rpl'] <= thresholds['avg_rpl_exclude'] or s['total_rpl'] <= thresholds['total_rpl_exclude']:
        return 'pausar'
    # keep band
    if (thresholds['avg_rpl_keep_min'] <= s['avg_rpl'] <= thresholds['avg_rpl_keep_max'] and
            s['total_rpl'] >= thresholds['total_rpl_keep_min'] and
            s['winrate'] >= thresholds['winrate_keep_min']):
        return 'mantener'
    return 'piloto'


def process_report(path: str, thresholds: Dict[str, float]) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results: Dict[str, Dict[str, Any]] = {}
    recommendations: Dict[str, str] = {}

    for k, v in data.items():
        # Skip non-symbol sections
        if k.lower() in ('meta', 'summary', 'funds', 'diagnostics'):
            continue
        code = to_code(k)
        stats = extract_stats(v)
        results[code] = stats
        recommendations[code] = classify_symbol(stats, thresholds)

    return results, recommendations


def print_summary(report_path: str, results: Dict[str, Dict[str, Any]], recs: Dict[str, str]) -> None:
    print(f"Reporte: {report_path}")
    # Group by recommendation
    grupos = {'mantener': [], 'piloto': [], 'pausar': []}
    for code, rec in recs.items():
        grupos.setdefault(rec, []).append(code)

    for nombre in ('mantener', 'piloto', 'pausar'):
        sims = sorted(grupos.get(nombre, []))
        print(f"\nRecomendación: {nombre} ({len(sims)})")
        print(', '.join(sims) if sims else '-')

    # Top losers/winners for context
    tuples = [(c, r['total_rpl']) for c, r in results.items()]
    losers = sorted(tuples, key=lambda x: x[1])[:10]
    winners = sorted(tuples, key=lambda x: x[1], reverse=True)[:10]
    print("\nTop 10 por pérdidas (total_rpl ascendente):")
    for c, t in losers:
        print(f" - {c}: {t:.2f}")
    print("\nTop 10 por ganancias (total_rpl descendente):")
    for c, t in winners:
        print(f" - {c}: {t:.2f}")


def main():
    parser = argparse.ArgumentParser(description='Revisión de reportes y clasificación por símbolo')
    parser.add_argument('--input', '-i', default='scripts/outputs/live_reports_summary_20251113_2.json',
                        help='Ruta a archivo JSON de reporte o directorio con JSONs')
    parser.add_argument('--min_closes', type=int, default=10, help='Mínimo de cierres para decisión definitiva')
    parser.add_argument('--avg_rpl_exclude', type=float, default=-3.0, help='Umbral de avg_rpl para pausar')
    parser.add_argument('--total_rpl_exclude', type=float, default=-30.0, help='Umbral de total_rpl para pausar')
    parser.add_argument('--avg_rpl_keep_min', type=float, default=-0.5, help='Banda mínima de avg_rpl para mantener')
    parser.add_argument('--avg_rpl_keep_max', type=float, default=2.5, help='Banda máxima de avg_rpl para mantener')
    parser.add_argument('--total_rpl_keep_min', type=float, default=-15.0, help='Mínimo total_rpl para mantener')
    parser.add_argument('--winrate_keep_min', type=float, default=0.45, help='Winrate mínimo para mantener')
    args = parser.parse_args()

    thresholds = {
        'min_closes': args.min_closes,
        'avg_rpl_exclude': args.avg_rpl_exclude,
        'total_rpl_exclude': args.total_rpl_exclude,
        'avg_rpl_keep_min': args.avg_rpl_keep_min,
        'avg_rpl_keep_max': args.avg_rpl_keep_max,
        'total_rpl_keep_min': args.total_rpl_keep_min,
        'winrate_keep_min': args.winrate_keep_min,
    }

    input_path = args.input
    report_paths: List[str] = []
    if os.path.isdir(input_path):
        report_paths = [os.path.join(input_path, f) for f in os.listdir(input_path) if f.endswith('.json')]
    else:
        report_paths = [input_path]

    for rp in sorted(report_paths):
        try:
            results, recs = process_report(rp, thresholds)
            print_summary(rp, results, recs)
            print('\n' + '=' * 80 + '\n')
        except Exception as e:
            print(f"Error procesando {rp}: {e}")


if __name__ == '__main__':
    main()