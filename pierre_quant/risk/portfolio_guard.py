"""
pierre_quant/risk/portfolio_guard.py
Agent 02 (Risk & Portfolio Guard) - Dynamic Monotonic ATR Stop-Loss & Risk Engine.
"""
from __future__ import annotations
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from pierre_quant.core.agent_contract import (
    AgentExecutionPayload, DirectionalBias, ExecutionStatus
)
from pierre_quant.ingestion.live_feed import LiveFeedIngestionAgent

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent02_RiskGuard")

WORKSPACE_ROOT = Path(r"C:\Users\Pierre\.openclaw\workspace")
DB_PATH = Path(r"C:\Users\Pierre\.openclaw\pierre_quant.db")

class RiskGuardAgent:
    """Agent 02: Enforces monotonic volatility stops and capital defense invariants."""
    
    AGENT_ID = "02_risk_portfolio_guard"
    ATR_MULTIPLIER = 1.8
    ATR_PERIOD = 14

    @classmethod
    def calculate_atr(cls, df: pd.DataFrame, period: int = 14) -> float:
        if len(df) < period + 1:
            return 0.0
        high = df["High"].values
        low = df["Low"].values
        close = df["Close"].values
        
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        atr_series = pd.Series(tr).rolling(window=period).mean()
        return float(atr_series.dropna().iloc[-1])

    @classmethod
    def evaluate_position_risk(
        cls, 
        ticker: str, 
        cost_basis: float, 
        current_stop: float
    ) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        # 1. Fetch live candles via Agent 05 Employee Contract
        feed_payload = LiveFeedIngestionAgent.fetch(clean_ticker, period="3mo", interval="1d")
        if feed_payload.status != ExecutionStatus.SUCCESS or not feed_payload.candles:
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=f"Agent 05 upstream feed failed: {feed_payload.error_message}"
            )

        spot = feed_payload.spot_price
        c_df = pd.DataFrame([
            {"Open": c.open, "High": c.high, "Low": c.low, "Close": c.close, "Volume": c.volume}
            for c in feed_payload.candles
        ])

        atr = cls.calculate_atr(c_df, period=cls.ATR_PERIOD)
        atr_buffer = cls.ATR_MULTIPLIER * atr if atr > 0 else (spot * 0.05)
        raw_floor = spot - atr_buffer

        # Calculate standard return and standard deviation bands
        gain_pct = ((spot - cost_basis) / cost_basis) * 100.0 if cost_basis > 0 else 0.0
        rolling_std = float(c_df["Close"].pct_change().rolling(20).std().iloc[-1]) if len(c_df) >= 20 else 0.02
        sigma_1_0 = rolling_std * cost_basis * 100.0

        # Monotonic Ratchet Rules (Stop can only ascend)
        proposed_stop = current_stop
        ratchet_phase = "BASE"

        if spot >= cost_basis + (2.5 * sigma_1_0):
            # Phase 3 Ratchet: Lock +1.5 sigma
            proposed_stop = max(current_stop, cost_basis + (1.5 * sigma_1_0))
            ratchet_phase = "PHASE_3_PROFIT_LOCK"
        elif spot >= cost_basis + (1.5 * sigma_1_0):
            # Phase 2 Ratchet: Lock +0.75 sigma
            proposed_stop = max(current_stop, cost_basis + (0.75 * sigma_1_0))
            ratchet_phase = "PHASE_2_EXPANSION"
        elif spot >= cost_basis + (1.0 * sigma_1_0):
            # Phase 1 Ratchet: Move to Breakeven
            proposed_stop = max(current_stop, cost_basis)
            ratchet_phase = "PHASE_1_BREAKEVEN"
        else:
            # Base dynamic ATR floor
            proposed_stop = max(current_stop, raw_floor)

        # Monotonic Invariant Enforcement
        final_stop = max(current_stop, proposed_stop)
        stop_breached = spot <= final_stop

        bias = DirectionalBias.BEARISH if stop_breached else (
            DirectionalBias.BULLISH if gain_pct > 0 else DirectionalBias.NEUTRAL
        )

        return AgentExecutionPayload(
            agent_id=cls.AGENT_ID,
            ticker=clean_ticker,
            status=ExecutionStatus.SUCCESS,
            directional_bias=bias,
            confidence_score=95.0,
            spot_price=spot,
            metrics={
                "cost_basis": round(cost_basis, 4),
                "current_stop": round(current_stop, 4),
                "computed_atr": round(atr, 4),
                "proposed_stop": round(final_stop, 4),
                "ratchet_phase": ratchet_phase,
                "gain_pct": round(gain_pct, 2),
                "stop_breached": stop_breached,
                "monotonic_floor_held": final_stop >= current_stop
            }
        )

    # Resilient Employee Aliases
    @classmethod
    def evaluate(cls, ticker: str, cost_basis: float, current_stop: float) -> AgentExecutionPayload:
        return cls.evaluate_position_risk(ticker, cost_basis, current_stop)

    @classmethod
    def get_stop_floor(cls, ticker: str, cost_basis: float, current_stop: float) -> float:
        payload = cls.evaluate_position_risk(ticker, cost_basis, current_stop)
        return payload.metrics.get("proposed_stop", current_stop) if payload.status == ExecutionStatus.SUCCESS else current_stop
