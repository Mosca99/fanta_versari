# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os

# Config iniziale
st.set_page_config(page_title="LA DECIMA", layout="centered")

# Lista squadre (modifica se vuoi)
SQUADRE = ['Deportivo La Cadrega', 'FC Porcellona', 'Dio Kean', 'Mainz Na Gioia', 'Hellas Madonna', 'Pro Secco']

FILE_CLASSIFICA = "classifica.csv"
FILE_GIORNATE = "giornate.csv"

# --- Funzioni salvataggio/caricamento ---
def carica_classifica():
    if os.path.exists(FILE_CLASSIFICA):
        df = pd.read_csv(FILE_CLASSIFICA, index_col="Squadra")
        # cerca la colonna giusta indipendentemente dal nome
        for col in ["Totale Bonus", "Totale Punti Decima"]:
            if col in df.columns:
                return df[col].to_dict()
        # se non trova nulla, inizializza da zero
        return {s: 0 for s in SQUADRE}
    else:
        return {s: 0 for s in SQUADRE}

def salva_classifica(classifica_generale):
    df = pd.DataFrame(
        {"Squadra": list(classifica_generale.keys()),
         "Totale Bonus": list(classifica_generale.values())}
    )
    df.to_csv(FILE_CLASSIFICA, index=False)

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

def carica_giornate():
    if os.path.exists(FILE_GIORNATE):
        return pd.read_csv(FILE_GIORNATE)
    else:
        return pd.DataFrame(columns=["Giornata", "Squadra", "Punteggio Giornata", "Punti Decima"])

# --- Funzione calcolo bonus ---
def calcola_bonus(punteggi_giornata):
    bonus_map = {1: 1, 2: 0.5, 3: 0, 4: 0, 5: -0.5, 6: -1}
    sorted_items = sorted(punteggi_giornata.items(), key=lambda x: x[1], reverse=True)
    bonus = {}
    posizione = 1
    i = 0
    n = len(sorted_items)
    while i < n:
        stesso_punteggio = [sorted_items[i][0]]
        j = i + 1
        while j < n and sorted_items[j][1] == sorted_items[i][1]:
            stesso_punteggio.append(sorted_items[j][0])
            j += 1
        for squadra in stesso_punteggio:
            bonus[squadra] = bonus_map.get(posizione, 0)
        posizione += len(stesso_punteggio)
        i = j
    return bonus

# --- APP ---
st.title("⚽ Gestione Fantacalcio")

# --- Reset totale ---
if st.button("🔄 Reset Classifica e Storico"):
    if os.path.exists(FILE_CLASSIFICA):
        os.remove(FILE_CLASSIFICA)
    if os.path.exists(FILE_GIORNATE):
        os.remove(FILE_GIORNATE)
    st.session_state.classifica_generale = {s: 0 for s in SQUADRE}
    st.session_state.giornata = 1
    if "ultima_giornata" in st.session_state:
        del st.session_state["ultima_giornata"]
    st.success("✅ Classifica e giornate azzerate! Ricarica la pagina per ricominciare.")

# --- Carica dati all'avvio ---
if "classifica_generale" not in st.session_state:
    st.session_state.classifica_generale = carica_classifica()
if "giornata" not in st.session_state:
    giornate_df = carica_giornate()
    if len(giornate_df) > 0:
        st.session_state.giornata = giornate_df["Giornata"].max() + 1
    else:
        st.session_state.giornata = 1

# --- Riepilogo ultima giornata ---
if "ultima_giornata" in st.session_state:
    ug = st.session_state.ultima_giornata
    st.success(f"✅ Giornata {ug['numero']} registrata!")

    st.subheader(f"📊 Classifica giornata {ug['numero']}")
    st.table(ug["df_giornata"].set_index("Squadra"))

    st.subheader("🏆 Classifica Generale")
    st.table(ug["df_generale"].set_index("Squadra"))

st.subheader(f"Giornata {st.session_state.giornata}")

# --- Input punteggi ---
with st.form("punteggi_form"):
    punteggi_giornata = {}
    for squadra in SQUADRE:
        punteggi_giornata[squadra] = st.number_input(
            f"Punteggio di {squadra}",
            min_value=0.0,
            max_value=120.0,
            step=0.5,
            key=f"{squadra}_{st.session_state.giornata}",
        )
    submit = st.form_submit_button("Conferma giornata")

# --- Logica submit ---
if submit:
    bonus = calcola_bonus(punteggi_giornata)

    for s in SQUADRE:
        st.session_state.classifica_generale[s] += bonus[s]

    salva_classifica(st.session_state.classifica_generale)
    salva_giornata(st.session_state.giornata, punteggi_giornata, bonus)

    # Memorizza riepilogo ultima giornata
    st.session_state.ultima_giornata = {
        "numero": st.session_state.giornata,
        "df_giornata": pd.DataFrame(
            {"Squadra": SQUADRE,
             "Punteggio Reale": [punteggi_giornata[s] for s in SQUADRE],
             "Bonus": [bonus[s] for s in SQUADRE]}
        ).sort_values(by=["Punteggio Reale", "Bonus"], ascending=False),
        "df_generale": pd.DataFrame(
            {"Squadra": SQUADRE,
             "Totale Bonus": [st.session_state.classifica_generale[s] for s in SQUADRE]}
        ).sort_values(by="Totale Bonus", ascending=False),
    }

    st.session_state.giornata += 1
    st.rerun()

# --- Storico ---
st.subheader("📜 Storico Giornate")
storico = carica_giornate()
if len(storico) > 0:
    st.dataframe(storico.sort_values(by=["Giornata", "Squadra"]))

    # --- Grafico andamento bonus ---
    st.subheader("📈 Andamento Bonus nel Tempo")
    pivot = storico.pivot(index="Giornata", columns="Squadra", values="Bonus").fillna(0)
    cumulativo = pivot.cumsum()
    st.line_chart(cumulativo)
else:
    st.info("Nessuna giornata registrata finora.")
