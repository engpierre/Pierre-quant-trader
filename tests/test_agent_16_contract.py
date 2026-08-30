"""
tests/test_agent_16_contract.py
Deterministic validation harness for Agent 16 (Sentiment Harvester Agent).
"""
import sys
from pathlib import Path

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import ExecutionStatus, DirectionalBias
from pierre_quant.sentiment.sentiment_harvester import SentimentHarvesterAgent, SentimentState

def test_sentiment_harvester_contract():
    test_tickers = ["SOFI", "META", "ENB"]
    for ticker in test_tickers:
        payload = SentimentHarvesterAgent.harvest(ticker)
        assert payload.status == ExecutionStatus.SUCCESS, f"Execution failed on {ticker}: {payload.error_message}"
        
        m = payload.metrics
        assert "polarity_score" in m, "Polarity score missing"
        assert "article_count" in m, "Article count missing"
        assert "sentiment_state" in m, "Sentiment state missing"
        assert -1.0 <= m["polarity_score"] <= 1.0, f"Polarity out of range: {m['polarity_score']}"
        assert m["sentiment_state"] in [s.value for s in SentimentState], f"Invalid sentiment state: {m['sentiment_state']}"
        
        print(f"✅ Sentiment Harvester Passed ({ticker}): Spot=${payload.spot_price:.2f} | Polarity={m['polarity_score']:+4.2f} | Articles={m['article_count']} | State={m['sentiment_state']} | Bias={payload.directional_bias.value}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("RUNNING AGENT 16 (SENTIMENT HARVESTER) CONTRACT VALIDATION")
    print("=" * 80)
    test_sentiment_harvester_contract()
    print("=" * 80)
    print("✅ ALL AGENT 16 CONTRACT INVARIANTS CONFIRMED.\n")
