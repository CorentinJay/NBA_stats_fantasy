# 🛠️ WORK IN PROGRESS 🛠️

# 🏀 NBA Stats Fantasy

Application web interactive pour explorer les statistiques des joueurs NBA de la saison en cours.

Fournit des prédictions quotidiennes pour le fantasy basketball :
- **TrashTalk Fantasy League** : https://fantasy.trashtalk.co/
- **SORARE NBA** : https://sorare.com/fr/nba/

👉 **[Voir l'application](https://nba-fantasy-headquarter.streamlit.app)** 👈

---

## 🛠️ PROCESSUS QUOTIDIEN

### BACKEND (Python)

#### 1. API & Web Scraping
- Extraction via l'API NBA (box scores, données personnelles des joueurs, données des équipes et calendrier de la saison)
- Scraping de la liste des blessures (ESPN : https://www.espn.com/nba/injuries)
- Extraction des rosters actifs

#### 2. Data Engineering
- Nettoyage des données
- Engineering de features (statistiques glissantes et spécifiques)
- Tests unitaires et vérifications

#### 3. Modélisation
- Entraînement sur les données historiques
- Prédictions pour les matchs du jour avec les deux méthodes de calcul fantasy
- Conservation uniquement des données nécessaires pour le dashboard
- Commit quotidien vers le dépôt distant (lié à Streamlit Community Cloud)

### FRONTEND

**MISE À JOUR QUOTIDIENNE** : statistiques, liste des blessures et prédictions fantasy

- Dashboard interactif centré sur les joueurs NBA de la saison en cours
- Statistiques des joueurs (saison, carrière et tendances récentes)
- Liste des blessures avec statut officiel (Out ou Game Time Decision)
- Prédictions fantasy (excluant les joueurs "Out") : Trashtalk Fantasy League et SORARE NBA

---

## 📁 STRUCTURE DU PROJET
```
NBA_stats_fantasy/
├── app.py                                # Code du dashboard
├── fantasy_daily_predictions.parquet     # Prédictions fantasy quotidiennes
├── injury_list.parquet                   # Liste des joueurs blessés
├── player_career.parquet                 # Statistiques carrière
├── player_info.parquet                   # Informations personnelles
├── player_season.parquet                 # Statistiques de saison
├── player_trend.parquet                  # Tendances récentes
├── season_schedule.parquet               # Calendrier de la saison
├── .streamlit/config.toml                # Configuration
└── requirements.txt                      # Dépendances
```

---

## 👤 Auteur

**Corentin Jay**

- GitHub : [@CorentinJay](https://github.com/CorentinJay)
- LinkedIn : [corentin-jay](https://www.linkedin.com/in/corentin-jay/)

---

⭐ **Si vous aimez ce projet, donnez-lui une étoile !**