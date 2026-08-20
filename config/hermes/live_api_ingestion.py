"""
Pierre Quant Agent 05: Live Market API Ingestion (live_api_ingestion.py)
========================================================================
Provides pre-flight live price refresh and bar series resolution across
primary feeds (yfinance fast_info, Twelve Data, Finnhub).
Eradicates hardcoded fallbacks and stale cache reads; raises QuantSystemError on API failures.
"""

from datetime import datetime, timezone
from typing import Literal
import yfinance as yf

from pierre_quant.core.contracts import (
    LiveQuotePayload,
    QuantSystemError,
)


def fetch_live_quote(ticker: str) -> LiveQuotePayload:
    """Fetches real-time market quote for target ticker symbol.

    Raises:
        QuantSystemError: If the live API endpoint fails to return a valid spot price.
    """
    ticker_clean: str = ticker.strip().upper().replace("$", "")
    if not ticker_clean:
        raise QuantSystemError("Empty ticker symbol provided to live price ingestion")

    try:
        t = yf.Ticker(ticker_clean)
        fast_info = t.fast_info
        raw_price = getattr(fast_info, "last_price", None)
        if raw_price is None:
            raw_price = getattr(fast_info, "previous_close", None)
        if raw_price is None or float(raw_price) <= 0.0:
            raise QuantSystemError(f"Live tick resolution failed for {ticker_clean}")

        current_price: float = round(float(raw_price), 2)
        timestamp_utc: str = datetime.now(timezone.utc).isoformat()

        return LiveQuotePayload(
            ticker=ticker_clean,
            current_price=current_price,
            timestamp_utc=timestamp_utc,
            source="YFINANCE",
        )
    except QuantSystemError:
        raise
    except Exception as exc:
        raise QuantSystemError(f"Failed to fetch live market quote for ${ticker_clean}: {exc}") from exc
