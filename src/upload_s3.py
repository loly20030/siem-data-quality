"""
Semaine 2 — Chargement des données nettoyées vers AWS S3
"""

import boto3
import pandas as pd
import os

# ─── Configuration ───────────────────────────────────────────
BUCKET_NAME  = "siem-data-quality-groupe5"  # ton nom exact de bucket
FICHIER_LOCAL = "data/validated/logs_clean.csv"
CLE_S3_RAW   = "raw/logs_clean.csv"
CLE_S3_INFO  = "raw/dataset_info.txt"

def upload_fichier(s3_client, chemin_local, bucket, cle_s3):
    """Upload un fichier local vers S3."""
    print(f"Upload : {chemin_local} → s3://{bucket}/{cle_s3}")
    s3_client.upload_file(chemin_local, bucket, cle_s3)
    print(f"  OK !")

def generer_info(df, chemin):
    """Génère un fichier texte résumant le dataset."""
    with open(chemin, "w") as f:
        f.write("=== SIEM Data Quality — Résumé du dataset ===\n\n")
        f.write(f"Lignes        : {len(df)}\n")
        f.write(f"Colonnes      : {len(df.columns)}\n")
        f.write(f"Colonnes      : {list(df.columns)}\n\n")
        f.write(f"EventID uniques : {df['EventID'].nunique()}\n")
        systime = pd.to_datetime(df['SystemTime'], errors='coerce')
        f.write(f"Période       : {systime.min()} → {systime.max()}\n")
        f.write(f"Tactiques     : {df['EVTX_Tactic'].unique().tolist()}\n")
        print(f"Fichier info généré : {chemin}")

if __name__ == "__main__":

    # 1. Charger le CSV nettoyé
    print("Chargement du CSV nettoyé...")
    df = pd.read_csv(FICHIER_LOCAL)
    print(f"  {len(df)} lignes chargées")

    # 2. Générer le fichier info
    generer_info(df, "data/validated/dataset_info.txt")

    # 3. Connexion S3
    print("\nConnexion à S3...")
    s3 = boto3.client("s3")

    # 4. Upload des fichiers
    upload_fichier(s3, FICHIER_LOCAL, BUCKET_NAME, CLE_S3_RAW)
    upload_fichier(s3, "data/validated/dataset_info.txt", BUCKET_NAME, CLE_S3_INFO)

    # 5. Vérifier ce qui est dans le bucket
    print("\nContenu du bucket S3 :")
    response = s3.list_objects_v2(Bucket=BUCKET_NAME)
    for obj in response.get("Contents", []):
        taille = obj["Size"] / 1024
        print(f"  {obj['Key']:<40} {taille:.1f} Ko")

    print("\nSemaine 2 terminée — données sur S3 !")
