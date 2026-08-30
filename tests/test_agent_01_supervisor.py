"""
tests/test_agent_01_supervisor.py
Deterministic validation harness for Agent 01 (Supervisor Orchestrator).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.orchestration.supervisor import SupervisorOrchestrator, ConsensusBias

def test_supervisor_synthesis_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        res = SupervisorOrchestrator.synthesize(ticker)
        assert res.spot_price > 0.0, f"Zero spot price on {ticker}"
        assert res.consensus_bias in [b for b in ConsensusBias], f"Invalid bias: {res.consensus_bias}"
        assert -100.0 <= res.net_confluence_score <= 100.0, f"Confluence score out of bounds: {res.net_confluence_score}"
        assert res.predictive_regime in ("CONFLICTING_REGIME", "CONVERGENT_REGIME")
        assert res.risk_invalidation_floor > 0.0, f"Invalid stop floor: {res.risk_invalidation_floor}"
        assert len(res.vote_breakdown) >= 10, f"Incomplete vote breakdown on {ticker}: {len(res.vote_breakdown)}"
        assert res.action_directive != ""
        
        print(f"✅ Supervisor Synthesis Passed ({ticker}): Spot=${res.spot_price:.2f} | Consensus={res.consensus_bias.value} | Confluence={res.net_confluence_score:+5.2f}% | Spread={res.predictive_spread_pct:+5.2f}% ({res.predictive_regime}) | Stop Floor=${res.risk_invalidation_floor:.2f}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 01 (SUPERVISOR ORCHESTRATOR) CONTRACT VALIDATION")
    print("=" * 80)
    test_supervisor_synthesis_contract()
    print("=" * 80)
    print("✅ ALL AGENT 01 CONTRACT INVARIANTS CONFIRMED.\n")
