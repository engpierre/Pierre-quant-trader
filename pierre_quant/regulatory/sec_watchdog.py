"""
pierre_quant/regulatory/sec_watchdog.py
Agent 13 (Regulatory & SEC Watchdog Worker) - Deterministic Insider Transaction Engine.
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
logger = logging.getLogger("Agent13_SECWatchdog")

class RegulatoryState(str, Enum):
    INSIDER_ACCUMULATION = "INSIDER_ACCUMULATION"
    INSIDER_DISTRIBUTION = "INSIDER_DISTRIBUTION"
    CLEAN_NEUTRAL = "CLEAN_NEUTRAL"
    INSIDER_BLINDSPOT = "INSIDER_BLINDSPOT"

class SECWatchdogAgent:
    AGENT_ID = "13_sec_watchdog"

    @classmethod
    def evaluate_insiders(cls, ticker: str) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        try:
            t = yf.Ticker(clean_ticker)
            df_insiders = t.insider_transactions
            fast_info = getattr(t, "fast_info", {})
            spot = float(fast_info.get("lastPrice") or 0.0)

            if df_insiders is None or df_insiders.empty:
                # 20% Data-Opacity Penalty when regulatory stream is unpopulated
                return AgentExecutionPayload(
                    agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
                    directional_bias=DirectionalBias.NEUTRAL, confidence_score=50.0, spot_price=spot,
                    metrics={"insider_net_shares": 0, "purchase_count": 0, "sale_count": 0, "regulatory_state": RegulatoryState.INSIDER_BLINDSPOT.value}
                )

            # Standardize column naming across yfinance schemas
            df = df_insiders.copy()
            text_col = "Text" if "Text" in df.columns else "Transaction" if "Transaction" in df.columns else ""
            shares_col = "Shares" if "Shares" in df.columns else "Value" if "Value" in df.columns else ""

            purchases, sales, net_shares = 0, 0, 0
            for _, row in df.head(15).iterrows():
                tx_type = str(row.get(text_col, "")).lower()
                raw_shares = row.get(shares_col, 0)
                try:
                    sh = int(raw_shares) if pd.notna(raw_shares) else 0
                except (ValueError, TypeError):
                    sh = 0
                if "purchase" in tx_type or "buy" in tx_type:
                    purchases += 1
                    net_shares += sh
                elif "sale" in tx_type or "sell" in tx_type:
                    sales += 1
                    net_shares -= sh

            # State & Bias Mapping
            if purchases > sales and net_shares > 0:
                state = RegulatoryState.INSIDER_ACCUMULATION
                bias = DirectionalBias.BULLISH
                conf = 85.0 if purchases >= 3 else 75.0
            elif sales > purchases and net_shares < 0:
                state = RegulatoryState.INSIDER_DISTRIBUTION
                bias = DirectionalBias.BEARISH
                conf = 80.0 if sales >= 3 else 70.0
            else:
                state = RegulatoryState.CLEAN_NEUTRAL
                bias = DirectionalBias.NEUTRAL
                conf = 65.0

            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
                directional_bias=bias, confidence_score=conf, spot_price=spot,
                metrics={
                    "insider_net_shares": net_shares,
                    "purchase_count": purchases,
                    "sale_count": sales,
                    "regulatory_state": state.value
                }
            )
        except Exception as e:
            logger.error(f"Agent 13 exception on {clean_ticker}: {e}")
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=str(e)
            )

    @classmethod
    def evaluate(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.evaluate_insiders(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 13: SEC Watchdog CLI")
    parser.add_argument("--ticker", required=True, help="Ticker to evaluate")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = SECWatchdogAgent.evaluate(args.ticker)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<6} | Purchases: {m['purchase_count']} | Sales: {m['sale_count']} | Net Shares: {m['insider_net_shares']:+d} | State: {m['regulatory_state']} | Bias: {payload.directional_bias.value}")
