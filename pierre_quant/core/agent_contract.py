"""
pierre_quant/core/agent_contract.py
Immutable data contracts and execution schemas for the 16 Sentry Nodes.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

class DirectionalBias(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class ExecutionStatus(str, Enum):
    SUCCESS = "SUCCESS"
    DEGRADED = "DEGRADED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"

@dataclass(slots=True, frozen=True)
class CandleData:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float

@dataclass(slots=True, frozen=True)
class AgentExecutionPayload:
    agent_id: str
    ticker: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: ExecutionStatus = ExecutionStatus.SUCCESS
    directional_bias: DirectionalBias = DirectionalBias.NEUTRAL
    confidence_score: float = 0.0
    spot_price: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    candles: List[CandleData] = field(default_factory=list)
    error_message: Optional[str] = None
