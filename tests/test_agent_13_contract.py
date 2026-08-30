"""
tests/test_agent_13_contract.py
Deterministic validation harness for Agent 13 (Regulatory & SEC Watchdog Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.regulatory.sec_watchdog import SECWatchdogAgent, RegulatoryState

def test_sec_watchdog_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = SECWatchdogAgent.evaluate(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price >= 0.0
        
        m = payload.metrics
        assert "insider_net_shares" in m, "Net shares missing"
        assert "purchase_count" in m, "Purchase count missing"
        assert "sale_count" in m, "Sale count missing"
        assert "regulatory_state" in m, "Regulatory state missing"
        assert m["regulatory_state"] in [r.value for r in RegulatoryState], f"Invalid regulatory state: {m['regulatory_state']}"
        
        print(f"✅ SEC Watchdog Passed ({ticker}): Spot=${payload.spot_price:.2f} | Buys={m['purchase_count']} | Sells={m['sale_count']} | Net Shares={m['insider_net_shares']:+d} | State={m['regulatory_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 13 (SEC WATCHDOG) CONTRACT VALIDATION")
    print("=" * 80)
    test_sec_watchdog_contract()
    print("=" * 80)
    print("✅ ALL AGENT 13 CONTRACT INVARIANTS CONFIRMED.\n")
