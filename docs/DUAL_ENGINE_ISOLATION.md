# Pierre Quant Architecture :: Dual-Engine Forecasting & Model Isolation

## 1. System Topology & Hardware Bindings
- **Host CPU:** AMD Ryzen 9 9950X (16 cores / 32 threads)
- **Primary GPU (GPU 0 - `cuda:0`):** NVIDIA GeForce RTX 5060 Ti (16 GiB VRAM)
  - **Pinned Engine:** Google Research `google/timesfm-1.0-200m-pytorch`
  - **Tensor Shape:** 128-bar historical context tensor (padded)
  - **Horizon:** 16-bar forward mean trajectory & 1-sigma probability envelope
- **Secondary GPU (GPU 1 - `cuda:1`):** NVIDIA GeForce RTX 5060 Ti (16 GiB VRAM)
  - **Pinned Engine:** Amazon Research `amazon/chronos-bolt-base` (via `chronos.BaseChronosPipeline`)
  - **Precision:** `torch.bfloat16`
  - **Horizon:** 16-bar forward probabilistic expectation vector & volatility bands
- **Inference Server:** Ollama `qwen3.8-hardened:27b` with 128K context (`num_ctx 131072`) split across dual GPUs

---

## 2. Pipeline Components & Decoupled Roles

### A. OpenClaw Live API Ingestion & Pre-Flight Gate (`Agent 05`)
- **Location:** `pierre_quant/agents/live_api_ingestion.py`
- **Dual-Node Live Corroboration:** Primary (`yfinance.fast_info`) ∩ Secondary (`HTTP Market Oracle`) requiring inter-node divergence $\le 0.75\%$ for `DUAL_NODE_SIGNED`.
- **Pre-Flight Drift Intercept Gate:** Halts downstream tensor computation if $|\text{Drift}_{\%}| > 5.0\%$ to eradicate prompt lineage drift.
- **Dynamic ATR Calculation:** True 14-day Average True Range (`calculate_14_day_atr`) computed directly from historical OHLCV data.

### B. Predictive Dispatcher (`Division III`)
- **Location:** `pierre_quant/runners/predictive_dispatcher.py`
- **Concurrent Dispatch:** Executes TimesFM (`cuda:0`) and Amazon Chronos-Bolt (`cuda:1`) asynchronously via `asyncio.gather`.
- **Cross-Model Examination:** Evaluates directional consensus and target spread ($\Delta_{\text{models}} = \text{Target}_{\text{TimesFM}} - \text{Target}_{\text{Chronos}}$).

### C. Standalone Hermes Chronos Audit Runner
- **Location:** `run_chronos_audit.py`
- **Role:** Independent adversarial red-team verification script for Hermes agent tool invocation.

---

## 3. Verification Telemetry Log

### $META Live Verification Pass
- **Spot Price:** `$549.90` (Live Tape Verified)
- **14-Day ATR:** `$17.02` | **Daily Volatility (σ):** `2.77%`
- **Google TimesFM 1.0 (`cuda:0`):** Target `$558.15` (+1.50%) | Confidence: HIGH
- **Amazon Chronos-Bolt (`cuda:1`):** Target `$573.83` (+4.35%) | Confidence: HIGH
- **Model Alignment:** CONVERGENT BULLISH ($\Delta = +2.81\%$) | Actionable Verdict: **`BUY`**
- **Hardware Status:** GPU 0 & GPU 1 operational, zero OOM faults, zero write locks on `pierre_quant.db`.

### $ABTC Live Verification Pass
- **Status:** `VERIFIED` | **Integrity:** `DUAL_NODE_SIGNED`
- **Pre-Flight Gate:** Passed (Drift: `NONE`)
- **Forecast Envelopes:** Synchronized trajectory bounds across Division III predictive nodes.
