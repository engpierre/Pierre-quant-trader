# PIERRE QUANT SYSTEM ARCHITECTURE SPECIFICATION
**Version:** 3.4.0  
**Target Environment:** AMD Ryzen 9 9950X 16-Core | 64GB DDR5 | Dual NVIDIA GeForce RTX 5060 Ti (2x 16GB)  
**Operating Framework:** OpenClaw Swarm Daemon + Hermes Quantitative Agent Runtime  

---

## 1. HARDWARE COMPUTE & VRAM PARTITION MAP

```
+---------------------------------------------------------------------------------------------------+
|                                   HOST COMPUTE ARCHITECTURE                                       |
|                  AMD Ryzen 9 9950X (16C/32T) | 64GB DDR5 RAM | Windows 11 Enterprise             |
+-------------------------------------------------+-------------------------------------------------+
|              GPU 0 (cuda:0 - 16GB VRAM)         |           GPU 1 (cuda:1 - 16GB VRAM)            |
+-------------------------------------------------+-------------------------------------------------+
| • Google TimesFM 1.0 (200M Patch-based Transformer) | • Amazon Chronos-Bolt Base (T5-based Autoregressive)  |
| • PyTorch Tensor Forecasting Pipeline           | • Qwen 2.5 27B Hardened (Split Layer Execution) |
| • Context Window: 128 Bars (Daily)              | • Horizon: 16 Bars (Daily)                      |
+-------------------------------------------------+-------------------------------------------------+
|                                    CPU RUNTIME ISOLATION LAYER                                    |
| • faster-whisper (ONNX Execution Provider / CPU INT8) - Speech Ingestion (Zero GPU VRAM Impact)  |
| • Deterministic NumPy / Pandas / SciPy Vector Mathematics Engine                                  |
| • OpenClaw Gateway Daemon (Port 18789) & SQLite WAL Connection Pool                                |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. 16-NODE SENTRY SWARM TOPOLOGY & DIVISION HIERARCHY

```
                                  +---------------------------------------+
                                  |     DIVISION I: SWARM LEADERSHIP      |
                                  |  Agent 01: Master Supervisor Synth    |
                                  |  Agent 05: Live Data Ingestion Pipe   |
                                  +-------------------+-------------------+
                                                      |
         +-----------------------------+--------------+--------------+-----------------------------+
         |                             |                             |                             |
