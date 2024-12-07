import pandas as pd
import plotly.express as px

def visualize_clusters_with_highlights(stock_data, selected_stocks, recommended_stocks):
    """
    Visualisiere die Cluster der Aktien, hebe die ausgewählten und empfohlenen Aktien hervor.
    """
    
    # Konvertiere stock_data in ein DataFrame
    df = pd.DataFrame(stock_data)

    # Markiere die ausgewählten und empfohlenen Aktien
    df['Category'] = "Andere"  # Standardkategorie
    df.loc[df['Symbol'].isin(selected_stocks), 'Category'] = "Portfolio"
    df.loc[df['Symbol'].isin([stock['Symbol'] for stock in recommended_stocks]), 'Category'] = "Empfehlung"

    # Farbe für Kategorien definieren
    category_colors = {
        "Andere": "lightgray",
        "Portfolio": "blue",
        "Empfehlung": "green",
    }

    # Streudiagramm erstellen
    fig = px.scatter(
        df,
        x="Risk",
        y="Cluster",
        color="Category",
        color_discrete_map=category_colors,
        hover_data=["Symbol", "Name", "Country", "Sector", "Risk"],
        title="Risikoverteilung und Clusterzugehörigkeit",
        labels={"Risk": "Risikowert", "Cluster": "Cluster"},
        template="plotly_white",
        symbol="Category",  # Unterscheidet die Kategorie durch Symbole
    )

    # Layout anpassen
    fig.update_layout(
        xaxis_title="Risikowert",
        yaxis_title="Cluster",
        yaxis=dict(tickmode="linear"),
        showlegend=True,
    )

    return fig
