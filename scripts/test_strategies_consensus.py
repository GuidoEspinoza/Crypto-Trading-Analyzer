"""
🧪 Script de prueba: estrategias individuales y consenso

Ejecuta análisis para un símbolo y múltiples timeframes usando:
- TrendFollowingProfessional (via ProfessionalStrategyAdapter)
- BreakoutProfessional (via BreakoutAdapter)
- MeanReversionProfessional (via MeanReversionAdapter)
- ConsensusStrategy (via ConsensusAdapter)

Imprime una tabla comparativa y guarda resultados en CSV y JSON
para contrastar con los gráficos de precio (TradingView u otros).
"""

import os
import sys
import json
import csv
import time
import argparse
from datetime import datetime, timezone
from typing import List, Dict, Any

# Asegurar que la raíz del proyecto esté en sys.path cuando se ejecuta desde scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.capital_client import create_capital_client_from_env
from src.core.consensus_adapter import ConsensusAdapter
from src.core.professional_adapter import ProfessionalStrategyAdapter
from src.core.breakout_adapter import BreakoutAdapter
from src.core.mean_reversion_adapter import MeanReversionAdapter


class _BotStub:
    """Stub mínimo para proveer capital_client a los adapters.
    Evita instanciar el TradingBot completo.
    """

    def __init__(self, capital_client):
        self.capital_client = capital_client


def _print_row(row: Dict[str, Any]):
    cols = [
        row.get("timeframe", ""),
        row.get("strategy", ""),
        row.get("signal", ""),
        f"{row.get('confidence', 0):.1f}%",
        row.get("strength", ""),
        f"{row.get('price', 0):.2f}",
        f"RR {row.get('rr', 0):.2f}",
        row.get("extra", ""),
    ]
    print(" | ".join(cols))


# Reglas de votación y umbrales (valores por defecto, sobreescribibles por CLI)
DEFAULT_CONF_THRESHOLD = 0.70  # 70%
DEFAULT_STRENGTH_ALLOWED = {"Strong"}
DEFAULT_CONSENSUS_MIN_PERCENT = 0.70
DEFAULT_CONSENSUS_MIN_COHERENCE = 0.50


def _compute_recommendation(
    tf: str,
    tf_rows: List[Dict[str, Any]],
    consensus_row: Dict[str, Any] | None,
    conf_threshold: float,
    strength_allowed: set,
    consensus_min_percent: float,
    consensus_min_coherence: float,
):
    voters_buy = []
    voters_sell = []
    confidences_buy = []
    confidences_sell = []
    rr_buy = []
    rr_sell = []

    for r in tf_rows:
        strat = r.get("strategy", "")
        if strat == "ConsensusStrategy":
            continue
        signal = r.get("signal", "HOLD")
        conf = float(r.get("confidence", 0.0)) / 100.0 if r.get("confidence", 0.0) > 1.0 else float(r.get("confidence", 0.0))
        # normalizamos a 0..1 si vino como 75.0 en vez de 0.75
        if conf > 1.0:
            conf = conf / 100.0
        strength = r.get("strength", "Weak")
        if strength not in strength_allowed:
            continue
        if conf < conf_threshold:
            continue
        if signal == "BUY":
            voters_buy.append(strat)
            confidences_buy.append(conf)
            rr_buy.append(float(r.get("rr", 0.0)))
        elif signal == "SELL":
            voters_sell.append(strat)
            confidences_sell.append(conf)
            rr_sell.append(float(r.get("rr", 0.0)))

    recommendation = None
    # Regla 2/3: mayoría de 2 o más
    if len(voters_buy) >= 2 or len(voters_sell) >= 2:
        direction = "BUY" if len(voters_buy) >= 2 else "SELL"
        voters = voters_buy if direction == "BUY" else voters_sell
        confs = confidences_buy if direction == "BUY" else confidences_sell
        rrs = rr_buy if direction == "BUY" else rr_sell
        confidence_avg = sum(confs) / len(confs) if confs else 0.0
        rr_avg = sum(rrs) / len(rrs) if rrs else 0.0
        recommendation = {
            "timeframe": tf,
            "type": "hard",
            "strategy": "Recommendation(2/3)",
            "signal": direction,
            "confidence": round(confidence_avg * 100, 1),
            "strength": "Strong",
            "price": 0.0,
            "rr": round(rr_avg, 2),
            "extra": f"voters:{','.join(voters)}",
        }
    elif consensus_row is not None:
        # Si no hay mayoría dura, usar consenso como recomendación blanda si pasa umbrales
        cons_pct_str = consensus_row.get("extra", "")
        # intentamos leer directamente del objeto; como en results guardamos porcentaje en extra, itera la extracción
        cons_pct = 0.0
        try:
            # "Consensus SELL (75%)"
            import re
            m = re.search(r"\((\d+)\%\)", cons_pct_str)
            if m:
                cons_pct = float(m.group(1)) / 100.0
        except Exception:
            cons_pct = 0.0

        # En algunos casos podemos tener coherencia en el objeto original; aquí no está, así que asumimos si porcentaje es alto
        if cons_pct >= consensus_min_percent:
            recommendation = {
                "timeframe": tf,
                "type": "soft",
                "strategy": "Recommendation(Consensus)",
                "signal": consensus_row.get("signal", "HOLD"),
                "confidence": consensus_row.get("confidence", 0.0),
                "strength": "Moderate",
                "price": consensus_row.get("price", 0.0),
                "rr": consensus_row.get("rr", 0.0),
                "extra": cons_pct_str,
            }

    if recommendation is None:
        recommendation = {
            "timeframe": tf,
            "type": "none",
            "strategy": "Recommendation(2/3)",
            "signal": "HOLD",
            "confidence": 0.0,
            "strength": "Weak",
            "price": 0.0,
            "rr": 0.0,
            "extra": "Sin mayoría ni consenso fuerte",
        }
    return recommendation


