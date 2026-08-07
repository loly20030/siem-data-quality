"""
Semaine 2 améliorée — Stockage organisé sur AWS S3
Structure : raw/ validated/ reports/ metrics/
"""

import boto3
import pandas as pd
import os

# ─── Configuration ───────────────────────────────────────────
BUCKET = "siem-data-quality-groupe5"

# Fichiers à uploader avec leur destination S3
FICHIERS = {
    # Logs nettoyés (les données brutes sont uploadées une seule fois,
    # manuellement, vers raw/ — elles ne changent pas d'un run à l'autre)
    "data/validated/logs_clean.csv":          "validated/logs_clean.csv",
    # Rapports
    "reports/quality_report.html":            "reports/quality_report.html",
    "reports/quality_report.json":            "reports/quality_report.json",
    # Métriques Power BI
    "reports/metrics_qualite.csv":            "metrics/metrics_qualite.csv",
    "reports/metriques_tactique.csv":         "metrics/metriques_tactique.csv",
    "reports/metriques_canal.csv":            "metrics/metriques_canal.csv",
    "reports/metrics_qualite.parquet":        "metrics/metrics_qualite.parquet",
}

def upload_tous_les_fichiers(s3, fichiers, bucket):
    print(f"\nUpload vers s3://{bucket}/\n")
    ok = 0
    ko = 0
    for local, distant in fichiers.items():
        if os.path.exists(local):
            try:
                s3.upload_file(local, bucket, distant)
                taille = os.path.getsize(local) / 1024
                print(f"  ✅ {distant:<45} {taille:.1f} Ko")
                ok += 1
            except Exception as e:
                print(f"  ❌ {distant} — Erreur : {e}")
                ko += 1
        else:
            print(f"  ⚠️  {local} — Fichier introuvable, ignoré")
    print(f"\n  {ok} fichiers uploadés, {ko} erreurs")

def afficher_contenu_bucket(s3, bucket):
    print(f"\nContenu complet de s3://{bucket}/\n")
    response = s3.list_objects_v2(Bucket=bucket)
    dossiers = {}
    for obj in response.get("Contents", []):
        dossier = obj["Key"].split("/")[0]
        if dossier not in dossiers:
            dossiers[dossier] = []
        dossiers[dossier].append({
            "fichier": obj["Key"],
            "taille":  obj["Size"] / 1024
        })
    for dossier, fichiers in dossiers.items():
        print(f"  📁 {dossier}/")
        for f in fichiers:
            print(f"     {f['fichier']:<50} {f['taille']:.1f} Ko")

if __name__ == "__main__":
    print("Connexion à AWS S3...")
    s3 = boto3.client("s3")

    # Upload de tous les fichiers
    upload_tous_les_fichiers(s3, FICHIERS, BUCKET)

    # Afficher le contenu final du bucket
    afficher_contenu_bucket(s3, BUCKET)

    print("\nCloud S3 organisé et à jour !")
