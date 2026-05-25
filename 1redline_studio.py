import streamlit as st
import pandas as pd
import datetime
import base64

# ==============================================================================
# 1. SEITENKONFIGURATION & PREMIUM GLOBAL STYLES
# ==============================================================================
st.set_page_config(
    page_title="Redline Studio Pro - Premium Management & Booking System",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. INITIALISIERUNG ALLER SITZUNGSSPEICHER (SESSION STATES)
# ==============================================================================
# Authentifizierung & Benutzerstatus
if 'user' not in st.session_state: 
    st.session_state.user = None

# Behandlungstypen und Basis-Dauer (in Minuten)
if 'zeiten_naegel' not in st.session_state:
    st.session_state.zeiten_naegel = {
        "Neumodellage": 120, 
        "Auffüllen": 90, 
        "French / Extra Design": 45,
        "Maniküre Klassisch": 45,
        "Wellness Fußpflege": 60,
        "Nagel-Reparatur Einzeln": 20
    }

# Standard-Pufferzeiten für Hygiene, Desinfektion und Vorbereitung
if 'puffer_zeit' not in st.session_state: 
    st.session_state.puffer_zeit = 20

# Zusätzliche Beratungszeit, falls es sich um einen Neukunden handelt
if 'neukunden_extra_zeit' not in st.session_state: 
    st.session_state.neukunden_extra_zeit = 30  

# Digitales Schwarzes Brett (Studio-News auf der Startseite)
if 'studio_news' not in st.session_state:
    st.session_state.studio_news = "✨ Willkommen im Redline Studio! Ab sofort über 20 neue Chrome-Pigmente und luxuriöse Cat-Eye-Gele verfügbar! ✨"
if 'news_aktiv' not in st.session_state:
    st.session_state.news_aktiv = True

# 🎨 LIVE-DESIGN-SPEICHER & ADVANCED BRANDING SYSTEM
if 'uploaded_logo' not in st.session_state: 
    st.session_state.uploaded_logo = None
if 'uploaded_bg' not in st.session_state: 
    st.session_state.uploaded_bg = None
if 'use_background_image' not in st.session_state: 
    st.session_state.use_background_image = True
if 'color_bg' not in st.session_state: 
    st.session_state.color_bg = "#FFF5F5"
if 'color_primary' not in st.session_state: 
    st.session_state.color_primary = "#D4A3A3"
if 'color_accent' not in st.session_state: 
    st.session_state.color_accent = "#D4AF37"
if 'color_text' not in st.session_state: 
    st.session_state.color_text = "#4A3737"

# Absolutes Fallback-Bild für das Logo, falls nichts hochgeladen wurde
LOGO_URL_DEFAULT = "https://i.ibb.co/6w2fR6V/1000083367.jpg"

# 🗃️ ERWEITERTES DYNAMISCHES WARENLAGER (Inklusive Kostenkalkulation)
if 'lager_bestand' not in st.session_state:
    st.session_state.lager_bestand = {
        "Nagelfeilen (Premium Zebra)": {"aktuell": 25.0, "limit": 5.0, "einheit": "Stk.", "auto_abzug": True, "verbrauch_pro_kunde": 1.0, "kosten_pro_einheit": 1.20},
        "Primer / Haftvermittler": {"aktuell": 60.0, "limit": 10.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 0.5, "kosten_pro_einheit": 0.30},
        "High-Gloss Top Coat": {"aktuell": 120.0, "limit": 15.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 1.5, "kosten_pro_einheit": 0.45},
        "Isopropanol Cleaner": {"aktuell": 1500.0, "limit": 200.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 15.0, "kosten_pro_einheit": 0.05},
        "Premium Aufbaugel (Nude)": {"aktuell": 250.0, "limit": 30.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 4.0, "kosten_pro_einheit": 0.60},
        "Acrylgel Clear": {"aktuell": 180.0, "limit": 20.0, "einheit": "ml", "auto_abzug": True, "verbrauch_pro_kunde": 3.5, "kosten_pro_einheit": 0.75},
        "Zelletten (Fusselfrei)": {"aktuell": 500.0, "limit": 50.0, "einheit": "Stk.", "auto_abzug": True, "verbrauch_pro_kunde": 12.0, "kosten_pro_einheit": 0.02}
    }

# 🛒 SPEICHER FÜR MATERIAL-KATALOG & FAVORITEN
if 'material_katalog' not in st.session_state:
    st.session_state.material_katalog = []

# 📋 RECHTLICHE TEXT-VORLAGEN
if 'anamnese_vorlage' not in st.session_state:
    st.session_state.anamnese_vorlage = (
        "1. Haben Sie bekannte Allergien (z.B. gegen Acrylate, Gele, Klebstoffe, Kunststoffe)?\n"
        "2. Liegen Nagelerkrankungen vor (z.B. Nagelpilz, Onycholyse, bakterielle Infektionen)?\n"
        "3. Nehmen Sie regelmäßig Medikamente (z.B. Cortison, Antibiotika, Blutverdünner)?\n"
        "4. Besteht eine Schwangerschaft, eine hormonelle Umstellung oder Diabetes Mellitus?\n"
        "5. Neigen Ihre Nägel zu starker Liftung oder Feuchtigkeit?"
    )
if 'datenschutz_vorlage' not in st.session_state:
    st.session_state.datenschutz_vorlage = (
        "Einwilligungserklärung nach DSGVO:\n"
        "Ich willige ausdrücklich ein, dass Redline Studio meine personenbezogenen Daten, Kontaktdaten, "
        "Fotos der Modellagen sowie medizinische Behandlungsnotizen zum Zweck der Kundenbetreuung elektronisch speichert. "
        "Die Daten werden absolut vertraulich behandelt, verschlüsselt hinterlegt und niemals an Dritte weitergegeben."
    )

# ==============================================================================
# NEU: LIVE-VERBINDUNG ZU GOOGLE SHEETS (KUNDENKARTEI)
# ==============================================================================
try:
    conn = st.connection("gsheets", type=None)
    df_kunden = conn.read(worksheet="Kunden", ttl="5m")
    
    if not df_kunden.empty:
        st.session_state.kunden_liste = {}
        for _, row in df_kunden.iterrows():
            name_key = str(row["Name"]).strip()
            st.session_state.kunden_liste[name_key] = {
                "Telefon": str(row["Telefon"]) if pd.notna(row["Telefon"]) else "",
                "Farbe": str(row["Farbe"]) if pd.notna(row["Farbe"]) else "#D4A3A3",
                "Kaffee": str(row["Kaffee"]) if pd.notna(row["Kaffee"]) else "",
                "Allergien": str(row["Allergien"]) if pd.notna(row["Allergien"]) else "Keine",
                "Notizen": str(row["Notizen"]) if pd.notna(row["Notizen"]) else "",
                "Anamnese_Text": str(row["Anamnese_Text"]) if pd.notna(row["Anamnese_Text"]) else "Noch kein Befund eingetragen.",
                "DSGVO_Akzeptiert": bool(row["DSGVO_Akzeptiert"]) if pd.notna(row["DSGVO_Akzeptiert"]) else False,
                "Fotos": []
            }
    else:
        st.session_state.kunden_liste = {
            "Beispiel Kundin": {"Telefon": "+49 123", "Farbe": "#D4A3A3", "Kaffee": "Cappuccino", "Allergien": "Keine", "Notizen": "", "Anamnese_Text": "Gesund", "DSGVO_Akzeptiert": True, "Fotos": []}
        }
except Exception as e:
    if 'kunden_liste' not in st.session_state:
        st.session_state.kunden_liste = {
            "Beispiel Kundin": {"Telefon": "+49 123", "Farbe": "#D4A3A3", "Kaffee": "Cappuccino", "Allergien": "Keine", "Notizen": "", "Anamnese_Text": "Gesund", "DSGVO_Akzeptiert": True, "Fotos": []}
        }

# Tabellen-Strukturen für Termine, Arbeits-Slots und Finanzen
if 'freie_slots' not in st.session_state: 
    st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
if 'termine' not in st.session_state: 
    st.session_state.termine = pd.DataFrame(columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe", "Status", "Ist_Neukunde"])
if 'finanzen' not in st.session_state: 
    st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])

