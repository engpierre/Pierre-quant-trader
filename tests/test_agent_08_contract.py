"""
tests/test_agent_08_contract.py
Deterministic validation harness for Agent 08 (Momentum Vector Agent).
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
        assert "macd_hist" in m
        assert "rsi_14" in m
        assert "roc_10" in m
        assert "velocity_state" in m
        assert m["velocity_state"] in [v.value for v in VelocityState]
        assert 0.0 <= m["rsi_14"] <= 100.0
        
        print(f"✅ Momentum Analysis Passed ({ticker}): Spot=${payload.spot_price:.2f} | RSI-14={m['rsi_14']:.1f} | Velocity={m['velocity_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 08 (MOMENTUM VECTOR) CONTRACT VALIDATION")
    print("=" * 80)
    test_momentum_vector_contract()
    print("=" * 80)
    print("✅ ALL AGENT 08 CONTRACT INVARIANTS CONFIRMED.\n")
