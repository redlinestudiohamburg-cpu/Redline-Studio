
Pastebin
API
tools
faq
paste
Login Sign up
SHARE
TWEET
Guest User
Untitled
a guest
May 17th, 2026
2
0
Never
Add comment
Not a member of Pastebin yet? Sign Up, it unlocks many cool features!
4.04 KB | None |

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
        /* Hintergrund und Textfarben */
        .stApp {
            background-color: #ffffff;
            color: #333333;
        }
     
        /* Haupt-Banner oben */
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
     
        /* Buttons */
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
        </style>
    """, unsafe_allow_html=True)
     
    # --- INITIALISIERUNG DES SPEICHERS ---
    if 'user' not in st.session_state:
        st.session_state.user = None
     
    # --- STARTSEITE: KUNDEN-LOGIN ---
    if st.session_state.user is None:
        st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Kreativität & Eleganz</p></div>", unsafe_allow_html=True)
        st.markdown("<h2 style='text-align: center;'>Willkommen im Redline Studio</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; font-style: italic;'>Schön, dass du da bist! Bitte gib deinen Namen ein, um deinen Wunschtermin zu buchen.</p>", unsafe_allow_html=True)
     
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            name_eingabe = st.text_input("Dein vollständiger Name *", placeholder="Hier eintippen...")
     
            # Der reparierte Button, der immer aktiv ist
            if st.button("Anmelden & Weiter zur Buchung", use_container_width=True):
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
     
        # Sidebar für den Logout
        with st.sidebar:
            st.write(f"Logged in als: **{st.session_state.user}**")
            if st.button("Abmelden", use_container_width=True):
                st.session_state.user = None
                st.rerun()
     
        st.success("Erfolgreich als Admin angemeldet!")
        st.subheader("📊 Deine Studio-Übersicht")
     
        # Platzhalter für die Excel-Rechner und Kundenkartei
        col1, col2 = st.columns(2)
        with col1:
            st.info("📂 Einnahmen- & Ausgabenrechner (In Kürze)")
        with col2:
            st.info("👥 Kundenkartei & Termine (In Kürze)")
     
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
     

Advertisement
Add Comment
Please, Sign In to add comment
Public Pastes

    Paladin - Prot/Sunlight
    1 hour ago | 16.25 KB
    Untitled
    1 hour ago | 15.42 KB
    GSA
    2 hours ago | 1.77 KB
    Untitled
    3 hours ago | 12.97 KB
    Untitled
    5 hours ago | 15.90 KB
    Example color scheme with Maroon, yellow and...
    7 hours ago | 12.32 KB
    Untitled
    7 hours ago | 18.50 KB
    Untitled
    9 hours ago | 12.78 KB

create new paste  /  syntax languages  /  archive  /  faq  /  tools  /  night mode  /  api  /  scraping api  /  news  /  pro
privacy statement  /  cookies policy  /  terms of service /  security disclosure  /  dmca  /  report abuse  /  contact

By using Pastebin.com you agree to our cookies policy to enhance your experience.
Site design & logo © 2026 Pastebin
We use cookies for various purposes including analytics. By continuing to use Pastebin, you agree to our use of cookies as described in the Cookies Policy.  OK, I Understand
Not a member of Pastebin yet?
Sign Up, it unlocks many cool features!
 