# ==============================================================================
# 3. INTERNE HINTERGRUND-BILD-VERARBEITUNG & CSS ENGINE
# ==============================================================================
bg_style = ""
if st.session_state.use_background_image and st.session_state.uploaded_bg is not None:
    try:
        bytes_data = st.session_state.uploaded_bg.getvalue()
        base64_bg = base64.b64encode(bytes_data).decode()
        bg_style = f"""
            background-image: linear-gradient(rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.5)), url("data:image/jpeg;base64,{base64_bg}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        """
    except Exception:
        bg_style = f"background-color: {st.session_state.color_bg} !important;"
else:
    bg_style = f"background-color: {st.session_state.color_bg} !important;"

# Umfassendes Design-Injektions-System (Erhöht Stabilität und visuelle Eleganz)
st.markdown(f"""
    <style>
    .stApp {{
        {bg_style}
        color: {st.session_state.color_text} !important;
    }}
    h1, h2, h3, h4, h5, h6, label, .stMarkdown {{
        color: {st.session_state.color_text} !important;
        font-family: 'Playfair Display', serif;
    }}
    .main-header {{
        background-color: {st.session_state.color_primary};
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 30px;
        border-bottom: 4px solid {st.session_state.color_accent};
    }}
    .main-header h1 {{
        color: #ffffff !important;
        font-size: 3.6rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
    }}
    .main-header p {{
        color: #ffffff;
        font-size: 1.4rem;
        font-style: italic;
        margin-top: 5px;
        opacity: 0.95;
    }}
    .main-logo-img {{
        max-height: 110px;
        max-width: 110px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid {st.session_state.color_accent};
    }}
    .news-banner {{
        background-color: rgba(255, 255, 255, 0.9);
        color: {st.session_state.color_text};
        border: 2px solid {st.session_state.color_accent};
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        font-size: 1.25rem;
        font-weight: bold;
        margin-bottom: 30px;
        backdrop-filter: blur(6px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.06);
    }}
    .material-alert {{
        background-color: #fff3cd;
        color: #856404;
        border: 2px solid #ffeeba;
        padding: 15px;
        border-radius: 10px;
        font-weight: bold;
        margin-bottom: 12px;
    }}
    .stButton>button {{
        background-color: {st.session_state.color_primary} !important;
        color: #ffffff !important;
        border: 1px solid {st.session_state.color_accent} !important;
        border-radius: 10px !important;
        font-weight: bold !important;
        padding: 10px 20px !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        background-color: {st.session_state.color_accent} !important;
        color: {st.session_state.color_text} !important;
        transform: scale(1.03);
        box-shadow: 0 5px 12px rgba(0,0,0,0.15);
    }}
    .card {{
        background-color: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(12px);
        padding: 25px;
        border-radius: 15px;
        border-left: 6px solid {st.session_state.color_primary};
        margin-bottom: 25px;
        box-shadow: 0 5px 10px rgba(0,0,0,0.04);
    }}
    .kunden-akte {{
        background-color: rgba(255, 255, 255, 0.94);
        backdrop-filter: blur(12px);
        padding: 30px;
        border-radius: 15px;
        border: 2px solid {st.session_state.color_accent};
        margin-top: 20px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.05);
    }}
    .calendar-box {{
        border: 1px solid {st.session_state.color_primary};
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: {st.session_state.color_text};
        background-color: rgba(255,255,255,0.92);
        border-left: 8px solid {st.session_state.color_accent};
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }}
    .pdf-frame {{
        border: 3px solid {st.session_state.color_primary};
        padding: 35px;
        background-color: white;
        color: black;
        font-family: 'Courier New', monospace;
        box-shadow: 0 6px 12px rgba(0,0,0,0.12);
        border-radius: 4px;
    }}
    .vergleichs-box {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 20px;
        border-radius: 12px;
        border: 2px solid {st.session_state.color_accent};
        text-align: center;
        margin-bottom: 15px;
        transition: transform 0.2s;
    }}
    .vergleichs-box:hover {{
        transform: translateY(-3px);
    }}
    .scroll-container {{
        max-height: 420px;
        overflow-y: auto;
        padding-right: 10px;
        border: 1px solid {st.session_state.color_accent};
        border-radius: 8px;
        background-color: rgba(255,255,255,0.75);
    }}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 4. FEIERTAGS-BERECHNUNGS-ENGINE (GAUSS-ALGORITHMUS)
# ==============================================================================
def get_feiertag(datum):
    jahr = datum.year
    feste = {
        (1, 1): "Neujahr", (6, 1): "Heilige Drei Könige", (1, 5): "Tag der Arbeit",
        (1, 8): "Schweizer Nationalfeiertag", (3, 10): "Tag der Deutschen Einheit",
        (26, 10): "Nationalfeiertag (AT)", (1, 11): "Allerheiligen",
        (25, 12): "1. Weihnachtstag", (26, 12): "2. Weihnachtstag"
    }
    # Gaußsche Osterformel zur dynamischen Berechnung beweglicher Feiertage
    a = jahr % 19
    b = jahr % 4
    c = jahr % 7
    d = (19 * a + 24) % 30
    e = (2 * b + 4 * c + 6 * d + 5) % 7
    oster_tage = 22 + d + e
    
    if oster_tage > 31:
        oster_datum = datetime.date(jahr, 4, oster_tage - 31)
    else:
        oster_datum = datetime.date(jahr, 3, oster_tage)
    
    # Abhängige bewegliche Feiertage ermitteln
    if datum == oster_datum - datetime.timedelta(days=2): return "Karfreitag"
    if datum == oster_datum: return "Ostersonntag"
    if datum == oster_datum + datetime.timedelta(days=1): return "Ostermonntag"
    if datum == oster_datum + datetime.timedelta(days=39): return "Auffahrt / Himmelfahrt"
    if datum == oster_datum + datetime.timedelta(days=50): return "Pfingstmontag"
    
    # Fixe Feiertage abgleichen
    if (datum.day, datum.month) in feste: 
        return feste[(datum.day, datum.month)]
    return None

# ==============================================================================
# 5. HEADER & BRANDING RENDERER
# ==============================================================================
def show_logo_and_header():
    if st.session_state.uploaded_logo is not None:
        try:
            bytes_logo = st.session_state.uploaded_logo.getvalue()
            base64_logo = base64.b64encode(bytes_logo).decode()
            logo_src = f"data:image/jpeg;base64,{base64_logo}"
        except Exception:
            logo_src = LOGO_URL_DEFAULT
    else:
        logo_src = LOGO_URL_DEFAULT

    st.markdown(f"""
        <div class='main-header'>
            <img src='{logo_src}' class='main-logo-img'>
            <div>
                <h1>Redline Studio</h1>
                <p>Kreativität, Eleganz & High-End Nageldesign</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.news_aktiv and st.session_state.studio_news:
        st.markdown(f"<div class='news-banner'>📢 {st.session_state.studio_news}</div>", unsafe_allow_html=True)

# ==============================================================================
# 6. LOGIN- & REGISTRIERUNGSSYSTEM (FÜR KUNDEN UND ADMIN)
# ==============================================================================
if st.session_state.user is None:
    show_logo_and_header()
    st.markdown("<h2 style='text-align: center; font-weight: bold;'>Willkommen im digitalen Studio-Portal</h2>", unsafe_allow_html=True)
    st.write("")
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        tab_log, tab_reg = st.tabs(["🔑 Studio-Anmeldung", "✨ Neue Kundenkartei anlegen"])
        
        # TAB: ANMELDUNG
        with tab_log:
            with st.form(key="login_form_comprehensive", clear_on_submit=False):
                st.markdown("##### Bitte Identität nachweisen oder Admin-Code eingeben")
                passwort_verbergen = st.checkbox("🔒 Sicherheits-Modus aktivieren (Verdeckte Eingabe)", key="chk_sec_comp")
                input_type = "password" if passwort_verbergen else "default"
                
                name_eingabe = st.text_input(
                    "Dein vollständiger Name ODER Admin-Passwort *", 
                    placeholder="Vorname Nachname oder Passwort...",
                    type=input_type,
                    key="log_name_in_comp"
                )
                submit_login = st.form_submit_button("Anmelden & Dashboard laden", use_container_width=True)
                
                if submit_login:
                    bereinigte_eingabe = name_eingabe.strip()
                    if bereinigte_eingabe == "Alocasia":
                        st.session_state.user = "Admin"
                        st.success("Erfolgreich als Admin autorisiert! Lade Kontrollzentrum...")
                        st.rerun()
                    elif bereinigte_eingabe == "":
                        st.error("Eingabefeld darf nicht leer sein! Bitte gib deinen Namen ein.")
                    else:
                        if bereinigte_eingabe in st.session_state.kunden_liste:
                            st.session_state.user = bereinigte_eingabe
                            st.success(f"Willkommen zurück, {bereinigte_eingabe}! ✨")
                            st.rerun()
                        else:
                            st.error("❌ Name nicht in der Kartei registriert. Bitte erstelle rechts eine Kartei oder prüfe die Schreibweise.")

        # TAB: REGISTRIERUNG DURCH KUNDEN
        with tab_reg:
            with st.form(key="register_form_comprehensive", clear_on_submit=True):
                st.markdown("##### ✨ Digitale Kundenkartei für Neukunden erstellen")
                reg_name = st.text_input("Vollständiger Name (Vorname Nachname) *", placeholder="Max Mustermann")
                reg_tel = st.text_input("Telefonnummer für kurzfristige Rückfragen / Absagen", placeholder="+49 170 ...")
                reg_kaffee = st.text_input("☕ Wie trinkst du deinen Kaffee oder Tee am liebsten?", placeholder="z.B. Schwarz, Zucker, Hafermilch...")
                reg_allergien = st.text_input("⚠️ Bekannte Allergien gegen Inhaltsstoffe", value="Keine")
                reg_notizen = st.text_area("💅 Erste Wünsche für deine Modellage", placeholder="z.B. Bevorzuge extreme Längen, Acryl, French-Klassiker...")
                
                st.markdown("---")
                st.markdown(f"**Datenschutz-Einwilligung gemäß DSGVO:**\n{st.session_state.datenschutz_vorlage}")
                reg_dsgvo = st.checkbox("Ich stimme den Datenschutzbestimmungen zur elektronischen Speicherung vollinhaltlich zu. *")
                
                submit_reg = st.form_submit_button("Kundenkartei jetzt absenden ✨", use_container_width=True)
                
                if submit_reg:
                    if not reg_name.strip():
                        st.error("Bitte einen gültigen Namen eintragen.")
                    elif not reg_dsgvo:
                        st.error("Die Zustimmung zum Datenschutz ist gesetzlich zwingend erforderlich.")
                    elif reg_name.strip() in st.session_state.kunden_liste:
                        st.error("Dieser Name ist bereits vergeben. Logge dich bitte regulär ein.")
                   else:
            neuer_name = reg_name.strip()
            
            # 1. In der Live-Sitzung des Browsers speichern
            st.session_state.kunden_liste[neuer_name] = {
                "Telefon": reg_tel.strip(),
                "Farbe": st.session_state.color_primary,
                "Kaffee": reg_kaffee.strip() if reg_kaffee.strip() else "Keine Angabe",
                "Allergien": reg_allergien.strip() if reg_allergien.strip() else "Keine",
                "Notizen": reg_notizen.strip(),
                "Anamnese_Text": "Noch nicht vom Admin erhoben. (Wird beim ersten Termin durchgeführt.)",
                "DSGVO_Akzeptiert": True,
                "Fotos": []
            }
            
            # 2. Direkt live in die Google Tabelle hochladen
            try:
                neue_zeile = pd.DataFrame([{
                    "Name": neuer_name,
                    "Telefon": reg_tel.strip(),
                    "Farbe": st.session_state.color_primary,
                    "Kaffee": reg_kaffee.strip() if reg_kaffee.strip() else "Keine Angabe",
                    "Allergien": reg_allergien.strip() if reg_allergien.strip() else "Keine",
                    "Notizen": reg_notizen.strip(),
                    "Anamnese_Text": "Noch nicht vom Admin erhoben.",
                    "DSGVO_Akzeptiert": True
                }])
                
                conn = st.connection("gsheets", type=None)
                existing_df = conn.read(worksheet="Kunden")
                updated_df = pd.concat([existing_df, neue_zeile], ignore_index=True)
                conn.update(worksheet="Kunden", data=updated_df)
            except Exception as e:
                st.warning("Hinweis: Kartei lokal erstellt, aber Google-Synchronisation verzögert.")

            st.session_state.user = neuer_name
            st.success("Konto erfolgreich generiert und eingeloggt! Erlebe Redline Studio. 🎉")
            st.rerun()
    # 2. NEU: Direkt in die Google Tabelle hochladen
    try:
        # Wir erstellen eine neue Zeile als Daten-Tabelle (DataFrame)
        neue_zeile = pd.DataFrame([{
            "Name": neuer_name,
            "Telefon": reg_tel.strip(),
            "Farbe": st.session_state.color_primary,
            "Kaffee": reg_kaffee.strip() if reg_kaffee.strip() else "Keine Angabe",
            "Allergien": reg_allergien.strip() if reg_allergien.strip() else "Keine",
            "Notizen": reg_notizen.strip(),
            "Anamnese_Text": "Noch nicht vom Admin erhoben.",
            "DSGVO_Akzeptiert": True
        }])
        
        # Verbindung holen und anhängen (append)
        conn = st.connection("gsheets", type=None)
        # Streamlit bietet für gsheets oft '.create' oder wir nutzen direkt ein Update. 
        # Der sicherste Weg über st.connection("gsheets"):
        existing_df = conn.read(worksheet="Kunden")
        updated_df = pd.concat([existing_df, neue_zeile], ignore_index=True)
        conn.update(worksheet="Kunden", data=updated_df)
    except Exception as e:
        st.warning("Hinweis: Kartei lokal erstellt, aber Google-Synchronisation verzögert.")

    st.session_state.user = neuer_name
    st.success("Konto erfolgreich generiert und eingeloggt! Erlebe Redline Studio. 🎉")
    st.rerun()
                        st.session_state.user = neuer_name
                        st.success("Konto erfolgreich generiert und eingeloggt! Erlebe Redline Studio. 🎉")
                        st.rerun()

# ==============================================================================
# 7. ADMIN-DASHBOARD (STRENG GEPRÜFTES KONTROLLZENTRUM)
# ==============================================================================
elif st.session_state.user == "Admin":
    show_logo_and_header()
    
    # Automatische Überprüfung der Material-Grenzwerte
    for produkt, daten in st.session_state.lager_bestand.items():
        if daten["aktuell"] <= daten["limit"]:
            st.markdown(f"""
                <div class='material-alert'>
                    ⚠️ KRITISCHER BESTAND: Das Produkt <strong>{produkt}</strong> unterschreitet das Limit! 
                    Aktueller Vorrat: {daten['aktuell']} {daten['einheit']} (Mindestlimit gesetzt bei: {daten['limit']} {daten['einheit']}). Bitte zeitnah nachbestellen!
                </div>
            """, unsafe_allow_html=True)
    
    # Seitenleiste für administrative Statistiken und Shortcuts
    with st.sidebar:
        st.markdown(f"### 💼 Admin-Modus")
        st.write("Eingeloggt als Haupt-Designerin")
        st.write("---")
        heute_str = datetime.date.today().strftime('%Y-%m-%d')
        termine_heute = len(st.session_state.termine[st.session_state.termine["Datum"] == heute_str]) if not st.session_state.termine.empty else 0
        st.metric(label="Termine am heutigen Tag", value=termine_heute)
        
        st.write("### 📜 Registrierte Kundinnen")
        st.markdown("<div class='scroll-container'>", unsafe_allow_html=True)
        for kunde_name, k_daten in st.session_state.kunden_liste.items():
            st.markdown(f"""
            **👤 {kunde_name}** * ☕ Getränk: {k_daten['Kaffee']}  
            * 📞 Tel: {k_daten['Telefon'] if k_daten['Telefon'] else 'Keine Nummer hinterlegt'}  
            <hr style='margin: 8px 0; border:0; border-top:1px solid #ddd;'>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.write("---")
        if st.button("Sitzung beenden (Abmelden)", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    # Hauptmenü-Tabs des Admin-Bereichs
    menue = st.tabs([
        "🗓️ Kalender & Slots", 
        "👥 Digitale Luxus-Kartei", 
        "📝 Datenschutz & Anamnese-Editor", 
        "📢 Schwarzes Brett & Lager", 
        "🛒 Material-Einkauf & Vergleich", 
        "📄 Dokumente & Quittungen", 
        "📊 Finanzen & Bunte Diagramme",
        "🎨 Studio-Design & Branding"
    ])
    
    # --------------------------------------------------------------------------
    # TAB 1: KALENDER, ZEITEN & ANFRAGEN-FREIGABE
    # --------------------------------------------------------------------------
    with menue[0]:
        st.subheader("🗓️ Slot-Generierung und Terminfreigabe")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            st.markdown("<div class='card'><h4>⏱️ Zeiteinstellungen & Puffer</h4></div>", unsafe_allow_html=True)
            st.session_state.puffer_zeit = st.number_input("Hygiene- & Rüstzeit zwischen Kunden (Minuten)", value=st.session_state.puffer_zeit, step=5)
            st.session_state.neukunden_extra_zeit = st.number_input("⏱️ Extra Beratungs-Zeit für Neukunden-Termine (Minuten)", value=st.session_state.neukunden_extra_zeit, step=5)
            
            st.write("---")
            st.markdown("<h4>Arbeitszeit freigeben</h4>", unsafe_allow_html=True)
            slot_datum = st.date_input("Datum wählen", datetime.date.today(), key="admin_slot_d_c")
            feiertag_name = get_feiertag(slot_datum)
            hinweis_text = feiertag_name if feiertag_name else "-"
            if feiertag_name:
                st.markdown(f"<span style='color: red; font-weight: bold;'>ℹ️ Gesetzlicher Feiertag erkannt: {feiertag_name}</span>", unsafe_allow_html=True)
                
            start_zeit = st.time_input("Startzeit", datetime.time(9, 0))
            end_zeit = st.time_input("Endzeit", datetime.time(18, 0))
            
            if st.button("Arbeits-Slot freigeben", use_container_width=True):
                dauer = (datetime.datetime.combine(slot_datum, end_zeit) - datetime.datetime.combine(slot_datum, start_zeit)).seconds // 60
                if dauer <= 0:
                    st.error("Fehler: Die Endzeit muss chronologisch nach der Startzeit liegen!")
                else:
                    neuer_slot = pd.DataFrame([[slot_datum.strftime('%Y-%m-%d'), start_zeit.strftime('%H:%M'), end_zeit.strftime('%H:%M'), dauer, hinweis_text, "Frei"]], 
                                              columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                    st.session_state.freie_slots = pd.concat([st.session_state.freie_slots, neuer_slot], ignore_index=True)
                    st.success("Arbeitszeit wurde erfolgreich für Kunden zur Buchung freigegeben!")
                    st.rerun()
            
            st.write("---")
            st.markdown("##### Erstellte Arbeitszeitfenster:")
            st.dataframe(st.session_state.freie_slots, use_container_width=True)
            if st.button("Alle Slots unwiderruflich löschen"):
                st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                st.rerun()
                    
        with col_s2:
            st.markdown("<div class='card'><h4>🔮 Eingehende Terminanfragen & Bestätigung</h4></div>", unsafe_allow_html=True)
            
            # Terminfreigabe-Bereich
            if not st.session_state.termine.empty:
                anfragen = st.session_state.termine[st.session_state.termine["Status"] == "Wartet auf Freigabe"]
                if anfragen.empty:
                    st.success("✅ Keine offenen Terminanfragen. Alle Buchungen sind bearbeitet!")
                else:
                    st.info(f"Es liegen {len(anfragen)} offene Buchungsanfragen vor. Bitte prüfen und freigeben:")
                    for idx, row in anfragen.iterrows():
                        neukunden_status_str = "🆕 JA (Extrazeit berechnet)" if row["Ist_Neukunde"] else "👑 Nein (Stammkunde)"
                        st.markdown(f"""
                            <div style='background-color: #f8d7da; padding: 15px; border-radius: 10px; border-left: 5px solid red; margin-bottom: 10px;'>
                                <strong>👤 Kunde: {row['Kunde']}</strong><br>
                                📅 Datum: {row['Datum']} | ⏰ Uhrzeit: {row['Uhrzeit']} Uhr<br>
                                💅 Leistung: {row['Typ']} | ⏱️ Gesamtdauer: {row['Dauer_Gesamt']} Min.<br>
                                🔍 Vom Kunden deklariert als Neukunde? {neukunden_status_str}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        c_acc, c_dec = st.columns(2)
                        if c_acc.button(f"✓ Termin bestätigen##{idx}", key=f"btn_acc_{idx}"):
                            st.session_state.termine.at[idx, "Status"] = "Bestätigt"
                            st.success("Termin wurde offiziell bestätigt!")
                            st.rerun()
                        if c_dec.button(f"✕ Ablehnen & Slot freigeben##{idx}", key=f"btn_dec_{idx}"):
                            st.session_state.termine.drop(idx, inplace=True)
                            st.session_state.termine.reset_index(drop=True, inplace=True)
                            st.warning("Terminanfrage wurde gelöscht.")
                            st.rerun()
            else:
                st.info("Bisher wurden noch keine Termine im System angefragt.")

            st.write("---")
            st.markdown("<h4>📅 Bestätigter Terminkalender</h4>", unsafe_allow_html=True)
            view_mode = st.radio("Kalender-Ansicht:", ["Gesamtübersicht", "Fokus-Tag"], horizontal=True)
            wahl_datum = st.date_input("Fokus-Datum:", datetime.date.today(), key="cal_focus_c")
            
            if not st.session_state.termine.empty:
                st.session_state.termine["Datum_Parsed"] = pd.to_datetime(st.session_state.termine["Datum"]).dt.date
                if view_mode == "Fokus-Tag":
                    aktuelle_termine = st.session_state.termine[(st.session_state.termine["Datum_Parsed"] == wahl_datum) & (st.session_state.termine["Status"] == "Bestätigt")]
                else:
                    aktuelle_termine = st.session_state.termine[st.session_state.termine["Status"] == "Bestätigt"]
            else:
                aktuelle_termine = pd.DataFrame()
                
            if aktuelle_termine.empty:
                st.info("Keine bestätigten Termine für diesen Filter vorhanden.")
            else:
                for _, t in aktuelle_termine.iterrows():
                    bg_color = t['Farbe'] if 'Farbe' in t and t['Farbe'] else st.session_state.color_primary
                    neuk_tag = "🆕 Erstbehandlung" if t.get("Ist_Neukunde", False) else "Stammbehandlung"
                    st.markdown(f"""
                        <div class='calendar-box' style='border-left: 8px solid {bg_color};'>
                            <strong>📅 {t['Datum']} | ⏰ {t['Uhrzeit']} Uhr</strong><br>
                            👤 VIP Kunde: {t['Kunde']} ({neuk_tag})<br>
                            💅 Behandlung: {t['Typ']} (Geplante Blockierung: {t['Dauer_Gesamt']} Min.)
                        </div>
                    """, unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 2: DIGITALE LUXUS-KARTEI (ANAMNESE WIRD VOM ADMIN SELBST GEMACHT)
    # --------------------------------------------------------------------------
    with menue[1]:
        st.subheader("👥 Redline Premium Kundenkartei & Manuelle Anamnese-Führung")
        col_k_liste, col_k_akte = st.columns([1, 2])
        
        with col_k_liste:
            ausgewaehlter_kunde = st.selectbox("Kunden-Akte zur Bearbeitung öffnen:", list(st.session_state.kunden_liste.keys()))
            st.write("---")
            st.markdown("<h4>👤 Neue Kundin manuell anlegen</h4>", unsafe_allow_html=True)
            
            # OPTISCHE UMSTRUKTURIERUNG: Die geforderten Elemente rücken nach links!
            n_name = st.text_input("Vollständiger Name der Kundin")
            
            # 1. OPTISCHE ÄNDERUNG: Individuelle Kalenderfarbe nach links verschoben
            manuelle_farbe = st.color_picker("🎨 Individuelle Kalenderfarbe zuweisen:", st.session_state.color_primary, key="manuelle_farbe_k_links")
            
            # 2. OPTISCHE ÄNDERUNG: Integrierte Foto-Galerie nach links verschoben
            st.markdown("#### 🖼️ Integrierte Foto-Galerie (Modellagen & Fortschritt)")
            hochgeladenes_foto_links = st.file_uploader(
                "Neues Foto direkt aus der Studio-Kamera oder Ordner laden:", 
                type=["jpg", "png", "jpeg", "webp", "gif", "JPG", "JPEG", "PNG", "WEBP", "GIF"], 
                key="img_c_links_manuell"
            )
            
            # Aktions-Button rückt nach ganz unten
            if st.button("Kundin manuell hinzufügen", use_container_width=True):
                if n_name and n_name not in st.session_state.kunden_liste:
                    linke_fotos = [hochgeladenes_foto_links] if hochgeladenes_foto_links else []
                    st.session_state.kunden_liste[n_name.strip()] = {
                        "Telefon": "", "Farbe": manuelle_farbe, "Kaffee": "", "Allergien": "", "Notizen": "", 
                        "Anamnese_Text": "Noch kein Befund eingetragen.", "DSGVO_Akzeptiert": False, "Fotos": linke_fotos
                    }
                    st.success(f"Akte für '{n_name}' wurde erfolgreich angelegt!")
                    st.rerun()
                    
        with col_k_akte:
            if ausgewaehlter_kunde:
                akte = st.session_state.kunden_liste[ausgewaehlter_kunde]
                st.markdown(f"<div class='kunden-akte'><h3>👑 VIP Akte: {ausgewaehlter_kunde}</h3>", unsafe_allow_html=True)
                
                akte["Telefon"] = st.text_input("📞 Hinterlegte Telefonnummer:", akte["Telefon"], key=f"tel_c_{ausgewaehlter_kunde}")
                akte["Kaffee"] = st.text_input("☕ Service-Getränkewunsch:", akte["Kaffee"], key=f"kaf_c_{ausgewaehlter_kunde}")
                akte["Allergien"] = st.text_input("⚠️ Allergien / Chemische Unverträglichkeiten:", akte["Allergien"], key=f"all_c_{ausgewaehlter_kunde}")
                akte["Notizen"] = st.text_area("📝 Styling-Notizen (Form, Stil, Vorlieben):", akte["Notizen"], key=f"not_c_{ausgewaehlter_kunde}")
                
                st.write("---")
                st.markdown("#### 🩺 Medizinische Anamnese (Wird exklusiv von dir ausgefüllt!)")
                st.markdown(f"*Studio-Leitfaden Fragen:*\n`{st.session_state.anamnese_vorlage}`")
                akte["Anamnese_Text"] = st.text_area("Dein professioneller Anamnese-Befund für diese Kundin:", value=akte["Anamnese_Text"], height=150, key=f"anam_k_c_{ausgewaehlter_kunde}")
                
                # UNBERÜHRT: Die DSGVO Checkbox bleibt exakt auf der rechten Seite bestehen
                akte["DSGVO_Akzeptiert"] = st.checkbox("Datenschutzerklärung (DSGVO) liegt physisch oder digital unterschrieben vor", value=akte["DSGVO_Akzeptiert"], key=f"dsgvo_k_c_{ausgewaehlter_kunde}")
                
                st.write("---")
                st.markdown("#### 🖼️ Aktuelle Fotos im Profil")
                
                # Falls in der Akte noch kein Datei-Uploader vorhanden ist für bestehende Konten, hier als Ergänzung
                zusatz_foto = st.file_uploader(
                    "Zusätzliches Foto an diese Akte anhängen:", 
                    type=["jpg", "png", "jpeg", "webp", "gif", "JPG", "JPEG", "PNG", "WEBP", "GIF"], 
                    key=f"img_zusatz_{ausgewaehlter_kunde}"
                )
                if zusatz_foto:
                    if st.button("Zusatzbild in Akte abspeichern", key=f"btn_save_zusatz_{ausgewaehlter_kunde}"):
                        akte["Fotos"].append(zusatz_foto)
                        st.success("Zusätzliches Bild angeheftet!")
                        st.rerun()

                if akte["Fotos"]:
                    cols_img = st.columns(3)
                    for idx, img in enumerate(akte["Fotos"]):
                        cols_img[idx % 3].image(img, use_container_width=True, caption=f"Modellage (Bild {idx+1})")
                st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------------------------------------
    # TAB 3: TEMPLATE-EDITOR FÜR RECHTLICHE UNTERLAGEN
    # --------------------------------------------------------------------------
    with menue[2]:
        st.subheader("📝 Zentrale Formular-Verwaltung & Leitfäden")
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            st.markdown("<div class='card'><h4>📋 Medizinischer Anamnesebogen (Fragen-Leitfaden)</h4></div>", unsafe_allow_html=True)
            neue_anamnese_v = st.text_area("Fragenkatalog für deine Kartei modifizieren:", value=st.session_state.anamnese_vorlage, height=220)
        with col_form2:
            st.markdown("<div class='card'><h4>⚖️ Datenschutzerklärung / DSGVO-Rechtstext</h4></div>", unsafe_allow_html=True)
            neue_dsgvo_v = st.text_area("Gesetzlichen Rechtstext anpassen:", value=st.session_state.datenschutz_vorlage, height=220)
            
        if st.button("✨ Beide Vorlagen studio-weit aktualisieren", use_container_width=True):
            st.session_state.anamnese_vorlage = neue_anamnese_v
            st.session_state.datenschutz_vorlage = neue_dsgvo_v
            st.success("Die Dokumenten-Vorlagen wurden erfolgreich im System aktualisiert!")

    # --------------------------------------------------------------------------
    # TAB 4: SCHWARZES BRETT & AUTOMATISIERTES LAGER
    # --------------------------------------------------------------------------
    with menue[3]:
        st.subheader("📢 Studio-Management & Flexibles Verbrauchslager")
        col_board, col_lager = st.columns([1, 1])
        
        with col_board:
            st.markdown("<div class='card'><h4>📢 Digitales Schwarzes Brett konfigurieren</h4></div>", unsafe_allow_html=True)
            st.session_state.news_aktiv = st.checkbox("Schwarzes Brett auf der Kunden-Startseite einblenden", value=st.session_state.news_aktiv)
            st.session_state.studio_news = st.text_area("News-Aushang Text verfassen:", value=st.session_state.studio_news)
            if st.button("News jetzt veröffentlichen"):
                st.success("Das Schwarze Brett wurde live aktualisiert!")
                st.rerun()
                
            st.write("---")
            st.markdown("<h4>➕ Neues Produkt ins System aufnehmen</h4>", unsafe_allow_html=True)
            neu_prod = st.text_input("Genaue Produktbezeichnung", placeholder="z.B. Farbgel Midnight Glow 15ml")
            
            c_menge, c_einheit = st.columns([2, 1])
            eingabe_menge = c_menge.number_input("Menge / Inhalt bei Einbuchung:", min_value=0.0, value=10.0, step=0.5)
            gewaehlte_einheit = c_einheit.selectbox("Verpackungseinheit:", ["ml", "l (Liter Bulk)", "Stk.", "Rolle"])
            
            if "l (Liter Bulk)" in gewaehlte_einheit:
                berechnete_menge = eingabe_menge * 1000.0
                speicher_einheit = "ml"
            else:
                berechnete_menge = eingabe_menge
                speicher_einheit = gewaehlte_einheit
                
            neu_lim = st.number_input("Sicherheits-Warnlimit (Meldebestand)", min_value=0.0, value=5.0)
            neu_menge = st.number_input(f"Kalkulierter Verbrauch pro Kundin (in {speicher_einheit})", min_value=0.0, value=1.0)
            neu_cost = st.number_input("💰 Einkaufspreis umgerechnet pro Einheit (€):", min_value=0.0, value=0.25, step=0.05)
            
            if st.button("Material dauerhaft registrieren"):
                if neu_prod:
                    st.session_state.lager_bestand[neu_prod] = {
                        "aktuell": berechnete_menge, "limit": neu_lim, "einheit": speicher_einheit, 
                        "auto_abzug": True, "verbrauch_pro_kunde": neu_menge, "kosten_pro_einheit": neu_cost
                    }
                    st.success(f"Das Produkt '{neu_prod}' ist ab sofort einsatzbereit!")
                    st.rerun()
                
        with col_lager:
            st.markdown("<div class='card'><h4>📦 Aktuelle Lagerbestände & Genaue Verbrauchswerte</h4></div>", unsafe_allow_html=True)
            for prod, daten in list(st.session_state.lager_bestand.items()):
                st.write(f"##### 🏷️ {prod} ({daten['einheit']})")
                c1, c2, c3 = st.columns(3)
                
                st.session_state.lager_bestand[prod]["aktuell"] = c1.number_input(f"Ist-Bestand##{prod}", min_value=0.0, value=float(daten["aktuell"]), key=f"ist_{prod}")
                st.session_state.lager_bestand[prod]["verbrauch_pro_kunde"] = c2.number_input(f"Verbrauch/Behandlung##{prod}", min_value=0.0, value=float(daten["verbrauch_pro_kunde"]), key=f"vpr_{prod}")
                st.session_state.lager_bestand[prod]["kosten_pro_einheit"] = c3.number_input(f"Kosten/Einheit in €##{prod}", min_value=0.0, value=float(daten.get("kosten_pro_einheit", 0.10)), key=f"cpe_{prod}")
                
                mat_kosten_pro_kunde = daten["verbrauch_pro_kunde"] * daten.get("kosten_pro_einheit", 0.0)
                st.write(f"💵 *Material-Selbstkostenanteil pro Kundin:* **{mat_kosten_pro_kunde:.2f} €**")
                
                if c1.button(f"Schnell-Aufstockung (+50 / +5)##{prod}"):
                    st.session_state.lager_bestand[prod]["aktuell"] += 50 if daten["einheit"] == "ml" else 5
                    st.rerun()
                st.write("---")

    # --------------------------------------------------------------------------
    # TAB 5: PREISVERGLEICHS-MATRIX FÜR ONLINE-SHOPS
    # --------------------------------------------------------------------------
    with menue[4]:
        st.subheader("🛒 Material-Einkaufskatalog & Live-Markt-Preisvergleich")
        col_cat1, col_cat2 = st.columns([1, 2])
        
        with col_cat1:
            st.markdown("<div class='card'><h4>📸 Lieblingsmaterial / Produkt-Favorit abspeichern</h4></div>", unsafe_allow_html=True)
            mat_name = st.text_input("Produktname / Farbnummer:", placeholder="z.B. Jolifin Base-Gel Ultrabond")
            mat_preis = st.number_input("Bisheriger Richtpreis (€):", min_value=0.0, value=14.95, step=0.5)
            mat_notiz = st.text_area("Hersteller-Infos / Bezugsquelle / Artikelnummer:")
            
            # Explorer-Filter auf Groß-/Kleinschreibung angepasst
            mat_foto = st.file_uploader(
                "Produktbild hinterlegen:", 
                type=["jpg", "png", "jpeg", "webp", "gif", "JPG", "JPEG", "PNG", "WEBP", "GIF"], 
                key="mat_foto_upload_c"
            )
            
            if st.button("Im persönlichen Katalog speichern", use_container_width=True):
                if mat_name:
                    st.session_state.material_katalog.append({
                        "Name": mat_name, "Preis": mat_preis, "Notiz": mat_notiz, "Foto": mat_foto
                    })
                    st.success(f"Das Produkt '{mat_name}' wurde sicher in den Favoriten abgelegt.")
                    st.rerun()
                    
        with col_cat2:
            st.markdown("<div class='card'><h4>🔍 Deine hinterlegten Material-Favoriten</h4></div>", unsafe_allow_html=True)
            if not st.session_state.material_katalog:
                st.info("Dein Einkaufskatalog ist zurzeit leer. Nutze das linke Formular zum Füllen!")
            else:
                for idx, item in enumerate(st.session_state.material_katalog):
                    c_box1, c_box2 = st.columns([1, 3])
                    with c_box1:
                        if item["Foto"] is not None:
                            st.image(item["Foto"], use_container_width=True)
                        else:
                            st.write("🧱 *Kein Produktbild*")
                    with c_box2:
                        st.write(f"##### **{item['Name']}**")
                        st.write(f"💰 **Zielpreis:** {item['Preis']:.2f} € | *Notizen:* {item['Notiz']}")
                        if st.button(f"Produkt entfernen##{idx}", key=f"del_mat_c_{idx}"):
                            st.session_state.material_katalog.pop(idx)
                            st.rerun()
                    st.write("---")
                    
        st.write("---")
        st.markdown("### 🌐 Live-Einkaufs-Matrix & Webseiten-Direktvergleich")
        st.write("Klicke auf den Link, um den jeweiligen Großhändler in einem neuen Tab aufzurufen und Preise abzugleichen:")
        
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.markdown("<div class='vergleichs-box'><h4>🛍️ Jolifin Store</h4><a href='https://www.jolifin.de' target='_blank'>Shop aufrufen ↗️</a>", unsafe_allow_html=True); cc1.number_input("Live-Preis (€):", key="p_s1_c"); cc1.markdown("</div>", unsafe_allow_html=True)
        cc2.markdown("<div class='vergleichs-box'><h4>🛍️ NeoNail</h4><a href='https://www.neonail.de' target='_blank'>Shop aufrufen ↗️</a>", unsafe_allow_html=True); cc2.number_input("Live-Preis (€):", key="p_s2_c"); cc2.markdown("</div>", unsafe_allow_html=True)
        cc3.markdown("<div class='vergleichs-box'><h4>🛍️ LyniNails</h4><a href='https://www.lyni-nails.de' target='_blank'>Shop aufrufen ↗️</a>", unsafe_allow_html=True); cc3.number_input("Live-Preis (€):", key="p_s3_c"); cc3.markdown("</div>", unsafe_allow_html=True)
        cc4.markdown("<div class='vergleichs-box'><h4>🛍️ Amazon Business</h4><a href='https://www.amazon.de' target='_blank'>Shop aufrufen ↗️</a>", unsafe_allow_html=True); cc4.number_input("Live-Preis (€):", key="p_s4_c"); cc4.markdown("</div>", unsafe_allow_html=True)
        
        cc5, cc6, cc7, cc8 = st.columns(4)
        cc5.markdown("<div class='vergleichs-box'><h4>🛍️ Shein Trend-Zubehör</h4><a href='https://de.shein.com' target='_blank'>Shop aufrufen ↗️</a>", unsafe_allow_html=True); cc5.number_input("Live-Preis (€):", key="p_s5_c"); cc5.markdown("</div>", unsafe_allow_html=True)
        cc6.markdown("<div class='vergleichs-box'><h4>🛍️ AliExpress Wholesale</h4><a href='https://de.aliexpress.com' target='_blank'>Shop aufrufen ↗️</a>", unsafe_allow_html=True); cc6.number_input("Live-Preis (€):", key="p_s6_c"); cc6.markdown("</div>", unsafe_allow_html=True)
        cc7.write("") 
        cc8.write("") 

    # --------------------------------------------------------------------------
    # TAB 6: BEARBEITBARE DIGITALE RECHNUNGEN & PROTOKOLLE
    # --------------------------------------------------------------------------
    with menue[5]:
        st.subheader("📄 Bearbeitbare Quittungen & Automatisierte Material-Anrechnung")
        col_pdf_f, col_pdf_v = st.columns([1, 2])
        
        # Errechnen der exakten Materialkosten pro Behandlung
        gesamte_studiomaterial_kosten = 0.0
        for p, d in st.session_state.lager_bestand.items():
            gesamte_studiomaterial_kosten += (d["verbrauch_pro_kunde"] * d.get("kosten_pro_einheit", 0.0))
            
        with col_pdf_f:
            st.markdown("<div class='card'><h4>Rechnungs-Generator Konfiguration</h4></div>", unsafe_allow_html=True)
            doc_kunde = st.selectbox("Kundin auswählen:", list(st.session_state.kunden_liste.keys()), key="doc_k_c")
            doc_art = st.selectbox("Erbrachte Leistung:", list(st.session_state.zeiten_naegel.keys()), key="doc_a_c")
            doc_basispreis = st.number_input("Dienstleistungspreis (Arbeitswert in €):", min_value=0.0, value=65.0, step=5.0)
            
            anrechnen = st.checkbox("Ermittelte Materialkosten addieren & transparent ausweisen?", value=True)
            effektive_materialkosten = gesamte_studiomaterial_kosten if anrechnen else 0.0
            
            st.write(f"ℹ️ *Ermittelter realer Materialwert für diese Behandlung:* **{effektive_materialkosten:.2f} €**")
            end_gesamtpreis = doc_basispreis + effektive_materialkosten
            st.write(f"🎯 **Rechnungs-Endsumme:** {end_gesamtpreis:.2f} €")
            
            doc_datum = st.date_input("Ausstellungsdatum", datetime.date.today(), key="doc_d_c")
            doc_typ = st.radio("Dokumententyp festlegen:", ["Professionelle Quittung", "Einverständniserklärung / Modellage-Protokoll"], horizontal=True)
            
            if st.button("Dokument generieren", use_container_width=True):
                if st.session_state.uploaded_logo is not None:
                    try:
                        bytes_logo = st.session_state.uploaded_logo.getvalue()
                        base64_logo = base64.b64encode(bytes_logo).decode()
                        logo_html = f"<img src='data:image/jpeg;base64,{base64_logo}' style='max-height: 70px; float: right; border-radius: 8px;'>"
                    except Exception:
                        logo_html = ""
                else:
                    logo_html = ""

                if "Professionelle Quittung" in doc_typ:
                    st.session_state.pdf_view = f"""
                        <div class='pdf-frame'>
                            {logo_html}
                            <h1 style='color: {st.session_state.color_primary}; margin:0;'>Redline Studio</h1>
                            <p style='margin:0; font-size:0.9em;'>Exklusives Nageldesign & Kosmetik</p>
                            <hr style='border: 1px solid {st.session_state.color_primary}; margin: 15px 0;'>
                            <h2 style='text-align: center;'>OFFIZIELLE QUITTUNG / BELEG</h2>
                            <p><strong>Rechnungsnummer:</strong> RE-{datetime.date.today().strftime('%Y%m%d')}-{doc_kunde[:3].upper()}</p>
                            <p><strong>Rechnungsdatum:</strong> {doc_datum.strftime('%d.%m.%Y')}</p>
                            <p><strong>Leistungsempfänger (Kunde):</strong> {doc_kunde}</p>
                            <table style='width:100%; border-collapse: collapse; margin-top:25px;'>
                                <tr style='border-bottom: 2px solid #333; font-weight:bold;'>
                                    <td style='padding: 8px 0;'>Position / Beschreibung</td>
                                    <td style='text-align:right; padding: 8px 0;'>Betrag</td>
                                </tr>
                                <tr style='border-bottom: 1px solid #ddd;'>
                                    <td style='padding: 10px 0;'>Dienstleistung ({doc_art})</td>
                                    <td style='text-align:right;'>{doc_basispreis:.2f} €</td>
                                </tr>
                                <tr style='border-bottom: 1px solid #333;'>
                                    <td style='padding: 10px 0;'>Material- & Produktverbrauchspauschale</td>
                                    <td style='text-align:right;'>{effektive_materialkosten:.2f} €</td>
                                </tr>
                                <tr style='font-weight: bold; font-size:1.3em;'>
                                    <td style='padding: 15px 0;'>Gesamtsumme (Bar / Unbar bezahlt):</td>
                                    <td style='text-align:right; padding: 15px 0; color:{st.session_state.color_primary};'>{end_gesamtpreis:.2f} €</td>
                                </tr>
                            </table>
                            <p style='font-style: italic; font-size: 0.85em; margin-top:50px;'>Hinweis: Als Kleinunternehmer im Sinne von § 19 Abs. 1 UStG wird keine Umsatzsteuer berechnet und ausgewiesen.</p>
                            <p style='text-align:center; font-weight:bold; margin-top:20px;'>Vielen Dank für dein Vertrauen! Bis zum nächsten Mal! 💅✨</p>
                        </div>
                    """
                else:
                    st.session_state.pdf_view = f"""
                        <div class='pdf-frame'>
                            {logo_html}
                            <h1 style='color: {st.session_state.color_primary}; margin:0;'>Redline Studio</h1>
                            <hr style='border: 1px solid {st.session_state.color_primary}; margin: 15px 0;'>
                            <h2 style='text-align: center;'>Einverständniserklärung & Behandlungsprotokoll</h2>
                            <p><strong>Datum der Behandlung:</strong> {doc_datum.strftime('%d.%m.%Y')}</p>
                            <p><strong>Kunde:</strong> {doc_kunde}</p>
                            <p><strong>Art der Modellage:</strong> {doc_art}</p>
                            <p style='margin-top:25px; line-height:1.5;'>
                                Ich bestätige hiermit, vor der heutigen kosmetischen Nagelbehandlung ausführlich über den Ablauf, 
                                die verwendeten Materialien sowie mögliche Kontraindikationen aufgeklärt worden zu sein. 
                                Die Pflegehinweise zur optimalen Haltbarkeit der Modellage wurden mir ausgehändigt.
                            </p>
                            <br><br>
                            <div style='display: flex; justify-content: space-between; margin-top:60px;'>
                                <div>_________________________________<br><span style='font-size: 0.85em;'>Rechtsverbindliche Unterschrift Kunde</span></div>
                                <div>_________________________________<br><span style='font-size: 0.85em;'>Unterschrift Redline Studio</span></div>
                            </div>
                        </div>
                    """
                st.rerun()
        with col_pdf_v:
            if 'pdf_view' in st.session_state: 
                st.markdown(st.session_state.pdf_view, unsafe_allow_html=True)
            else:
                st.info("Konfiguriere links die Daten und klicke auf 'Dokument generieren', um die Vorschau anzuzeigen.")

    # --------------------------------------------------------------------------
    # TAB 7: FINANZEN & METRIKEN
    # --------------------------------------------------------------------------
    with menue[6]:
        st.subheader("📊 Studio-Finanzen & Bunte Live-Diagramme")
        if not st.session_state.finanzen.empty:
            einnahmen = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Einnahme"]["Betrag (€)"].sum()
            ausgaben = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Ausgabe"]["Betrag (€)"].sum()
            gewinn = einnahmen - ausgaben
        else:
            einnahmen, ausgaben, gewinn = 0.0, 0.0, 0.0
            
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Verbuchte Gesamteinnahmen", f"{einnahmen:.2f} €")
        c_m2.metric("Verbuchte Gesamtausgaben", f"{ausgaben:.2f} €")
        c_m3.metric("Errechneter Reingewinn", f"{gewinn:.2f} €", delta=f"{gewinn:.2f} €")
        
        st.write("---")
        col_f1, col_f2 = st.columns([1, 1])
        
        with col_f1:
            st.markdown("<h4>Transaktion manuell buchen</h4>", unsafe_allow_html=True)
            f_datum = st.date_input("Buchungsdatum", datetime.date.today(), key="fin_d_c")
            f_typ = st.selectbox("Buchungsart", ["Einnahme", "Ausgabe"])
            f_kat = st.selectbox("Buchungskategorie", ["Neumodellage", "Auffüllen", "Design-Extra", "Materialeinkauf", "Miete/Strom", "Werbung", "Sonstiges"])
            f_betrag = st.number_input("Transaktionsbetrag in €", min_value=0.0, step=5.0)
            
            if st.button("Transaktion fest verbuchen"):
                neuer_eintrag = pd.DataFrame([[f_datum.strftime('%Y-%m-%d'), f_typ, f_kat, f_betrag]], columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
                st.session_state.finanzen = pd.concat([st.session_state.finanzen, neuer_eintrag], ignore_index=True)
                st.success("Die Transaktion wurde erfolgreich in die Buchführung aufgenommen!")
                st.rerun()
                
            st.write("---")
            st.write("**Einzelbuchungen im Journal:**")
            st.dataframe(st.session_state.finanzen, use_container_width=True)
        
        with col_f2:
            st.markdown("<h4>📈 Visualisierte Umsatz-Auswertungen</h4>", unsafe_allow_html=True)
            if not st.session_state.finanzen.empty:
                st.write("**Gegenüberstellung (Einnahmen vs. Ausgaben):**")
                st.bar_chart(data=st.session_state.finanzen, x="Typ", y="Betrag (€)", color="Typ", use_container_width=True)
                
                einnahmen_df = st.session_state.finanzen[st.session_state.finanzen["Typ"] == "Einnahme"]
                if not einnahmen_df.empty:
                    st.write("**Umsatzverteilung nach Kategorie:**")
                    st.bar_chart(data=einnahmen_df, x="Kategorie", y="Betrag (€)", color="Kategorie", use_container_width=True)
            else:
                st.info("Sobald die ersten Transaktionen gebucht wurden, erscheinen hier aussagekräftige Business-Diagramme!")

    # --------------------------------------------------------------------------
    # TAB 8: BRANDING & DESIGN-PARADIES (LOGO- UND BACKGROUND-UPLOAD)
    # --------------------------------------------------------------------------
    with menue[7]:
        st.subheader("🎨✨ Willkommen im Redline Design-Paradies! ✨🌈🔮")
        st.markdown("""
            <div style='background: linear-gradient(45deg, #FFDEE9 0%, #B5FFFC 100%); padding: 25px; border-radius: 15px; border: 3px dashed #FF1493; text-align: center;'>
                <h3 style='color: #FF1493 !important; margin: 0; font-weight:bold;'>🥰 Gestalte dein eigenes Traum-Studio 🥰</h3>
                <p style='color: #4A3737 !important; font-size: 1.15rem; margin: 8px 0 0 0;'>Lade dein Logo und deine Hintergrundbilder hoch. Alle Formate werden jetzt problemlos erkannt! 💅💖⭐</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        col_up1, col_up2 = st.columns(2)
        
        with col_up1:
            st.markdown("### 👑 Foto-Upload: Dein Studio-Logo")
            
            # Filter komplett für Groß- und Kleinschreibung konfiguriert
            uploaded_logo_file = st.file_uploader(
                "Wähle dein Logo-Bild von deinem Gerät aus 📸", 
                type=["jpg", "png", "jpeg", "webp", "gif", "JPG", "JPEG", "PNG", "WEBP", "GIF"], 
                key="design_logo_uploader_c"
            )
            if uploaded_logo_file is not None:
                st.session_state.uploaded_logo = uploaded_logo_file
                st.success("🎉 Genial! Dein Logo wurde geladen und strahlt jetzt ganz oben im System!")
                
        with col_up2:
            st.markdown("### 🖼️ Foto-Upload: Dein App-Hintergrund")
            
            # Filter komplett für Groß- und Kleinschreibung konfiguriert
            uploaded_bg_file = st.file_uploader(
                "Wähle dein tolles Rosé-Hintergrundbild aus ✨", 
                type=["jpg", "png", "jpeg", "webp", "gif", "JPG", "JPEG", "PNG", "WEBP", "GIF"], 
                key="design_bg_uploader_c"
            )
            if uploaded_bg_file is not None:
                st.session_state.uploaded_bg = uploaded_bg_file
                st.success("🌈 Wunderschön! Das Hintergrundbild wurde im System verankert!")

        st.write("---")
        st.session_state.use_background_image = st.checkbox(
            "🖼️ Das hochgeladene Hintergrundbild aktiv im Studio-Hintergrund einblenden", 
            value=st.session_state.use_background_image
        )
        
        st.write("---")
        auswahl_design = st.radio(
            "🎈 Vordefinierte Farbwelten (Schnell-Auswahl):",
            ["Rosé-Gold Luxus (Perfekt für dein Bild) 🥰", "Klassisches Weinrot 🍷", "Völlig freie Farbgestaltung (Custom Mischer) 🎨🌈"],
            horizontal=True
        )
        
        if "Rosé-Gold Luxus" in auswahl_design:
            st.session_state.color_bg = "#FFF5F5"
            st.session_state.color_primary = "#D4A3A3"
            st.session_state.color_accent = "#D4AF37"
            st.session_state.color_text = "#4A3737"
        
        elif "Klassisches Weinrot" in auswahl_design:
            st.session_state.color_bg = "#ffffff"
            st.session_state.color_primary = "#721c24"
            st.session_state.color_accent = "#d4af37"
            st.session_state.color_text = "#333333"
            
        elif "Völlig freie Farbgestaltung" in auswahl_design:
            st.write("---")
            st.markdown("##### 🎛️ Eigener Farbmischer (Bewege die Regler nach deinen Wünschen):")
            c_p1, c_p2, c_p3, c_p4 = st.columns(4)
            st.session_state.color_bg = c_p1.color_picker("Hintergrundfarbe (Fallback):", st.session_state.color_bg)
            st.session_state.color_primary = c_p2.color_picker("Hauptfarbe (Header/Klickflächen):", st.session_state.color_primary)
            st.session_state.color_accent = c_p3.color_picker("Akzentfarbe (Glanz/Linien/Gold):", st.session_state.color_accent)
            st.session_state.color_text = c_p4.color_picker("Textfarbe (Für alle Beschriftungen):", st.session_state.color_text)

        if st.button("✨ Alle Design-Anpassungen sofort live speichern! 💖", use_container_width=True):
            st.success("💎 Ausgezeichnet! Dein Studio-Branding wurde erfolgreich übernommen!")
            st.rerun()

# ==============================================================================
# 8. KUNDEN-BUCHUNGSBEREICH (DIE KUNDEN-ANSICHT)
# ==============================================================================
else:
    show_logo_and_header()
    
    with st.sidebar:
        st.markdown(f"### 🌸 Kunden-Bereich")
        st.write(f"Eingeloggt als: **{st.session_state.user}**")
        st.write("---")
        st.markdown("##### ☕ Deine hinterlegten Präferenzen:")
        st.write(f"**Getränkewunsch:** {st.session_state.kunden_liste[st.session_state.user]['Kaffee']}")
        st.write(f"**Allergie-Hinweis:** {st.session_state.kunden_liste[st.session_state.user]['Allergien']}")
        st.write("---")
        if st.button("Sitzung beenden (Abmelden)", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    st.subheader("🗓️ Buche jetzt deinen Wunschtermin im Redline Studio")
    
    # Der Kunde wählt die gewünschte Nagelbehandlung aus
    nagel_wunsch = st.selectbox("Wähle deine gewünschte Behandlung aus:", list(st.session_state.zeiten_naegel.keys()))
    
    # KUNDE ENTSCHEIDET SELBST: Das Feld ist wieder da und steuert die Logik!
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    ist_neukunde_haken = st.checkbox("✨ Ich bin Neukunde in diesem Studio (Aktiviert automatische Erstberatungszeit)", value=False)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Berechnen der benötigten Zeitsegmente anhand der Auswahl des Kunden
    basis_zeit = st.session_state.zeiten_naegel[nagel_wunsch]
    aufgeschlagene_zeit = st.session_state.neukunden_extra_zeit if ist_neukunde_haken else 0
    gesamte_blockade_zeit = basis_zeit + aufgeschlagene_zeit + st.session_state.puffer_zeit
    
    st.info(f"Eingeplante Nettozeit: {basis_zeit} Min. " + (f"+ {aufgeschlagene_zeit} Min. für deine Erstberatung!" if ist_neukunde_haken else "") + f" (Zuzüglich {st.session_state.puffer_zeit} Min. Pufferzeit für Hygiene).")
    
    # Anzeigen der vom Admin freigegebenen Arbeits-Slots
    if "freie_slots" in st.session_state and not st.session_state.freie_slots.empty:
        freie_anzeige = st.session_state.freie_slots[st.session_state.freie_slots["Status"] == "Frei"]
    else:
        freie_anzeige = pd.DataFrame()
        
    if freie_anzeige.empty:
        st.warning("Zurzeit sind leider keine freien Terminfenster freigeschaltet. Bitte kontaktiere das Studio telefonisch!")
    else:
        st.markdown("#### Verfügbare Terminfenster:")
        for idx, row in freie_anzeige.iterrows():
            verfuegbare_minuten = int(row["Dauer_Minuten"])
            
            # Prüfen, ob das freie Zeitfenster groß genug für die Behandlung inklusive Puffer ist
            if verfuegbare_minuten >= gesamte_blockade_zeit:
                col_slot, col_buch_btn = st.columns([3, 1])
                feiertags_tag = f" ({row['Feiertag-Hinweis']})" if row['Feiertag-Hinweis'] != "-" else ""
                col_slot.write(f"📅 **{row['Datum']}** | ⏰ Zeitrahmen: {row['Startzeit']} bis {row['Endzeit']} Uhr{feiertags_tag}")
                
                if col_buch_btn.button("Terminanfrage senden", key=f"book_c_{idx}"):
                    # Der Arbeits-Slot wird im System als reserviert bzw. blockiert markiert
                    st.session_state.freie_slots.at[idx, "Status"] = "In Prüfung"
                    
                    # Automatischer Produkt-Abzug aus dem Lagerbestand bei Buchung
                    for prod, daten in st.session_state.lager_bestand.items():
                        if daten["auto_abzug"] and daten["aktuell"] > 0:
                            st.session_state.lager_bestand[prod]["aktuell"] = max(0.0, daten["aktuell"] - daten["verbrauch_pro_kunde"])
                    
                    # Einpflegen in die Termin-Datenbank mit dem Status "Wartet auf Freigabe"
                    kunden_farbe = st.session_state.kunden_liste[st.session_state.user]["Farbe"]
                    neuer_termin = pd.DataFrame(
                        [[row['Datum'], row['Startzeit'], st.session_state.user, nagel_wunsch, gesamte_blockade_zeit, kunden_farbe, "Wartet auf Freigabe", ist_neukunde_haken]], 
                        columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe", "Status", "Ist_Neukunde"]
                    )
                    st.session_state.termine = pd.concat([st.session_state.termine, neuer_termin], ignore_index=True)
                    
                    st.success("🎉 Deine Terminanfrage wurde erfolgreich an das Studio übermittelt! Sobald das Studio den Termin geprüft und freigegeben hat, siehst du ihn als bestätigt.")
                    st.rerun()



