import streamlit as st
import pandas as pd
import datetime
import os

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Redline Studio - Dashboard",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DESIGN & STYLE (Weinrot & Gold) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #333333;
    }
    .main-header {
        background-color: #721c24;
        padding: 30px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 {
        color: #d4af37 !important;
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        margin: 0;
    }
    .main-header p {
        color: #f8f9fa;
        font-size: 1.2rem;
        font-style: italic;
        margin-top: 5px;
    }
    .stButton>button {
        background-color: #721c24 !important;
        color: #d4af37 !important;
        border: 2px solid #d4af37 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #d4af37 !important;
        color: #721c24 !important;
        transform: scale(1.02);
    }
    .card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #721c24;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- INITIALISIERUNG DER DATEN-SPEICHER ---
if 'user' not in st.session_state:
    st.session_state.user = None

# Daten für Finanzen und Kunden vorbereiten, falls noch keine da sind
if 'finanzen' not in st.session_state:
    st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
if 'kunden' not in st.session_state:
    st.session_state.kunden = pd.DataFrame(columns=["Kunden-Name", "Telefonnummer", "Notizen"])

# --- STARTSEITE: KUNDEN-LOGIN ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Kreativität & Eleganz</p></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Willkommen im Redline Studio</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic;'>Bitte gib deinen Namen ein, um fortzufahren.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_eingabe = st.text_input("Dein vollständiger Name *", placeholder="Hier eintippen...")
        
        if st.button("Anmelden & Weiter", use_container_width=True):
            if name_eingabe.strip() == "":
                st.error("Bitte gib einen Namen ein.")
            elif name_eingabe.strip().lower() == "admin123":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.session_state.user = name_eingabe.strip()
                st.rerun()

# --- BEREICH: ADMIN-DASHBOARD ---
elif st.session_state.user == "Admin":
    st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Admin-Schaltzentrale</p></div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.write(f"Logged in als: **{st.session_state.user}**")
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    st.success("Erfolgreich als Admin angemeldet!")
    
    # Navigation im Dashboard
    menue = st.tabs(["📊 Einnahmen- & Ausgabenrechner", "👥 Kundenkartei & Kontakte"])
    
    # TAB 1: FINANZEN
    with menue[0]:
        st.subheader("📊 Finanzen verwalten")
        
        col_form, col_view = st.columns([1, 2])
        
        with col_form:
            st.markdown("<div class='card'><h4>Neuen Eintrag hinzufügen</h4></div>", unsafe_allow_html=True)
            f_datum = st.date_input("Datum", datetime.date.today())
            f_typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
            f_kat = st.text_input("Kategorie (z.B. Miete, Material, Maniküre)", placeholder="z.B. Nägel machen")
            f_betrag = st.number_input("Betrag in €", min_value=0.0, step=0.50)
            
            if st.button("Eintrag speichern", use_container_width=True):
                if f_kat == "":
                    st.error("Bitte gib eine Kategorie an.")
                else:
                    neuer_eintrag = pd.DataFrame([[f_datum, f_typ, f_kat, f_betrag]], columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
                    st.session_state.finanzen = pd.concat([st.session_state.finanzen, neuer_eintrag], ignore_index=True)
                    st.success("Finanzdaten aktualisiert!")
                    st.rerun()
        
        with col_view:
            st.markdown("<div class='card'><h4>Übersicht & Statistik</h4></div>", unsafe_allow_html=True)
            
            # Berechnungen
            einnahmen = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Einnahme"]["Betrag (€)"].sum()
            ausgaben = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Ausgabe"]["Betrag (€)"].sum()
            gewinn = einnahmen - ausgaben
            
            col_e, col_a, col_g = st.columns(3)
            col_e.metric("Gesamteinnahmen", f"{einnahmen:.2f} €")
            col_a.metric("Gesamtausgaben", f"{ausgaben:.2f} €")
            col_g.metric("Reingewinn", f"{gewinn:.2f} €")
            
            st.write("---")
            st.dataframe(st.session_state.finanzen, use_container_width=True)
            
            if st.button("Alle Finanzdaten löschen", help="Setzt die Tabelle zurück"):
                st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
                st.rerun()

    # TAB 2: KUNDENKARTEI
    with menue[1]:
        st.subheader("👥 Digitale Kundenkartei")
        
        col_k_form, col_k_view = st.columns([1, 2])
        
        with col_k_form:
            st.markdown("<div class='card'><h4>Neuen Kunden anlegen</h4></div>", unsafe_allow_html=True)
            k_name = st.text_input("Kunden-Name", placeholder="Vor- und Nachname")
            k_tel = st.text_input("Telefonnummer", placeholder="z.B. 0176...")
            k_notiz = st.text_area("Besondere Notizen (Allergien, Wünsche)", placeholder="z.B. Schablone Verlängerung...")
            
            if st.button("Kunde abspeichern", use_container_width=True):
                if k_name == "":
                    st.error("Bitte einen Namen eintragen.")
                else:
                    neuer_kunde = pd.DataFrame([[k_name, k_tel, k_notiz]], columns=["Kunden-Name", "Telefonnummer", "Notizen"])
                    st.session_state.kunden = pd.concat([st.session_state.kunden, neuer_kunde], ignore_index=True)
                    st.success(f"{k_name} wurde registriert!")
                    st.rerun()
                    
        with col_k_view:
            st.markdown("<div class='card'><h4>Gespeicherte Kunden</h4></div>", unsafe_allow_html=True)
            suche = st.text_input("🔍 Kunden suchen...", placeholder="Name eingeben zum Filtern")
            
            if suche:
                gefilterte_kunden = st.session_state.kunden[st.session_state.kunden["Kunden-Name"].str.contains(suche, case=False, na=False)]
                st.dataframe(gefilterte_kunden, use_container_width=True)
            else:
                st.dataframe(st.session_state.kunden, use_container_width=True)

# --- BEREICH: NORMALE KUNDEN-BUCHUNG ---
else:
    st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Terminbuchung</p></div>", unsafe_allow_html=True)
    
    with st.sidebar:
        st.write(f"Willkommen, **{st.session_state.user}**!")
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    st.subheader("🗓️ Wähle deinen Wunschtermin")
    st.write("Hier können deine Kunden bald ihre Termine eintragen.")
