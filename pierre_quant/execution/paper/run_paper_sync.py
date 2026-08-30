"""
pierre_quant/execution/paper/run_paper_sync.py
Synchronizes active paper positions, evaluates monotonic trailing stops, and dumps UI state JSON for Julie Core HUD.
"""
from __future__ import annotations
import json
import sys
import time
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

DATA_DIR = PROJECT_ROOT / "pierre_quant" / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
STATE_JSON_PATH = DATA_DIR / "paper_portfolio_state.json"

from pierre_quant.execution.paper.paper_ledger import PaperLedger
from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent
from pierre_quant.risk.portfolio_guard import PortfolioGuardAgent


def seed_initial_positions_if_empty():
    """Seeds default approved long allocations if ledger is currently empty."""
    open_pos = PaperLedger.get_open_positions()
    if not open_pos:
        initial_allocations = [
            ("PFE", 53),
            ("CELH", 45),
            ("TSCO", 43)
        ]
        for sym, shs in initial_allocations:
            feed = LiveFeedIngestionAgent.fetch(sym, period="1mo", interval="1d")
            risk = PortfolioGuardAgent.calculate_stops(sym)
            spot = feed.spot_price if feed and feed.spot_price > 0 else 30.0
            stop = risk.metrics.get("proposed_stop", spot * 0.95)
            PaperLedger.add_position(sym, shs, spot, stop)


def main():
    seed_initial_positions_if_empty()
    sync_result = PaperLedger.sync_positions()

    # Dump state JSON for Julie Core HUD polling
    STATE_JSON_PATH.write_text(json.dumps(sync_result, indent=2), encoding="utf-8")

    # Render Markdown Report
    lines = [
        "# 📄 SANDBOXED PAPER PORTFOLIO & HUD STATE SYNC",
        f"**Sync Timestamp:** `{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(sync_result['last_sync']))}` | "
        f"**Total Equity:** `${sync_result['total_equity']:,.2f}` | **Open PnL:** `${sync_result['unrealized_pnl']:+,.2f}`\n",
        "| Ticker | Shares | Entry Price | Current Spot | Trailing Stop | Stop Distance | Open PnL ($) | PnL (%) | Status |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
    ]

    for p in sync_result["positions"]:
        lines.append(
            f"| **${p['ticker']}** | {p['shares']} shs | `${p['entry']:.2f}` | `${p['spot']:.2f}` | "
            f"`${p['stop']:.2f}` | `{p['stop_dist_pct']:+.1f}%` | `${p['pnl_usd']:+,.2f}` | `{p['pnl_pct']:+5.2f}%` | `{p['status']}` |"
        )

    lines.extend([
        "\n---",
        f"*UI HUD state bridge written to: `pierre_quant/data/paper_portfolio_state.json`*"
    ])

    print("\n".join(lines))


if __name__ == "__main__":
    main()
