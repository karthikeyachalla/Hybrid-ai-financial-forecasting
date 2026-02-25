import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.metrics import mean_squared_error

def run_evaluation(ticker="NSEI"):
    # Load data
    data_file = f"{ticker}_10y_data.csv"
    pred_file = "predicted_volatility.csv"
    
    if not (os.path.exists(data_file) and os.path.exists(pred_file)):
        print("Required files missing for evaluation.")
        return
        
    df = pd.read_csv(data_file, index_col=0, parse_dates=True)
    pred_df = pd.read_csv(pred_file, index_col=0, parse_dates=True)
    
    # Calculate Realized Volatility Proxy (21-day rolling std of returns)
    # Scaling to match percentage returns in models.py
    real_returns = df['Log_Return'] * 100
    realized_vol = real_returns.rolling(window=21).std()
    
    # Calculate RMSE for each model
    results = {}
    for col in pred_df.columns:
        # Align data (drop first 20 rows of NaN in realized_vol)
        valid_idx = realized_vol.dropna().index.intersection(pred_df.index)
        rmse = np.sqrt(mean_squared_error(realized_vol.loc[valid_idx], pred_df.loc[valid_idx, col]))
        results[col] = rmse
        print(f"RMSE for {col}: {rmse:.4f}")
        
    # Plot Confidence Intervals (using GARCH as primary example)
    plt.figure(figsize=(12, 6))
    mu = real_returns.mean()
    vol = pred_df['GARCH']
    
    plt.plot(real_returns, color='gray', alpha=0.3, label='Actual Returns')
    plt.plot(mu + 1.96 * vol, color='red', linestyle='--', label='95% Upper Bound')
    plt.plot(mu - 1.96 * vol, color='red', linestyle='--', label='95% Lower Bound')
    plt.title('95% Confidence Intervals for Returns (GARCH)')
    plt.legend()
    plt.savefig('confidence_intervals.png')
    plt.close()
    
    # Save statistics
    stats_df = pd.DataFrame(results.items(), columns=['Model', 'RMSE'])
    stats_df.to_csv('model_evaluation_stats.csv', index=False)
    print("Evaluation complete. Stats saved and final plots generated.")

if __name__ == "__main__":
    run_evaluation()
