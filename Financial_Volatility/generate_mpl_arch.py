import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

def draw_box(ax, x, y, width, height, text, color):
    # Add shadow
    shadow = patches.FancyBboxPatch((x+1, y-1), width, height, boxstyle="round,pad=1", fill=True, color='gray', alpha=0.3)
    ax.add_patch(shadow)
    # Add box
    box = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=1", facecolor=color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text, ha='center', va='center', fontsize=10, fontweight='bold', color='white', family='sans-serif')

def draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", lw=2, color='black'))

# Data layer
draw_box(ax, 5, 75, 20, 10, "Data Ingestion\n(YFinance API)", "#1f77b4")
draw_box(ax, 5, 55, 20, 10, "News Scraping\n(Financial News)", "#1f77b4")

# Processing layer
draw_box(ax, 35, 75, 20, 10, "Feature Engineering\n(pandas-ta)", "#ff7f0e")

# Models layer
draw_box(ax, 35, 45, 20, 10, "Volatility Engine\n(GARCH + LSTM)", "#2ca02c")
draw_box(ax, 35, 25, 20, 10, "Regime Detection\n(VAE Anomaly)", "#2ca02c")
draw_box(ax, 35, 5, 20, 10, "Sentiment Analysis\n(FinBERT NLP)", "#d62728")

# Forecasting layer
draw_box(ax, 70, 45, 25, 15, "Quantile Forecaster\n(LSTM + Confidence)", "#9467bd")
draw_box(ax, 70, 15, 25, 10, "Explainable AI\n(SHAP & LIME)", "#8c564b")

# Arrows
draw_arrow(ax, 26, 80, 34, 80) # Ingest -> Features
draw_arrow(ax, 26, 60, 34, 10) # News -> Sentiment (adjusted logic)

draw_arrow(ax, 45, 74, 45, 56) # Features -> Vol
draw_arrow(ax, 56, 75, 82, 61) # Features -> Forecaster

draw_arrow(ax, 56, 50, 69, 50) # Vol -> Forecaster
draw_arrow(ax, 56, 30, 69, 45) # Regime -> Forecaster
draw_arrow(ax, 56, 10, 69, 45) # Sentiment -> Forecaster

draw_arrow(ax, 82.5, 44, 82.5, 26) # Forecaster -> XAI

plt.title("QUANT-PRO System Architecture", fontsize=16, fontweight='bold', family='sans-serif', pad=20)
plt.tight_layout()
plt.savefig("assets/arch_diagram.png", dpi=300, bbox_inches='tight')
print("Saved assets/arch_diagram.png")
