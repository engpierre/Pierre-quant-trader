# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import requests
import time
import json
import os

class SECEDGARIngestor:
    def __init__(self):
        # SEC strict header compliance
        self.headers = {
            "User-Agent": "PierreQuantAgent / contact@pierre-quant.local",
            "Accept-Encoding": "gzip, deflate"
        }
        self.tickers_url = "https://www.sec.gov/files/company_tickers.json"
        self.submissions_url_template = "https://data.sec.gov/submissions/CIK{cik}.json"
        # SEC rate limit is 10 requests per second. Using 0.11s delay to be safe.
        self.rate_limit_delay = 0.11
        self.ticker_to_cik = None

    def _sleep_for_rate_limit(self):
        time.sleep(self.rate_limit_delay)

    def load_ticker_mapping(self):
        """Fetches and builds the ticker to CIK mapping."""
        self._sleep_for_rate_limit()
        response = requests.get(self.tickers_url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        self.ticker_to_cik = {}
        # Iterate over the dict mapping
        for idx, entry in data.items():
            ticker = entry.get('ticker').upper()
            # CIK must be exactly 10 digits zero-padded
            cik = str(entry.get('cik_str')).zfill(10)
            self.ticker_to_cik[ticker] = cik
            
    def get_cik_for_ticker(self, ticker: str) -> str:
        """Returns the 10-digit CIK for a given ticker."""
        if self.ticker_to_cik is None:
            self.load_ticker_mapping()
        
        return self.ticker_to_cik.get(ticker.upper())

    def fetch_recent_insider_and_institutional_filings(self, ticker: str, limit: int = 10):
        """Fetches the recent submissions and extracts Form 4 and 13F filings."""
        cik = self.get_cik_for_ticker(ticker)
        if not cik:
            raise ValueError(f"Could not find CIK for ticker {ticker}")
            
        url = self.submissions_url_template.format(cik=cik)
        self._sleep_for_rate_limit()
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        
        recent_filings = data.get('filings', {}).get('recent', {})
        if not recent_filings:
            return []
            
        forms = recent_filings.get('form', [])
        accession_numbers = recent_filings.get('accessionNumber', [])
        filing_dates = recent_filings.get('filingDate', [])
        primary_documents = recent_filings.get('primaryDocument', [])
        
        extracted_filings = []
        for i in range(len(forms)):
            form_type = forms[i]
            # Check for Form 4 (Insider Trading) or 13F (Institutional Holding)
            if form_type.startswith('4') or form_type.startswith('13F'):
                extracted_filings.append({
                    "ticker": ticker.upper(),
                    "cik": cik,
                    "form_type": form_type,
                    "filing_date": filing_dates[i],
                    "accession_number": accession_numbers[i],
                    # Construct link to the actual filing document
                    "document_url": f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/{accession_numbers[i].replace('-', '')}/{primary_documents[i]}" if primary_documents[i] else None
                })
                
                # Stop if we hit our limit for this specific ticker
                if len(extracted_filings) >= limit:
                    break
                    
        return extracted_filings

def main():
    ingestor = SECEDGARIngestor()
    
    # Demonstration tickers; could be parameterized
    target_tickers = ['PLTR', 'NVDA']
    all_filings = []
    
    print("Initiating SEC EDGAR Data Ingestor...")
    for ticker in target_tickers:
        print(f"Fetching recent Form 4 and 13F filings for {ticker}...")
        try:
            filings = ingestor.fetch_recent_insider_and_institutional_filings(ticker, limit=10)
            all_filings.extend(filings)
            print(f" -> Found {len(filings)} relevant filings.")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            
    # Save to buffer
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sec_intel_buffer.json")
    with open(output_path, "w") as f:
        json.dump({"filings": all_filings}, f, indent=4)
        
    print(f"\nSuccessfully generated payload: {output_path}")

if __name__ == "__main__":
    main()
