"""
advanced_regime.py
Phase I (continued): VAE Anomaly Scorer + Bayesian Change-Point Detection
Replaces the old binary HMM with a continuous Anomaly Score system.
"""
import numpy as np
import pandas as pd


# ─────────────────────────────────────────────────────────────
# 1.  VAE Anomaly Scorer  (PyTorch – fallback to scipy z-score)
# ─────────────────────────────────────────────────────────────

def _build_vae(input_dim: int, latent_dim: int = 4):
    """Builds a simple Variational Autoencoder for anomaly scoring."""
    import torch
    import torch.nn as nn

    class VAE(nn.Module):
        def __init__(self):
            super().__init__()
            self.enc1 = nn.Linear(input_dim, 16)
            self.enc_mu  = nn.Linear(16, latent_dim)
            self.enc_logvar = nn.Linear(16, latent_dim)
            self.dec1 = nn.Linear(latent_dim, 16)
            self.dec2 = nn.Linear(16, input_dim)

        def encode(self, x):
            h = torch.relu(self.enc1(x))
            return self.enc_mu(h), self.enc_logvar(h)

        def reparameterize(self, mu, logvar):
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std

        def decode(self, z):
            h = torch.relu(self.dec1(z))
            return self.dec2(h)

        def forward(self, x):
            mu, logvar = self.encode(x)
            z = self.reparameterize(mu, logvar)
            x_hat = self.decode(z)
            return x_hat, mu, logvar

    return VAE()


def _vae_loss(x_hat, x, mu, logvar):
    import torch.nn.functional as F
    import torch
    recon = F.mse_loss(x_hat, x, reduction='sum')
    kld   = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    return recon + kld


def detect_anomalies_vae(df: pd.DataFrame, feature_cols: list = None) -> pd.Series:
    """
    Trains a VAE on market data and returns a continuous Anomaly Score per day.
    High score = market behaving unusually (potential regime shift or crash).
    """
    if feature_cols is None:
        feature_cols = ['Log_Return', 'RollingVol_21'] if 'RollingVol_21' in df.columns \
                       else ['Log_Return']

    data = df[feature_cols].dropna().values
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(data).astype(np.float32)

    try:
        import torch
        X = torch.FloatTensor(data_scaled)
        vae = _build_vae(input_dim=data_scaled.shape[1])
        optimizer = torch.optim.Adam(vae.parameters(), lr=1e-3)

        vae.train()
        for epoch in range(80):
            optimizer.zero_grad()
            x_hat, mu, logvar = vae(X)
            loss = _vae_loss(x_hat, X, mu, logvar)
            loss.backward()
            optimizer.step()
        print(f"[VAE] Training complete. Final loss: {loss.item():.2f}")

        vae.eval()
        with torch.no_grad():
            x_hat, _, _ = vae(X)
            recon_error = ((X - x_hat) ** 2).mean(dim=1).numpy()

        # Normalize to 0–100 scale
        recon_min, recon_max = recon_error.min(), recon_error.max()
        anomaly_score = 100 * (recon_error - recon_min) / (recon_max - recon_min + 1e-8)

        idx = df[feature_cols].dropna().index
        return pd.Series(anomaly_score, index=idx, name='Anomaly_Score')

    except ImportError:
        print("[VAE] PyTorch unavailable. Using z-score anomaly fallback.")
        from scipy import stats
        z_scores = np.abs(stats.zscore(data_scaled, axis=0)).mean(axis=1)
        z_min, z_max = z_scores.min(), z_scores.max()
        anomaly_score = 100 * (z_scores - z_min) / (z_max - z_min + 1e-8)
        idx = df[feature_cols].dropna().index
        return pd.Series(anomaly_score, index=idx, name='Anomaly_Score')


# ─────────────────────────────────────────────────────────────
# 2.  Bayesian Change-Point Detection  (ruptures library)
# ─────────────────────────────────────────────────────────────

def detect_change_points(series: pd.Series, n_bkps: int = 5) -> list:
    """
    Uses the `ruptures` library (PELT algorithm) to detect change points.
    Returns a list of dates where structural breaks were detected.
    """
    try:
        import ruptures as rpt
        signal = series.values.reshape(-1, 1)
        algo = rpt.Pelt(model="rbf").fit(signal)
        breakpoint_indices = algo.predict(pen=10)
        # Convert to dates (exclude the last index which is always len(series))
        breakpoint_dates = [series.index[i - 1] for i in breakpoint_indices if i < len(series)]
        print(f"[ChangePoint] Detected {len(breakpoint_dates)} structural breaks.")
        return breakpoint_dates
    except ImportError:
        print("[ChangePoint] ruptures not available. Using rolling z-score method.")
        # Fallback: detect days where z-score > 2.5
        z = (series - series.rolling(30).mean()) / (series.rolling(30).std() + 1e-8)
        breakpoints = series.index[z.abs() > 2.5].tolist()
        return breakpoints[:5]   # return top 5 most extreme


# ─────────────────────────────────────────────────────────────
# 3.  Combined Regime Analysis
# ─────────────────────────────────────────────────────────────

def analyze_regime(df: pd.DataFrame) -> dict:
    """
    Entry point for advanced regime analysis.
    Returns regime state, anomaly score, and change-point dates.
    """
    anomaly_series = detect_anomalies_vae(df)
    current_anomaly = float(anomaly_series.iloc[-1])

    # Regime classification based on anomaly score percentile
    threshold_75 = float(np.percentile(anomaly_series.values, 75))
    threshold_90 = float(np.percentile(anomaly_series.values, 90))

    if current_anomaly >= threshold_90:
        regime = 'CRISIS'
        regime_color = '#ff0040'
    elif current_anomaly >= threshold_75:
        regime = 'VOLATILE'
        regime_color = '#ff8800'
    else:
        regime = 'CALM'
        regime_color = '#00ff88'

    change_points = detect_change_points(anomaly_series)

    return {
        'regime': regime,
        'regime_color': regime_color,
        'anomaly_score': round(current_anomaly, 2),
        'anomaly_threshold_75': round(threshold_75, 2),
        'anomaly_threshold_90': round(threshold_90, 2),
        'anomaly_series': anomaly_series,
        'change_points': change_points[-3:],    # last 3 breakpoints
    }


if __name__ == '__main__':
    try:
        from src.data_loader import download_data
        from src.feature_engineering import add_technical_indicators
    except ImportError:
        from data_loader import download_data
        from feature_engineering import add_technical_indicators
    df = download_data("RELIANCE.NS", years=5)
    if df is not None:
        df = add_technical_indicators(df)
        result = analyze_regime(df)
        print(f"\n=== Regime Analysis ===")
        print(f"  Current Regime:     {result['regime']}")
        print(f"  Anomaly Score:      {result['anomaly_score']} / 100")
        print(f"  Recent Breakpoints: {[str(d.date()) for d in result['change_points']]}")
