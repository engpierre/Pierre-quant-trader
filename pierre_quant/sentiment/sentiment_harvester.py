"""
pierre_quant/sentiment/sentiment_harvester.py
Agent 16 (Sentiment Harvester Worker) - News Buzz, Polarity Scoring & Dispersion Engine.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import yfinance as yf

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path for direct CLI execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import AgentExecutionPayload, DirectionalBias, ExecutionStatus

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent16_Sentiment")

BULLISH_KEYWORDS = {"surge", "beat", "growth", "upgrade", "record", "jump", "rally", "profit", "expansion", "buy", "gain"}
BEARISH_KEYWORDS = {"drop", "miss", "cut", "downgrade", "fall", "loss", "plunge", "decline", "warning", "slump", "investigation"}

class SentimentState(str, Enum):
    BULLISH_EUPHORIA = "BULLISH_EUPHORIA"
    BEARISH_FEAR = "BEARISH_FEAR"
    BALANCED_NEUTRAL = "BALANCED_NEUTRAL"
    DATA_BLINDSPOT = "DATA_BLINDSPOT"

class SentimentHarvesterAgent:
    AGENT_ID = "16_sentiment_harvester"

    @classmethod
    def evaluate_sentiment(cls, ticker: str) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        try:
            t = yf.Ticker(clean_ticker)
            news_items = getattr(t, "news", []) or []
            fast_info = getattr(t, "fast_info", {})
            spot = float(fast_info.get("lastPrice") or 0.0)

            # Enforce 20% Data-Opacity Penalty if news array returns empty
            if not news_items:
                return AgentExecutionPayload(
                    agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
                    directional_bias=DirectionalBias.NEUTRAL, confidence_score=50.0, spot_price=spot,
                    metrics={"polarity_score": 0.0, "article_count": 0, "sentiment_state": SentimentState.DATA_BLINDSPOT.value, "opacity_penalty": True}
                )

            pos_hits, neg_hits, total_words = 0, 0, 0
            for item in news_items[:10]:
                title = item.get("title", "")
                if not title and isinstance(item.get("content"), dict):
                    title = item.get("content", {}).get("title", "")
                title_str = str(title).lower()
                words = set(title_str.split())
                pos_hits += len(words & BULLISH_KEYWORDS)
                neg_hits += len(words & BEARISH_KEYWORDS)
                total_words += max(len(words), 1)

            total_hits = pos_hits + neg_hits
            if total_hits > 0:
                polarity = round((pos_hits - neg_hits) / float(total_hits), 2)
            else:
                polarity = 0.0

            # State & Bias Mapping
            if polarity >= 0.35:
                state = SentimentState.BULLISH_EUPHORIA
                bias = DirectionalBias.BULLISH
                conf = 80.0 if pos_hits >= 3 else 70.0
            elif polarity <= -0.35:
                state = SentimentState.BEARISH_FEAR
                bias = DirectionalBias.BEARISH
                conf = 80.0 if neg_hits >= 3 else 70.0
            else:
                state = SentimentState.BALANCED_NEUTRAL
                bias = DirectionalBias.NEUTRAL
                conf = 65.0

            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
                directional_bias=bias, confidence_score=conf, spot_price=spot,
                metrics={
                    "polarity_score": polarity,
                    "bullish_keyword_hits": pos_hits,
                    "bearish_keyword_hits": neg_hits,
                    "article_count": min(len(news_items), 10),
                    "sentiment_state": state.value
                }
            )
        except Exception as e:
            logger.error(f"Agent 16 exception on {clean_ticker}: {e}")
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=str(e)
            )

    @classmethod
    def harvest(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.evaluate_sentiment(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 16: Sentiment Harvester CLI")
    parser.add_argument("--ticker", required=True, help="Ticker to evaluate")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = SentimentHarvesterAgent.harvest(args.ticker)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<6} | Polarity: {m['polarity_score']:+4.2f} | Articles: {m['article_count']} | State: {m['sentiment_state']} | Bias: {payload.directional_bias.value}")
