import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import os

# --- SEITENKONFIGURATION ---
st.set_page_config(
    page_title="Redline Studio Pro - Dashboard",
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
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
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
        max-height: 80px;
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
        (1, 5): "Tag der Arbeit",
        (1, 8): "Schweizer Nationalfeiertag",
        (3, 10): "Tag der Deutschen Einheit",
        (25, 12): "1. Weihnachtstag",
        (26, 12): "2. Weihnachtstag"
    }
    # Einfache Osterberechnung (für CH/DE Feiertage)
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
    pfingstmontag = oster_datum + datetime.timedelta(days=50)
    
    if datum == karfreitag: return "Karfreitag"
    if datum == pfingstmontag: return "Pfingstmontag"
    if (datum.day, datum.month) in feste: return feste[(datum.day, datum.month)]
    return None

# --- INITIALISIERUNG DER DATEN-SPEICHER ---
if 'user' not in st.session_state: st.session_state.user = None
if 'zeiten_naegel' not in st.session_state: st.session_state.zeiten_naegel = {"Neumodellage": 120, "Auffüllen": 90}
if 'kunden' not in st.session_state: st.session_state.kunden = pd.DataFrame(columns=["Kunden-Name", "Telefonnummer", "Notizen"])
if 'freie_slots' not in st.session_state: st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
if 'termine' not in st.session_state: st.session_state.termine = pd.DataFrame(columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt"])
if 'finanzen' not in st.session_state: st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])

