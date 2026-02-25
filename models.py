import pandas as pd
import numpy as np
from arch import arch_model
import matplotlib.pyplot as plt
import os

def fit_volatility_models(ticker="NSEI"):
    filename = f"{ticker}_10y_data.csv"
    if not os.path.exists(filename):
        print(f"File {filename} not found.")
        return
        
    df = pd.read_csv(filename, index_col=0, parse_dates=True)
    returns = df['Log_Return'] * 100  # Rescale to percentage for better convergence
    
    models = {
        "ARCH": arch_model(returns, vol='ARCH', p=1),
        "GARCH": arch_model(returns, vol='GARCH', p=1, q=1),
        "GARCH-t": arch_model(returns, vol='GARCH', p=1, q=1, dist='t'),
        "GJR-GARCH": arch_model(returns, vol='GARCH', p=1, o=1, q=1),
        "EGARCH": arch_model(returns, vol='EGARCH', p=1, o=1, q=1)
    }
    
    results = {}
    forecasts = {}
    
    for name, model in models.items():
        print(f"Fitting {name} model...")
        res = model.fit(disp='off')
        results[name] = res
        print(res.summary())
        
        # Get conditional volatility
        forecasts[name] = res.conditional_volatility
        
    # Plotting comparisons
    plt.figure(figsize=(15, 10))
    for name, vol in forecasts.items():
        plt.plot(vol, label=name, alpha=0.8)
    
    plt.plot(returns.abs(), label='Absolute Returns (Proxy)', color='gray', alpha=0.3)
    plt.title('Conditional Volatility Forecasts vs Realized Volatility Proxy')
    plt.legend()
    plt.savefig('volatility_models_comparison.png')
    plt.close()
    
    # Save forecasts for evaluation
    vol_df = pd.DataFrame(forecasts)
    vol_df.to_csv('predicted_volatility.csv')
    print("Model fitting complete. Results saved.")

if __name__ == "__main__":
    fit_volatility_models()

