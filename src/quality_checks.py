"""
Semaine 3 — Tests de qualité avec Great Expectations
10 règles de validation sur les logs Windows
"""

import great_expectations as ge
import pandas as pd
import json
import os
from datetime import datetime

# ─── Chemins ────────────────────────────────────────────────
FICHIER_LOGS = "data/validated/logs_clean.csv"
RAPPORT_JSON = "reports/quality_report.json"

# ─── Chargement des données ─────────────────────────────────
def charger_donnees(chemin):
    print(f"Chargement : {chemin}")
    df = pd.read_csv(chemin, low_memory=False)
    print(f"  {len(df)} lignes chargées")
    return df

# ─── Les 10 règles de qualité ───────────────────────────────
def appliquer_regles(df):
    """
    Applique les 10 règles de qualité sur le DataFrame.
    Retourne un dictionnaire avec les résultats.
    """
    # Convertir en DataFrame Great Expectations
    gdf = ge.from_pandas(df)

    resultats = []

    print("\nApplication des 10 règles de qualité...\n")

    # ── Règle 1 : EventID non null ───────────────────────────
    r = gdf.expect_column_values_to_not_be_null("EventID")
    resultats.append({
        "regle": "R01",
        "description": "EventID ne doit pas être vide",
        "colonne": "EventID",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 2 : Computer non null ──────────────────────────
    r = gdf.expect_column_values_to_not_be_null("Computer")
    resultats.append({
        "regle": "R02",
        "description": "Computer ne doit pas être vide",
        "colonne": "Computer",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 3 : Channel non null ───────────────────────────
    r = gdf.expect_column_values_to_not_be_null("Channel")
    resultats.append({
        "regle": "R03",
        "description": "Channel ne doit pas être vide",
        "colonne": "Channel",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 4 : EventID entre 1 et 65535 ──────────────────
    r = gdf.expect_column_values_to_be_between(
        "EventID", min_value=1, max_value=65535
    )
    resultats.append({
        "regle": "R04",
        "description": "EventID doit être entre 1 et 65535",
        "colonne": "EventID",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 5 : Channel dans liste connue ──────────────────
    canaux_valides = [
        "Security",
        "System",
        "Application",
        "Microsoft-Windows-Sysmon/Operational",
        "Microsoft-Windows-TerminalServices-RemoteConnectionManager/Operational",
        "Microsoft-Windows-RemoteDesktopServices-RdpCoreTS/Operational",
        "Microsoft-Windows-Bits-Client/Operational",
        "Microsoft-Windows-WinRM/Operational",
        "Microsoft-Windows-PowerShell/Operational",
        "Microsoft-Windows-Application-Experience/Program-Telemetry",
        "Microsoft-Windows-Application-Experience/Program-Compatibility-Assistant",
        "Microsoft-Windows-Winsock-WS2HELP/Operational"
    ]
    r = gdf.expect_column_values_to_be_in_set("Channel", canaux_valides)
    resultats.append({
        "regle": "R05",
        "description": "Channel doit être dans la liste des canaux connus",
        "colonne": "Channel",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 6 : SystemTime non null ────────────────────────
    r = gdf.expect_column_values_to_not_be_null("SystemTime")
    resultats.append({
        "regle": "R06",
        "description": "SystemTime ne doit pas être vide",
        "colonne": "SystemTime",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 7 : SystemTime format datetime valide ──────────
    df_temp = df.copy()
    df_temp["SystemTime"] = pd.to_datetime(
        df_temp["SystemTime"], errors="coerce"
    )
    nb_invalides = df_temp["SystemTime"].isnull().sum()
    pct_valide = 100 - (nb_invalides / len(df_temp) * 100)
    resultats.append({
        "regle": "R07",
        "description": "SystemTime doit être une date valide",
        "colonne": "SystemTime",
        "succes": nb_invalides == 0,
        "pct_valide": round(pct_valide, 2),
        "nb_erreurs": int(nb_invalides)
    })

    # ── Règle 8 : Pas de doublons ────────────────────────────
    cols_doublon = ["EventID", "SystemTime", "Computer"]
    nb_doublons = df.duplicated(subset=cols_doublon).sum()
    pct_valide = 100 - (nb_doublons / len(df) * 100)
    resultats.append({
        "regle": "R08",
        "description": "Pas de doublons sur (EventID, SystemTime, Computer)",
        "colonne": "EventID+SystemTime+Computer",
        "succes": nb_doublons == 0,
        "pct_valide": round(pct_valide, 2),
        "nb_erreurs": int(nb_doublons)
    })

    # ── Règle 9 : EVTX_Tactic non null ──────────────────────
    r = gdf.expect_column_values_to_not_be_null("EVTX_Tactic")
    resultats.append({
        "regle": "R09",
        "description": "EVTX_Tactic (tactique d'attaque) ne doit pas être vide",
        "colonne": "EVTX_Tactic",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })

    # ── Règle 10 : Level entre 0 et 5 ───────────────────────
    r = gdf.expect_column_values_to_be_between(
        "Level", min_value=0, max_value=5
    )
    resultats.append({
        "regle": "R10",
        "description": "Level doit être entre 0 et 5",
        "colonne": "Level",
        "succes": r.success,
        "pct_valide": 100 - (r.result.get("unexpected_percent", 0) or 0),
        "nb_erreurs": r.result.get("unexpected_count", 0) or 0
    })
# ── Règle 11 : Computer ne contient pas de caractères invalides ──
    r = gdf.expect_column_values_to_match_regex(
        "Computer", r'^[a-zA-Z0-9\-\.\_]+$'
    )
    resultats.append({
        "regle":       "R11",
        "description": "Computer ne contient pas de caractères invalides",
        "colonne":     "Computer",
        "succes":      bool(r.success),
        "pct_valide":  float(100 - (r.result.get("unexpected_percent", 0) or 0)),
        "nb_erreurs":  int(r.result.get("unexpected_count", 0) or 0)
    })

    # ── Règle 12 : ProcessID est un nombre positif ───────────────────
    df_pid = df.copy()
    df_pid["ProcessID"] = pd.to_numeric(df_pid["ProcessID"], errors="coerce")
    nb_pid_invalides = (df_pid["ProcessID"] < 0).sum()
    pct_pid = 100 - (nb_pid_invalides / len(df_pid) * 100)
    resultats.append({
        "regle":       "R12",
        "description": "ProcessID doit être un nombre positif",
        "colonne":     "ProcessID",
        "succes":      bool(nb_pid_invalides == 0),
        "pct_valide":  round(float(pct_pid), 2),
        "nb_erreurs":  int(nb_pid_invalides)
    })

    # ── Règle 13 : ProviderName non null ────────────────────────────
    r = gdf.expect_column_values_to_not_be_null("ProviderName")
    resultats.append({
        "regle":       "R13",
        "description": "ProviderName ne doit pas être vide",
        "colonne":     "ProviderName",
        "succes":      bool(r.success),
        "pct_valide":  float(100 - (r.result.get("unexpected_percent", 0) or 0)),
        "nb_erreurs":  int(r.result.get("unexpected_count", 0) or 0)
    })

    # ── Règle 14 : EventRecordID est unique par fichier source ───────
    nb_doublons_record = df.duplicated(
        subset=["EventRecordID", "EVTX_FileName"]
    ).sum()
    pct_record = 100 - (nb_doublons_record / len(df) * 100)
    resultats.append({
        "regle":       "R14",
        "description": "EventRecordID unique par fichier source",
        "colonne":     "EventRecordID",
        "succes":      bool(nb_doublons_record == 0),
        "pct_valide":  round(float(pct_record), 2),
        "nb_erreurs":  int(nb_doublons_record)
    })

    # ── Règle 15 : Level non null ────────────────────────────────────
    r = gdf.expect_column_values_to_not_be_null("Level")
    resultats.append({
        "regle":       "R15",
        "description": "Level ne doit pas être vide",
        "colonne":     "Level",
        "succes":      bool(r.success),
        "pct_valide":  float(100 - (r.result.get("unexpected_percent", 0) or 0)),
        "nb_erreurs":  int(r.result.get("unexpected_count", 0) or 0)
    })

    return resultats

# ─── Affichage des résultats ────────────────────────────────
def afficher_resultats(resultats):
    print("=" * 60)
    print("  RAPPORT DE QUALITÉ — GREAT EXPECTATIONS")
    print("=" * 60)

    nb_ok  = sum(1 for r in resultats if r["succes"])
    nb_ko  = len(resultats) - nb_ok
    score  = (nb_ok / len(resultats)) * 100

    print(f"\n Score global : {score:.0f}% ({nb_ok}/{len(resultats)} règles passées)\n")
    print(f"  {'Règle':<6} {'Description':<45} {'%Valide':>8} {'Erreurs':>8} {'Statut'}")
    print(f"  {'-'*6} {'-'*45} {'-'*8} {'-'*8} {'-'*6}")

    for r in resultats:
        statut = "✅ OK" if r["succes"] else "❌ KO"
        print(f"  {r['regle']:<6} {r['description']:<45} "
              f"{r['pct_valide']:>7.1f}% {r['nb_erreurs']:>8} {statut}")

    print(f"\n {nb_ok} règles passées, {nb_ko} règles échouées")

# ─── Sauvegarde JSON ────────────────────────────────────────
def sauvegarder_rapport(resultats, chemin):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)

    # Convertir les types numpy en types Python natifs
    resultats_clean = []
    for r in resultats:
        resultats_clean.append({
            "regle":       str(r["regle"]),
            "description": str(r["description"]),
            "colonne":     str(r["colonne"]),
            "succes":      bool(r["succes"]),
            "pct_valide":  float(r["pct_valide"]),
            "nb_erreurs":  int(r["nb_erreurs"])
        })

    rapport = {
        "timestamp":    datetime.now().isoformat(),
        "nb_regles":    len(resultats_clean),
        "nb_ok":        sum(1 for r in resultats_clean if r["succes"]),
        "score_global": round(
            sum(1 for r in resultats_clean if r["succes"]) / len(resultats_clean) * 100, 2
        ),
        "resultats": resultats_clean
    }

    with open(chemin, "w") as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)

    print(f"\nRapport JSON sauvegardé : {chemin}")
# ─── Programme principal ────────────────────────────────────
if __name__ == "__main__":
    df = charger_donnees(FICHIER_LOGS)
    resultats = appliquer_regles(df)
    afficher_resultats(resultats)
    sauvegarder_rapport(resultats, RAPPORT_JSON)
