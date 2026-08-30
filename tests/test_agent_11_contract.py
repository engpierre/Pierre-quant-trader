"""
tests/test_agent_11_contract.py
Deterministic validation harness for Agent 11 (Timeframe Matrix Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.analysis.timeframe_matrix import TimeframeMatrixAgent, AlignmentState

def test_timeframe_matrix_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = TimeframeMatrixAgent.analyze(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "short_term_bias" in m, "Short term bias missing"
        assert "daily_trend_bias" in m, "Daily trend bias missing"
        assert "macro_trend_bias" in m, "Macro trend bias missing"
        assert "alignment_score" in m, "Alignment score missing"
        assert -3 <= m["alignment_score"] <= 3, f"Score out of range: {m['alignment_score']}"
        assert 0.0 <= m["compatibility_index"] <= 100.0, f"Index out of range: {m['compatibility_index']}"
        assert m["alignment_state"] in [s.value for s in AlignmentState], f"Invalid state: {m['alignment_state']}"
        
        print(f"✅ Timeframe Matrix Passed ({ticker}): Spot=${payload.spot_price:.2f} | Score={m['alignment_score']:+d}/3 | Compatibility={m['compatibility_index']:.1f}% | State={m['alignment_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 11 (TIMEFRAME MATRIX) CONTRACT VALIDATION")
    print("=" * 80)
    test_timeframe_matrix_contract()
    print("=" * 80)
    print("✅ ALL AGENT 11 CONTRACT INVARIANTS CONFIRMED.\n")
