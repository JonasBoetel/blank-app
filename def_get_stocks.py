import requests
import csv
import os

def fetch_and_save_symbols(api_key, file_path="symbols.csv"):
    """
    Diese Funktion ruft alle Symbole von Alpha Vantage ab und speichert sie in einer CSV-Datei.
    """
    url = f"https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={api_key}"
    
    # Sendet eine Anfrage an Alpha Vantage
    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Fehler beim Abrufen der Daten von Alpha Vantage: {response.status_code}")

    # CSV-Inhalt dekodieren
    decoded_content = response.content.decode('utf-8')
    csv_reader = csv.reader(decoded_content.splitlines(), delimiter=',')

    # Die erste Zeile überspringen (Header)
    stock_data = [row for idx, row in enumerate(csv_reader) if idx > 0 and row[3].lower() == "stock"]

    # Speichern der Daten in einer CSV-Datei
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Schreibe die Header
        writer.writerow(['Symbol', 'Name', 'Exchange', 'Type', 'Date', 'Status'])
        # Schreibe die Stock-Daten
        for row in stock_data:
            writer.writerow([row[0], row[1], row[2], row[3], row[4], row[6]])

    print(f"Die Symbol-Liste wurde erfolgreich in '{file_path}' gespeichert.")

# Beispielaufruf
fetch_and_save_symbols("demo")
