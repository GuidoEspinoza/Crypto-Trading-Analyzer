"""
🧪 Test NUEVO: estrategias individuales y consenso con logging detallado

Objetivo:
- Ejecutar las 3 estrategias individuales (TrendFollowing, Breakout, MeanReversion)
- Ejecutar la estrategia de consenso
- Registrar paso a paso y comparar métricas para GOLD en 15m/30m/1h

Salida:
- Consola con logs detallados
- JSON/CSV en scripts/outputs/
- CSV de alineación manual vs oficial
"""

import os
import sys
import json
import csv
import argparse
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

# Asegurar importaciones relativas al proyecto
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.capital_client import create_capital_client_from_env
from src.core.consensus_adapter import ConsensusAdapter
from src.core.professional_adapter import ProfessionalStrategyAdapter
from src.core.breakout_adapter import BreakoutAdapter
from src.core.mean_reversion_adapter import MeanReversionAdapter


DEFAULT_TOLERANCE_CONF = 5.0       # puntos porcentuales tolerados en confianza
DEFAULT_TOLERANCE_CONSENSUS = 2.0  # puntos porcentuales tolerados en % consenso


def setup_logger(out_dir: str) -> logging.Logger:
    os.makedirs(out_dir, exist_ok=True)
    logger = logging.getLogger("strategies_test")
    logger.setLevel(logging.DEBUG)

    # Formato
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    # Consola
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    # Archivo
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(out_dir, f"test_individual_vs_consensus_{ts}.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    logger.info(f"📄 Log archivo: {log_path}")
    return logger


class _BotStub:
    def __init__(self, capital_client):
        self.capital_client = capital_client


def _dump_signal_dict(s: Any, strategy_name: str, tf: str) -> Dict[str, Any]:
    try:
        ts = getattr(s, "timestamp", None)
        ts_str = ts.isoformat() if ts else datetime.now(timezone.utc).isoformat()
    except Exception:
        ts_str = datetime.now(timezone.utc).isoformat()
    # Normalizar confianza a escala 0–100
    raw_conf = float(getattr(s, "confidence_score", 0.0))
    conf_pct = raw_conf * 100.0 if 0.0 <= raw_conf <= 2.0 else raw_conf
    return {
        "timeframe": tf,
        "strategy": strategy_name,
        "signal": getattr(s, "signal_type", "HOLD"),
        "confidence": float(conf_pct),
        "strength": getattr(s, "strength", "Weak"),
        "price": float(getattr(s, "price", 0.0)),
        "rr": float(getattr(s, "risk_reward_ratio", 0.0)) if hasattr(s, "risk_reward_ratio") else 0.0,
        "timestamp": ts_str,
        "notes": getattr(s, "notes", ""),
    }


def _compute_manual_consensus(
    rows: List[Dict[str, Any]],
    weights: Dict[str, float],
    contributor_names: List[str] | None = None,
) -> Dict[str, Any]:
    """Calcular consenso manual usando exactamente los contribuyentes oficiales.

    - Filtra por nombres en contributor_names si se proporcionan.
    - Usa los mismos pesos por estrategia que el consenso oficial.
    - Incluye señales HOLD en la distribución y en el denominador, igual que el consenso.
    """
    # Filtrar filas de estrategias individuales y, si aplica, por contribuyentes
    indiv_all = [r for r in rows if r.get("strategy") != "ConsensusStrategy"]
    indiv = (
        [r for r in indiv_all if r.get("strategy") in set(contributor_names or [])]
        if contributor_names
        else indiv_all
    )

    dist: Dict[str, int] = {}
    total_weight = 0.0
    weighted_conf = 0.0
    total = len(indiv)

    for r in indiv:
        sig = r.get("signal", "HOLD")
        conf = float(r.get("confidence", 0.0))
        if conf <= 1.0:  # normalizar si viene 0..1
            conf *= 100.0
        w = float(weights.get(r.get("strategy", ""), 0.0))
        # Distribución incluye HOLD, como en el consenso oficial
        dist[sig] = dist.get(sig, 0) + 1
        # Confianza ponderada se calcula sobre todas las señales incluidas
        weighted_conf += conf * w
        total_weight += w

    dominant = max(dist.keys(), key=lambda k: dist[k]) if dist else "HOLD"
    agreeing = dist.get(dominant, 0)
    consensus_pct = (agreeing / total) * 100.0 if total > 0 else 0.0
    weighted_conf = (weighted_conf / total_weight) if total_weight > 0 else 0.0

    return {
        "dominant_signal": dominant,
        "consensus_percentage": consensus_pct,
        "weighted_confidence": weighted_conf,
        "distribution": dist,
        "total": total,
        "agreeing": agreeing,
    }


def run_test(symbol: str, timeframes: List[str], points: int, logger: logging.Logger) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "symbol": symbol,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "results": {},
        "consensus": {},
        "alignment": {},
        "weights": {},
    }

    # Crear capital client y sesión
    client = create_capital_client_from_env()
    try:
        logger.info("🔑 Creando sesión con Capital.com…")
        client.create_session()
        logger.info("✅ Sesión creada correctamente")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo crear sesión: {e}. Continuamos en modo limitado.")

    # Adapters
    consensus = ConsensusAdapter(client)
    trend = ProfessionalStrategyAdapter(client)
    breakout = BreakoutAdapter(client)
    meanrev = MeanReversionAdapter(client)
    bot_stub = _BotStub(client)
    for adapter in [trend, breakout, meanrev]:
        if hasattr(adapter, "set_trading_bot"):
            adapter.set_trading_bot(bot_stub)

    # Pesos actuales del consenso
    try:
        weights = consensus.get_strategy_weights()
        logger.info(f"⚖️ Pesos del consenso: {weights}")
    except Exception:
        weights = {
            "TrendFollowingProfessional": 0.40,
            "BreakoutProfessional": 0.35,
            "MeanReversionProfessional": 0.25,
        }
        logger.info(f"⚖️ Pesos por defecto (fallback): {weights}")
    payload["weights"] = weights

    # Iterar por timeframes
    for tf in timeframes:
        logger.info("=" * 80)
        logger.info(f"🧪 Timeframe {tf} — símbolo {symbol}")
        tf_rows: List[Dict[str, Any]] = []

        # 1) Ejecutar estrategias individuales
        for name, adapter in [
            ("TrendFollowingProfessional", trend),
            ("BreakoutProfessional", breakout),
            ("MeanReversionProfessional", meanrev),
        ]:
            try:
                logger.debug(f"▶️ Ejecutando {name} ({tf})…")
                s = adapter.analyze(symbol, tf)
                if s:
                    row = _dump_signal_dict(s, name, tf)
                    tf_rows.append(row)
                    logger.info(
                        f"✅ {name} {tf}: {row['signal']} | conf={row['confidence']:.1f}% | fuerza={row['strength']} | rr={row['rr']:.2f}"
                    )
                else:
                    logger.info(f"⚪ {name} {tf}: sin señal válida")
            except Exception as e:
                logger.error(f"❌ Error en {name} {tf}: {e}")

        # 2) Ejecutar consenso
        consensus_row: Dict[str, Any] = {}
        consensus_obj = None
        try:
            logger.debug(f"▶️ Ejecutando ConsensusStrategy ({tf})…")
            s = consensus.analyze(symbol, tf)
            if s:
                consensus_obj = s
                consensus_row = _dump_signal_dict(s, "ConsensusStrategy", tf)
                # extendido con campos de consenso
                consensus_row.update({
                    "consensus_decision": getattr(s, "consensus_decision", "N/A"),
                    "consensus_percentage": getattr(s, "consensus_percentage", 0.0),
                    "coherence": getattr(s, "coherence_score", 0.0),
                    "quality": getattr(s, "quality_score", 0.0),
                    "contributors": len(getattr(s, "contributing_strategies", []) ),
                })
                tf_rows.append(consensus_row)
                logger.info(
                    "✅ Consensus {tf}: {sig} | dec={dec} | pct={pct:.1f}% | conf={conf:.1f}% | coher={coh:.1f}% | contrib={contrib}".format(
                        tf=tf,
                        sig=consensus_row["signal"],
                        dec=consensus_row["consensus_decision"],
                        pct=consensus_row["consensus_percentage"],
                        conf=consensus_row["confidence"],
                        coh=consensus_row["coherence"],
                        contrib=consensus_row["contributors"],
                    )
                )
            else:
                logger.info(f"⚪ Consensus {tf}: sin señal válida")
        except Exception as e:
            logger.error(f"❌ Error en ConsensusStrategy {tf}: {e}")

        # 3) Consenso manual y comparación — restringido a contribuyentes del consenso
        contributor_names: List[str] = []
        weights_contrib: Dict[str, float] = {}
        try:
            contrib = getattr(s, "contributing_strategies", []) if consensus_obj else []
            contributor_names = [d.get("name") for d in contrib if isinstance(d, dict) and d.get("name")]
            # Usar pesos exactos por contribuyente si están disponibles; si no, fallback a 'weights'
            for d in contrib:
                if isinstance(d, dict) and d.get("name") is not None:
                    weights_contrib[d["name"]] = float(d.get("weight", weights.get(d["name"], 0.0)))
        except Exception:
            contributor_names = []
            weights_contrib = {}

        effective_weights = weights_contrib if weights_contrib else weights
        manual = _compute_manual_consensus(tf_rows, effective_weights, contributor_names if contributor_names else None)
        # Métricas oficiales disponibles desde el TradingSignal del adapter
        official = {
            "dominant_signal": consensus_row.get("signal", "HOLD"),
            "consensus_percentage": float(consensus_row.get("consensus_percentage", 0.0)),
            "weighted_confidence": float(consensus_row.get("confidence", 0.0)),
        }
        pct_diff = abs(manual["consensus_percentage"] - official["consensus_percentage"])
        # Calcular confianza ajustada manual (mismo esquema del adapter)
        quality = float(consensus_row.get("quality", 0.0))
        coherence = float(consensus_row.get("coherence", 0.0))
        manual_adjusted_conf = manual["weighted_confidence"] * 0.6 + quality * 0.25 + coherence * 0.15
        manual_adjusted_conf = max(0.0, min(100.0, manual_adjusted_conf))
        conf_diff = abs(manual_adjusted_conf - official["weighted_confidence"])
        dom_match = manual["dominant_signal"] == official["dominant_signal"]
        aligned = dom_match and pct_diff <= DEFAULT_TOLERANCE_CONSENSUS and conf_diff <= DEFAULT_TOLERANCE_CONF

        logger.info(
            (
                "📊 Alineación {tf}: {status} | dom={dom} | pct(man={mpct:.2f},off={opct:.2f}) Δ={pd:.2f} | conf(man={mconf:.2f},off={oconf:.2f}) Δ={cd:.2f}"
            ).format(
                tf=tf,
                status="ALIGNED" if aligned else "NOT ALIGNED",
                dom=dom_match,
                mpct=manual["consensus_percentage"],
                opct=official["consensus_percentage"],
                pd=pct_diff,
                mconf=manual_adjusted_conf,
                oconf=official["weighted_confidence"],
                cd=conf_diff,
            )
        )

        # Guardar en payload
        payload["results"][tf] = tf_rows
        payload["consensus"][tf] = consensus_row
        payload["alignment"][tf] = {
            "manual": manual,
            "official": official,
            "differences": {
                "consensus_pct_diff": round(pct_diff, 2),
                "weighted_conf_diff": round(conf_diff, 2),
            },
            "dominant_match": dom_match,
            "aligned": aligned,
        }

    return payload


