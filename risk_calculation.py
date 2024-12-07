from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def calculate_risk(stock, max_beta):
    """
    Berechnet den Risikowert einer Aktie basierend nur auf Beta.
    Fehlende Werte für Beta werden mit einem Standardwert (1.0) ersetzt.
    """
    # Wert für Beta extrahieren
    beta = stock.get("Beta", "N/A")
    # Fehlende Werte ersetzen
    beta = float(beta) if beta != "N/A" else 1.0  # Standardwert für Beta

    # Normalisierung des Beta-Werts basierend auf dem maximalen Beta-Wert
    beta_normalized = min(max(beta / max_beta, 0), 1)  # Normalisiert auf den maximalen Beta-Wert

    # Risikobewertung (da nur Beta verwendet wird, ist es einfach der normalisierte Beta-Wert)
    risk = beta_normalized
    return risk


def apply_risk_clustering(stock_data):
    """Clusterbildung basierend auf Beta"""
    # Berechne den maximalen Beta-Wert in den Daten
    betas = [float(stock["Beta"]) for stock in stock_data if stock.get("Beta", "N/A") != "N/A"]
    max_beta = max(betas) if betas else 2.0  # Maximaler Beta-Wert, der als Referenz dient

    # Berechne das Risiko für jede Aktie basierend auf Beta
    features = []
    for stock in stock_data:
        stock["Risk"] = calculate_risk(stock, max_beta)
        features.append([stock["Risk"]])

    # KMeans Clustering (3 Cluster: 0, 1, 2)
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(features)

    # Cluster-Zuweisung zu den Aktien
    for i, stock in enumerate(stock_data):
        stock["Cluster"] = clusters[i]
    return stock_data