def run_test(
    symbol: str,
    timeframes: List[str],
    points: int,
    conf_threshold: float,
    strength_allowed: set,
    consensus_min_percent: float,
    consensus_min_coherence: float,
) -> Dict[str, Any]:
    results: Dict[str, List[Dict[str, Any]]] = {tf: [] for tf in timeframes}
    recommendations: Dict[str, Dict[str, Any]] = {}

    # 1) Capital.com client y sesión
    client = create_capital_client_from_env()
    session_ok = False
    try:
        # Crear sesión (demo o live según env)
        client.create_session()
        session_ok = True
    except Exception as e:
        print(f"⚠️ No se pudo crear sesión en Capital.com: {e}")
        print("   Revisa variables de entorno (.env). Continuaré e intentaré recuperar datos.")

    # 2) Adapters y stub
    bot_stub = _BotStub(client)
    consensus = ConsensusAdapter(client)
    trend = ProfessionalStrategyAdapter(client)
    breakout = BreakoutAdapter(client)
    meanrev = MeanReversionAdapter(client)

    # Asignar bot_stub para que get_market_data funcione en adapters
    for adapter in [trend, breakout, meanrev]:
        if hasattr(adapter, "set_trading_bot"):
            adapter.set_trading_bot(bot_stub)

    # 3) Ejecutar análisis por timeframe
    print("\n==============================================")
    print(f"🧪 Test estrategias y consenso para {symbol}")
    print("==============================================")
    print(
        f"Política: 2/3 con conf>={int(conf_threshold*100)}% y fuerza in {sorted(list(strength_allowed))}; "
        f"Consenso fuerte>={int(consensus_min_percent*100)}%"
    )
    print("\n")
    header = ["TF", "Estrategia", "Señal", "Conf", "Fuerza", "Precio", "R/R", "Extra"]
    print(" | ".join(header))
    print("-" * 100)

    for tf in timeframes:
        # Consensus primero (incluye detalles de contribuyentes)
        consensus_row = None
        try:
            s = consensus.analyze(symbol, tf)
            if s:
                extra = (
                    f"Consensus {getattr(s, 'consensus_decision', 'N/A')} "
                    f"({getattr(s, 'consensus_percentage', 0):.0f}%)"
                )
                consensus_row = {
                    "timeframe": tf,
                    "strategy": "ConsensusStrategy",
                    "signal": s.signal_type,
                    "confidence": s.confidence_score,
                    "strength": s.strength,
                    "price": getattr(s, "price", 0.0),
                    "rr": getattr(s, "risk_reward_ratio", 0.0),
                    "extra": extra,
                }
                results[tf].append(consensus_row)
                _print_row(consensus_row)
            else:
                consensus_row = {
                    "timeframe": tf,
                    "strategy": "ConsensusStrategy",
                    "signal": "HOLD",
                    "confidence": 0.0,
                    "strength": "Weak",
                    "price": 0.0,
                    "rr": 0.0,
                    "extra": "Sin consenso",
                }
                results[tf].append(consensus_row)
                _print_row(consensus_row)
        except Exception as e:
            print(f"❌ Error consenso {tf}: {e}")

        # Estrategias individuales
        for name, adapter in [
            ("TrendFollowingProfessional", trend),
            ("BreakoutProfessional", breakout),
            ("MeanReversionProfessional", meanrev),
        ]:
            try:
                s = adapter.analyze(symbol, tf)
                if s:
                    extra_parts = []
                    # Campos potenciales que suelen estar en EnhancedSignal
                    for k in ["market_regime", "trend_confirmation", "volume_confirmation"]:
                        v = getattr(s, k, None)
                        if v is not None and v != "":
                            extra_parts.append(f"{k}:{v}")
                    extra = ", ".join(extra_parts)

                    results[tf].append(
                        {
                            "timeframe": tf,
                            "strategy": name,
                            "signal": s.signal_type,
                            "confidence": s.confidence_score,
                            "strength": s.strength,
                            "price": getattr(s, "price", 0.0),
                            "rr": getattr(s, "risk_reward_ratio", 0.0),
                            "extra": extra,
                        }
                    )
                    _print_row(results[tf][-1])
                else:
                    results[tf].append(
                        {
                            "timeframe": tf,
                            "strategy": name,
                            "signal": "HOLD",
                            "confidence": 0.0,
                            "strength": "Weak",
                            "price": 0.0,
                            "rr": 0.0,
                            "extra": "Sin señal",
                        }
                    )
                    _print_row(results[tf][-1])
            except Exception as e:
                print(f"❌ Error {name} {tf}: {e}")

        # Recomendación por regla 2/3 (con fallback a consenso)
        rec = _compute_recommendation(
            tf,
            results[tf],
            consensus_row,
            conf_threshold,
            strength_allowed,
            consensus_min_percent,
            consensus_min_coherence,
        )
        recommendations[tf] = rec
        _print_row(rec)

        # Separador por timeframe
        print("-" * 100)

    return {
        "symbol": symbol,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "recommendations": recommendations,
        "policy": {
            "conf_threshold": conf_threshold,
            "strength_allowed": sorted(list(strength_allowed)),
            "consensus_min_percent": consensus_min_percent,
            "consensus_min_coherence": consensus_min_coherence,
        },
    }


