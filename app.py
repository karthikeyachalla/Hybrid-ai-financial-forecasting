import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import time

from src.data_loader import download_data
from src.feature_engineering import add_technical_indicators
from src.advanced_volatility import generate_ensemble_forecast
from src.advanced_regime import analyze_regime
from src.sentiment_engine import fetch_news_sentiment, get_sentiment_gauge_color
from src.explainability import generate_plain_english_explanation
from src.backtest import run_backtest, format_backtest_report

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ATS QUANT-PRO | Next-Gen Intelligence",
    page_icon="🧬",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');

    :root {
        --primary-glow: #00f2ff;
        --secondary-glow: #bc13fe;
        --glass-bg: rgba(26, 28, 36, 0.7);
        --glass-border: rgba(255, 255, 255, 0.1);
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
        max-width: 98rem !important;
    }

    .stApp {
        background: radial-gradient(circle at 50% 0%, #1a1c2c 0%, #0e1117 100%);
        font-family: 'Inter', sans-serif;
    }

    [data-testid="stHeader"] { background: rgba(0,0,0,0); }

    .main-title {
        font-size: 3.0rem;
        font-weight: 800;
        background: linear-gradient(90deg, #00f2ff, #bc13fe, #ff6b35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        animation: fadeIn 1.5s ease-out;
    }

    .main-subtitle {
        color: #8b949e;
        margin-bottom: 1.5rem;
        text-align: center;
        font-size: 0.9rem;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(14px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.4rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.37);
        margin-bottom: 1rem;
    }

    .glass-card:hover {
        border-color: var(--primary-glow);
        transform: translateY(-4px);
        box-shadow: 0 12px 48px 0 rgba(0,242,255,0.2);
    }

    .tech-metric {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1;
    }

    .metric-label {
        color: #8b949e;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 8px;
    }

    .badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.7rem;
        letter-spacing: 1px;
        font-weight: 700;
        margin-top: 6px;
    }

    .badge-green  { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; }
    .badge-red    { background: rgba(255,51,102,0.15); color: #ff3366; border: 1px solid #ff3366; }
    .badge-orange { background: rgba(255,136,0,0.15);  color: #ff8800; border: 1px solid #ff8800; }
    .badge-blue   { background: rgba(0,242,255,0.15);  color: #00f2ff; border: 1px solid #00f2ff; }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3665/3665923.png", width=70)
st.sidebar.markdown("### 🎛️ MASTER CONTROL")

stocks = ["^NSEI", "RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "INFY.NS",
          "ICICIBANK.NS", "AAPL", "NVDA", "TSLA", "BTC-USD", "MSFT"]
selected_stock = st.sidebar.selectbox("🎯 Target Asset", stocks, index=1)
years_scope    = st.sidebar.slider("🕰️ Temporal Scope (Years)", 1, 15, 5)

use_finbert = st.sidebar.toggle("🤖 Use FinBERT (Slower, Better)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("**Architecture:**")
st.sidebar.markdown("- Realized GARCH + Neural Vol\n- VAE Anomaly Scorer\n- Bayesian Change-Points\n- FinBERT Sentiment\n- LSTM Multi-Horizon\n- SHAP Explainability\n- Backtesting Engine")
st.sidebar.caption("QUANT-PRO v4.0 | Hybrid AI Edition")

# ─────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("<h1 class='main-title'>ATS QUANT-PRO</h1>", unsafe_allow_html=True)
st.markdown("<p class='main-subtitle'>Next-Gen Financial Intelligence · Hybrid AI · Explainable Finance</p>",
            unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# MAIN SCAN BUTTON
# ─────────────────────────────────────────────────────────────
if st.sidebar.button("⚡ INITIATE QUANT SCAN", use_container_width=True):

    with st.spinner(f"🧬 Running Hybrid AI Engine for **{selected_stock}**... (this may take ~30s)"):

        # 1. Download & feature engineer
        df = download_data(selected_stock, years_scope)
        if df is None:
            st.error("FATAL: Asset Synchronization Timeout. Check network connectivity.")
            st.stop()

        df = add_technical_indicators(df)

        # 2. Advanced Volatility Ensemble
        vol_result = generate_ensemble_forecast(df)

        # 3. Advanced Regime Analysis
        regime_result = analyze_regime(df)

        # 4. Sentiment
        sentiment_result = fetch_news_sentiment(selected_stock, use_finbert=use_finbert)

        # 5. Backtest
        bt_result = run_backtest(df, vol_result['realized_vol'])

        # 6. XAI Explanation
        # Lightweight SHAP (correlation fallback) for speed
        shap_info = {
            'method': 'Correlation',
            'top_features': [
                {'feature': c, 'importance': round(abs(df[c].corr(
                    df['Adj Close'] if 'Adj Close' in df.columns else df['Close'])), 4)}
                for c in df.columns
                if c not in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume',
                             'Return', 'Log_Return', 'Realized_Vol']
                and df[c].dtype in [float, 'float64', 'int64']
            ][:8]
        }
        shap_info['top_features'].sort(key=lambda x: x['importance'], reverse=True)

        explanation = generate_plain_english_explanation(
            regime_result, vol_result, sentiment_result, shap_info, selected_stock)

    # ────────────────────────────────────────────────
    # ROW 1: Key Metric Cards
    # ────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        badge_class = "badge-green" if regime_result['regime'] == "CALM" else \
                      "badge-orange" if regime_result['regime'] == "VOLATILE" else "badge-red"
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Ensemble Volatility</div>
            <div class="tech-metric">{vol_result['ensemble_vol']:.2f}%</div>
            <span class="badge badge-blue" style="margin-top:6px">GARCH {vol_result['w_garch']:.0%} · Neural {vol_result['w_neural']:.0%}</span>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Regime (VAE)</div>
            <div class="tech-metric" style="color:{regime_result['regime_color']}">{regime_result['regime']}</div>
            <span class="badge {badge_class}">Anomaly: {regime_result['anomaly_score']:.1f}/100</span>
        </div>""", unsafe_allow_html=True)
    with c3:
        sent_color = get_sentiment_gauge_color(sentiment_result['sentiment_score'])
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">News Sentiment</div>
            <div class="tech-metric" style="font-size:1.6rem; color:{sent_color}">{sentiment_result['sentiment_label']}</div>
            <span class="badge" style="background:rgba(255,255,255,0.05); color:{sent_color}; border:1px solid {sent_color}">
                Score: {sentiment_result['sentiment_score']:+.3f} · {sentiment_result['num_articles']} articles
            </span>
        </div>""", unsafe_allow_html=True)
    with c4:
        bt_color = "#00ff88" if bt_result.get('sharpe_ratio', 0) > 1 else \
                   "#ff8800" if bt_result.get('sharpe_ratio', 0) > 0.5 else "#ff3366"
        st.markdown(f"""
        <div class="glass-card">
            <div class="metric-label">Sharpe Ratio (Backtest)</div>
            <div class="tech-metric" style="color:{bt_color}">{bt_result.get('sharpe_ratio', 'N/A')}</div>
            <span class="badge" style="background:rgba(255,255,255,0.05); color:{bt_color}; border:1px solid {bt_color}">
                Return: {bt_result.get('total_return_pct', 0):+.1f}% vs BH: {bt_result.get('benchmark_return_pct', 0):+.1f}%
            </span>
        </div>""", unsafe_allow_html=True)

    # ────────────────────────────────────────────────
    # TABS
    # ────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧠 Neural Reasoning",
        "📰 News Pulse",
        "📉 Market Overview",
        "🔭 Technical Proofs",
        "📊 Backtesting Report"
    ])

    # TAB 1 — Neural Reasoning (XAI)
    with tab1:
        st.markdown("### 🧠 Why Did The Model Say This?")
        st.markdown(f"""<div class="glass-card" style="border-left: 5px solid #bc13fe; line-height:1.8;">
            {explanation}
        </div>""", unsafe_allow_html=True)

        colA, colB = st.columns(2)
        with colA:
            st.markdown("**📊 Feature Importance (Correlation-Based)**")
            if shap_info['top_features']:
                feat_df = pd.DataFrame(shap_info['top_features'])
                fig_fi = go.Figure(go.Bar(
                    x=feat_df['importance'], y=feat_df['feature'],
                    orientation='h', marker_color='#bc13fe', opacity=0.85
                ))
                fig_fi.update_layout(height=300, template="plotly_dark",
                                     margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig_fi, use_container_width=True)

        with colB:
            st.markdown("**🕐 Structural Breaks Detected**")
            if regime_result.get('change_points'):
                dates_str = [str(d.date()) if hasattr(d, 'date') else str(d)
                             for d in regime_result['change_points']]
                for i, d in enumerate(dates_str, 1):
                    st.markdown(f"- **Break {i}:** `{d}`")
            else:
                st.info("No significant structural breaks detected in this period.")

            st.markdown("**⚖️ Ensemble Weights**")
            w_df = pd.DataFrame({
                'Model': ['GARCH', 'Neural LSTM'],
                'Weight': [vol_result['w_garch'], vol_result['w_neural']],
                'RMSE':   [vol_result['garch_rmse'], vol_result['neural_rmse']]
            })
            st.dataframe(w_df, use_container_width=True, hide_index=True)

    # TAB 2 — News Pulse
    with tab2:
        st.markdown("### 📰 Real-Time News Intelligence")
        sent_color = get_sentiment_gauge_color(sentiment_result['sentiment_score'])
        st.markdown(f"""<div class="glass-card" style="border-left: 5px solid {sent_color};">
            <h4 style="color:{sent_color}; margin:0">{sentiment_result['sentiment_label']} SIGNAL</h4>
            <p style="font-size:1.1rem; color:#ccc; margin:8px 0 0">
                Composite Score: <b style="color:{sent_color}">{sentiment_result['sentiment_score']:+.4f}</b>
                &nbsp;·&nbsp; Based on {sentiment_result['num_articles']} articles
            </p>
        </div>""", unsafe_allow_html=True)

        if sentiment_result.get('headlines'):
            st.markdown("**📋 Latest Headlines & Scores**")
            for h in sentiment_result['headlines']:
                score = h['score']
                hcolor = "#00ff88" if score > 0.1 else "#ff3366" if score < -0.1 else "#aaaaaa"
                st.markdown(f"""<div class="glass-card" style="padding:0.8rem 1rem; margin-bottom:0.5rem">
                    <span style="color:{hcolor}; font-family: monospace; font-size:0.85rem">[{score:+.2f}]</span>
                    &nbsp;&nbsp;<span style="color:#ddd; font-size:0.9rem">{h['title']}</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No news articles found for this ticker right now.")

        st.info("ℹ️ Enable **FinBERT** in the sidebar for higher-quality sentiment analysis using a financial language model.", icon="🤖")

    # TAB 3 — Market Overview
    with tab3:
        st.markdown("### 📉 Price · Returns · Volatility Overview")
        p_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True,
                            vertical_spacing=0.04,
                            subplot_titles=['Price', 'Log Return %', 'Rolling Volatility (21D)'])
        fig.add_trace(go.Scatter(x=df.index, y=df[p_col], name="Price",
                                 line=dict(color='#00f2ff', width=2)), row=1, col=1)
        fig.add_trace(go.Bar(x=df.index, y=df['Log_Return']*100, name="Log Return",
                             marker_color='#bc13fe', opacity=0.6), row=2, col=1)
        rv = vol_result['realized_vol']
        fig.add_trace(go.Scatter(x=rv.index, y=rv, name="Realized Vol",
                                 line=dict(color='#ff6b35', width=1.5)), row=3, col=1)
        fig.add_hline(y=vol_result['ensemble_vol'], line_dash="dash",
                      line_color="#ffffff", opacity=0.5,
                      annotation_text=f"Tomorrow Forecast: {vol_result['ensemble_vol']:.2f}%",
                      row=3, col=1)
        fig.update_layout(height=550, template="plotly_dark",
                          margin=dict(l=0,r=0,t=30,b=0), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        # 3D Volatility Surface
        st.markdown("### 🌋 3D Volatility Surface")
        h_vol = rv.values
        s_df  = df.iloc[-len(h_vol):]
        fig3d = go.Figure(data=[go.Scatter3d(
            x=np.arange(len(s_df)), y=s_df[p_col], z=h_vol,
            mode='markers',
            marker=dict(size=3, color=h_vol, colorscale='Plasma', opacity=0.85)
        )])
        fig3d.update_layout(
            scene=dict(xaxis_title='Time', yaxis_title='Price', zaxis_title='Vol %',
                       camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))),
            height=600, template="plotly_dark", margin=dict(l=0,r=0,t=0,b=0))
        st.plotly_chart(fig3d, use_container_width=True)

    # TAB 4 — Technical Proofs
    with tab4:
        st.markdown("### 🔬 Technical Verification Matrix")

        from statsmodels.tsa.stattools import acf
        returns = df['Log_Return'] * 100
        acf_ret = acf(returns.dropna(), nlags=40)
        acf_sq  = acf((returns**2).dropna(), nlags=40)

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Return ACF (test for patterns)**")
            fig_acf1 = go.Figure(go.Bar(y=acf_ret, marker_color='#00f2ff'))
            fig_acf1.update_layout(height=280, template="plotly_dark",
                                   margin=dict(l=0,r=0,t=5,b=0))
            st.plotly_chart(fig_acf1, use_container_width=True)
        with col_b:
            st.markdown("**Squared ACF (Volatility Clustering Proof)**")
            fig_acf2 = go.Figure(go.Bar(y=acf_sq, marker_color='#bc13fe'))
            fig_acf2.update_layout(height=280, template="plotly_dark",
                                   margin=dict(l=0,r=0,t=5,b=0))
            st.plotly_chart(fig_acf2, use_container_width=True)

        st.markdown("**⚖️ Model RMSE Comparison**")
        rmse_data = {
            'GARCH': vol_result['garch_rmse'],
            'Neural LSTM': vol_result['neural_rmse'],
            'Ensemble': round(
                vol_result['w_garch'] * vol_result['garch_rmse'] +
                vol_result['w_neural'] * vol_result['neural_rmse'], 4)
        }
        rmse_df = pd.DataFrame(rmse_data.items(), columns=['Model', 'RMSE'])
        rmse_df['Status'] = rmse_df['RMSE'].apply(
            lambda x: '🥇 Best' if x == rmse_df['RMSE'].min() else '')
        st.table(rmse_df)

        with st.expander("🔬 GARCH Raw Parameters"):
            st.json(vol_result['garch_params'])

        if 'RSI_14' in df.columns:
            st.markdown("**📈 RSI (14-Day) Momentum**")
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI_14'],
                                         line=dict(color='#00f2ff', width=1.5), name='RSI'))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#ff3366",
                              annotation_text="Overbought (70)")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#00ff88",
                              annotation_text="Oversold (30)")
            fig_rsi.update_layout(height=250, template="plotly_dark",
                                  margin=dict(l=0,r=0,t=5,b=0), yaxis_range=[0, 100])
            st.plotly_chart(fig_rsi, use_container_width=True)

    # TAB 5 — Backtesting
    with tab5:
        st.markdown("### 📊 Strategy Backtesting Report")
        if 'error' in bt_result:
            st.error(bt_result['error'])
        else:
            m1, m2, m3, m4 = st.columns(4)
            def metric_card(title, value, color="#00f2ff"):
                return f"""<div class='glass-card' style='text-align:center'>
                    <div class='metric-label'>{title}</div>
                    <div class='tech-metric' style='color:{color}'>{value}</div>
                </div>"""
            sr_color = "#00ff88" if bt_result['sharpe_ratio'] > 1 else \
                       "#ff8800" if bt_result['sharpe_ratio'] > 0.5 else "#ff3366"
            m1.markdown(metric_card("Sharpe Ratio", bt_result['sharpe_ratio'], sr_color), unsafe_allow_html=True)
            m2.markdown(metric_card("Sortino Ratio", bt_result['sortino_ratio'], "#00f2ff"), unsafe_allow_html=True)
            m3.markdown(metric_card("Max Drawdown", f"{bt_result['max_drawdown_pct']:.2f}%", "#ff3366"), unsafe_allow_html=True)
            m4.markdown(metric_card("VaR (95%)", f"{bt_result['var_95_pct']:.3f}%", "#ff8800"), unsafe_allow_html=True)

            # Equity Curves
            st.markdown("**📈 Strategy vs Buy-and-Hold**")
            fig_bt = go.Figure()
            fig_bt.add_trace(go.Scatter(
                x=bt_result['portfolio_curve'].index,
                y=bt_result['portfolio_curve'],
                name='Our Strategy', line=dict(color='#00f2ff', width=2)))
            fig_bt.add_trace(go.Scatter(
                x=bt_result['benchmark_curve'].index,
                y=bt_result['benchmark_curve'],
                name='Buy & Hold', line=dict(color='#8b949e', width=1.5, dash='dot')))
            fig_bt.update_layout(height=400, template="plotly_dark",
                                 margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig_bt, use_container_width=True)

            col_stats1, col_stats2 = st.columns(2)
            with col_stats1:
                st.markdown(f"**Strategy Total Return:** `{bt_result['total_return_pct']:+.2f}%`")
                st.markdown(f"**Benchmark (B&H) Return:** `{bt_result['benchmark_return_pct']:+.2f}%`")
                st.markdown(f"**CVaR (95%):** `{bt_result['cvar_95_pct']:.3f}%`")
            with col_stats2:
                st.markdown(f"**Number of Trades:** `{bt_result['num_trades']}`")
                st.markdown(f"**Benchmark Sharpe:** `{bt_result['benchmark_sharpe']}`")

else:
    # Landing Page
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0;">
        <div style="font-size:5rem">🧬</div>
        <h2 style="color:#8b949e; letter-spacing:4px; font-weight:600;">HYBRID AI ENGINE ONLINE</h2>
        <p style="color:#555; font-size:1.05rem;">Multi-Modal · Explainable Finance · 7 Pillars of Intelligence</p>
        <br>
        <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap; color:#8b949e; font-size:0.85rem;">
            <span>🔬 Realized GARCH</span> <span>|</span>
            <span>🤖 Neural Vol (LSTM)</span> <span>|</span>
            <span>🧩 VAE Anomaly</span> <span>|</span>
            <span>📰 FinBERT Sentiment</span> <span>|</span>
            <span>📈 50+ Indicators</span> <span>|</span>
            <span>🧠 SHAP Explainability</span> <span>|</span>
            <span>📊 Backtest Engine</span>
        </div>
        <br>
        <p style="color:#444;">← Select a Target Asset from the sidebar, then click ⚡ INITIATE QUANT SCAN</p>
    </div>
    """, unsafe_allow_html=True)
