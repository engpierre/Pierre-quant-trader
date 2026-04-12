# 🚀 Pierre Quant Agent (Anti-gravity)

**Pierre Quant Agent** is an advanced, autonomous algorithmic quantitative research desk engineered for zero-cloud execution. By leveraging a multi-agent AI framework powered entirely by a localized **Gemma-4 (26-Billion Parameter) Inference Engine**, the system continuously monitors, synthesizes, and evaluates market data across multiple critical dimensions—technicals, fundamentals, sentiment, and dark pool integrity—to generate mathematically structured trading signals in a 100% air-gapped environment.

---

## ⚡ Features

- **Dual-Mode Discovery Engine**: The system can operate Reactively (scanning a user-provided ticker) or Proactively (using mathematical Mansfield Relative Strength to autonomously scan the S&P 100 proxy for high-conviction breakouts).
- **Multi-Agent Adversarial Swarm**: Eleven specially crafted tactical nodes analyzing strict fundamental, technical, geopolitical, and alternative data pillars.
- **Master Synthesizer (Judicial Loop)**: Instead of a flat aggregator, the orchestrator triggers an adversarial sequence: constructing a Bull case via the internal swarm, then immediately forcing a specialized Critic Agent to ruthlessly attack the thesis.
- **Backtest Validator (AAR Ledger)**: Eliminates static execution by introducing a persistent SQLite intelligence loop mapping every $T+24$ paper-trade performance directly against the system's historical verdicts.
- **Recursive Self-Optimization**: The Swarm acts as an independent learning organism. The CIO queries the SQLite AAR Database dynamically at runtime adjusting Node Trust Coefficients—mathematically amplifying the Adversarial Critic's veto weight if systemic LLM hallucinations drag the Win Rate below 50%.
- **Dynamic Regime Anchor**: The system natively calculates the overarching macroeconomic regime (Trending-Bull vs Volatile-Bear) using FRED Yield Curve / Asset grids, automatically scaling the Red Team's mathematical veto power based on structural vulnerability.
- **Algorithmic Covariance Locks**: The Proactive Scanner enforces strict Force Composition metrics natively discarding positively correlated ($R > 0.85$) targets to guarantee perfectly uncoupled Alpha.
- **High-Density 'War Room' Dashboard**: A completely re-engineered Streamlit UI utilizing 'Adaptive Wide' CSS container configurations, bespoke HTML metric bounds (`.quant-metric-box`), and an ultra-condensed Print Protocol for flawless 1-page PDF Executive board reporting.
- **AgentFi Cloud Architecture**: Completely containerized for decentralized smart-contract integration, exporting dynamic `Signal_Report_Intent.json` files while running dual-duty alongside an MCP-wrapped localized Ground Truth Oracle Server.
- **Monte Carlo Projection Matrix**: Simulates 10,000 independent mathematical futures via Geometric Brownian Motion to project strict 63-day target probabilities directly on your dashboard.
- **Real-Time Web Reconnaissance**: Natively intercepts and parses real-time global news via active RSS scraping without relying on external or paid search API keys.
- **Alternative Data Rules Protocol**: Enforces quantitative mechanics like ATR-based stops and 50-day Volume Divergences—ignoring "vibes" in favor of strict empirical data points.

### Phase 1: Doctrine & Command Protocol

**1. The Reasoning XO (Executive Officer) Persona**
The Supervisor Agent is no longer a passive script. It is now designated as the Reasoning XO.

- **Chain-of-Thought (CoT) Requirement:** For every market analysis, the XO must generate an internal reasoning trace, comparing agent outputs against the Blackwell Critic’s adversarial audit.
- **Conversational Logic:** The XO is tasked with translating high-density JSON telemetry into professional, data-backed verbal reports for the MWO.

**2. The Hard Veto Protocol (MWO-in-the-Loop)**
To eliminate "Alpha Hallucinations" and systemic drift, a strict Hard Veto protocol is now in effect:

- **Veto Trigger:** If the Blackwell Critic identifies a logic paradox (e.g., price/volume divergence not supported by the Reality Anchor), a Hard Veto is issued.
- **Pipeline Freeze:** In a Veto state, all automated trade intent exports (Signal_Report_Intent.json) are locked.
- **Manual Override:** The system will enter a "Standby" state, providing a forensic audit to the MWO. Execution only proceeds upon a manual Accept or Bypass command.

**3. Adversarial Forensic Protocol**
When a Veto occurs, the Supervisor must provide a Forensic Audit consisting of:

- **Conflict Mapping:** Identifying which specific nodes are in disagreement (e.g., Technical vs. Whale).
- **Hallucination Probability:** A confidence score reflecting the likelihood that an agent is "hallucinating" data points not found in the local Oracle database.
- **Friction Points:** A bulleted summary of empirical data mismatches.

