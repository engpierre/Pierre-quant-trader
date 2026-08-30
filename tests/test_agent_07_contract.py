"""
tests/test_agent_07_contract.py
Deterministic validation harness for Agent 07 (Statistical Invariance Engine).
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
    test_symbols = ["NVDA", "BTC-USD", "OKLO"]
    for sym in test_symbols:
        payload = StatisticalInvarianceAgent.analyze(sym, period="3mo")
        assert payload.status == ExecutionStatus.SUCCESS, f"Analysis failed: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "z_score" in m, "Z-Score missing in payload metrics"
        assert "rolling_mean_20" in m, "Rolling mean missing in payload metrics"
        assert "rolling_std_20" in m, "Rolling std missing in payload metrics"
        assert "bollinger_upper" in m, "Bollinger upper missing in payload metrics"
        assert "bollinger_lower" in m, "Bollinger lower missing in payload metrics"
        assert "percent_b" in m, "Percent B missing in payload metrics"
        assert m["equilibrium_state"] in [e.value for e in EquilibriumState]
        
        z = m["z_score"]
        if z >= 2.0:
            assert payload.directional_bias == DirectionalBias.BEARISH
            assert m["equilibrium_state"] == EquilibriumState.OVERBOUGHT.value
        elif z <= -2.0:
            assert payload.directional_bias == DirectionalBias.BULLISH
            assert m["equilibrium_state"] == EquilibriumState.OVERSOLD.value
        else:
            assert payload.directional_bias == DirectionalBias.NEUTRAL
            assert m["equilibrium_state"] == EquilibriumState.FAIR_VALUE.value

        print(f"✅ Live Statistical Check Passed ({sym}): Spot=${payload.spot_price:.2f} | Z={z:+.2f} | %B={m['percent_b']:.2f} | State={m['equilibrium_state']} | Bias={payload.directional_bias.value}")

def test_z_score_alias():
    ticker = "NVDA"
    z = StatisticalInvarianceAgent.get_z_score(ticker)
    assert isinstance(z, float)
    print(f"✅ Verified get_z_score alias ({ticker}): Z={z:+.4f}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 07 (STATISTICAL INVARIANCE) CONTRACT VALIDATION")
    print("=" * 80)
    test_statistical_invariance_contract()
    test_z_score_alias()
    print("=" * 80)
    print("✅ ALL AGENT 07 WORKER INVARIANTS CONFIRMED.\n")
