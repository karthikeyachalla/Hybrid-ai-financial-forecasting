"""
backtest.py
Phase VI: Backtesting Engine with Sharpe, Sortino, Max Drawdown, VaR, CVaR.
Uses a simple volatility-based strategy to validate the model's predictions.
"""
import numpy as np
import pandas as pd


def run_backtest(df: pd.DataFrame, vol_series: pd.Series,
                 initial_capital: float = 100_000.0,
                 vol_threshold: float = 1.5,
                 slippage_pct: float = 0.001,
                 transaction_cost_pct: float = 0.002) -> dict:
    """
    Strategy:
      - When predicted volatility drops below `vol_threshold` × median → LONG (buy)
      - When predicted volatility exceeds threshold → CASH (sit out)
    This simulates using our volatility forecast to time the market.
    """
    price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'

    # Align data
    common_idx = df.index.intersection(vol_series.index)
    prices = df.loc[common_idx, price_col]
    vol    = vol_series.loc[common_idx]

    if len(prices) < 50:
        return {'error': 'Insufficient data for backtesting (need > 50 rows).'}

    median_vol = vol.median()

    # Generate signals: 1 = long, 0 = cash
    signals = (vol < vol_threshold * median_vol).astype(int)

    # Calculate daily returns
    daily_returns = prices.pct_change().fillna(0)
    strategy_returns = signals.shift(1).fillna(0) * daily_returns  # next-day execution

    # Deduct transaction costs on signal changes
    trades = signals.diff().fillna(0).abs()
    cost = trades * (slippage_pct + transaction_cost_pct)
    strategy_returns = strategy_returns - cost

    # Portfolio Value
    portfolio = initial_capital * (1 + strategy_returns).cumprod()

    # Buy-and-Hold Benchmark
    benchmark_returns = daily_returns
    benchmark = initial_capital * (1 + benchmark_returns).cumprod()

    # ---- Risk Metrics ----
    ann_factor = np.sqrt(252)
    rf_daily = 0.06 / 252    # assume 6% annual risk-free rate

    def sharpe(returns):
        excess = returns - rf_daily
        return float((excess.mean() / (excess.std() + 1e-8)) * ann_factor)

    def sortino(returns):
        excess = returns - rf_daily
        downside_std = returns[returns < 0].std() + 1e-8
        return float((excess.mean() / downside_std) * ann_factor)

    def max_drawdown(port_values):
        roll_max = port_values.cummax()
        drawdown = (port_values - roll_max) / roll_max
        return float(drawdown.min())

    def value_at_risk(returns, alpha=0.05):
        return float(np.percentile(returns, alpha * 100))

    def cvar(returns, alpha=0.05):
        var = value_at_risk(returns, alpha)
        return float(returns[returns <= var].mean())

    total_return_strategy  = float((portfolio.iloc[-1] / initial_capital - 1) * 100)
    total_return_benchmark = float((benchmark.iloc[-1] / initial_capital - 1) * 100)
    num_trades = int(trades.sum())

    metrics = {
        # Strategy
        'total_return_pct':   round(total_return_strategy, 2),
        'sharpe_ratio':       round(sharpe(strategy_returns), 3),
        'sortino_ratio':      round(sortino(strategy_returns), 3),
        'max_drawdown_pct':   round(max_drawdown(portfolio) * 100, 2),
        'var_95_pct':         round(value_at_risk(strategy_returns) * 100, 3),
        'cvar_95_pct':        round(cvar(strategy_returns) * 100, 3),
        'num_trades':         num_trades,
        # Benchmark
        'benchmark_return_pct': round(total_return_benchmark, 2),
        'benchmark_sharpe':     round(sharpe(benchmark_returns), 3),
        # Curves
        'portfolio_curve':    portfolio,
        'benchmark_curve':    benchmark,
        'strategy_returns':   strategy_returns,
        'signals':            signals,
    }
    return metrics


def format_backtest_report(metrics: dict) -> str:
    """Returns a formatted summary of backtest results."""
    if 'error' in metrics:
        return f"Backtest Error: {metrics['error']}"
    lines = [
        "════════════════════════════════════",
        "     BACKTEST PERFORMANCE REPORT    ",
        "════════════════════════════════════",
        f"  Total Return:        {metrics['total_return_pct']:+.2f}%",
        f"  Benchmark Return:    {metrics['benchmark_return_pct']:+.2f}%",
        f"  Sharpe Ratio:        {metrics['sharpe_ratio']:.3f}",
        f"  Sortino Ratio:       {metrics['sortino_ratio']:.3f}",
        f"  Max Drawdown:        {metrics['max_drawdown_pct']:.2f}%",
        f"  VaR (95%):           {metrics['var_95_pct']:.3f}%",
        f"  CVaR (95%):          {metrics['cvar_95_pct']:.3f}%",
        f"  # Trades:            {metrics['num_trades']}",
        "════════════════════════════════════",
    ]
    return '\n'.join(lines)


if __name__ == '__main__':
    from data_loader import download_data
    from advanced_volatility import generate_ensemble_forecast

    df = download_data("RELIANCE.NS", years=5)
    if df is not None:
        vol_result = generate_ensemble_forecast(df)
        metrics = run_backtest(df, vol_result['realized_vol'])
        print(format_backtest_report(metrics))
