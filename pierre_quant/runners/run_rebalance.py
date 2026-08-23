"""
Deterministic Portfolio Rebalancing Engine (Agent 02 Risk Guard Binding)
========================================================================
Executes exact floating-point portfolio rebalancing math in Python rather
than relying on LLM token arithmetic, preventing truncation and hallucination.
"""

import sys
import os
import argparse
import json
from typing import Sequence, List, Dict, Any, Optional

# UTF-8 stdout protection for Windows CP1252 environments
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Ensure pierre-quant root and workspace are on sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_quant_root = os.path.abspath(os.path.join(_current_dir, "..", ".."))
_workspace_root = os.path.abspath(os.path.join(_quant_root, ".."))
for _p in [_quant_root, _workspace_root]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pierre_quant.core.contracts import (
    AllocationTarget,
    PortfolioRebalanceReport,
    QuantSystemError,
)
from pierre_quant.agents.live_api_ingestion import fetch_live_quote


def calculate_rebalance(
    holdings: Dict[str, int],
    target_weights: Dict[str, float],
    cash_balance: float = 0.0,
    price_overrides: Optional[Dict[str, float]] = None,
) -> PortfolioRebalanceReport:
    """Executes exact deterministic portfolio rebalance calculations."""
    price_overrides = price_overrides or {}
    all_tickers = sorted(list(set(list(holdings.keys()) + list(target_weights.keys()))))
    
    # 1. Fetch live prices for all assets
    prices: Dict[str, float] = {}
    for ticker in all_tickers:
        if ticker in price_overrides and price_overrides[ticker] > 0.0:
            prices[ticker] = float(price_overrides[ticker])
        else:
            try:
                quote = fetch_live_quote(ticker)
                prices[ticker] = quote.current_price
            except Exception as exc:
                raise QuantSystemError(f"Failed to fetch live price for {ticker}: {exc}") from exc

    # 2. Compute current asset values and total portfolio equity
    current_values: Dict[str, float] = {}
    for ticker in all_tickers:
        shares = holdings.get(ticker, 0)
        current_values[ticker] = round(shares * prices[ticker], 2)

    total_equity: float = round(sum(current_values.values()) + cash_balance, 2)
    if total_equity <= 0.0:
        raise QuantSystemError("Total portfolio value must be greater than zero.")

    # 3. Calculate target weights & delta shares
    total_target_weight = sum(target_weights.values())
    if abs(total_target_weight - 1.0) > 0.05 and total_target_weight > 0.0:
        # Normalize target weights to 1.0 if not already normalized
        target_weights = {k: v / total_target_weight for k, v in target_weights.items()}

    allocations: List[AllocationTarget] = []
    for ticker in all_tickers:
        price = prices[ticker]
        curr_shares = holdings.get(ticker, 0)
        curr_val = current_values[ticker]
        curr_wt = round(curr_val / total_equity, 4)
        tgt_wt = round(target_weights.get(ticker, 0.0), 4)
        tgt_val = round(total_equity * tgt_wt, 2)
        delta_val = round(tgt_val - curr_val, 2)

        # Exact integer share delta calculation
        delta_sh = int(round(delta_val / price)) if price > 0 else 0
        if delta_sh > 0:
            action = "BUY"
        elif delta_sh < 0:
            action = "SELL"
        else:
            action = "HOLD"

        allocations.append(
            AllocationTarget(
                ticker=ticker,
                current_price=price,
                current_shares=curr_shares,
                current_value=curr_val,
                current_weight=curr_wt,
                target_weight=tgt_wt,
                target_value=tgt_val,
                delta_value=delta_val,
                action=action,
                delta_shares=abs(delta_sh),
            )
        )

    # 4. Generate Condensed Markdown Table
    lines: List[str] = [
        "# ⚖️ PORTFOLIO REBALANCE DOSSIER",
        f"**Total Portfolio Value:** `${total_equity:,.2f}` | **Cash Available:** `${cash_balance:,.2f}`",
        "",
        "| Ticker | Spot Price | Current Qty | Current Value | Current Wt | Target Wt | Target Value | Action | Delta Shares |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for a in allocations:
        action_emoji = "🟢 BUY" if a.action == "BUY" else ("🔴 SELL" if a.action == "SELL" else "⚪ HOLD")
        sign = "+" if a.delta_value > 0 else ""
        lines.append(
            f"| **${a.ticker}** | `${a.current_price:.2f}` | {a.current_shares} | `${a.current_value:,.2f}` | "
            f"`{a.current_weight * 100:.1f}%` | `{a.target_weight * 100:.1f}%` | `${a.target_value:,.2f}` | "
            f"**{action_emoji}** | `{sign}{a.delta_shares}` (`{sign}${a.delta_value:,.2f}`) |"
        )

    condensed_md = "\n".join(lines)
    return PortfolioRebalanceReport(
        total_portfolio_value=total_equity,
        cash_balance=cash_balance,
        allocations=allocations,
        condensed_markdown=condensed_md,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic Portfolio Rebalancing Engine")
    parser.add_argument("--portfolio", "-p", type=str, default=None, help="JSON string or path specifying holdings and target weights")
    args = parser.parse_args()

    if args.portfolio:
        try:
            if os.path.exists(args.portfolio):
                with open(args.portfolio, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(args.portfolio)
        except Exception as exc:
            print(f"Error parsing portfolio JSON: {exc}")
            sys.exit(1)
    else:
        # Default sample portfolio for verification
        data = {
            "holdings": {"ENB": 200, "ONDS": 500, "IONQ": 100},
            "target_weights": {"ENB": 0.40, "ONDS": 0.30, "IONQ": 0.30},
            "cash_balance": 1500.0,
        }

    report = calculate_rebalance(
        holdings=data.get("holdings", {}),
        target_weights=data.get("target_weights", {}),
        cash_balance=float(data.get("cash_balance", 0.0)),
        price_overrides=data.get("price_overrides", {}),
    )
    print(report.condensed_markdown)


if __name__ == "__main__":
    main()
