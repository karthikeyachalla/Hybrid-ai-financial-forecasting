import yfinance as yf
import pandas as pd
import numpy as np
import os

def download_data(ticker="^NSEI", years=10):
    """
    Downloads historical data and calculates returns.
    """
    print(f"Downloading {years} years of data for {ticker}...")
    try:
        data = yf.download(ticker, period=f"{years}y")
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None
    
    if data.empty:
        print(f"No data found for the given ticker {ticker} or period.")
        return None
    
    # Handle MultiIndex if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        
    # Check for 'Adj Close', fallback to 'Close'
    target_col = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
    
    # Calculate Returns
    data['Return'] = data[target_col].pct_change()
    
    # Calculate Log Returns
    data['Log_Return'] = np.log(data[target_col] / data[target_col].shift(1))
    
    # Drop first row (NaN from returns)
    data = data.dropna()
    
    # Save to CSV (Optional, but kept for compatibility)
    clean_ticker = ticker.replace('^', '').replace('-', '_')
    filename = f"{clean_ticker}_{years}y_data.csv"
    data.to_csv(filename)
    print(f"Data saved to {filename}")
    return data

if __name__ == "__main__":
    download_data()
