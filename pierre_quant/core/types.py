"""
Pierre Quant Core: Compatibility Type Layer
============================================
Re-exports canonical slotted frozen contracts from contracts.py for backwards compatibility.
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Union, List, Literal

from pierre_quant.core.contracts import (
    DirectionalBias,
    ConfidenceLevel,
    DataSourceType,
    PierreQuantError,
    InstitutionalBlindspotError,
    PredictorInferenceError,
    InsufficientDataError,
    InvalidDimensionError,
    VaultCorruptionError,
    DataProvenanceMismatchError,
    TradingViewWebhookPayload,
    ForecastPayload,
    SubAgentForecastReport,
    SupervisorDossier,
)


@dataclass(slots=True)
class BaseAgentPayload:
    """Base schema for sub-agent payloads."""
    agent_id: str
    ticker: str = "NVDA"
    timestamp: float = field(default_factory=time.time)
    institutional_blindspot: bool = False
    blindspot_reason: Optional[str] = None
    base_confidence_score: float = 1.0
    adjusted_confidence_score: float = 1.0

    def apply_opacity_penalty(self) -> float:
        """Enforces a 20% data-opacity penalty if an institutional blindspot occurs."""
        if self.institutional_blindspot:
            self.adjusted_confidence_score = max(0.0, self.base_confidence_score - 0.20)
        else:
            self.adjusted_confidence_score = self.base_confidence_score
        return self.adjusted_confidence_score


@dataclass(slots=True)
class Agent13RegulatoryWatchdogPayload(BaseAgentPayload):
    agent_id: str = "13_regulatory_watchdog"
    data_source: DataSourceType = "SEC_EDGAR_RSS"
    directional_bias: DirectionalBias = "NEUTRAL"
    confidence_level: ConfidenceLevel = "HIGH"
    raw_confidence_score: float = 0.90
    form_type: str = "Form 4"
    insider_shares_traded: int = 0
    net_insider_flow_usd: float = 0.0
    is_executive_buy: bool = False


@dataclass(slots=True)
class Agent06TimesFMPredictorPayload(BaseAgentPayload):
    agent_id: str = "06_timesfm_predictor"
    data_source: DataSourceType = "TRADINGVIEW_LIVE"
    directional_bias: DirectionalBias = "NEUTRAL"
    confidence_level: ConfidenceLevel = "HIGH"
    raw_confidence_score: float = 0.95
    context_len: int = 128
    horizon_bars: int = 16
    mean_expectation_vector: List[float] = field(default_factory=list)
    upper_bound_vector: List[float] = field(default_factory=list)
    lower_bound_vector: List[float] = field(default_factory=list)


__all__ = [
    "DirectionalBias",
    "ConfidenceLevel",
    "DataSourceType",
    "PierreQuantError",
    "InstitutionalBlindspotError",
    "PredictorInferenceError",
    "InsufficientDataError",
    "InvalidDimensionError",
    "VaultCorruptionError",
    "DataProvenanceMismatchError",
    "TradingViewWebhookPayload",
    "BaseAgentPayload",
    "Agent13RegulatoryWatchdogPayload",
    "Agent06TimesFMPredictorPayload",
    "ForecastPayload",
    "SubAgentForecastReport",
    "SupervisorDossier",
]
