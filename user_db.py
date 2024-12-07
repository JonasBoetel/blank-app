import json
import streamlit as st


def load_user_data(USER_DB_PATH = "Input/users_data.json"):
    """Lädt die Nutzerdatenbank von der JSON-Datei."""
    try:
        with open(USER_DB_PATH, "r", encoding="utf-8") as file:
            user_data = json.load(file)
    except FileNotFoundError:
        user_data = {}  # Leere Datenbank, wenn keine Datei existiert
    return user_data


def save_user_data(ratings, USER_DB_PATH = "Input/users_data.json"):
    """Speichert die aktualisierten Nutzerdaten in der JSON-Datei und ergänzt bestehende Daten."""
    
    # Versuche, die existierenden Daten zu laden
    try:
        with open(USER_DB_PATH, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = {}

    # Falls der Nutzer schon existiert, ergänze die Bewertungen
    if st.session_state['user'] in existing_data:
        # Ergänze die neuen Bewertungen zu den alten
        existing_data[st.session_state['user']]['ratings'].update(ratings)
    else:
        # Füge den neuen Nutzer hinzu, falls er noch nicht existiert
        existing_data[st.session_state['user']] = {'ratings': ratings}

    # Speichere die kombinierten Daten zurück in die Datei
    with open(USER_DB_PATH, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)
    
    return existing_data
    

def create_or_select_user():
    """Erstellt einen neuen Benutzer oder wählt einen bestehenden aus."""
    user_data = load_user_data()

    st.subheader("Benutzerverwaltung")

    # Benutzername auswählen oder erstellen
    existing_users = list(user_data.keys())
    username = st.selectbox("Wähle deinen Benutzernamen oder erstelle einen neuen:", 
                            ["Neuer Benutzer"] + existing_users)

    if username == "Neuer Benutzer":
        new_username = st.text_input("Gib einen neuen Benutzernamen ein:")
        if new_username:
            st.session_state['user'] = new_username
            username = new_username
            user_data = save_user_data({})
            st.success(f"Benutzer {username} wurde erstellt!")
    
    return username, user_data


def record_user_ratings(username, recommended_stocks):
    """Erfasst die Bewertungen des Nutzers für alle empfohlenen Aktien."""

    # Wenn die Bewertung bereits im session_state gespeichert ist, setzen wir sie wieder
    if "overall_rating" not in st.session_state:
        st.session_state["overall_rating"] = 0  # Standardbewertung 0

    # Erstelle das Formular
    with st.form("rating_form"):
        # Anzeige der Selectbox mit der aktuellen Bewertung im session_state
        overall_rating = st.slider(
            "Setze eine Bewertung für alle empfohlenen Aktien:",
            0, 5, step=1
        )

        # Formular-Submit-Button
        submitted = st.form_submit_button("Bewertungen speichern")

        # Wenn der Button gedrückt wird
        if submitted:
            ratings = {stock["Symbol"]: overall_rating for stock in recommended_stocks}
            save_user_data(ratings)
