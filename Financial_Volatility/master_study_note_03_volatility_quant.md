# 📓 Master Project Study Note 03: Hybrid AI Financial Volatility & Market Regime Engine
## Track: Quantitative Finance, Deep Learning (PyTorch), Time Series & Financial NLP

> **Author:** Karthikeya Challa (Lead Developer & ML Engineer)  
> **Course:** Applied Time Series (ATS Quant-Pro)  
> **Project Path:** `/Users/karthikeyachalla/ats stock predection`

---

## 1. Executive Summary & Core Objective

### What is the project about?
This project is an **End-to-End Quantitative AI System** (`QuantVision-Volatility-Regime-AI`) that predicts financial market volatility, detects market regime shifts (Calm vs. Crisis), extracts news sentiment via NLP, and backtests trading strategies using institutional risk-adjusted metrics.

### Key Financial ML Problems Solved:
1. **Volatile Residual Modeling:** Combining classical econometric statistical models (Realized GARCH) with PyTorch LSTMs to capture non-linear market shocks.
2. **Market Regime Detection:** Using an unsupervised **Variational Autoencoder (VAE)** to score market structural anomalies (0–100 risk score).
3. **Financial NLP:** Deploying **FinBERT** (domain-adapted BERT) to quantify sentiment from financial news headlines (`yfinance`).
4. **Time-Series Safe Validation:** Enforcing **Walk-Forward Validation** (Chronological Splitting) to prevent fatal look-ahead bias.

---

## 2. Core Technical Architectures & Math

### Component 1: GARCH + LSTM Hybrid Ensemble
* **Realized GARCH (Generalized Autoregressive Conditional Heteroskedasticity):** Models time-varying conditional variance based on past squared returns and past variances:
$$\sigma_t^2 = \omega + \alpha \epsilon_{t-1}^2 + \beta \sigma_{t-1}^2$$
* **LSTM (Long Short-Term Memory) Network:** Captures long-term non-linear sequential dependencies and residual errors missed by GARCH.
* **Hybrid Inverse-RMSE Ensemble:** Combines both models dynamically, weighting predictions by their historical inverse Root Mean Squared Error (RMSE).

### Component 2: Variational Autoencoder (VAE) for Regime Detection
* **Why VAE for Market Regimes?** VAEs learn a low-dimensional continuous latent space distribution $q_\phi(z|x)$ parameterised by mean $\mu$ and variance $\sigma^2$.
* **Anomaly Score:** Reconstruction loss + Kullback-Leibler (KL) Divergence:
$$\mathcal{L}_{\text{VAE}} = \mathbb{E}[\log p_\theta(x|z)] - D_{\text{KL}}(q_\phi(z|x) \parallel p(z))$$
* When market conditions deviate significantly from historical "Calm" regimes, reconstruction error spikes $\rightarrow$ Flags **Crisis Regime**.

### Component 3: FinBERT Sentiment Engine
* **Why FinBERT over VADER or TextBlob?** Standard NLP tools fail in finance (e.g., "Company reported negative debt growth" is GOOD in finance, but generic NLP flags "negative" and "debt" as bad). FinBERT is pre-trained on financial corpora (Financial PhraseBank).

---

## 3. Institutional Financial Metrics (Must Know For Quant Roles)

| Metric | Mathematical / Intuitive Meaning |
|---|---|
| **Sharpe Ratio** | $\frac{R_p - R_f}{\sigma_p}$ — Excess return per unit of total risk. Higher is better. |
| **Sortino Ratio** | $\frac{R_p - R_f}{\sigma_d}$ — Excess return per unit of **downside risk** (ignores upside volatility). |
| **Maximum Drawdown (MaxDD)** | Peak-to-trough drop during a specific period: $\frac{\text{Trough Value} - \text{Peak Value}}{\text{Peak Value}}$. |
| **Value at Risk (VaR 95%)** | Maximum expected daily loss with 95% confidence over a given time horizon. |
| **Conditional VaR (CVaR / Expected Shortfall)** | Average loss incurred in the worst 5% tail scenarios (more robust than VaR). |

---

## 4. Why These Tools & Why NOT Alternatives?

| Tool Used | Why We Used It | Why NOT Alternatives? |
|---|---|---|
| **PyTorch (LSTM & VAE)** | Dynamic computation graphs, native tensor operations, easy custom loss functions (KL divergence). | **TensorFlow/Keras:** PyTorch is industry-standard in Quant research for custom model architectures. |
| **FinBERT (Transformers)** | Understands financial context, subword tokenization, high precision on headlines. | **Generic VADER Sentiment:** VADER lacks context and misses financial nuance completely. |
| **Walk-Forward Validation** | Retains strict chronological ordering ($T_{\text{train}} < T_{\text{val}} < T_{\text{test}}$). | **K-Fold Cross-Validation:** Standard K-Fold randomly shuffles data, leaking future prices into the past (look-ahead bias). |
| **Streamlit Dashboard** | Live, interactive UI rendering interactive technical charts and backtest curves. | **Flask/React:** For internal quantitative tools, Streamlit allows rapid iteration without backend overhead. |

---

## 5. Interview Defense Guide (How to Speak About This Project)

### ❓ Question 1: *"How do you prevent data leakage when training ML models on stock data?"*
> **Answer:** *"Standard K-Fold Cross Validation causes catastrophic look-ahead bias in time series. In my ATS Quant-Pro system, I enforced strict chronological splitting (Train 70% | Val 15% | Test 15%) and implemented Walk-Forward validation with rolling windows, ensuring no future statistical features or scalers leak into past training sets."*

### ❓ Question 2: *"Why combine GARCH with an LSTM instead of using just LSTM?"*
> **Answer:** *"GARCH provides a mathematically sound econometric baseline for conditional heteroskedasticity (volatility clustering), while LSTMs capture complex non-linear residual patterns. Combining them via inverse-RMSE weighting yields an ensemble that outperforms either standalone model on unseen market regimes."*

### ❓ Question 3: *"How does your system detect market crises without labeled training data?"*
> **Answer:** *"I used an unsupervised Variational Autoencoder (VAE) trained on normal market regimes. During market anomalies, the VAE's reconstruction error and KL-divergence spike due to out-of-distribution inputs, providing a continuous 0–100 anomaly score that automatically flags market regimes."*

---

*Master Study Note 03 created by Antigravity AI for Karthikeya Challa — July 2026*
