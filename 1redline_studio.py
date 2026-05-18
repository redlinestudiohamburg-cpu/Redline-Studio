import streamlit as st
import pandas as pd
import datetime

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Redline Studio Pro - Dashboard",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🌐 DEIN REINER, QUADRATISCHER LOGO-DIREKTLINK:
LOGO_URL = "https://i.ibb.co/6w2fR6V/1000083367.jpg"

# --- INITIALISIERUNG DER DATEN-SPEICHER ---
if 'user' not in st.session_state: st.session_state.user = None
if 'zeiten_naegel' not in st.session_state:
    st.session_state.zeiten_naegel = {"Neumodellage": 120, "Auffüllen": 90, "French / Extra Design": 45}
if 'puffer_zeit' not in st.session_state: st.session_state.puffer_zeit = 20

# 📢 Speicher für das Schwarze Brett (Studio-News)
if 'studio_news' not in st.session_state:
    st.session_state.studio_news = "✨ Willkommen im Redline Studio! Ab sofort über 20 neue Chrome-Pigmente verfügbar! ✨"
if 'news_aktiv' not in st.session_state:
    st.session_state.news_aktiv = True

# 🗃️ ERWEITERTES DYNAMISCHES LAGER (Mengen werden intern einheitlich in ml/Stk. verwaltet)
if 'lager_bestand' not in st.session_state:
    st.session_state.lager_bestand = {
        "Nagelfeilen": {"aktuell": 20.0, "limit": 5.0, "einheit": "Stk.", "auto_abzug": True, "verbrauch_pro_kunde": 1.0},
        "Primer": {"aktuell": 50.0, "limit": 10.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 0.5},
        "Top Coat": {"aktuell": 100.0, "limit": 15.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 1.5},
        "Cleaner": {"aktuell": 1000.0, "limit": 200.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 15.0}
    }

# 🛒 SPEICHER FÜR MATERIAL-KATALOG & PREISVERGLEICH
if 'material_katalog' not in st.session_state:
    st.session_state.material_katalog = []

# 📋 DATENSCHUTZ & ANAMNESE FORMULAR-VORLAGEN
if 'anamnese_vorlage' not in st.session_state:
    st.session_state.anamnese_vorlage = (
        "1. Haben Sie bekannte Allergien (z.B. gegen Acrylate, Gele, Klebstoffe)?\n"
        "2. Liegen Nagelerkrankungen vor (z.B. Nagelpilz, Nagelablösung)?\n"
        "3. Nehmen Sie Medikamente (z.B. Cortison, Blutverdünner)?\n"
        "4. Besteht eine Schwangerschaft oder Diabetes?"
    )
if 'datenschutz_vorlage' not in st.session_state:
    st.session_state.datenschutz_vorlage = (
        "Einwilligungserklärung nach DSGVO:\n"
        "Ich willige ein, dass Redline Studio meine personenbezogenen Daten, Fotos der Modellagen "
        "sowie Behandlungsnotizen zum Zweck der Kundenbetreuung elektronisch speichert. "
        "Die Daten werden vertraulich behandelt und niemals an Dritte weitergegeben."
    )

# Premium Kundenstruktur
if 'kunden_liste' not in st.session_state:
    st.session_state.kunden_liste = {
        "Beispiel Kundin": {
            "Telefon": "+49 123 456789", "Farbe": "#721c24", 
            "Kaffee": "Cappuccino mit Hafermilch", "Allergien": "Keine", "Notizen": "Bevorzugt mattes Finish", 
            "Anamnese_Text": "Keine Auffälligkeiten", "DSGVO_Akzeptiert": True, "Fotos": []
        }
    }

if 'freie_slots' not in st.session_state: 
    st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
if 'termine' not in st.session_state: 
    st.session_state.termine = pd.DataFrame(columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe"])

# FEHLERBEHEBUNG FINANZEN: Absolut sauberer Start bei 0,00 € ohne Geister-Einträge
if 'finanzen' not in st.session_state: 
    st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])

