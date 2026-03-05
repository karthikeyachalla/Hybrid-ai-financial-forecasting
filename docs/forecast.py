"""
forecast.py — Tomorrow's Forecast
Generates a comprehensive next-day volatility forecast using GARCH-t
and regime detection using HMM.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from arch import arch_model
from statsmodels.tsa.stattools import acf
from sklearn.metrics import mean_squared_error
from src.data_loader import download_data

# HMM is optional
try:
    from hmmlearn import hmm
    HAS_HMM = True
except ImportError:
    HAS_HMM = False
    print("[forecast] hmmlearn not available. Regime detection will be skipped.")


def generate_tomorrow_forecast(df, ticker="RELIANCE.NS"):
    """Generates a GARCH-based forecast with optional HMM regime detection."""
    returns = df['Log_Return'] * 100

    # 1. Fit multi-models for comparison
    models = {
        "ARCH":      arch_model(returns, vol='ARCH', p=1),
        "GARCH":     arch_model(returns, vol='GARCH', p=1, q=1),
        "GJR-GARCH": arch_model(returns, vol='GARCH', p=1, o=1, q=1),
        "EGARCH":    arch_model(returns, vol='EGARCH', p=1, o=1, q=1),
    }

    rmses = {}
    realized_vol = returns.rolling(window=21).std().dropna()

    for name, m in models.items():
        res = m.fit(disp='off')
        pred_vol = res.conditional_volatility
        common_idx = realized_vol.index.intersection(pred_vol.index)
        rmse = np.sqrt(mean_squared_error(realized_vol.loc[common_idx], pred_vol.loc[common_idx]))
        rmses[name] = rmse

    # 2. Primary model (GARCH-t)
    primary = arch_model(returns, vol='GARCH', p=1, q=1, dist='t').fit(disp='off')
    params = primary.params
    garch_params = {
        "omega": params.get('omega', 0),
        "alpha": params.get('alpha[1]', 0),
        "beta":  params.get('beta[1]', 0),
        "persistence": params.get('alpha[1]', 0) + params.get('beta[1]', 0),
    }

    # 3. Tomorrow's volatility
    forecast = primary.forecast(horizon=1)
    tomorrow_vol = np.sqrt(forecast.variance.values[-1, -1])

    # 4. Regime detection (HMM)
    if HAS_HMM:
        returns_reshaped = returns.values.reshape(-1, 1)
        hmm_model = hmm.GaussianHMM(n_components=2, covariance_type="diag", n_iter=1000)
        hmm_model.fit(returns_reshaped)
        current_state = hmm_model.predict(returns_reshaped)[-1]
        calm_state = 0 if hmm_model.covars_[0][0] < hmm_model.covars_[1][0] else 1
        regime_name = "CALM" if current_state == calm_state else "VOLATILE"
    else:
        regime_name = "UNKNOWN (hmmlearn not installed)"

    # 5. ACF data
    acf_ret = acf(returns.dropna(), nlags=40)
    acf_sq  = acf((returns**2).dropna(), nlags=40)

    return {
        "ticker": ticker,
        "tomorrow_vol": tomorrow_vol,
        "regime": regime_name,
        "confidence_range": 1.96 * tomorrow_vol,
        "garch_params": garch_params,
        "rmses": rmses,
        "acf_ret": acf_ret,
        "acf_sq": acf_sq,
        "historical_vol": primary.conditional_volatility,
    }


def run_standalone_forecast(ticker="RELIANCE.NS", years=5):
    print(f"[Forecast] Generating forecast for {ticker}...")
    df = download_data(ticker, years=years)
    if df is None:
        print("[Forecast] ❌ Failed to download data.")
        return

    results = generate_tomorrow_forecast(df, ticker)

    print("\n" + "=" * 50)
    print(f"  FORECAST FOR NEXT TRADING DAY — {results['ticker']}")
    print("=" * 50)
    print(f"  Predicted Volatility: {results['tomorrow_vol']:.2f}%")
    print(f"  Market Regime:        {results['regime']}")
    print(f"  95% Confidence:       ±{results['confidence_range']:.2f}%")
    print("-" * 50)
    print(f"  GARCH Params: ω={results['garch_params']['omega']:.4f}, "
          f"α={results['garch_params']['alpha']:.4f}, "
          f"β={results['garch_params']['beta']:.4f}")
    print(f"  Persistence:  {results['garch_params']['persistence']:.4f}")
    print("-" * 50)
    print("  Model RMSE Comparison:")
    for name, rmse in results['rmses'].items():
        print(f"    {name:12s}: {rmse:.4f}")
    best = min(results['rmses'], key=results['rmses'].get)
    print(f"  🏆 Best: {best}")
    print("=" * 50 + "\n")
    return results


if __name__ == "__main__":
    ticker = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    run_standalone_forecast(ticker)
