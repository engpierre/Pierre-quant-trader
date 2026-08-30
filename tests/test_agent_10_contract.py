"""
tests/test_agent_10_contract.py
Deterministic validation harness for Agent 10 (Smart Money Flow Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.analysis.smart_money import SmartMoneyAgent, FlowRegime

def test_smart_money_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = SmartMoneyAgent.analyze(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "point_of_control" in m, "POC missing"
        assert "value_area_high" in m, "VAH missing"
        assert "value_area_low" in m, "VAL missing"
        assert "obv_slope_10" in m, "OBV slope missing"
        assert "flow_regime" in m, "Flow regime missing"
        assert m["flow_regime"] in [r.value for r in FlowRegime]
        assert m["value_area_high"] >= m["value_area_low"], f"VAH < VAL on {ticker}"
        
        print(f"✅ Smart Money Flow Passed ({ticker}): Spot=${payload.spot_price:.2f} | POC=${m['point_of_control']:.2f} | VAH=${m['value_area_high']:.2f} | VAL=${m['value_area_low']:.2f} | Regime={m['flow_regime']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 10 (SMART MONEY FLOW) CONTRACT VALIDATION")
    print("=" * 80)
    test_smart_money_contract()
    print("=" * 80)
    print("✅ ALL AGENT 10 CONTRACT INVARIANTS CONFIRMED.\n")
