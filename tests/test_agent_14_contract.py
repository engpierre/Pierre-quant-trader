"""
tests/test_agent_14_contract.py
Deterministic validation harness for Agent 14 (Sector Rotation Specialist Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.analysis.sector_rotation import SectorRotationAgent, SectorState

def test_sector_rotation_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = SectorRotationAgent.evaluate(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "benchmark" in m, "Benchmark missing"
        assert "asset_20d_ret_pct" in m, "Asset return missing"
        assert "benchmark_20d_ret_pct" in m, "Benchmark return missing"
        assert "alpha_20d_pct" in m, "Alpha missing"
        assert "rs_slope_10d_pct" in m, "RS slope missing"
        assert "sector_state" in m, "Sector state missing"
        assert m["sector_state"] in [s.value for s in SectorState], f"Invalid sector state: {m['sector_state']}"
        
        print(f"✅ Sector Rotation Passed ({ticker}): Spot=${payload.spot_price:.2f} | Bench={m['benchmark']} | Alpha={m['alpha_20d_pct']:+5.2f}% | RS Slope={m['rs_slope_10d_pct']:+5.2f}% | State={m['sector_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 14 (SECTOR ROTATION) CONTRACT VALIDATION")
    print("=" * 80)
    test_sector_rotation_contract()
    print("=" * 80)
    print("✅ ALL AGENT 14 CONTRACT INVARIANTS CONFIRMED.\n")
