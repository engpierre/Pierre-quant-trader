import streamlit as st
import pandas as pd
import numpy as np
from supervisor_agent import SupervisorXO

def render_audit_card(ticker, json_data, raw_reports):
    """ Modular helper perfectly structured for intuitive top-down PDF reading natively. """
    v_action = json_data.get('verdict', {}).get('action', 'NEUTRAL')
    v_confidence = json_data.get('verdict', {}).get('confidence', 'Unknown')
    v_logic = json_data.get('verdict', {}).get('final_logic', json_data.get('verdict', {}).get('logic', 'Fetching Master Logic...'))
    integrity = json_data.get('integrity_check', json_data.get('raw_integrity', 'System Status Pending...'))
    delta_str = json_data.get('conviction_delta', 'N/A')
    
    v_color = "#3498db"
    if "BUY" in v_action.upper(): v_color = "#2ecc71"
    if "SELL" in v_action.upper() or "CAUTION" in v_action.upper() or "TRAP" in v_action.upper(): v_color = "#e74c3c"
    if "HOLD" in v_action.upper(): v_color = "#FF9800"

    # --- ROW 1: MASTER VERDICT & KEY METRICS ---
    st.markdown(f"<h3 style='text-align: center;'>Target: {ticker.upper()} | Master CIO Verdict: <span style='color:{v_color};'>{v_action}</span></h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    v_col1, v_col2, v_col3 = st.columns([2, 1, 1])
    with v_col1:
        if json_data.get("judicial_override"):
            st.warning("⚠️ **JUDICIAL OVERRIDE ACTIVE:** The Master CIO has overridden the Adversarial Critic based on 'Generational Alpha' parameters.")
        st.markdown(f"""
            <div class="intel-card">
                <div class="intel-header">🧠 Strategy</div>
                <div style="color: #2c3e50; line-height: 1.6;">{v_logic}</div>
            </div>
        """, unsafe_allow_html=True)

    with v_col2:
        delta_color = "#e74c3c" if "-" in str(delta_str) else "#2ecc71"
        st.markdown(f"""
            <div class="quant-metric-box">
                <div class="metric-label">Conviction</div>
                <div class="metric-value">{json_data.get('swarm_score', 0)}/100</div>
                <div style="color: {delta_color}; font-size: 0.9rem; font-weight: bold;">{delta_str}</div>
            </div>
        """, unsafe_allow_html=True)

    with v_col3:
        ipb_data = json_data.get('geopolitical', {})
        geo_regime = ipb_data.get('geopolitical_regime', 'STABLE')
        geo_risk = ipb_data.get('risk_score', 0)
        st.markdown(f"""
            <div class="quant-metric-box">
                <div class="metric-label">Regime</div>
                <div class="metric-value">{geo_regime}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    # --- ROW 1.5: ADVERSARIAL REBUTTAL ---
    critic_data = json_data.get('critic', {})
    st.markdown(f"""
        <div class="intel-card">
            <div class="intel-header" style="color: #d35400;">🔥 Critic Rebuttal (Danger Score: {json_data.get('critic_score', 0)}/100)</div>
            <div style="color: #2c3e50; line-height: 1.6;">{critic_data.get('rebuttal', 'No structural weaknesses mathematically uncovered.')}</div>
        </div>
    """, unsafe_allow_html=True)
    st.divider()

    # --- ROW 2: CRITICAL INTELLIGENCE CARDS ---
    i_col1, i_col2 = st.columns(2)
    
    with i_col1:
        st.markdown(f"""
            <div class="intel-card">
                <div class="intel-header" style="color: #2980b9;">🛡️ Integrity Monitor</div>
                <div style="color: #2c3e50; line-height: 1.6;">{integrity}</div>
            </div>
        """, unsafe_allow_html=True)
        
    with i_col2:
        if geo_regime == 'VOLATILE':
            geo_str = f"<b>Zone:</b> {ipb_data.get('chokepoint_analysis', 'Friction')}<br><b>Impact:</b> {ipb_data.get('strategic_impact', 'Risk detected.')}"
        else:
            geo_str = "Regime STABLE. No severe kinetic friction vectors mapped."
            
        st.markdown(f"""
            <div class="intel-card">
                <div class="intel-header" style="color: #27ae60;">🌍 GEOPOLITICAL SITREP (Risk {geo_risk}/100)</div>
                <div style="color: #2c3e50; line-height: 1.6;">{geo_str}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- BOTTOM SECTION: DEEP DIVE (Containment Tabs for PDF bloat reduction) ---
    tab_mc, tab_tech, tab_fund = st.tabs(["Market Context", "Technical Deep-Dive", "Fundamental Audit"])
    
    with tab_mc:
        st.code(raw_reports.get('FetchAI (Oracle)', 'No Oracle Data'), language="json")
        st.info(raw_reports.get('WhaleWatcher', 'No Whale Data'))
        
    with tab_tech:
        st.info(raw_reports.get('Technical', 'No Tech Data'))
        
    with tab_fund:
        st.info(raw_reports.get('Fundamental', 'No Fund Data'))

def main():
    # 1. Switch back to wide for better horizontal utility
    st.set_page_config(page_title="Pierre Quant Agent", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")
    
    # 2. Add Adaptive CSS
    st.markdown("""
    <style>
    /* Font Scaling for High Density */
    html, body, [class*="css"] {
        font-size: 14px !important;
    }
    h1, h2, h3 {
        font-size: 20px !important;
    }

    /* Desktop: Comfortable reading width. Mobile/Print: 100% width. */
    .main .block-container {
        max-width: 1200px; /* Mission Parameter: 1200px Constraint */
        padding-top: 1.5rem;
        padding-left: 3rem;
        padding-right: 3rem;
        margin: auto;
    }

    /* Professional Card Styling - prevents narrow vertical scrolling */
    .stAlert {
        border: 1px solid #e6e9ef;
        border-radius: 12px;
        padding: 1.5rem;
        background-color: #ffffff;
    }
    
    /* Custom High-Density Metric Boxes */
    .quant-metric-box {
        background-color: #f8f9fa;
        border: 1px solid #e6e9ef;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
    }
    
    /* Standardized Card for both Strategy and Critic */
    .intel-card {
        background-color: #fffdf0; /* Light yellow/cream to match the Critic box */
        border: 1px solid #ffe58f; /* Subtle yellow border */
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        height: 100%; /* Ensures they stay equal height in a column */
    }
    
    .intel-header {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Print Optimization: Removes sidebar/footer and expands text */
    @media print {
        [data-testid="stSidebar"], header, footer { display: none !important; }
        .main .block-container { max-width: 100% !important; padding: 0 !important; }
        .stButton, .stDownloadButton { display: none !important; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.sidebar.title("📡 Command Center")
    mode = st.sidebar.radio("Operating Mode", ["Manual Audit", "Autonomous Recon", "AAR Ledger (Backtest)"])

    
    # Re-inject professional Header
    st.title("⚖️ Pierre Quant Agent")
    st.markdown("---")
    
    supervisor = SupervisorXO()

    if mode == "Manual Audit":
        st.markdown("<h4 style='text-align: center; color: gray;'>Reactive Ticker Analysis</h4>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            ticker = st.text_input("Target Node:", "AAPL", label_visibility="collapsed").upper()
            if st.button("Execute Reactive Audit", use_container_width=True, type="primary"):
                with st.spinner(f"Initiating 8-Node Judicial Loop targeting {ticker}..."):
                    j_list, r_list = supervisor.execute(ticker, mode="manual")
                
                if not j_list or j_list[0] is None:
                    st.error("❌ Agent Swarm Failed. Check the local inference engine logs for out-of-memory errors.")
                else:
                    render_audit_card(ticker, j_list[0], r_list[0])
                    
    elif mode == "Autonomous Recon":
        st.markdown("<h4 style='text-align: center; color: #3498db;'>Proactive Market Discovery</h4>", unsafe_allow_html=True)
        st.info("The Scout Node aggressively scans the highly liquid megacap universe (S&P benchmark) to mathematically isolate the Top 3 Mansfield Outliers, autonomously piping each target natively into the Master CIO Judicial loop.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Launch Autonomous Recon 🚀", use_container_width=True, type="primary"):
                
                with st.status("Deploying Proactive Hunter... (Approx 45s Multi-Array Generation)", expanded=True) as status:
                    st.write("1️⃣ Scout Agent Calculating MRS & Volume Delta Arrays...")
                    st.write("2️⃣ Triangulating Top 10 Anomalies & Executing Pearson Matrix Locks...")
                    st.write("3️⃣ Dispatching Central Swarms & Extrapolating Insider Interventions...")
                    
                    j_list, r_list = supervisor.execute("SCAN", mode="discovery")
                    status.update(label="Reconnaissance Sweep Complete!", state="complete", expanded=False)
                    
                if not j_list or all(j is None for j in j_list):
                    st.error("❌ Reconnaissance Failed. Local Engine Initialization failed.")
                else:
                    valid_j_list = [j for j in j_list if j is not None]
                    st.success(f"Successfully calculated and adjudicated {len(valid_j_list)} completely diversified algorithmic breakouts.")
                    
                    # Intercept the Covariance Report globally injected into the first array object safely
                    cov_report = r_list[0].get('Covariance (Diversification Matrix)', '')
                    if "TACTICAL ADJUSTMENT" in cov_report:
                        # Split by newline and render each warning separately
                        for warning_msg in cov_report.split("\n\n"):
                            st.warning(warning_msg)
                    elif cov_report:
                        st.success(cov_report)
                        
                    # Generates flexible array architecture independent of volume payload
                    for j, r in zip(j_list, r_list):
                        if j is None:
                            continue
                        t_name = j.get("ticker", "UNKNOWN")
                        with st.expander(f"📌 HIGH-CONVICTION SCOUT TARGET LOCKED: {t_name}", expanded=True):
                            render_audit_card(t_name, j, r)

    elif mode == "AAR Ledger (Backtest)":
        st.markdown("<h4 style='text-align: center; color: #8e44ad;'>📈 After-Action DB Overrider</h4>", unsafe_allow_html=True)
        st.info("The Validator physically tracks the paper-trade lifecycle and natively penalizes Hallucinating nodes utilizing Spearman Rank correlation metrics over time.")
        
        try:
            from optimizer_engine import get_global_trust_weights
            weights, trust_avg = get_global_trust_weights()
            
            st.subheader("🧠 Self-Optimization: Trust Matrix")
            df_weights = pd.DataFrame([weights]).T.reset_index()
            df_weights.columns = ['Agent', 'Active Weight']
            
            st.data_editor(
                df_weights,
                column_config={
                    "Active Weight": st.column_config.ProgressColumn(
                        "Current Influence",
                        help="The mathematical weight used in final synthesis",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                },
                hide_index=True,
                use_container_width=True
            )
            
            if trust_avg < 0.40:
                st.error(f"🤖 **SELF-OPTIMIZATION ACTIVE:** Boosting Adversarial Critic weight natively due to trailing volatility-drift (Swarm Trust {trust_avg*100:.1f}%).")
        
            from backtest_validator import grade_overrides
            needs_recalibration, grade_report = grade_overrides()
            if needs_recalibration:
                st.error(f"🚨 **LOGIC RECALIBRATION REQUIRED:** Judicial Override trailing win-rate failing baseline ({grade_report}). Advocate tightening Generational Alpha trigger to RSI-20 to avoid catching 'Falling Knives'.")
            else:
                st.success(f"⚖️ Judicial Overrides maintaining structural precision. {grade_report}")
                
            # Display Mission Logs locally
            import sqlite3
            conn = sqlite3.connect('antigravity_aar.db')
            df_logs = pd.read_sql_query("SELECT mission_id, timestamp, ticker, regime, conviction_delta, override_active, price_entry FROM mission_logs ORDER BY timestamp DESC LIMIT 25", conn)
            st.dataframe(df_logs, use_container_width=True)
            conn.close()
        except Exception as e:
            st.warning("Database currently empty. Execute 8-Node CI array loops to populate the structural persistent ledgers.")

if __name__ == "__main__":
    main()
