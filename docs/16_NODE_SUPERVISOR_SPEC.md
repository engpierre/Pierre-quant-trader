# 🛡️ PIERRE QUANT :: 16-NODE SENTRY & SUPERVISOR ARCHITECTURE SPEC
**Hardware Allocation:** AMD 9950X | Dual RTX 5060 Ti (GPU 0: TimesFM 1.0, GPU 1: Chronos-Bolt)  
**Orchestration Engine:** Agent 01 Master Supervisor (`supervisor.py` / `run_single_dossier.py`)  
**Memory & Persistence:** Martian Engine "Lossless Claw" SQLite DAG (`pierre_quant.db`)  

## 1. Tactical Division Breakdown
* **Division I (Command & Defense):**
  - **Agent 01 (Supervisor Orchestrator):** Master confluence aggregator & directive synthesis.
  - **Agent 02 (Risk & Portfolio Guard):** ATR-based monotonic stop ratchets & drawdown boundaries.
* **Division II (Alpha Ingestion & Storage):**
  - **Agent 03 (Spending-Sentry):** USAspending.gov contract discovery.
  - **Agent 04 (Vault Custodian):** SQLite DAG state persistence (`pierre_quant.db`).
  - **Agent 05 (Live API Ingestion):** High-frequency multi-vendor OHLCV feed management.
* **Division III (Predictive Foundation & Quant):**
  - **Agent 06a (TimesFM 1.0):** Google Research foundational time-series on `cuda:0`.
  - **Agent 06b (Chronos-Bolt):** Amazon Research autoregressive forecaster on `cuda:1`.
  - **Agent 07 (Stat Invariance):** Z-Score, Bollinger Bands, and mean-reversion analysis.
  - **Agent 08 (Momentum Vector):** MACD, RSI, and multi-horizon velocity modeling.
* **Division IV (Technical & Orderflow Structure):**
  - **Agent 09 (Visual Sentry):** Anchored VWAP, pivot clusters, and structural levels.
  - **Agent 10 (Smart Money Flow):** Volume Profile POC, Value Area, and OBV distribution.
  - **Agent 11 (Timeframe Matrix):** 4H / Daily / Weekly multi-EMA alignment reconciler.
* **Division V (Fundamental, Regulatory & Crowd Intel):**
  - **Agent 12 (Corporate Fundamentals):** Valuation multiples (P/E, EV/EBITDA) & FCF yields.
  - **Agent 13 (SEC Watchdog):** Form 4 insider clustering & net volume tracking.
  - **Agent 14 (Sector Rotation):** Benchmark ETF relative strength & sector alpha.
  - **Agent 15 (Macro Environment):** 10Y Yields (`^TNX`) & DXY regime overlays.
  - **Agent 16 (Sentiment Harvester):** Crowd buzz polarity with 0.50x anti-herd discount.

## 2. Mathematical Consensus Invariants
* **Confluence Range:** $S_{\text{net}} = \frac{\sum W_{\text{bull}} - \sum W_{\text{bear}}}{\sum W_{\text{total}}} \times 100$
* **Consensus Thresholds:** $\ge +25.0\%$ (`BULLISH_CONVERGENCE`), $\le -25.0\%$ (`BEARISH_CONVERGENCE`), otherwise `NEUTRAL_CONSOLIDATION`
* **Dual-Model Conflict Rule:** $\vert{}\text{TimesFM}_\Delta - \text{Chronos}_\Delta\vert{} > 1.5\% \implies 20\%$ confidence haircut across predictive nodes.
* **Data-Opacity Rule:** Unpopulated feeds (SEC Form 4 / news gaps) carry a mandatory 20% haircut (`conf = 50.0%`).

## 3. Standard Invocation Contract
* **Single Dossier CLI Command:**
  `& "C:\Users\Pierre\.openclaw\workspace\Julie-Core\.venv\Scripts\python.exe" "C:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant\orchestration\run_single_dossier.py" --ticker "<TICKER>"`
