# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import json
import os
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange

class TVPullAgent:
    def __init__(self, buffer_path=r'c:\Users\Pierre\.openclaw\workspace\pierre-quant\technical_intel_buffer.json'):
        self.buffer_path = buffer_path

    def fetch_technicals(self, symbol, screener="america", interval=Interval.INTERVAL_1_MINUTE):
        """
        Dynamically fetches technical indicators from TradingView.
        """
        try:
            # Multi-Asset Auto-Detection
            # If the ticker contains 'USD', we pivot to the Crypto Screener.
            is_crypto = "USD" in symbol or "BTC" in symbol
            current_screener = "crypto" if is_crypto else "america"
            current_exchange = "BINANCE" if is_crypto else "NASDAQ"

            handler = TA_Handler(
                symbol=symbol,
                screener=current_screener,
                exchange=current_exchange,
                interval=interval
            )
            
            analysis = handler.get_analysis()
            
            payload = {
                "ticker": symbol,
                "price": analysis.indicators.get("close"),
                "rsi": analysis.indicators.get("RSI"),
                "ema20": analysis.indicators.get("EMA20"),
                "adx": analysis.indicators.get("ADX"),
                "recommendation": analysis.summary.get("RECOMMENDATION"),
                "buy_signals": analysis.summary.get("BUY"),
                "sell_signals": analysis.summary.get("SELL"),
                "timestamp": datetime.now().isoformat(),
                "status": "SUCCESS"
            }
            
            self._update_buffer(payload)
            return payload

        except Exception as e:
            error_payload = {"ticker": symbol, "status": "ERROR", "message": str(e)}
            self._update_buffer(error_payload)
            return error_payload

    def _update_buffer(self, data):
        # Safely merge into the global technicals object to avoid overwriting other tickers
        buffer_data = {"technicals": {}}
        if os.path.exists(self.buffer_path):
            with open(self.buffer_path, 'r', encoding='utf-8') as f:
                try:
                    buffer_data = json.load(f)
                except json.JSONDecodeError:
                    pass
                    
        if "technicals" not in buffer_data:
            buffer_data["technicals"] = {}
            
        ticker = data.get("ticker")
        if ticker:
            buffer_data["technicals"][ticker] = data
            
        with open(self.buffer_path, 'w', encoding='utf-8') as f:
            json.dump(buffer_data, f, indent=2)

if __name__ == "__main__":
    import sys
    ticker = sys.argv[1] if len(sys.argv) > 1 else "NVDA"
    agent = TVPullAgent()
    result = agent.fetch_technicals(ticker)
    print(json.dumps(result, indent=2))
