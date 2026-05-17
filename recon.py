import requests
import yfinance as yf
import json
import time

token = 'd7tq4bpr01qlbd3l50sgd7tq4bpr01qlbd3l50t0'
res = {}

for t in ['NVDA', 'GLW']:
    try:
        ns = requests.get(f'https://finnhub.io/api/v1/news-sentiment?symbol={t}&token={token}').json()
        time.sleep(1)
        iss = requests.get(f'https://finnhub.io/api/v1/stock/insider-sentiment?symbol={t}&from=2026-01-01&to=2026-05-08&token={token}').json()
        time.sleep(1)
        tk = yf.Ticker(t)
        h = tk.history(period='2d')
        pd = 0
        if len(h) >= 2:
            pd = ((h['Close'].iloc[-1] - h['Close'].iloc[-2]) / h['Close'].iloc[-2]) * 100
            
        mspr_data = iss.get('data', [])
        latest_mspr = mspr_data[-1] if mspr_data else None
            
        res[t] = {
            'buzz': ns.get('buzz', {}).get('buzz', None),
            'mspr': latest_mspr,
            'price_delta': pd
        }
    except Exception as e:
        res[t] = {"error": str(e)}

print(json.dumps(res, indent=2))
