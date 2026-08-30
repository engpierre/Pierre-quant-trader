"""
tests/test_agent_07_contract.py
Deterministic validation harness for Agent 07 (Statistical Invariance Analyst).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.analysis.statistical_invariance import StatisticalInvarianceAgent, EquilibriumState

def test_statistical_invariance_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = StatisticalInvarianceAgent.analyze(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "z_score" in m
        assert "equilibrium_state" in m
        assert m["equilibrium_state"] in [e.value for e in EquilibriumState]
        assert m["bollinger_upper"] >= m["bollinger_lower"]
        
        print(f"✅ Statistical Analysis Passed ({ticker}): Spot=${payload.spot_price:.2f} | Z-Score={m['z_score']:+.2f} | State={m['equilibrium_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 07 (STATISTICAL INVARIANCE) CONTRACT VALIDATION")
    print("=" * 80)
    test_statistical_invariance_contract()
    print("=" * 80)
    print("✅ ALL AGENT 07 CONTRACT INVARIANTS CONFIRMED.\n")
