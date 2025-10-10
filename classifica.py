# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

# Config iniziale
st.set_page_config(page_title="LA DECIMA", layout="centered")

# Lista squadre
SQUADRE = [
    "Deportivo La Cadrega",
    "FC Porcellona",
    "Dio Kean",
    "Mainz Na Gioia",
    "Hellas Madonna",
    "Pro Secco"
]

FILE_GIORNATE = "giornate.csv"

# --- Imposta password amministratore ---
PASSWORD = "decima2025"  # <-- Modifica qui la password di inserimento

# --- Funzioni salvataggio/caricamento ---
def carica_giornate():
    if os.path.exists(FILE_GIORNATE):
        return pd.read_csv(FILE_GIORNATE)
    else:
        return pd.DataFrame(columns=["Giornata", "Squadra", "Punteggio Reale", "Bonus"])

def salva_giornata(numero, punteggi, bonus):
    df = pd.DataFrame({
        "Giornata": [numero]*len(SQUADRE),
        "Squadra": SQUADRE,
        "Punteggio Reale": [punteggi[s] for s in SQUADRE],
        "Bonus": [bonus[s] for s in SQUADRE]
    })
    if os.path.exists(FILE_GIORNATE):
        df.to_csv(FILE_GIORNATE, mode="a", header=False, index=False)
    else:
        df.to_csv(FILE_GIORNATE, index=False)

# --- Funzione calcolo bonus ---
def calcola_bonus(punteggi_giornata):
    bonus_map = {1: 1, 2: 0.5, 3: 0, 4: 0, 5: -0.5, 6: -1}
    sorted_items = sorted(punteggi_giornata.items(), key=lambda x: x[1], reverse=True)
    bonus = {}
    posizione = 1
    for squadra, _ in sorted_items:
        bonus[squadra] = bonus_map.get(posizione, 0)
        posizione += 1
    return bonus

# --- Calcolo classifica generale basata sui bonus ---
def calcola_classifica_generale(df_giornate):
    if df_giornate.empty:
        return pd.DataFrame(columns=["Posizione", "Squadra", "Bonus"])
    
    df_classifica = (
        df_giornate.groupby("Squadra")["Bonus"]
        .sum()
        .reset_index()
        .sort_values(by="Bonus", ascending=False)
    )
    df_classifica["Posizione"] = range(1, len(df_classifica)+1)
    return df_classifica[["Posizione", "Squadra", "Bonus"]]

# --- Interfaccia Streamlit ---
st.title("⚽ LA DECIMA - Gestione Classifica")

df_giornate = carica_giornate()

# Sezione Classifica Generale
st.header("🏆 Classifica Generale (solo Bonus)")
df_generale = calcola_classifica_generale(df_giornate)

if not df_generale.empty:
    st.dataframe(df_generale, use_container_width=True)
    st.bar_chart(df_generale.set_index("Squadra")["Bonus"])
else:
    st.info("Nessuna giornata registrata ancora. Inserisci la prima per iniziare!")

# --- Sezione password per inserimento punteggi ---
st.header("🔐 Accesso per inserimento risultati")

password_input = st.text_input("Inserisci password", type="password")

if password_input == PASSWORD:
    st.success("Accesso consentito ✅")

    # Sezione Giornata
    st.header("📅 Gestione Giornata")

    numero_giornata = st.number_input("Numero giornata", min_value=1, step=1)

    st.subheader("Inserisci punteggi")
    punteggi = {s: st.number_input(f"{s} - Punteggio Reale", key=f"p_{s}") for s in SQUADRE}

    if st.button("Salva giornata"):
        bonus = calcola_bonus(punteggi)
        salva_giornata(numero_giornata, punteggi, bonus)
        st.success(f"Giornata {numero_giornata} salvata con successo!")
        st.experimental_rerun()

else:
    if password_input:
        st.error("Password errata ❌")
    st.info("Inserisci la password per abilitare l'inserimento dei punteggi.")

# Sezione per consultare giornate passate
st.header("📊 Classifiche Giornate")
if not df_giornate.empty:
    giornate_disponibili = sorted(df_giornate["Giornata"].unique())
    giornata_scelta = st.selectbox("Seleziona giornata", giornate_disponibili)
    df_sel = df_giornate[df_giornate["Giornata"] == giornata_scelta].copy()
    df_sel["Totale Giornata"] = df_sel["Punteggio Reale"] + df_sel["Bonus"]
    df_sel = df_sel.sort_values(by="Totale Giornata", ascending=False)
    st.dataframe(df_sel, use_container_width=True)
else:
    st.info("Nessuna giornata registrata ancora.")
