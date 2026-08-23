"""
Pierre Quant Predictive Dispatcher Runner
=========================================
Concurrent execution engine for Division III dual-model forecasting
(TimesFM 06 on cuda:0 and Kronos 06B on cuda:1).
"""

import asyncio
from typing import Tuple, Dict, Any, Optional
import pandas as pd

from pierre_quant.core.contracts import (
    SubAgentForecastReport,
    PriceVerificationPayload,
    InsufficientDataError,
    PredictorInferenceError,
)
from pierre_quant.agents.timesfm_agent import TimesFMAgent
from pierre_quant.agents.chronos_agent import ChronosAgent
from pierre_quant.supervisor.synthesizer import generate_recon_markdown


class PredictiveDispatcher:
    """Orchestrates concurrent dual-model inference: TimesFM (cuda:0) and Amazon Chronos-Bolt (cuda:1)."""

    def __init__(self, timesfm_device: str = "cuda:0", chronos_device: str = "cuda:1") -> None:
        self.agent_timesfm: TimesFMAgent = TimesFMAgent(device=timesfm_device)
        self.agent_chronos: ChronosAgent = ChronosAgent(device=chronos_device)

    async def execute_dual_forecast(
        self,
        ticker: str,
        df: pd.DataFrame,
        horizon: int = 16,
    ) -> Tuple[SubAgentForecastReport, SubAgentForecastReport]:
        """Concurrently evaluates Google TimesFM and Amazon Chronos-Bolt models on target asset."""
        if len(df) < 16:
            raise InsufficientDataError(
                agent_id="06_timesfm_engine",
                available_bars=len(df),
                required_bars=16,
            )

        loop = asyncio.get_running_loop()
        timesfm_task = loop.run_in_executor(None, self.agent_timesfm.evaluate, ticker, df, horizon)
        chronos_task = loop.run_in_executor(None, self.agent_chronos.evaluate, ticker, df, horizon)

        timesfm_report, chronos_report = await asyncio.gather(timesfm_task, chronos_task)
        return timesfm_report, chronos_report


_global_dispatcher: Optional[PredictiveDispatcher] = None


def get_predictive_dispatcher() -> PredictiveDispatcher:
    """Returns or lazily initializes the singleton PredictiveDispatcher."""
    global _global_dispatcher
    if _global_dispatcher is None:
        _global_dispatcher = PredictiveDispatcher(timesfm_device="cuda:0", chronos_device="cuda:1")
    return _global_dispatcher


async def execute_dual_forecast(
    ticker: str,
    df: pd.DataFrame,
    horizon: int = 16,
) -> Tuple[SubAgentForecastReport, SubAgentForecastReport]:
    """Module-level helper to execute dual forecast via singleton dispatcher."""
    dispatcher = get_predictive_dispatcher()
    return await dispatcher.execute_dual_forecast(ticker, df, horizon)


def build_sentry_dossier(
    ticker: str,
    price: float,
    recon_res: Dict[str, Any],
    timesfm_report: Optional[SubAgentForecastReport] = None,
    kronos_report: Optional[SubAgentForecastReport] = None,
    source: str = "TRADINGVIEW_LIVE",
    verification: Optional[PriceVerificationPayload] = None,
    atr: float = 0.45,
    sigma: float = 1.45,
) -> str:
    """Builds the comprehensive 5-section Sentry Recon report."""
    return generate_recon_markdown(
        ticker=ticker,
        price=price,
        recon_res=recon_res,
        timesfm_report=timesfm_report,
        kronos_report=kronos_report,
        source=source,
        verification=verification,
        atr=atr,
        sigma=sigma,
    )
