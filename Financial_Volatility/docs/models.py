"""
models.py — Multi-Model Volatility Fitting
Fits ARCH, GARCH, GJR-GARCH, EGARCH, and GARCH-t models.
Compares conditional volatility and saves predicted series.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from arch import arch_model
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.data_loader import download_data

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def fit_volatility_models(ticker="RELIANCE.NS", years=5):
    print(f"[Models] Fitting volatility models for {ticker}...")
    df = download_data(ticker, years=years)
    if df is None:
        print("[Models] ❌ Failed to download data.")
        return

    returns = df['Log_Return'] * 100  # percentage for better convergence

    models = {
        "ARCH":      arch_model(returns, vol='ARCH', p=1),
        "GARCH":     arch_model(returns, vol='GARCH', p=1, q=1),
        "GARCH-t":   arch_model(returns, vol='GARCH', p=1, q=1, dist='t'),
        "GJR-GARCH": arch_model(returns, vol='GARCH', p=1, o=1, q=1),
        "EGARCH":    arch_model(returns, vol='EGARCH', p=1, o=1, q=1),
    }

    forecasts = {}
    for name, model in models.items():
        print(f"  Fitting {name}...")
        res = model.fit(disp='off')
        forecasts[name] = res.conditional_volatility

    # Plot
    plt.figure(figsize=(15, 7))
    for name, vol in forecasts.items():
        plt.plot(vol, label=name, alpha=0.8, linewidth=0.8)
    plt.plot(returns.abs(), label='|Returns| (proxy)', color='gray', alpha=0.2)
    plt.title(f'{ticker} — Conditional Volatility: Model Comparison', fontweight='bold')
    plt.legend()
    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, f'{ticker}_models_comparison.png')
    plt.savefig(plot_path, dpi=150)
    plt.close()

    # Save predicted volatility
    vol_df = pd.DataFrame(forecasts)
    csv_path = os.path.join(OUTPUT_DIR, f'{ticker}_predicted_volatility.csv')
    vol_df.to_csv(csv_path)

    print(f"[Models] ✅ Plot: {plot_path}")
    print(f"[Models] ✅ CSV:  {csv_path}")
    return {'plot': plot_path, 'csv': csv_path, 'forecasts': forecasts}


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    fit_volatility_models(ticker)