# --- DESIGN & STYLE (Weinrot & Gold Luxe Edition) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #333333;
    }
    .main-header {
        background-color: #721c24;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 25px;
    }
    .main-header h1 {
        color: #d4af37 !important;
        font-family: 'Playfair Display', serif;
        font-size: 3.2rem;
        margin: 0;
    }
    .main-header p {
        color: #f8f9fa;
        font-size: 1.3rem;
        font-style: italic;
        margin-top: 5px;
    }
    .main-logo-img {
        max-height: 100px;
        border-radius: 12px;
        border: 2px solid #d4af37;
    }
    .news-banner {
        background-color: #721c24;
        color: #d4af37;
        border: 2px solid #d4af37;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .material-alert {
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeeba;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
        margin-bottom: 10px;
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
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .kunden-akte {
        background-color: #fffdf9;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #d4af37;
        margin-top: 15px;
    }
    .calendar-box {
        border: 1px solid #721c24;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: white;
    }
    .pdf-frame {
        border: 2px solid #721c24;
        padding: 25px;
        background-color: white;
        color: black;
        font-family: 'Courier New', monospace;
    }
    .vergleichs-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# --- FEIERTAGE-BERECHNER ---
def get_feiertag(datum):
    jahr = datum.year
    feste = {
        (1, 1): "Neujahr", (6, 1): "Heilige Drei Könige", (1, 5): "Tag der Arbeit",
        (1, 8): "Schweizer Nationalfeiertag", (3, 10): "Tag der Deutschen Einheit",
        (26, 10): "Nationalfeiertag (AT)", (1, 11): "Allerheiligen",
        (25, 12): "1. Weihnachtstag", (26, 12): "2. Weihnachtstag"
    }
    a, b, c = jahr % 19, jahr % 4, jahr % 7
    d = (19 * a + 24) % 30
    e = (2 * b + 4 * c + 6 * d + 5) % 7
    oster_tage = 22 + d + e
    oster_datum = datetime.date(jahr, 4, oster_tage - 31) if oster_tage > 31 else datetime.date(jahr, 3, oster_tage)
    
    if datum == oster_datum - datetime.timedelta(days=2): return "Karfreitag"
    if datum == oster_datum: return "Ostersonntag"
    if datum == oster_datum + datetime.timedelta(days=1): return "Ostermonntag"
    if datum == oster_datum + datetime.timedelta(days=39): return "Auffahrt / Himmelfahrt"
    if datum == oster_datum + datetime.timedelta(days=50): return "Pfingstmontag"
    if (datum.day, datum.month) in feste: return feste[(datum.day, datum.month)]
    return None

def show_logo_and_header():
    st.markdown(f"""
        <div class='main-header'>
            <img src='{LOGO_URL}' class='main-logo-img' onerror="this.style.display='none'">
            <div>
                <h1>Redline Studio</h1>
                <p>Kreativität & Eleganz</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.news_aktiv and st.session_state.studio_news:
        st.markdown(f"<div class='news-banner'>📢 {st.session_state.studio_news}</div>", unsafe_allow_html=True)

# --- STARTSEITE: KUNDEN-LOGIN ---
if st.session_state.user is None:
    show_logo_and_header()
    st.markdown("<h2 style='text-align: center;'>Willkommen im Redline Studio</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_eingabe = st.text_input("Dein vollständiger Name *", placeholder="Hier eintippen...")
        if st.button("Anmelden & Weiter zur Buchung", use_container_width=True):
            if name_eingabe.strip() == "":
                st.error("Bitte gib einen Namen ein.")
            elif name_eingabe.strip().lower() == "admin123":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.session_state.user = name_eingabe.strip()
                if st.session_state.user not in st.session_state.kunden_liste:
                    st.session_state.kunden_liste[st.session_state.user] = {
                        "Telefon": "", "Farbe": "#721c24", "Kaffee": "Noch unbekannt", "Allergien": "Keine", "Notizen": "",
                        "Anamnese_Text": "", "DSGVO_Akzeptiert": False, "Fotos": []
                    }
                st.rerun()

# --- BEREICH: ADMIN-DASHBOARD ---
elif st.session_state.user == "Admin":
    show_logo_and_header()
    
    # Globaler intelligenter Material-Warner
    for produkt, daten in st.session_state.lager_bestand.items():
        if daten["aktuell"] <= daten["limit"]:
            st.markdown(f"""
                <div class='material-alert'>
                    ⚠️ MATERIAL-WARNUNG: <strong>{produkt}</strong> neigt sich dem Ende! Vorrat: {daten['aktuell']} {daten['einheit']} (Limit: ab {daten['limit']} {daten['einheit']}).
                </div>
            """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.write(f"💼 Modus: **{st.session_state.user}**")
        st.write("---")
        heute_str = datetime.date.today().strftime('%Y-%m-%d')
        termine_heute = len(st.session_state.termine[st.session_state.termine["Datum"] == heute_str]) if not st.session_state.termine.empty else 0
        st.metric(label="Termine heute", value=termine_heute)
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    menue = st.tabs([
        "🗓️ Kalender & Slots", 
        "👥 Digitale Luxus-Kartei", 
        "📝 Datenschutz & Anamnese-Editor", 
        "📢 Schwarzes Brett & Lager", 
        "🛒 Material-Einkauf & Vergleich", # DER NEUE REITER!
        "📄 Dokumente & Quittungen", 
        "📊 Finanzen & Bunte Diagramme"
    ])
    
    # TAB 1: KALENDER & ARBEITSZEITEN
    with menue[0]:
        st.subheader("🗓️ Arbeitszeiten & Kalenderübersicht")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            st.markdown("<div class='card'><h4>⏱️ Zeiteinstellungen & Puffer</h4></div>", unsafe_allow_html=True)
            st.session_state.puffer_zeit = st.number_input("Hygiene-Pufferzeit zwischen Kunden (Minuten)", value=st.session_state.puffer_zeit, step=5)
            
            st.write("---")
            st.markdown("<h4>Slot freigeben</h4>")
            slot_datum = st.date_input("Datum wählen", datetime.date.today(), key="admin_slot_d")
            feiertag_name = get_feiertag(slot_datum)
            hinweis_text = "-"
            if feiertag_name:
                st.markdown(f"<span class='holiday-text'>ℹ️ Hinweis: An diesem Tag ist {feiertag_name}.</span>", unsafe_allow_html=True)
                hinweis_text = feiertag_name
                
            start_zeit = st.time_input("Von", datetime.time(14, 0))
            end_zeit = st.time_input("Bis", datetime.time(17, 0))
            
            if st.button("Zeitraum freistellen", use_container_width=True):
                dauer = (datetime.datetime.combine(slot_datum, end_zeit) - datetime.datetime.combine(slot_datum, start_zeit)).seconds // 60
                if dauer <= 0:
                    st.error("Die Endzeit muss nach der Startzeit liegen!")
                else:
                    neuer_slot = pd.DataFrame([[slot_datum.strftime('%Y-%m-%d'), start_zeit.strftime('%H:%M'), end_zeit.strftime('%H:%M'), dauer, hinweis_text, "Frei"]], 
                                              columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                    st.session_state.freie_slots = pd.concat([st.session_state.freie_slots, neuer_slot], ignore_index=True)
                    st.success("Erfolgreich eingetragen!")
                    st.rerun()
            
            st.write("---")
            st.dataframe(st.session_state.freie_slots, use_container_width=True)
            if st.button("Alle Slots löschen / zurücksetzen"):
                st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                st.rerun()
                    
        with col_s2:
            st.markdown("<div class='card'><h4>🔮 Visueller Terminkalender</h4></div>", unsafe_allow_html=True)
            view_mode = st.radio("Ansichtsmodus:", ["Monat", "Tag"], horizontal=True)
            wahl_datum = st.date_input("Kalender-Fokus auf:", datetime.date.today(), key="cal_focus")
            
            if not st.session_state.termine.empty:
                st.session_state.termine["Datum_Parsed"] = pd.to_datetime(st.session_state.termine["Datum"]).dt.date
                if view_mode == "Tag":
                    aktuelle_termine = st.session_state.termine[st.session_state.termine["Datum_Parsed"] == wahl_datum]
                else:
                    aktuelle_termine = st.session_state.termine[(pd.to_datetime(st.session_state.termine["Datum"]).dt.month == wahl_datum.month) & (pd.to_datetime(st.session_state.termine["Datum"]).dt.year == wahl_datum.year)]
            else:
                aktuelle_termine = pd.DataFrame()
                
            if aktuelle_termine.empty:
                st.info("Keine Termine für diesen Zeitraum gebucht.")
            else:
                for _, t in aktuelle_termine.iterrows():
                    bg_color = t['Farbe'] if 'Farbe' in t and t['Farbe'] else "#721c24"
                    st.markdown(f"""
                        <div class='calendar-box' style='background-color: {bg_color};'>
                            <strong>📅 {t['Datum']} | ⏰ {t['Uhrzeit']} Uhr</strong><br>
                            👤 Kunde: {t['Kunde']} <br>
                            💅 Behandlung: {t['Typ']} ({t['Dauer_Gesamt']} Min. inkl. Puffer)
                        </div>
                    """, unsafe_allow_html=True)

    # TAB 2: DIGITALE LUXUS-KARTEI
    with menue[1]:
        st.subheader("👥 Redline Premium Kundenkartei")
        col_k_liste, col_k_akte = st.columns([1, 2])
        
        with col_k_liste:
            ausgewaehlter_kunde = st.selectbox("Kunden-Akte öffnen:", list(st.session_state.kunden_liste.keys()))
            st.write("---")
            st.markdown("<h4>👤 Neue Kundin manuell anlegen</h4>")
            n_name = st.text_input("Name der Kundin")
            if st.button("Kundin in Kartei aufnehmen", use_container_width=True):
                if n_name and n_name not in st.session_state.kunden_liste:
                    st.session_state.kunden_liste[n_name.strip()] = {
                        "Telefon": "", "Farbe": "#721c24", "Kaffee": "", "Allergien": "", "Notizen": "", 
                        "Anamnese_Text": "", "DSGVO_Akzeptiert": False, "Fotos": []
                    }
                    st.success("Kundin angelegt!")
                    st.rerun()
                    
        with col_k_akte:
            if ausgewaehlter_kunde:
                akte = st.session_state.kunden_liste[ausgewaehlter_kunde]
                st.markdown(f"<div class='kunden-akte'><h3>👑 VIP Akte: {ausgewaehlter_kunde}</h3>", unsafe_allow_html=True)
                akte["Telefon"] = st.text_input("📞 Telefonnummer:", akte["Telefon"], key=f"tel_{ausgewaehlter_kunde}")
                akte["Kaffee"] = st.text_input("☕ Kaffee- / Getränkevorliebe:", akte["Kaffee"], key=f"kaf_{ausgewaehlter_kunde}")
                akte["Allergien"] = st.text_input("⚠️ Allergien / Empfindlichkeiten:", akte["Allergien"], key=f"all_{ausgewaehlter_kunde}")
                akte["Notizen"] = st.text_area("📝 Besondere Design-Wünsche & Notizen:", akte["Notizen"], key=f"not_{ausgewaehlter_kunde}")
                
                st.write("---")
                akte["Anamnese_Text"] = st.text_area("Medizinischer Befund / Anamnese Notiz:", akte["Anamnese_Text"], key=f"anam_k_{ausgewaehlter_kunde}")
                akte["DSGVO_Akzeptiert"] = st.checkbox("Datenschutzerklärung (DSGVO) liegt unterschrieben vor", value=akte["DSGVO_Akzeptiert"], key=f"dsgvo_k_{ausgewaehlter_kunde}")
                akte["Farbe"] = st.color_picker("🎨 Eigene Kalender-Farbe für diese Kundin:", akte["Farbe"], key=f"col_{ausgewaehlter_kunde}")
                
                st.write("---")
                st.markdown("<h4>🖼️ Foto-Galerie (Modellagen)</h4>", unsafe_allow_html=True)
                hochgeladenes_foto = st.file_uploader("Neues Foto hochladen:", type=["jpg", "png", "jpeg"], key=f"img_{ausgewaehlter_kunde}")
                if hochgeladenes_foto:
                    if st.button("Foto in Akte speichern", key=f"save_img_{ausgewaehlter_kunde}"):
                        akte["Fotos"].append(hochgeladenes_foto)
                        st.success("Bild hinzugefügt!")
                        st.rerun()
                
                if akte["Fotos"]:
                    cols_img = st.columns(3)
                    for idx, img in enumerate(akte["Fotos"]):
                        cols_img[idx % 3].image(img, use_container_width=True, caption=f"Modellage {idx+1}")
                st.markdown("</div>", unsafe_allow_html=True)

    # TAB 3: DATENSCHUTZ- & ANAMNESE-VORLAGEN-EDITOR
    with menue[2]:
        st.subheader("📝 Zentrale Formular-Verwaltung")
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            st.markdown("<div class='card'><h4>📋 Medizinischer Anamnesebogen (Vorlage)</h4></div>", unsafe_allow_html=True)
            neue_anamnese_v = st.text_area("Fragenkatalog bearbeiten:", value=st.session_state.anamnese_vorlage, height=200)
        with col_form2:
            st.markdown("<div class='card'><h4>⚖️ Datenschutzerklärung / DSGVO (Vorlage)</h4></div>", unsafe_allow_html=True)
            neue_dsgvo_v = st.text_area("Rechtstext bearbeiten:", value=st.session_state.datenschutz_vorlage, height=200)
            
        if st.button("✨ Formular-Vorlagen studio-weit aktualisieren"):
            st.session_state.anamnese_vorlage = neue_anamnese_v
            st.session_state.datenschutz_vorlage = neue_dsgvo_v
            st.success("Die Dokumenten-Vorlagen wurden erfolgreich live aktualisiert!")

    # TAB 4: SCHWARZES BRETT & INTELLIGENTES LAGER (Mit flexibler Liter/ml Wahl!)
    with menue[3]:
        st.subheader("📢 Studio-Management & Flexibles Verbrauchslager")
        col_board, col_lager = st.columns([1, 1])
        
        with col_board:
            st.markdown("<div class='card'><h4>📢 Digitales Schwarzes Brett konfigurieren</h4></div>", unsafe_allow_html=True)
            st.session_state.news_aktiv = st.checkbox("Schwarzes Brett für Kunden sichtbar schalten", value=st.session_state.news_aktiv)
            st.session_state.studio_news = st.text_area("Aushang-Text:", value=st.session_state.studio_news)
            if st.button("Aushang aktualisieren"):
                st.success("Das Schwarze Brett wurde live aktualisiert!")
                st.rerun()
                
            st.write("---")
            st.markdown("<h4>➕ Neues Produkt ins Lager aufnehmen</h4>")
            neu_prod = st.text_input("Produktname", placeholder="z.B. Cleaner Premium")
            
            # 🌟 NEU: Einzelne Wahl zwischen Liter und ml bei der Lageraufnahme!
            c_menge, c_einheit = st.columns([2, 1])
            eingabe_menge = c_menge.number_input("Menge/Inhalt:", min_value=0.0, value=1.0, step=0.5)
            gewaehlte_einheit = c_einheit.selectbox("Einheit:", ["ml", "l (Liter)", "Stk."])
            
            # Automatische Umrechnung in Milliliter im Hintergrund, falls Liter gewählt wird
            if "l (Liter)" in gewaehlte_einheit:
                berechnete_menge = eingabe_menge * 1000.0
                speicher_einheit = "ml"
            else:
                berechnete_menge = eingabe_menge
                speicher_einheit = gewaehlte_einheit
                
            neu_lim = st.number_input("Warnen ab (Mindestlimit)", min_value=0.0, value=15.0)
            neu_auto = st.checkbox("Soll automatisch bei Kundenbuchung verbraucht werden?", value=True)
            neu_menge = st.number_input(f"Verbrauch pro Kunde (ca. in {speicher_einheit})", min_value=0.0, value=1.5)
            
            if st.button("Produkt ins System aufnehmen"):
                if neu_prod:
                    st.session_state.lager_bestand[neu_prod] = {
                        "aktuell": berechnete_menge, "limit": neu_lim, "einheit": speicher_einheit, 
                        "auto_abzug": neu_auto, "verbrauch_pro_kunde": neu_menge
                    }
                    st.success(f"'{neu_prod}' wurde erfolgreich mit {berechnete_menge} ml/Stk. registriert!")
                    st.rerun()
                
        with col_lager:
            st.markdown("<div class='card'><h4>📦 Lagerbestände & Genaue Verbrauchswerte</h4></div>", unsafe_allow_html=True)
            for prod, daten in list(st.session_state.lager_bestand.items()):
                st.write(f"##### 🏷️ {prod} ({daten['einheit']})")
                c1, c2, c3 = st.columns(3)
                
                st.session_state.lager_bestand[prod]["aktuell"] = c1.number_input(f"Ist-Vorrat##{prod}", min_value=0.0, value=float(daten["aktuell"]), key=f"ist_{prod}")
                st.session_state.lager_bestand[prod]["limit"] = c2.number_input(f"Warn-Limit##{prod}", min_value=0.0, value=float(daten["limit"]), key=f"lim_{prod}")
                st.session_state.lager_bestand[prod]["verbrauch_pro_kunde"] = c3.number_input(f"Verbrauch/Kunde##{prod}", min_value=0.0, value=float(daten["verbrauch_pro_kunde"]), key=f"vpr_{prod}")
                
                if c1.button(f"Aufstocken (+100 / +10)##{prod}"):
                    st.session_state.lager_bestand[prod]["aktuell"] += 100 if daten["einheit"] == "ml" else 10
                    st.rerun()
                st.write("---")

    # TAB 5: 🛒 MATERIAL-EINKAUF-FAVORITEN & WEBSEITEN-PREISVERGLEICH (Der brandneue Wunsch-Tab!)
    with menue[4]:
        st.subheader("🛒 Material-Katalog mit Foto-Upload & Live-Preisvergleich")
        
        col_cat1, col_cat2 = st.columns([1, 2])
        
        with col_cat1:
            st.markdown("<div class='card'><h4>📸 Lieblingsmaterial hinzufügen</h4></div>", unsafe_allow_html=True)
            mat_name = st.text_input("Name des Materials:", placeholder="z.B. Jolifin Farbgel Diamond Rose")
            mat_preis = st.number_input("Standard-Richtpreis (€):", min_value=0.0, value=9.95, step=0.5)
            mat_notiz = st.text_area("Besondere Notizen / Marke / Code:")
            
            # Foto-Upload direkt über den Datei-Button wie bei den Modellagen!
            mat_foto = st.file_uploader("Produkt-Foto hochladen:", type=["jpg", "png", "jpeg"], key="mat_foto_upload")
            
            if st.button("Material im Katalog speichern", use_container_width=True):
                if mat_name:
                    st.session_state.material_katalog.append({
                        "Name": mat_name, "Preis": mat_preis, "Notiz": mat_notiz, "Foto": mat_foto
                    })
                    st.success(f"'{mat_name}' wurde in deinen Favoriten gespeichert!")
                    st.rerun()
                    
        with col_cat2:
            st.markdown("<div class='card'><h4>🔍 Deine Material-Favoriten</h4></div>", unsafe_allow_html=True)
            if not st.session_state.material_katalog:
                st.info("Dein Material-Katalog ist noch leer. Füge links Produkte hinzu!")
            else:
                for idx, item in enumerate(st.session_state.material_katalog):
                    c_box1, c_box2 = st.columns([1, 3])
                    with c_box1:
                        if item["Foto"] is not None:
                            st.image(item["Foto"], use_container_width=True)
                        else:
                            st.write("🧱 *Kein Bild*")
                    with c_box2:
                        st.write(f"##### **{item['Name']}**")
                        st.write(f"💰 **Standardpreis:** {item['Preis']:.2f} € | *{item['Notiz']}*")
                        if st.button(f"Löschen##{idx}", key=f"del_mat_{idx}"):
                            st.session_state.material_katalog.pop(idx)
                            st.rerun()
                    st.write("---")
                    
        st.write("---")
        st.markdown("### 🌐 Live-Einkaufs-Matrix & Webseiten-Preisvergleich")
        st.write("Vergleiche hier zeitgleich bis zu 4 deiner gängigsten Shopping-Seiten für den Studioeinkauf:")
        
        # 4 Spalten für den direkten Vergleich nebeneinander
        w1, w2, w3, w4 = st.columns(4)
        
        with w1:
            st.markdown("<div class='vergleichs-box'><h4>🛍️ Shop 1: Jolifin</h4>", unsafe_allow_html=True)
            st.markdown("[👉 Jolifin Shop öffnen](https://www.jolifin.de)")
            st.number_input("Aktueller Warenkorb-Preis (€):", min_value=0.0, step=1.0, key="p_shop1")
            st.text_area("Angebote / Rabattcodes:", placeholder="z.B. 10% mit CODE10", key="n_shop1")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with w2:
            st.markdown("<div class='vergleichs-box'><h4>🛍️ Shop 2: NeoNail</h4>", unsafe_allow_html=True)
            st.markdown("[👉 NeoNail Shop öffnen](https://www.neonail.de)")
            st.number_input("Aktueller Warenkorb-Preis (€):", min_value=0.0, step=1.0, key="p_shop2")
            st.text_area("Angebote / Rabattcodes:", placeholder="z.B. Gratis Versand", key="n_shop2")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with w3:
            st.markdown("<div class='vergleichs-box'><h4>🛍️ Shop 3: LyniNails</h4>", unsafe_allow_html=True)
            st.markdown("[👉 LyniNails Shop öffnen](https://www.lyni-nails.de)")
            st.number_input("Aktueller Warenkorb-Preis (€):", min_value=0.0, step=1.0, key="p_shop3")
            st.text_area("Angebote / Rabattcodes:", placeholder="Aktion beachten", key="n_shop3")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with w4:
            st.markdown("<div class='vergleichs-box'><h4>🛍️ Shop 4: Amazon / Sonstige</h4>", unsafe_allow_html=True)
            st.markdown("[👉 Alternativ-Shop öffnen](https://www.amazon.de)")
            st.number_input("Aktueller Warenkorb-Preis (€):", min_value=0.0, step=1.0, key="p_shop4")
            st.text_area("Angebote / Rabattcodes:", placeholder="Prime-Vorteile?", key="n_shop4")
            st.markdown("</div>", unsafe_allow_html=True)

    # TAB 6: DOKUMENTE & QUITTUNGEN
    with menue[5]:
        st.subheader("📄 Professionelle Dokumente erstellen")
        col_pdf_f, col_pdf_v = st.columns([1, 2])
        with col_pdf_f:
            st.markdown("<div class='card'><h4>Dokumenten-Konfigurator</h4></div>", unsafe_allow_html=True)
            doc_kunde = st.selectbox("Wähle einen Kunden:", list(st.session_state.kunden_liste.keys()), key="doc_k")
            doc_art = st.selectbox("Behandlung:", list(st.session_state.zeiten_naegel.keys()), key="doc_a")
            doc_datum = st.date_input("Datum", datetime.date.today(), key="doc_d")
            doc_preis = st.number_input("Beitrag in €", min_value=0.0, step=0.5)
            doc_typ = st.radio("Dokumententyp:", ["Professionelle Quittung", "Einverständniserklärung"], horizontal=True)
            
            if st.button("Dokument generieren", use_container_width=True):
                logo_html = f"<img src='{LOGO_URL}' style='max-height: 60px; float: right; border-radius: 8px;' onerror='this.style.display=\"none\"'>"
                if doc_typ == "Professionelle Quittung":
                    st.session_state.pdf_view = f"""
                        <div class='pdf-frame'>
                            {logo_html}
                            <h1 style='color: #721c24; margin:0;'>Redline Studio</h1>
                            <hr>
                            <h2 style='text-align: center;'>QUITTUNG / RECHNUNG</h2>
                            <p><strong>Datum:</strong> {doc_datum.strftime('%d.%m.%Y')}</p>
                            <p><strong>Kunde:</strong> {doc_kunde}</p>
                            <p><strong>Leistung:</strong> {doc_art}</p>
                            <h3 style='text-align: right; border-top: 2px solid #333; padding-top:10px;'>Gesamtbetrag erhalten: {doc_preis:.2f} €</h3>
                            <p style='font-style: italic; font-size: 0.9em; margin-top:30px;'>Vielen Dank für deinen Besuch!<br>Es gilt die Kleinunternehmerregelung (§ 19 UStG).</p>
                        </div>
                    """
                else:
                    st.session_state.pdf_view = f"""
                        <div class='pdf-frame'>
                            {logo_html}
                            <h1 style='color: #721c24; margin:0;'>Redline Studio</h1>
                            <hr>
                            <h2 style='text-align: center;'>Einverständniserklärung & Protokoll</h2>
                            <p><strong>Datum:</strong> {doc_datum.strftime('%d.%m.%Y')}</p>
                            <p><strong>Kunde:</strong> {doc_kunde}</p>
                            <p><strong>Behandlung:</strong> {doc_art}</p>
                            <p style='margin-top:20px;'>Ich wurde über die Behandlung, Risiken und die Nachpflege aufgeklärt und stimme zu.</p>
                            <br><br>
                            <div style='display: flex; justify-content: space-between; margin-top:40px;'>
                                <div>_____________________<br><span style='font-size: 0.8em;'>Unterschrift Kunde</span></div>
                                <div>_____________________<br><span style='font-size: 0.8em;'>Unterschrift Studio</span></div>
                            </div>
                        </div>
                    """
                st.rerun()
        with col_pdf_v:
            if 'pdf_view' in st.session_state: st.markdown(st.session_state.pdf_view, unsafe_allow_html=True)

    # TAB 7: FINANZEN & BUNTE DIAGRAMME
    with menue[6]:
        st.subheader("📊 Studio-Finanzen & Bunte Live-Diagramme")
        if not st.session_state.finanzen.empty:
            einnahmen = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Einnahme"]["Betrag (€)"].sum()
            ausgaben = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Ausgabe"]["Betrag (€)"].sum()
            gewinn = einnahmen - ausgaben
        else:
            einnahmen, ausgaben, gewinn = 0.0, 0.0, 0.0
            
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Gesamteinnahmen", f"{einnahmen:.2f} €")
        c_m2.metric("Gesamtausgaben", f"{ausgaben:.2f} €")
        c_m3.metric("Reingewinn / Verlust", f"{gewinn:.2f} €")
        
        st.write("---")
        col_f1, col_f2 = st.columns([1, 1])
        
        with col_f1:
            st.markdown("<h4>Transaktion buchen</h4>", unsafe_allow_html=True)
            f_datum = st.date_input("Datum", datetime.date.today(), key="fin_d")
            f_typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
            f_kat = st.selectbox("Kategorie", ["Neumodellage", "Auffüllen", "Design-Extra", "Materialeinkauf", "Miete/Strom", "Sonstiges"])
            f_betrag = st.number_input("Betrag in €", min_value=0.0, step=5.0)
            
            if st.button("Eintrag Speichern"):
                neuer_eintrag = pd.DataFrame([[f_datum.strftime('%Y-%m-%d'), f_typ, f_kat, f_betrag]], columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
                st.session_state.finanzen = pd.concat([st.session_state.finanzen, neuer_eintrag], ignore_index=True)
                st.rerun()
        
        with col_f2:
            st.markdown("<h4>📈 Visualisierte Umsatz-Auswertungen</h4>", unsafe_allow_html=True)
            if not st.session_state.finanzen.empty:
                st.write("**Gegenüberstellung (Einnahmen vs. Ausgaben):**")
                st.bar_chart(data=st.session_state.finanzen, x="Typ", y="Betrag (€)", color="Typ", use_container_width=True)
                
                einnahmen_df = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Einnahme"]
                if not einnahmen_df.empty:
                    st.write("**Umsatzquellen nach Kategorie:**")
                    st.bar_chart(data=einnahmen_df, x="Kategorie", y="Betrag (€)", color="Kategorie", use_container_width=True)
            else:
                st.info("Sobald ihr Einnahmen oder Ausgaben eintragt, erscheinen hier die bunten Diagramme automatisch!")

# --- SEITE: KUNDEN-BUCHUNG ---
else:
    show_logo_and_header()
    with st.sidebar:
        st.write(f"🌸 Kundin: **{st.session_state.user}**")
        st.write("---")
        if st.session_state.user in st.session_state.kunden_liste:
            k_info = st.session_state.kunden_liste[st.session_state.user]
            st.write(f"☕ Dein Wunschgetränk:  \n*{k_info['Kaffee']}*")
        if st.button("Abmelden"):
            st.session_state.user = None
            st.rerun()
            
    st.subheader("🗓️ Wähle deinen Wunschtermin")
    nagel_wunsch = st.selectbox("Was möchtest du machen lassen?", list(st.session_state.zeiten_naegel.keys()))
    benoetigte_zeit = st.session_state.zeiten_naegel[nagel_wunsch]
    gesamte_blockade_zeit = benoetigte_zeit + st.session_state.puffer_zeit
    
    st.info(f"Für {nagel_wunsch} werden {benoetigte_zeit} Minuten pure Wellness eingeplant.")
    
    if "freie_slots" in st.session_state and not st.session_state.freie_slots.empty:
        freie_anzeige = st.session_state.freie_slots[st.session_state.freie_slots["Status"] == "Frei"]
    else:
        freie_anzeige = pd.DataFrame()
        
    if freie_anzeige.empty:
        st.warning("Aktuell sind leider keine freien Termine freigeschaltet. Bitte schaue später noch einmal vorbei!")
    else:
        for idx, row in freie_anzeige.iterrows():
            verfuegbare_minuten = int(row["Dauer_Minuten"])
            if verfuegbare_minuten >= gesamte_blockade_zeit:
                col_slot, col_buch_btn = st.columns([3, 1])
                col_slot.write(f"📅 **{row['Datum']}** | ⏰ Von {row['Startzeit']} bis {row['Endzeit']} Uhr")
                if col_buch_btn.button("Jetzt buchen", key=f"book_{idx}"):
                    st.session_state.freie_slots.at[idx, "Status"] = "Gebucht"
                    
                    # Bestandsabzug basierend auf den eingestellten ml / Stk. Werten im Lager
                    for prod, daten in st.session_state.lager_bestand.items():
                        if daten["auto_abzug"] and daten["aktuell"] > 0:
                            st.session_state.lager_bestand[prod]["aktuell"] = max(0.0, daten["aktuell"] - daten["verbrauch_pro_kunde"])
                    
                    kunden_farbe = "#721c24"
                    if st.session_state.user in st.session_state.kunden_liste:
                        kunden_farbe = st.session_state.kunden_liste[st.session_state.user]["Farbe"]
                    
                    neuer_termin = pd.DataFrame([[row['Datum'], row['Startzeit'], st.session_state.user, nagel_wunsch, gesamte_blockade_zeit, kunden_farbe]], 
                                                columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe"])
                    st.session_state.termine = pd.concat([st.session_state.termine, neuer_termin], ignore_index=True)
                    st.success("Erfolgreich gebucht! Wir freuen uns auf dich! 🎉")
                    st.rerun()
                    
