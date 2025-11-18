import argparse
import pandas as pd
from pathlib import Path


def load_trades(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Normalize columns
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])  # naive UTC
    # Fill missing numeric columns
    for col in ["Rpl Converted", "Swap Converted", "Fee"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    return df


def filter_closed_user_trades(df: pd.DataFrame) -> pd.DataFrame:
    # Keep only CLOSED executions (exclude SYSTEM SWAP rows)
    mask_closed = df.get("Status", pd.Series(index=df.index)).eq("CLOSED")
    mask_not_system = ~df.get("Source", pd.Series(index=df.index)).eq("SYSTEM")
    filtered = df[mask_closed & mask_not_system].copy()
    return filtered


def exclude_last_fr40_loss(df_closed: pd.DataFrame) -> pd.DataFrame:
    fr40 = df_closed[df_closed["Instrument Symbol"] == "FR40"].copy()
    # Identify last negative realized PnL
    fr40_losses = fr40[fr40["Rpl Converted"] < 0].sort_values("Timestamp")
    if fr40_losses.empty:
        return df_closed
    row_to_exclude = fr40_losses.iloc[-1]
    # Exclude by exact Trade Id + Exec Id when available, else by Timestamp
    trade_id = row_to_exclude.get("Trade Id")
    exec_id = row_to_exclude.get("Exec Id")
    if pd.notna(trade_id):
        df_closed = df_closed[df_closed["Trade Id"] != trade_id]
    elif pd.notna(exec_id):
        df_closed = df_closed[df_closed["Exec Id"] != exec_id]
    else:
        ts = row_to_exclude["Timestamp"]
        df_closed = df_closed[df_closed["Timestamp"] != ts]
    return df_closed


def compute_trade_metrics(df_closed: pd.DataFrame) -> dict:
    # Net PnL per trade: realized + swap - fee
    net = df_closed["Rpl Converted"].fillna(0)
    if "Swap Converted" in df_closed.columns:
        net = net + df_closed["Swap Converted"].fillna(0)
    if "Fee" in df_closed.columns:
        net = net - df_closed["Fee"].fillna(0)

    wins = net[net > 0]
    losses = net[net < 0]
    metrics = {
        "trades_count": int(len(net)),
        "wins": int((net > 0).sum()),
        "losses": int((net < 0).sum()),
        "win_rate": float((net > 0).mean()) if len(net) else 0.0,
        "net_pnl": float(net.sum()),
        "avg_win": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss": float(losses.mean()) if len(losses) else 0.0,
        "profit_factor": float(wins.sum() / abs(losses.sum())) if len(losses) and losses.sum() != 0 else float("inf"),
    }

    # By symbol breakdown
    df_closed = df_closed.copy()
    df_closed["net"] = net
    by_symbol = (
        df_closed.groupby("Instrument Symbol")["net"].agg(["count", "sum"]).sort_values("sum", ascending=False)
    )
    metrics["by_symbol"] = by_symbol

    # By day
    df_closed["date"] = df_closed["Timestamp"].dt.date
    by_day = df_closed.groupby("date")["net"].sum()
    metrics["by_day"] = by_day

    # Hour-of-day distribution (UTC)
    df_closed["hour"] = df_closed["Timestamp"].dt.hour
    by_hour = df_closed.groupby("hour")["net"].sum()
    metrics["by_hour"] = by_hour

    return metrics


def load_funds(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "Modified" in df.columns:
        df["Modified"] = pd.to_datetime(df["Modified"])  # naive UTC
    # numeric
    for col in ["Balance", "Amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def compute_equity_curves(df_funds: pd.DataFrame, df_trades_closed: pd.DataFrame) -> dict:
    """
    Use reported balances directly for the equity curve, and build an adjusted
    curve that adds back the last FR40 loss amount to all subsequent balances.
    """
    funds = df_funds.sort_values("Modified").copy()
    if funds.empty:
        return {
            "start_balance": 0.0,
            "end_balance_orig": 0.0,
            "end_balance_adj": 0.0,
            "equity_orig": [],
            "equity_adj": [],
        }

    # Identify last FR40 loss row in funds
    fr40_losses = funds[(funds["Instrument Symbol"].eq("FR40")) & (funds["Type"].eq("TRADE")) & (funds["Amount"] < 0)]
    fr40_last_loss = fr40_losses.sort_values("Modified").tail(1)
    adjust_ts = fr40_last_loss["Modified"].iloc[0] if not fr40_last_loss.empty else None
    adjust_amount = float(fr40_last_loss["Amount"].iloc[0]) if not fr40_last_loss.empty else 0.0

    # Build curves
    equity_orig = list(zip(funds["Modified"], funds["Balance"].astype(float)))
    if adjust_ts is None or adjust_amount == 0.0:
        equity_adj = equity_orig.copy()
    else:
        # Add back the negative amount to all balances at/after the loss timestamp
        equity_adj = []
        for ts, bal in equity_orig:
            if ts >= adjust_ts:
                equity_adj.append((ts, float(bal) - adjust_amount))
            else:
                equity_adj.append((ts, float(bal)))

    start_balance = float(funds.iloc[0]["Balance"]) if not funds.empty else 0.0
    end_balance_orig = float(funds.iloc[-1]["Balance"]) if not funds.empty else 0.0
    end_balance_adj = float(equity_adj[-1][1]) if equity_adj else 0.0

    return {
        "start_balance": start_balance,
        "end_balance_orig": end_balance_orig,
        "end_balance_adj": end_balance_adj,
        "equity_orig": equity_orig,
        "equity_adj": equity_adj,
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze performance over period, excluding last FR40 loss")
    parser.add_argument("trades_csv", type=Path)
    parser.add_argument("funds_csv", type=Path)
    args = parser.parse_args()

    trades_df = load_trades(args.trades_csv)
    closed_df = filter_closed_user_trades(trades_df)
    closed_excluded_df = exclude_last_fr40_loss(closed_df)

    # Metrics
    metrics = compute_trade_metrics(closed_excluded_df)

    # Funds / equity curve
    funds_df = load_funds(args.funds_csv)
    equity = compute_equity_curves(funds_df, closed_excluded_df)

    # Output summary
    print("=== Performance Summary (FR40 last loss excluded) ===")
    print(f"Trades: {metrics['trades_count']} | Win rate: {metrics['win_rate']*100:.1f}%")
    print(f"Net PnL: {metrics['net_pnl']:.2f} (Avg win: {metrics['avg_win']:.2f} | Avg loss: {metrics['avg_loss']:.2f})")
    print(f"Profit factor: {metrics['profit_factor']:.2f}")
    print("")
    print("Top symbols by PnL:")
    print(metrics["by_symbol"].head(10).to_string())
    print("")
    print("PnL by day:")
    print(metrics["by_day"].to_string())
    print("")
    print("PnL by hour (UTC):")
    print(metrics["by_hour"].to_string())
    print("")
    print("Equity:")
    print(f"Start balance: {equity['start_balance']:.2f}")
    print(f"End (original): {equity['end_balance_orig']:.2f}")
    print(f"End (adjusted): {equity['end_balance_adj']:.2f}")


if __name__ == "__main__":
    main()