def save_outputs(symbol: str, payload: Dict[str, Any], out_dir: str, logger: logging.Logger):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    os.makedirs(out_dir, exist_ok=True)

    # JSON completo
    json_path = os.path.join(out_dir, f"test_individual_vs_consensus_{symbol}_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # CSV de señales
    csv_path = os.path.join(out_dir, f"test_individual_vs_consensus_{symbol}_{ts}.csv")
    rows: List[Dict[str, Any]] = []
    for tf, tf_rows in payload["results"].items():
        rows.extend(tf_rows)
    fieldnames = [
        "timeframe",
        "strategy",
        "signal",
        "confidence",
        "strength",
        "price",
        "rr",
        "timestamp",
        "notes",
        "consensus_decision",
        "consensus_percentage",
        "coherence",
        "quality",
        "contributors",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    # CSV de alineación
    align_path = os.path.join(out_dir, f"test_alignment_{symbol}_{ts}.csv")
    align_rows: List[Dict[str, Any]] = []
    for tf, data in payload.get("alignment", {}).items():
        m = data.get("manual", {})
        o = data.get("official", {})
        d = data.get("differences", {})
        align_rows.append({
            "timeframe": tf,
            "dominant_manual": m.get("dominant_signal"),
            "dominant_official": o.get("dominant_signal"),
            "consensus_manual_pct": round(float(m.get("consensus_percentage", 0.0)), 2),
            "consensus_official_pct": round(float(o.get("consensus_percentage", 0.0)), 2),
            "weighted_conf_manual": round(float(m.get("weighted_confidence", 0.0)), 2),
            "weighted_conf_official": round(float(o.get("weighted_confidence", 0.0)), 2),
            "consensus_pct_diff": d.get("consensus_pct_diff"),
            "weighted_conf_diff": d.get("weighted_conf_diff"),
            "aligned": data.get("aligned"),
        })
    with open(align_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "timeframe",
                "dominant_manual",
                "dominant_official",
                "consensus_manual_pct",
                "consensus_official_pct",
                "weighted_conf_manual",
                "weighted_conf_official",
                "consensus_pct_diff",
                "weighted_conf_diff",
                "aligned",
            ],
        )
        writer.writeheader()
        writer.writerows(align_rows)

    logger.info("💾 Salidas guardadas:")
    logger.info(f"- JSON: {json_path}")
    logger.info(f"- CSV señales: {csv_path}")
    logger.info(f"- CSV alineación: {align_path}")


def main():
    parser = argparse.ArgumentParser(description="Test nuevo: estrategias individuales y consenso con logs detallados")
    parser.add_argument("--symbol", default="GOLD", help="Símbolo (ej: GOLD)")
    parser.add_argument("--timeframes", default="15m,30m,1h", help="Lista separada por comas (ej: 15m,30m,1h)")
    parser.add_argument("--points", type=int, default=350, help="Puntos históricos (si aplica)")
    args = parser.parse_args()

    out_dir = os.path.join("scripts", "outputs")
    logger = setup_logger(out_dir)
    tfs = [t.strip() for t in args.timeframes.split(",") if t.strip()]
    logger.info("🚀 Iniciando test NUEVO de estrategias individuales y consenso")
    logger.info(f"Símbolo: {args.symbol.upper()} | Timeframes: {tfs} | points={args.points}")

    payload = run_test(args.symbol.upper(), tfs, args.points, logger)
    save_outputs(args.symbol.upper(), payload, out_dir, logger)


if __name__ == "__main__":
    main()