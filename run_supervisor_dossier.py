"""
run_supervisor_dossier.py
Lead Quant Systems Architect: Agent 01 Supervisor Master Dossier Runner.
Compiles live multi-agent confluence and risk-floor envelopes across target assets.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path

# UTF-8 stdout protection for Windows CP1252 environments
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.platform == "win32" and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.orchestration.supervisor import SupervisorOrchestrator, SupervisorSynthesisResult

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("SupervisorDossier")


def main():
    parser = argparse.ArgumentParser(description="Agent 01 Supervisor Master Synthesis Harness")
    parser.add_argument("tickers", nargs="*", default=["SOFI", "META", "ENB"], help="Holding tickers to synthesize")
    parser.add_argument("--ticker", type=str, default="", help="Single ticker analysis")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    targets = [args.ticker.strip().upper()] if args.ticker else args.tickers

    for sym in targets:
        try:
            res: SupervisorSynthesisResult = SupervisorOrchestrator.synthesize(sym)
            if args.json:
                print(json.dumps({
                    "ticker": res.ticker,
                    "spot_price": res.spot_price,
                    "consensus_bias": res.consensus_bias.value,
                    "net_confluence_score": res.net_confluence_score,
                    "predictive_spread_pct": res.predictive_spread_pct,
                    "predictive_regime": res.predictive_regime,
                    "risk_invalidation_floor": res.risk_invalidation_floor,
                    "action_directive": res.action_directive,
                    "vote_breakdown": res.vote_breakdown
                }))
            else:
                print(f"\n# TARGET DEEP-DIVE DOSSIER :: ${res.ticker}")
                print(f"* **Spot Price:** ${res.spot_price:.2f}")
                print(f"* **Consensus Bias:** `{res.consensus_bias.value}` | **Net Confluence:** {res.net_confluence_score:+5.2f}%")
                print(f"* **Predictive Spread:** {res.predictive_spread_pct:+5.2f}% ({res.predictive_regime})")
                print(f"* **Risk Stop Floor (Agent 02):** ${res.risk_invalidation_floor:.2f}")
                print(f"* **Action Directive:** {res.action_directive}\n")
                print("| Agent Node | Bias | Raw Conf | Eff Wt | Key Metric Summary |")
                print("| :--- | :--- | :--- | :--- | :--- |")
                for node, data in res.vote_breakdown.items():
                    print(f"| **{node}** | `{data['bias']}` | {data['confidence']:.1f}% | {data['effective_weight']:.1f} | `{str(data['metrics'])[:50]}` |")
        except Exception as err:
            logger.error(f"Failed synthesis for {sym}: {err}")


if __name__ == "__main__":
    main()