---

## 🏗️ Architecture

The algorithmic framework relies on a decentralized, modular python agent hierarchy:

1. **Scout Agent (`discovery_engine.py`)**: The Proactive Scanner. Mathematically isolates Top 10 explosive breakouts via Mansfield Relative Strength ($MRS$) and filters noise utilizing a strict 50-day Volume Divergence index.
2. **Covariance Agent (`covariance_agent.py`)**: The Diversification Lock. Prevents structural exposure by forcing the Scout to re-roll and decouple highly correlated tickers ($R>0.85$).
3. **Supervisor Agent (`supervisor_agent.py`)**: The overarching Master CIO. Triggers the continuous 8-node loop and enforces strict JSON formatting containing precise current and projected price extractions natively.
4. **Optimizer Engine (`optimizer_engine.py`)**: Calculates dynamic $Global Trust$ arrays querying standard accuracy directly injecting mathematical Red Team boosts into the System Prompt.
5. **Backtest Validator (`backtest_validator.py`)**: The ACID compliant overarching SQLite constructor defining the Mission Logs and Agent Attribution persistence ledgers.
6. **Critic Agent (`critic_agent.py`)**: The Adversarial Auditor. Deployed explicitly to hunt for "Alpha Hallucination" by identifying structural weaknesses, Bear traps, and Volume Expansions inside the broader Swarm's reports.
7. **Geopolitical IPB Agent (`geopolitical_agent.py`)**: The Kinetic Friction Mapper. Calculates active supply chain chokepoints natively by intercepting and synthesizing live Real-Time Google News RSS feeds.
8. **Whale-Watcher Agent (`whale_agent.py`)**: The Intelligence Officer. Maps Dark Pool blocks, Congressional sweeps, and overarching macro regimes utilizing strictly mapped FRED Yield Curve hooks.
9. **Insider Integrity Auditor (`insider_agent.py`)**: The Logic Decoupler. Specifically isolates the Swarm payload hunting internal hallucination paradoxes natively.
10. **Fundamental Agent (`fundamental_agent.py`)**: Scrapes trailing P/E, institutional margins, while explicitly trapping incorrect Megacap Debt ratios natively via the Reality Anchor.
11. **Sentiment Agent (`sentiment_agent.py`)**: Queries live networks to monitor extreme retail panic surges (e.g. VIX spikes > 10%).
12. **Technical Agent (`technical_agent.py`)**: Mathematically targets Price/RSI disparities and natively simulates 10,000-path Geometric Brownian Motion to establish definitive 63-day Monte Carlo price targets.
13. **Fetch.AI Agent (`fetch_ai_agent.py`)**: Operating natively as a hyper-fast localized quantitative True Price Oracle featuring native robust caching and historical market-close fallbacks.

---

## 🚦 Getting Started

### Prerequisites
- Python 3.10+
- A Compute-Capable GPU with ~16GB+ VRAM (Optimized natively for RTX 5060 Ti architectures to run localized Gemma-4 Inference Engine payloads).
- *(Optional)* Fetch.AI `uAgent` Network hook Endpoint

### Installation
Install the necessary quantitative backend packages and the Streamlit frontend natively:

```bash
pip install streamlit requests beautifulsoup4 praw yfinance pandas numpy fredapi torch transformers bitsandbytes accelerate
```

*(Alternatively, the entire stack including the AAR SQLite ledger is containerized for AgentFi cloud deployments. Simply run `docker-compose up -d` to securely launch the persistent execution loop.)*

### Environment Setup
As of recent architectural shifts, the Master Oracle and standard intelligence Swarm process exclusively via a 100% air-gapped `LocalInferenceEngine` singleton. External API keys (like Google Gemini) are **no longer required** for execution.

---

## 💻 Usage

To launch the centralized visual dashboard locally:

```bash
streamlit run app.py
```

This command will initialize the local server and instantly open the user interface in your default browser. 

1. **Command Center Toggle**: The dashboard features an active sidebar mapping three explicit operational states.
2. **Manual Audit (Reactive)**: Type any stock ticker and hit Execute to instantly spin up the Swarm targeted precisely at your request.
3. **Autonomous Recon (Proactive)**: The app will autonomously boot the Scout Agent, calculate mathematical rankings across the S&P proxy universe, bypass standard Covariance correlations ($R>0.85$), and strictly pipeline structurally diversified targets directly into the Judicial Execution Courtrooms.
4. **AAR Ledger (Backtest)**: View the overarching Database persistence layers physically auditing recursive Self-Correction Trust algorithms mapping the Red Team's active override strength dynamically.
