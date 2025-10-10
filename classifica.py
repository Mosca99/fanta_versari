# --- Calcolo classifica generale basata sui bonus ---
def calcola_classifica_generale(df_giornate):
    if df_giornate.empty:
        return pd.DataFrame(columns=["Posizione", "Squadra", "Totale Bonus"])
    
    # Somma solo dei bonus
    df_classifica = (
        df_giornate.groupby("Squadra")["Bonus"]
        .sum()
        .reset_index()
        .sort_values(by="Bonus", ascending=False)
    )
    df_classifica["Posizione"] = range(1, len(df_classifica)+1)
    return df_classifica[["Posizione", "Squadra", "Bonus"]]
