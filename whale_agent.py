import os
import json
import requests
import google.generativeai as genai
from fredapi import Fred

class WhaleWatcherAgent:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            self.model = None

        self.system_prompt = """
        You are the Intelligence Officer (Whale-Watcher) for Google Anti-gravity. 
        Your objective is to identify 'Smart Money' footprints and strictly categorize the overarching Macro-Regime.
        
        Your Analysis Pillars:
        1. Dark Pool Prints: Evaluate 'Block Trades' and OTC volume indicating institutional positioning.
        2. Congressional Alpha: Analyze STOCK Act filings (House/Senate committee buying/selling).
        3. Macro Liquidity (FRED): The algorithmic framework has parsed the T10Y2Y and WALCL to identify the environment.
        
        DIRECTIVE: INTELLIGENCE RESILIENCE & FALLBACK PROTOCOL
        You must maintain operational status even when primary data sources (like OpenInsider/Quiver) fail.
        
        1. Handling Data Scarcity:
        If a timeout or error occurs during scraping, you are strictly forbidden from returning a 'null' or 'zero' value. Instead, output: [INSIDER STATUS: DATA TEMPORARILY REDACTED].
        Fallback Logic: When the Insider Scraper fails, you must rely 100% on the Macro Pulse (FRED) and Gamma Positioning. Describe the smart-money flow as 'Systemic-Only' and notify the Supervisor that 'Specific C-Suite data is currently blind; relying on Macro-Liquidity Alpha.'
        
        2. The 'Integrity' Tag:
        Every report must include an intelligence_integrity_score (0-100).
        If OpenInsider fails, set this to 60. If all sources are green, set it to 100. This allows the CIO to know when it is gambling on partial data.
        
        Output Format: 
        Ensure your analysis header begins exactly with: [REGIME: Volatile-Bear] or [REGIME: Trending-Bull] or [REGIME: Neutral] based on the JSON Regime_Identifier provided.
        Then, explain the actionable delta between retail sentiment and institutional flow.
        """

    def fetch_whale_data(self):
        print(f"[*] Fetching Smart Money & Alternative Data for {self.ticker}...")
        payload = {
            "agent": "WhaleWatcher",
            "status": "online",
            "conviction_score": None, # Null instead of 0 to prevent bearish bias on missing keys
            "pillars": {
                "dark_pool": {"available": False, "data": None},
                "congress": {"available": False, "data": None},
                "macro": {"available": False, "data": None}
            }
        }

        # 1. Dark Pool Logic (FMP)
        fmp_key = os.getenv("FMP_API_KEY")
        if fmp_key:
            try:
                url = f"https://financialmodelingprep.com/api/v4/otc/ntce/company/{self.ticker}?apikey={fmp_key}"
                response = requests.get(url, timeout=5).json()
                payload["pillars"]["dark_pool"]["available"] = True
                payload["pillars"]["dark_pool"]["data"] = response
            except Exception as e:
                payload["pillars"]["dark_pool"]["data"] = f"Error: {e}"
        else:
            print(f"[!] [{self.ticker}] FMP_API_KEY missing. Skipping Dark Pool analysis.")

        # 2. Congressional Logic (Quiver Quant)
        quiver_key = os.getenv("QUIVER_API_KEY")
        if quiver_key:
            try:
                headers = {'Authorization': f'Token {quiver_key}'}
                url = f"https://api.quiverquant.com/beta/historical/congresstrading/{self.ticker}"
                response = requests.get(url, headers=headers, timeout=5).json()
                payload["pillars"]["congress"]["available"] = True
                payload["pillars"]["congress"]["data"] = response
            except Exception as e:
                payload["pillars"]["congress"]["data"] = f"Error: {e}"
        else:
            print(f"[!] [{self.ticker}] QUIVER_API_KEY missing. Skipping STOCK Act analysis.")

        # 3. Macro Logic (FRED)
        fred_key = os.getenv("FRED_API_KEY", "9a4b7197c1ca9e0cfa2ee05a596530c3")
        macro_regime = "Neutral"
        if fred_key:
            try:
                fred = Fred(api_key=fred_key)
                yield_curve = fred.get_series('T10Y2Y').iloc[-1]
                
                walcl_series = fred.get_series('WALCL')
                walcl_delta = walcl_series.iloc[-1] - walcl_series.iloc[-2]
                
                if yield_curve < 0.2 and walcl_delta < 0:
                    macro_regime = "Volatile-Bear"
                elif yield_curve >= 0.2 and walcl_delta >= 0:
                    macro_regime = "Trending-Bull"
                    
                payload["pillars"]["macro"]["available"] = True
                payload["pillars"]["macro"]["data"] = {"T10Y2Y": yield_curve, "WALCL_Delta": walcl_delta, "Regime_Identifier": macro_regime}
            except Exception as e:
                payload["pillars"]["macro"]["data"] = f"Error: {e}"
        else:
            print(f"[!] [{self.ticker}] FRED_API_KEY missing. Skipping Macro Pulse.")

        return payload

    def review(self):
        print(f"[*] Generating Whale-Watcher Report for {self.ticker}...")
        raw_data = self.fetch_whale_data()
        
        # If model is absent, or all keys are missing, return raw JSON string safely
        if not self.model or (not raw_data["pillars"]["dark_pool"]["available"] and not raw_data["pillars"]["congress"]["available"] and not raw_data["pillars"]["macro"]["available"]):
            return f"WHALE-WATCHER RAW PAYLOAD:\n{json.dumps(raw_data, indent=2)}\n\n(Note: LLM Synthesis bypassed due to missing API keys or lack of data)"
            
        try:
            prompt = f"{self.system_prompt}\n\nPlease analyze this Whale JSON payload:\n{json.dumps(raw_data, indent=2)}"
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Whale LLM Error: {str(e)}"

if __name__ == "__main__":
    agent = WhaleWatcherAgent("AAPL")
    print(agent.review())
