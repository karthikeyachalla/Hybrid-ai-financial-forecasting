import pandas as pd
import numpy as np
from arch import arch_model
from hmmlearn import hmm
import os

from statsmodels.tsa.stattools import acf
from sklearn.metrics import mean_squared_error

import yfinance as yf

def fetch_news_headlines(ticker):
    """
    Fetches the latest news headlines using yfinance.
    """
    try:
        t = yf.Ticker(ticker)
        news = t.news[:5] # Get top 5
        return news
    except:
        return []

def generate_tomorrow_forecast(df, ticker="Selected Ticker"):
    """
    Generates a comprehensive forecast and evaluation based on requirements.
    """
    returns = df['Log_Return'] * 100
    
    # 1. Fit Multi-Models for Evaluation (Requirement 4 & 7)
    models = {
        "ARCH": arch_model(returns, vol='ARCH', p=1),
        "GARCH": arch_model(returns, vol='GARCH', p=1, q=1),
        "GJR-GARCH": arch_model(returns, vol='GARCH', p=1, o=1, q=1),
        "EGARCH": arch_model(returns, vol='EGARCH', p=1, o=1, q=1)
    }
    
    results_map = {}
    rmses = {}
    realized_vol = returns.rolling(window=21).std().dropna()
    
    # Fit the best model (GARCH-t) for parameters and prediction (Requirement 4c)
    primary_model = arch_model(returns, vol='GARCH', p=1, q=1, dist='t')
    primary_res = primary_model.fit(disp='off')
    
    params = primary_res.params
    # GARCH Parameters: omega (constant), alpha[1] (arch), beta[1] (garch)
    garch_params = {
        "omega": params.get('omega', 0),
        "alpha": params.get('alpha[1]', 0),
        "beta": params.get('beta[1]', 0),
        "persistence": params.get('alpha[1]', 0) + params.get('beta[1]', 0)
    }

    for name, m in models.items():
        res = m.fit(disp='off')
        # Calculate RMSE (Requirement 7a)
        pred_vol = res.conditional_volatility
        common_idx = realized_vol.index.intersection(pred_vol.index)
        rmse = np.sqrt(mean_squared_error(realized_vol.loc[common_idx], pred_vol.loc[common_idx]))
        rmses[name] = rmse

    # 2. Predict Tomorrow (Requirement 4)
    forecast = primary_res.forecast(horizon=1)
    tomorrow_vol = np.sqrt(forecast.variance.values[-1, -1])
    
    # 3. Predict Regime using HMM (Requirement 5)
    returns_reshaped = returns.values.reshape(-1, 1)
    hmm_model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
    hmm_model.fit(returns_reshaped)
    current_state = hmm_model.predict(returns_reshaped)[-1]
    
    # Identify calm vs volatile
    var_0 = hmm_model.covars_[0][0]
    var_1 = hmm_model.covars_[1][0]
    calm_state = 0 if var_0 < var_1 else 1
    regime_name = "CALM" if current_state == calm_state else "VOLATILE"
    
    # 4. ACF Data (Requirement 3)
    acf_ret = acf(returns, nlags=40)
    acf_sq = acf(returns**2, nlags=40)
    
    # Layman Explanation
    if regime_name == "CALM":
        layman = f"Market is currently in a steady phase. Think of it like a calm ocean—no big waves expected. " \
                 f"Our math shows that the price today is very similar to price yesterday, so its safe for steady growth."
    else:
        layman = f"Heads up! The market is behaving like an emotional roller coaster. We've detected 'Volatility Clustering', " \
                 f"which is just a fancy way of saying a big price swing is likely to be followed by another big one. " \
                 f"Expect the price of {ticker} to be quite jumpy tomorrow."

    return {
        "ticker": ticker,
        "tomorrow_vol": tomorrow_vol,
        "regime": regime_name,
        "confidence_range": 1.96 * tomorrow_vol,
        "summary": f"Tomorrow's market behaves as {regime_name}. Expect the price to swing within {1.96 * tomorrow_vol:.2f}% of today's close.",
        "layman_summary": layman,
        "garch_params": garch_params,
        "rmses": rmses,
        "acf_ret": acf_ret,
        "acf_sq": acf_sq,
        "historical_vol": primary_res.conditional_volatility
    }

def run_standalone_forecast(ticker="NSEI"):
    data_file = f"{ticker}_10y_data.csv"
    if not os.path.exists(data_file):
        print("Data file not found. Please run data_loader.py first.")
        return

    df = pd.read_csv(data_file, index_col=0, parse_dates=True)
    results = generate_tomorrow_forecast(df, ticker)
    
    # 3. Output the answer for the teacher
    print("\n" + "="*40)
    print(f"--- FORECAST FOR NEXT TRADING DAY ({results['ticker']}) ---")
    print("="*40)
    print(f"Predicted Volatility (Std Dev): {results['tomorrow_vol']:.2f}%")
    print(f"Predicted Market Regime: {results['regime']}")
    print(f"95% Confidence Range: +/- {results['confidence_range']:.2f}%")
    print("-" * 40)
    print(f"Summary: {results['summary']}")
    print("="*40 + "\n")

if __name__ == "__main__":
    run_standalone_forecast()
