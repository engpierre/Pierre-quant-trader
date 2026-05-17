# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import requests
import json
import os
import sys
from datetime import datetime, timedelta

# Local sentiment processing initialization
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    print("Error: The 'vaderSentiment' library is missing.")
    print("Please run the following command to install it: pip install vaderSentiment")
    sys.exit(1)

API_KEY = "d7tq4bpr01qlbd3l50sgd7tq4bpr01qlbd3l50t0"
BASE_URL = "https://finnhub.io/api/v1/company-news"

def fetch_local_sentiment(ticker):
    # Dynamically calculate dates
    to_date = datetime.now()
    from_date = to_date - timedelta(days=7)
    
    params = {
        'symbol': ticker,
        'from': from_date.strftime('%Y-%m-%d'),
        'to': to_date.strftime('%Y-%m-%d')
    }
    headers = {
        'X-Finnhub-Token': API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        articles = response.json()
        
        if not isinstance(articles, list):
            print(f"Warning: Unexpected data format received for ticker {ticker}.")
            return None
            
        analyzer = SentimentIntensityAnalyzer()
        bullish_count = 0
        bearish_count = 0
        total_articles = len(articles)
        
        for article in articles:
            headline = article.get('headline', '')
            if headline:
                # Calculate compound sentiment score for the headline
                score = analyzer.polarity_scores(headline)
                compound = score['compound']
                
                # Aggregate bullish and bearish
                if compound >= 0.05:
                    bullish_count += 1
                elif compound <= -0.05:
                    bearish_count += 1
                    
        # Calculate percentages
        if total_articles > 0:
            bullish_percent = (bullish_count / total_articles) * 100
            bearish_percent = (bearish_count / total_articles) * 100
        else:
            bullish_percent = 0
            bearish_percent = 0
            
        # Determine Local Buzz
        is_high_buzz = total_articles > 20
        
        # Ensure consistent output structure so Geopolitical and Critic agents don't break
        return {
            "ticker": ticker.upper(),
            "buzz": {
                "articlesInLastWeek": total_articles,
                "buzz": total_articles, # Using total articles as the raw buzz metric locally
                "weeklyAverage": 20, 
                "isHighVolatility": is_high_buzz
            },
            "sentiment": {
                "bullishPercent": round(bullish_percent, 2),
                "bearishPercent": round(bearish_percent, 2)
            },
            "sectorComparison": {
                "sectorAverageBullishPercent": None, # Unavailable via free tier company-news
                "sectorAverageNewsScore": None
            }
        }

    except requests.exceptions.Timeout:
        print(f"Error: Connection timed out while fetching data for {ticker}.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error: API request failed for {ticker}. Details: {e}")
        return None
    except ValueError:
        print(f"Error: Invalid JSON response received for {ticker}.")
        return None

def main():
    # Execute a test run on PLTR as requested
    tickers = ["PLTR"]
    all_sentiment_data = {}
    
    print("Initiating Operation Sentiment Pulse (Local Intelligence Model)...")
    
    for ticker in tickers:
        print(f"Fetching and analyzing local sentiment for {ticker}...")
        sentiment_info = fetch_local_sentiment(ticker)
        if sentiment_info:
            all_sentiment_data[ticker] = sentiment_info
            print(f" -> Successfully processed local sentiment for {ticker}.")
            print(f" -> Headlines analyzed: {sentiment_info['buzz']['articlesInLastWeek']}")
            print(f" -> Bullish Sentiment: {sentiment_info['sentiment']['bullishPercent']}%")
        else:
            print(f" -> Failed to process local sentiment for {ticker}.")
            
    # Save the processed data to sentiment_intel_buffer.json (overwriting existing)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sentiment_intel_buffer.json")
    try:
        with open(output_path, "w") as f:
            json.dump({"sentiments": all_sentiment_data}, f, indent=4)
        print(f"\nSuccessfully generated tactical payload: {output_path}")
    except IOError as e:
        print(f"Failed to write to {output_path}: {e}")

if __name__ == "__main__":
    main()
