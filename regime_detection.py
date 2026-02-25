import pandas as pd
import numpy as np
from hmmlearn import hmm
import matplotlib.pyplot as plt
import os

def detect_regimes(ticker="NSEI"):
    filename = f"{ticker}_10y_data.csv"
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
        
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    returns = df['Log_Return'].values.reshape(-1, 1)
    
    # Fit Gaussian HMM with 2 components (Calm vs Volatile)
    model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
    model.fit(returns)
    
    # Predict regimes (Viterbi decoding is usually default in predict)
    hidden_states = model.predict(returns)
    
    # Analyze states to identify which is 'Calm' (lower variance)
    var_0 = model.covars_[0][0]
    var_1 = model.covars_[1][0]
    
    if var_0 < var_1:
        calm_state = 0
        volatile_state = 1
    else:
        calm_state = 1
        volatile_state = 0
        
    df['Regime'] = hidden_states
    df['Regime_Label'] = df['Regime'].apply(lambda x: 'Calm' if x == calm_state else 'Volatile')
    
    # Plotting Regimes
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.plot(df['Log_Return'], color='gray', alpha=0.5)
    plt.scatter(df.index, df['Log_Return'], c=df['Regime'], cmap='viridis', s=10)
    plt.title('Market Regimes (Log Returns Colored by State)')
    
    plt.subplot(2, 1, 2)
    plt.plot(df['Regime'], color='orange')
    plt.title('Regime State Over Time (0 and 1)')
    plt.tight_layout()
    plt.savefig('market_regimes.png')
    plt.close()
    
    df.to_csv('market_regimes.csv')
    print("Regime detection complete. Saved to market_regimes.csv and market_regimes.png")

if __name__ == "__main__":
    detect_regimes()
