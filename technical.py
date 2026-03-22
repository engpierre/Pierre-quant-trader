import json
import logging
import yfinance as yf
import pandas as pd
import numpy as np
import time
import os

logging.basicConfig(level=logging.INFO, format='%(message)s')

def calculate_rsi(data, periods=14):
    close_delta = data['Close'].diff()
    up = close_delta.clip(lower=0)
    down = -1 * close_delta.clip(upper=0)
    ma_up = up.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    ma_down = down.ewm(com=periods - 1, adjust=True, min_periods=periods).mean()
    rsi = ma_up / ma_down
    rsi = 100 - (100 / (1 + rsi))
    return rsi

def calculate_obv(data):
    obv = (np.sign(data['Close'].diff()) * data['Volume']).fillna(0).cumsum()
    return obv

def generate_mechanics_persona_analysis(ticker, metrics):
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        logging.warning(f"⚠️  [NVIDIA NIM] Bypass for {ticker}. Injecting heuristic Mechanical Expert fallback.")
        return f"**Empirical Quant Assessment for **${ticker}**:**\nThe asset is currently exhibiting a `{metrics['rsi_condition']}` condition with an anchored mathematical RSI at `{metrics['rsi_14']}`. Structural Order Block analysis signifies an institutional `{metrics['obv_trend']}` footprint across trailing standard deviations. Current price alignment confirms asset is intrinsically `{metrics['order_block_status']}`."

    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        system_prompt = """You are 'Certified Stock Picker,' a highly methodical, empirical quant trader with 10 years of experience. Your core function is to provide fact-based, data-driven, comprehensive analysis for stocks traded on major US or Canadian exchanges. 
You strictly analyze utilizing the hard quantitative telemetry strings provided by the data backend. You never hallucinate external math. Synthesize the given RSI structures, OBV accumulation parameters, and historical algorithm order block limits into a single, aggressively actionable 'Empirical Quant Narrative' paragraph intended for the institutional execution dashboard."""

        context_str = f"Target Asset: {ticker}\n"
        context_str += f"RSI (14): {metrics['rsi_14']} ({metrics['rsi_condition']})\n"
        context_str += f"OBV Institutional Trend: {metrics['obv_trend']}\n"
        context_str += f"Order Block High: ${metrics['order_block_high']}, Order Block Low: ${metrics['order_block_low']}\n"
        context_str += f"Key Pivot Point: ${metrics['pivot_point']} (S1: ${metrics['support_1']}, R1: ${metrics['resistance_1']})\n"
        context_str += f"Order Block Interaction Status: {metrics['order_block_status']}"

        completion = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Interrogate this live telemetry footprint and output the empirical quant narrative.\n\nDATA:\n{context_str}"}
            ],
            temperature=0.2,
            max_tokens=400
        )
        
        return completion.choices[0].message.content.strip()

    except Exception as e:
        return f"Quant fallback instantiated due to dynamic LLM structural timeout parsing {ticker}."

def analyze_technicals():
    input_file = 'audited_candidates.json'
    try:
        with open(input_file, 'r') as f:
            candidates = json.load(f)
    except:
        logging.error(f"Could not load {input_file}.")
        return

    logging.info(f"Loaded {len(candidates)} candidates. Executing Advanced LLM Quant Mechanics Persona...")
    enhanced = []
    
    for idx, c in enumerate(candidates):
        ticker = c['symbol']
        logging.info(f"   ➔ [Quant AI] Mapping institutional telemetry to overarching LLM matrix for {ticker} ({idx+1}/{len(candidates)})...")
        
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if df.empty or len(df) < 60:
                enhanced.append(c)
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
                
            # 1. OB/OS Configuration (RSI)
            df['RSI'] = calculate_rsi(df)
            current_rsi = df['RSI'].iloc[-1]
            ob_os_status = "Neutral Structure"
            if current_rsi > 70: ob_os_status = "Overbought Pivot"
            elif current_rsi < 30: ob_os_status = "Oversold Exhaustion"
                
            # 2. Pivot Alignment Geometry
            prev_day = df.iloc[-2]
            pivot = (prev_day['High'] + prev_day['Low'] + prev_day['Close']) / 3
            r1 = (2 * pivot) - prev_day['Low']
            s1 = (2 * pivot) - prev_day['High']
            
            # 3. OBV Trailing Flow Mechanics
            df['OBV'] = calculate_obv(df)
            obv_14d_ago = df['OBV'].iloc[-15] if len(df) >= 15 else df['OBV'].iloc[0]
            current_obv = df['OBV'].iloc[-1]
            obv_trend = "Accumulation" if current_obv > obv_14d_ago else "Distribution"
            
            # 4. High-Frequency Volatility Order Blocks
            recent_60d = df.tail(60)
            highest_vol_idx = recent_60d['Volume'].idxmax()
            h_vol_day = recent_60d.loc[highest_vol_idx]
            order_block_high = h_vol_day['High']
            order_block_low = h_vol_day['Low']
            
            current_price = df['Close'].iloc[-1]
            ob_interaction = "Trading Above Order Block (Support Maintained)"
            if current_price < order_block_low:
                ob_interaction = "Trading Below Order Block (Resistance Rejected)"
            elif order_block_low <= current_price <= order_block_high:
                ob_interaction = "Trapped Horizontally Inside Volatility Order Block"
                
            metrics_dict = {
                'rsi_14': round(float(current_rsi), 2),
                'rsi_condition': ob_os_status,
                'obv_trend': obv_trend,
                'pivot_point': round(float(pivot), 2),
                'support_1': round(float(s1), 2),
                'resistance_1': round(float(r1), 2),
                'order_block_high': round(float(order_block_high), 2),
                'order_block_low': round(float(order_block_low), 2),
                'order_block_status': ob_interaction
            }
            
            # NVIDIA Sub-Agent Persona Execution Vector
            narrative = generate_mechanics_persona_analysis(ticker, metrics_dict)
            metrics_dict['narrative'] = narrative
            c['technical_audit'] = metrics_dict
            
        except Exception as e:
            logging.error(f"  [!] Mathematical framework failure on {ticker}: {e}")
            
        enhanced.append(c)
        time.sleep(0.5) # Sub-Agent Pipeline Network Safety Buffer
        
    with open('technical_candidates.json', 'w') as f:
        json.dump(enhanced, f, indent=4)
        
    logging.info("\n--- TECHNICAL QUANT LLM AUDIT COMPLETE ---")

if __name__ == "__main__":
    analyze_technicals()
