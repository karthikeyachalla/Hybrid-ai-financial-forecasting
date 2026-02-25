"""
deep_model.py
Phase IV: Multi-horizon LSTM Forecaster (7-day and 30-day)
Outputs quantile predictions (10%, 50%, 90%) for uncertainty-aware forecasts.
Falls back to a statistical baseline if PyTorch is not available.
"""
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import Ridge


LOOKBACK = 30   # days of history to use as input


def _prepare_multistep_data(series: np.ndarray, lookback: int, horizon: int):
    X, y = [], []
    for i in range(lookback, len(series) - horizon + 1):
        X.append(series[i - lookback:i])
        y.append(series[i:i + horizon])
    return np.array(X), np.array(y)


def _build_lstm_model(input_size: int, horizon: int, hidden: int = 64):
    import torch
    import torch.nn as nn

    class LSTMForecaster(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(input_size, hidden, num_layers=2, batch_first=True,
                                dropout=0.2)
            # Output 3 quantiles × horizon steps
            self.head_low    = nn.Linear(hidden, horizon)  # 10th percentile
            self.head_median = nn.Linear(hidden, horizon)  # 50th percentile
            self.head_high   = nn.Linear(hidden, horizon)  # 90th percentile

        def forward(self, x):
            out, _ = self.lstm(x)
            ctx = out[:, -1, :]
            return self.head_low(ctx), self.head_median(ctx), self.head_high(ctx)

    return LSTMForecaster()


def _quantile_loss(pred, target, quantile):
    import torch
    err = target - pred
    return torch.max((quantile - 1) * err, quantile * err).mean()


def train_lstm(features: pd.DataFrame, target_col: str = 'Close',
               horizon: int = 7, epochs: int = 60):
    """
    Trains the LSTM and returns the model, scaler, and feature columns.
    """
    price_col = 'Adj Close' if 'Adj Close' in features.columns else target_col
    feature_cols = [c for c in features.columns
                    if c not in ['Open', 'High', 'Low', 'Close', 'Adj Close',
                                 'Volume', 'Return', 'Log_Return']]
    feature_cols = [price_col, 'Log_Return'] + feature_cols[:10]   # cap at 12 features
    feature_cols = [c for c in feature_cols if c in features.columns]

    data = features[feature_cols].dropna().values.astype(np.float32)
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(data)

    # Use first column (price) as target
    price_idx = 0
    X, y = _prepare_multistep_data(data_scaled, LOOKBACK, horizon)
    y_price = y[:, :, price_idx]

    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y_price[:split], y_price[split:]

    try:
        import torch
        X_t = torch.FloatTensor(X_train)
        y_t = torch.FloatTensor(y_train)

        model = _build_lstm_model(X.shape[2], horizon)
        optimizer = torch.optim.Adam(model.parameters(), lr=5e-4)

        model.train()
        for epoch in range(epochs):
            optimizer.zero_grad()
            low, median, high = model(X_t)
            loss = (_quantile_loss(low, y_t, 0.1) +
                    _quantile_loss(median, y_t, 0.5) +
                    _quantile_loss(high, y_t, 0.9))
            loss.backward()
            optimizer.step()

        print(f"[LSTM] Training complete (horizon={horizon}d). Final loss: {loss.item():.4f}")
        return {'type': 'pytorch', 'model': model, 'scaler': scaler,
                'feature_cols': feature_cols, 'price_idx': price_idx, 'horizon': horizon}

    except ImportError:
        print("[LSTM] PyTorch unavailable. Using Ridge regression fallback.")
        n = X_train.shape[0]
        lr = Ridge(alpha=1.0)
        lr.fit(X_train.reshape(n, -1), y_train)
        return {'type': 'sklearn', 'model': lr, 'scaler': scaler,
                'feature_cols': feature_cols, 'price_idx': price_idx, 'horizon': horizon}


def predict_horizon(trained: dict, features: pd.DataFrame) -> dict:
    """
    Given a trained model dict and features, predicts the next `horizon` days.
    Returns low/median/high price predictions (unscaled).
    """
    feature_cols = trained['feature_cols']
    scaler = trained['scaler']
    horizon = trained['horizon']
    price_idx = trained['price_idx']

    data = features[feature_cols].dropna().values.astype(np.float32)
    data_scaled = scaler.transform(data)
    last_seq = data_scaled[-LOOKBACK:]

    try:
        if trained['type'] == 'pytorch':
            import torch
            model = trained['model']
            model.eval()
            x_in = torch.FloatTensor(last_seq).unsqueeze(0)
            with torch.no_grad():
                low_s, median_s, high_s = model(x_in)
            low_s    = low_s.numpy()[0]
            median_s = median_s.numpy()[0]
            high_s   = high_s.numpy()[0]
        else:
            model = trained['model']
            flat = last_seq.reshape(1, -1)
            median_s = model.predict(flat)[0]
            low_s    = median_s * 0.97
            high_s   = median_s * 1.03

        def _unscale(arr):
            dummy = np.zeros((len(arr), len(feature_cols)))
            dummy[:, price_idx] = arr
            return scaler.inverse_transform(dummy)[:, price_idx]

        return {
            'horizon': horizon,
            'low':    _unscale(low_s),
            'median': _unscale(median_s),
            'high':   _unscale(high_s),
        }
    except Exception as e:
        print(f"[LSTM] Prediction error: {e}")
        last_price = features['Adj Close'].dropna().iloc[-1] \
            if 'Adj Close' in features.columns else features['Close'].dropna().iloc[-1]
        median = np.array([float(last_price)] * horizon)
        return {'horizon': horizon, 'low': median*0.97, 'median': median, 'high': median*1.03}


if __name__ == '__main__':
    from data_loader import download_data
    from feature_engineering import add_technical_indicators

    df = download_data("RELIANCE.NS", years=5)
    if df is not None:
        df = add_technical_indicators(df)
        trained_7d  = train_lstm(df, horizon=7)
        trained_30d = train_lstm(df, horizon=30)
        pred_7d  = predict_horizon(trained_7d, df)
        pred_30d = predict_horizon(trained_30d, df)
        print(f"\n7-Day  forecast: {[round(v,2) for v in pred_7d['median']]}")
        print(f"30-Day forecast: {[round(v,2) for v in pred_30d['median'][:5]]} ...")
