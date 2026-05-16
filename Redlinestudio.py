import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# 1. SEITEN-EINSTELLUNGEN
st.set_page_config(page_title="Redline Studio", page_icon="", layout="wide")

# 2. DATENBANK-VERBINDUNG (Erstellt die Datei automatisch, falls sie fehlt)
conn = sqlite3.connect('redline_studio.db', check_same_thread=False)
c = conn.cursor()

# Tabellen erstellen: Eine für Kunden/Termine, eine für deine Kostenplanung
c.execute('''CREATE TABLE IF NOT EXISTS kunden 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, telefon TEXT, 
              risiken TEXT, termin_datum TEXT, termin_zeit TEXT, status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS kosten 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, produkt TEXT, preis REAL)''')
conn.commit()

# 3. NAVIGATION (In der Seitenleiste)
st.sidebar.title(" Redline Studio")
bereich = st.sidebar.radio("Bereich wechseln:", ["Kunden-Portal", "Admin-Bereich (Geheim)"])

# =====================================================================
# BEREICH 1: KUNDEN-PORTAL (Das sehen deine Kunden über den Link)
# =====================================================================
if bereich == "Kunden-Portal":
    st.title("Wilkommen im Redline Studio")
    st.write("Schön, dass du da bist! Bitte frage hier deinen Wunschtermin an.")
    
    # Formular für den Kunden
    with st.form("buchungs_formular"):
        name = st.text_input("Dein vollständiger Name *")
        telefon = st.text_input("Deine Telefonnummer *")
        
        st.info("Wichtig für deine Sicherheit: Gibt es Allergien, Krankheiten (z.B. Diabetes) oder Besonderheiten?")
        risiken = st.text_area("Gesundheitliche Hinweise / Risiken (z.B. Keine Allergien)")
        
        st.write("Wann möchtest du vorbeikommen?")
        datum = st.date_input("Datum wählen", min_value=datetime.today())
        zeit = st.time_input("Uhrzeit wählen")
        
        # Datenschutz-Haken
        dsgvo = st.checkbox("Ich stimme zu, dass meine Daten für die Terminvereinbarung gespeichert werden.")
        
        eingereicht = st.form_submit_button("Termin jetzt anfragen")
        
        if eingereicht:
            if not name or not telefon:
                st.error("Bitte fülle die Pflichtfelder (Name und Telefonnummer) aus.")
            elif not dsgvo:
                st.error("Bitte bestätige die Datenschutzerklärung.")
            else:
                # Daten in die Datenbank schreiben. Status ist standardmäßig 'Angefragt'
                c.execute('''INSERT INTO kunden (name, telefon, risiken, termin_datum, termin_zeit, status) 
                             VALUES (?, ?, ?, ?, ?, 'Angefragt')''', 
                          (name, telefon, risiken, str(datum), str(zeit)))
                conn.commit()
                st.success(f"Vielen Dank, {name}! Deine Anfrage wurde weitergeleitet. Ich melde mich bei dir.")

# =====================================================================
# BEREICH 2: ADMIN-BEREICH (Nur für dich mit Passwort)
# =====================================================================
elif bereich == "Admin-Bereich (Geheim)":
    st.title("Admin-Zentrale ")
    
    # Passwort-Abfrage zum Schutz deiner Daten
    passwort = st.text_input("Bitte gib das Studio-Passwort ein:", type="password")
    
    # Du kannst 'redline2026' durch dein Wunschpasswort ersetzen
    if passwort == "Sarenka18!":
        st.success("Zugriff gewährt!")
        
        # Untermenü für deine Verwaltung (Reiter/Tabs)
        tab_termine, tab_kosten = st.tabs([" Termine & Kundenkartei", " Kosten & Ideen"])
        
        # REITER 1: TERMINE & KUNDENKARTEI
        with tab_termine:
            st.header("Aktuelle Buchungen & Kundenkartei")
            
            # Manuelle Pause oder Sperre eintragen
            st.subheader("Pausenzeiten blockieren")
            with st.expander(" Neue Pause / Sperre eintragen"):
                p_datum = st.date_input("Datum der Pause")
                p_zeit = st.time_input("Uhrzeit der Pause")
                if st.button("Pause eintragen"):
                    c.execute('''INSERT INTO kunden (name, telefon, risiken, termin_datum, termin_zeit, status) 
                                 VALUES ('PAUSE / SPERRE', '-', '-', ?, ?, 'Gesperrt')''', 
                              (str(p_datum), str(p_zeit)))
                    conn.commit()
                    st.success("Zeitfenster erfolgreich gesperrt!")
            
            # Kunden anzeigen
            st.subheader("Eingegangene Termine & Akten")
            kunden_daten = pd.read_sql_query("SELECT * FROM kunden", conn)
            
            if not kunden_daten.empty:
                for index, row in kunden_daten.iterrows():
                    # Risikowarnung: Wenn etwas eingetragen wurde, färben wir es rot
                    ist_pause = row['name'] == "PAUSE / SPERRE"
                    
                    if ist_pause:
                        st.warning(f" **{row['termin_datum']} um {row['termin_zeit']} Uhr:** ZEITFENSTER GESPERRT / PAUSE")
                    else:
                        st.write("---")
                        st.subheader(f" Kunde: {row['name']}")
                        st.write(f"**Termin:** {row['termin_datum']} um {row['termin_zeit']} Uhr | **Status:** {row['status']}")
                        st.write(f" **Telefon:** {row['telefon']}")
                        
                        # WICHTIG: Risikowarnung sofort sichtbar machen
                        if row['risiken'] and row['risiken'].strip() != "":
                            st.error(f" **WICHTIGE ANAMNESE / RISIKEN:** {row['risiken']}")
                        else:
                            st.info(" Keine gesundheitlichen Risiken angegeben.")
            else:
                st.info("Noch keine Termine oder Kunden eingetragen.")

        # REITER 2: KOSTEN & IDEEN (Deine Excel-Alternative)
        with tab_kosten:
            st.header("Ideenschmiede & Kostenrechner")
            
            # Neues Produkt für die Zukunft hinzufügen
            with st.form("kosten_formular"):
                produkt_name = st.text_input("Geplante Anschaffung (z.B. UV-Lampe, Gele)")
                produkt_preis = st.number_input("Voraussichtlicher Preis in €", min_value=0.0, step=1.0)
                if st.form_submit_button("Auf die Liste setzen"):
                    if produkt_name:
                        c.execute("INSERT INTO kosten (produkt, preis) VALUES (?, ?)", (produkt_name, produkt_preis))
                        conn.commit()
                        st.success(f"'{produkt_name}' wurde zur Liste hinzugefügt.")
            
            # Tabelle und Gesamtsumme anzeigen
            st.subheader("Deine Ausgaben-Planung")
            kosten_daten = pd.read_sql_query("SELECT * FROM kosten", conn)
            
            if not kosten_daten.empty:
                st.dataframe(kosten_daten[["produkt", "preis"]], use_container_width=True)
                gesamtsumme = kosten_daten["preis"].sum()
                st.metric(label="Erwartete Gesamtkosten", value=f"{gesamtsumme:.2f} €")
            else:
                st.info("Deine Liste ist noch leer.")
                
    elif passwort != "":
        st.error("Falsches Passwort! Zugriff verweigert.")
