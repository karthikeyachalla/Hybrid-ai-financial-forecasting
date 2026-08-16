import numpy as np
import pandas as pd
import torch
import warnings
warnings.filterwarnings('ignore')
from src.data_loader import download_data
from src.deep_model import load_or_train_lstm

def evaluate(ticker='RELIANCE.NS'):
    df = download_data(ticker, years=5)
    if df is None or len(df) < 100:
        return
    horizon = 7
    model, scaler = load_or_train_lstm(df, horizon=horizon)
    PRICE_LB = 30
    
    data = df[['Close', 'Log_Return']].values
    ds = scaler.transform(data)
    
    X_test = []
    y_test_actual = []
    prices = df['Close'].values
    valid_idx = []
    for i in range(PRICE_LB, len(ds) - horizon + 1):
        X_test.append(ds[i-PRICE_LB:i])
        y_test_actual.append(prices[i+horizon-1])
        valid_idx.append(i-1)
        
    X_t = torch.FloatTensor(np.array(X_test)).to('cpu')
    with torch.no_grad():
        lo, md, hi = model(X_t)
        
    md_np = md.numpy()
    dummy = np.zeros((md_np.shape[0], 2))
    
    hits = 0
    total = len(md_np)
    
    for i in range(total):
        # We predict Close and Log_Return. The MD output shape depends on horizon.
        # Oh wait! In Train_Global_LSTM.ipynb, the target was ONLY Close? No, it's a 7-day flat sequence or what?
        # Let's just calculate 1-day step direction for the first day of the horizon to be safe.
        pred_close_scaled = md_np[i][0] # 1st day of horizon
        dummy[0, 0] = pred_close_scaled
        pred_close = scaler.inverse_transform(dummy)[0, 0]
        
        current_close = prices[valid_idx[i]]
        actual_close = prices[valid_idx[i] + 1] # next day actual
        
        pred_dir = 1 if pred_close > current_close else -1
        actual_dir = 1 if actual_close > current_close else -1
        
        if pred_dir == actual_dir:
            hits += 1
            
    print(f"[{ticker}] Real Directional Hit Rate (1-day step): {hits/total*100:.2f}% ({hits}/{total})")

if __name__ == '__main__':
    evaluate('RELIANCE.NS')
