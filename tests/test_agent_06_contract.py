"""
tests/test_agent_06_contract.py
Deterministic validation harness for Agent 06 (TimesFM 1.0 Engine).
"""
import sys
from pathlib import Path
import numpy as np

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.models.timesfm_engine import TimesFMForecastingAgent

def test_tensor_padding_invariant():
    """Verify short and long arrays normalize to exact 128-bar context."""
    short_series = np.array([10.0, 11.0, 12.0], dtype=np.float32)
    padded = TimesFMForecastingAgent._pad_or_truncate_series(short_series, target_len=128)
    assert len(padded) == 128, f"Padding failed: expected 128, got {len(padded)}"
    assert padded[-1] == 12.0, "Right-padding failed to preserve latest spot price."

    long_series = np.arange(200, dtype=np.float32)
    truncated = TimesFMForecastingAgent._pad_or_truncate_series(long_series, target_len=128)
    assert len(truncated) == 128, f"Truncation failed: expected 128, got {len(truncated)}"
    assert truncated[-1] == 199.0, "Truncation failed to preserve latest spot price."
    print("✅ Tensor Shape Invariant Passed (Rigid 128-bar window guaranteed).")

def test_live_forecast_contract():
    """Verify live 16-bar forward trajectory payload generation."""
    ticker = "NVDA"
    payload = TimesFMForecastingAgent.forecast(ticker)
    assert payload.status == ExecutionStatus.SUCCESS, f"Forecast failed: {payload.error_message}"
    assert payload.spot_price > 0.0
    
    m = payload.metrics
    assert m["horizon_bars"] == 16, f"Expected 16-bar horizon, got {m['horizon_bars']}"
    assert len(m["vector"]) == 16, f"Vector length mismatch: {len(m['vector'])}"
    print(f"✅ Live Forecast Passed ({ticker}): Spot=${payload.spot_price:.2f} | 16-Bar End=${m['terminal_price']:.2f} (Δ={m['forecast_delta_pct']}%) | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 06 (TIMESFM 1.0) WORKER CONTRACT VALIDATION")
    print("=" * 80)
    test_tensor_padding_invariant()
    test_live_forecast_contract()
    print("=" * 80)
    print("✅ ALL AGENT 06 WORKER INVARIANTS CONFIRMED.\n")
