import sys, os
import joblib

# The scaler was trained directly in global scope in __main__ of the notebook,
# so when we load it here, joblib searches for `__main__.TorchScaler`.
# We need to make sure joblib can find TorchScaler here in __main__.
class TorchScaler:
    def fit(self, X): pass
    def transform(self, X): pass
    def fit_transform(self, X): pass
    def inverse_transform(self, X): pass

try:
    scaler = joblib.load("models/global_vol_scaler.pkl")
    print("✅ Loaded successfully!", type(scaler))
    print("Scaler attributes:", dir(scaler))
except Exception as e:
    print("❌ Loader failed:", e)

# The model is loaded in advanced_volatility.py, which is NOT __main__.
# So we need to ensure that advanced_volatility.py can also fool joblib.
