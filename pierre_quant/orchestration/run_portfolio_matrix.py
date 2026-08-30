"""
pierre_quant/orchestration/run_portfolio_matrix.py
Evaluates the complete Pierre Quant multi-tier portfolio registry concurrently and streams the categorized Trajectory Matrix.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import sys
from pathlib import Path
from typing import Dict, List, Tuple

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

from pierre_quant.orchestration.supervisor import SupervisorOrchestrator, SupervisorSynthesisResult

# Multi-Tier Portfolio Registry (Exited assets purged: IRM, RTX, ABTC, NFLX, ORCL)
PORTFOLIO_TIERS: Dict[str, List[str]] = {
    "Core Portfolio": ["ENB", "META", "IONQ", "ACM"],
    "Swing / Trading": ["SMR", "ACON", "CELH", "EH", "JOBY", "NVO", "OKLO", "PFE", "SOFI", "TSCO", "KWEB", "ONDS"],
    "IRS Portfolio": ["POET", "RR", "XNDU"],
    "Active Watchlist": ["BABA", "BIDU", "BTC-USD"]
}


def analyze_ticker(ticker: str) -> SupervisorSynthesisResult:
    return SupervisorOrchestrator.synthesize(ticker.strip().upper().lstrip("$"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Full Portfolio Trajectory Matrix & Weekly Movers")
    parser.add_argument("--tier", type=str, default="ALL", choices=["ALL", "CORE", "SWING", "IRS", "WATCHLIST"], help="Portfolio tier filter")
    parser.add_argument("--tickers", type=str, default="", help="Optional explicit comma-separated ticker list")
    args = parser.parse_args()

    # Determine target assets
    if args.tickers:
        selected_universe = {"Custom Selection": [t.strip().upper().lstrip("$") for t in args.tickers.split(",") if t.strip()]}
    elif args.tier == "CORE":
        selected_universe = {"Core Portfolio": PORTFOLIO_TIERS["Core Portfolio"]}
    elif args.tier == "SWING":
        selected_universe = {"Swing / Trading": PORTFOLIO_TIERS["Swing / Trading"]}
    elif args.tier == "IRS":
        selected_universe = {"IRS Portfolio": PORTFOLIO_TIERS["IRS Portfolio"]}
    elif args.tier == "WATCHLIST":
        selected_universe = {"Active Watchlist": PORTFOLIO_TIERS["Active Watchlist"]}
    else:
        selected_universe = PORTFOLIO_TIERS

    flat_tickers = list(dict.fromkeys([sym for group in selected_universe.values() for sym in group]))

    # Parallel synthesis across all target assets
    results_map: Dict[str, SupervisorSynthesisResult] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(12, len(flat_tickers))) as executor:
        future_map = {executor.submit(analyze_ticker, sym): sym for sym in flat_tickers}
        for future in concurrent.futures.as_completed(future_map):
            sym = future_map[future]
            try:
                results_map[sym] = future.result()
            except Exception:
                pass

    # Render Categorized Markdown Report
    lines = [
        "# 📊 PORTFOLIO TRAJECTORY MATRIX & WEEKLY MOVERS REPORT",
        f"**Active Scope:** `{len(results_map)} Assets Synthesized` | **Architecture:** `16-Node Confluence Swarm`\n"
    ]

    long_convictions: List[Tuple[str, float, str, str]] = []
    short_convictions: List[Tuple[str, float, str, str]] = []
    neutral_watches: List[Tuple[str, float, str, str]] = []

    for tier_name, tickers in selected_universe.items():
        tier_results = [results_map[sym] for sym in tickers if sym in results_map]
        if not tier_results:
            continue

        # Sort tier by net confluence descending
        tier_results.sort(key=lambda x: x.net_confluence_score, reverse=True)

        lines.extend([
            f"## {tier_name}",
            "| Ticker | Spot Price | Consensus Bias | Net Confluence | Predictive Regime | ATR Stop Floor | Action Directive |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ])

        for r in tier_results:
            lines.append(
                f"| **${r.ticker}** | `${r.spot_price:.2f}` | `{r.consensus_bias.value}` | `{r.net_confluence_score:+5.2f}%` | `{r.predictive_regime}` | `${r.risk_invalidation_floor:.2f}` | `{r.action_directive}` |"
            )
            if r.net_confluence_score >= 25.0:
                long_convictions.append((r.ticker, r.net_confluence_score, tier_name, r.action_directive))
            elif r.net_confluence_score <= -25.0:
                short_convictions.append((r.ticker, r.net_confluence_score, tier_name, r.action_directive))
            else:
                neutral_watches.append((r.ticker, r.net_confluence_score, tier_name, r.action_directive))

        lines.append("")

    lines.extend([
        "---",
        "## 2. Weekly Alpha & Allocation Directives",
        "### 🟢 Weekly Long Convictions (Accumulate / Momentum Lead)"
    ])

    if long_convictions:
        for sym, conf, tier, action in long_convictions:
            lines.append(f"* **${sym}** (`{conf:+5.2f}%` · {tier}): {action}")
    else:
        lines.append("* *No assets currently qualify for bullish convergence (Score ≥ +25.0%).*")

    lines.append("\n### 🔴 Weekly Short / De-Risk Convictions (Distribution / Breakdowns)")
    if short_convictions:
        for sym, conf, tier, action in short_convictions:
            lines.append(f"* **${sym}** (`{conf:+5.2f}%` · {tier}): {action}")
    else:
        lines.append("* *No assets currently qualify for bearish convergence (Score ≤ -25.0%).*")

    lines.append("\n### ⚪ Neutral Watch & Consolidation (Range-Bound / Conflicting Regimes)")
    for sym, conf, tier, action in neutral_watches:
        lines.append(f"* **${sym}** (`{conf:+5.2f}%` · {tier}): {action}")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
