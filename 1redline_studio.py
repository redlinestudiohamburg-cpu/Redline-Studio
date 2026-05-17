import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- SEITEN-EINSTELLUNGEN & DESIGN ---
st.set_page_config(page_title="Redline Studio", page_icon="💅", layout="wide")

# Weinrotes Edel-Design per CSS einfügen
st.markdown("""
    <style>
    .main { background-color: #f7f7f7; }
    .stButton>button { 
        background-color: #b8af94; 
        color: white; 
        border-radius: 5px; 
        border: none;
    }
    .stButton>button:hover { background-color: #8c2030; color: white; }
    h1, h2, h3 { color: #333333; }
    </style>
""", unsafe_allow_html=True)

# Weinroter Header-Balken oben
st.markdown("<div style='background-color: #8c2030; padding: 20px; text-align: center; border-radius: 5px; margin-bottom: 25px;'><h1 style='color: #d4af37; margin: 0; font-family: serif;'>Redline Studio</h1><p style='color: white; margin: 5px 0 0 0;'>Kreativität & Eleganz</p></div>", unsafe_allow_html=True)

# --- DATENBANKEN INITIALISIEREN (EXCEL-ERSATZ) ---
if 'kunden_db' not in st.session_state:
    if os.path.exists('kundenkartei.xlsx'):
        st.session_state.kunden_db = pd.read_excel('kundenkartei.xlsx')
    else:
        st.session_state.kunden_db = pd.DataFrame(columns=['Name', 'Telefonnummer', 'Adresse', 'Hauttyp_Allergien', 'Gesundheits_Risiken', 'Scan_Vorhanden'])

if 'finanzen_db' not in st.session_state:
    if os.path.exists('finanzen.xlsx'):
        st.session_state.finanzen_db = pd.read_excel('finanzen.xlsx')
    else:
        st.session_state.finanzen_db = pd.DataFrame(columns=['Datum', 'Typ', 'Kategorie_Leistung', 'Betrag', 'Notiz'])

if 'material_db' not in st.session_state:
    st.session_state.material_db = []

# --- HILFSFUNKTIONEN ZUM SPEICHERN ---
def speichere_kunden():
    st.session_state.kunden_db.to_excel('kundenkartei.xlsx', index=False)

def speichere_finanzen():
    st.session_state.finanzen_db.to_excel('finanzen.xlsx', index=False)

# --- LOGIK: WER IST EINGELOGGT? ---
if 'user' not in st.session_state:
    st.session_state.user = None

