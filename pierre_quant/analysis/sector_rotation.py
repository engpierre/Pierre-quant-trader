"""
pierre_quant/analysis/sector_rotation.py
Agent 14 (Sector Rotation Specialist Worker) - Benchmark-Relative Performance Engine.
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
logger = logging.getLogger("Agent14_SectorRotation")

SECTOR_MAP = {
    "META": "XLC", "GOOGL": "XLC", "SOFI": "XLF", "JPM": "XLF",
    "ENB": "XLE",  "XOM": "XLE",   "OKLO": "XLU", "NEE": "XLU",
    "BTC-USD": "SPY"
}

class SectorState(str, Enum):
    SECTOR_LEADER = "SECTOR_LEADER"
    IN_LINE_PERFORMER = "IN_LINE_PERFORMER"
    SECTOR_LAGGARD = "SECTOR_LAGGARD"

class SectorRotationAgent:
    AGENT_ID = "14_sector_rotation"

    @classmethod
    def evaluate_relative_strength(cls, ticker: str, period: str = "3mo") -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        benchmark = SECTOR_MAP.get(clean_ticker, "SPY")

        # Ingest asset and sector benchmark feeds via Agent 05 contract
        t_feed = LiveFeedIngestionAgent.fetch(clean_ticker, period=period, interval="1d")
        b_feed = LiveFeedIngestionAgent.fetch(benchmark, period=period, interval="1d")

        if t_feed.status != ExecutionStatus.SUCCESS or not t_feed.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 asset feed failed: {t_feed.error_message}"
            )
        if b_feed.status != ExecutionStatus.SUCCESS or not b_feed.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 benchmark ({benchmark}) feed failed: {b_feed.error_message}"
            )

        t_closes = np.array([c.close for c in t_feed.candles], dtype=np.float32)
        b_closes = np.array([c.close for c in b_feed.candles], dtype=np.float32)

        min_len = min(len(t_closes), len(b_closes))
        if min_len < 20:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=f"Insufficient matched history ({min_len} bars)."
            )

        t_ret = (t_closes[-1] - t_closes[-20]) / t_closes[-20] * 100.0
        b_ret = (b_closes[-1] - b_closes[-20]) / b_closes[-20] * 100.0
        alpha_20 = float(t_ret - b_ret)

        # Relative Strength Ratio (Asset / Benchmark)
        rs_ratio = (t_closes[-min_len:] / b_closes[-min_len:])
        rs_slope = float((rs_ratio[-1] - rs_ratio[-10]) / rs_ratio[-10] * 100.0)

        if alpha_20 >= 2.5 and rs_slope > 0:
            state = SectorState.SECTOR_LEADER
            bias = DirectionalBias.BULLISH
            conf = 85.0
        elif alpha_20 <= -2.5 and rs_slope < 0:
            state = SectorState.SECTOR_LAGGARD
            bias = DirectionalBias.BEARISH
            conf = 80.0
        else:
            state = SectorState.IN_LINE_PERFORMER
            bias = DirectionalBias.NEUTRAL
            conf = 65.0

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
            directional_bias=bias, confidence_score=conf, spot_price=t_feed.spot_price,
            metrics={
                "benchmark": benchmark,
                "asset_20d_ret_pct": round(float(t_ret), 2),
                "benchmark_20d_ret_pct": round(float(b_ret), 2),
                "alpha_20d_pct": round(alpha_20, 2),
                "rs_slope_10d_pct": round(rs_slope, 2),
                "sector_state": state.value
            }
        )

    @classmethod
    def evaluate(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.evaluate_relative_strength(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 14: Sector Rotation Worker CLI")
    parser.add_argument("--ticker", required=True, help="Ticker to evaluate")
    parser.add_argument("--period", default="3mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = SectorRotationAgent.evaluate(args.ticker, period=args.period)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<6} | Bench: {m['benchmark']} | Alpha: {m['alpha_20d_pct']:+5.2f}% | State: {m['sector_state']} | Bias: {payload.directional_bias.value}")
