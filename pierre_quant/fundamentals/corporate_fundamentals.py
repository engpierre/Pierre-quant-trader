"""
pierre_quant/fundamentals/corporate_fundamentals.py
Agent 12 (Corporate Fundamentals Worker) - Valuation Multiples & Solvency Health Engine.
"""
from __future__ import annotations
import argparse
import json
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional
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
logger = logging.getLogger("Agent12_Fundamentals")

class FundamentalState(str, Enum):
    UNDERVALUED_QUALITY = "UNDERVALUED_QUALITY"
    FAIR_VALUE = "FAIR_VALUE"
    OVERVALUED_EXPENSIVE = "OVERVALUED_EXPENSIVE"
    BALANCE_SHEET_DISTRESS = "BALANCE_SHEET_DISTRESS"

class CorporateFundamentalsAgent:
    AGENT_ID = "12_corporate_fundamentals"

    @classmethod
    def evaluate_fundamentals(cls, ticker: str) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        try:
            t = yf.Ticker(clean_ticker)
            info = t.info or {}
            fast_info = getattr(t, "fast_info", {})

            spot = float(fast_info.get("lastPrice") or info.get("currentPrice") or info.get("regularMarketPrice") or 0.0)
            if spot <= 0.0:
                return AgentExecutionPayload(
                    agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                    error_message=f"Zero/invalid spot price resolved for {clean_ticker}"
                )

            trailing_pe = float(info.get("trailingPE") or 0.0)
            forward_pe = float(info.get("forwardPE") or 0.0)
            price_to_book = float(info.get("priceToBook") or 0.0)
            debt_to_equity = float(info.get("debtToEquity") or 0.0)
            fcf = float(info.get("freeCashflow") or 0.0)
            market_cap = float(fast_info.get("marketCap") or info.get("marketCap") or 1.0)

            fcf_yield = (fcf / market_cap) * 100.0 if market_cap > 0 else 0.0

            # Solvency & Multiple Evaluation
            is_distressed = debt_to_equity > 250.0 and fcf_yield < -5.0
            is_undervalued = (0 < trailing_pe < 20.0 or 0 < forward_pe < 15.0) and fcf_yield > 4.0
            is_expensive = (trailing_pe > 50.0 or forward_pe > 40.0) and fcf_yield < 1.0

            if is_distressed:
                state = FundamentalState.BALANCE_SHEET_DISTRESS
                bias = DirectionalBias.BEARISH
                conf = 85.0
            elif is_undervalued:
                state = FundamentalState.UNDERVALUED_QUALITY
                bias = DirectionalBias.BULLISH
                conf = 80.0
            elif is_expensive:
                state = FundamentalState.OVERVALUED_EXPENSIVE
                bias = DirectionalBias.BEARISH
                conf = 70.0
            else:
                state = FundamentalState.FAIR_VALUE
                bias = DirectionalBias.NEUTRAL
                conf = 65.0

            # Data opacity penalty: haircut 20% if P/E and FCF are unpopulated
            if trailing_pe == 0.0 and fcf == 0.0:
                conf = max(40.0, conf - 20.0)

            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.SUCCESS,
                directional_bias=bias, confidence_score=conf, spot_price=spot,
                metrics={
                    "trailing_pe": round(trailing_pe, 2),
                    "forward_pe": round(forward_pe, 2),
                    "price_to_book": round(price_to_book, 2),
                    "debt_to_equity": round(debt_to_equity, 2),
                    "fcf_yield_pct": round(fcf_yield, 2),
                    "fundamental_state": state.value
                }
            )
        except Exception as e:
            logger.error(f"Agent 12 resolution exception on {clean_ticker}: {e}")
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID, ticker=clean_ticker, status=ExecutionStatus.FAILED,
                error_message=str(e)
            )

    @classmethod
    def evaluate(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        return cls.evaluate_fundamentals(ticker, **kwargs)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Agent 12: Corporate Fundamentals Worker CLI")
    parser.add_argument("--ticker", required=True, help="Holding symbol to evaluate")
    parser.add_argument("--json", action="store_true", help="Output pure JSON")
    args = parser.parse_args()

    payload = CorporateFundamentalsAgent.evaluate(args.ticker)
    if args.json:
        print(json.dumps({
            "agent_id": payload.agent_id, "ticker": payload.ticker, "status": payload.status.value,
            "directional_bias": payload.directional_bias.value, "confidence_score": payload.confidence_score,
            "spot_price": payload.spot_price, "metrics": payload.metrics, "error_message": payload.error_message
        }))
    else:
        m = payload.metrics
        print(f"Holding: {payload.ticker:<6} | Spot: ${payload.spot_price:<8.2f} | P/E: {m['trailing_pe']:<6.1f} | D/E: {m['debt_to_equity']:<6.1f} | FCF Yield: {m['fcf_yield_pct']:<+5.1f}% | State: {m['fundamental_state']} | Bias: {payload.directional_bias.value}")
