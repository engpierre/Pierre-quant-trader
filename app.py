import streamlit as st
import pandas as pd
import numpy as np

def main():
    st.set_page_config(
        page_title="Anti-gravity", 
        page_icon="🚀", 
        layout="centered", # Ensures excellent mobile readability
        initial_sidebar_state="collapsed"
    )
    
    # Title centered for mobile
    st.markdown("<h1 style='text-align: center;'>🚀 Anti-gravity</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Quant Desk Analysis System</h4>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Input section centrally aligned using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        ticker = st.text_input("Enter Ticker Symbol:", "AAPL", label_visibility="collapsed").upper()
        analyze_btn = st.button("Run Supervisor Audit", use_container_width=True, type="primary")

    if analyze_btn:
        st.success(f"Audit Complete for {ticker}")
        
        # --- 1. SUPERVISOR HERO SECTION ---
        st.markdown("<br>", unsafe_allow_html=True)
        master_card = st.container(border=True)
        
        with master_card:
            st.markdown("<h5 style='text-align: center; color: #888888;'>FINAL SUPERVISOR CONSENSUS</h5>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center; color: #4CAF50;'>🟢 HIGH-CONVICTION BUY</h2>", unsafe_allow_html=True)
            
            st.markdown("<hr>", unsafe_allow_html=True)
            st.caption("AGENT CONFIDENCE SCORES")
            
            # Use responsive metric cards instead of wide markdown tables
            c1, c2, c3 = st.columns(3)
            c1.metric(label="Technical", value="94/100", delta="Bullish")
            c2.metric(label="Fundamental", value="82/100", delta="Accumulation")
            c3.metric(label="Sentiment", value="55/100", delta="-VIX", delta_color="off")
            
            c4, c5 = st.columns(2)
            c4.metric(label="Insider Integrity", value="88/100", delta="C-Suite Buys")
            c5.metric(label="Fetch.AI Network", value="STRONG BUY", delta="85% Consensus")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("Deep Data Analysis")
        
        # --- 2. ACCORDION MODULES ---
        # Wrapping thick logic inside accordions saves vertical space on mobile devices.
        
        with st.expander("📈 Technical Analysis", expanded=True):
            st.success("**Current Price**: $182.24 | **RSI (14)**: 62.4")
            st.warning("**Volume Anomaly**: NO (>200% threshold not met)")
            st.info("**Bullish Divergence**: YES (PRICE LOWER LOW / RSI HIGHER LOW)")
            
            st.divider()
            st.caption("Dynamic Price Trend (Real-time Mock)")
            # Simulated chart showing Streamlit plotting capability
            chart_data = pd.DataFrame(
                np.cumprod(1 + np.random.randn(50, 1) / 100) * 180, 
                columns=["Implied Momentum"]
            )
            st.line_chart(chart_data)

        with st.expander("🏦 Fundamental Analysis"):
            st.metric(label="Trailing P/E", value="28.5")
            st.markdown("**Profit Margin**: 25.3% | **Debt-to-Equity**: 1.05")
            st.markdown("---")
            st.markdown("### OpenInsider C-Suite Form 4 Cluster (60-Day)")
            st.markdown("- **Purchases**: 4")
            st.markdown("- **Sales**: 0")
            st.success("Net Activity: **ACCUMULATION**")
            
        with st.expander("📰 Sentiment & Macro (VIX)"):
            st.metric(label="Latest VIX", value="13.50", delta="-1.2%", delta_color="inverse")
            st.success("**Status**: NORMAL (No Fear Surge Detected)")
            st.markdown("**Finviz/Reddit Trend**: Mixed sentiment showing positive divergence against institutional Dark Pool action.")

        with st.expander("🔍 Fetch.AI Decentralized Verification"):
            st.info("**Dark Pool Integrity**: CLEAR (No significant unaligned block distribution)")
            st.success("**Fetch.AI Query**: FINAL NETWORK SIGNAL: STRONG BUY")

        st.divider()
        st.caption("Anti-gravity Quant Desk © 2026 - UI Sandbox rendering.")

if __name__ == "__main__":
    main()
