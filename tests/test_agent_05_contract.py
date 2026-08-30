"""
tests/test_agent_05_contract.py
Deterministic validation harness for Agent 05 (Live Ingestion Layer).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent

def test_symbol_rejection():
    invalid_inputs = ["/alpha", "/status", "\\recon", "INVALID$$TICKER", "", "   "]
    for bad_input in invalid_inputs:
        payload = LiveFeedIngestionAgent.fetch_spot_and_candles(bad_input)
        assert payload.status == ExecutionStatus.REJECTED, f"Failed to reject: {bad_input}"
        print(f"✅ Correctly rejected invalid input: '{bad_input}'")

def test_live_feed_resolution():
    test_symbols = ["BTC-USD", "NVDA", "OKLO"]
    for sym in test_symbols:
        payload = LiveFeedIngestionAgent.fetch_spot_and_candles(sym, period="1mo", interval="1d")
        assert payload.status == ExecutionStatus.SUCCESS, f"Failed to fetch {sym}: {payload.error_message}"
        assert payload.spot_price > 0.0, f"Invalid spot price for {sym}"
        assert len(payload.candles) > 0, f"Candles array empty for {sym}"
        print(f"✅ Successfully ingested {sym}: Spot=${payload.spot_price:.2f} ({len(payload.candles)} bars, Bias={payload.directional_bias})")

def test_resilient_aliases():
    test_symbol = "NVDA"
    payload = LiveFeedIngestionAgent.fetch(test_symbol, period="1mo", interval="1d")
    assert payload.status == ExecutionStatus.SUCCESS, f"fetch() alias failed on {test_symbol}"
    
    spot = LiveFeedIngestionAgent.get_spot(test_symbol)
    assert spot > 0.0, f"get_spot() returned non-positive value: {spot}"
    
    quote = LiveFeedIngestionAgent.get_quote(test_symbol)
    assert quote == spot, f"get_quote() mismatch: {quote} != {spot}"
    print(f"✅ Verified resilient aliases (fetch, get_spot, get_quote): NVDA=${spot:.2f}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 05 (LIVE INGESTION) CONTRACT VALIDATION HARNESS")
    print("=" * 80)
    test_symbol_rejection()
    test_live_feed_resolution()
    test_resilient_aliases()
    print("=" * 80)
    print("✅ ALL AGENT 05 CONTRACT TESTS PASSED DETERMINISTICALLY.\n")

