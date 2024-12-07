import streamlit as st
import json
import yfinance as yf
from app.risk_calculation import apply_risk_clustering
from app.cluster_visualization import visualize_clusters_with_highlights
from app.user_db import create_or_select_user,record_user_ratings
from app.stock_recommendation import recommend_stocks

def search_stocks():

    # Verhindere Rerendern um Speichern der Bewertung zu ermöglichen
    try:
        # check if the key exists in session state
        _ = st.session_state.keep_graphics
    except AttributeError:
        # otherwise set it to false
        st.session_state.keep_graphics = False

    st.subheader("Teile uns mit, welche Aktien du in deinem Portfolio hast")

    # Laden der Daten aus der statischen JSON-Datei
    user_ratings = {}
    try:
        with open("Input/stock_overview_yfinance.json", "r", encoding="utf-8") as json_file:
            stock_data = json.load(json_file)
            # Liste von Symbol - Name extrahieren
            stock_list = [f"{stock['Symbol']} - {stock['Name']}" for stock in stock_data]
            print(f"Anzahl der Aktien: {len(stock_list)}")
            
            # Filter für geografische Region (Country), Industry (Sector) und MarketCapCategory
            countries = sorted(set(stock['Country'] for stock in stock_data))
            sectors = sorted(set(stock['Sector'] for stock in stock_data))
            market_cap_categories = sorted(set(stock['MarketCapCategory'] for stock in stock_data))

            # Aktien filtern, deren Beta-Wert unter dem Schwellenwert liegt
            filtered_stocks = [
                stock for stock in stock_data
                if (stock.get("Beta") != "N/A" and float(stock.get("Beta", 1.0)) <= 5)
                or stock.get("Beta") == "N/A"  # Hier berücksichtigen wir "N/A", falls vorhanden
            ]
            stock_list = [f"{stock['Symbol']} - {stock['Name']}" for stock in filtered_stocks]
            
    except Exception as e:
        st.error(f"Fehler beim Laden der Aktienliste: {e}")
        return

    # **2. Clusterbildung basierend auf Risiko**
    stock_data = apply_risk_clustering(filtered_stocks)

    # **Benutzer erstellen oder auswählen**
    username, user_data = create_or_select_user()
    if username in user_data:
        user_ratings = user_data[username]['ratings']

    st.session_state['user'] = username

    # **3. Nutzerauswahl: Eigene Aktien**
    st.subheader("Deine Aktienauswahl")
    stock_selection_user = st.multiselect(
        "Gib deine Aktien ein oder wähle aus der Liste: ",
        stock_list,
        key="stock_selection"
    )

    # **4. Cluster-Auswahl**
    st.subheader("Cluster-Auswahl")
    cluster_filter = st.selectbox(
        "Wähle ein Cluster basierend auf Risiko:",
        ["Alle", "Risikoarm (0)", "Mittelrisiko (1)", "Risikoreich (2)"],
        key="cluster_filter"
    )

    # **5. Filter: Region, Sektor, Unternehmensgröße**
    st.subheader("Filter")

    # Geografische Region (Country) Filter - multiselect für mehrere Länder
    country_filter = st.multiselect(
        "Wähle eine oder mehrere geografische Regionen (Länder):",
        ["Alle"] + countries,
        key="country_filter"
    )

    # Industry (Sector) Filter
    sector_filter = st.selectbox(
        "Wähle eine Industrie (Sektor):",
        ["Alle"] + sectors,
        key="sector_filter"
    )

    # Unternehmensgröße (MarketCapCategory) Filter
    market_cap_filter = st.selectbox(
        "Wähle eine Unternehmensgröße:",
        ["Alle"] + market_cap_categories,
        key="market_cap_filter"
    )

    # Anzeige der ausgewählten Filter
    st.write("Ausgewählte Filter:")
    st.write(f"Land: {country_filter}")
    st.write(f"Sektor: {sector_filter}")
    st.write(f"Unternehmensgröße: {market_cap_filter}")
    
    # Submit Button für die Filterung der Aktien
    if st.button("Aktien filtern", type="primary") or st.session_state.keep_graphics:
        st.session_state.keep_graphics = True
        # Herausfiltern der Aktien, die den Filterkriterien entsprechen
        filtered_stocks = []
        # **Aktien filtern**
        if "filtered_stocks" not in st.session_state:
            st.session_state.filtered_stocks = []

        user_stock_symbols = [s.split(" - ")[0] for s in stock_selection_user]

        for stock in stock_data:
            # Überprüfen, ob die Aktie in der Benutzerauswahl enthalten ist
            if f"{stock['Symbol']} - {stock['Name']}" in stock_selection_user:
                continue  # Diese Aktie überspringen, da sie vom Benutzer ausgewählt wurde

            # Geografische Region (Country) Filter anwenden
            if country_filter != ["Alle"] and stock['Country'] not in country_filter:
                continue

            # Industry (Sector) Filter anwenden
            if sector_filter != "Alle" and stock['Sector'] != sector_filter:
                continue

            # Unternehmensgröße (MarketCapCategory) Filter anwenden
            if market_cap_filter != "Alle" and stock['MarketCapCategory'] != market_cap_filter:
                continue

            # Cluster-Filter anwenden
            if cluster_filter != "Alle":
                cluster_mapping = {"Risikoarm (0)": 0, "Mittelrisiko (1)": 1, "Risikoreich (2)": 2}
                cluster_value = cluster_mapping.get(cluster_filter, None)
                if cluster_value is not None and stock["Cluster"] != cluster_value:
                    continue  # Diese Aktie überspringen, wenn sie nicht im ausgewählten Cluster ist

            # Wenn alle Filterbedingungen erfüllt sind, die Aktie zur gefilterten Liste hinzufügen
            st.session_state.filtered_stocks.append(stock)


        # **7. Ähnlichkeit berechnen und Empfehlungen anzeigen**
        if st.session_state.filtered_stocks:
            recommendations = recommend_stocks(user_stock_symbols, stock_data, st.session_state.filtered_stocks, user_ratings)
            st.write("Empfohlene Aktien basierend auf Ähnlichkeit:")
            for stock in recommendations:
                # Box um die Aktie hinzufügen
                st.markdown(f"""
                <div style="border:2px solid #0099ff; border-radius: 10px; padding: 10px; margin-bottom: 20px; background-color: #f5f5f5;">
                    <h3>{stock['Symbol']} - {stock['Name']}</h3>
                    <p><strong>Land:</strong> {stock['Country']}</p>
                    <p><strong>Sektor:</strong> {stock['Sector']}</p>
                    <p><strong>Risiko:</strong> {stock['Risk']:.2f}</p>
                </div>
                """, unsafe_allow_html=True)

                # Jetzt YFinance Abfrage für Detailinformationen
                ticker = stock['Symbol']
                stock_info = yf.Ticker(ticker)
                info = stock_info.info

                # Card für die Aktieninformationen
                with st.expander(f"Mehr Infos zu {ticker}"):
                    st.write(f"**Letzter Preis (Close):** {info.get('previousClose', 'N/A')}")
                    st.write(f"**MarketCap Kategorie:** {stock['MarketCapCategory']}")
                    st.write(f"**Beschreibung:** {info.get('longBusinessSummary', 'N/A')}")

                # Kursdaten der letzten 365 Tage
                historical_data = stock_info.history(period="1y")  # 1 Jahr

                # Diagramm der täglichen Kurse
                st.subheader(f"Kursverlauf für {ticker} (letzte 365 Tage)")
                st.line_chart(historical_data['Close'])
            
            # Cluster-Risiko-Visualisierung
            st.subheader("Cluster-Risiko-Visualisierung")
            cluster_fig_highlighted = visualize_clusters_with_highlights(
                stock_data,
                selected_stocks=[stock.split(" - ")[0] for stock in stock_selection_user],  # Symbole extrahieren
                recommended_stocks=recommendations  # Empfehlungsliste
            )
            st.plotly_chart(cluster_fig_highlighted, use_container_width=True)

            # Bewertungen für die empfohlenen Aktien erfassen
            record_user_ratings(username, recommendations)  

        else:
            st.write("Keine Aktien entsprechen den ausgewählten Kriterien.")
