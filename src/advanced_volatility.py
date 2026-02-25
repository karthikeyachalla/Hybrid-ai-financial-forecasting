"""
advanced_volatility.py
Phase I: Realized GARCH + Neural Volatility LSTM Ensemble
Replaces the basic GARCH model with a hybrid ensemble.
"""
import numpy as np
import pandas as pd
from arch import arch_model
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error

def compute_realized_volatility(df: pd.DataFrame, window: int = 21) -> pd.Series:
    """
    Computes annualized Realized Volatility from log returns.
    In a production system this would use 5-min bars; here we use daily log returns.
    """
    log_ret = df['Log_Return']
    realized_vol = log_ret.rolling(window=window).std() * np.sqrt(252) * 100
    realized_vol.name = 'Realized_Vol'
    return realized_vol


def fit_garch_model(returns: pd.Series):
    """Fits GARCH(1,1)-t and returns the fitted result."""
    model = arch_model(returns * 100, vol='GARCH', p=1, q=1, dist='t')
    result = model.fit(disp='off')
    return result


def build_neural_vol_model(train_X, train_y):
    """
    Builds a 2-layer LSTM for volatility prediction.
    Falls back to a simple linear model if PyTorch is unavailable.
    """
    try:
        import torch
        import torch.nn as nn

        class NeuralVol(nn.Module):
            def __init__(self, input_size, hidden=64):
                super().__init__()
                self.lstm = nn.LSTM(input_size, hidden, num_layers=2, batch_first=True,
                                    dropout=0.2)
                self.fc = nn.Linear(hidden, 1)

            def forward(self, x):
                out, _ = self.lstm(x)
                return self.fc(out[:, -1, :])

        X_tensor = torch.FloatTensor(train_X)
        y_tensor = torch.FloatTensor(train_y).unsqueeze(1)

        model = NeuralVol(input_size=train_X.shape[2])
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
        loss_fn = nn.MSELoss()

        model.train()
        for epoch in range(50):
            optimizer.zero_grad()
            pred = model(X_tensor)
            loss = loss_fn(pred, y_tensor)
            loss.backward()
            optimizer.step()

        model.eval()
        print(f"[NeuralVol] LSTM Training complete. Final loss: {loss.item():.4f}")
        return model, 'pytorch', X_tensor
    except ImportError:
        print("[NeuralVol] PyTorch not available, using linear regression fallback.")
        from sklearn.linear_model import Ridge
        n_samples = train_X.shape[0]
        X_flat = train_X.reshape(n_samples, -1)
        lr = Ridge(alpha=1.0)
        lr.fit(X_flat, train_y)
        return lr, 'sklearn', None


def prepare_sequences(series: pd.Series, lookback: int = 20):
    """Converts a time series into supervised ML sequences."""
    values = series.values
    X, y = [], []
    for i in range(lookback, len(values)):
        X.append(values[i - lookback:i])
        y.append(values[i])
    X = np.array(X)
    X = X.reshape(X.shape[0], X.shape[1], 1)
    return X, np.array(y)


