"""
pierre_quant/ingestion/live_feed.py
Agent 05 (Live Ingestion Layer) - Deterministic Market Data Pipe with Resilient Aliasing.
"""
from __future__ import annotations
import logging
import re
from datetime import datetime
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
import yfinance as yf
from pierre_quant.core.agent_contract import (
    AgentExecutionPayload, CandleData, DirectionalBias, ExecutionStatus
)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("Agent05_LiveFeed")

TICKER_REGEX = re.compile(r"^[A-Z0-9.\-=]{1,10}$")

class LiveFeedIngestionAgent:
    """Agent 05: Deterministic market feed provider with strict validation and shorthand aliases."""
    
    AGENT_ID = "05_live_api_ingestion"

    @classmethod
    def validate_symbol(cls, symbol: str) -> bool:
        if not symbol or not isinstance(symbol, str):
            return False
        clean_symbol = symbol.strip().upper()
        if clean_symbol.startswith("/") or clean_symbol.startswith("\\"):
            return False
        return bool(TICKER_REGEX.match(clean_symbol))

    @classmethod
    def fetch_spot_and_candles(
        cls, 
        ticker: str, 
        period: str = "3mo", 
        interval: str = "1d"
    ) -> AgentExecutionPayload:
        clean_ticker = ticker.strip().upper().lstrip("$")
        
        if not cls.validate_symbol(clean_ticker):
            logger.warning(f"Agent 05 rejected invalid ticker input: '{ticker}'")
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.REJECTED,
                error_message=f"Input '{ticker}' failed symbol validation whitelist."
            )

        try:
            # 1. Fast Info Ingestion
            t_obj = yf.Ticker(clean_ticker)
            spot = t_obj.fast_info.get("lastPrice", None)
            
            # 2. Historical Candle Resolution
            df = t_obj.history(period=period, interval=interval, auto_adjust=True)
            
            if df.empty:
                df = yf.download(clean_ticker, period=period, interval=interval, progress=False, auto_adjust=True)
            
            if df.empty:
                return AgentExecutionPayload(
                    agent_id=cls.AGENT_ID,
                    ticker=clean_ticker,
                    status=ExecutionStatus.FAILED,
                    error_message=f"No market data returned for symbol '{clean_ticker}'."
                )

            df = df.dropna()
            if spot is None or np.isnan(spot):
                spot = float(df["Close"].iloc[-1])

            candles = [
                CandleData(
                    timestamp=idx.isoformat(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"])
                )
                for idx, row in df.iterrows()
            ]

            sma20 = float(df["Close"].rolling(20).mean().iloc[-1]) if len(df) >= 20 else spot
            bias = DirectionalBias.BULLISH if spot >= sma20 else DirectionalBias.BEARISH

            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.SUCCESS,
                directional_bias=bias,
                confidence_score=95.0,
                spot_price=round(float(spot), 4),
                metrics={
                    "sma20": round(sma20, 4),
                    "bars_loaded": len(candles),
                    "last_timestamp": candles[-1].timestamp if candles else ""
                },
                candles=candles
            )

        except Exception as e:
            logger.error(f"Agent 05 execution error on {clean_ticker}: {e}")
            return AgentExecutionPayload(
                agent_id=cls.AGENT_ID,
                ticker=clean_ticker,
                status=ExecutionStatus.FAILED,
                error_message=str(e)
            )

    # Standardized Resilient Aliases
    @classmethod
    def fetch(cls, ticker: str, **kwargs) -> AgentExecutionPayload:
        """Convenience alias mapping directly to fetch_spot_and_candles."""
        return cls.fetch_spot_and_candles(ticker, **kwargs)

    @classmethod
    def get_spot(cls, ticker: str) -> float:
        """Single-tick price lookup returning raw float."""
        payload = cls.fetch_spot_and_candles(ticker, period="5d", interval="1d")
        return payload.spot_price if payload.status == ExecutionStatus.SUCCESS else 0.0

    @classmethod
    def get_quote(cls, ticker: str) -> float:
        """Shorthand alias for get_spot."""
        return cls.get_spot(ticker)
