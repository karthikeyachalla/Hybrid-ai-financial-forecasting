import streamlit as st
import joblib
import sys

class TorchScaler:
    def fit(self, X): pass
    def transform(self, X): pass
    def fit_transform(self, X): pass
    def inverse_transform(self, X): pass

try:
    scaler = joblib.load("models/global_vol_scaler.pkl")
    print("✅ Streamlit loaded successfully!")
except Exception as e:
    print("❌ Streamlit Loader failed:", e, file=sys.stderr)
