import sys, os
from app import TorchScaler
import joblib

path = "models/global_vol_scaler.pkl"
try:
    scaler = joblib.load(path)
    print("Success loading scaler! Type:", type(scaler))
except Exception as e:
    print("Error:", e)
