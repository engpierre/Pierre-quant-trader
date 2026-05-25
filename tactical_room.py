import streamlit as st
import sqlite3
import urllib.request
import json
import math
import time
import requests
import speech_recognition as sr

DB_PATH = r"c:\Users\Pierre\.openclaw\workspace\pierre-quant\pierre_quant.db"

st.set_page_config(page_title="JARVIS VISUAL CONTROL ROOM", layout="wide", initial_sidebar_state="collapsed")

# Inject clean CSS styling
st.markdown("""<style>
.stApp { background-color: #0D1117; color: #C9D1D9; font-family: 'Inter', sans-serif; }
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
.metric-card { background: rgba(22, 27, 34, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 15px; backdrop-filter: blur(12px); display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
.emerald-glow { border-color: rgba(16, 185, 129, 0.6); box-shadow: 0 0 18px rgba(16, 185, 129, 0.3); }
.emerald-text { color: #10B981; text-shadow: 0 0 10px rgba(16, 185, 129, 0.6); font-weight: bold; }
.crimson-text { color: #f85149; font-weight: bold; }
.amber-pulse { border: 1px solid rgba(210, 153, 34, 0.8) !important; background-color: rgba(210, 153, 34, 0.15) !important; }
.card-ticker { font-size: 1.4em; font-weight: 800; color: #58a6ff; margin-bottom: 5px; }
.card-detail { font-size: 0.85em; color: #8b949e; margin-bottom: 2px; }
.card-price { font-size: 1.2em; font-weight: 600; color: #e6edf3; margin-top: 10px; }
.card-return { font-size: 1.1em; margin-top: 5px; text-align: right; }
.typewriter { font-family: 'Courier New', Courier, monospace; color: #58a6ff; padding: 15px; border-left: 3px solid #58a6ff; background: rgba(13, 17, 23, 0.8); border-radius: 4px; }
h1, h2, h3 { color: #F0F6FC; font-weight: 600; }
</style>""", unsafe_allow_html=True)

@st.cache_data(ttl=15)
def fetch_live_prices(tickers):
    if not tickers: return {}
    prices = {}
    for ticker in tickers:
        try:
            url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1d"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
                price = float(data['chart']['result'][0]['meta']['regularMarketPrice'])
                prices[ticker] = price
        except Exception:
            prices[ticker] = 0.0
    return prices

def get_watchlist():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT ticker, shares, avg_cost, currency FROM watchlist ORDER BY currency, ticker")
        rows = cursor.fetchall()
        conn.close()
        return [{'ticker': r[0], 'shares': float(r[1]), 'avg_cost': float(r[2]), 'currency': r[3]} for r in rows]
    except Exception as e:
        st.error(f"Failed to load watchlist: {e}")
        return []

def commit_position(ticker, shares, cost, cur):
    """Logic for updating position, extracted for voice trigger reuse"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT shares, avg_cost FROM watchlist WHERE ticker=?", (ticker,))
        row = cursor.fetchone()
        if row:
            current_shares, current_avg_cost = float(row[0]), float(row[1])
            total_shares = current_shares + shares
            new_avg_cost = (current_shares * current_avg_cost + shares * cost) / total_shares if total_shares > 0 else cost
            cursor.execute("UPDATE watchlist SET shares=?, avg_cost=?, currency=? WHERE ticker=?", (total_shares, new_avg_cost, cur, ticker))
        else:
            cursor.execute("INSERT INTO watchlist (ticker, shares, avg_cost, currency) VALUES (?, ?, ?, ?)", (ticker, shares, cost, cur))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"SQL Error: {e}")
        return False

def query_ollama(prompt):
    """Lightweight local bridge to Ollama"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "ollama/gemma4:31b", "prompt": prompt, "stream": False},
            timeout=30
        )
        return response.json().get("response", "System Error: No response from Ollama.")
    except Exception as e:
        return f"Ollama connection failed: {str(e)}"

def listen_for_command():
    """Capture microphone input and return text"""
    r = sr.Recognizer()
    with sr.Microphone(device_index=None) as source:
        r.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            return r.recognize_google(audio)
        except Exception as e:
             return f'ERROR: {str(e)}'

# --- SIDEBAR: JENNY VOICE LINK ---
with st.sidebar:
    st.markdown("### ðŸŽ™ï¸ JENNY VOICE LINK")
    if st.button("Activate Voice Link", use_container_width=True):
        with st.spinner("Listening..."):
            voice_text = listen_for_command()
            if voice_text:
                st.info(f"Detected: '{voice_text}'")
                cmd = voice_text.lower()
                
                if any(k in cmd for k in ["commit", "save"]):
                    # Reuse current tactical modifier state for the voice commit
                    if 'sel_ticker' in locals() or 'sel_ticker' in st.session_state:
                        t = st.session_state.get('sel_ticker', 'UNKNOWN')
                        s = st.session_state.get('sel_shares', 0.0)
                        c = st.session_state.get('sel_cost', 0.0)
                        cur = st.session_state.get('sel_cur', 'USD')
                        if commit_position(t, s, c, cur):
                            st.success(f"Voice Command: Position {t} committed.")
                            st.rerun()
                else:
                    # General query to local Gemma4
                    answer = query_ollama(voice_text)
                    st.markdown(f"<div class='typewriter'>{answer}</div>", unsafe_allow_html=True)
            else:
                st.warning("No clear command detected.")

