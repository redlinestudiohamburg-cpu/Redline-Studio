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

# 🌐 DEIN REINER LOGO-DIREKTLINK:
LOGO_URL = "https://i.ibb.co/L5rCByH/1000083359.png"

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
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 25px;
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
    .main-logo-img {
        max-height: 90px;
        border-radius: 50%;
        border: 2px solid #d4af37;
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
    .holiday-text {
        color: #721c24;
        font-weight: bold;
        background-color: #f8d7da;
        padding: 8px;
        border-radius: 5px;
        display: block;
        margin-bottom: 15px;
    }
    .calendar-box {
        border: 1px solid #721c24;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        color: white;
    }
    .pdf-frame {
        border: 2px solid #721c24;
        padding: 20px;
        background-color: white;
        color: black;
        font-family: 'Courier New', monospace;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# --- FEIERTAGE-BERECHNER ---
def get_feiertag(datum):
    jahr = datum.year
    feste = {
        (1, 1): "Neujahr",
        (6, 1): "Heilige Drei Könige",
        (1, 5): "Tag der Arbeit",
        (1, 8): "Schweizer Nationalfeiertag",
        (3, 10): "Tag der Deutschen Einheit",
        (26, 10): "Nationalfeiertag (AT)",
        (1, 11): "Allerheiligen",
        (25, 12): "1. Weihnachtstag",
        (26, 12): "2. Weihnachtstag"
    }
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
    karfreitag = oster_datum - datetime.timedelta(days=2)
    ostermontag = oster_datum + datetime.timedelta(days=1)
    auffahrt = oster_datum + datetime.timedelta(days=39)
    pfingstmontag = oster_datum + datetime.timedelta(days=50)
    
    if datum == karfreitag: return "Karfreitag"
    if datum == oster_datum: return "Ostersonntag"
    if datum == ostermontag: return "Ostermontag"
    if datum == auffahrt: return "Auffahrt / Himmelfahrt"
    if datum == pfingstmontag: return "Pfingstmontag"
    if (datum.day, datum.month) in feste:
        return feste[(datum.day, datum.month)]
    return None

# --- INITIALISIERUNG DER DATEN-SPEICHER ---
if 'user' not in st.session_state: st.session_state.user = None
if 'zeiten_naegel' not in st.session_state:
    st.session_state.zeiten_naegel = {"Neumodellage": 120, "Auffüllen": 90, "French / Extra Design": 45}
if 'puffer_zeit' not in st.session_state: st.session_state.puffer_zeit = 15
if 'kunden_spalten' not in st.session_state: st.session_state.kunden_spalten = ["Kunden-Name", "Telefonnummer", "Notizen", "Farbe"]
if 'kunden' not in st.session_state: st.session_state.kunden = pd.DataFrame(columns=st.session_state.kunden_spalten)
if 'freie_slots' not in st.session_state: st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
if 'termine' not in st.session_state: st.session_state.termine = pd.DataFrame(columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe"])
if 'finanzen' not in st.session_state: st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])

# --- FUNKTION: DYNAMISCHER HEADER MIT LOGO ---
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
                st.rerun()

# --- BEREICH: ADMIN-DASHBOARD ---
elif st.session_state.user == "Admin":
    show_logo_and_header()
    
    with st.sidebar:
        st.write(f"Angemeldet als: **{st.session_state.user}**")
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    menue = st.tabs(["🗓️ Kalender & Slots", "⚙️ Nagel-Zeiten & Puffer", "👥 Kundenkartei", "📄 Dokumente & Quittungen", "📊 Finanzen"])
    
    # TAB 1: KALENDER & ARBEITSZEITEN
    with menue[0]:
        st.subheader("🗓️ Arbeitszeiten & Kalenderübersicht")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            st.markdown("<div class='card'><h4>Slot freigeben</h4></div>", unsafe_allow_html=True)
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
            if st.button("Alle Slots zurücksetzen"):
                st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                st.rerun()
                    
        with col_s2:
            st.markdown("<div class='card'><h4>🔮 Visueller Terminkalender</h4></div>", unsafe_allow_html=True)
            view_mode = st.radio("Ansichtsmodus:", ["Monat", "Tag"], horizontal=True)
            wahl_datum = st.date_input("Kalender-Fokus auf:", datetime.date.today(), key="cal_focus")
            
            st.write("### Termine in der Übersicht:")
            if not st.session_state.termine.empty:
                st.session_state.termine["Datum_Parsed"] = pd.to_datetime(st.session_state.termine["Datum"]).dt.date
                if view_mode == "Tag":
                    aktuelle_termine = st.session_state.termine[st.session_state.termine["Datum_Parsed"] == wahl_datum]
                else:
                    aktuelle_termine = st.session_state.termine[
                        (pd.to_datetime(st.session_state.termine["Datum"]).dt.month == wahl_datum.month) & 
                        (pd.to_datetime(st.session_state.termine["Datum"]).dt.year == wahl_datum.year)
                    ]
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

    # TAB 2: NAGEL-ZEITEN & NEUE ARTEN
    with menue[1]:
        st.subheader("⚙️ Behandlungsdauer & Nagel-Arten verwalten")
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            st.markdown("<div class='card'><h4>➕ Neue Nagel-Art hinzufügen</h4></div>", unsafe_allow_html=True)
            neue_art_name = st.text_input("Name der neuen Behandlung", placeholder="z.B. Acryl Verlängerung")
            neue_art_dauer = st.number_input("Dauer in Minuten", min_value=5, value=60, step=5)
            
            if st.button("💅 Neue Behandlung speichern", use_container_width=True):
                if neue_art_name:
                    st.session_state.zeiten_naegel[neue_art_name.strip()] = neue_art_dauer
                    st.success(f"'{neue_art_name}' wurde hinzugefügt!")
                    st.rerun()
            
            st.write("### Aktuell verfügbare Behandlungen:")
            for art, dauer in list(st.session_state.zeiten_naegel.items()):
                st.session_state.zeiten_naegel[art] = st.number_input(f"Dauer für: {art} (Min)", value=int(dauer), step=5, key=f"edit_{art}")
        with col_z2:
            st.markdown("<div class='card'><h4>🧼 Desinfektion & Aufbereitung</h4></div>", unsafe_allow_html=True)
            st.session_state.puffer_zeit = st.number_input("Pufferzeit zwischen Kunden (Minuten)", value=st.session_state.puffer_zeit, step=5)

    # TAB 3: KUNDENKARTEI
    with menue[2]:
        st.subheader("👥 Digitale Kundenkartei (Erweiterbar)")
        col_k_form, col_k_view = st.columns([1, 2])
        with col_k_form:
            st.markdown("<div class='card'><h4>➕ Neue Tabellen-Spalte hinzufügen</h4></div>", unsafe_allow_html=True)
            neue_spalte = st.text_input("Name für neues Datenfeld", placeholder="z.B. Instagram, Allergien")
            if st.button("➕ Spalte der Kartei hinzufügen", use_container_width=True):
                if neue_spalte and neue_spalte not in st.session_state.kunden_spalten:
                    st.session_state.kunden_spalten.append(neue_spalte.strip())
                    st.session_state.kunden[neue_spalte.strip()] = ""
                    st.success(f"Spalte '{neue_spalte}' hinzugefügt!")
                    st.rerun()
            
            st.write("---")
            st.markdown("<div class='card'><h4>👤 Neuen Kunden anlegen</h4></div>", unsafe_allow_html=True)
            kunden_daten = {}
            for spalte in st.session_state.kunden_spalten:
                if spalte == "Farbe":
                    kunden_daten[spalte] = st.color_picker("🎨 Erkennungs-Farbe für Kalender", "#721c24")
                elif spalte == "Notizen":
                    kunden_daten[spalte] = st.text_area(spalte)
                else:
                    kunden_daten[spalte] = st.text_input(spalte)
                    
            if st.button("Kunde abspeichern", use_container_width=True):
                if kunden_daten.get("Kunden-Name") == "":
                    st.error("Bitte mindestens den Kunden-Namen eingeben!")
                else:
                    neuer_kunde = pd.DataFrame([kunden_daten], columns=st.session_state.kunden_spalten)
                    st.session_state.kunden = pd.concat([st.session_state.kunden, neuer_kunde], ignore_index=True)
                    st.success("Kunde erfolgreich gesichert!")
                    st.rerun()
        with col_k_view:
            st.dataframe(st.session_state.kunden, use_container_width=True)

    # TAB 4: DOKUMENTE & QUITTUNGEN (Mit Logo!)
    with menue[3]:
        st.subheader("📄 Professionelle Dokumente erstellen")
        col_pdf_f, col_pdf_v = st.columns([1, 2])
        with col_pdf_f:
            st.markdown("<div class='card'><h4>Dokumenten-Konfigurator</h4></div>", unsafe_allow_html=True)
            if st.session_state.kunden.empty:
                st.warning("Keine Kunden in der Kartei!")
            else:
                doc_kunde = st.selectbox("Wähle einen Kunden:", st.session_state.kunden["Kunden-Name"])
                doc_art = st.selectbox("Behandlung:", list(st.session_state.zeiten_naegel.keys()))
                doc_datum = st.date_input("Datum", datetime.date.today())
                doc_preis = st.number_input("Beitrag in €", min_value=0.0, step=0.5)
                doc_typ = st.radio("Dokumententyp:", ["Professionelle Quittung", "Einverständniserklärung"], horizontal=True)
                
                if st.button("Dokument generieren", use_container_width=True):
                    logo_html = f"<img src='{LOGO_URL}' style='max-height: 60px; float: right; border-radius: 50%;' onerror='this.style.display=\"none\"'>"
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
            if 'pdf_view' in st.session_state:
                st.markdown(st.session_state.pdf_view, unsafe_allow_html=True)

    # TAB 5: FINANZEN
    with menue[4]:
        st.subheader("📊 Finanzen")
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            f_datum = st.date_input("Datum", datetime.date.today(), key="fin_d")
            f_typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
            f_kat = st.text_input("Kategorie")
            f_betrag = st.number_input("Betrag in €", min_value=0.0)
            if st.button("Eintrag Speichern"):
                neuer_eintrag = pd.DataFrame([[f_datum, f_typ, f_kat, f_betrag]], columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
                st.session_state.finanzen = pd.concat([st.session_state.finanzen, neuer_eintrag], ignore_index=True)
                st.rerun()
        with col_f2:
            st.dataframe(st.session_state.finanzen, use_container_width=True)

# --- SEITE: KUNDEN-BUCHUNG ---
else:
    show_logo_and_header()
    with st.sidebar:
        st.write(f"Willkommen, **{st.session_state.user}**!")
        if st.button("Abmelden"):
            st.session_state.user = None
            st.rerun()
            
    st.subheader("🗓️ Wähle deinen Wunschtermin")
    nagel_wunsch = st.selectbox("Was möchtest du machen lassen?", list(st.session_state.zeiten_naegel.keys()))
    benoetigte_zeit = st.session_state.zeiten_naegel[nagel_wunsch]
    gesamte_blockade_zeit = benoetigte_zeit + st.session_state.puffer_zeit
    
    st.info(f"Für {nagel_wunsch} werden {benoetigte_zeit} Minuten eingeplant.")
    
    freie_anzeige = st.session_state.freie_slots[st.session_state.freie_slots["Status"] == "Frei"]
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
                    kunden_farbe = "#721c24"
                    if not st.session_state.kunden.empty:
                        treffer = st.session_state.kunden[st.session_state.kunden["Kunden-Name"] == st.session_state.user]
                        if not treffer.empty: kunden_farbe = treffer.iloc[0]["Farbe"]
                    
                    neuer_termin = pd.DataFrame([[row['Datum'], row['Startzeit'], st.session_state.user, nagel_wunsch, gesamte_blockade_zeit, kunden_farbe]], 
                                                columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt", "Farbe"])
                    st.session_state.termine = pd.concat([st.session_state.termine, neuer_termin], ignore_index=True)
                    st.success("Erfolgreich gebucht! 🎉")
                    st.rerun()