# --- FUNKTION: LOGO LADEN ---
def show_logo_and_header():
    # Suche nach 'redline-logo.png' im gleichen Ordner wie die Python-Datei
    logo_filename = "redline-logo.png"
    if os.path.exists(logo_filename):
        image = Image.open(logo_filename)
        # HTML mit Logo und Text
        st.markdown(f"""
            <div class='main-header'>
                <img src='file://{logo_filename}' class='main-logo-img'>
                <h1>Redline Studio</h1>
                <p>Kreativität & Eleganz</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        # Standard-Header, wenn kein Logo da ist
        st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Kreativität & Eleganz</p></div>", unsafe_allow_html=True)

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

# --- BEREICH: ADMIN-DASHBOARD (Professional Edition) ---
elif st.session_state.user == "Admin":
    show_logo_and_header()
    
    with st.sidebar:
        st.write(f"Logged in als: **{st.session_state.user}**")
        if st.button("Abmelden", use_container_width=True):
            st.session_state.user = None
            st.rerun()
            
    menue = st.tabs(["🗓️ Kalender & Slots", "👥 Kundenkartei", "📄 Dokumente & Quittungen", "📊 Finanzen", "⚙️ Nagel-Zeiten"])
    
    # TAB 1: KALENDER & SLOTS FREIGEBEN
    with menue[0]:
        st.subheader("🗓️ Deine Arbeitszeiten freischalten")
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            st.markdown("<div class='card'><h4>Slot freigeben</h4></div>", unsafe_allow_html=True)
            slot_datum = st.date_input("Datum wählen", datetime.date.today(), key="admin_d")
            
            feiertag_name = get_feiertag(slot_datum)
            hinweis_text = "-"
            if feiertag_name:
                st.markdown(f"<span class='holiday-text'>ℹ️ Hinweis: An diesem Tag ist {feiertag_name}. (Flexibel buchbar)</span>", unsafe_allow_html=True)
                hinweis_text = feiertag_name
            
            st.write("Zeitangebot:")
            start_zeit = st.time_input("Von", datetime.time(14, 0))
            end_zeit = st.time_input("Bis", datetime.time(17, 0))
            
            if st.button("Zeitraum freistellen", use_container_width=True):
                dauer = (datetime.datetime.combine(slot_datum, end_zeit) - datetime.datetime.combine(slot_datum, start_zeit)).seconds // 60
                if dauer <= 0: st.error("Endzeit nach Startzeit!")
                else:
                    neuer_slot = pd.DataFrame([[slot_datum.strftime('%Y-%m-%d'), start_zeit.strftime('%H:%M'), end_zeit.strftime('%H:%M'), dauer, hinweis_text, "Frei"]], 
                                              columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                    st.session_state.freie_slots = pd.concat([st.session_state.freie_slots, neuer_slot], ignore_index=True)
                    st.success("Zeitraum erfolgreich freigegeben!")
                    st.rerun()
        with col_s2:
            st.markdown("<div class='card'><h4>Deine freigestellten Arbeitszeiten</h4></div>", unsafe_allow_html=True)
            st.dataframe(st.session_state.freie_slots, use_container_width=True)
            if st.button("Alle Slots zurücksetzen"):
                st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                st.rerun()

    # TAB 2: KUNDENKARTEI
    with menue[1]:
        st.subheader("👥 Digitale Kundenkartei")
        col_k_form, col_k_view = st.columns([1, 2])
        with col_k_form:
            st.markdown("<div class='card'><h4>Neuen Kunden anlegen</h4></div>", unsafe_allow_html=True)
            k_name = st.text_input("Kunden-Name", placeholder="Name")
            k_tel = st.text_input("Telefonnummer", placeholder="z.B. 0176...")
            k_notiz = st.text_area("Besondere Notizen")
            if st.button("Kunde abspeichern", use_container_width=True):
                if k_name:
                    neuer_kunde = pd.DataFrame([[k_name, k_tel, k_notiz]], columns=["Kunden-Name", "Telefonnummer", "Notizen"])
                    st.session_state.kunden = pd.concat([st.session_state.kunden, neuer_kunde], ignore_index=True)
                    st.success(f"{k_name} gesichert!")
                    st.rerun()
        with col_k_view:
            st.dataframe(st.session_state.kunden, use_container_width=True)

    # TAB 3: DOKUMENTE & QUITTUNGEN (Das Profi-Feature!)
    with menue[2]:
        st.subheader("📄 Professionelle Dokumente erstellen (Logo-Branding)")
        st.write("Generiere Protokolle oder Quittungen zum Ausdrucken/Versenden.")
        
        col_pdf_f, col_pdf_v = st.columns([1, 2])
        with col_pdf_f:
            st.markdown("<div class='card'><h4>Dokumenten-Konfigurator</h4></div>", unsafe_allow_html=True)
            
            if st.session_state.kunden.empty:
                st.warning("Keine Kunden in der Kartei! Bitte leg erst Kunden an.")
            else:
                doc_kunde = st.selectbox("Wähle einen Kunden:", st.session_state.kunden["Kunden-Name"])
                doc_art = st.selectbox("Behandlung:", list(st.session_state.zeiten_naegel.keys()))
                doc_datum = st.date_input("Datum", datetime.date.today())
                doc_preis = st.number_input("Beitrag in €", min_value=0.0, step=0.5)
                
                doc_typ = st.radio("Was möchtest du erstellen?", ["Professionelle Quittung", "Einverständniserklärung / Protokoll"], horizontal=True)
                
                if st.button("Dokument generieren", use_container_width=True):
                    # PDF-Inhalt vorbereiten
                    doc_content = ""
                    logo_html = ""
                    logo_filename = "redline-logo.png"
                    if os.path.exists(logo_filename):
                        logo_html = f"<img src='file://{logo_filename}' style='max-height: 50px; float: right;'>"
                    
                    if doc_typ == "Professionelle Quittung":
                        doc_content = f"""
                            <div class='pdf-frame'>
                                {logo_html}
                                <h1 style='color: #721c24;'>Redline Studio</h1>
                                <h2 style='text-align: center;'>QUITTUNG / RECHNUNG</h2>
                                <p><strong>Nummer:</strong> RE-{datetime.datetime.now().strftime('%Y%m%d%H%M')}</p>
                                <p><strong>Datum:</strong> {doc_datum.strftime('%Y-%m-%d')}</p>
                                <hr>
                                <p><strong>Kunde:</strong> {doc_kunde}</p>
                                <p><strong>Leistung:</strong> {doc_art}</p>
                                <h3 style='text-align: right; border-top: 2px solid #333;'>Gesamtbetrag erhalten: {doc_preis:.2f} €</h3>
                                <br><br>
                                <p style='font-style: italic; font-size: 0.9em;'>Vielen Dank für deinen Besuch!<br>Es gilt die Kleinunternehmerregelung (§ 19 UStG).</p>
                                <p>_____________________</p>
                                <p style='font-size: 0.8em;'>Unterschrift Redline Studio</p>
                            </div>
                        """
                    else: # Einverständniserklärung / Protokoll
                        doc_content = f"""
                            <div class='pdf-frame'>
                                {logo_html}
                                <h1 style='color: #721c24;'>Redline Studio</h1>
                                <h2 style='text-align: center;'>Einverständniserklärung & Protokoll</h2>
                                <p><strong>Datum:</strong> {doc_datum.strftime('%Y-%m-%d')}</p>
                                <hr>
                                <p><strong>Kunde:</strong> {doc_kunde}</p>
                                <p><strong>Geplante Behandlung:</strong> {doc_art}</p>
                                <br>
                                <p>Ich wurde über die Behandlung, mögliche Risiken und die richtige Nachpflege aufgeklärt.<br>
                                Ich stimme der Behandlung zu. Meine Notizen aus der Kundenkartei sind korrekt.</p>
                                <br><br><br>
                                <div style='display: flex; justify-content: space-between;'>
                                    <div>_____________________<br><span style='font-size: 0.8em;'>Unterschrift Kunde</span></div>
                                    <div>_____________________<br><span style='font-size: 0.8em;'>Unterschrift Redline Studio</span></div>
                                </div>
                            </div>
                        """
                    # Speichern in Session-State zum Anzeigen
                    st.session_state.pdf_view = doc_content
                    st.rerun()

        with col_pdf_v:
            st.markdown("<div class='card'><h4>Dokumenten-Vorschau</h4></div>", unsafe_allow_html=True)
            if 'pdf_view' in st.session_state:
                st.markdown(st.session_state.pdf_view, unsafe_allow_html=True)
                st.write("---")
                st.markdown("<p style='text-align: center; color: #721c24;'>Tipp: Kopiere den Text und füge ihn in Word/Pages ein, um ihn mit Logo als PDF zu speichern.</p>", unsafe_allow_html=True)
            else:
                st.info("Fülle links die Felder aus, um ein Dokument zu generieren.")

    # TAB 4: FINANZEN
    with menue[3]:
        st.subheader("📊 Finanzen (Admin Only)")
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

    # TAB 5: NAGEL-ZEITEN EINSTELLEN
    with menue[4]:
        st.subheader("⚙️ Behandlungsdauer einstellen")
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            st.markdown("<div class='card'><h4>Dauer je Nagel-Art (in Minuten)</h4></div>", unsafe_allow_html=True)
            st.session_state.zeiten_naegel["Neumodellage"] = st.number_input("Neumodellage Dauer", value=st.session_state.zeiten_naegel["Neumodellage"], step=5)
            st.session_state.zeiten_naegel["Auffüllen"] = st.number_input("Auffüllen Dauer", value=st.session_state.zeiten_naegel["Auffüllen"], step=5)
            st.write("#### Gesamte Blockadezeit (inkl. Reinigungspause)")
            for art, dauer in st.session_state.zeiten_naegel.items():
                st.write(f"💅 {art}: {dauer + 15} Min.")

# --- SEITE: KUNDEN-BUCHUNG (Professional Edition) ---
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
    
    # Automatische 15 Min. Reinigungspause für die Admin im Hintergrund!
    reinigungspause = 15
    gesamte_blockade_zeit = benoetigte_zeit + reinigungspause
    
    st.info(f"Für {nagel_wunsch} werden {benoetigte_zeit} Minuten eingeplant (zzgl. Reinigungspause).")
    
    st.write("### Verfügbare Termine im Studio:")
    freie_anzeige = st.session_state.freie_slots[st.session_state.freie_slots["Status"] == "Frei"]
    
    if freie_anzeige.empty:
        st.warning("Aktuell sind leider keine freien Termine freigeschaltet. Bitte frage direkt im Studio nach!")
    else:
        for idx, row in freie_anzeige.iterrows():
            verfuegbare_minuten = int(row["Dauer_Minuten"])
            if verfuegbare_minuten >= gesamte_blockade_zeit:
                col_slot, col_buch_btn = st.columns([3, 1])
                col_slot.write(f"📅 **{row['Datum']}** | ⏰ Von {row['Startzeit']} bis {row['Endzeit']} Uhr ({verfuegbare_minuten} Min. frei)")
                if col_buch_btn.button("Jetzt buchen", key=f"book_{idx}"):
                    # Slot als gebucht markieren
                    st.session_state.freie_slots.at[idx, "Status"] = "Gebucht"
                    # Termin eintragen
                    neuer_termin = pd.DataFrame([[row['Datum'], row['Startzeit'], st.session_state.user, nagel_wunsch, gesamte_blockade_zeit]], 
                                                columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt"])
                    st.session_state.termine = pd.concat([st.session_state.termine, neuer_termin], ignore_index=True)
                    st.success("Dein Termin wurde erfolgreich gebucht! Wir freuen uns auf dich. 🎉 (Symbolische Bestätigungs-E-Mail gesendet)")
                    st.rerun()
            else:
                st.markdown(f"~~📅 {row['Datum']} | ⏰ {row['Startzeit']} - {row['Endzeit']}~~ *(Slot zu kurz für {nagel_wunsch})*")
