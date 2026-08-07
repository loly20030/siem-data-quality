"""
Semaine 4 — Export des métriques de qualité vers CSV et Parquet
Pour alimentation du dashboard Power BI
"""

import json
import pandas as pd
import os
from datetime import datetime

# ─── Chemins ────────────────────────────────────────────────
RAPPORT_JSON    = "reports/quality_report.json"
LOGS_CSV        = "data/validated/logs_clean.csv"
EXPORT_CSV      = "reports/metrics_qualite.csv"
EXPORT_PARQUET  = "reports/metrics_qualite.parquet"

def exporter_metriques_regles(rapport):
    """
    Transforme les résultats des 15 règles en DataFrame exportable.
    C'est ce que Power BI va lire pour le dashboard.
    """
    lignes = []
    for r in rapport["resultats"]:
        lignes.append({
            "timestamp":      rapport["timestamp"],
            "regle":          r["regle"],
            "description":    r["description"],
            "colonne":        r["colonne"],
            "succes":         r["succes"],
            "pct_valide":     r["pct_valide"],
            "pct_erreur":     round(100 - r["pct_valide"], 2),
            "nb_erreurs":     r["nb_erreurs"],
            "score_global":   rapport["score_global"],
            "categorie":      categoriser_regle(r["regle"])
        })
    return pd.DataFrame(lignes)

def categoriser_regle(regle):
    """Catégorise chaque règle pour le dashboard Power BI."""
    categories = {
        "R01": "Complétude",
        "R02": "Complétude",
        "R03": "Complétude",
        "R04": "Validité",
        "R05": "Validité",
        "R06": "Complétude",
        "R07": "Format",
        "R08": "Unicité",
        "R09": "Complétude",
        "R10": "Validité",
        "R11": "Validité",
        "R12": "Validité",
        "R13": "Complétude",
        "R14": "Unicité",
        "R15": "Complétude"
    }
    return categories.get(regle, "Autre")

def exporter_metriques_logs(df_logs):
    """
    Calcule des métriques supplémentaires sur les logs bruts.
    Utile pour les visualisations Power BI.
    """
    # Métriques par tactique d'attaque
    par_tactique = df_logs.groupby("EVTX_Tactic").agg(
        nb_logs=("EventID", "count"),
        nb_eventid_uniques=("EventID", "nunique"),
        nb_machines=("Computer", "nunique")
    ).reset_index()
    par_tactique["timestamp"] = datetime.now().isoformat()

    # Métriques par canal
    par_canal = df_logs.groupby("Channel").agg(
        nb_logs=("EventID", "count")
    ).reset_index()
    par_canal["pct"] = round(
        par_canal["nb_logs"] / par_canal["nb_logs"].sum() * 100, 2
    )
    par_canal["timestamp"] = datetime.now().isoformat()

    return par_tactique, par_canal

if __name__ == "__main__":

    # 1. Charger le rapport JSON des règles
    print("Chargement du rapport JSON...")
    with open(RAPPORT_JSON, "r") as f:
        rapport = json.load(f)

    # 2. Charger les logs nettoyés
    print("Chargement des logs nettoyés...")
    df_logs = pd.read_csv(LOGS_CSV, low_memory=False)
    print(f"  {len(df_logs)} lignes")

    # 3. Exporter les métriques des règles
    print("\nExport des métriques des règles...")
    df_metriques = exporter_metriques_regles(rapport)
    print(df_metriques[["regle", "description", "pct_valide",
                          "nb_erreurs", "categorie"]].to_string(index=False))

    # 4. Exporter les métriques des logs
    print("\nExport des métriques par tactique...")
    df_tactique, df_canal = exporter_metriques_logs(df_logs)
    print(df_tactique.to_string(index=False))

    # 5. Sauvegarder en CSV (pour Power BI)
    os.makedirs("reports", exist_ok=True)
    df_metriques.to_csv(EXPORT_CSV, index=False)
    df_tactique.to_csv("reports/metriques_tactique.csv", index=False)
    df_canal.to_csv("reports/metriques_canal.csv", index=False)
    print(f"\nCSV sauvegardé : {EXPORT_CSV}")
    print(f"CSV sauvegardé : reports/metriques_tactique.csv")
    print(f"CSV sauvegardé : reports/metriques_canal.csv")

    # 6. Sauvegarder en Parquet (format optimisé)
    df_metriques.to_parquet(EXPORT_PARQUET, index=False)
    print(f"Parquet sauvegardé : {EXPORT_PARQUET}")

    print("\nSemaine 4 — Export terminé !")
    print("Ces fichiers CSV sont prêts à être importés dans Power BI.")
