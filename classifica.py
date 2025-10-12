# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import os
from datetime import datetime

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
PASSWORD = "decima2025"  # <-- Modifica qui la password

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
    
    # Backup automatico
    if os.path.exists(FILE_GIORNATE):
        backup_name = f"giornate_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        os.system(f"cp {FILE_GIORNATE} {backup_name}")
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

# --- Classifica generale (Bonus + Punteggi totali) ---
def calcola_classifica_generale(df_giornate):
    if df_giornate.empty:
        return pd.DataFrame(columns=["Posizione", "Squadra", "Bonus Totale", "Punteggio Totale"])
    
    df_classifica = (
        df_giornate.groupby("Squadra")[["Bonus", "Punteggio Reale"]]
        .sum()
        .reset_index()
        .sort_values(by="Bonus", ascending=False)
    )
    df_classifica["Posizione"] = range(1, len(df_classifica) + 1)
    return df_classifica[["Posizione", "Squadra", "Bonus", "Punteggio Reale"]].rename(
        columns={"Bonus": "Bonus Totale", "Punteggio Reale": "Punteggio Totale"}
    )

# --- Pagina 1: Classifica Generale ---
def pagina_classifica_generale(df_giornate):
    st.header("🏆 Classifica Generale (solo Bonus per il grafico)")
    df_generale = calcola_classifica_generale(df_giornate)

    if not df_generale.empty:
        st.dataframe(df_generale, use_container_width=True)
        # Grafico basato solo sui bonus totali
        st.bar_chart(df_generale.set_index("Squadra")["Bonus Totale"])
    else:
        st.info("Nessuna giornata registrata ancora. Inserisci la prima per iniziare!")

# --- Pagina 2: Classifiche Giornate ---
def pagina_classifiche_giornate(df_giornate):
    st.header("📊 Classifiche Giornate")
    if not df_giornate.empty:
        giornate_disponibili = sorted(df_giornate["Giornata"].unique())
        giornata_scelta = st.selectbox("Seleziona giornata", giornate_disponibili)
        df_sel = df_giornate[df_giornate["Giornata"] == giornata_scelta].copy()
        df_sel["Totale Giornata"] = df_sel["Punteggio Reale"] + df_sel["Bonus"]
        df_sel = df_sel.sort_values(by="Totale Giornata", ascending=False)
        st.dataframe(df_sel, use_container_width=True)
        st.bar_chart(df_sel.set_index("Squadra")["Totale Giornata"])
    else:
        st.info("Nessuna giornata registrata ancora.")

# --- Pagina 3: Inserimento Risultati ---
def pagina_inserimento_risultati():
    st.header("🔐 Inserimento risultati")
    password_input = st.text_input("Inserisci password", type="password")

    if password_input == PASSWORD:
        st.success("Accesso consentito ✅")

        numero_giornata = st.number_input("📅 Numero giornata", min_value=1, step=1)
        st.subheader("Inserisci punteggi reali")
        punteggi = {s: st.number_input(f"{s}", key=f"p_{s}") for s in SQUADRE}

        if st.button("💾 Salva giornata"):
            bonus = calcola_bonus(punteggi)
            salva_giornata(numero_giornata, punteggi, bonus)
            st.success(f"Giornata {numero_giornata} salvata con successo!")
            st.experimental_rerun()

    else:
        if password_input:
            st.error("Password errata ❌")
        else:
            st.info("Inserisci la password per abilitare l’inserimento dei punteggi.")

# =====================================================
#                  INTERFACCIA PRINCIPALE
# =====================================================

st.title("⚽ LA DECIMA")

# Menu laterale
menu = st.sidebar.radio(
    "📍 Seleziona una pagina:",
    ("🏆 Classifica Generale", "📊 Classifiche Giornate", "🔐 Inserimento Risultati")
)

# Carica i dati
df_giornate = carica_giornate()

# Navigazione
if menu == "🏆 Classifica Generale":
    pagina_classifica_generale(df_giornate)
elif menu == "📊 Classifiche Giornate":
    pagina_classifiche_giornate(df_giornate)
elif menu == "🔐 Inserimento Risultati":
    pagina_inserimento_risultati()
