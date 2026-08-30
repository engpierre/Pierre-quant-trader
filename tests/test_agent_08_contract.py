"""
tests/test_agent_08_contract.py
Deterministic validation harness for Agent 08 (Momentum Vector Analyst).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.analysis.momentum_vector import MomentumVectorAgent, VelocityState

def test_momentum_vector_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = MomentumVectorAgent.analyze(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "macd_line" in m, "MACD line missing"
        assert "signal_line" in m, "Signal line missing"
        assert "macd_hist" in m, "MACD histogram missing"
        assert "rsi_14" in m, "RSI missing"
        assert 0.0 <= m["rsi_14"] <= 100.0, f"RSI out of bounds: {m['rsi_14']}"
        assert "roc_10" in m, "ROC-10 missing"
        assert m["velocity_state"] in [v.value for v in VelocityState], f"Invalid velocity state: {m['velocity_state']}"
        
        print(f"✅ Momentum Analysis Passed ({ticker}): Spot=${payload.spot_price:.2f} | RSI={m['rsi_14']:.1f} | ROC10={m['roc_10']:+.1f}% | State={m['velocity_state']} | Bias={payload.directional_bias.value}")

def test_velocity_alias():
    ticker = "SOFI"
    vel = MomentumVectorAgent.get_velocity(ticker)
    assert vel in [v.value for v in VelocityState]
    print(f"✅ Verified get_velocity alias ({ticker}): Velocity={vel}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 08 (MOMENTUM VECTOR) CONTRACT VALIDATION")
    print("=" * 80)
    test_momentum_vector_contract()
    test_velocity_alias()
    print("=" * 80)
    print("✅ ALL AGENT 08 CONTRACT INVARIANTS CONFIRMED.\n")
