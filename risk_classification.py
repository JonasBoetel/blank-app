import json
import yfinance as yf
import time

def update_stock_data_with_additional_metrics(json_file_path="stock_overview_yfinance.json"):
    """
    Ergänzt bestehende JSON-Datenbank mit Beta, Debt-to-Equity und Profit Margins.
    """
    # Vorhandene Daten laden
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            stock_data = json.load(file)
    except FileNotFoundError:
        print("JSON-Datei nicht gefunden. Bitte zuerst die ursprüngliche Datenbank erstellen.")
        return

    # Schleife über alle Einträge in der JSON-Datei
    for index, stock in enumerate(stock_data):
        symbol = stock.get("Symbol")
        if not symbol:
            continue  # Falls kein Symbol vorhanden ist, überspringen

        print(f"Ergänze Daten für: {symbol}")
        try:
            # Abrufen der Daten von Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info

            # Rate Limit beachten
            time.sleep(1)

            # Hinzufügen der neuen Variablen
            stock["Beta"] = info.get("beta", "N/A")
            stock["DebtToEquity"] = info.get("debtToEquity", "N/A")
            stock["ProfitMargins"] = info.get("profitMargins", "N/A")

        except Exception as e:
            print(f"Fehler bei der Abfrage für {symbol}: {e}")
        
        # Zwischenspeichern alle 10 Einträge
        if index % 10 == 0:
            with open(json_file_path, "w", encoding="utf-8") as file:
                json.dump(stock_data, file, indent=4)

    # Endgültiges Speichern
    with open(json_file_path, "w", encoding="utf-8") as file:
        json.dump(stock_data, file, indent=4)

    print("Datenbank erfolgreich ergänzt.")

update_stock_data_with_additional_metrics()