import streamlit as st
from app.user_input_filters import search_stocks
import os


current_dir = os.path.dirname(os.path.abspath(__file__)) # Bestimmt den Pfad zum aktuellen Verzeichnis
logo_path = os.path.join(current_dir, "app","title_img.png") # Pfad zum Logo im Unterordner relativ zum aktuellen Verzeichnis
st.image(logo_path, width=300)  # Bildgrösse

st.title("Aktien Empfehlungen!")
st.write("""
## Optimale Empfehlungen auf Basis deines Portfolios!
... kurze Projektbeschreibung ...
""")
search_stocks()
