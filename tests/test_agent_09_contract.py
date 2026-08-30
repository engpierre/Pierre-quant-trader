"""
tests/test_agent_09_contract.py
Deterministic validation harness for Agent 09 (Operation Visual-Sentry Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.analysis.visual_sentry import VisualSentryAgent, StructuralState

def test_visual_sentry_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = VisualSentryAgent.analyze(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "vwap" in m, "VWAP missing"
        assert "vwap_delta_pct" in m, "VWAP delta missing"
        assert "nearest_support" in m, "Nearest support missing"
        assert "nearest_resistance" in m, "Nearest resistance missing"
        assert m["structural_state"] in [s.value for s in StructuralState], f"Invalid structural state: {m['structural_state']}"
        assert m["nearest_resistance"] >= m["nearest_support"], f"Resistance lower than support on {ticker}"
        
        print(f"✅ Structural Sentry Passed ({ticker}): Spot=${payload.spot_price:.2f} | VWAP=${m['vwap']:.2f} (Δ={m['vwap_delta_pct']:+.2f}%) | Supp=${m['nearest_support']:.2f} | Res=${m['nearest_resistance']:.2f} | State={m['structural_state']} | Bias={payload.directional_bias.value}")

def test_vwap_alias():
    ticker = "SOFI"
    vwap = VisualSentryAgent.get_vwap(ticker)
    assert isinstance(vwap, float)
    assert vwap > 0.0
    print(f"✅ Verified get_vwap alias ({ticker}): VWAP=${vwap:.2f}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 09 (VISUAL-SENTRY STRUCTURAL) CONTRACT VALIDATION")
    print("=" * 80)
    test_visual_sentry_contract()
    test_vwap_alias()
    print("=" * 80)
    print("✅ ALL AGENT 09 CONTRACT INVARIANTS CONFIRMED.\n")
