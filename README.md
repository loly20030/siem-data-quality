# 🛡️ SIEM Data Quality — Groupe 5

Système automatisé de contrôle de la qualité sur des logs Windows
(SIEM simplifié) — Projet Data Engineering

---

## 📋 Description

Ce projet met en place un pipeline de data quality appliqué à des logs
d'événements Windows issus de simulations d'attaques réelles (MITRE ATT&CK).
Il détecte automatiquement les anomalies, génère des rapports visuels
et stocke les données sur AWS S3.

---

## 🏗️ Architecture

```
EVTX-ATTACK-SAMPLES (GitHub)
        │
        ▼
parse_evtx.py         — Parsing & nettoyage
        │
        ▼
quality_checks.py     — 15 règles Great Expectations
        │
        ▼
generate_report.py    — Rapport HTML interactif
        │
        ▼
export_metrics.py     — CSV/Parquet pour Power BI
        │
        ▼
upload_s3.py           — Stockage AWS S3 (logs validés + rapports + métriques)
```

---

## 🗂️ Structure du projet

```
siem-data-quality/
├── src/
│   ├── parse_evtx.py         # Parsing et nettoyage des logs
│   ├── upload_s3.py          # Upload vers AWS S3
│   ├── quality_checks.py     # 15 règles Great Expectations
│   ├── generate_report.py    # Rapport HTML interactif
│   ├── export_metrics.py     # Export CSV/Parquet Power BI
│   └── pipeline.py           # Pipeline automatisé complet
├── data/
│   ├── raw/                  # Dataset EVTX-ATTACK-SAMPLES
│   └── validated/            # Logs nettoyés (4633 lignes)
├── reports/
│   ├── quality_report.html   # Rapport HTML interactif
│   ├── quality_report.json   # Résultats JSON
│   ├── metrics_qualite.csv   # Métriques Power BI
│   ├── metriques_tactique.csv
│   ├── metriques_canal.csv
│   └── pipeline.log          # Log d'exécution
├── dashboard/                 # Fichier Power BI (.pbix)
├── docs/
│   ├── rapport_siem.tex      # Rapport LaTeX
│   └── guide_demarrage_projet.md
├── great_expectations/        # Configuration GE
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

- **Source** : [EVTX-ATTACK-SAMPLES](https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES)
- **Format** : EVTX (logs Windows) + CSV pré-parsé
- **Volume** : 278 fichiers EVTX · 4 633 enregistrements · 18 colonnes
- **Période** : 2017 → 2021
- **Tactiques** : 8 catégories MITRE ATT&CK

---

## ⚙️ Stack Technique

| Outil | Rôle |
|-------|------|
| Python 3.12 | Langage principal |
| pandas | Manipulation des données |
| python-evtx | Décodage fichiers EVTX |
| Great Expectations | Tests de qualité |
| boto3 | Connexion AWS S3 |
| plotly | Graphiques interactifs |
| AWS S3 | Stockage cloud |
| Power BI Desktop | Dashboard de qualité |

---

## 🚀 Installation

```bash
# Cloner le projet
git clone https://github.com/loly20030/siem-data-quality.git
cd siem-data-quality

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer AWS
aws configure
```

---

## ▶️ Utilisation

### Lancer le pipeline complet en une commande
```bash
python src/pipeline.py
```

### Ou étape par étape
```bash
python src/parse_evtx.py       # Parsing & nettoyage
python src/quality_checks.py   # GE — 15 règles de qualité
python src/generate_report.py  # Rapport HTML interactif
python src/export_metrics.py   # Export CSV/Parquet pour Power BI
python src/upload_s3.py        # Upload final vers AWS S3
```

### Ouvrir le rapport HTML
```bash
xdg-open reports/quality_report.html
```

---

## ✅ Résultats des Tests de Qualité

**Score global : 80% — 12/15 règles passées**

| Règle | Description | Statut |
|-------|-------------|--------|
| R01 | EventID non vide | ✅ OK |
| R02 | Computer non vide | ✅ OK |
| R03 | Channel non vide | ✅ OK |
| R04 | EventID entre 1 et 65535 | ✅ OK |
| R05 | Channel dans liste connue | ✅ OK |
| R06 | SystemTime non vide | ❌ KO — 355 erreurs |
| R07 | SystemTime format valide | ❌ KO — 355 erreurs |
| R08 | Pas de doublons | ❌ KO — 1370 doublons |
| R09 | EVTX_Tactic non vide | ✅ OK |
| R10 | Level entre 0 et 5 | ✅ OK |
| R11 | Computer sans caractères invalides | ✅ OK |
| R12 | ProcessID positif | ✅ OK |
| R13 | ProviderName non vide | ✅ OK |
| R14 | EventRecordID unique par fichier | ✅ OK |
| R15 | Level non vide | ✅ OK |

---

## ☁️ AWS S3

Bucket : `siem-data-quality-groupe5` (eu-north-1)

```
s3://siem-data-quality-groupe5/
├── validated/   ← logs nettoyés
├── reports/     ← rapports HTML et JSON
├── metrics/     ← CSV pour Power BI
└── raw/         ← données brutes
```

---

## 👥 Groupe 5

Projet Data Engineering — 2026