# --- STARTSEITE: KUNDEN-LOGIN ---
if st.session_state.user is None:
    st.markdown("<h2 style='text-align: center;'>Willkommen im Redline Studio</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic;'>Schön, dass du da bist! Bitte gib deinen Namen ein, um deinen Wunschtermin zu buchen.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        name_eingabe = st.text_input("Dein vollständiger Name *", placeholder="Hier eintippen...")
        if st.button("Anmelden & Weiter zur Buchung", use_container_width=True):
            if name_eingabe.strip() == "":
                st.error("Bitte gib einen Namen ein.")
            elif name_eingabe.strip() == "admin123":
                st.session_state.user = "Admin"
                st.rerun()
            else:
                st.session_state.user = name_eingabe.strip()
                st.rerun()
                
    st.markdown("<hr style='border-top: 1px solid #ddd; margin-top: 5px;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.9em; color: #666;'>Du bist das erste Mal bei mir? Kein Problem! Wir füllen deine Akte ganz entspannt gemeinsam beim ersten Termin vor Ort in Papierform aus. 📜✨</p>", unsafe_allow_html=True)

# --- BEREICH: DER KUNDE IST EINGELOGGT ---
elif st.session_state.user != "Admin":
    st.markdown(f"### Hallo, **{st.session_state.user}**! 👋")
    st.info("Hier kannst du gleich deinen Wunschtermin auswählen. (Terminkalender-Modul wird geladen...)")
    
    # Einfacher Logout-Button für den Kunden
    if st.button("Abmelden"):
        st.session_state.user = None
        st.rerun()

# --- BEREICH: ADMIN-DASHBOARD (GEHEIM) ---
else:
    st.markdown("## 🔐 Admin-Dashboard (Geheim)")
    
    if st.button("🚪 Admin-Bereich verlassen & Abmelden"):
        st.session_state.user = None
        st.rerun()
        
    tab1, tab2 = st.tabs(["📋 Kundenkartei & Termine", "📊 Materialrechner & Finanzen"])
    
    # REITER 1: KUNDENKARTEI VERWALTEN
    with tab1:
        st.subheader("Kunden-Kartei verwalten")
        
        # Neuen Kunden manuell hinzufügen
        with st.expander("➕ Neue Kunden-Karteikarte anlegen"):
            neuer_name = st.text_input("Vollständiger Name")
            neue_tel = st.text_input("Telefonnummer")
            neue_adr = st.text_input("Adresse")
            neuer_hauttyp = st.text_input("Hauttyp / Allergien (z.B. Keine)")
            neue_risiken = st.text_input("Gesundheits-Risiken (z.B. Diabetes)")
            
            uploaded_file = st.file_uploader("Papier-Formular einscannen / hochladen (Bild oder PDF)", type=["png", "jpg", "jpeg", "pdf"])
            
            if st.button("Karteikarte speichern"):
                if neuer_name:
                    scan_status = "Ja" if uploaded_file is not None else "Nein"
                    neue_zeile = pd.DataFrame([{
                        'Name': neuer_name, 'Telefonnummer': neue_tel, 'Adresse': neue_adr,
                        'Hauttyp_Allergien': neuer_hauttyp, 'Gesundheits_Risiken': neue_risiken,
                        'Scan_Vorhanden': scan_status
                    }])
                    st.session_state.kunden_db = pd.concat([st.session_state.kunden_db, neue_zeile], ignore_index=True)
                    speichere_kunden()
                    st.success(f"Karteikarte für {neuer_name} erfolgreich angelegt!")
                    st.rerun()
                else:
                    st.error("Der Name ist ein Pflichtfeld!")

        # Kundenliste anzeigen und bearbeiten
        if not st.session_state.kunden_db.empty:
            st.write("### Aktuelle Kundenkartei (Direkt in Excel gespeichert)")
            
            for index, row in st.session_state.kunden_db.iterrows():
                with st.container():
                    col_n, col_t, col_a, col_h, col_r, col_s, col_b = st.columns([2, 2, 2, 2, 2, 1, 1])
                    
                    with col_n: st.text_input("Name", row['Name'], key=f"name_{index}")
                    with col_t: st.text_input("Telefon", row['Telefonnummer'], key=f"tel_{index}")
                    with col_a: st.text_input("Adresse", row['Adresse'], key=f"adr_{index}")
                    with col_h: st.text_input("Allergien", row['Hauttyp_Allergien'], key=f"haut_{index}")
                    with col_r: st.text_input("Risiken", row['Gesundheits_Risiken'], key=f"risk_{index}")
                    with col_s: st.write(f"📄 Scan: {row['Scan_Vorhanden']}")
                    
                    with col_b:
                        if st.button("🗑️", key=f"del_{index}"):
                            st.session_state.kunden_db = st.session_state.kunden_db.drop(index).reset_index(drop=True)
                            speichere_kunden()
                            st.warning("Eintrag gelöscht.")
                            st.rerun()
            
            if st.button("💾 Alle Änderungen in Excel übernehmen"):
                for index in range(len(st.session_state.kunden_db)):
                    st.session_state.kunden_db.at[index, 'Name'] = st.session_state[f"name_{index}"]
                    st.session_state.kunden_db.at[index, 'Telefonnummer'] = st.session_state[f"tel_{index}"]
                    st.session_state.kunden_db.at[index, 'Adresse'] = st.session_state[f"adr_{index}"]
                    st.session_state.kunden_db.at[index, 'Hauttyp_Allergien'] = st.session_state[f"haut_{index}"]
                    st.session_state.kunden_db.at[index, 'Gesundheits_Risiken'] = st.session_state[f"risk_{index}"]
                speichere_kunden()
                st.success("Änderungen erfolgreich in Excel-Datei gespeichert!")
        else:
            st.info("Noch keine Kundenkarten angelegt.")

    # REITER 2: MATERIALRECHNER & FINANZEN
    with tab2:
        col_links, col_rechts = st.columns(2)
        
        # LINKS: MATERIAL- & PREISKALKULATOR
        with col_links:
            st.markdown("### 🧮 Material- & Preiskalkulator")
            
            with st.form("kalkulator_form"):
                prod_bild = st.file_uploader("Produkt-Bild (optional)", type=["png", "jpg", "jpeg"])
                prod_name = st.text_input("Produkt / Material Bezeichnung", placeholder="z.B. UV-Gel 1")
                prod_preis = st.number_input("Gesamtpreis der Packung (€)", min_value=0.0, step=0.01, format="%.2f")
                prod_anzahl = st.number_input("Wie viele Behandlungen hält die Packung?", min_value=1, step=1)
                
                if st.form_submit_button("➕ Zum Set hinzufügen"):
                    if prod_name and prod_preis > 0:
                        anteil = prod_preis / prod_anzahl
                        st.session_state.material_db.append({
                            'Name': prod_name, 'Gesamtpreis': prod_preis, 'Behandlungen': prod_anzahl, 'Anteil': anteil
                        })
            
            # Liste der hinzugefügten Produkte im aktuellen Set
            gesamtkosten = 0.0
            if st.session_state.material_db:
                st.write("#### Aktuelle Produkte im Set:")
                for item in st.session_state.material_db:
                    st.write(f"- **{item['Name']}**: {item['Gesamtpreis']:.2f}€ / {item['Behandlungen']} Behandlungen = **{item['Anteil']:.2f}€** anteilig pro Kunde")
                    gesamtkosten += item['Anteil']
                
                st.markdown(f"**Gesamt-Anteilige Materialkosten pro Set: {gesamtkosten:.2f} €**")
                
                empfohlener_preis = st.number_input("Dein gewünschter Kundenpreis (€)", min_value=0.0, step=5.0, value=gesamtkosten*4)
                gewinn_pro_set = empfohlener_preis - gesamtkosten
                st.metric("Dein Reingewinn pro Set", f"{gewinn_pro_set:.2f} €")
                
                if st.button("🗑️ Gesamtes Set zurücksetzen"):
                    st.session_state.material_db = []
                    st.rerun()

        # RECHTS: EINNAHMEN & AUSGABEN
        with col_rechts:
            st.markdown("### 📈 Einnahmen- & Ausgaben-Planung")
            
            # Formular für Einträge
            typ = st.selectbox("Typ", ["Einnahme", "Ausgabe"])
            kat = st.selectbox("Kategorie / Leistung", ["Neuanlage", "Auffüllen", "Nailart", "Material-Einkauf", "Werbung", "Sonstiges"])
            betrag = st.number_input("Betrag (€)", min_value=0.0, step=1.0, format="%.2f")
            notiz = st.text_input("Notiz (z.B. Kundin Lisa)")
            
            if st.button("📝 Eintrag in Finanz-Excel speichern"):
                if betrag > 0:
                    neuer_eintrag = pd.DataFrame([{
                        'Datum': datetime.now().strftime("%d.%m.%Y"),
                        'Typ': typ, 'Kategorie_Leistung': kat, 'Betrag': betrag, 'Notiz': notiz
                    }])
                    st.session_state.finanzen_db = pd.concat([st.session_state.finanzen_db, neuer_eintrag], ignore_index=True)
                    speichere_finanzen()
                    st.success("Eintrag erfolgreich verbucht!")
                    st.rerun()
            
            # Auswertung anzeigen
            if not st.session_state.finanzen_db.empty:
                einnahmen_gesamt = st.session_state.finanzen_db[st.session_state.finanzen_db['Typ'] == "Einnahme"]['Betrag'].sum()
                ausgaben_gesamt = st.session_state.finanzen_db[st.session_state.finanzen_db['Typ'] == "Ausgabe"]['Betrag'].sum()
                gewinn_gesamt = einnahmen_gesamt - ausgaben_gesamt
                
                st.markdown("#### Monats-Übersicht")
                st.write(f"💰 **Einnahmen gesamt:** {einnahmen_gesamt:.2f} €")
                st.write(f"🛑 **Ausgaben gesamt:** {ausgaben_gesamt:.2f} €")
                st.write(f"🟩 **Aktueller GEWINN:** {gewinn_gesamt:.2f} €")
                
                with st.expander("📄 Ganze Finanz-Tabelle ansehen"):
                    st.dataframe(st.session_state.finanzen_db)
