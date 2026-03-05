"""
eda.py — Exploratory Data Analysis
Generates return distribution plots and ACF analysis for volatility clustering.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
from src.data_loader import download_data

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def run_eda(ticker="RELIANCE.NS", years=5):
    print(f"[EDA] Running for {ticker} ({years}y)...")
    df = download_data(ticker, years=years)
    if df is None:
        print("[EDA] ❌ Failed to download data.")
        return

    # 1. Plot Returns
    fig, axes = plt.subplots(2, 1, figsize=(14, 7), sharex=True)
    axes[0].plot(df['Return'], color='#3b82f6', alpha=0.7, linewidth=0.6)
    axes[0].set_title(f'{ticker} — Daily Returns', fontweight='bold')
    axes[0].set_ylabel('Return')

    axes[1].plot(df['Log_Return'], color='#10b981', alpha=0.7, linewidth=0.6)
    axes[1].set_title(f'{ticker} — Log Returns', fontweight='bold')
    axes[1].set_ylabel('Log Return')
    plt.tight_layout()
    path1 = os.path.join(OUTPUT_DIR, f'{ticker}_returns.png')
    plt.savefig(path1, dpi=150)
    plt.close()

    # 2. ACF of Returns + Squared Returns (volatility clustering)
    fig, axes = plt.subplots(2, 1, figsize=(14, 8))
    plot_acf(df['Log_Return'].dropna(), lags=40, ax=axes[0])
    axes[0].set_title('ACF of Log Returns')

    plot_acf((df['Log_Return']**2).dropna(), lags=40, ax=axes[1])
    axes[1].set_title('ACF of Squared Log Returns (Volatility Clustering)')
    plt.tight_layout()
    path2 = os.path.join(OUTPUT_DIR, f'{ticker}_acf.png')
    plt.savefig(path2, dpi=150)
    plt.close()

    print(f"[EDA] ✅ Saved: {path1}")
    print(f"[EDA] ✅ Saved: {path2}")
    return {'returns_plot': path1, 'acf_plot': path2}


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    run_eda(ticker)