+--------v--------+           +--------v--------+           +--------v--------+           +--------v--------+
|   DIVISION II   |           |  DIVISION III   |           |   DIVISION IV   |           |   DIVISION V    |
|   RISK GUARD    |           |  PREDICTIVE &   |           |   STRUCTURAL &  |           |  FUNDAMENTALS & |
|  & EXECUTION    |           |   STATISTICS    |           |  FLOW DYNAMICS  |           |    OVERLAYS     |
+-----------------+           +-----------------+           +-----------------+           +-----------------+
| 02: Risk Guard  |           | 06a: TimesFM    |           | 09: Visual-     |           | 12: Corporate   |
| 03: Allocator   |           | 06b: Chronos    |           |     Sentry VWAP |           |     Health      |
| 04: Execution   |           | 07: Statistical |           | 10: Smart Money |           | 13: SEC Form 4  |
|     Sentry      |           |     Invariance  |           |     Volume Prof |           | 14: Sector Rot  |
|                 |           | 08: Momentum    |           | 11: Timeframe   |           | 15: Macro Matrix|
|                 |           |     Vector      |           |     Matrix      |           | 16: Sentiment   |
+-----------------+           +-----------------+           +-----------------+           +-----------------+
```

---

## 3. NODE CONTRACTS & SPECIALIST SPECIFICATIONS

### DIVISION I: LEADERSHIP & INGESTION
* **Agent 01 (Supervisor Orchestrator):** Master confluence consensus engine. Runs isolated CLI worker subprocesses across Divisions III–V, executes dual-model predictive divergence checks, applies 20% opacity haircuts and 50% retail sentiment counter-trend discounts, and emits unified `SupervisorSynthesisResult` dossiers.
* **Agent 05 (Live Ingestion Layer):** Deterministic market data pipeline. Validates ticker strings against regex `^[\^A-Z0-9.\-=]{1,12}$`, fetches fast info & OHLCV bar history, enforces dual-node corroboration, and exposes resilient aliases (`fetch`, `get_spot`, `get_quote`).

### DIVISION II: RISK, CAPITAL DEFENSE & POSITION GUARDS
* **Agent 02 (Risk & Portfolio Guard):** Monotonic volatility stop engine. Computes $1.8 \times \text{ATR}_{14}$ dynamic risk boundaries and multi-phase $\sigma$-ratchets (`BASE`, `PHASE_1_BREAKEVEN`, `PHASE_2_EXPANSION`, `PHASE_3_PROFIT_LOCK`). Strictly enforces the monotonic stop invariant:
  $$\text{Stop}_{\text{final}} = \max(\text{Stop}_{\text{current}}, \text{Stop}_{\text{proposed}})$$
* **Agent 03 (Capital Allocation Engine):** Dynamically bounds holding exposures based on volatility regime and corroboration status (Max 20% dual-verified, 10% single-node).
* **Agent 04 (Execution Sentry):** Pre-trade validation gate verifying spread limits, slippage bounds, and execution venue liquidity.

### DIVISION III: DEEP TIME-SERIES PREDICTIVE & STATISTICAL WORKERS
* **Agent 06a (Google TimesFM 1.0):** Zero-shot patch-based transformer on `cuda:0`. Enforces rigid $(1, 128)$ input padding/truncation and forecasts a 16-bar forward mean trajectory.
* **Agent 06b (Amazon Chronos-Bolt Base):** Autoregressive T5-based probabilistic forecaster on `cuda:1`. Generates a 16-bar quantile/mean trajectory vector.
* **Agent 07 (Statistical Invariance Analyst):** Computes rolling 20-bar Z-score ($Z = \frac{P - \mu_{20}}{\sigma_{20}}$), Bollinger Bands ($\pm 2.0\sigma$), and `%B` metrics. Classifies `OVERBOUGHT` ($Z \ge 2.0$), `OVERSOLD` ($Z \le -2.0$), and `FAIR_VALUE`.
* **Agent 08 (Momentum Vector Analyst):** Computes MACD (12, 26, 9), Wilder's RSI (14), and ROC-10. Maps `VelocityState` into `ACCELERATING_UPWARD`, `ACCELERATING_DOWNWARD`, `COMPRESSING`, or `FLATLINING`.

### DIVISION IV: STRUCTURAL, FLOW & ALIGNMENT ENGINES
* **Agent 09 (Visual-Sentry Structural Worker):** Computes volume-weighted average price (VWAP) and extracts 5-bar rolling local extrema support/resistance boundaries. Maps structural regime (`ABOVE_VWAP_EXPANSION`, `BELOW_VWAP_COMPRESSION`, `AT_VWAP_EQUILIBRIUM`).
* **Agent 10 (Smart Money Flow Worker):** Computes Point of Control (POC) and 70% Value Area High/Low (VAH/VAL) volume profiles alongside 10-bar OBV trend slopes. Classifies `INSTITUTIONAL_ACCUMULATION`, `INSTITUTIONAL_DISTRIBUTION`, or `NEUTRAL_FLOW`.
* **Agent 11 (Timeframe Matrix Alignment Worker):** Multi-horizon EMA-8 vs EMA-21 trend confluence engine evaluating Short-Term (~15d), Daily Structure (~60d), and Macro Trend (~52wk) horizons. Computes Confluence Score $[-3, +3]$ and Compatibility Index $[0\%, 100\%]$.

### DIVISION V: FUNDAMENTAL, REGULATORY, MACRO & SENTIMENT OVERLAYS
* **Agent 12 (Corporate Fundamentals Worker):** Ingests Trailing P/E, Forward P/E, Price-to-Book, Debt-to-Equity, and FCF Yield % to classify `UNDERVALUED_QUALITY`, `OVERVALUED_EXPENSIVE`, `BALANCE_SHEET_DISTRESS`, or `FAIR_VALUE`.
* **Agent 13 (SEC Watchdog & Form 4 Worker):** Aggregates insider purchase vs sale counts and net insider share volumes. Classifies `INSIDER_ACCUMULATION`, `INSIDER_DISTRIBUTION`, `CLEAN_NEUTRAL`, or `INSIDER_BLINDSPOT`.
* **Agent 14 (Sector Rotation Specialist):** Computes 20-day alpha ($\alpha_{20d} = R_{\text{asset}} - R_{\text{bench}}$) against sector ETF benchmarks (`XLC`, `XLF`, `XLE`, `XLU`, `SPY`) and tracks 10-day Relative Strength slope.
* **Agent 15 (Macro Environment Tracker):** Evaluates 10-Year Treasury Yield (`^TNX`), US Dollar Index proxy (`UUP`), and benchmark equity (`SPY`) deltas to classify `RISK_ON_EXPANSION`, `RISK_OFF_DEFENSIVE`, `STAGFLATION_COMPRESSION`, or `NEUTRAL_TRANSITION`.
* **Agent 16 (Sentiment Harvester Worker):** Lexical polarity scoring engine analyzing recent news headlines. Computes normalized polarity $[-1.0, +1.0]$ and categorizes `BULLISH_EUPHORIA`, `BEARISH_FEAR`, `BALANCED_NEUTRAL`, or `DATA_BLINDSPOT`.

---

## 4. UNIFIED COMMUNICATION PROTOCOL & TYPE CONTRACTS

### Data Contract (`pierre_quant.core.agent_contract`)
All specialist workers must emit immutable, strictly typed payloads conforming to `AgentExecutionPayload`:

```python
@dataclass(slots=True, frozen=True)
class AgentExecutionPayload:
    agent_id: str
    ticker: str
    status: ExecutionStatus          # SUCCESS | REJECTED | FAILED | TIMEOUT
    directional_bias: DirectionalBias = DirectionalBias.NEUTRAL  # BULLISH | BEARISH | NEUTRAL
    confidence_score: float = 50.0  # Normalized [0.0, 100.0]
    spot_price: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    candles: Optional[List[CandleData]] = None
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
```

### Systemic Invariant Rules
1. **Zero Autoregressive Text Arithmetic:** All mathematical operations (Z-scores, VWAP, MACD, ATR, relative alpha, volume profiles) must execute inside Python/NumPy/Pandas methods. Raw LLM model arithmetic is strictly forbidden.
2. **Subprocess Isolation:** PyTorch tensor predictive engines (TimesFM, Chronos) run via isolated CLI subprocesses (`--json` mode) with distinct CUDA device mappings to guarantee zero VRAM or runtime interference.
3. **Mandatory Opacity Haircuts:**
   - A mandatory **20% confidence haircut** is applied if SEC Form 4 (`Agent 13`) or News Sentiment (`Agent 16`) arrays return empty.
   - A **50% discount** is applied to retail sentiment weight if it directly opposes institutional flow (`Agent 10`).
   - A **20% discount** is applied to predictive weights when TimesFM and Chronos indicate a `CONFLICTING_REGIME`.
4. **Monotonic Stop Floor Retention:** Stop boundaries can never be lowered under any market conditions.
5. **Database Concurrency Isolation:** The central ledger `pierre_quant.db` operates exclusively in SQLite WAL mode (`PRAGMA journal_mode=WAL;`), enforcing read-only modes (`?mode=ro`) during scan compilation.

---

## 5. DUAL-MODEL PREDICTIVE RESOLUTION MATRIX

| Model A (TimesFM `cuda:0`) | Model B (Chronos `cuda:1`) | Spread Delta $|\Delta_{\text{TFM}} - \Delta_{\text{CHR}}|$ | Divergence Status | Consensus Action |
| :---: | :---: | :---: | :---: | :---: |
| BULLISH | BULLISH | $\le 1.5\%$ | `CONVERGENT_REGIME` | Full 100% Weight Ingestion |
| BEARISH | BEARISH | $\le 1.5\%$ | `CONVERGENT_REGIME` | Full 100% Weight Ingestion |
| BULLISH | BEARISH | $> 1.5\%$ | `CONFLICTING_REGIME` | 20% Confidence Haircut Applied |
| BEARISH | BULLISH | $> 1.5\%$ | `CONFLICTING_REGIME` | 20% Confidence Haircut Applied |
| SUCCESS | FAILED / NULL | N/A | `SINGLE_MODEL_OPACITY` | Active Model Ingested; Failed Model Excluded |
