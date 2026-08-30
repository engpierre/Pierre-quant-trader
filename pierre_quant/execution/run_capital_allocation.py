"""
pierre_quant/execution/run_capital_allocation.py
Direct CLI entry point evaluating capital allocation across active long convictions.
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Environment setup
VENV_SITE_PACKAGES = Path(r"C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Lib\site-packages")
if VENV_SITE_PACKAGES.exists() and str(VENV_SITE_PACKAGES) not in sys.path:
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

PROJECT_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace\pierre-quant")
if PROJECT_ROOT.exists() and str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.orchestration.supervisor import SupervisorOrchestrator
from pierre_quant.execution.position_sizer import PositionSizer
from pierre_quant.execution.circuit_breaker import ExecutionCircuitBreaker

TARGET_LONG_CANDIDATES = ["PFE", "CELH", "TSCO"]
SIMULATION_MODE = True


def main():
    parser = argparse.ArgumentParser(description="Capital Allocation & Order Sizing Matrix")
    parser.add_argument("--cash", type=float, default=25000.0, help="Total available deployable cash ($)")
    parser.add_argument("--tickers", type=str, default="", help="Optional comma-separated list of target tickers")
    args = parser.parse_args()

    targets = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] if args.tickers else TARGET_LONG_CANDIDATES

    lines = [
        "# 💼 REAL-CAPITAL ALLOCATION & SIZING BRACKET",
        f"**Deployable Capital:** `${args.cash:,.2f}` | **Max Risk Per Trade:** `2.0%` | **Kelly Multiplier:** `0.35x` | **Mode:** `{'SIMULATION / PAPER' if SIMULATION_MODE else 'LIVE MICRO-LOT'}`\n",
        "| Ticker | Spot Price | Confluence | ATR Stop | Target Shares | Total Cost | Max Loss Risk | Verdict |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    total_deployed = 0.0
    total_risk = 0.0

    for ticker in targets:
        res = SupervisorOrchestrator.synthesize(ticker)
        bracket = PositionSizer.calculate_sizing(
            ticker=res.ticker,
            spot_price=res.spot_price,
            confluence_score=res.net_confluence_score,
            atr_stop_floor=res.risk_invalidation_floor,
            total_portfolio_cash=args.cash
        )
        total_deployed += bracket.dollar_allocation
        total_risk += bracket.max_capital_loss

        lines.append(
            f"| **${bracket.ticker}** | `${res.spot_price:.2f}` | `{res.net_confluence_score:+5.2f}%` | "
            f"`${bracket.risk_stop_floor:.2f}` | **{bracket.target_shares} shs** | "
            f"`${bracket.dollar_allocation:,.2f}` | `${bracket.max_capital_loss:,.2f}` | `{bracket.execution_verdict}` |"
        )

    cash_reserve = args.cash - total_deployed
    pct_deployed = (total_deployed / args.cash) * 100.0 if args.cash > 0 else 0.0
    pct_risk = (total_risk / args.cash) * 100.0 if args.cash > 0 else 0.0
    pct_reserve = (cash_reserve / args.cash) * 100.0 if args.cash > 0 else 0.0

    lines.extend([
        "\n---",
        "### 🛡️ Capital Preservation & Balance Summary",
        f"* **Total Capital Allocated:** `${total_deployed:,.2f}` ({pct_deployed:.1f}%)",
        f"* **Total Downside Book Risk:** `${total_risk:,.2f}` ({pct_risk:.2f}%)",
        f"* **Unallocated Cash Reserve:** `${cash_reserve:,.2f}` ({pct_reserve:.1f}%)\n"
    ])

    print("\n".join(lines))


if __name__ == "__main__":
    main()
