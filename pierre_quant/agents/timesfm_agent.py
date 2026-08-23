"""
Pierre Quant Agent 06: Google TimesFM Agent
===========================================
Dedicated TimesFMAgent implementing zero-shot time-series forecasting
on primary GPU (cuda:0).
"""

from typing import List
import pandas as pd
import torch

from pierre_quant.core.contracts import (
    SubAgentForecastReport,
    ForecastPayload,
    DirectionalBias,
    ConfidenceLevel,
    InsufficientDataError,
)
from pierre_quant.predictors.timesfm_predictor import TimesFMModelWrapper


class TimesFMAgent:
    def __init__(self, device: str = "cuda:0", model_name: str = "google/timesfm-2.5-200m-pytorch") -> None:
        self.device: torch.device = (
            torch.device(device)
            if (torch.cuda.is_available() and "cuda" in device) or device == "cpu"
            else torch.device("cpu")
        )
        self.model_name: str = model_name
        self.model = TimesFMModelWrapper()

    def evaluate(self, ticker: str, df: pd.DataFrame, horizon: int = 16) -> SubAgentForecastReport:
        if len(df) < 16:
            raise InsufficientDataError(agent_id="06_timesfm_engine", available_bars=len(df), required_bars=16)

        close_col = "close" if "close" in df.columns else ("Close" if "Close" in df.columns else df.columns[0])
        price_series: List[float] = [float(p) for p in df[close_col].tolist()]
        
        mean_vec, _, _ = self.model.predict(price_series)
        vector: List[float] = [round(float(val), 2) for val in mean_vec[:horizon]]
        last_close: float = round(float(price_series[-1]), 2)
        target_price: float = vector[-1]
        pct_change: float = (target_price - last_close) / last_close

        bias: DirectionalBias = "BULLISH" if pct_change >= 0.005 else "BEARISH" if pct_change <= -0.005 else "NEUTRAL"
        confidence: ConfidenceLevel = "HIGH" if abs(pct_change) > 0.015 else "MEDIUM" if abs(pct_change) > 0.005 else "LOW"

        return SubAgentForecastReport(
            agent_id="06_timesfm_engine",
            ticker=ticker.upper(),
            last_close=last_close,
            forecast=ForecastPayload(
                vector=vector,
                horizon_bars=horizon,
                target_price=target_price,
                expected_delta_pct=round(pct_change * 100, 2),
            ),
            directional_bias=bias,
            confidence_level=confidence,
        )
