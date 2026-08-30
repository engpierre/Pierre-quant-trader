"""
pierre_quant/analysis/smart_money.py
Agent 10 (Smart Money Flow Worker) - Volume Profile & Institutional Accumulation Engine.
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
logger = logging.getLogger("Agent10_SmartMoney")

class FlowRegime(str, Enum):
    INSTITUTIONAL_ACCUMULATION = "INSTITUTIONAL_ACCUMULATION"
    INSTITUTIONAL_DISTRIBUTION = "INSTITUTIONAL_DISTRIBUTION"
    NEUTRAL_FLOW = "NEUTRAL_FLOW"

class SmartMoneyAgent:
    AGENT_ID = "10_smart_money_flow"

    @classmethod
    def calculate_volume_profile(cls, df: pd.DataFrame, bins: int = 10) -> Dict[str, float]:
        price_min, price_max = df["Low"].min(), df["High"].max()
        if price_min == price_max:
            return {"point_of_control": float(price_min), "value_area_high": float(price_max), "value_area_low": float(price_min)}
        
        hist, bin_edges = np.histogram(df["Close"], bins=bins, weights=df["Volume"])
        poc_idx = int(np.argmax(hist))
        poc = float((bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2.0)
        
        # Approximate 70% Value Area
        total_vol = hist.sum()
        target_vol = total_vol * 0.70
        sorted_indices = np.argsort(hist)[::-1]
        accum_vol, va_bins = 0.0, []
        for idx in sorted_indices:
            accum_vol += hist[idx]
            va_bins.append(idx)
            if accum_vol >= target_vol:
                break
        
        vah = float(bin_edges[max(va_bins) + 1])
        val = float(bin_edges[min(va_bins)])
        return {"point_of_control": round(poc, 4), "value_area_high": round(vah, 4), "value_area_low": round(val, 4)}

    @classmethod
    def analyze_flow(cls, ticker: str, period: str = "3mo") -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        feed_payload = LiveFeedIngestionAgent.fetch(clean_ticker, period=period, interval="1d")
        if feed_payload.status != ExecutionStatus.SUCCESS or not feed_payload.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 feed failed: {feed_payload.error_message}"
            )

        df = pd.DataFrame([{"Open": c.open, "High": c.high, "Low": c.low, "Close": c.close, "Volume": c.volume} for c in feed_payload.candles])
        if len(df) < 20:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=f"Insufficient history ({len(df)} bars) for Volume Profile."
            )

        spot = feed_payload.spot_price
        vp = cls.calculate_volume_profile(df, bins=10)
        
        # On-Balance Volume (OBV) trend slope (10-bar)
        obv = (np.sign(df["Close"].diff().fillna(0)) * df["Volume"]).cumsum()
        obv_slope = float(obv.iloc[-1] - obv.iloc[-10]) if len(obv) >= 10 else 0.0

        # Institutional Regime Logic
        if spot >= vp["point_of_control"] and obv_slope > 0:
            regime = FlowRegime.INSTITUTIONAL_ACCUMULATION
            bias = DirectionalBias.BULLISH
            conf = 85.0 if spot >= vp["value_area_high"] else 75.0
        elif spot < vp["point_of_control"] and obv_slope < 0:
            regime = FlowRegime.INSTITUTIONAL_DISTRIBUTION
            bias = DirectionalBias.BEARISH
            conf = 85.0 if spot <= vp["value_area_low"] else 75.0
        else:
            regime = FlowRegime.NEUTRAL_FLOW
            bias = DirectionalBias.NEUTRAL
            conf = 65.0

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
            directional_bias=bias, confidence_score=conf, spot_price=spot,
            metrics={
                "point_of_control": vp["point_of_control"],
                "value_area_high": vp["value_area_high"],
                "value_area_low": vp["value_area_low"],
                "obv_slope_10": round(obv_slope, 2),
                "flow_regime": regime.value
            }
        )

    @classmethod
    def analyze(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.analyze_flow(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 10: Smart Money Flow Worker CLI")
    parser.add_argument("--ticker", required=True, help="Ticker to analyze")
    parser.add_argument("--period", default="3mo", help="Lookback period")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = SmartMoneyAgent.analyze(args.ticker, period=args.period)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<6} | Spot: ${payload.spot_price:<8.2f} | POC: ${m['point_of_control']:<8.2f} | VAH: ${m['value_area_high']:<8.2f} | VAL: ${m['value_area_low']:<8.2f} | Regime: {m['flow_regime']} | Bias: {payload.directional_bias.value}")
