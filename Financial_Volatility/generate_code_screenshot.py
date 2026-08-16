import urllib.request
import os
try:
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import ImageFormatter
except ImportError:
    os.system("pip install pygments")
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import ImageFormatter

code = """
import torch
import torch.nn as nn
from arch import arch_model

class HybridVolatilityLSTM(nn.Module):
    def __init__(self, input_size=10, hidden_size=128, num_layers=2):
        super(HybridVolatilityLSTM, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, 3) # Quantiles: 10th, 50th, 90th
        
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        quantiles = self.fc(lstm_out[:, -1, :])
        return quantiles

# Baseline Statistical Engine
garch = arch_model(returns, vol='EGARCH', p=1, q=1, o=1)
garch_fit = garch.fit(disp='off')
statistical_vol = garch_fit.conditional_volatility

# Hybrid Integration
ensemble_prediction = (0.35 * statistical_vol.values[-1]) + (0.65 * lstm_prediction.item())
"""

formatter = ImageFormatter(font_size=16, line_numbers=True, style='monokai')
with open("assets/code_snippet.png", "wb") as f:
    f.write(highlight(code, PythonLexer(), formatter))
print("Code screenshot generated.")
