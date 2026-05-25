import requests
import sys

def fetch_fred(series_id, api_key, limit=1):
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['observations']
    else:
        raise Exception(f"FRED API Error: {response.status_code} - {response.text}")

def fetch_data(target_arg):
    api_key = '9a4b7197c1ca9e0cfa2ee05a596530c3'
    try:
        t10y2y_obs = fetch_fred(target_arg, api_key, 1)
        walcl_obs = fetch_fred('WALCL', api_key, 2)
        
        yield_curve = float(t10y2y_obs[0]['value'])
        walcl_latest = float(walcl_obs[0]['value'])
        walcl_prev = float(walcl_obs[1]['value'])
        walcl_delta = walcl_latest - walcl_prev
        
        regime = 'Neutral'
        if yield_curve < 0.2 and walcl_delta < 0:
            regime = 'Volatile-Bear (Risk-Off)'
        elif yield_curve >= 0.2 and walcl_delta >= 0:
            regime = 'Trending-Bull (Risk-On)'
            
        print(f"Target Series ({target_arg}): {yield_curve}")
        print(f"WALCL Delta: {walcl_delta}")
        print(f"Macro Environment: {regime}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target_arg = sys.argv[1] if len(sys.argv) > 1 else 'T10Y2Y'
    fetch_data(target_arg)
