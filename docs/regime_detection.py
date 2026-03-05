"""
regime_detection.py — HMM-Based Market Regime Detection
Identifies calm vs volatile market periods using Gaussian HMM.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.data_loader import download_data

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

try:
    from hmmlearn import hmm
    HAS_HMM = True
except ImportError:
    HAS_HMM = False


def detect_regimes(ticker="RELIANCE.NS", years=5):
    print(f"[Regime] Detecting market regimes for {ticker}...")

    if not HAS_HMM:
        print("[Regime] ❌ hmmlearn is not installed. Install with: pip install hmmlearn")
        return

    df = download_data(ticker, years=years)
    if df is None:
        return

    returns = df['Log_Return'].values.reshape(-1, 1)

    model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
    model.fit(returns)
    hidden_states = model.predict(returns)

    calm_state = 0 if model.covars_[0][0] < model.covars_[1][0] else 1
    df['Regime'] = hidden_states
    df['Regime_Label'] = df['Regime'].apply(lambda x: 'Calm' if x == calm_state else 'Volatile')

    # Stats
    calm_pct = (df['Regime_Label'] == 'Calm').mean() * 100
    current = df['Regime_Label'].iloc[-1]
    print(f"  Current regime: {current}")
    print(f"  Calm periods:   {calm_pct:.1f}%")
    print(f"  Volatile:       {100 - calm_pct:.1f}%")

    # Plot
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    colors = ['#10b981' if s == calm_state else '#ef4444' for s in df['Regime']]
    axes[0].scatter(df.index, df['Log_Return'], c=colors, s=3, alpha=0.7)
    axes[0].set_title(f'{ticker} — Returns Colored by Regime', fontweight='bold')
    axes[0].set_ylabel('Log Return')

    axes[1].fill_between(df.index, df['Regime'], alpha=0.4, color='#f59e0b')
    axes[1].set_title('Regime State (0=Calm, 1=Volatile)', fontweight='bold')
    axes[1].set_ylabel('State')
    plt.tight_layout()

    plot_path = os.path.join(OUTPUT_DIR, f'{ticker}_regimes.png')
    plt.savefig(plot_path, dpi=150)
    plt.close()

    csv_path = os.path.join(OUTPUT_DIR, f'{ticker}_regimes.csv')
    df[['Log_Return', 'Regime', 'Regime_Label']].to_csv(csv_path)

    print(f"[Regime] ✅ Plot: {plot_path}")
    print(f"[Regime] ✅ CSV:  {csv_path}")
    return {'plot': plot_path, 'csv': csv_path, 'current_regime': current}


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    detect_regimes(ticker)
