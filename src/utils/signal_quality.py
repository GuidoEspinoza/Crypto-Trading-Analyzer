import warnings
from typing import Dict, Any
from datetime import datetime

try:
    import pandas as pd
    from ta.trend import EMAIndicator, ADXIndicator
    from ta.volatility import AverageTrueRange
except Exception:
    pd = None
    EMAIndicator = None
    ADXIndicator = None
    AverageTrueRange = None


def summarize_quality(df: Any, use_last_closed: bool = True) -> Dict[str, Any]:
    """Resumen compacto de calidad de señal a partir de OHLC.

    Calcula:
    - adx: fuerza de tendencia (fallback neutral 18)
    - atr_pct: ATR como % del precio
    - ema_alignment: 1 si EMA rápida > lenta, -1 si inversa, 0 si indeterminado
    - chop_score: menor es más "chop"; combina adx bajo y pendiente EMA baja
    """
    if df is None or (pd is not None and df.empty):
        return {
            "adx": 18.0,
            "atr_pct": 0.15,
            "ema_alignment": 0,
            "chop_score": 0.7,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Datos insuficientes"
        }

    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    # Usar última vela cerrada si hay al menos 2 velas
    idx = -2 if use_last_closed and len(close) > 1 else -1
    current_price = float(close.iloc[idx])

    # ADX
    adx = 18.0
    try:
        if ADXIndicator:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                adx_series = ADXIndicator(high=high, low=low, close=close, window=14).adx()
                val = adx_series.iloc[idx]
                adx = float(val) if not pd.isna(val) else 18.0
    except Exception:
        adx = 18.0

    # ATR%
    atr_pct = 0.15
    try:
        if AverageTrueRange:
            atr = AverageTrueRange(high=high, low=low, close=close, window=14).average_true_range()
            cur_atr = float(atr.iloc[idx])
            atr_pct = (cur_atr / current_price) * 100 if current_price > 0 else 0.0
    except Exception:
        pass

    # EMA alineación
    ema_alignment = 0
    try:
        if EMAIndicator:
            ema_fast = EMAIndicator(close=close, window=20).ema_indicator()
            ema_slow = EMAIndicator(close=close, window=50).ema_indicator()
            f = float(ema_fast.iloc[idx])
            s = float(ema_slow.iloc[idx])
            ema_alignment = 1 if f > s else (-1 if f < s else 0)
    except Exception:
        pass

    # Chop score (0–1): 1 limpio, 0 muy chop
    # penaliza adx < 20 y pendiente baja
    try:
        slope_ratio = 0.0004
        ema = None
        if EMAIndicator:
            ema = EMAIndicator(close=close, window=20).ema_indicator()
        if ema is not None:
            step = 5 if len(ema) > 5 else max(1, len(ema) // 4)
            # calcular pendiente hasta la vela seleccionada
            prev_idx = idx - step if (idx - step) >= -len(ema) else -len(ema)
            slope = abs(float(ema.iloc[idx] - ema.iloc[prev_idx])) / float(abs(idx - prev_idx))
            slope_ratio = slope / current_price if current_price > 0 else 0.0
        chop_penalty = 0.5 * (1.0 if adx < 20 else 0.0) + 0.5 * (1.0 if abs(slope_ratio) < 0.0003 else 0.0)
        chop_score = max(0.0, 1.0 - chop_penalty)
    except Exception:
        chop_score = 0.7

    return {
        "adx": round(adx, 2),
        "atr_pct": round(atr_pct, 2),
        "ema_alignment": int(ema_alignment),
        "chop_score": round(chop_score, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }
