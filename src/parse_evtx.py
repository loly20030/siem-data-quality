"""
Semaine 1 — Exploration et parsing des logs Windows
Dataset : EVTX-ATTACK-SAMPLES
"""

import pandas as pd
import os

# ─── Chemins ────────────────────────────────────────────────
RAW_CSV   = "data/raw/EVTX-ATTACK-SAMPLES/evtx_data.csv"
OUTPUT    = "data/validated/logs_clean.csv"

# ─── Colonnes utiles pour notre projet ──────────────────────
# On garde seulement les colonnes pertinentes pour la qualité
COLONNES_UTILES = [
    "EventID",
    "Channel",
    "Computer",
    "SystemTime",
    "ProviderName",
    "Level",
    "EventRecordID",
    "ProcessID",
    "EVTX_FileName",
    "EVTX_Tactic",
    "SubjectUserName",
    "TargetUserName",
    "LogonType",
    "IpAddress",
    "CommandLine",
    "Image",
    "Keywords",
    "Task",
]

def charger_csv(chemin):
    """Charge le CSV brut avec gestion des erreurs."""
    print(f"Chargement de : {chemin}")
    df = pd.read_csv(
        chemin,
        low_memory=False,   # évite les warnings de types mixtes
        index_col=0         # la première colonne est un index
    )
    print(f"  {len(df)} lignes, {len(df.columns)} colonnes chargées")
    return df

def selectionner_colonnes(df, colonnes):
    """Garde uniquement les colonnes qui existent réellement dans le CSV."""
    existantes = [c for c in colonnes if c in df.columns]
    manquantes = [c for c in colonnes if c not in df.columns]

    if manquantes:
        print(f"  Colonnes absentes du CSV : {manquantes}")

    print(f"  {len(existantes)} colonnes sélectionnées")
    return df[existantes]

def analyser_qualite(df):
    """Rapport d'exploration de la qualité des données."""
    print("\n" + "="*55)
    print("  RAPPORT D'EXPLORATION — QUALITÉ DES DONNÉES")
    print("="*55)

    print(f"\n Dimensions : {df.shape[0]} lignes × {df.shape[1]} colonnes")

    print("\n--- Taux de nullité par colonne ---")
    nullite = df.isnull().mean().sort_values(ascending=False)
    for col, pct in nullite.items():
        barre = "█" * int((1 - pct) * 20)
        print(f"  {col:<25} {pct*100:5.1f}% vide   [{barre:<20}]")

    print("\n--- Distribution des EventID (top 10) ---")
    print(df["EventID"].value_counts().head(10).to_string())

    print("\n--- Canaux (Channel) ---")
    print(df["Channel"].value_counts().to_string())

    print("\n--- Tactiques d'attaque (EVTX_Tactic) ---")
    if "EVTX_Tactic" in df.columns:
        print(df["EVTX_Tactic"].value_counts().to_string())

    print("\n--- Plage temporelle ---")
    if "SystemTime" in df.columns:
        # APRÈS — correct
        df = df.copy()
        df["SystemTime"] = pd.to_datetime(df["SystemTime"], errors="coerce")
        print(f"  Début : {df['SystemTime'].min()}")
        print(f"  Fin   : {df['SystemTime'].max()}")
        nulls_time = df["SystemTime"].isnull().sum()
        print(f"  Dates invalides : {nulls_time}")

    print("\n--- Doublons ---")
    cols_doublon = ["EventID", "SystemTime", "Computer"]
    cols_ok = [c for c in cols_doublon if c in df.columns]
    doublons = df.duplicated(subset=cols_ok).sum()
    print(f"  {doublons} doublons sur ({', '.join(cols_ok)})")

    print("\n--- Types de données ---")
    print(df.dtypes.to_string())

def nettoyer(df):
    """Nettoyage de base avant export."""
    df = df.copy()

    # Convertir EventID en entier
    df["EventID"] = pd.to_numeric(df["EventID"], errors="coerce").astype("Int64")

    # Convertir SystemTime en datetime
    if "SystemTime" in df.columns:
        df["SystemTime"] = pd.to_datetime(df["SystemTime"], errors="coerce")

    # Convertir EventRecordID en entier
    if "EventRecordID" in df.columns:
        df["EventRecordID"] = pd.to_numeric(
            df["EventRecordID"], errors="coerce"
        ).astype("Int64")

    # Nettoyer les espaces en trop dans les colonnes texte
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    return df

def sauvegarder(df, chemin):
    """Sauvegarde le DataFrame nettoyé."""
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    df.to_csv(chemin, index=False)
    print(f"\nFichier sauvegardé : {chemin}")
    print(f"  {len(df)} lignes, {len(df.columns)} colonnes")


# ─── Programme principal ─────────────────────────────────────
if __name__ == "__main__":

    # 1. Charger
    df_raw = charger_csv(RAW_CSV)

    # 2. Sélectionner les colonnes utiles
    df = selectionner_colonnes(df_raw, COLONNES_UTILES)

    # 3. Analyser la qualité brute
    analyser_qualite(df)

    # 4. Nettoyer
    df_clean = nettoyer(df)

    # 5. Sauvegarder
    sauvegarder(df_clean, OUTPUT)
