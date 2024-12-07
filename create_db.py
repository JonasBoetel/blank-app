import yfinance as yf
import csv
import time
import json

def fetch_stock_overview_from_csv_yfinance(csv_file="symbols.csv", json_file_path="stock_overview_yfinance.json"):
    """
    Diese Funktion liest die Symbole aus einer CSV-Datei und ruft für jedes Symbol die Daten
    von der yfinance API ab. Die Ergebnisse werden als JSON gespeichert. Symbole, die bereits
    im JSON vorhanden sind, werden übersprungen.
    """
    stock_data = []

    # Versuchen, die vorhandenen Daten aus der JSON-Datei zu laden, wenn sie existiert
    try:
        with open(json_file_path, "r", encoding="utf-8") as file:
            stock_data = json.load(file)
            # Erstellen eines Sets der Symbole, die bereits im JSON existieren, um Duplikate zu vermeiden
            existing_symbols = {stock["Symbol"] for stock in stock_data}
    except FileNotFoundError:
        # Wenn die Datei nicht existiert, wird ein leerer Satz für vorhandene Symbole verwendet
        existing_symbols = set()

    # Lesen der Symbole aus der CSV-Datei
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        symbols = [row[0] for row in reader][1:]  # Die erste Zeile überspringen (Header)

    # Schleife über alle Symbole
    for count, symbol in enumerate(symbols, 1):
        # Überspringen, wenn das Symbol bereits im JSON vorhanden ist
        if symbol in existing_symbols:
            print(f"Symbol {symbol} bereits vorhanden, wird übersprungen.")
            continue

        print(f"Abfrage für: {symbol}")
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            # Rate limit beachten: 1 Sekunde zwischen den Anfragen
            time.sleep(1)

            # Prüfen, ob die notwendigen Daten vorhanden sind
            if info and "sector" in info and "marketCap" in info and "country" in info:
                print(info)
                market_cap = info.get("marketCap", 0)
                if market_cap < 2_000_000_000:
                    market_cap_category = "Small-Cap"
                elif 2_000_000_000 <= market_cap <= 10_000_000_000:
                    market_cap_category = "Mid-Cap"
                else:
                    market_cap_category = "Large-Cap"

                # Speichern der relevanten Informationen
                stock_data.append({
                    "Symbol": symbol,
                    "Name": info.get("longName", "N/A"),  # Falls der Name nicht verfügbar ist
                    "Country": info.get("country", "N/A"),
                    "Sector": info.get("sector", "N/A"),
                    "MarketCap": market_cap,
                    "MarketCapCategory": market_cap_category
                })

                # Ausgabe der abgerufenen Daten
                print({
                    "Symbol": symbol,
                    "Name": info.get("longName", "N/A"),
                    "Country": info.get("country", "N/A"),
                    "Sector": info.get("sector", "N/A"),
                    "MarketCap": market_cap,
                    "MarketCapCategory": market_cap_category
                })

            else:
                print(f"Fehler bei den Daten für {symbol}. Keine vollständigen Informationen verfügbar.")
        except:
            print(f"Fehler bei den Daten für {symbol}. Keine vollständigen Informationen verfügbar.")
        
        # Speichern der Daten alle 10 Symbole, um große JSON-Dateien zu vermeiden
        if count % 10 == 0:
            with open(json_file_path, "w") as json_file:
                json.dump(stock_data, json_file, indent=4)

    # Endgültiges Speichern der Daten am Ende
    with open(json_file, "w") as json_file:
        json.dump(stock_data, json_file, indent=4)

    print(f"{count} Symbole wurden erfolgreich verarbeitet.")

# Beispielaufruf
# fetch_stock_overview_from_csv_yfinance()
