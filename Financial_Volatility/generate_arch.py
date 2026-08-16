import subprocess
try:
    from diagrams import Diagram, Cluster, Edge
    from diagrams.programming.language import Python
    from diagrams.custom import Custom
    from diagrams.onprem.database import PostgreSQL
    from diagrams.onprem.analytics import Spark
    from diagrams.generic.network import Switch
    from diagrams.generic.device import Mobile
except ImportError:
    subprocess.check_call(["pip", "install", "diagrams"])
    from diagrams import Diagram, Cluster, Edge

# Generating architecture diagram requires Graphviz installed on the system (brew install graphviz)
import os
import sys
if os.system("dot -V") != 0:
    os.system("brew install graphviz")

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.programming.framework import Fastapi
from diagrams.onprem.client import Client

try:
    with Diagram("QuantPro_Architecture", show=False, outformat="png", filename="assets/arch_diagram"):
        with Cluster("Data Ingestion"):
            data_source = Client("YFinance API")
            news_source = Client("Financial News")

        with Cluster("Preprocessing & Feature Engineering"):
            features = EC2("pandas-ta\nTechnical Indicators")
            
        with Cluster("Hybrid AI Engine"):
            with Cluster("Volatility"):
                garch = EC2("Realized GARCH")
                lstm_vol = EC2("LSTM Volatility")
                ensemble = EC2("Weighted Ensemble")
                garch >> ensemble
                lstm_vol >> ensemble
                
            with Cluster("Regime Detection"):
                vae = EC2("VAE Anomaly Scorer")
                
            with Cluster("Sentiment NLP"):
                finbert = EC2("FinBERT")
                
        with Cluster("Forecasting & XAI"):
            forecaster = EC2("LSTM Quantile Forecaster")
            xai = EC2("SHAP / LIME Explainer")
            
        ui = Client("Streamlit Dashboard")

        data_source >> features
        news_source >> finbert
        
        features >> garch
        features >> lstm_vol
        features >> vae
        features >> forecaster
        
        ensemble >> forecaster
        finbert >> forecaster
        vae >> forecaster
        
        forecaster >> xai
        xai >> ui
except Exception as e:
    print("Error:", e)
