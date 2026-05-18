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
if 'neukunden_extra_zeit' not in st.session_state: st.session_state.neukunden_extra_zeit = 30  # ⏱️ Extra-Zeit für Neukunden

# 📢 Speicher für das Schwarze Brett (Studio-News)
if 'studio_news' not in st.session_state:
    st.session_state.studio_news = "✨ Willkommen im Redline Studio! Ab sofort über 20 neue Chrome-Pigmente verfügbar! ✨"
if 'news_aktiv' not in st.session_state:
    st.session_state.news_aktiv = True

# 🗃️ ERWEITERTES DYNAMISCHES LAGER (Mit Einkaufspreis pro Einheit für die genaue Quittung)
if 'lager_bestand' not in st.session_state:
    st.session_state.lager_bestand = {
        "Nagelfeilen": {"aktuell": 20.0, "limit": 5.0, "einheit": "Stk.", "auto_abzug": True, "verbrauch_pro_kunde": 1.0, "kosten_pro_einheit": 1.20},
        "Primer": {"aktuell": 50.0, "limit": 10.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 0.5, "kosten_pro_einheit": 0.30},
        "Top Coat": {"aktuell": 100.0, "limit": 15.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 1.5, "kosten_pro_einheit": 0.45},
        "Cleaner": {"aktuell": 1000.0, "limit": 200.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 15.0, "kosten_pro_einheit": 0.05}
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

# Premium Kundenstruktur (inkl. Neukunden-Erkennung)
if 'kunden_liste' not in st.session_state:
    st.session_state.kunden_liste = {
        "Beispiel Kundin": {
            "Telefon": "+49 123 456789", "Farbe": "#721c24", "Ist_Neukunde": False,
            "Kaffee": "Cappuccino mit Hafermilch", "Allergien": "Keine", "Notizen": "Bevorzugt mattes Finish", 
            "Anamnese_Text": "Keine Auffälligkeiten", "DSGVO_Akzeptiert": True, "Fotos": []
        }
    }

if 'freie_slots' not in st.session_state: 
    st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
if 'termine' not in st.session_state: 
    st.session_state.termine = pd.DataFrame(columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe", "Ist_Neukunde"])

# FINANZEN DATENFRAME
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
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .vergleichs-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    /* 📜 Kompakter Scroll-Container für unendlich viele Kundeninformationen */
    .scroll-container {
        max-height: 380px;
        overflow-y: auto;
        padding-right: 8px;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        background-color: #fafafa;
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
                        "Anamnese_Text": "", "DSGVO_Akzeptiert": False, "Fotos": [], "Ist_Neukunde": True
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
    
    # 💾 Optimierter, schlankerer linker Bereich (Sidebar) mit Rollbalken
    with st.sidebar:
        st.write(f"💼 Modus: **{st.session_state.user}**")
        st.write("---")
        heute_str = datetime.date.today().strftime('%Y-%m-%d')
        termine_heute = len(st.session_state.termine[st.session_state.termine["Datum"] == heute_str]) if not st.session_state.termine.empty else 0
        st.metric(label="Termine heute", value=termine_heute)
        
        st.write("### 📜 Studio-Schnellübersicht")
        st.markdown("<div class='scroll-container'>", unsafe_allow_html=True)
        for kunde_name, k_daten in st.session_state.kunden_liste.items():
            status_tag = "🆕 Neukunde" if k_daten.get("Ist_Neukunde", False) else "👑 Stammkunde"
            st.markdown(f"""
            **👤 {kunde_name}** * Status: {status_tag}  
            * ☕ Getränk: {k_daten['Kaffee']}  
            * 📞 Tel: {k_daten['Telefon'] if k_daten['Telefon'] else 'Nicht hinterlegt'}  
            <hr style='margin: 8px 0; border:0; border-top:1px solid #ddd;'>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    menue = st.tabs([
        "🗓️ Kalender & Slots", 
        "👥 Digitale Luxus-Kartei", 
        "📝 Datenschutz & Anamnese-Editor", 
        "📢 Schwarzes Brett & Lager", 
        "🛒 Material-Einkauf & Vergleich", 
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
            st.session_state.neukunden_extra_zeit = st.number_input("⏱️ Extra Beratungs-Zeit für Neukunden (Minuten)", value=st.session_state.neukunden_extra_zeit, step=5)
            
            st.write("---")
            st.markdown("<h4>Slot freigeben</h4>")
            slot_datum = st.date_input("Datum wählen", datetime.date.today(), key="admin_slot_d")
            feiertag_name = get_feiertag(slot_datum)
            hinweis_text = feiertag_name if feiertag_name else "-"
            if feiertag_name:
                st.markdown(f"<span style='color: #721c24;'>ℹ️ Hinweis: An diesem Tag ist {feiertag_name}.</span>", unsafe_allow_html=True)
                
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
                    status_hinweis = "⚠️ NEUKUNDE (inkl. Extra-Zeit)" if t.get("Ist_Neukunde", False) else "Stammkunde"
                    st.markdown(f"""
                        <div class='calendar-box' style='background-color: {bg_color};'>
                            <strong>📅 {t['Datum']} | ⏰ {t['Uhrzeit']} Uhr</strong><br>
                            👤 Kunde: {t['Kunde']} ({status_hinweis})<br>
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
                        "Anamnese_Text": "", "DSGVO_Akzeptiert": False, "Fotos": [], "Ist_Neukunde": False
                    }
                    st.success("Kundin angelegt!")
                    st.rerun()
                    
        with col_k_akte:
            if ausgewaehlter_kunde:
                akte = st.session_state.kunden_liste[ausgewaehlter_kunde]
                st.markdown(f"<div class='kunden-akte'><h3>👑 VIP Akte: {ausgewaehlter_kunde}</h3>", unsafe_allow_html=True)
                
                akte["Ist_Neukunde"] = st.checkbox("Als Neukunde markieren (Löst automatische Extrazeit aus)", value=akte.get("Ist_Neukunde", False))
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

    # TAB 4: SCHWARZES BRETT & INTELLIGENTES LAGER
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
            
            c_menge, c_einheit = st.columns([2, 1])
            eingabe_menge = c_menge.number_input("Menge/Inhalt:", min_value=0.0, value=1.0, step=0.5)
            gewaehlte_einheit = c_einheit.selectbox("Einheit:", ["ml", "l (Liter)", "Stk."])
            
            if "l (Liter)" in gewaehlte_einheit:
                berechnete_menge = eingabe_menge * 1000.0
                speicher_einheit = "ml"
            else:
                berechnete_menge = eingabe_menge
                speicher_einheit = gewaehlte_einheit
                
            neu_lim = st.number_input("Warnen ab (Mindestlimit)", min_value=0.0, value=15.0)
            neu_menge = st.number_input(f"Verbrauch pro Kunde (ca. in {speicher_einheit})", min_value=0.0, value=1.5)
            neu_cost = st.number_input("💰 Material-Kosten für eine Einheit (€):", min_value=0.0, value=0.50, step=0.05, help="Der Preis pro ml oder pro Stück für deinen Material-Einkauf.")
            
            if st.button("Produkt ins System aufnehmen"):
                if neu_prod:
                    st.session_state.lager_bestand[neu_prod] = {
                        "aktuell": berechnete_menge, "limit": neu_lim, "einheit": speicher_einheit, 
                        "auto_abzug": True, "verbrauch_pro_kunde": neu_menge, "kosten_pro_einheit": neu_cost
                    }
                    st.success(f"'{neu_prod}' wurde registriert!")
                    st.rerun()
                
        with col_lager:
            st.markdown("<div class='card'><h4>📦 Lagerbestände & Genaue Verbrauchswerte</h4></div>", unsafe_allow_html=True)
            for prod, daten in list(st.session_state.lager_bestand.items()):
                st.write(f"##### 🏷️ {prod} ({daten['einheit']})")
                c1, c2, c3 = st.columns(3)
                
                st.session_state.lager_bestand[prod]["aktuell"] = c1.number_input(f"Ist-Vorrat##{prod}", min_value=0.0, value=float(daten["aktuell"]), key=f"ist_{prod}")
                st.session_state.lager_bestand[prod]["verbrauch_pro_kunde"] = c2.number_input(f"Verbrauch/Kunde##{prod}", min_value=0.0, value=float(daten["verbrauch_pro_kunde"]), key=f"vpr_{prod}")
                st.session_state.lager_bestand[prod]["kosten_pro_einheit"] = c3.number_input(f"Kosten/Einheit (€)##{prod}", min_value=0.0, value=float(daten.get("kosten_pro_einheit", 0.10)), key=f"cpe_{prod}")
                
                mat_kosten_pro_kunde = daten["verbrauch_pro_kunde"] * daten.get("kosten_pro_einheit", 0.0)
                st.write(f"💵 *Materialpreis pro Kunde für dieses Produkt:* **{mat_kosten_pro_kunde:.2f} €**")
                
                if c1.button(f"Aufstocken (+100 / +10)##{prod}"):
                    st.session_state.lager_bestand[prod]["aktuell"] += 100 if daten["einheit"] == "ml" else 10
                    st.rerun()
                st.write("---")

    # TAB 5: MATERIAL-EINKAUF-FAVORITEN & WEBSEITEN-PREISVERGLEICH
    with menue[4]:
        st.subheader("🛒 Material-Katalog mit Foto-Upload & Live-Preisvergleich")
        col_cat1, col_cat2 = st.columns([1, 2])
        
        with col_cat1:
            st.markdown("<div class='card'><h4>📸 Lieblingsmaterial hinzufügen</h4></div>", unsafe_allow_html=True)
            mat_name = st.text_input("Name des Materials:", placeholder="z.B. Jolifin Farbgel Diamond Rose")
            mat_preis = st.number_input("Standard-Richtpreis (€):", min_value=0.0, value=9.95, step=0.5)
            mat_notiz = st.text_area("Besondere Notizen / Marke / Code:")
            
            mat_foto = st.file_uploader("Produkt-Foto hochladen (Kamera/Galerie):", type=["jpg", "png", "jpeg"], key="mat_foto_upload")
            
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
                st.info("Dein Material-Katalog ist noch leer.")
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
        w1, w2, w3, w4 = st.columns(4)
        
        w1.markdown("<div class='vergleichs-box'><h4>🛍️ Jolifin</h4><a href='https://www.jolifin.de' target='_blank'>Shop öffnen</a>", unsafe_allow_html=True); w1.number_input("Warenkorb Preis (€):", key="p_s1"); w1.markdown("</div>", unsafe_allow_html=True)
        w2.markdown("<div class='vergleichs-box'><h4>🛍️ NeoNail</h4><a href='https://www.neonail.de' target='_blank'>Shop öffnen</a>", unsafe_allow_html=True); w2.number_input("Warenkorb Preis (€):", key="p_s2"); w2.markdown("</div>", unsafe_allow_html=True)
        w3.markdown("<div class='vergleichs-box'><h4>🛍️ LyniNails</h4><a href='https://www.lyni-nails.de' target='_blank'>Shop öffnen</a>", unsafe_allow_html=True); w3.number_input("Warenkorb Preis (€):", key="p_s3"); w3.markdown("</div>", unsafe_allow_html=True)
        w4.markdown("<div class='vergleichs-box'><h4>🛍️ Amazon</h4><a href='https://www.amazon.de' target='_blank'>Shop öffnen</a>", unsafe_allow_html=True); w4.number_input("Warenkorb Preis (€):", key="p_s4"); w4.markdown("</div>", unsafe_allow_html=True)

    # TAB 6: BEARBEITBARE RECHNUNGEN & QUITTUNGEN (Mit automatischer Materialanrechnung)
    with menue[5]:
        st.subheader("📄 Bearbeitbare Quittungen & Automatisierte Material-Anrechnung")
        col_pdf_f, col_pdf_v = st.columns([1, 2])
        
        # Berechne die gesamten Materialkosten, die pro Behandlung verbraucht werden
        gesamte_studiomaterial_kosten = 0.0
        for p, d in st.session_state.lager_bestand.items():
            gesamte_studiomaterial_kosten += (d["verbrauch_pro_kunde"] * d.get("kosten_pro_einheit", 0.0))
            
        with col_pdf_f:
            st.markdown("<div class='card'><h4>Rechnungs-Editor</h4></div>", unsafe_allow_html=True)
            doc_kunde = st.selectbox("Wähle eine Kundin:", list(st.session_state.kunden_liste.keys()), key="doc_k")
            doc_art = st.selectbox("Behandlung:", list(st.session_state.zeiten_naegel.keys()), key="doc_a")
            doc_basispreis = st.number_input("Reiner Dienstleistungspreis (€):", min_value=0.0, value=60.0, step=5.0)
            
            anrechnen = st.checkbox("Materialkosten aufschlagen & separat ausweisen?", value=True)
            effektive_materialkosten = gesamte_studiomaterial_kosten if anrechnen else 0.0
            
            st.write(f"ℹ️ *Ermittelter Materialwert für diese Behandlung:* **{effektive_materialkosten:.2f} €**")
            end_gesamtpreis = doc_basispreis + effektive_materialkosten
            st.write(f"🎯 **Endpreis für die Kundin:** {end_gesamtpreis:.2f} €")
            
            doc_datum = st.date_input("Rechnungsdatum", datetime.date.today(), key="doc_d")
            doc_typ = st.radio("Dokumententyp:", ["Professionelle Quittung", "Einverständniserklärung"], horizontal=True)
            
            if st.button("Dokument generieren & anzeigen", use_container_width=True):
                logo_html = f"<img src='{LOGO_URL}' style='max-height: 60px; float: right; border-radius: 8px;' onerror='this.style.display=\"none\"'>"
                if doc_typ == "Professionelle Quittung":
                    st.session_state.pdf_view = f"""
                        <div class='pdf-frame'>
                            {logo_html}
                            <h1 style='color: #721c24; margin:0;'>Redline Studio</h1>
                            <hr style='border: 1px solid #721c24;'>
                            <h2 style='text-align: center;'>OFFIZIELLE QUITTUNG</h2>
                            <p><strong>Datum:</strong> {doc_datum.strftime('%d.%m.%Y')}</p>
                            <p><strong>Kunde:</strong> {doc_kunde}</p>
                            <p><strong>Leistung:</strong> {doc_art}</p>
                            <table style='width:100%; border-collapse: collapse; margin-top:20px;'>
                                <tr style='border-bottom: 1px solid #ddd; padding: 8px 0;'>
                                    <td style='padding: 8px 0;'>Dienstleistung ({doc_art})</td>
                                    <td style='text-align:right;'>{doc_basispreis:.2f} €</td>
                                </tr>
                                <tr style='border-bottom: 1px solid #ddd;'>
                                    <td style='padding: 8px 0;'>Angerechnetes Studiomaterial (Anteilig)</td>
                                    <td style='text-align:right;'>{effektive_materialkosten:.2f} €</td>
                                </tr>
                                <tr style='font-weight: bold; font-size:1.2em;'>
                                    <td style='padding: 10px 0;'>Gesamtsumme bezahlt:</td>
                                    <td style='text-align:right; padding: 10px 0;'>{end_gesamtpreis:.2f} €</td>
                                </tr>
                            </table>
                            <p style='font-style: italic; font-size: 0.85em; margin-top:40px;'>Es gilt die Kleinunternehmerregelung (§ 19 UStG). Vielen Dank für deinen Besuch! 💅</p>
                        </div>
                    """
                else:
                    st.session_state.pdf_view = f"""
                        <div class='pdf-frame'>
                            {logo_html}
                            <h1 style='color: #721c24; margin:0;'>Redline Studio</h1>
                            <hr style='border: 1px solid #721c24;'>
                            <h2 style='text-align: center;'>Einverständniserklärung & Protokoll</h2>
                            <p><strong>Datum:</strong> {doc_datum.strftime('%d.%m.%Y')}</p>
                            <p><strong>Kunde:</strong> {doc_kunde}</p>
                            <p><strong>Behandlung:</strong> {doc_art}</p>
                            <p style='margin-top:20px;'>Ich wurde über die Behandlung, eventuelle Risiken sowie die häusliche Nachpflege aufgeklärt und stimme der Behandlung zu.</p>
                            <br><br>
                            <div style='display: flex; justify-content: space-between; margin-top:50px;'>
                                <div>_____________________<br><span style='font-size: 0.8em;'>Unterschrift Kunde</span></div>
                                <div>_____________________<br><span style='font-size: 0.8em;'>Unterschrift Redline Studio</span></div>
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
                st.success("Transaktion erfolgreich verbucht!")
                st.rerun()
                
            st.write("---")
            st.write("**Historischer Verlauf (Einzelbuchungen):**")
            st.dataframe(st.session_state.finanzen, use_container_width=True)
        
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
                st.info("Sobald Transaktionen vorliegen, entstehen hier die Grafiken!")

# --- SEITE: KUNDEN-BUCHUNG ---
else:
    show_logo_and_header()
    
    # Erkennt vollautomatisch, ob registrierter Stammkunde oder Neukunde
    ist_neukunde_erkannt = st.session_state.kunden_liste[st.session_state.user].get("Ist_Neukunde", True)
    
    with st.sidebar:
        st.write(f"🌸 Kundin: **{st.session_state.user}**")
        if ist_neukunde_erkannt:
            st.markdown("<span style='color: #721c24; font-weight:bold;'>✨ Neukundinnen-Status aktiv (inkl. Erstberatung)</span>", unsafe_allow_html=True)
        else:
            st.write("👑 Status: Stammkundin")
        if st.button("Abmelden"):
            st.session_state.user = None
            st.rerun()
            
    st.subheader("🗓️ Wähle deinen Wunschtermin")
    nagel_wunsch = st.selectbox("Was möchtest du machen lassen?", list(st.session_state.zeiten_naegel.keys()))
    
    basis_zeit = st.session_state.zeiten_naegel[nagel_wunsch]
    aufgeschlagene_zeit = st.session_state.neukunden_extra_zeit if ist_neukunde_erkannt else 0
    gesamte_blockade_zeit = basis_zeit + aufgeschlagene_zeit + st.session_state.puffer_zeit
    
    st.info(f"Eingeplante Behandlungsdauer: {basis_zeit} Min. " + (f"+ {aufgeschlagene_zeit} Min. Erstberatung" if ist_neukunde_erkannt else "") + f" (+ Hygiene-Puffer).")
    
    if "freie_slots" in st.session_state and not st.session_state.freie_slots.empty:
        freie_anzeige = st.session_state.freie_slots[st.session_state.freie_slots["Status"] == "Frei"]
    else:
        freie_anzeige = pd.DataFrame()
        
    if freie_anzeige.empty:
        st.warning("Aktuell sind leider keine freien Termine freigeschaltet.")
    else:
        for idx, row in freie_anzeige.iterrows():
            verfuegbare_minuten = int(row["Dauer_Minuten"])
            if verfuegbare_minuten >= gesamte_blockade_zeit:
                col_slot, col_buch_btn = st.columns([3, 1])
                col_slot.write(f"📅 **{row['Datum']}** | ⏰ Von {row['Startzeit']} bis {row['Endzeit']} Uhr")
                if col_buch_btn.button("Jetzt buchen", key=f"book_{idx}"):
                    st.session_state.freie_slots.at[idx, "Status"] = "Gebucht"
                    
                    # Automatischer Bestandsabzug im Verbrauchslager
                    for prod, daten in st.session_state.lager_bestand.items():
                        if daten["auto_abzug"] and daten["aktuell"] > 0:
                            st.session_state.lager_bestand[prod]["aktuell"] = max(0.0, daten["aktuell"] - daten["verbrauch_pro_kunde"])
                    
                    kunden_farbe = st.session_state.kunden_liste[st.session_state.user]["Farbe"]
                    neuer_termin = pd.DataFrame([[row['Datum'], row['Startzeit'], st.session_state.user, nagel_wunsch, gesamte_blockade_zeit, kunden_farbe, ist_neukunde_erkannt]], 
                                                columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe", "Ist_Neukunde"])
                    st.session_state.termine = pd.concat([st.session_state.termine, neuer_termin], ignore_index=True)
                    
                    # Nach der ersten erfolgreichen Buchung wird sie automatisch zur Stammkundin
                    st.session_state.kunden_liste[st.session_state.user]["Ist_Neukunde"] = False
                    
                    st.success("Erfolgreich gebucht! Wir freuen uns auf dich! 🎉")
                    st.rerun()

