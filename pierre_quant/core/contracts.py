"""
Pierre Quant Core: Canonical Data Contracts & Discrete Exceptions
==================================================================
Strictly-typed dataclass contracts and discrete exceptions for all 16 Sentry nodes,
Division III predictive engines (TimesFM on cuda:0 and Kronos on cuda:1),
and the Lossless Claw SQLite DAG vault.
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Literal

# --- CANONICAL SCALAR & DISCRETE LITERAL TYPES ---
DirectionalBias = Literal["BULLISH", "BEARISH", "NEUTRAL"]
ConfidenceLevel = Literal["HIGH", "MEDIUM", "LOW"]
DataSourceType = Literal[
    "TRADINGVIEW_LIVE",
    "YFINANCE_LAGGING",
    "TWELVE_DATA",
    "SEC_EDGAR_RSS",
    "FRED_MACRO",
    "USASPENDING_API",
    "FINNHUB_LIVE"
]
SentryNodeId = Literal[
    "01_jenny_xo",
    "02_risk_guard",
    "03_spending_miner",
    "04_vault_custodian",
    "05_api_ingestion",
    "06_timesfm_engine",
    "06b_kronos_engine",
    "07_stat_invariance",
    "08_momentum_vector",
    "09_visual_sentry",
    "10_smart_money",
    "11_timeframe_matrix",
    "12_corporate_fundamental",
    "13_sec_watchdog",
    "14_sector_rotation",
    "15_macro_tracker",
    "16_sentiment_harvester"
]
AgentIdentifier = Literal["06_timesfm_engine", "06b_kronos_engine"]


# --- DISCRETE CUSTOM DOMAIN EXCEPTIONS (NO SILENT SWALLOWING) ---
class PierreQuantError(Exception):
    """Root domain exception for Pierre Quant framework."""
    pass


class QuantSystemError(PierreQuantError):
    """Raised when quantitative pipeline or live price ingestion fails."""
    pass


class InstitutionalBlindspotError(PierreQuantError):
    """Raised when institutional metrics or SEC Form 4 clusters are missing/tampered."""
    def __init__(self, agent_id: str, missing_metric: str, details: Optional[str] = None) -> None:
        self.agent_id: str = agent_id
        self.missing_metric: str = missing_metric
        self.details: str = details or "Missing institutional data point triggering opacity penalty"
        super().__init__(f"[{agent_id}] Institutional Blindspot on '{missing_metric}': {self.details}")


class PredictorInferenceError(PierreQuantError):
    """Raised when tensor transformation or model forward pass fails."""
    def __init__(self, agent_id: AgentIdentifier, message: str) -> None:
        self.agent_id: AgentIdentifier = agent_id
        self.message: str = message
        super().__init__(f"[{agent_id}] Inference Failure: {message}")


class InsufficientDataError(PierreQuantError):
    """Raised when price series length is below minimum required context length."""
    def __init__(self, agent_id: str, available_bars: int, required_bars: int) -> None:
        self.agent_id: str = agent_id
        self.available_bars: int = available_bars
        self.required_bars: int = required_bars
        super().__init__(
            f"[{agent_id}] Insufficient historical data: got {available_bars} bars, required minimum {required_bars} bars."
        )


class InvalidDimensionError(PierreQuantError):
    """Raised when tensor shape or array dimension mismatch occurs."""
    def __init__(self, agent_id: AgentIdentifier, expected_shape: str, actual_shape: str) -> None:
        self.agent_id: AgentIdentifier = agent_id
        self.expected_shape: str = expected_shape
        self.actual_shape: str = actual_shape
        super().__init__(
            f"[{agent_id}] Invalid Tensor Dimension: Expected {expected_shape}, got {actual_shape}."
        )


class VaultCorruptionError(PierreQuantError):
    """Raised when SQLite DAG integrity check or block hashing fails."""
    def __init__(self, message: str) -> None:
        super().__init__(f"[DAG Vault] Corruption Detected: {message}")


class DataProvenanceMismatchError(PierreQuantError):
    """Raised when HMAC signature or data feed authenticity verification fails."""
    def __init__(self, source: str, reason: str) -> None:
        super().__init__(f"[Provenance Mismatch] Source '{source}' failed verification: {reason}")


# --- CANONICAL IMMUTABLE DATA MODELS (SLOTTED & FROZEN) ---

@dataclass(frozen=True, slots=True)
class ForecastPayload:
    vector: List[float]
    horizon_bars: int
    target_price: float
    expected_delta_pct: float


@dataclass(frozen=True, slots=True)
class SubAgentForecastReport:
    agent_id: AgentIdentifier
    ticker: str
    last_close: float
    forecast: ForecastPayload
    directional_bias: DirectionalBias
    confidence_level: ConfidenceLevel


@dataclass(frozen=True, slots=True)
class LiveQuotePayload:
    ticker: str
    current_price: float
    timestamp_utc: str
    source: Literal["YFINANCE", "TWELVE_DATA", "FINNHUB"]


@dataclass(frozen=True, slots=True)
class PriceVerificationPayload:
    ticker: str
    primary_price: float
    secondary_price: float
    verified_live_price: float
    injected_spot: Optional[float]
    drift_pct: float
    divergence_pct: float
    dual_node_signed: bool
    is_drift_critical: bool
    source_flag: str
    timestamp_utc: str


@dataclass(frozen=True, slots=True)
class TradingViewWebhookPayload:
    ticker: str
    close_price: float
    timestamp: float = 0.0
    volume: float = 100000.0
    strategy_signal: str = "BUY"


@dataclass(frozen=True, slots=True)
class AllocationTarget:
    ticker: str
    current_price: float
    current_shares: int
    current_value: float
    current_weight: float
    target_weight: float
    target_value: float
    delta_value: float
    action: Literal["BUY", "SELL", "HOLD"]
    delta_shares: int


@dataclass(frozen=True, slots=True)
class PortfolioRebalanceReport:
    total_portfolio_value: float
    cash_balance: float
    allocations: List[AllocationTarget]
    condensed_markdown: str


# --- SENTRY NODE 01 TO 16 PAYLOAD CONTRACTS ---

@dataclass(frozen=True, slots=True)
class Node01JennyXOPayload:
    agent_id: Literal["01_jenny_xo"]
    ticker: str
    orchestration_status: str
    active_sentry_count: int
    global_conviction_score: float


@dataclass(frozen=True, slots=True)
class Node02RiskGuardPayload:
    agent_id: Literal["02_risk_guard"]
    ticker: str
    covariance_risk_score: float
    bubble_state: str
    max_drawdown_tolerance_pct: float
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node03SpendingMinerPayload:
    agent_id: Literal["03_spending_miner"]
    ticker: str
    gov_contract_flow_usd: float
    agency_recipient: str
    award_count_90d: int
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node04VaultCustodianPayload:
    agent_id: Literal["04_vault_custodian"]
    ticker: str
    dag_block_height: int
    total_matrices_cached: int
    is_vault_synchronized: bool


@dataclass(frozen=True, slots=True)
class Node05ApiIngestionPayload:
    agent_id: Literal["05_api_ingestion"]
    ticker: str
    feed_source: DataSourceType
    latency_ms: float
    bars_ingested: int


@dataclass(frozen=True, slots=True)
class Node06TimesFMPayload:
    agent_id: Literal["06_timesfm_engine"]
    ticker: str
    device: Literal["cuda:0"]
    report: SubAgentForecastReport


@dataclass(frozen=True, slots=True)
class Node06bKronosPayload:
    agent_id: Literal["06b_kronos_engine"]
    ticker: str
    device: Literal["cuda:1"]
    report: SubAgentForecastReport


@dataclass(frozen=True, slots=True)
class Node07StatInvariancePayload:
    agent_id: Literal["07_stat_invariance"]
    ticker: str
    monte_carlo_var_95: float
    kurtosis_z_score: float
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node08MomentumVectorPayload:
    agent_id: Literal["08_momentum_vector"]
    ticker: str
    rsi_14: float
    atr_14: float
    macd_delta: float
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node09VisualSentryPayload:
    agent_id: Literal["09_visual_sentry"]
    ticker: str
    pattern_label: str
    support_level: float
    resistance_level: float
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node10SmartMoneyPayload:
    agent_id: Literal["10_smart_money"]
    ticker: str
    dark_pool_volume_pct: float
    institutional_block_bias: DirectionalBias
    whale_accumulation_flag: bool


@dataclass(frozen=True, slots=True)
class Node11TimeframeMatrixPayload:
    agent_id: Literal["11_timeframe_matrix"]
    ticker: str
    daily_bias: DirectionalBias
    hourly_bias: DirectionalBias
    m15_bias: DirectionalBias
    is_timeframe_aligned: bool


@dataclass(frozen=True, slots=True)
class Node12CorporateFundamentalPayload:
    agent_id: Literal["12_corporate_fundamental"]
    ticker: str
    pe_ratio: float
    free_cash_flow_yield_pct: float
    revenue_growth_yoy_pct: float
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node13SecWatchdogPayload:
    agent_id: Literal["13_sec_watchdog"]
    ticker: str
    form_type: str
    insider_shares_traded: int
    net_insider_flow_usd: float
    is_executive_cluster_buy: bool
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node14SectorRotationPayload:
    agent_id: Literal["14_sector_rotation"]
    ticker: str
    sector: str
    mansfield_relative_strength: float
    sector_flow_rank: int
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node15MacroTrackerPayload:
    agent_id: Literal["15_macro_tracker"]
    ticker: str
    us10y_yield_pct: float
    dxy_index: float
    macro_regime: str
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class Node16SentimentHarvesterPayload:
    agent_id: Literal["16_sentiment_harvester"]
    ticker: str
    social_sentiment_z_score: float
    news_velocity: float
    directional_bias: DirectionalBias


@dataclass(frozen=True, slots=True)
class SupervisorDossier:
    ticker: str
    timestamp_utc: str
    last_close: float
    timesfm_report: SubAgentForecastReport
    kronos_report: SubAgentForecastReport
    cross_model_alignment: bool
    target_spread_delta_pct: float
    final_conviction_score: float
    data_source: DataSourceType
    condensed_markdown: str


# --- CONDENSED FORMATTERS ---

def format_condensed_forecast_markdown(report: SubAgentForecastReport) -> str:
    """Renders SubAgentForecastReport into condensed Markdown format to eliminate token bloat."""
    delta_sign: str = "+" if report.forecast.expected_delta_pct >= 0 else ""
    vector_preview: str = ", ".join(f"{p:.2f}" for p in report.forecast.vector[:4])
    if len(report.forecast.vector) > 4:
        vector_preview += f", ... [{len(report.forecast.vector)} bars total]"

    lines: List[str] = [
        f"### {report.agent_id.upper()} FORECAST :: ${report.ticker.upper()}",
        f"- **Bias**: `{report.directional_bias}` | **Confidence**: `{report.confidence_level}`",
        f"- **Last Close**: `${report.last_close:,.2f}` -> **Target ({report.forecast.horizon_bars}b)**: `${report.forecast.target_price:,.2f}` ({delta_sign}{report.forecast.expected_delta_pct:.2f}%)",
        f"- **Trajectory Vector**: `[{vector_preview}]`",
    ]
    return "\n".join(lines)
