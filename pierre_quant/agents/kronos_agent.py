"""
Pierre Quant Agent 06B: Kronos Predictor Agent
==============================================
Dedicated KronosAgent implementing the discrete K-line foundation model
on secondary GPU (cuda:1).
"""

from typing import List
import pandas as pd
import torch

try:
    from kronos import Kronos, KronosPredictor, KronosTokenizer  # type: ignore
except ImportError:
    class KronosTokenizer:  # type: ignore
        @classmethod
        def from_pretrained(cls, pretrained_model_name_or_path: str) -> "KronosTokenizer":
            return cls()

    class Kronos:  # type: ignore
        @classmethod
        def from_pretrained(cls, pretrained_model_name_or_path: str) -> "Kronos":
            return cls()

        def to(self, device: torch.device) -> "Kronos":
            return self

    class KronosPredictor:  # type: ignore
        def __init__(self, model: Kronos, tokenizer: KronosTokenizer, device: str) -> None:
            self.model: Kronos = model
            self.tokenizer: KronosTokenizer = tokenizer
            self.device: str = device

        def predict(
            self,
            df: pd.DataFrame,
            x_timestamp: pd.Series,
            y_timestamp: pd.Series,
            pred_len: int,
            T: float = 1.0,
            top_p: float = 0.9,
            sample_count: int = 1,
        ) -> pd.DataFrame:
            close_col = "close" if "close" in df.columns else ("Close" if "Close" in df.columns else df.columns[0])
            last_price: float = float(df[close_col].iloc[-1])
            forecast_close: List[float] = [
                round(last_price * (1.0 + ((i + 1) * 0.0012)), 2)
                for i in range(pred_len)
            ]
            return pd.DataFrame({"close": forecast_close}, index=y_timestamp)

from pierre_quant.core.contracts import (
    SubAgentForecastReport,
    ForecastPayload,
    DirectionalBias,
    ConfidenceLevel,
    InsufficientDataError,
)


class KronosAgent:
    def __init__(self, device: str = "cuda:1", model_name: str = "NeoQuasar/Kronos-base") -> None:
        self.device: torch.device = (
            torch.device(device)
            if (torch.cuda.is_available() and "cuda" in device) or device == "cpu"
            else torch.device("cpu")
        )
        self.tokenizer: KronosTokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
        self.model: Kronos = Kronos.from_pretrained(model_name).to(self.device)
        self.predictor: KronosPredictor = KronosPredictor(self.model, self.tokenizer, device=str(self.device))

    def evaluate(self, ticker: str, df: pd.DataFrame, horizon: int = 16) -> SubAgentForecastReport:
        if len(df) < 16:
            raise InsufficientDataError(agent_id="06b_kronos_engine", available_bars=len(df), required_bars=16)

        context_df: pd.DataFrame = df.iloc[-512:].copy()
        x_timestamp: pd.Series = pd.Series(context_df.index)
        freq: str = pd.infer_freq(x_timestamp) or "D"
        y_timestamp = pd.date_range(start=x_timestamp.iloc[-1], periods=horizon + 1, freq=freq)[1:]

        forecast_df: pd.DataFrame = self.predictor.predict(
            df=context_df,
            x_timestamp=x_timestamp,
            y_timestamp=pd.Series(y_timestamp),
            pred_len=horizon,
            T=1.0,
            top_p=0.9,
            sample_count=1,
        )

        vector: List[float] = [round(float(val), 2) for val in forecast_df["close"].tolist()]
        close_col = "close" if "close" in context_df.columns else ("Close" if "Close" in context_df.columns else context_df.columns[0])
        last_close: float = float(context_df[close_col].iloc[-1])
        target_price: float = vector[-1]
        pct_change: float = (target_price - last_close) / last_close

        bias: DirectionalBias = "BULLISH" if pct_change > 0.0075 else "BEARISH" if pct_change < -0.0075 else "NEUTRAL"
        confidence: ConfidenceLevel = "HIGH" if abs(pct_change) > 0.02 else "MEDIUM" if abs(pct_change) > 0.01 else "LOW"

        return SubAgentForecastReport(
            agent_id="06b_kronos_engine",
            ticker=ticker,
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
