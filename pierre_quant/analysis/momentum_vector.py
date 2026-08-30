"""
pierre_quant/analysis/momentum_vector.py
Agent 08 (Momentum Vector Agent) - Deterministic Velocity, MACD & RSI Worker.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from datetime import datetime
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

from pierre_quant.core.agent_contract import (
    AgentExecutionPayload, DirectionalBias, ExecutionStatus
)
from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent

logging.basicConfig(level=logging.WARNING, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent08_MomentumVector")

class VelocityState(str, Enum):
    ACCELERATING_UPWARD = "ACCELERATING_UPWARD"
    COMPRESSING = "COMPRESSING"
    FLATLINING = "FLATLINING"
    ACCELERATING_DOWNWARD = "ACCELERATING_DOWNWARD"

class MomentumVectorAgent:
    """Agent 08: Deterministic multi-timeframe rate of change and momentum worker."""
    
    AGENT_ID = "08_momentum_vector"

    @classmethod
    def calculate_rsi(cls, series: pd.Series, period: int = 14) -> float:
        if len(series) < period + 1:
            return 50.0
        delta = series.diff().dropna()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean().iloc[-1]
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean().iloc[-1]
        
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return float(100.0 - (100.0 / (1.0 + rs)))

    @classmethod
    def analyze_momentum(
        cls, 
        ticker: str, 
        period: str = "3mo"
    ) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        # Ingest market history via Agent 05 Worker Contract
        feed_payload = LiveFeedIngestionAgent.fetch(clean_ticker, period=period, interval="1d")
        if feed_payload.status != ExecutionStatus.SUCCESS or not feed_payload.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 feed resolution failed: {feed_payload.error_message}"
            )

        df = pd.DataFrame([
            {"Open": c.open, "High": c.high, "Low": c.low, "Close": c.close, "Volume": c.volume}
            for c in feed_payload.candles
        ])

        if len(df) < 30:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Insufficient history ({len(df)} bars) for MACD/RSI calculations."
            )

        spot = feed_payload.spot_price
        closes = df["Close"]

        # 1. MACD Calculation (12, 26, 9)
        ema12 = closes.ewm(span=12, adjust=False).mean()
        ema26 = closes.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        macd_hist = macd_line - signal_line

        curr_hist = float(macd_hist.iloc[-1])
        prev_hist = float(macd_hist.iloc[-2])

        # 2. RSI & Rate of Change (ROC-10)
        rsi_14 = cls.calculate_rsi(closes, period=14)
        roc_10 = float(((closes.iloc[-1] - closes.iloc[-11]) / closes.iloc[-11]) * 100.0) if len(closes) >= 11 else 0.0

        # 3. Classify Velocity State
        if curr_hist > 0 and curr_hist > prev_hist:
            state = VelocityState.ACCELERATING_UPWARD
            bias = DirectionalBias.BULLISH
        elif curr_hist < 0 and curr_hist < prev_hist:
            state = VelocityState.ACCELERATING_DOWNWARD
            bias = DirectionalBias.BEARISH
        elif abs(curr_hist) < abs(prev_hist):
            state = VelocityState.COMPRESSING
            bias = DirectionalBias.NEUTRAL
        else:
            state = VelocityState.FLATLINING
            bias = DirectionalBias.NEUTRAL

        # Confidence derived from momentum agreement
        conf = 70.0
        if (bias == DirectionalBias.BULLISH and rsi_14 > 50 and roc_10 > 0) or \
           (bias == DirectionalBias.BEARISH and rsi_14 < 50 and roc_10 < 0):
            conf = 90.0
        elif bias == DirectionalBias.NEUTRAL:
            conf = 65.0

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID,
            ticker=clean_ticker,
            status=ExecutionStatus.SUCCESS,
            directional_bias=bias,
            confidence_score=conf,
            spot_price=spot,
            metrics={
                "macd_line": round(float(macd_line.iloc[-1]), 4),
                "signal_line": round(float(signal_line.iloc[-1]), 4),
                "macd_hist": round(curr_hist, 4),
                "rsi_14": round(rsi_14, 2),
                "roc_10": round(roc_10, 2),
                "velocity_state": state.value
            }
        )

    # Standard Worker Aliases
    @classmethod
    def analyze(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.analyze_momentum(ticker, **kwargs)

    @classmethod
    def get_velocity(cls, ticker: str) -> str:
        payload = cls.analyze_momentum(ticker)
        return payload.metrics.get("velocity_state", VelocityState.FLATLINING.value) if payload.status == ExecutionStatus.SUCCESS else VelocityState.FLATLINING.value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 08: Momentum Vector Worker CLI")
    parser.add_argument("--ticker", type=str, required=True, help="Holding symbol to evaluate")
    parser.add_argument("--period", type=str, default="3mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = MomentumVectorAgent.analyze(args.ticker, period=args.period)
    
    if args.json:
        out = {
            "agent_id": payload.agent_id,
            "ticker": payload.ticker,
            "status": payload.status.value,
            "directional_bias": payload.directional_bias.value,
            "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price,
            "metrics": payload.metrics,
            "error_message": payload.error_message
        }
        print(json.dumps(out))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<8} | Status: {payload.status.value:<7} | Spot: ${payload.spot_price:<9.2f} | RSI: {m.get('rsi_14', 0.0):<5.1f} | ROC10: {m.get('roc_10', 0.0):<+5.1f}% | State: {m.get('velocity_state', 'N/A'):<22} | Bias: {payload.directional_bias.value}")
