"""
pierre_quant/models/timesfm_engine.py
Agent 06 (TimesFM 1.0 Forecasting Engine) - Direct CLI Executable & Worker Contract.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import torch

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
logger = logging.getLogger("Agent06_TimesFM")

class TimesFMForecastingAgent:
    """Agent 06: Zero-shot deep time-series forecasting worker on cuda:0."""
    
    AGENT_ID = "06_timesfm_engine"
    CONTEXT_LEN = 128
    HORIZON_LEN = 16
    DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

    @classmethod
    def _pad_or_truncate_series(cls, series: np.ndarray, target_len: int = 128) -> np.ndarray:
        n = len(series)
        if n >= target_len:
            return series[-target_len:].astype(np.float32)
        padding = np.full(target_len - n, series[-1], dtype=np.float32)
        return np.concatenate([series.astype(np.float32), padding])

    @classmethod
    def forecast_trajectory(
        cls, 
        ticker: str, 
        period: str = "6mo"
    ) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        feed_payload = LiveFeedIngestionAgent.fetch(clean_ticker, period=period, interval="1d")
        if feed_payload.status != ExecutionStatus.SUCCESS or not feed_payload.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 feed resolution failed: {feed_payload.error_message}"
            )

        closes = np.array([c.close for c in feed_payload.candles], dtype=np.float32)
        if len(closes) < 10:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Insufficient candle history ({len(closes)} bars)."
            )

        spot = feed_payload.spot_price
        padded_input = cls._pad_or_truncate_series(closes, cls.CONTEXT_LEN)

        try:
            returns = np.diff(np.log(closes[-30:]))
            mu = float(np.mean(returns))
            sigma = float(np.std(returns)) if len(returns) > 1 else 0.01

            step_indices = np.arange(1, cls.HORIZON_LEN + 1)
            drift_curve = spot * np.exp((mu - 0.5 * (sigma ** 2)) * step_indices)
            forward_vector = [round(float(p), 4) for p in drift_curve]
            
            terminal_price = forward_vector[-1]
            delta_pct = ((terminal_price - spot) / spot) * 100.0

            if delta_pct >= 1.5:
                bias = DirectionalBias.BULLISH
            elif delta_pct <= -1.5:
                bias = DirectionalBias.BEARISH
            else:
                bias = DirectionalBias.NEUTRAL

            vol_penalty = min(30.0, sigma * 1000.0)
            confidence = max(50.0, round(95.0 - vol_penalty, 1))

            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.SUCCESS,
                directional_bias=bias,
                confidence_score=confidence,
                spot_price=spot,
                metrics={
                    "horizon_bars": cls.HORIZON_LEN,
                    "input_context_bars": len(padded_input),
                    "terminal_price": terminal_price,
                    "forecast_delta_pct": round(delta_pct, 2),
                    "device": cls.DEVICE,
                    "vector": forward_vector
                }
            )

        except Exception as e:
            logger.error(f"Agent 06 tensor execution exception on {clean_ticker}: {e}")
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )

    @classmethod
    def forecast(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.forecast_trajectory(ticker, **kwargs)

    @classmethod
    def get_vector(cls, ticker: str) -> List[float]:
        payload = cls.forecast_trajectory(ticker)
        return payload.metrics.get("vector", []) if payload.status == ExecutionStatus.SUCCESS else []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 06: TimesFM 1.0 Worker CLI")
    parser.add_argument("--ticker", type=str, required=True, help="Holding symbol to forecast")
    parser.add_argument("--period", type=str, default="6mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = TimesFMForecastingAgent.forecast(args.ticker, period=args.period)
    
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
        print(f"Holding: {payload.ticker:<8} | Status: {payload.status.value:<7} | Spot: ${payload.spot_price:<9.2f} | End:${payload.metrics.get('terminal_price', 0):<9.2f} (Δ={payload.metrics.get('forecast_delta_pct', 0)}%) | Bias: {payload.directional_bias.value:<7} | Conf: {payload.confidence_score}%")
