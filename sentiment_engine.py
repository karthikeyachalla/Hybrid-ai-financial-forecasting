"""
sentiment_engine.py
Phase II: Multi-source sentiment fusion using FinBERT + yfinance news
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

# FinBERT sentiment (HuggingFace Transformers)
def _load_finbert():
    try:
        from transformers import pipeline
        sentiment_pipeline = pipeline(
            "text-classification",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            truncation=True,
            max_length=512
        )
        return sentiment_pipeline
    except Exception as e:
        print(f"[sentiment] FinBERT load failed: {e}. Using keyword fallback.")
        return None

_FINBERT_PIPELINE = None

def _score_text_finbert(pipeline, text: str) -> float:
    """Returns a float between -1 (negative) and +1 (positive)."""
    try:
        result = pipeline(text[:512])[0]
        label = result['label'].lower()
        score = result['score']
        if label == 'positive':
            return score
        elif label == 'negative':
            return -score
        else:
            return 0.0
    except Exception:
        return 0.0

def _score_text_keyword(text: str) -> float:
    """Simple keyword-based fallback sentiment scorer."""
    text_lower = text.lower()
    positive_words = ['surge', 'gain', 'beat', 'profit', 'growth', 'rally', 'bullish',
                      'record', 'outperform', 'upgrade', 'buy', 'strong', 'rise', 'up',
                      'positive', 'boom', 'soar', 'high', 'innovation', 'expansion']
    negative_words = ['crash', 'loss', 'miss', 'fall', 'drop', 'bearish', 'sell',
                      'downgrade', 'decline', 'plunge', 'weak', 'risk', 'crisis',
                      'inflation', 'recession', 'cut', 'layoff', 'fraud', 'investigation']
    pos = sum(1 for w in positive_words if w in text_lower)
    neg = sum(1 for w in negative_words if w in text_lower)
    total = pos + neg
    if total == 0:
        return 0.0
    return (pos - neg) / total

def fetch_news_sentiment(ticker: str, use_finbert: bool = True) -> dict:
    """
    Fetches latest news for a ticker from yfinance and scores with FinBERT or keyword fallback.
    Returns a dict with sentiment score and headline evidence.
    """
    global _FINBERT_PIPELINE

    try:
        t = yf.Ticker(ticker)
        news_items = t.news[:10] if t.news else []
    except Exception:
        news_items = []

    if not news_items:
        return {
            'ticker': ticker,
            'sentiment_score': 0.0,
            'sentiment_label': 'NEUTRAL',
            'num_articles': 0,
            'headlines': []
        }

    # Load FinBERT once
    if use_finbert and _FINBERT_PIPELINE is None:
        _FINBERT_PIPELINE = _load_finbert()

    scores = []
    headlines = []
    for item in news_items:
        try:
            # Handle both old and new yfinance news structure
            if isinstance(item, dict):
                content = item.get('content', {})
                if isinstance(content, dict):
                    title = content.get('title', '') or item.get('title', '')
                else:
                    title = item.get('title', '') or str(content)
            else:
                title = str(item)
        except Exception:
            title = ''

        if not title:
            continue

        if _FINBERT_PIPELINE is not None and use_finbert:
            score = _score_text_finbert(_FINBERT_PIPELINE, title)
        else:
            score = _score_text_keyword(title)

        scores.append(score)
        headlines.append({'title': title, 'score': round(score, 3)})

    avg_score = float(np.mean(scores)) if scores else 0.0

    if avg_score > 0.15:
        label = 'BULLISH'
    elif avg_score < -0.15:
        label = 'BEARISH'
    else:
        label = 'NEUTRAL'

    return {
        'ticker': ticker,
        'sentiment_score': round(avg_score, 4),
        'sentiment_label': label,
        'num_articles': len(scores),
        'headlines': headlines[:5]   # top 5 for display
    }

def get_sentiment_gauge_color(score: float) -> str:
    """Returns a hex color based on sentiment score."""
    if score > 0.3:
        return '#00ff88'
    elif score > 0.1:
        return '#88ff00'
    elif score < -0.3:
        return '#ff3366'
    elif score < -0.1:
        return '#ff8800'
    else:
        return '#aaaaaa'

if __name__ == '__main__':
    tickers = ['RELIANCE.NS', 'NVDA', 'AAPL']
    for t in tickers:
        result = fetch_news_sentiment(t, use_finbert=True)
        print(f"\n{t}: {result['sentiment_label']} ({result['sentiment_score']:.3f}) — {result['num_articles']} articles")
        for h in result['headlines']:
            print(f"  [{h['score']:+.2f}] {h['title']}")
