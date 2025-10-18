import streamlit as st
import json
import os
import subprocess
from datetime import datetime

# ===============================================================
# CONFIGURAZIONE GITHUB
# ===============================================================
GITHUB_REPO_URL = "https://github.com/Mosca99/fanta_versari.git"
GITHUB_USER = "Mosca99"
GITHUB_EMAIL = "mosca.luca1999@gmail.com"
RESULTS_FILE = "risultati.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # meglio impostarlo come variabile d’ambiente

# ===============================================================
# FUNZIONI DI SUPPORTO
# ===============================================================

def carica_risultati():
    """Carica i risultati esistenti dal file JSON."""
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def salva_risultati(risultati):
    """Salva i risultati e fa commit + push su GitHub."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(risultati, f, indent=4, ensure_ascii=False)

    subprocess.run(["git", "config", "user.name", GITHUB_USER], check=True)
    subprocess.run(["git", "config", "user.email", GITHUB_EMAIL], check=True)

    subprocess.run(["git", "add", RESULTS_FILE], check=True)
    subprocess.run([
        "git", "commit", "-m",
        f"Aggiornamento risultati {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ], check=False)
    subprocess.run([
        "git", "push",
        f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/Mosca99/fanta_versari.git"
    ], check=True)

# ===============================================================
# INTERFACCIA STREAMLIT
# ===============================================================

st.title("🏆 Gestione Classifica Fanta Versari")

risultati = carica_risultati()

# Mostra classifica attuale
if risultati:
    st.subheader("Classifica attuale:")
    sorted_classifica = sorted(risultati.items(), key=lambda x: x[1], reverse=True)
    for nome, punteggio in sorted_classifica:
        st.write(f"**{nome}** — {punteggio} punti")
else:
    st.info("Nessun risultato presente. Inserisci il primo!")

st.divider()

# Form per aggiungere o aggiornare risultati
st.subheader("➕ Inserisci o aggiorna un risultato")

col1, col2 = st.columns(2)
with col1:
    nome = st.text_input("Nome giocatore")
with col2:
    punteggio = st.number_input("Punteggio", min_value=0, step=1)

if st.button("💾 Salva risultato"):
    if not nome:
        st.error("⚠️ Inserisci il nome del giocatore.")
    else:
        risultati[nome] = int(punteggio)
        salva_risultati(risultati)
        st.success(f"✅ Risultato per {nome} salvato e aggiornato su GitHub!")
        st.rerun()  # Ricarica l’app per aggiornare la classifica

