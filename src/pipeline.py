"""
Semaine 5 — Pipeline automatisé complet
Lance toutes les étapes en une seule commande :
python src/pipeline.py
"""

import subprocess
import sys
import os
import json
from datetime import datetime

# ─── Configuration ───────────────────────────────────────────
LOG_FILE = "reports/pipeline.log"

def log(message, niveau="INFO"):
    """Écrit dans le terminal ET dans un fichier log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ligne = f"[{timestamp}] [{niveau}] {message}"
    print(ligne)
    with open(LOG_FILE, "a") as f:
        f.write(ligne + "\n")

def lancer_script(script, description):
    """Lance un script Python et retourne True si succès."""
    log(f"Démarrage : {description}")
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        if result.returncode == 0:
            log(f"✅ {description} — OK")
            return True
        else:
            log(f"❌ {description} — ERREUR", "ERROR")
            log(result.stderr, "ERROR")
            return False
    except Exception as e:
        log(f"❌ {description} — Exception : {e}", "ERROR")
        return False

def afficher_resume():
    """Affiche un résumé du pipeline à la fin."""
    try:
        with open("reports/quality_report.json", "r") as f:
            rapport = json.load(f)
        score = rapport["score_global"]
        nb_ok = rapport["nb_ok"]
        nb_total = rapport["nb_regles"]
        couleur = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        log("=" * 55)
        log(f"  RÉSUMÉ DU PIPELINE")
        log("=" * 55)
        log(f"  Score qualité  : {couleur} {score}%")
        log(f"  Règles passées : {nb_ok}/{nb_total}")
        log(f"  Rapport HTML   : reports/quality_report.html")
        log(f"  Rapport JSON   : reports/quality_report.json")
        log(f"  Log pipeline   : {LOG_FILE}")
        log("=" * 55)
    except Exception as e:
        log(f"Impossible de lire le rapport : {e}", "ERROR")

if __name__ == "__main__":
    # Créer le dossier reports si absent
    os.makedirs("reports", exist_ok=True)

    # En-tête du log
    log("=" * 55)
    log("  PIPELINE SIEM DATA QUALITY — GROUPE 5")
    log(f"  Démarrage : {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
    log("=" * 55)

    # Définir les étapes dans l'ordre
    etapes = [
        ("src/parse_evtx.py",      "Étape 1 — Parsing et nettoyage des logs"),
        ("src/quality_checks.py",  "Étape 2 — Tests Great Expectations (15 règles)"),
        ("src/generate_report.py", "Étape 3 — Génération du rapport HTML"),
        ("src/export_metrics.py",  "Étape 4 — Export métriques CSV/Parquet"),
        ("src/upload_s3.py",       "Étape 5 — Upload vers AWS S3"),
    ]

    # Lancer chaque étape
    resultats = []
    for script, description in etapes:
        succes = lancer_script(script, description)
        resultats.append(succes)
        if not succes:
            log(f"Pipeline arrêté à : {description}", "ERROR")
            log("Corrige l'erreur et relance : python src/pipeline.py")
            sys.exit(1)

    # Résumé final
    afficher_resume()
    log("Pipeline terminé avec succès !")
    log(f"Ouvre le rapport : xdg-open reports/quality_report.html")
