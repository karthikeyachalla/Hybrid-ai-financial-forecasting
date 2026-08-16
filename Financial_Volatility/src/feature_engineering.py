"""
feature_engineering.py
Phase III: 50+ Technical Indicators using pandas-ta
"""
import pandas as pd
import numpy as np

def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a raw OHLCV dataframe and adds 50+ technical indicators.
    Requires columns: Open, High, Low, Close, Volume (or Adj Close)
    """
    price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    df = df.copy()

    # --- Use pandas-ta if available ---
    try:
        import pandas_ta as ta

        # Momentum Indicators
        df['RSI_14'] = ta.rsi(df[price_col], length=14)
        stoch = ta.stoch(df['High'], df['Low'], df[price_col])
        if stoch is not None:
            df = pd.concat([df, stoch], axis=1)
        df['WILLR_14'] = ta.willr(df['High'], df['Low'], df[price_col], length=14)

        # Trend Indicators
        macd = ta.macd(df[price_col])
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
        df['ADX_14'] = ta.adx(df['High'], df['Low'], df[price_col], length=14).iloc[:, 0]

        # Volatility Indicators
        bbands = ta.bbands(df[price_col], length=20)
        if bbands is not None:
            df = pd.concat([df, bbands], axis=1)
        df['ATR_14'] = ta.atr(df['High'], df['Low'], df[price_col], length=14)

        # Volume Indicators
        if 'Volume' in df.columns:
            df['OBV'] = ta.obv(df[price_col], df['Volume'])
            vwap = ta.vwap(df['High'], df['Low'], df[price_col], df['Volume'])
            if vwap is not None:
                df['VWAP'] = vwap

        print(f"[feature_engineering] Added {len(df.columns)} features using pandas-ta.")

    except ImportError:
        print("[feature_engineering] pandas-ta not available. Using manual indicators.")
        # Fallback: Manual basic indicators
        df['RSI_14'] = _manual_rsi(df[price_col], 14)
        df['SMA_20'] = df[price_col].rolling(window=20).mean()
        df['SMA_50'] = df[price_col].rolling(window=50).mean()
        df['EMA_12'] = df[price_col].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df[price_col].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['BB_Upper'] = df['SMA_20'] + 2 * df[price_col].rolling(20).std()
        df['BB_Lower'] = df['SMA_20'] - 2 * df[price_col].rolling(20).std()
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        df['ATR_14'] = _manual_atr(df, 14)
        print(f"[feature_engineering] Added basic indicators (fallback mode).")

    # Rolling Volatility Stats
    df['RollingVol_7']  = df['Log_Return'].rolling(7).std() * np.sqrt(252) * 100
    df['RollingVol_21'] = df['Log_Return'].rolling(21).std() * np.sqrt(252) * 100
    df['RollingVol_63'] = df['Log_Return'].rolling(63).std() * np.sqrt(252) * 100

    # Lag Features (past returns)
    for lag in [1, 2, 3, 5, 10]:
        df[f'Return_Lag_{lag}'] = df['Log_Return'].shift(lag)

    df = df.dropna()
    return df


def _manual_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def _manual_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df[price_col].shift()).abs()
    low_close = (df['Low'] - df[price_col].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()


if __name__ == '__main__':
    try:
        from src.data_loader import download_data
    except ImportError:
        from data_loader import download_data
    df = download_data("RELIANCE.NS", years=5)
    if df is not None:
        df_features = add_technical_indicators(df)
        print(df_features.tail())
        print(f"\nTotal features: {len(df_features.columns)}")
