"""
pierre_quant/analysis/visual_sentry.py
Agent 09 (Operation Visual-Sentry Agent) - Deterministic VWAP & Structural Extrema Worker.
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
logger = logging.getLogger("Agent09_VisualSentry")

class StructuralState(str, Enum):
    ABOVE_VWAP_EXPANSION = "ABOVE_VWAP_EXPANSION"
    AT_VWAP_EQUILIBRIUM = "AT_VWAP_EQUILIBRIUM"
    BELOW_VWAP_COMPRESSION = "BELOW_VWAP_COMPRESSION"

class VisualSentryAgent:
    """Agent 09: Deterministic VWAP, pivot boundaries, and structural support/resistance worker."""
    
    AGENT_ID = "09_visual_sentry"
    EXTREMA_WINDOW = 5

    @classmethod
    def calculate_vwap(cls, df: pd.DataFrame) -> float:
        typical_price = (df["High"] + df["Low"] + df["Close"]) / 3.0
        total_vp = (typical_price * df["Volume"]).sum()
        total_vol = df["Volume"].sum()
        return float(total_vp / total_vol) if total_vol > 0 else float(df["Close"].iloc[-1])

    @classmethod
    def find_pivots(cls, df: pd.DataFrame, window: int = 5) -> Dict[str, float]:
        closes = df["Close"].values
        spot = closes[-1]
        
        supports: List[float] = []
        resistances: List[float] = []

        for i in range(window, len(closes) - window):
            curr = closes[i]
            if curr == np.min(closes[i - window : i + window + 1]):
                supports.append(float(curr))
            if curr == np.max(closes[i - window : i + window + 1]):
                resistances.append(float(curr))

        # Filter nearest levels relative to spot price
        lower_levels = [s for s in supports if s < spot]
        upper_levels = [r for r in resistances if r > spot]

        nearest_support = max(lower_levels) if lower_levels else float(df["Low"].min())
        nearest_resistance = min(upper_levels) if upper_levels else float(df["High"].max())

        return {
            "nearest_support": round(nearest_support, 4),
            "nearest_resistance": round(nearest_resistance, 4)
        }

    @classmethod
    def analyze_structure(
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

        if len(df) < 15:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Insufficient candle history ({len(df)} bars) for structural mapping."
            )

        spot = feed_payload.spot_price
        vwap = cls.calculate_vwap(df)
        pivots = cls.find_pivots(df, window=cls.EXTREMA_WINDOW)

        vwap_delta_pct = ((spot - vwap) / vwap) * 100.0

        # Classify structural regime
        if vwap_delta_pct > 1.0:
            state = StructuralState.ABOVE_VWAP_EXPANSION
            bias = DirectionalBias.BULLISH
        elif vwap_delta_pct < -1.0:
            state = StructuralState.BELOW_VWAP_COMPRESSION
            bias = DirectionalBias.BEARISH
        else:
            state = StructuralState.AT_VWAP_EQUILIBRIUM
            bias = DirectionalBias.NEUTRAL

        # Structural proximity confidence
        supp_gap = (spot - pivots["nearest_support"]) / spot if spot > 0 else 0.0
        res_gap = (pivots["nearest_resistance"] - spot) / spot if spot > 0 else 0.0
        
        # Higher confidence when grounded near confirmed support boundaries
        confidence = 75.0
        if supp_gap < 0.02:
            confidence = 85.0
        elif res_gap < 0.02:
            confidence = 80.0

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID,
            ticker=clean_ticker,
            status=ExecutionStatus.SUCCESS,
            directional_bias=bias,
            confidence_score=confidence,
            spot_price=spot,
            metrics={
                "vwap": round(vwap, 4),
                "vwap_delta_pct": round(vwap_delta_pct, 2),
                "nearest_support": pivots["nearest_support"],
                "nearest_resistance": pivots["nearest_resistance"],
                "structural_state": state.value
            }
        )

    # Standard Worker Aliases
    @classmethod
    def analyze(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.analyze_structure(ticker, **kwargs)

    @classmethod
    def get_vwap(cls, ticker: str) -> float:
        payload = cls.analyze_structure(ticker)
        return payload.metrics.get("vwap", 0.0) if payload.status == ExecutionStatus.SUCCESS else 0.0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 09: Visual-Sentry Worker CLI")
    parser.add_argument("--ticker", type=str, required=True, help="Holding symbol to evaluate")
    parser.add_argument("--period", type=str, default="3mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = VisualSentryAgent.analyze(args.ticker, period=args.period)
    
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
        print(f"Holding: {payload.ticker:<8} | Status: {payload.status.value:<7} | Spot: ${payload.spot_price:<9.2f} | VWAP: ${m.get('vwap', 0.0):<9.2f} (Δ={m.get('vwap_delta_pct', 0.0):<+5.2f}%) | Supp: ${m.get('nearest_support', 0.0):<9.2f} | Res: ${m.get('nearest_resistance', 0.0):<9.2f} | State: {m.get('structural_state', 'N/A')}")
