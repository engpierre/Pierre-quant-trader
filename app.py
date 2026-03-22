import streamlit as st
import subprocess
import json
import sys
import os
import time
import pandas as pd
import re
from textblob import TextBlob

st.set_page_config(page_title="Antigravity Quant Desk", layout="wide", page_icon="🌌", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* High-Contrast Accessible Light Theme */
    .stApp {
        background-color: #FFFFFF;
        font-family: 'Inter', -apple-system, sans-serif;
        color: #111111;
    }
    
    h1 {
        color: #003366 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    h2, h3, h4, h5, h6 {
        color: #222222;
        font-weight: 700;
    }
    p, span, div {
        color: #333333;
    }
    
    /* High-Contrast Buttons */
    .stButton>button {
        background-color: #E2E8F0;
        color: #0F172A !important;
        font-weight: 700;
        border: 2px solid #CBD5E1;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        transition: all 0.2s ease-in-out;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stButton>button:hover {
        background-color: #CBD5E1;
        border-color: #94A3B8;
        color: #000000 !important;
    }
    
    /* Input Fields: Dark text on light backgrounds */
    .stTextInput>div>div>input {
        background-color: #F8FAFC !important;
        border: 2px solid #CBD5E1 !important;
        color: #0F172A !important;
        border-radius: 6px;
        font-weight: 500;
        transition: border-color 0.2s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 1px #2563EB !important;
        background-color: #FFFFFF !important;
    }
    
    /* DataFrame & Expander Styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
    }
    [data-testid="stExpander"] {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    [data-testid="stExpander"] > summary {
        color: #0F172A;
        font-weight: 700;
        background-color: #F1F5F9;
        border-radius: 8px;
    }
    [data-testid="stExpander"] > summary:hover {
        background-color: #E2E8F0;
    }
    
    /* Sidebar Aesthetics */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    
    /* Checkbox text */
    .stCheckbox label span {
        color: #0F172A !important;
        font-weight: 500;
    }
    
    /* Info/Warning/Success override for better contrast */
    [data-testid="stAlert"] {
        color: #0F172A !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🌌 Antigravity Quant Desk")
st.markdown("Automated High-Conviction Stock Screening Pipeline integrating Technical, Sentiment, and Insider Intelligence.")

# --- NLP Intepretation Layer ---
def parse_nlp_query(query):
    query_upper = query.upper()
    res = {"intent": "UNKNOWN", "target": None, "sector": None, "time_context": None}
    
    sector_map = {
        "TECH": "Information Technology", "TECHNOLOGY": "Information Technology",
        "HEALTH": "Health Care", "HEALTHCARE": "Health Care", "MEDICAL": "Health Care",
        "FINANCE": "Financials", "FINANCIAL": "Financials", "FINANCIALS": "Financials", "BANK": "Financials",
        "CONSUMER": "Consumer Discretionary", "RETAIL": "Consumer Discretionary",
        "COMMUNICATION": "Communication Services", "COMMUNICATIONS": "Communication Services",
        "INDUSTRIAL": "Industrials", "INDUSTRIALS": "Industrials", "MANUFACTURING": "Industrials",
        "STAPLES": "Consumer Staples", "FOOD": "Consumer Staples",
        "ENERGY": "Energy", "OIL": "Energy", "GAS": "Energy",
        "UTILITIES": "Utilities", "UTILITY": "Utilities",
        "REAL ESTATE": "Real Estate", "HOUSING": "Real Estate",
        "MATERIALS": "Materials"
    }
    
    for k, v in sector_map.items():
        if k in query_upper:
            res["sector"] = v
            break
            
    time_match = re.search(r'(MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|NEXT WEEK|TOMORROW|\d{1,2}(ST|ND|RD|TH)? (JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*)', query_upper)
    if time_match:
        res["time_context"] = time_match.group(0)
    
    words = query_upper.split()
    stop_words = {'A', 'I', 'THE', 'OF', 'IN', 'ON', 'TO', 'FOR', 'IS', 'WHAT', 'HOW', 'WHY', 'ABOUT', 'THINK', 'FIND', 'ME', 'STOCK', 'ANY', 'GOOD', 'BAD', 'ALTERNATIVE', 'BETTER'}
    
    words = [w.strip('?,.!:\'\"') for w in words]
    potential_tickers = [w for w in words if re.match(r'^[A-Z]{1,5}$', w) and w not in stop_words and len(w)>0 and w not in sector_map.keys()]
    
    if potential_tickers and not potential_tickers[0] in ['ARE', 'CAN', 'YOU', 'DAY', 'NOW']:
         res["intent"] = "SINGLE_TICKER"
         res["target"] = potential_tickers[0]
         return res
         
    if res["sector"]:
         res["intent"] = "SECTOR_SCAN"
         return res
         
    if "DAY" in query_upper or "TODAY" in query_upper or "NOW" in query_upper:
         res["intent"] = "STOCK_OF_THE_DAY"
         return res
         
    if "WEEK" in query_upper or "MOVING" in query_upper or "MOMENTUM" in query_upper:
         res["intent"] = "MOMENTUM_RUNNERS"
         return res
         
    return res

# --- Sidebar for orchestration ---
with st.sidebar:
    st.header("⚙️ Agent Routines")
    
    with st.expander("🛠️ Advanced Agent Settings", expanded=False):
        st.markdown("Toggle specific execution domains.")
        run_scout = st.checkbox("Phase 1: Scout Agent", value=True)
        run_sentiment = st.checkbox("Phase 1.1: Sentiment NLP", value=True)
        run_insider = st.checkbox("Phase 1.2: Insider Audit", value=True)
        run_tech = st.checkbox("Phase 1.5: Mechanics", value=True)
        run_intel = st.checkbox("Phase 1.8: NVIDIA AI-Q RAG", value=True)
        run_verify = st.checkbox("Phase 2: Validation", value=True)
    
    start_run = st.button("🚀 Execute Alpha Pipeline")

    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🧠 NLP Chat UI")
    st.markdown("<span style='font-size:0.85em; color:#444;'>Query via natural language or discrete tickers.</span>", unsafe_allow_html=True)
    single_ticker = st.text_input("Message Base Agent", placeholder="e.g. 'Any Tech stocks for Monday?'", label_visibility="collapsed")
    run_single = st.button("💬 Send to Orchestrator")

st.markdown("---")

# Main content hierarchy: Output first, Logs collapsed below (Mobile First design)
st.subheader("📊 Final Intelligence Matrix")
results_output = st.empty()

st.markdown("<br>", unsafe_allow_html=True)

with st.expander("🖥️ Live Execution Telemetry (Agent Logs)", expanded=True):
    log_output = st.empty()

def run_agent(script_name, log_container, args=None):
    log_text = f"--- Initiating {script_name} ---\n"
    log_container.code(log_text, language='bash')
    
    cmd_args = [sys.executable, '-u', script_name]
    if args:
        cmd_args.extend(args)
        
    process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    
    for line in iter(process.stdout.readline, ''):
        log_text += line
        log_container.code(log_text, language='bash')
        
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        st.error(f"[{script_name}] Execution halted internally with exit code {return_code}.")
        return False
    return True

if start_run or (run_single and single_ticker):
    pipeline = []
    agent_args = {}
    nlp_res = None
    
    if run_single and single_ticker:
        nlp_res = parse_nlp_query(single_ticker)
        pipeline = ["scout.py", "sentiment.py", "insider.py", "technical.py", "market_intelligence.py", "verification.py"]
        
        msg = f"**🧠 NLP Interpretation:** Intent ➔ `{nlp_res['intent']}`"
        if nlp_res['time_context']: msg += f" | Temporal Focus: `{nlp_res['time_context']}`"
        st.sidebar.info(msg)
        
        if nlp_res["intent"] == "SINGLE_TICKER":
             st.sidebar.success(f"🎯 Locking single asset target ➔ **${nlp_res['target']}**")
             agent_args["scout.py"] = ['--ticker', nlp_res["target"]]
             
        elif nlp_res["intent"] == "SECTOR_SCAN":
             st.sidebar.success(f"🎯 Isolating structural scan to Sector ➔ **{nlp_res['sector']}**")
             agent_args["scout.py"] = ['--sector', nlp_res['sector']]
             
        elif nlp_res["intent"] in ["STOCK_OF_THE_DAY", "MOMENTUM_RUNNERS"]:
             st.sidebar.success("🎯 Routing broader discovery intent to Alpha Momentum Pipeline.")
             
        else:
             st.sidebar.warning("⚠️ Intent ambiguous. Routing strictly to broad objective pipeline.")
             
    else:
        if run_scout: pipeline.append("scout.py")
        if run_sentiment: pipeline.append("sentiment.py")
        if run_insider: pipeline.append("insider.py")
        if run_tech: pipeline.append("technical.py")
        if run_intel: pipeline.append("market_intelligence.py")
        if run_verify: pipeline.append("verification.py")
    
    if not pipeline:
        st.warning("Please toggle at least one agent or submit a chat message to initiate the execution sequence.")
    else:
        success = True
        log_output.empty() 
        for script in pipeline:
            s_args = agent_args.get(script, None)
            success = run_agent(script, log_output, s_args)
            if not success:
                st.error("Pipeline severed due to subsystem telemetry anomaly.")
                break
                
        if success and nlp_res and nlp_res["intent"] == "SINGLE_TICKER":
            try:
                with open('verified_candidates.json', 'r') as f:
                    verified_data = json.load(f)
                if verified_data:
                    c = verified_data[0] 
                    score = c.get('verification_audit', {}).get('validity_score', 0)
                    
                    if score < 60:
                        sec = c.get('sector')
                        if sec and sec != 'Unknown':
                            st.warning(f"⚠️ **${c['symbol']}** triggered a REJECT status (FCS: {score}%). Autonomously scanning the '{sec}' sector to proactively locate high-momentum alternatives!")
                            
                            with st.expander(f"Dissect Rejected Fundamentals: {c['symbol']} | FCS: {score}%", expanded=True):
                                b = c.get('verification_audit', {}).get('breakdown', {})
                                st.markdown(f"**1. Scout Tracking:** `{'+' if b.get('Scout',0)>=0 else ''}{b.get('Scout',0)}%`")
                                st.markdown(f"**2. Sentiment Base:** `{'+' if b.get('Sentiment',0)>=0 else ''}{b.get('Sentiment',0)}%`")
                                st.markdown(f"**3. Tech Mechanics:** `{'+' if b.get('Mechanics',0)>=0 else ''}{b.get('Mechanics',0)}%`")
                                st.markdown(f"**4. NVIDIA API-Q:** `{'+' if b.get('NVIDIA AI-Q',0)>=0 else ''}{b.get('NVIDIA AI-Q',0)}%`")
                                st.markdown(f"**5. Insider Audit:** `{'+' if b.get('Insider',0)>=0 else ''}{b.get('Insider',0)}%`")
                                st.markdown("---")
                                st.markdown("**Concise Validation Reasoning:**")
                                for req in c.get('verification_audit', {}).get('reasoning', []):
                                    st.markdown(f"- {req}")

                            log_output.empty()
                            agent_args["scout.py"] = ['--sector', sec]
                            for script in pipeline:
                                s_args = agent_args.get(script, None)
                                success = run_agent(script, log_output, s_args)
                                if not success: break
                            if success:
                                st.success(f"✅ Autonomous Alternative Scan Complete for **{sec}**! Evaluated outperforming targets.")
            except Exception as e:
                pass
                
        if success:
            st.toast("✅ Quantitative NLP Pipeline Executed Successfully!", icon="🚀")

def render_metrics():
    if os.path.exists('verified_candidates.json'):
        try:
            with open('verified_candidates.json', 'r') as f:
                verified_data = json.load(f)
                
            if verified_data:
                 display_data = []
                 for c in verified_data:
                     info = c.get('verification_audit', {})
                     score = info.get('validity_score', 0)
                     b = info.get('breakdown', {})
                     display_data.append({
                         "Ticker": c['symbol'],
                         "FCS (%)": score,
                         "Status": "🟩 BUY" if score >= 75 else ("🟨 WATCH" if score >= 60 else "⬛ REJECT"),
                         "Scout": f"{b.get('Scout', 0)}%",
                         "Sentiment": f"{b.get('Sentiment', 0)}%",
                         "Mechanics": f"{b.get('Mechanics', 0)}%",
                         "NVIDIA RAG": f"{b.get('NVIDIA AI-Q', 0)}%",
                         "Insider": f"{b.get('Insider', 0)}%",
                         "Sector": c['sector'],
                     })
                 
                 df = pd.DataFrame(display_data)
                 df = df.sort_values(by="FCS (%)", ascending=False)
                 df["FCS (%)"] = df["FCS (%)"].astype(str) + "%" 
                 
                 with results_output.container():
                     st.dataframe(df, use_container_width=True, hide_index=True)
                     st.markdown("<br>", unsafe_allow_html=True)
                     st.markdown("### 🧠 Interactive Diagnostic Breakdown")
                     st.markdown("<span style='font-size:0.85em; color:#444;'>Review the structural contribution mapping defining the 'REJECT' logic threshold.</span>", unsafe_allow_html=True)
                     for c in verified_data:
                         info = c.get('verification_audit', {})
                         score = info.get('validity_score', 0)
                         b = info.get('breakdown', {})
                         with st.expander(f"Sub-Agent Diagnostics: {c['symbol']} | FCS Tracker: {score}%"):
                             st.markdown(f"**1. Scout Base Framework:** Evaluates trailing 200-MA liquidity macro floors. -> `Score Contribution: {'+' if b.get('Scout',0)>=0 else ''}{b.get('Scout',0)}%`")
                             st.markdown(f"**2. Sentiment NLP Interpreter:** Indexes social momentum against retail exhaustion trends. -> `Score Contribution: {'+' if b.get('Sentiment',0)>=0 else ''}{b.get('Sentiment',0)}%`")
                             narrative_text = c.get('sentiment', {}).get('narrative', '')
                             if narrative_text:
                                 st.info(f"**Leading Expert Synopsis:**\n\n{narrative_text}")
                             st.markdown(f"**3. Technical Mechanics:** Detects institutional Order Block 'Accumulation' patterns. -> `Score Contribution: {'+' if b.get('Mechanics',0)>=0 else ''}{b.get('Mechanics',0)}%`")
                             tech_narrative = c.get('technical_audit', {}).get('narrative', '')
                             if tech_narrative:
                                 st.info(f"**Certified Quant Empirical Assessment:**\n\n{tech_narrative}")
                             st.markdown(f"**4. NVIDIA AI-Q RAG (Market Intelligence):** Leverages AI mapping over unstructured 10-K filings + KDB-X baselines. -> `Score Contribution: {'+' if b.get('NVIDIA AI-Q',0)>=0 else ''}{b.get('NVIDIA AI-Q',0)}%`")
                             st.markdown(f"**5. Insider Audit Node:** Penalizes severe 60-day CEO/CFO cluster execution divergence. -> `Score Contribution: {'+' if b.get('Insider',0)>=0 else ''}{b.get('Insider',0)}%`")
                             st.markdown("---")
                             if score < 60:
                                 st.error(f"**Validator Subsystem (REJECT STATUS):** Synthesizing the 5 vectors yielded `{score}%`. Confluence strictly <60% automatically routes the asset to REJECT due to foundational instability in the metrics listed above.")
                             else:
                                 st.success(f"**Validator Subsystem (APPROVAL STATUS):** Synthesizing the 5 vectors yielded `{score}%`. Mathematical logic confidently overrides rejection barriers due to profound confluence across the algorithms listed above.")
                 
        except Exception as e:
            results_output.error(f"Render Payload Error: {e}")

render_metrics()
