"""
tests/test_agent_15_contract.py
Deterministic validation harness for Agent 15 (Macro Environment Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.macro.macro_tracker import MacroEnvironmentAgent, MacroRegime

def test_macro_tracker_contract():
    test_contexts = ["SPY", "SOFI", "META"]
    for ctx in test_contexts:
        payload = MacroEnvironmentAgent.evaluate(ctx)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ctx}: {payload.error_message}"
        
        m = payload.metrics
        assert "macro_regime" in m, "Macro regime missing"
        assert m["macro_regime"] in [r.value for r in MacroRegime], f"Invalid regime: {m['macro_regime']}"
        
        print(f"✅ Macro Tracker Passed ({ctx}): Spot={payload.spot_price:.2f} | 10Y Yield={m.get('tnx_10y_yield', 'N/A')}% | DXY Δ={m.get('dxy_proxy_5d_delta_pct', 0.0):+5.2f}% | Regime={m['macro_regime']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 15 (MACRO ENVIRONMENT) CONTRACT VALIDATION")
    print("=" * 80)
    test_macro_tracker_contract()
    print("=" * 80)
    print("✅ ALL AGENT 15 CONTRACT INVARIANTS CONFIRMED.\n")