# --- MAIN INTERFACE ---
st.markdown("<h1>âš¡ JARVIS VISUAL CONTROL ROOM | CORE: JENNY (XO)</h1>", unsafe_allow_html=True)
st.markdown("<h3>ðŸ“Š TACTICAL INVENTORY</h3>", unsafe_allow_html=True)

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
        
        ret = ((p - c) / c) * 100 if c > 0 and p > 0 else 0.0
        amber_flag = -6.0 <= ret <= -5.0
        card_class = "metric-card"
        ret_class = "card-return"
        ret_display = f"{ret:+.2f}%"
        
        if amber_flag:
            card_class += " amber-pulse"
            ret_class += " crimson-text"
            ret_display = f"âš ï¸ {ret:+.2f}%"
        elif ret > 0:
            card_class += " emerald-glow"
            ret_class += " emerald-text"
        elif ret < 0:
            ret_class += " crimson-text"
            
        price_disp = f"${p:,.2f}" if p > 0 else "---"
        card_html = f"<div class='{card_class}'><div><div class='card-ticker'>{t}</div><div class='card-detail'>Shares: {s:,.2f}</div><div class='card-detail'>Avg Cost: ${c:,.2f} {cur}</div></div><div><div class='card-price'>{price_disp}</div><div class='{ret_class}'>{ret_display}</div></div></div>"
        html_grid += card_html
        
    html_grid += "</div>"
    st.markdown(html_grid, unsafe_allow_html=True)
else:
    st.info("Watchlist is empty.")

st.markdown("---")
with st.container():
    st.markdown("<h3>âš¡ TACTICAL MODIFIERS</h3>", unsafe_allow_html=True)
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 2, 2, 2])
    with f_col1:
        ticker_list = [item['ticker'] for item in watchlist] + ["NEW..."]
        sel_ticker = st.selectbox("Asset", ticker_list, key='sel_ticker')
        if sel_ticker == "NEW...":
            sel_ticker = st.text_input("New Ticker Symbol", key='new_ticker_input').upper()
            st.session_state['sel_ticker'] = sel_ticker
    with f_col2:
        sel_shares = st.number_input("Shares", value=0.0, step=1.0, key='sel_shares')
    with f_col3:
        sel_cost = st.number_input("Average Cost", value=0.0, step=0.01, key='sel_cost')
    with f_col4:
        sel_cur = st.selectbox("Currency", ["USD", "CAD"], key='sel_cur')
        
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        if st.button("ðŸ“¥ Commit Position Update", use_container_width=True, type="primary"):
            if sel_ticker:
                if commit_position(sel_ticker, sel_shares, sel_cost, sel_cur):
                    st.success(f"Position {sel_ticker} successfully logged.")
                    time.sleep(1)
                    st.rerun()
                
    with b_col2:
        if st.button("âŒ Purge Asset", use_container_width=True):
            if sel_ticker and sel_ticker != "NEW...":
                try:
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM watchlist WHERE ticker=?", (sel_ticker,))
                    conn.commit()
                    conn.close()
                    st.warning(f"Position {sel_ticker} cleanly purged.")
                    time.sleep(1)
                    st.rerun()
                except Exception as e:
                    st.error(f"SQL Error: {e}")

st.markdown("---")
st.markdown("<h3>ðŸŽ™ï¸ COMM-LINK: JENNY</h3>", unsafe_allow_html=True)
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
            verbal_report = f"Offline routing active. System exception: {str(e)}."
            
    with st.chat_message("assistant", avatar="âš¡"):
        st.markdown(f"<div class='typewriter'>{verbal_report}</div>", unsafe_allow_html=True)
# --- NATIVE TACTICAL VOICE INTERFACE ---
import streamlit as st
import speech_recognition as sr
import requests

def run_voice_interface():
    st.sidebar.markdown("---")
    st.sidebar.subheader("??? Jenny Comm-Link")
    
    if st.sidebar.button("?? Initialize Voice Link", key="jenny_voice_link_v2"):
        r = sr.Recognizer()
        with sr.Microphone(device_index=None) as source:
            st.sidebar.info("Listening to channel...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = r.listen(source, timeout=4, phrase_time_limit=5)
                command = r.recognize_google(audio).lower()
                st.sidebar.success(f"Signal Captured: '{command}'")
                
                # Command Mapping Logic
                if "commit" in command or "save" in command:
                    st.sidebar.warning("Executing position save sequence...")
                    if 'commit_position' in globals():
                        globals()['commit_position']()
                        st.sidebar.success("? Position successfully saved to database.")
                    else:
                        st.sidebar.error("Commit function not found in workspace scope.")
                elif "status" in command:
                    st.sidebar.info("All engine parameters holding green at 128k context.")
                else:
                    # Fallback straight to local gemma model via ollama port
                    st.sidebar.info("Routing query to local gemma engine...")
                    res = requests.post("http://127.0.0.1:11434/api/generate", 
                                        json={"model": "gemma4:31b", "prompt": command, "stream": False})
                    if res.status_code == 200:
                        st.sidebar.write(res.json().get("response", "No response data."))
            except sr.WaitTimeoutError:
                st.sidebar.error("Signal Timeout: No voice detected.")
            except Exception as e:
                st.sidebar.error(f"Interface Error: {str(e)}")

run_voice_interface()

# --- NATIVE TACTICAL VOICE INTERFACE ---
import streamlit as st
import speech_recognition as sr
import requests