def save_outputs(symbol: str, payload: Dict[str, Any]):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join("scripts", "outputs")
    os.makedirs(out_dir, exist_ok=True)

    # JSON
    json_path = os.path.join(out_dir, f"test_{symbol}_{ts}.json")
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)

    # CSV plano: filas por resultado
    csv_path = os.path.join(out_dir, f"test_{symbol}_{ts}.csv")
    rows = []
    for tf, tf_rows in payload["results"].items():
        rows.extend(tf_rows)
        # Añadir la recomendación al CSV como una fila más
        rec = payload.get("recommendations", {}).get(tf)
        if rec:
            rows.append(rec)
    fieldnames = ["timeframe", "strategy", "signal", "confidence", "strength", "price", "rr", "extra", "type"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n💾 Resultados guardados:\n- JSON: {json_path}\n- CSV:  {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Test de estrategias y consenso")
    parser.add_argument("--symbol", default="GOLD", help="Símbolo Capital.com (ej: GOLD)")
    parser.add_argument(
        "--timeframes",
        default="15m,30m,1h",
        help="Lista separada por comas (ej: 15m,30m,1h)",
    )
    parser.add_argument(
        "--points",
        type=int,
        default=350,
        help="Puntos históricos a usar si la estrategia lo requiere",
    )
    parser.add_argument(
        "--conf-threshold",
        type=float,
        default=DEFAULT_CONF_THRESHOLD,
        help="Umbral de confianza (0..1), por defecto 0.70",
    )
    parser.add_argument(
        "--strengths",
        default="Strong",
        help="Fuerzas permitidas separadas por comas (ej: Strong,Moderate). Por defecto Strong",
    )
    parser.add_argument(
        "--consensus-min-percent",
        type=float,
        default=DEFAULT_CONSENSUS_MIN_PERCENT,
        help="Porcentaje mínimo de consenso (0..1), por defecto 0.70",
    )
    parser.add_argument(
        "--consensus-min-coherence",
        type=float,
        default=DEFAULT_CONSENSUS_MIN_COHERENCE,
        help="Coherencia mínima de consenso (0..1), por defecto 0.50",
    )
    args = parser.parse_args()

    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    strengths_allowed = {s.strip() for s in args.strengths.split(",") if s.strip()}
    if not strengths_allowed:
        strengths_allowed = DEFAULT_STRENGTH_ALLOWED
    payload = run_test(
        args.symbol.upper(),
        tfs,
        args.points,
        args.conf_threshold,
        strengths_allowed,
        args.consensus_min_percent,
        args.consensus_min_coherence,
    )
    save_outputs(args.symbol.upper(), payload)


if __name__ == "__main__":
    main()
"""
Script de prueba: ejecuta el TradingBot para generar señales SIN ejecutar trades
y guarda las señales en un archivo JSON para su análisis posterior.

Uso:
  - python scripts/test_strategies_consensus.py
  - Opcional: establecer variables de entorno para credenciales si el bot
    requiere acceso a Capital.com. Si no hay conexión, el bot intentará
    continuar y registrará errores.
"""

import os
import json
from datetime import datetime
from typing import List, Dict

from src.core.trading_bot import TradingBot
from src.core.enhanced_strategies import TradingSignal


def signal_to_dict(sig: TradingSignal) -> Dict:
    """Convertir una señal a dict serializable para JSON."""
    try:
        ts = getattr(sig, "timestamp", None)
        timestamp_str = ts.isoformat() if ts else datetime.now().isoformat()
    except Exception:
        timestamp_str = datetime.now().isoformat()

    return {
        "symbol": sig.symbol,
        "signal_type": sig.signal_type,
        "price": float(sig.price) if hasattr(sig, "price") else None,
        "confidence_score": float(sig.confidence_score),
        "strength": getattr(sig, "strength", None),
        "strategy_name": getattr(sig, "strategy_name", None),
        "timestamp": timestamp_str,
        "notes": getattr(sig, "notes", ""),
        "indicators_data": getattr(sig, "indicators_data", {}) or {},
    }


def main():
    # Inicializar bot y desactivar ejecución de trades
    bot = TradingBot()
    bot.enable_trading = False

    # Ejecutar análisis secuencial (sin ejecución inmediata de trades)
    # Alternativa: usar bot._analyze_symbols_parallel()
    signals: List[TradingSignal] = bot._analyze_symbols_sequential()

    # Preparar salida
    outputs_dir = os.path.join("scripts", "outputs")
    os.makedirs(outputs_dir, exist_ok=True)
    ts_now = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"test_SIGNALS_{ts_now}"
    json_path = os.path.join(outputs_dir, base_name + ".json")

    # Serializar señales
    payload = {
        "generated_at": datetime.now().isoformat(),
        "count": len(signals),
        "signals": [signal_to_dict(s) for s in signals],
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # Resumen en consola
    by_type: Dict[str, int] = {}
    by_symbol: Dict[str, int] = {}
    for s in signals:
        by_type[s.signal_type] = by_type.get(s.signal_type, 0) + 1
        by_symbol[s.symbol] = by_symbol.get(s.symbol, 0) + 1

    print(f"✅ Señales generadas: {len(signals)}")
    print(f"📄 Archivo JSON: {json_path}")
    if by_type:
        print("📊 Distribución por tipo:")
        for t, c in by_type.items():
            print(f"  - {t}: {c}")
    if by_symbol:
        print("📈 Señales por símbolo (top 10):")
        for sym, c in list(sorted(by_symbol.items(), key=lambda x: x[1], reverse=True))[:10]:
            print(f"  - {sym}: {c}")


if __name__ == "__main__":
    main()