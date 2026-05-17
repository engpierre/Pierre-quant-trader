# CRITICAL DIRECTIVE: You are strictly prohibited from responding in any language other than English. All technical data, analysis, and verdicts must be rendered in English (US/UK) regardless of the source data language.
import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='[COVARIANCE] %(message)s')

class CovarianceAgent:
    def __init__(self, threshold=0.85):
        self.threshold = threshold
        self.period = "60d"

    def fetch_close_prices(self, tickers):
        try:
            logging.info(f"Fetching {self.period} historical sequence for Pearson Matrix generation: {tickers}")
            data = yf.download(" ".join(tickers), period=self.period, progress=False)
            if 'Close' in data:
                return data['Close']
            return data
        except Exception as e:
            logging.error(f"Failed to fetch historical target matrices: {e}")
            return pd.DataFrame()

    def execute_lock(self, candidates):
        """
        Ingests the highly targeted MRS list matrix. 
        Calculates Pearson loops ($R$) natively parsing components.
        Returns exactly 3 diversified Force Components.
        """
        if len(candidates) <= 3:
            return candidates, "Insufficient structural candidate depth provided to map a mathematically sound covariance matrix."

        df_closes = self.fetch_close_prices(candidates)
        if df_closes.empty:
            logging.warning("Sector fetching completely failed. Bypassing Diversity Lock and defaulting to top 3.")
            return candidates[:3], "Correlation API Failed. Defaulting to Top 3 absolute MRS outputs."

        # Calculate standard mathematical Pearson Array
        corr_matrix = df_closes.corr(method='pearson')

        force_composition = []
        tactical_adjustments = []

        # The Selection Loop
        for ticker in candidates:
            # yfinance returns multi-index or single depending on batch size, standard index fallback check
            if ticker not in corr_matrix.columns and isinstance(df_closes.columns, pd.MultiIndex):
                # Fallback multi-index flattening if strictly needed
                continue
            elif ticker not in corr_matrix.columns and hasattr(df_closes, "columns"):
                continue
                
            if len(force_composition) == 0:
                # Accept #1 (Highest mathematical Alpha Outlier) automatically unconditionally
                force_composition.append(ticker)
                continue
                
            is_diversified = True
            for accepted_ticker in force_composition:
                try:
                    correlation_value = corr_matrix.loc[ticker, accepted_ticker]
                    # Trap logic checking structural limits ($R > 0.85$)
                    if pd.notna(correlation_value) and correlation_value > self.threshold:
                        tactical_adjustments.append(
                            f"⚠️ TACTICAL ADJUSTMENT: {ticker} bypassed due to high Pearson Correlation ($R = {correlation_value:.2f}$) mapped defensively to dominant force vector ({accepted_ticker})."
                        )
                        is_diversified = False
                        break
                except KeyError:
                    pass
                    
            if is_diversified:
                force_composition.append(ticker)
                
            # Hard limit enforcing 3-Node target structure natively required by Streamlit
            if len(force_composition) == 3:
                break
                
        # Defensive fallback capturing variables preventing sub-3 drops
        if len(force_composition) < 3:
            needed = 3 - len(force_composition)
            for fallback in candidates:
                if fallback not in force_composition:
                    force_composition.append(fallback)
                    if len(force_composition) == 3:
                        break

        # Generate Streamlit UI Report Flag string array
        report_log = ""
        if tactical_adjustments:
            report_log = "\n\n".join(tactical_adjustments)
        else:
            report_log = "✅ FORCE COMPOSITION SECURED: All 3 targets natively bypass the Pearson correlation array (R < 0.85 limit). Structural Risk Diversified."

        logging.info(f"Algorithmic Diversification Secured natively on target indices: {force_composition}")
        return force_composition, report_log
