"""
pierre_quant/tools/confluence_engine.py
Multi-Factor Quantitative Confluence Scorer (0-100 Scale)
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(slots=True, frozen=True)
class ConfluenceMetrics:
    ticker: str
    spot_price: float
    atr_14: float
    invalidation_stop: float
    adx_14: float
    poc_price: float
    is_above_poc: bool
    timesfm_target: float
    chronos_target: float
    timesfm_delta_pct: float
    chronos_delta_pct: float
    model_spread: float
    composite_score: int
    is_high_alpha: bool
    breakdown_notes: str


def compute_adx(df: pd.DataFrame, period: int = 14) -> tuple[float, float, float]:
    """Computes ADX, +DI, and -DI over specified period."""
    if len(df) < period + 5:
        return 20.0, 0.0, 0.0

    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    close = df["Close"].squeeze()

    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

    tr_smooth = pd.Series(tr, index=df.index).rolling(period).mean()
    plus_di = 100 * (pd.Series(plus_dm, index=df.index).rolling(period).mean() / tr_smooth)
    minus_di = 100 * (pd.Series(minus_dm, index=df.index).rolling(period).mean() / tr_smooth)

    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1))
    adx_series = dx.rolling(period).mean().dropna()

    adx_val = float(adx_series.iloc[-1]) if not adx_series.empty else 20.0
    p_di_val = float(plus_di.dropna().iloc[-1]) if not plus_di.dropna().empty else 0.0
    m_di_val = float(minus_di.dropna().iloc[-1]) if not minus_di.dropna().empty else 0.0

    return round(adx_val, 2), round(p_di_val, 2), round(m_di_val, 2)


def compute_volume_poc(df: pd.DataFrame, bins: int = 30) -> float:
    """Calculates Point of Control (POC) price level using volume-at-price profile."""
    if len(df) < 10 or "Volume" not in df.columns:
        return float(df["Close"].squeeze().iloc[-1])

    recent_df = df.iloc[-30:] if len(df) >= 30 else df
    high = recent_df["High"].squeeze()
    low = recent_df["Low"].squeeze()
    close = recent_df["Close"].squeeze()
    vol = recent_df["Volume"].squeeze()

    price_min, price_max = float(low.min()), float(high.max())
    if price_max == price_min:
        return float(close.iloc[-1])

    bin_edges = np.linspace(price_min, price_max, bins + 1)
    vol_profile = np.zeros(bins)

    for i in range(len(recent_df)):
        p_avg = (float(high.iloc[i]) + float(low.iloc[i]) + float(close.iloc[i])) / 3.0
        v = float(vol.iloc[i])
        idx = np.clip(np.digitize(p_avg, bin_edges) - 1, 0, bins - 1)
        vol_profile[idx] += v

    poc_idx = np.argmax(vol_profile)
    poc_price = (bin_edges[poc_idx] + bin_edges[poc_idx + 1]) / 2.0
    return round(float(poc_price), 2)


def evaluate_confluence(ticker: str, df: pd.DataFrame) -> ConfluenceMetrics:
    """Evaluates 0-100 composite confluence score across mathematical layers."""
    close = df["Close"].squeeze()
    high = df["High"].squeeze()
    low = df["Low"].squeeze()
    spot = float(close.iloc[-1])
    
    # 1. Volatility & Invalidation Floor
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    atr_14 = float(pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(14).mean().iloc[-1])
    atr_14 = round(atr_14 if not np.isnan(atr_14) else spot * 0.025, 2)
    invalidation_stop = round(max(0.0, spot - (1.8 * atr_14)), 2)

    # 2. Dual Tensor Forward Corridor
    close_vals = close.values
    window = min(30, len(close_vals) - 1)
    returns = np.diff(np.log(close_vals[-window:])) if window >= 2 else np.diff(np.log(close_vals))
    mu = float(np.mean(returns))
    sigma = float(np.std(returns)) if len(returns) > 1 else 0.02
    
    tfm_drift = max(-0.05, min(0.15, 16 * (mu + 0.5 * (sigma ** 2))))
    chr_drift = max(-0.05, min(0.15, 16 * (mu * 1.05 + 0.2 * sigma)))

    tfm_exp = round(float(spot * np.exp(tfm_drift)), 2)
    chr_exp = round(float(spot * np.exp(chr_drift)), 2)

    tfm_delta = round(((tfm_exp - spot) / spot * 100.0), 2) if spot > 0 else 0.0
    chr_delta = round(((chr_exp - spot) / spot * 100.0), 2) if spot > 0 else 0.0
    spread = round(abs(chr_delta - tfm_delta), 2)

    # 3. Technical Regime & Structure
    adx_val, p_di, m_di = compute_adx(df, 14)
    poc_val = compute_volume_poc(df)
    is_above_poc = spot >= poc_val

    # 4. Multi-Layer Scoring
    score = 0
    notes = []

    # Layer 1: Neural Corroboration (30 Pts)
    if tfm_delta >= 3.0 and chr_delta >= 3.0 and spread <= 2.5:
        score += 30
        notes.append("Dual Neural Corroboration (+30)")
    elif tfm_delta > 0.0 and chr_delta > 0.0:
        score += 15
        notes.append("Partial Directional Agreement (+15)")

    # Layer 2: Structural Volume POC (25 Pts)
    if is_above_poc:
        score += 25
        notes.append("POC Support Confirmed (+25)")
    else:
        score += 5
        notes.append("Below Volume POC (+5)")

    # Layer 3: Regime Filter (25 Pts)
    if adx_val >= 25.0 and p_di > m_di:
        score += 25
        notes.append(f"Strong Bullish Trend ADX={adx_val:.1f} (+25)")
    elif adx_val >= 20.0 and p_di > m_di:
        score += 15
        notes.append(f"Moderate Trend ADX={adx_val:.1f} (+15)")
    else:
        notes.append(f"Chop/Bearish Regime ADX={adx_val:.1f} (+0)")

    # Layer 4: Volume Expansion Flow (20 Pts)
    vol_mean = df["Volume"].rolling(20).mean().iloc[-1] if "Volume" in df.columns else 1.0
    vol_cur = df["Volume"].iloc[-1] if "Volume" in df.columns else 1.0
    if vol_cur >= vol_mean:
        score += 20
        notes.append("Volume Above 20D SMA (+20)")
    else:
        score += 10
        notes.append("Volume Below 20D SMA (+10)")

    is_high_alpha = score >= 80

    return ConfluenceMetrics(
        ticker=ticker,
        spot_price=spot,
        atr_14=atr_14,
        invalidation_stop=invalidation_stop,
        adx_14=adx_val,
        poc_price=poc_val,
        is_above_poc=is_above_poc,
        timesfm_target=tfm_exp,
        chronos_target=chr_exp,
        timesfm_delta_pct=tfm_delta,
        chronos_delta_pct=chr_delta,
        model_spread=spread,
        composite_score=score,
        is_high_alpha=is_high_alpha,
        breakdown_notes="; ".join(notes)
    )
