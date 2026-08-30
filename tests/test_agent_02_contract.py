"""
tests/test_agent_02_contract.py
Deterministic test harness for Agent 02 (Risk & Portfolio Guard).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.risk.portfolio_guard import RiskGuardAgent

def test_monotonic_invariant():
    """Verify that an existing stop of $100 NEVER ratchets down to $90."""
    ticker = "SOFI"
    high_stop = 100.0
    payload = RiskGuardAgent.evaluate(ticker, cost_basis=16.97, current_stop=high_stop)
    assert payload.status == ExecutionStatus.SUCCESS
    assert payload.metrics["proposed_stop"] >= high_stop, "Monotonic stop violation: Stop decreased!"
    assert payload.metrics["monotonic_floor_held"] is True
    print(f"✅ Monotonic Invariant Passed: Stop held at ${payload.metrics['proposed_stop']:.2f} >= ${high_stop:.2f}")

def test_risk_evaluation_live():
    """Verify active evaluation against live spot."""
    ticker = "SOFI"
    payload = RiskGuardAgent.evaluate(ticker, cost_basis=16.97, current_stop=15.00)
    assert payload.status == ExecutionStatus.SUCCESS
    assert payload.spot_price > 0.0
    assert payload.metrics["proposed_stop"] >= 15.00
    print(f"✅ Live Evaluation Passed ({ticker}): Spot=${payload.spot_price:.2f} | Phase={payload.metrics['ratchet_phase']} | Proposed Stop=${payload.metrics['proposed_stop']:.2f}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 02 (RISK & PORTFOLIO GUARD) CONTRACT VALIDATION")
    print("=" * 80)
    test_monotonic_invariant()
    test_risk_evaluation_live()
    print("=" * 80)
    print("✅ ALL AGENT 02 CONTRACT INVARIANTS CONFIRMED.\n")
