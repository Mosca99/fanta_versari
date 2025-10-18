import streamlit as st
import json
import os
import subprocess
from datetime import datetime
import pandas as pd

# ===============================================================
# CONFIGURAZIONE GITHUB
# ===============================================================
GITHUB_REPO_URL = "https://github.com/Mosca99/fanta_versari.git"
GITHUB_USER = "Mosca99"
GITHUB_EMAIL = "mosca.luca1999@gmail.com"
RESULTS_FILE = "risultati.json"
GITHUB_TOKEN = st.secrets.get("github_token")

# ===============================================================
# CONFIGURAZIONE SQUADRE
# ===============================================================
SQUADRE = [
    "Porcellona",
    "Hellas Madonna",
    "Dio Kean",
    "Main Na Gioia",
    "Deportivo La Cadrega",
    "Pro Secco"
]

# ===============================================================
# FUNZIONI DI SUPPORTO
# ===============================================================

def carica_risultati():
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"giornate": {}}
    return {"giornate": {}}


def salva_risultati(risultati):
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


def calcola_bonus(punteggi):
    """Calcola i bonus per una singola giornata gestendo i pari merito."""
    df = pd.DataFrame(list(punteggi.items()), columns=["Squadra", "Punteggio"])
    df = df.sort_values(by="Punteggio", ascending=False)

    bonus_mapping = {1: 1, 2: 0.5, 3: 0, 4: 0, 5: -0.5, 6: -1}

    df["Posizione"] = df["Punteggio"].rank(method="min", ascending=False).astype(int)
    df["Bonus"] = df["Posizione"].map(bonus_mapping).fillna(0)

    return dict(zip(df["Squadra"], df["Bonus"]))


def calcola_classifica_generale(risultati):
    """Calcola la classifica generale (somma bonus) e punteggi totali."""
    giornate = risultati.get("giornate", {})
    bonus_tot = {sq: 0 for sq in SQUADRE}
    punti_tot = {sq: 0 for sq in SQUADRE}

    for giornata, punteggi in giornate.items():
        bonus = calcola_bonus(punteggi)
        for sq in SQUADRE:
            bonus_tot[sq] += bonus.get(sq, 0)
            punti_tot[sq] += punteggi.get(sq, 0)

    df = pd.DataFrame({
        "Squadra": SQUADRE,
        "Bonus Totali": [bonus_tot[sq] for sq in SQUADRE],
        "Punteggio Totale": [punti_tot[sq] for sq in SQUADRE]
    })

    df = df.sort_values(
        by=["Bonus Totali", "Punteggio Totale"], ascending=[False, False]
    ).reset_index(drop=True)

    return df, bonus_tot, punti_tot


def calcola_andamento(risultati):
    """Restituisce un dataframe con i punteggi giornalieri per ogni squadra."""
    giornate = risultati.get("giornate", {})
    df = pd.DataFrame(giornate).T
    df.index.name = "Giornata"
    return df[SQUADRE]


# ===============================================================
# INTERFACCIA STREAMLIT
# ===============================================================

st.set_page_config(page_title="Fanta Versari", layout="wide")

menu = st.sidebar.radio(
    "Navigazione",
    ["🏆 Classifica Generale", "📅 Classifiche Giornate", "🔒 Inserisci Risultati"]
)

risultati = carica_risultati()

# ---------------------------------------------------------------
# 🏆 PAGINA 1 — CLASSIFICA GENERALE
# ---------------------------------------------------------------
if menu == "🏆 Classifica Generale":
    st.title("🏆 Classifica Generale Fanta Versari")

    if not risultati["giornate"]:
        st.info("Nessuna giornata registrata.")
    else:
        classifica, bonus_tot, punti_tot = calcola_classifica_generale(risultati)

        st.dataframe(classifica, use_container_width=True)

        st.subheader("📈 Andamento punteggi giornalieri")
        andamento = calcola_andamento(risultati)
        st.line_chart(andamento)

# ---------------------------------------------------------------
# 📅 PAGINA 2 — CLASSIFICHE GIORNATE
# ---------------------------------------------------------------
elif menu == "📅 Classifiche Giornate":
    st.title("📅 Classifiche delle Giornate")

    if not risultati["giornate"]:
        st.info("Nessuna giornata presente.")
    else:
        for giornata, punteggi in risultati["giornate"].items():
            st.subheader(giornata)
            bonus = calcola_bonus(punteggi)
            df = pd.DataFrame({
                "Squadra": list(punteggi.keys()),
                "Punteggio": list(punteggi.values()),
                "Bonus": [bonus[sq] for sq in punteggi.keys()]
            }).sort_values(by="Punteggio", ascending=False)
            st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------------
# 🔒 PAGINA 3 — INSERIMENTO RISULTATI
# ---------------------------------------------------------------
elif menu == "🔒 Inserisci Risultati":
    st.title("🔒 Inserimento Risultati Giornata")

    password = st.text_input("Password", type="password")
    if password == st.secrets.get("admin_password"):
        st.success("Accesso autorizzato ✅")

        numero_giornata = len(risultati["giornate"]) + 1
        nome_giornata = f"Giornata {numero_giornata}"

        st.subheader(f"Inserisci i risultati per {nome_giornata}:")
        nuovi_punteggi = {}

        for squadra in SQUADRE:
            nuovi_punteggi[squadra] = st.number_input(
                f"Punteggio {squadra}",
                min_value=0,
                step=1,
                key=squadra
            )

        if st.button("💾 Salva giornata"):
            risultati["giornate"][nome_giornata] = nuovi_punteggi
            salva_risultati(risultati)
            st.success(f"{nome_giornata} salvata con successo e inviata su GitHub!")
            st.rerun()
    else:
        if password:
            st.error("Password errata ❌")
        else:
            st.info("Inserisci la password per accedere.")
