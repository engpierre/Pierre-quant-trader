"""
tests/test_agent_12_contract.py
Deterministic validation harness for Agent 12 (Corporate Fundamentals Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.fundamentals.corporate_fundamentals import CorporateFundamentalsAgent, FundamentalState

def test_corporate_fundamentals_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = CorporateFundamentalsAgent.evaluate(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        assert payload.spot_price > 0.0
        
        m = payload.metrics
        assert "trailing_pe" in m, "Trailing P/E missing"
        assert "forward_pe" in m, "Forward P/E missing"
        assert "price_to_book" in m, "Price to Book missing"
        assert "debt_to_equity" in m, "Debt to Equity missing"
        assert "fcf_yield_pct" in m, "FCF Yield missing"
        assert "fundamental_state" in m, "Fundamental state missing"
        assert m["fundamental_state"] in [s.value for s in FundamentalState], f"Invalid state: {m['fundamental_state']}"
        
        print(f"✅ Fundamental Health Passed ({ticker}): Spot=${payload.spot_price:.2f} | P/E={m['trailing_pe']:.1f} | D/E={m['debt_to_equity']:.1f} | FCF Yield={m['fcf_yield_pct']:+.1f}% | State={m['fundamental_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 12 (CORPORATE FUNDAMENTALS) CONTRACT VALIDATION")
    print("=" * 80)
    test_corporate_fundamentals_contract()
    print("=" * 80)
    print("✅ ALL AGENT 12 CONTRACT INVARIANTS CONFIRMED.\n")
