# 📈 PROJECT 3 — Financial Market Volatility Modeling

> **ATS QUANT-PRO | Next-Gen Financial Intelligence**  
> Hybrid AI system for stock volatility forecasting and market regime detection.  
> Powered by Realized GARCH · LSTM · VAE · FinBERT Sentiment · Explainable AI (SHAP/LIME)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-orange?logo=pytorch)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## 🧠 What This Project Does

This system automatically fetches live stock data (no manual download needed) and runs a pipeline of hybrid AI models to:

- 📊 **Predict volatility** using a blend of Realized GARCH (statistical) + LSTM (deep learning)
- 🌍 **Detect market regimes** (Calm / Crisis) using a Variational Autoencoder (VAE) + Bayesian Change-Point Detection
- 📰 **Analyze news sentiment** using FinBERT (a finance-specific language model)
- 🧩 **Explain every prediction** using SHAP and LIME (so we know *why* the model said what it said)
- 📉 **Backtest the strategy** and compute Sharpe Ratio, Sortino Ratio, Max Drawdown, VaR, CVaR

---

## 🗂️ Project Structure

```
QuantVision-Volatility-Regime-AI/
│
├── app.py                    ← Main Streamlit dashboard (run this!)
├── requirements.txt          ← All Python dependencies
├── .gitignore                ← Files excluded from Git
│
├── src/                      ← Core AI/ML modules
│   ├── data_loader.py        ← Fetches stock data via yfinance (no download needed)
│   ├── feature_engineering.py← 50+ technical indicators (RSI, MACD, Bollinger, etc.)
│   ├── advanced_volatility.py← Realized GARCH + LSTM Neural Volatility ensemble
│   ├── advanced_regime.py    ← VAE anomaly scorer + Bayesian change-point detection
│   ├── sentiment_engine.py   ← FinBERT news sentiment analysis
│   ├── deep_model.py         ← LSTM quantile forecaster (7-day, 30-day horizons)
│   ├── explainability.py     ← SHAP & LIME feature importance + plain-English narrative
│   └── backtest.py           ← Strategy simulation (Sharpe, Sortino, VaR, MaxDD)
│
├── assets/                   ← Generated charts and plots
│   ├── acf_plots.png
│   ├── market_regimes.png
│   ├── confidence_intervals.png
│   └── volatility_models_comparison.png
│
├── docs/                     ← Exploratory scripts and reports
│   ├── eda.py                ← Exploratory Data Analysis
│   ├── evaluate.py           ← Model evaluation utilities
│   ├── models.py             ← Baseline model comparisons
│   └── forecast.py           ← Standalone forecasting script
│
├── data/                     ← (Auto-generated) Downloaded price data cached here
├── models/                   ← (Auto-generated) Saved model checkpoints
└── notebooks/                ← Place for Jupyter notebooks (experiments)
```

---

## ⚙️ Setup & Installation

### Step 1 – Clone the repository
```bash
git clone https://github.com/karthikeyachalla/QuantVision-Volatility-Regime-AI.git
cd QuantVision-Volatility-Regime-AI
```

### Step 2 – Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate          # Mac / Linux
# OR on Windows: .venv\Scripts\activate
```

### Step 3 – Install all dependencies
```bash
pip install -r requirements.txt
```
> ✅ This installs everything: PyTorch, Transformers, pandas-ta, SHAP, vectorbt, yfinance, Streamlit, etc.

### Step 4 – Run the dashboard
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501` 🎉

> **No manual data download needed!** The system fetches live stock data automatically via `yfinance` the moment you enter a ticker symbol.

---

## 📡 Data Sources

| Source | Library | What it provides |
|--------|---------|-----------------|
| Yahoo Finance | `yfinance` | Historical OHLCV prices (daily + 5-min intraday) and news headlines |
| FinBERT | `transformers` | Sentiment scores for news headlines (Positive / Negative / Neutral) |
| Reddit *(optional)* | `praw` | Social sentiment (requires API keys in `.env`) |

---

## 🤖 Models Used

| Model | Type | Purpose |
|-------|------|---------|
| **Realized GARCH** | Statistical | Baseline volatility estimation from high-frequency (5-min) returns |
| **LSTM Neural Net** | Deep Learning | Learns residual patterns missed by GARCH |
| **Ensemble (GARCH + LSTM)** | Hybrid | Weighted blend using inverse-RMSE; best of both worlds |
| **VAE (Variational Autoencoder)** | Unsupervised DL | Detects anomalous/extreme market states (anomaly score 0–100) |
| **Bayesian Change-Point Detection** | Probabilistic | Finds structural breaks in the market (e.g., crash onset dates) |
| **LSTM Quantile Forecaster** | Deep Learning | 7-day and 30-day price forecasts with 10%/50%/90% confidence bands |
| **FinBERT** | NLP Transformer | Finance-specific sentiment analysis on news headlines |
| **SHAP + LIME** | XAI | Explains *why* the model made a specific prediction |

---

## 📊 Evaluation Metrics

| Metric | What it measures |
|--------|----------------|
| **MSE / RMSE / MAE** | Statistical accuracy of price/volatility forecasts |
| **Directional Accuracy** | % of times the model correctly predicts up/down |
| **Sharpe Ratio** | Risk-adjusted return (higher = better) |
| **Sortino Ratio** | Downside-risk-adjusted return |
| **Max Drawdown** | Worst peak-to-trough loss in the backtest |
| **VaR (95%)** | Maximum expected daily loss at 95% confidence |
| **CVaR (95%)** | Average loss beyond the VaR threshold |

---

## 📈 Dashboard Tabs

| Tab | What you see |
|-----|-------------|
| 🧠 **Neural Reasoning** | SHAP feature importance + plain-English AI explanation |
| 📰 **News Pulse** | Latest headlines with FinBERT sentiment scores |
| 📉 **Market Overview** | Ensemble volatility + regime detection + anomaly score |
| 🔭 **Technical Proofs** | RSI, MACD, Bollinger Bands, VWAP charts |
| 📊 **Backtesting Report** | Equity curve, Sharpe, Sortino, MaxDD, VaR |

---

## 🧪 Validation Strategy

The model is validated properly using **time-series-safe** methods:

1. **Chronological split** → Train (70%) | Validation (15%) | Test (15%) — no data leakage
2. **Walk-forward validation** → Rolling windows that mimic real-world prediction
3. **Early stopping** → Training stops when validation MSE stops improving
4. **Back-testing** → Financial performance verified on the held-out test set

---

## 📦 Key Dependencies

```
streamlit          ← Dashboard UI
yfinance           ← Automatic live data fetching
pandas-ta          ← 150+ technical indicators
torch              ← PyTorch deep learning framework
transformers       ← FinBERT sentiment model (HuggingFace)
shap               ← Explainable AI (SHAP values)
lime               ← Explainable AI (LIME)
arch               ← GARCH volatility models
ruptures           ← Bayesian change-point detection
vectorbt           ← Fast backtesting engine
praw               ← Reddit sentiment (optional)
```

---

## 👨‍💻 Author

**Karthikeya Challa** | [@karthikeyachalla](https://github.com/karthikeyachalla)  
Project for **Applied Time Series** — Project Based Learning (PBL)

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.  
Free to use, modify, and share with attribution. ✅
