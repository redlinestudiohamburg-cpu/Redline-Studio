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
    .holiday-text {
        color: #721c24;
        font-weight: bold;
        background-color: #f8d7da;
        padding: 8px;
        border-radius: 5px;
        display: block;
        margin-bottom: 15px;
        border: 1px solid #f5c6cb;
    }
    </style>
""", unsafe_allow_html=True)

# --- FEIERTAGE-BERECHNER (DE/CH/AT Grundausstattung) ---
def get_feiertag(datum):
    jahr = datum.year
    feste = {
        (1, 1): "Neujahr",
        (6, 1): "Heilige Drei Könige",
        (1, 5): "Tag der Arbeit",
        (1, 8): "Schweizer Nationalfeiertag",
        (3, 10): "Tag der Deutschen Einheit",
        (26, 10): "Nationalfeiertag (Österreich)",
        (1, 11): "Allerheiligen",
        (25, 12): "1. Weihnachtstag",
        (26, 12): "2. Weihnachtstag"
    }
    
    # Osterberechnung für die Feiertage
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
    leichnam = oster_datum + datetime.timedelta(days=60)
    
    if datum == karfreitag: return "Karfreitag"
    if datum == oster_datum: return "Ostersonntag"
    if datum == ostermontag: return "Ostermontag"
    if datum == auffahrt: return "Auffahrt / Christi Himmelfahrt"
    if datum == pfingstmontag: return "Pfingstmontag"
    if datum == leichnam: return "Fronleichnam"
    
    if (datum.day, datum.month) in feste:
        return feste[(datum.day, datum.month)]
    return None

# --- INITIALISIERUNG DER DATEN-SPEICHER ---
if 'user' not in st.session_state:
    st.session_state.user = None

if 'zeiten_naegel' not in st.session_state:
    st.session_state.zeiten_naegel = {
        "Neumodellage": 120,
        "Auffüllen": 90,
        "French / Extra Design": 45
    }
if 'puffer_zeit' not in st.session_state:
    st.session_state.puffer_zeit = 15

if 'freie_slots' not in st.session_state:
    st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])

if 'finanzen' not in st.session_state:
    st.session_state.finanzen = pd.DataFrame(columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
if 'kunden' not in st.session_state:
    st.session_state.kunden = pd.DataFrame(columns=["Kunden-Name", "Telefonnummer", "Notizen"])
if 'termine' not in st.session_state:
    st.session_state.termine = pd.DataFrame(columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt"])

# --- STARTSEITE: KUNDEN-LOGIN ---
if st.session_state.user is None:
    st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Kreativität & Eleganz</p></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>Willkommen im Redline Studio</h2>", unsafe_allow_html=True)
    
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
            
    menue = st.tabs(["🗓️ Kalender & Slots", "⚙️ Nagel-Zeiten & Puffer", "👥 Kundenkartei", "📊 Finanzen"])
    
    # TAB 1: KALENDER & SLOTS FREIGEBEN
    with menue[0]:
        st.subheader("🗓️ Deine Arbeitszeiten flexibel freischalten")
        col_s1, col_s2 = st.columns([1, 2])
        
        with col_s1:
            st.markdown("<div class='card'><h4>Slot freigeben</h4></div>", unsafe_allow_html=True)
            slot_datum = st.date_input("Wähle das Datum", datetime.date.today(), key="admin_date")
            
            # Feiertag prüfen und nur als Information anzeigen!
            feiertag_name = get_feiertag(slot_datum)
            hinweis_text = "-"
            if feiertag_name:
                st.markdown(f"<span class='holiday-text'>ℹ️ Hinweis: An diesem Tag ist {feiertag_name}. Du kannst den Termin trotzdem unten freigeben!</span>", unsafe_allow_html=True)
                hinweis_text = feiertag_name
            
            st.write("Wann möchtest du Zeit anbieten?")
            start_zeit = st.time_input("Von", datetime.time(14, 0))
            end_zeit = st.time_input("Bis", datetime.time(17, 0))
            
            if st.button("Diesen Zeitraum freistellen", use_container_width=True):
                dauer = (datetime.datetime.combine(slot_datum, end_zeit) - datetime.datetime.combine(slot_datum, start_zeit)).seconds // 60
                if dauer <= 0:
                    st.error("Die Endzeit muss nach der Startzeit liegen!")
                else:
                    neuer_slot = pd.DataFrame([[slot_datum.strftime('%Y-%m-%d'), start_zeit.strftime('%H:%M'), end_zeit.strftime('%H:%M'), dauer, hinweis_text, "Frei"]], 
                                              columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                    st.session_state.freie_slots = pd.concat([st.session_state.freie_slots, neuer_slot], ignore_index=True)
                    st.success("Zeitraum erfolgreich eingetragen!")
                    st.rerun()
                    
        with col_s2:
            st.markdown("<div class='card'><h4>Deine freigestellten Arbeitszeiten</h4></div>", unsafe_allow_html=True)
            st.dataframe(st.session_state.freie_slots, use_container_width=True)
            if st.button("Alle Slots zurücksetzen"):
                st.session_state.freie_slots = pd.DataFrame(columns=["Datum", "Startzeit", "Endzeit", "Dauer_Minuten", "Feiertag-Hinweis", "Status"])
                st.rerun()

    # TAB 2: NAGEL-ZEITEN EINSTELLEN
    with menue[1]:
        st.subheader("⚙️ Behandlungsdauer & Aufbereitungszeit einstellen")
        col_z1, col_z2 = st.columns(2)
        with col_z1:
            st.markdown("<div class='card'><h4>💅 Dauer je Nagel-Art (in Minuten)</h4></div>", unsafe_allow_html=True)
            st.session_state.zeiten_naegel["Neumodellage"] = st.number_input("Neumodellage Dauer", value=st.session_state.zeiten_naegel["Neumodellage"], step=5)
            st.session_state.zeiten_naegel["Auffüllen"] = st.number_input("Auffüllen Dauer", value=st.session_state.zeiten_naegel["Auffüllen"], step=5)
            st.session_state.zeiten_naegel["French / Extra Design"] = st.number_input("French / Extra Design Dauer", value=st.session_state.zeiten_naegel["French / Extra Design"], step=5)
            
        with col_z2:
            st.markdown("<div class='card'><h4>🧼 Desinfektion & Aufbereitung</h4></div>", unsafe_allow_html=True)
            st.session_state.puffer_zeit = st.number_input("Pufferzeit zwischen Kunden (Minuten)", value=st.session_state.puffer_zeit, step=5)
            st.info(f"Das bedeutet: Das System rechnet nach jeder Behandlung automatisch {st.session_state.puffer_zeit} Minuten Pause ein.")

    # TAB 3: KUNDENKARTEI
    with menue[2]:
        st.subheader("👥 Digitale Kundenkartei")
        col_k_form, col_k_view = st.columns([1, 2])
        with col_k_form:
            st.markdown("<div class='card'><h4>Neuen Kunden anlegen</h4></div>", unsafe_allow_html=True)
            k_name = st.text_input("Kunden-Name")
            k_tel = st.text_input("Telefonnummer")
            k_notiz = st.text_area("Besondere Notizen")
            if st.button("Kunde abspeichern"):
                if k_name:
                    neuer_kunde = pd.DataFrame([[k_name, k_tel, k_notiz]], columns=["Kunden-Name", "Telefonnummer", "Notizen"])
                    st.session_state.kunden = pd.concat([st.session_state.kunden, neuer_kunde], ignore_index=True)
                    st.success(f"{k_name} gesichert!")
                    st.rerun()
        with col_k_view:
            st.dataframe(st.session_state.kunden, use_container_width=True)

    # TAB 4: FINANZEN
    with menue[3]:
        st.subheader("📊 Finanzen")
        col_f1, col_f2 = st.columns([1, 2])
        with col_f1:
            f_datum = st.date_input("Datum", datetime.date.today(), key="fin_date")
            f_typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
            f_kat = st.text_input("Kategorie")
            f_betrag = st.number_input("Betrag in €", min_value=0.0)
            if st.button("Speichern"):
                neuer_eintrag = pd.DataFrame([[f_datum, f_typ, f_kat, f_betrag]], columns=["Datum", "Typ", "Kategorie", "Betrag (€)"])
                st.session_state.finanzen = pd.concat([st.session_state.finanzen, neuer_eintrag], ignore_index=True)
                st.rerun()
        with col_f2:
            st.dataframe(st.session_state.finanzen, use_container_width=True)

# --- BEREICH: KUNDEN-TERMINBUCHUNG ---
else:
    st.markdown("<div class='main-header'><h1>Redline Studio</h1><p>Terminbuchung</p></div>", unsafe_allow_html=True)
    with st.sidebar:
        st.write(f"Willkommen, **{st.session_state.user}**!")
        if st.button("Abmelden"):
            st.session_state.user = None
            st.rerun()
            
    st.subheader("🗓️ Finde deinen Wunschtermin")
    
    nagel_wunsch = st.selectbox("Was möchtest du machen lassen?", list(st.session_state.zeiten_naegel.keys()))
    benoetigte_zeit = st.session_state.zeiten_naegel[nagel_wunsch]
    gesamte_blockade_zeit = benoetigte_zeit + st.session_state.puffer_zeit
    
    st.info(f"Für {nagel_wunsch} werden {benoetigte_zeit} Minuten benötigt (zzgl. Reinigungspause).")
    
    st.write("### Verfügbare Termine im Studio:")
    freie_anzeige = st.session_state.freie_slots[st.session_state.freie_slots["Status"] == "Frei"]
    
    if freie_anzeige.empty:
        st.warning("Aktuell sind leider keine freien Termine freigeschaltet. Bitte frage direkt im Studio nach!")
    else:
        for idx, row in freie_anzeige.iterrows():
            verfuegbare_minuten = int(row["Dauer_Minuten"])
            
            if verfuegbare_minuten >= gesamte_blockade_zeit:
                col_slot, col_buch_btn = st.columns([3, 1])
                
                # Feiertags-Anzeige für den Kunden, falls an dem Tag einer ist
                ft_zusatz = f" | 🎉 ({row['Feiertag-Hinweis']})" if row['Feiertag-Hinweis'] != "-" else ""
                col_slot.write(f"📅 **{row['Datum']}**{ft_zusatz} | ⏰ Von {row['Startzeit']} bis {row['Endzeit']} Uhr ({verfuegbare_minuten} Min. frei)")
                
                if col_buch_btn.button("Jetzt buchen", key=f"book_{idx}"):
                    st.session_state.freie_slots.at[idx, "Status"] = "Gebucht"
                    neuer_termin = pd.DataFrame([[row['Datum'], row['Startzeit'], st.session_state.user, nagel_wunsch, gesamte_blockade_zeit]], 
                                                columns=["Datum", "Uhrzeit", "Kunde", "Typ", "Dauer_Gesamt"])
                    st.session_state.termine = pd.concat([st.session_state.termine, neuer_termin], ignore_index=True)
                    st.success("Dein Termin wurde erfolgreich gebucht! Wir freuen uns auf dich. 🎉")
                    st.rerun()
            else:
                st.markdown(f"~~📅 {row['Datum']} | ⏰ {row['Startzeit']} - {row['Endzeit']}~~ *(Slot zu kurz für {nagel_wunsch})*")
                
