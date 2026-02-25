"""
explainability.py
Phase V: SHAP-based feature importance + readable explanation generation.
Falls back to correlation-based importance if SHAP is unavailable.
"""
import numpy as np
import pandas as pd


def compute_shap_importance(model_dict: dict, features: pd.DataFrame,
                             n_background: int = 50) -> dict:
    """
    Computes SHAP feature importance for the latest prediction.
    Returns top features with their contribution direction.
    """
    feature_cols = model_dict['feature_cols']
    data = features[feature_cols].dropna().values.astype(np.float32)
    scaler = model_dict['scaler']
    data_scaled = scaler.transform(data)

    try:
        import shap

        if model_dict['type'] == 'pytorch':
            import torch

            model = model_dict['model']
            model.eval()

            def predict_fn(x):
                with torch.no_grad():
                    x_t = torch.FloatTensor(x).unsqueeze(0)
                    _, median, _ = model(x_t)
                    return median.numpy()[0]

            background = data_scaled[-n_background:]
            explainer = shap.KernelExplainer(
                lambda x: np.array([predict_fn(xi) for xi in x.reshape(-1, 30, len(feature_cols))]),
                background.reshape(n_background, -1)
            )
            last_seq = data_scaled[-30:].reshape(1, -1)
            shap_values = explainer.shap_values(last_seq, nsamples=50)

            # Average across horizon steps
            if isinstance(shap_values, list):
                shap_mean = np.abs(np.mean([sv for sv in shap_values], axis=0)).flatten()
            else:
                shap_mean = np.abs(shap_values).flatten()

            # Map back to feature names (averaged over lookback window)
            n_features = len(feature_cols)
            feature_importance = {}
            for i, col in enumerate(feature_cols):
                feature_importance[col] = float(np.mean(shap_mean[i::n_features]))

        else:
            # sklearn model: use model.coef_
            model = model_dict['model']
            coef = np.abs(model.coef_).mean(axis=0) if model.coef_.ndim > 1 else np.abs(model.coef_)
            n = len(feature_cols)
            feature_importance = {feature_cols[i]: float(np.mean(coef[i::n]))
                                   for i in range(n)}

        method = 'SHAP'

    except (ImportError, Exception) as e:
        print(f"[Explainability] SHAP failed ({e}). Using correlation fallback.")
        # Correlation-based fallback
        price_col = 'Adj Close' if 'Adj Close' in features.columns else 'Close'
        feature_importance = {}
        for col in feature_cols:
            if col in features.columns and col != price_col:
                corr = features[col].corr(features[price_col])
                feature_importance[col] = abs(float(corr)) if not np.isnan(corr) else 0.0
            else:
                feature_importance[col] = 0.0
        method = 'Correlation'

    # Sort and pick top 8
    sorted_fi = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:8]
    top_features = [{'feature': k, 'importance': round(v, 4)} for k, v in sorted_fi]

    return {
        'method': method,
        'top_features': top_features,
        'all_importances': feature_importance,
    }


def generate_plain_english_explanation(
        regime_info: dict,
        vol_info: dict,
        sentiment_info: dict,
        shap_info: dict,
        ticker: str) -> str:
    """
    Generates a human-readable explanation of WHY the model made its prediction.
    This is the XAI (Explainable AI) narrative.
    """
    regime   = regime_info.get('regime', 'CALM')
    anomaly  = regime_info.get('anomaly_score', 0)
    vol      = vol_info.get('ensemble_vol', vol_info.get('garch_vol', 0))
    w_neural = vol_info.get('w_neural', 0.5)
    sentiment_label = sentiment_info.get('sentiment_label', 'NEUTRAL')
    sentiment_score = sentiment_info.get('sentiment_score', 0)
    top_features    = shap_info.get('top_features', [])
    method          = shap_info.get('method', 'Correlation')
    change_points   = regime_info.get('change_points', [])

    narrative = []

    # Opening
    if regime == 'CRISIS':
        narrative.append(f"⚠️ **{ticker} is in CRISIS mode.** Our VAE anomaly detector has "
                         f"flagged an extreme market state (anomaly score: {anomaly:.1f}/100).")
    elif regime == 'VOLATILE':
        narrative.append(f"🔥 **{ticker} is in a VOLATILE regime.** The market is showing "
                         f"signs of stress (anomaly score: {anomaly:.1f}/100).")
    else:
        narrative.append(f"✅ **{ticker} is in a CALM regime.** Market conditions appear "
                         f"stable (anomaly score: {anomaly:.1f}/100).")

    # Volatility explanation
    narrative.append(f"\n\n**📊 Predicted Volatility: {vol:.2f}%**  "
                     f"The Neural LSTM contributed {w_neural*100:.0f}% weight to this estimate.")

    # Sentiment
    if sentiment_label == 'BULLISH':
        narrative.append(f"\n\n**📰 News Pulse: BULLISH** (score: +{sentiment_score:.2f}). "
                         f"Recent headlines have a positive tone, suggesting market confidence.")
    elif sentiment_label == 'BEARISH':
        narrative.append(f"\n\n**📰 News Pulse: BEARISH** (score: {sentiment_score:.2f}). "
                         f"Recent news is casting a shadow over this asset.")
    else:
        narrative.append(f"\n\n**📰 News Pulse: NEUTRAL** (score: {sentiment_score:.2f}). "
                         f"News flow has no strong directional signal right now.")

    # Top features
    if top_features:
        narrative.append(f"\n\n**🧠 Key Drivers ({method} Analysis):**")
        for f in top_features[:4]:
            narrative.append(f"\n  • `{f['feature']}` — importance: {f['importance']:.4f}")

    # Structural breaks
    if change_points:
        last_bp = change_points[-1]
        last_bp_str = last_bp.strftime('%d %b %Y') if hasattr(last_bp, 'strftime') else str(last_bp)
        narrative.append(f"\n\n**📍 Last Structural Break Detected:** {last_bp_str} — "
                         f"the market's behavior changed significantly around this date.")

    return ''.join(narrative)


if __name__ == '__main__':
    print("explainability.py: Test requires a trained model. "
          "Run app.py or individual modules to test.")
