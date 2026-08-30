"""
pierre_quant/analysis/timeframe_matrix.py
Agent 11 (Timeframe Matrix Alignment Worker) - Multi-Horizon Trend Confluence Engine.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

# Force UTF-8 output on Windows console
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path for direct CLI execution
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pierre_quant.core.agent_contract import AgentExecutionPayload, DirectionalBias, ExecutionStatus
from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent11_TimeframeMatrix")

class AlignmentState(str, Enum):
    FULL_BULLISH_CONFLUENCE = "FULL_BULLISH_CONFLUENCE"
    FULL_BEARISH_CONFLUENCE = "FULL_BEARISH_CONFLUENCE"
    TIMEFRAME_CONFLICT = "TIMEFRAME_CONFLICT"
    NEUTRAL_CONVERGENCE = "NEUTRAL_CONVERGENCE"

class TimeframeMatrixAgent:
    AGENT_ID = "11_timeframe_matrix"

    @classmethod
    def _evaluate_trend(cls, closes: pd.Series) -> int:
        """Returns +1 (Bullish), -1 (Bearish), or 0 (Neutral) based on EMA8 vs EMA21 slope."""
        if len(closes) < 21:
            return 0
        ema8 = closes.ewm(span=8, adjust=False).mean().iloc[-1]
        ema21 = closes.ewm(span=21, adjust=False).mean().iloc[-1]
        if ema8 > ema21 * 1.002:
            return 1
        elif ema8 < ema21 * 0.998:
            return -1
        return 0

    @classmethod
    def analyze_alignment(cls, ticker: str) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        # 1. Ingest Daily (Macro) and Weekly (Structure) feeds via Agent 05
        d_feed = LiveFeedIngestionAgent.fetch(clean_ticker, period="3mo", interval="1d")
        w_feed = LiveFeedIngestionAgent.fetch(clean_ticker, period="1y", interval="1wk")
        
        if d_feed.status != ExecutionStatus.SUCCESS or not d_feed.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 daily feed failed: {d_feed.error_message}"
            )

        d_closes = pd.Series([c.close for c in d_feed.candles])
        w_closes = pd.Series([c.close for c in w_feed.candles]) if (w_feed.status == ExecutionStatus.SUCCESS and w_feed.candles) else d_closes

        spot = d_feed.spot_price
        
        # 2. Multi-Horizon Vector Evaluation
        short_term = cls._evaluate_trend(d_closes.tail(15)) # ~15 days
        daily_trend = cls._evaluate_trend(d_closes)         # ~60 days
        macro_trend = cls._evaluate_trend(w_closes)         # ~52 weeks

        alignment_sum = short_term + daily_trend + macro_trend

        # 3. State & Alignment Index Mapping
        if alignment_sum >= 2:
            state = AlignmentState.FULL_BULLISH_CONFLUENCE
            bias = DirectionalBias.BULLISH
            conf = 90.0 if alignment_sum == 3 else 75.0
        elif alignment_sum <= -2:
            state = AlignmentState.FULL_BEARISH_CONFLUENCE
            bias = DirectionalBias.BEARISH
            conf = 90.0 if alignment_sum == -3 else 75.0
        elif (short_term * daily_trend < 0) or (daily_trend * macro_trend < 0):
            state = AlignmentState.TIMEFRAME_CONFLICT
            bias = DirectionalBias.NEUTRAL
            conf = 60.0
        else:
            state = AlignmentState.NEUTRAL_CONVERGENCE
            bias = DirectionalBias.NEUTRAL
            conf = 65.0

        compatibility_idx = round(((alignment_sum + 3) / 6.0) * 100.0, 1)

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
            directional_bias=bias, confidence_score=conf, spot_price=spot,
            metrics={
                "short_term_bias": short_term,
                "daily_trend_bias": daily_trend,
                "macro_trend_bias": macro_trend,
                "alignment_score": alignment_sum,
                "compatibility_index": compatibility_idx,
                "alignment_state": state.value
            }
        )

    @classmethod
    def analyze(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.analyze_alignment(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 11: Timeframe Matrix Worker CLI")
    parser.add_argument("--ticker", required=True, help="Ticker to analyze")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = TimeframeMatrixAgent.analyze(args.ticker)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<6} | Spot: ${payload.spot_price:<8.2f} | Score: {m['alignment_score']:+d}/3 | Index: {m['compatibility_index']}% | State: {m['alignment_state']} | Bias: {payload.directional_bias.value}")
