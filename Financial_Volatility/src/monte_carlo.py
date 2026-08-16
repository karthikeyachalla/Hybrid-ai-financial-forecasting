"""
monte_carlo.py
Monte Carlo Simulation Engine using Geometric Brownian Motion (GBM).
Generates N simulated price paths for risk visualization.
"""
import numpy as np
import pandas as pd


def run_monte_carlo(df: pd.DataFrame,
                    n_simulations: int = 1000,
                    horizon: int = 30,
                    garch_vol: float = None) -> dict:
    """
    Runs Monte Carlo simulation using GBM (Geometric Brownian Motion).

    Parameters:
        df            : DataFrame with price history (needs 'Log_Return' and 'Close'/'Adj Close')
        n_simulations : Number of simulated price paths
        horizon       : Number of trading days to simulate forward
        garch_vol     : Optional GARCH-predicted annualized vol (%). If None, uses historical.

    Returns dict with:
        - paths        : np.array of shape (n_simulations, horizon+1) — simulated prices
        - percentiles  : dict of p5, p25, p50, p75, p95 paths
        - prob_gain    : probability price ends higher than today
        - expected_return : mean simulated return %
        - var_95       : 95% Value-at-Risk (worst 5% outcome)
        - last_price   : starting price
    """
    price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    last_price = float(df[price_col].iloc[-1])
    log_returns = df['Log_Return'].dropna()

    # Drift = mean daily return
    mu_daily = float(log_returns.mean())

    # Volatility: use GARCH forecast if provided, else historical
    if garch_vol is not None:
        sigma_daily = (garch_vol / 100.0) / np.sqrt(252)
    else:
        sigma_daily = float(log_returns.std())

    # GBM simulation
    dt = 1  # 1 trading day
    np.random.seed(42)  # reproducibility
    Z = np.random.standard_normal((n_simulations, horizon))

    # Daily returns: r = (mu - 0.5*sigma^2)*dt + sigma*sqrt(dt)*Z
    daily_returns = (mu_daily - 0.5 * sigma_daily**2) * dt + sigma_daily * np.sqrt(dt) * Z

    # Cumulative price paths
    paths = np.zeros((n_simulations, horizon + 1))
    paths[:, 0] = last_price
    for t in range(1, horizon + 1):
        paths[:, t] = paths[:, t-1] * np.exp(daily_returns[:, t-1])

    # Final prices
    final_prices = paths[:, -1]

    # Percentile paths
    percentiles = {
        'p5':  np.percentile(paths, 5, axis=0),
        'p25': np.percentile(paths, 25, axis=0),
        'p50': np.percentile(paths, 50, axis=0),
        'p75': np.percentile(paths, 75, axis=0),
        'p95': np.percentile(paths, 95, axis=0),
    }

    # Stats
    prob_gain = float(np.mean(final_prices > last_price) * 100)
    expected_return = float((np.mean(final_prices) / last_price - 1) * 100)
    var_95 = float((np.percentile(final_prices, 5) / last_price - 1) * 100)
    cvar_95 = float((np.mean(final_prices[final_prices <= np.percentile(final_prices, 5)]) / last_price - 1) * 100)
    median_return = float((np.median(final_prices) / last_price - 1) * 100)

    return {
        'paths': paths,
        'percentiles': percentiles,
        'final_prices': final_prices,
        'prob_gain': round(prob_gain, 1),
        'expected_return': round(expected_return, 2),
        'median_return': round(median_return, 2),
        'var_95': round(var_95, 2),
        'cvar_95': round(cvar_95, 2),
        'last_price': last_price,
        'n_simulations': n_simulations,
        'horizon': horizon,
        'sigma_daily': sigma_daily,
        'mu_daily': mu_daily,
    }


if __name__ == '__main__':
    try:
        from src.data_loader import download_data
    except ImportError:
        from data_loader import download_data

    df = download_data("RELIANCE.NS", years=5)
    if df is not None:
        result = run_monte_carlo(df, n_simulations=1000, horizon=30)
        print(f"\n=== Monte Carlo Simulation (1000 paths, 30 days) ===")
        print(f"  Starting Price:     ₹{result['last_price']:,.2f}")
        print(f"  Prob of Gain:       {result['prob_gain']}%")
        print(f"  Expected Return:    {result['expected_return']:+.2f}%")
        print(f"  Median Return:      {result['median_return']:+.2f}%")
        print(f"  VaR (95%):          {result['var_95']:+.2f}%")
        print(f"  CVaR (95%):         {result['cvar_95']:+.2f}%")
