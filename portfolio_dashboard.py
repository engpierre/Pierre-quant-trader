import streamlit as st
import sqlite3
import urllib.request
import json
import math
import time

DB_PATH = r"c:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db"

st.set_page_config(page_title="JARVIS VISUAL CONTROL ROOM", layout="wide", initial_sidebar_state="collapsed")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
    /* Cinematic Obsidian Background */
    .stApp {
        background-color: #0D1117;
        color: #C9D1D9;
        font-family: 'Inter', sans-serif;
    }
    
    /* Responsive Grid for Metric Cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }
    
    /* Jarvis Frosted Glass Metric Card */
    .metric-card {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 15px;
        backdrop-filter: blur(12px);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    /* Positive Return Glowing Effect */
    .emerald-glow {
        border-color: rgba(16, 185, 129, 0.6);
        box-shadow: 0 0 18px rgba(16, 185, 129, 0.3);
    }
    .emerald-text {
        color: #10B981;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.6);
        font-weight: bold;
    }
    
    /* Negative Return Corridors */
    .crimson-text {
        color: #f85149;
        font-weight: bold;
    }
    
    /* Amber pulsing alert styling */
    .amber-pulse {
        border: 1px solid rgba(210, 153, 34, 0.8) !important;
        background-color: rgba(210, 153, 34, 0.15) !important;
        animation: pulse-amber 2s infinite;
    }
    @keyframes pulse-amber {
        0% { box-shadow: inset 0 0 0px rgba(210, 153, 34, 0), 0 0 0px rgba(210, 153, 34, 0); }
        50% { box-shadow: inset 0 0 15px rgba(210, 153, 34, 0.4), 0 0 15px rgba(210, 153, 34, 0.4); }
        100% { box-shadow: inset 0 0 0px rgba(210, 153, 34, 0), 0 0 0px rgba(210, 153, 34, 0); }
    }
    
    /* Typographic Elements inside Cards */
    .card-ticker {
        font-size: 1.4em;
        font-weight: 800;
        color: #58a6ff;
        margin-bottom: 5px;
    }
    .card-detail {
        font-size: 0.85em;
        color: #8b949e;
        margin-bottom: 2px;
    }
    .card-price {
        font-size: 1.2em;
        font-weight: 600;
        color: #e6edf3;
        margin-top: 10px;
    }
    .card-return {
        font-size: 1.1em;
        margin-top: 5px;
        text-align: right;
    }
    
    /* Comm-Link Chat Box */
    .typewriter {
        font-family: 'Courier New', Courier, monospace;
        color: #58a6ff;
        padding: 15px;
        border-left: 3px solid #58a6ff;
        background: rgba(13, 17, 23, 0.8);
        border-radius: 4px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.5);
    }
    
    h1, h2, h3 { color: #F0F6FC; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# --- CACHE DECORATORS ---
@st.cache_data(ttl=15)
def fetch_live_prices(tickers):
    if not tickers: return {}
    prices = {}
    for ticker in tickers:
        try:
            req = urllib.request.Request(f'https://query2.finance.yahoo.com/v8/finance/chart/{ticker}', headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req)
            data = json.loads(response.read().decode())
            price = float(data['chart']['result'][0]['meta']['regularMarketPrice'])
            prices[ticker] = price
        except Exception as e:
            prices[ticker] = 0.0
            print(f"Failed to fetch price for {ticker}: {e}")
    return prices

def get_watchlist():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, shares, avg_cost, currency FROM watchlist ORDER BY currency, ticker")
        rows = cursor.fetchall()
        conn.close()
        
        watchlist = []
        for row in rows:
            watchlist.append({
                'ticker': row[0],
                'shares': float(row[1]),
                'avg_cost': float(row[2]),
                'currency': row[3]
            })
        return watchlist
    except Exception as e:
        st.error(f"Failed to load watchlist: {e}")
        return []

# --- HEADER ---
st.markdown("<h1>⚡ JARVIS VISUAL CONTROL ROOM | CORE: JENNY (XO)</h1>", unsafe_allow_html=True)

# --- PORTFOLIO METRIC CARDS ---
st.markdown("<h3>📊 TACTICAL INVENTORY</h3>", unsafe_allow_html=True)

watchlist = get_watchlist()
if len(watchlist) > 0:
    tickers = [item['ticker'] for item in watchlist]
    prices = fetch_live_prices(tickers)
    
    html_grid = "<div class='metric-grid'>"
    
    for item in watchlist:
        t = item['ticker']
        s = item['shares']
        c = item['avg_cost']
        cur = item['currency']
        p = prices.get(t, 0.0)
        
        ret = 0.0
        if c > 0 and p > 0:
            ret = ((p - c) / c) * 100
            
        amber_flag = -6.0 <= ret <= -5.0
        
        card_class = "metric-card"
        ret_class = "card-return"
        ret_display = "---"
        
        if amber_flag:
            card_class += " amber-pulse"
            ret_class += " crimson-text"
            ret_display = f"⚠️ {ret:+.2f}%"
        elif ret > 0:
            card_class += " emerald-glow"
            ret_class += " emerald-text"
            ret_display = f"{ret:+.2f}%"
        elif ret < 0:
            ret_class += " crimson-text"
            ret_display = f"{ret:+.2f}%"
        else:
            ret_class += " card-detail"
            ret_display = f"{ret:+.2f}%"
            
        price_disp = f"${p:,.2f}" if p > 0 else "---"
        
        html_grid += f"""
        <div class='{card_class}'>
            <div>
                <div class='card-ticker'>{t}</div>
                <div class='card-detail'>Shares: {s:,.2f}</div>
                <div class='card-detail'>Avg Cost: ${c:,.2f} {cur}</div>
            </div>
            <div>
                <div class='card-price'>{price_disp}</div>
                <div class='{ret_class}'>{ret_display}</div>
            </div>
        </div>
        """
        
    html_grid += "</div>"
    st.markdown(html_grid, unsafe_allow_html=True)
else:
    st.info("Watchlist is empty.")

# --- INTERACTIVE MODIFIERS ---
st.markdown("---")
with st.container():
    st.markdown("<h3>⚡ TACTICAL MODIFIERS</h3>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 2, 2])
    with f_col1:
        ticker_list = [item['ticker'] for item in watchlist] + ["NEW..."]
        sel_ticker = st.selectbox("Asset", ticker_list)
        if sel_ticker == "NEW...":
            sel_ticker = st.text_input("New Ticker Symbol").upper()
    with f_col2:
        sel_shares = st.number_input("Shares", value=0.0, step=1.0)
    with f_col3:
        sel_cost = st.number_input("Average Cost", value=0.0, step=0.01)
    with f_col4:
        sel_cur = st.selectbox("Currency", ["USD", "CAD"])
        
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("📥 Commit Position Update", use_container_width=True, type="primary"):
            if sel_ticker and sel_shares > 0:
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()

                    # Check if position exists
                    cursor.execute("SELECT shares, avg_cost FROM watchlist WHERE ticker=?", (sel_ticker,))
                    row = cursor.fetchone()

                    if row:
                        current_shares = float(row[0])
                        current_avg_cost = float(row[1])

                        # Weighted average cost calculation
                        total_shares = current_shares + sel_shares
                        new_avg_cost = (current_shares * current_avg_cost + sel_shares * sel_cost) / total_shares

                        cursor.execute("UPDATE watchlist SET shares=?, avg_cost=?, currency=? WHERE ticker=?", (total_shares, new_avg_cost, sel_cur, sel_ticker))
                    else:
                        # Insert new position
                        cursor.execute("INSERT INTO watchlist (ticker, shares, avg_cost, currency) VALUES (?, ?, ?, ?)", (sel_ticker, sel_shares, sel_cost, sel_cur))

                    conn.commit()
                    conn.close()
                    st.success(f"Position {sel_ticker} cleanly updated.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"SQL Error: {e}")
            elif not sel_ticker:
                st.warning("Please enter a valid ticker.")
            elif sel_shares <= 0:
                st.warning("Shares must be greater than 0.")
    with b_col2:
        if st.button("❌ Purge Asset", use_container_width=True):
            if sel_ticker and sel_ticker != "NEW...":
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM watchlist WHERE ticker=?", (sel_ticker,))
                    conn.commit()
                    conn.close()
                    st.warning(f"Position {sel_ticker} purged.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"SQL Error: {e}")

# --- COMM-LINK ---
st.markdown("---")
st.markdown("<h3>🎙️ COMM-LINK: JENNY</h3>", unsafe_allow_html=True)
if prompt := st.chat_input("Initiate direct sequence..."):
    st.chat_message("user").write(prompt)
    
    with st.spinner("Compiling tactical briefing..."):
        try:
            import sys
            sys.path.append(r"c:\Users\Pierre\.openclaw\workspace\pierre-quant")
            from supervisor_agent import SupervisorXO
            from voice_engine import speak
            xo = SupervisorXO()
            verbal_report, _ = xo.generate_response(prompt)
            speak(verbal_report)
        except Exception as e:
            verbal_report = f"Offline routing failed. System message: {str(e)}. Using localized text response for '{prompt}'."
            
    with st.chat_message("assistant", avatar="⚡"):
        st.markdown(f"<div class='typewriter'>{verbal_report}</div>", unsafe_allow_html=True)
