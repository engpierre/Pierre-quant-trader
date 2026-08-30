"""
pierre_quant/analysis/statistical_invariance.py
Agent 07 (Statistical Invariance Analyst) - Deterministic Z-Score & Volatility Band Worker.
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
logger = logging.getLogger("Agent07_StatInvariance")

class EquilibriumState(str, Enum):
    OVERBOUGHT = "OVERBOUGHT"
    OVERSOLD = "OVERSOLD"
    FAIR_VALUE = "FAIR_VALUE"

class StatisticalInvarianceAgent:
    """Agent 07: Mean-reversion Z-score and statistical equilibrium worker."""
    
    AGENT_ID = "07_statistical_invariance"
    WINDOW = 20
    NUM_STD = 2.0

    @classmethod
    def analyze_equilibrium(
        cls, 
        ticker: str, 
        period: str = "3mo"
    ) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        # 1. Ingest market history via Agent 05 Worker Contract
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

        if len(df) < cls.WINDOW:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Insufficient history ({len(df)} bars) for {cls.WINDOW}-period statistical window."
            )

        spot = feed_payload.spot_price
        closes = df["Close"]

        # 2. Deterministic Bollinger & Z-Score Mathematics
        rolling_mean = float(closes.rolling(window=cls.WINDOW).mean().iloc[-1])
        rolling_std = float(closes.rolling(window=cls.WINDOW).std().iloc[-1])
        
        z_score = float((spot - rolling_mean) / rolling_std) if rolling_std > 0 else 0.0
        upper_band = rolling_mean + (cls.NUM_STD * rolling_std)
        lower_band = rolling_mean - (cls.NUM_STD * rolling_std)
        percent_b = float((spot - lower_band) / (upper_band - lower_band)) if (upper_band - lower_band) > 0 else 0.5

        # 3. Equilibrium State & Mean-Reversion Bias Mapping
        if z_score >= cls.NUM_STD:
            state = EquilibriumState.OVERBOUGHT
            bias = DirectionalBias.BEARISH
        elif z_score <= -cls.NUM_STD:
            state = EquilibriumState.OVERSOLD
            bias = DirectionalBias.BULLISH
        else:
            state = EquilibriumState.FAIR_VALUE
            bias = DirectionalBias.NEUTRAL

        # Confidence scales proportionally with deviation magnitude
        deviation_magnitude = min(abs(z_score) / 3.0, 1.0)
        confidence = round(70.0 + (deviation_magnitude * 25.0), 1)

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID,
            ticker=clean_ticker,
            status=ExecutionStatus.SUCCESS,
            directional_bias=bias,
            confidence_score=confidence,
            spot_price=spot,
            metrics={
                "z_score": round(z_score, 4),
                "rolling_mean_20": round(rolling_mean, 4),
                "rolling_std_20": round(rolling_std, 4),
                "bollinger_upper": round(upper_band, 4),
                "bollinger_lower": round(lower_band, 4),
                "percent_b": round(percent_b, 4),
                "equilibrium_state": state.value
            }
        )

    # Standard Worker Aliases
    @classmethod
    def analyze(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.analyze_equilibrium(ticker, **kwargs)

    @classmethod
    def get_z_score(cls, ticker: str) -> float:
        payload = cls.analyze_equilibrium(ticker)
        return payload.metrics.get("z_score", 0.0) if payload.status == ExecutionStatus.SUCCESS else 0.0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 07: Statistical Invariance Worker CLI")
    parser.add_argument("--ticker", type=str, required=True, help="Holding symbol to evaluate")
    parser.add_argument("--period", type=str, default="3mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = StatisticalInvarianceAgent.analyze(args.ticker, period=args.period)
    
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
        print(f"Holding: {payload.ticker:<8} | Status: {payload.status.value:<7} | Spot: ${payload.spot_price:<9.2f} | Z-Score: {m.get('z_score', 0.0):<+6.2f} | State: {m.get('equilibrium_state', 'N/A'):<11} | Bias: {payload.directional_bias.value}")
