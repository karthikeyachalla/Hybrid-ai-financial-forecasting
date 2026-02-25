import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
import os

def run_eda(ticker="NSEI"):
    filename = f"{ticker}_10y_data.csv"
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
        
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    
    # 1. Plot Returns
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(df['Return'], label='Daily Returns', color='blue', alpha=0.7)
    plt.title(f'{ticker} Daily Returns')
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(df['Log_Return'], label='Log Returns', color='green', alpha=0.7)
    plt.title(f'{ticker} Log Returns')
    plt.legend()
    plt.tight_layout()
    plt.savefig('returns_plot.png')
    plt.close()
    
    # 2. ACF of Returns
    fig, ax = plt.subplots(2, 1, figsize=(12, 8))
    plot_acf(df['Log_Return'], lags=40, ax=ax[0])
    ax[0].set_title('ACF of Log Returns')
    
    # 3. ACF of Squared Returns (Volatility Clustering)
    plot_acf(df['Log_Return']**2, lags=40, ax=ax[1])
    ax[1].set_title('ACF of Squared Log Returns (Volatility Clustering)')
    plt.tight_layout()
    plt.savefig('acf_plots.png')
    plt.close()
    
    print("EDA plots saved as 'returns_plot.png' and 'acf_plots.png'")

if __name__ == "__main__":
    run_eda()
