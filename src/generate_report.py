"""
Rapport HTML amélioré avec graphiques interactifs Plotly
"""

import json
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
from datetime import datetime

# ─── Chemins ────────────────────────────────────────────────
RAPPORT_JSON     = "reports/quality_report.json"
LOGS_CSV         = "data/validated/logs_clean.csv"
TACTIQUE_CSV     = "reports/metriques_tactique.csv"
CANAL_CSV        = "reports/metriques_canal.csv"
RAPPORT_HTML     = "reports/quality_report.html"
HISTORIQUE_JSON  = "reports/historique_scores.json"

def charger_historique():
    """Charge l'historique des scores précédents."""
    if os.path.exists(HISTORIQUE_JSON):
        with open(HISTORIQUE_JSON, "r") as f:
            return json.load(f)
    return []

def sauvegarder_historique(historique, score, timestamp):
    """Ajoute le score actuel à l'historique."""
    historique.append({
        "timestamp": timestamp,
        "score":     score
    })
    with open(HISTORIQUE_JSON, "w") as f:
        json.dump(historique, f, indent=2)

def graphique_jauge(score):
    """Jauge du score global."""
    couleur = "#27ae60" if score >= 80 else "#f39c12" if score >= 60 else "#e74c3c"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Score Global de Qualité", "font": {"size": 18}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar":  {"color": couleur},
            "steps": [
                {"range": [0,  60],  "color": "#fdecea"},
                {"range": [60, 80],  "color": "#fef9e7"},
                {"range": [80, 100], "color": "#eafaf1"},
            ],
            "threshold": {
                "line":  {"color": "black", "width": 3},
                "thickness": 0.75,
                "value": score
            }
        },
        number={"suffix": "%", "font": {"size": 36}}
    ))
    fig.update_layout(height=280, margin=dict(t=50, b=10, l=30, r=30))
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def graphique_completude(resultats):
    """Histogramme de complétude par colonne."""
    df = pd.DataFrame(resultats)
    df = df[df["colonne"] != "EventID+SystemTime+Computer"]
    df = df.sort_values("pct_valide", ascending=True)
    couleurs = ["#27ae60" if s else "#e74c3c" for s in df["succes"]]
    fig = go.Figure(go.Bar(
        x=df["pct_valide"],
        y=df["colonne"],
        orientation="h",
        marker_color=couleurs,
        text=[f"{v:.1f}%" for v in df["pct_valide"]],
        textposition="outside"
    ))
    fig.update_layout(
        title="Complétude par Colonne",
        xaxis=dict(range=[0, 110], title="% Valide"),
        yaxis=dict(title=""),
        height=400,
        margin=dict(t=50, b=30, l=150, r=60)
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def graphique_categories(resultats):
    """Camembert des erreurs par catégorie."""
    df = pd.DataFrame(resultats)
    df_erreurs = df[df["nb_erreurs"] > 0].groupby(
        "categorie")["nb_erreurs"].sum().reset_index()

    if df_erreurs.empty:
        df_erreurs = pd.DataFrame({
            "categorie": ["Aucune erreur"],
            "nb_erreurs": [1]
        })

    fig = px.pie(
        df_erreurs,
        names="categorie",
        values="nb_erreurs",
        title="Répartition des Erreurs par Catégorie",
        color_discrete_sequence=["#e74c3c", "#f39c12", "#3498db", "#9b59b6"]
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=350, margin=dict(t=50, b=10, l=10, r=10))
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def graphique_tactiques(chemin_csv):
    """Barres par tactique d'attaque."""
    df = pd.read_csv(chemin_csv)
    df = df.sort_values("nb_logs", ascending=True)
    fig = go.Figure(go.Bar(
        x=df["nb_logs"],
        y=df["EVTX_Tactic"],
        orientation="h",
        marker_color="#3498db",
        text=df["nb_logs"],
        textposition="outside"
    ))
    fig.update_layout(
        title="Distribution par Tactique d'Attaque",
        xaxis=dict(title="Nombre de logs"),
        yaxis=dict(title=""),
        height=400,
        margin=dict(t=50, b=30, l=180, r=60)
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def graphique_historique(historique):
    """Courbe d'évolution du score dans le temps."""
    if len(historique) < 2:
        return "<p style='color:#888;text-align:center;padding:40px;'>"\
               "Pas encore assez de données pour l'évolution temporelle."\
               "<br>Relance le pipeline plusieurs fois pour voir la courbe.</p>"

    df = pd.DataFrame(historique)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    fig = go.Figure(go.Scatter(
        x=df["timestamp"],
        y=df["score"],
        mode="lines+markers",
        line=dict(color="#3498db", width=2),
        marker=dict(size=8, color="#2980b9"),
        fill="tozeroy",
        fillcolor="rgba(52,152,219,0.1)"
    ))
    fig.add_hline(y=80, line_dash="dash",
                  line_color="#27ae60", annotation_text="Seuil 80%")
    fig.update_layout(
        title="Évolution du Score de Qualité dans le Temps",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Score (%)", range=[0, 105]),
        height=350,
        margin=dict(t=50, b=30, l=60, r=30)
    )
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def graphique_canaux(chemin_csv):
    """Camembert des logs par canal Windows."""
    df = pd.read_csv(chemin_csv)
    # Raccourcir les noms longs
    df["Channel_court"] = df["Channel"].apply(
        lambda x: x.split("/")[0].replace("Microsoft-Windows-", "MW-")
    )
    fig = px.pie(
        df,
        names="Channel_court",
        values="nb_logs",
        title="Logs par Canal Windows",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(height=380, margin=dict(t=50, b=10, l=10, r=10))
    return pio.to_html(fig, full_html=False, include_plotlyjs=False)

def generer_tableau(resultats):
    """Tableau HTML des 15 règles."""
    lignes = ""
    for r in resultats:
        statut = "✅ OK" if r["succes"] else "❌ KO"
        couleur_ligne = "#f0faf4" if r["succes"] else "#fef0f0"
        couleur_barre = "#27ae60" if r["succes"] else "#e74c3c"
        pct = r["pct_valide"]
        lignes += f"""
        <tr style="background:{couleur_ligne}">
          <td><b>{r['regle']}</b></td>
          <td>{r['description']}</td>
          <td><code>{r['colonne']}</code></td>
          <td style="color:#666;font-size:13px;">{r.get('categorie','—')}</td>
          <td>
            <div style="background:#eee;border-radius:4px;
                        height:16px;width:120px;display:inline-block;">
              <div style="background:{couleur_barre};width:{min(pct,100)}%;
                          height:16px;border-radius:4px;"></div>
            </div>
            <span style="margin-left:6px;font-size:13px;">{pct:.1f}%</span>
          </td>
          <td style="text-align:center;font-weight:bold;
                     color:{'#e74c3c' if r['nb_erreurs']>0 else '#27ae60'};">
            {r['nb_erreurs']:,}
          </td>
          <td style="text-align:center;font-size:18px;">{statut}</td>
        </tr>"""
    return lignes

def generer_html(rapport, graphiques):
    """Génère le HTML complet."""
    score = rapport["score_global"]
    nb_ok = rapport["nb_ok"]
    nb_ko = rapport["nb_regles"] - nb_ok
    nb_total = rapport["nb_regles"]
    nb_enregistrements = rapport.get("nb_enregistrements", 0)
    nb_anomalies = rapport.get("nb_anomalies", 0)
    couleur_score = "#27ae60" if score >= 80 else \
                    "#f39c12" if score >= 60 else "#e74c3c"
    mention = "Bonne qualité ✓" if score >= 80 else \
              "Qualité moyenne ⚠" if score >= 60 else "Qualité insuffisante ✗"
    tableau = generer_tableau(rapport["resultats"])

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Rapport Qualité SIEM — Groupe 5</title>
  <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  <style>
    *{{box-sizing:border-box;margin:0;padding:0;}}
    body{{font-family:'Segoe UI',Arial,sans-serif;
          background:#f0f2f5;color:#2c3e50;}}

    .header{{background:linear-gradient(135deg,#1a252f,#2980b9);
             color:white;padding:30px 40px;}}
    .header h1{{font-size:26px;margin-bottom:6px;}}
    .header p{{opacity:0.8;font-size:13px;}}

    .container{{max-width:1400px;margin:0 auto;padding:24px;}}

    .cards{{display:flex;gap:16px;margin-bottom:24px;flex-wrap:wrap;}}
    .card{{background:white;border-radius:12px;padding:20px 24px;
           flex:1;min-width:150px;text-align:center;
           box-shadow:0 2px 10px rgba(0,0,0,0.08);}}
    .card .val{{font-size:38px;font-weight:bold;margin-bottom:4px;}}
    .card .lbl{{color:#7f8c8d;font-size:12px;text-transform:uppercase;
                letter-spacing:0.5px;}}

    .grid-2{{display:grid;grid-template-columns:1fr 1fr;
             gap:20px;margin-bottom:20px;}}
    .grid-3{{display:grid;grid-template-columns:1fr 1fr 1fr;
             gap:20px;margin-bottom:20px;}}
    .panel{{background:white;border-radius:12px;padding:20px;
            box-shadow:0 2px 10px rgba(0,0,0,0.08);}}

    table{{width:100%;border-collapse:collapse;}}
    th{{background:#2c3e50;color:white;padding:12px 14px;
        text-align:left;font-size:12px;text-transform:uppercase;
        letter-spacing:0.5px;}}
    td{{padding:11px 14px;border-bottom:1px solid #f0f0f0;
        font-size:13px;vertical-align:middle;}}
    tr:hover td{{background:rgba(0,0,0,0.02)!important;}}

    .badge{{display:inline-block;padding:3px 10px;border-radius:20px;
            font-size:11px;font-weight:bold;}}
    .badge-ok{{background:#eafaf1;color:#27ae60;}}
    .badge-ko{{background:#fdecea;color:#e74c3c;}}

    .footer{{text-align:center;padding:24px;color:#95a5a6;font-size:12px;}}

    @media(max-width:768px){{
      .grid-2,.grid-3{{grid-template-columns:1fr;}}
      .cards{{flex-direction:column;}}
    }}
  </style>
</head>
<body>

<div class="header">
  <h1>📊 Rapport de Qualité des Données — SIEM Simplifié</h1>
  <p>Groupe 5 &nbsp;|&nbsp; Dataset : EVTX-ATTACK-SAMPLES &nbsp;|&nbsp;
     Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')} &nbsp;|&nbsp;
     {f'{nb_enregistrements:,}'.replace(',', ' ')} enregistrements · {nb_total} règles de qualité</p>
</div>

<div class="container">

  <!-- Cartes résumé -->
  <div class="cards">
    <div class="card">
      <div class="val" style="color:{couleur_score};">{score:.0f}%</div>
      <div class="lbl">Score Global<br><b>{mention}</b></div>
    </div>
    <div class="card">
      <div class="val" style="color:#27ae60;">{nb_ok}</div>
      <div class="lbl">Règles Passées</div>
    </div>
    <div class="card">
      <div class="val" style="color:#e74c3c;">{nb_ko}</div>
      <div class="lbl">Règles Échouées</div>
    </div>
    <div class="card">
      <div class="val" style="color:#3498db;">{nb_total}</div>
      <div class="lbl">Règles Totales</div>
    </div>
    <div class="card">
      <div class="val" style="color:#9b59b6;">{f'{nb_enregistrements:,}'.replace(',', ' ')}</div>
      <div class="lbl">Enregistrements</div>
    </div>
    <div class="card">
      <div class="val" style="color:#e67e22;">{f'{nb_anomalies:,}'.replace(',', ' ')}</div>
      <div class="lbl">Anomalies Détectées</div>
    </div>
  </div>

  <!-- Jauge + Complétude -->
  <div class="grid-2">
    <div class="panel">{graphiques['jauge']}</div>
    <div class="panel">{graphiques['completude']}</div>
  </div>

  <!-- Catégories + Tactiques -->
  <div class="grid-2">
    <div class="panel">{graphiques['categories']}</div>
    <div class="panel">{graphiques['tactiques']}</div>
  </div>

  <!-- Canaux + Historique -->
  <div class="grid-2">
    <div class="panel">{graphiques['canaux']}</div>
    <div class="panel">{graphiques['historique']}</div>
  </div>

  <!-- Tableau des 15 règles -->
  <div class="panel" style="margin-bottom:20px;">
    <h3 style="margin-bottom:16px;color:#2c3e50;">
      📋 Détail des {nb_total} Règles de Qualité
    </h3>
    <table>
      <thead>
        <tr>
          <th>Règle</th>
          <th>Description</th>
          <th>Colonne</th>
          <th>Catégorie</th>
          <th>% Valide</th>
          <th>Erreurs</th>
          <th>Statut</th>
        </tr>
      </thead>
      <tbody>{tableau}</tbody>
    </table>
  </div>

</div>

<div class="footer">
  Rapport généré automatiquement par Great Expectations &amp; Python —
  Groupe 5 — {datetime.now().strftime('%Y')}
</div>

</body>
</html>"""

if __name__ == "__main__":
    # Charger les données
    with open(RAPPORT_JSON, "r") as f:
        rapport = json.load(f)

    # Charger et sauvegarder l'historique
    historique = charger_historique()
    sauvegarder_historique(
        historique,
        rapport["score_global"],
        rapport["timestamp"]
    )

    # Générer tous les graphiques
    print("Génération des graphiques...")
    graphiques = {
        "jauge":      graphique_jauge(rapport["score_global"]),
        "completude": graphique_completude(rapport["resultats"]),
        "categories": graphique_categories(rapport["resultats"]),
        "tactiques":  graphique_tactiques(TACTIQUE_CSV),
        "historique": graphique_historique(historique),
        "canaux":     graphique_canaux(CANAL_CSV),
    }

    # Générer le HTML
    html = generer_html(rapport, graphiques)

    # Sauvegarder
    os.makedirs("reports", exist_ok=True)
    with open(RAPPORT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Rapport HTML généré : {RAPPORT_HTML}")
    print("Ouverture dans le navigateur...")
