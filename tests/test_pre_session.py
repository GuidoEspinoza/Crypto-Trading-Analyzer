from datetime import datetime, timedelta
from types import SimpleNamespace

import sys, os
sys.path.append(os.path.abspath("."))

from src.core.trading_bot import TradingBot
from src.core.enhanced_strategies import TradingSignal
from src.config.time_trading_config import UTC_TZ, get_session_budget


def make_signal(symbol: str, conf: float = 90.0) -> TradingSignal:
    return TradingSignal(
        symbol=symbol,
        signal_type="BUY",
        price=100.0,
        confidence_score=conf,
        strength="STRONG",
        strategy_name="UnitTest",
        timestamp=datetime.now(UTC_TZ),
        indicators_data={},
        notes="",
    )


def dummy_assess_trade_risk(signal, portfolio_value):
    # Minimal fake assessment object compatible with TradingBot logging
    risk_level = SimpleNamespace(value="LOW")
    position_sizing = SimpleNamespace(recommended_size=1.0)
    return SimpleNamespace(
        overall_risk_score=10.0,
        risk_level=risk_level,
        position_sizing=position_sizing,
        is_approved=True,
    )


def dummy_execute_signal(signal):
    # Minimal fake trade result
    return SimpleNamespace(success=True, message=f"Executed {signal.symbol}")


def run():
    print("=== Pre-session routine and session budgets test ===")
    bot = TradingBot(analysis_interval_minutes=1)

    # Monkey-patch risk manager and paper trader for deterministic behavior
    bot.risk_manager.assess_trade_risk = dummy_assess_trade_risk
    bot.paper_trader.execute_signal = dummy_execute_signal
    # Desactivar trading real y eventos para evitar requerir atributos reales en mocks
    bot.enable_real_trading = False
    bot._execute_real_trade = lambda *args, **kwargs: None
    bot._emit_trade_event = lambda *args, **kwargs: None

    # Avoid cooldown interfering
    bot._check_trade_cooldown = lambda s: True

    # 1) Trigger pre-session for current detected session
    current_session = bot.current_session
    bot._run_pre_session_routine(current_session)
    assert bot.stats["session_trades"][current_session] == 0
    print("Pre-session routine applied; session_trades reset.")

    # 2) Early session limits: set window active and max positions to 4
    bot.session_open_until = datetime.now(UTC_TZ) + timedelta(minutes=5)
    # Simulate active positions count
    bot.position_monitor.position_manager.get_active_positions = lambda: [object(), object(), object(), object()]

    sig = make_signal("BTCUSD")
    bot._process_signals([sig])
    # Should be blocked by early-session max positions
    assert bot.stats["session_trades"][current_session] == 0
    print("Early-session max positions enforced (no trade executed).")

    # Reduce active positions to allow trades
    bot.position_monitor.position_manager.get_active_positions = lambda: [object(), object(), object()]

    # 3) Generate 12 signals across distinct symbols; session budget is base ± adjustment
    symbols = [
        "BTCUSD","ETHUSD","ADAUSD","XRPUSD","BNBUSD","SOLUSD",
        "DOTUSD","LTCUSD","AVAXUSD","MATICUSD","ATOMUSD","NEARUSD"
    ]
    signals = [make_signal(sym, conf=95.0) for sym in symbols]
    # Desactivar límites tempranos para el bloque de prueba
    bot.session_open_until = None
    bot.last_trade_global_time = None
    bot._process_signals(signals)

    # Verify session trades capped at base + adjustment
    session_count = bot.stats["session_trades"][current_session]
    session_base = int(get_session_budget(current_session).get("max_trades", 0))
    session_adj = int(bot.session_budget_adjustments.get(current_session, 0))
    expected_max = max(0, session_base + session_adj)
    print(f"Session trades executed: {session_count} (expected {expected_max})")
    assert session_count == expected_max, "Session budget should cap at configured max trades with adjustment"

    # 4) Global daily cap: set at cap and confirm block
    bot.stats["daily_trades"] = bot.daily_max_trades_cap
    bot._process_signals([make_signal("DOGEUSD")])
    assert bot.stats["daily_trades"] == bot.daily_max_trades_cap
    print("Global daily cap enforced (no additional trades).")


if __name__ == "__main__":
    run()