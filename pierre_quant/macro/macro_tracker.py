"""
pierre_quant/macro/macro_tracker.py
Agent 15 (Macro Environment Worker) - Yield Curve, Dollar Index & Systemic Regime Engine.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional
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
logger = logging.getLogger("Agent15_MacroTracker")

class MacroRegime(str, Enum):
    RISK_ON_EXPANSION = "RISK_ON_EXPANSION"
    RISK_OFF_DEFENSIVE = "RISK_OFF_DEFENSIVE"
    STAGFLATION_COMPRESSION = "STAGFLATION_COMPRESSION"
    NEUTRAL_TRANSITION = "NEUTRAL_TRANSITION"

class MacroEnvironmentAgent:
    AGENT_ID = "15_macro_tracker"

    @classmethod
    def evaluate_regime(cls, ticker: str = "SPY") -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        # Ingest Macro Benchmarks via Agent 05: 10Y Yield (^TNX), Dollar Index (DX-Y.NYB / UUP), SPY
        tnx_feed = LiveFeedIngestionAgent.fetch("^TNX", period="1mo", interval="1d")
        dxy_feed = LiveFeedIngestionAgent.fetch("UUP", period="1mo", interval="1d")
        spy_feed = LiveFeedIngestionAgent.fetch("SPY", period="1mo", interval="1d")

        # Fallback to neutral if macro feeds are restricted or unpopulated
        if tnx_feed.status != ExecutionStatus.SUCCESS or dxy_feed.status != ExecutionStatus.SUCCESS:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
                directional_bias=DirectionalBias.NEUTRAL, confidence_score=50.0, spot_price=spy_feed.spot_price if spy_feed.status == ExecutionStatus.SUCCESS else 0.0,
                metrics={"tnx_yield": 0.0, "dxy_delta_pct": 0.0, "macro_regime": MacroRegime.NEUTRAL_TRANSITION.value, "opacity_penalty": True}
            )

        tnx_closes = [c.close for c in tnx_feed.candles]
        dxy_closes = [c.close for c in dxy_feed.candles]
        
        tnx_spot = float(tnx_closes[-1]) if tnx_closes else 4.0
        dxy_delta = float((dxy_closes[-1] - dxy_closes[-5]) / dxy_closes[-5] * 100.0) if len(dxy_closes) >= 5 else 0.0
        tnx_delta = float((tnx_closes[-1] - tnx_closes[-5]) / tnx_closes[-5] * 100.0) if len(tnx_closes) >= 5 else 0.0

        # Systemic Macro Matrix Logic
        if dxy_delta < 0 and tnx_delta <= 0:
            regime = MacroRegime.RISK_ON_EXPANSION
            bias = DirectionalBias.BULLISH
            conf = 80.0
        elif dxy_delta > 0.5 and tnx_delta > 0.5:
            regime = MacroRegime.RISK_OFF_DEFENSIVE
            bias = DirectionalBias.BEARISH
            conf = 80.0
        elif dxy_delta > 0.5 and tnx_delta <= 0:
            regime = MacroRegime.STAGFLATION_COMPRESSION
            bias = DirectionalBias.BEARISH
            conf = 75.0
        else:
            regime = MacroRegime.NEUTRAL_TRANSITION
            bias = DirectionalBias.NEUTRAL
            conf = 65.0

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
            directional_bias=bias, confidence_score=conf, spot_price=tnx_spot,
            metrics={
                "tnx_10y_yield": round(tnx_spot, 2),
                "tnx_5d_delta_pct": round(tnx_delta, 2),
                "dxy_proxy_5d_delta_pct": round(dxy_delta, 2),
                "macro_regime": regime.value
            }
        )

    @classmethod
    def evaluate(cls, ticker: str = "SPY", **kwargs) -> AgentExecutionPayload:
        return cls.evaluate_regime(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 15: Macro Tracker Worker CLI")
    parser.add_argument("--ticker", default="SPY", help="Holding context (default: SPY)")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = MacroEnvironmentAgent.evaluate(args.ticker)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Macro Context: {payload.ticker} | 10Y Yield: {m.get('tnx_10y_yield')}% | DXY Proxy Δ: {m.get('dxy_proxy_5d_delta_pct', 0.0):+5.2f}% | Regime: {m.get('macro_regime')} | Bias: {payload.directional_bias.value}")