def generate_ensemble_forecast(df: pd.DataFrame) -> dict:
    """
    Main entry point for the Advanced Volatility Engine.
    Returns ensemble prediction of tomorrow's volatility.
    """
    returns = df['Log_Return']
    returns_pct = returns * 100

    # --- 1. GARCH Component ---
    garch_res = fit_garch_model(returns)
    garch_forecast = garch_res.forecast(horizon=1)
    garch_vol = float(np.sqrt(garch_forecast.variance.values[-1, -1]))
    garch_params = {
        'omega': float(garch_res.params.get('omega', 0)),
        'alpha': float(garch_res.params.get('alpha[1]', 0)),
        'beta':  float(garch_res.params.get('beta[1]', 0)),
        'persistence': float(garch_res.params.get('alpha[1]', 0) +
                             garch_res.params.get('beta[1]', 0))
    }
    garch_cond_vol = garch_res.conditional_volatility

    # --- 2. Realized Volatility ---
    realized_vol = compute_realized_volatility(df, window=21).dropna()

    # --- 3. Neural Vol Component ---
    lookback = 20
    scaler = MinMaxScaler()
    rv_scaled = scaler.fit_transform(realized_vol.values.reshape(-1, 1)).flatten()
    rv_series = pd.Series(rv_scaled, index=realized_vol.index)

    X, y = prepare_sequences(rv_series, lookback=lookback)
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    neural_model, backend, X_tensor_train = build_neural_vol_model(X_train, y_train)

    # Predict next step
    last_seq = X[-1:]
    try:
        if backend == 'pytorch':
            import torch
            with torch.no_grad():
                X_last = torch.FloatTensor(last_seq)
                neural_pred_scaled = neural_model(X_last).item()
        else:
            n = last_seq.shape[0]
            neural_pred_scaled = neural_model.predict(last_seq.reshape(n, -1))[0]
    except Exception as e:
        print(f"[NeuralVol] Prediction error: {e}. Using GARCH as fallback.")
        neural_pred_scaled = scaler.transform([[garch_vol]])[0][0]

    neural_vol = float(scaler.inverse_transform([[neural_pred_scaled]])[0][0])

    # --- 4. RMSE-Weighted Ensemble ---
    common_idx = realized_vol.index.intersection(garch_cond_vol.index)
    if len(common_idx) > 0:
        rv_aligned = realized_vol.loc[common_idx].values
        garch_aligned = garch_cond_vol.loc[common_idx].values
        garch_rmse = float(np.sqrt(mean_squared_error(rv_aligned, garch_aligned)))
    else:
        garch_rmse = 0.5

    # Neural RMSE (use validation set)
    try:
        if backend == 'pytorch':
            import torch
            with torch.no_grad():
                X_test_t = torch.FloatTensor(X_test)
                y_pred_scaled = neural_model(X_test_t).numpy().flatten()
        else:
            y_pred_scaled = neural_model.predict(X_test.reshape(len(X_test), -1))
        y_pred = scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
        y_actual = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
        neural_rmse = float(np.sqrt(mean_squared_error(y_actual, y_pred)))
    except Exception:
        neural_rmse = garch_rmse * 1.1  # slightly worse to give GARCH more weight

    # Inverse-RMSE weighting (lower RMSE → higher weight)
    w_garch  = (1 / garch_rmse)
    w_neural = (1 / neural_rmse)
    total_w  = w_garch + w_neural
    w_garch  /= total_w
    w_neural /= total_w

    ensemble_vol = w_garch * garch_vol + w_neural * neural_vol

    return {
        'garch_vol':    garch_vol,
        'neural_vol':   neural_vol,
        'ensemble_vol': ensemble_vol,
        'w_garch':      round(w_garch, 3),
        'w_neural':     round(w_neural, 3),
        'garch_rmse':   round(garch_rmse, 4),
        'neural_rmse':  round(neural_rmse, 4),
        'garch_params': garch_params,
        'cond_vol':     garch_cond_vol,
        'realized_vol': realized_vol,
    }


if __name__ == '__main__':
    from data_loader import download_data
    df = download_data("RELIANCE.NS", years=5)
    if df is not None:
        result = generate_ensemble_forecast(df)
        print("\n=== Ensemble Volatility Forecast ===")
        print(f"  GARCH Vol:    {result['garch_vol']:.3f}%  (w={result['w_garch']:.2f})")
        print(f"  Neural Vol:   {result['neural_vol']:.3f}%  (w={result['w_neural']:.2f})")
        print(f"  ENSEMBLE Vol: {result['ensemble_vol']:.3f}%")
        print(f"  GARCH RMSE:   {result['garch_rmse']}")
        print(f"  Neural RMSE:  {result['neural_rmse']}")
