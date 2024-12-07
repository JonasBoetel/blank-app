from sklearn.metrics.pairwise import euclidean_distances


def recommend_stocks(user_stocks, all_stocks, filtered_stocks, user_ratings):
    """
    Empfehle ähnliche Aktien basierend auf Risikoprofil, Clusterzugehörigkeit und den Bewertungen des Nutzers.
    """
    # Extrahiere Risiko und Cluster der Benutzeraktien
    average_rating = get_average_rating(user_ratings)
    user_features = []
    for stock in all_stocks:
        if stock["Symbol"] in user_stocks:
            # Füge Risiko und Cluster und die Bewertungen als Features hinzu
            user_features.append([stock["Risk"], stock["Cluster"], user_ratings.get(stock["Symbol"], average_rating)])

    # Berechne die Ähnlichkeit zu den gefilterten Aktien
    filtered_features = []
    for stock in filtered_stocks:
        # Füge Risiko, Cluster und die Bewertungen als Features hinzu
        filtered_features.append([stock["Risk"], stock["Cluster"], user_ratings.get(stock["Symbol"], average_rating)])

    # Berechne die Ähnlichkeit (Euclidische Distanz) zwischen den Benutzer-Aktien und den gefilterten Aktien
    distances = euclidean_distances(user_features, filtered_features)

    # Empfehle die nächsten (ähnlichsten) Aktien
    closest_indices = distances.min(axis=0).argsort()[:5]  # Top 5 Empfehlungen
    recommendations = [filtered_stocks[i] for i in closest_indices]

    return recommendations


def get_average_rating(user_ratings):
    """
    Gibt den Durchschnitt aller Bewertungen zurück. 
    """
    return sum(user_ratings.values()) / len(user_ratings)