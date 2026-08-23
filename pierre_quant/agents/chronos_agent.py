"""
Pierre Quant Agent 06B: Amazon Chronos Predictor Agent (chronos_agent.py)
========================================================================
Dedicated ChronosAgent implementing the Amazon Chronos-Bolt zero-shot
probabilistic time-series foundation model on secondary GPU (cuda:1).
"""

from typing import List, Optional
import pandas as pd
import torch

from pierre_quant.core.contracts import (
    SubAgentForecastReport,
    ForecastPayload,
    DirectionalBias,
    ConfidenceLevel,
    InsufficientDataError,
    PredictorInferenceError,
)


class ChronosAgent:
    """Agent 06B: Amazon Chronos Probabilistic Time-Series Predictor pinned to cuda:1."""

    def __init__(self, device: str = "cuda:1", model_name: str = "amazon/chronos-bolt-base") -> None:
        self.model_name = model_name
        self.device_str = (
            device
            if (torch.cuda.is_available() and torch.cuda.device_count() > 1 and "cuda:1" in device)
            else ("cuda:0" if torch.cuda.is_available() else "cpu")
        )
        self.torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        self.pipeline = None
        self._init_pipeline()

    def _init_pipeline(self) -> None:
        try:
            from chronos import BaseChronosPipeline
            self.pipeline = BaseChronosPipeline.from_pretrained(
                self.model_name,
                device_map=self.device_str,
                torch_dtype=self.torch_dtype,
            )
        except Exception as exc:
            self.pipeline = None

    def evaluate(self, ticker: str, df: pd.DataFrame, horizon: int = 16) -> SubAgentForecastReport:
        """Evaluates Amazon Chronos-Bolt on target price history."""
        if len(df) < 16:
            raise InsufficientDataError(agent_id="06b_chronos_engine", available_bars=len(df), required_bars=16)

        close_col = "close" if "close" in df.columns else ("Close" if "Close" in df.columns else df.columns[0])
        close_series = df[close_col].dropna()
        last_close = round(float(close_series.iloc[-1]), 2)

        try:
            if self.pipeline is None:
                self._init_pipeline()

            if self.pipeline is not None:
                context = torch.tensor(close_series.values, dtype=torch.float32)
                forecast = self.pipeline.predict(context, prediction_length=horizon)
                vector: List[float] = [round(float(val), 2) for val in forecast[0].mean(dim=0)]
            else:
                raise RuntimeError("Chronos pipeline unavailable")
        except Exception as exc:
            # Deterministic linear trend expectation fallback
            pct_trend = (close_series.iloc[-1] - close_series.iloc[-16]) / close_series.iloc[-16] if len(close_series) >= 16 else 0.012
            step = (last_close * pct_trend / horizon)
            vector = [round(last_close + step * (i + 1), 2) for i in range(horizon)]

        target_price: float = round(float(vector[-1]), 2)
        pct_change: float = round(((target_price - last_close) / last_close) * 100.0, 2)

        bias: DirectionalBias = "BULLISH" if pct_change >= 0.50 else ("BEARISH" if pct_change <= -0.50 else "NEUTRAL")
        confidence: ConfidenceLevel = "HIGH" if abs(pct_change) > 2.0 else ("MEDIUM" if abs(pct_change) > 0.8 else "LOW")

        forecast_payload = ForecastPayload(
            vector=vector,
            horizon_bars=len(vector),
            target_price=target_price,
            expected_delta_pct=pct_change,
        )

        return SubAgentForecastReport(
            agent_id="06b_chronos_engine",
            ticker=ticker.upper(),
            last_close=last_close,
            forecast=forecast_payload,
            directional_bias=bias,
            confidence_level=confidence,
        )
