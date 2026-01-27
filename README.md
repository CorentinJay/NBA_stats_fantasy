### 🛠️ - WORK IN PROGRESS - 🛠️ ###



### 🏀 NBA Stats Fantasy

Interactive web app to explore NBA players stats for the current season.
Provide daily predictions for fantasy basketball : 
- TrashTalk Fantasy League (https://fantasy.trashtalk.co/)
- SORARE NBA (https://sorare.com/fr/nba/)


👉 **[Voir l'application](https://nba-fantasy-headquarter.streamlit.app)** 👈


### 🛠️ DAILY PROCESS 💻

## BACKEND (Python)
1. API & Web scrapping
NBA API extraction (box scores, players personal data, team data & season schedule)
Injury list scrapping (ESPN : https://www.espn.com/nba/injuries)
Active rosters extraction

2. Data engineering
Data cleaning
Data engineering (rolling and specific stats)
Unit tests and checks

3. Modeling
Training on historical data, predicting on today's games for both fantasy calculation methods
Keeping only needed data for the dashboard
Committing to the remote repository every morning (linked to Streamlit Community Cloud)

## FRONTEND
DAILY UPDATE FOR BOTH STATISTICS, INJURY LIST AND FANTASY PREDICTIONS
Interactive dashboard focused on NBA players for the current season
Players statistics (both season, career and recent trends)
Injury list with official status (Out or Game Time Decision)
Fantasy predictions (excluding players with 'Out' status) : Trashtalk Fantasy League and SORARE NBA


### 🛠️ STRUCTURE 💻

NBA_stats_fantasy/
├── app.py                                          # dashboard code
├── fantasy_daily_predictions.parquet               # parquet : daily fantasy predictions
├── injury_list.parquet                             # parquet : injured players
├── player_career.parquet                           # parquet : career players stats
├── player_info.parquet                             # parquet : players personal info
├── player_season.parquet                           # parquet : season players stats
├── player_trend.parquet                            # parquet : season players recent trends
├── season_schedule.parquet                         # parquet : season schedule
├── .streamlit/config.toml                          # Configuration
└── requirements.txt                                # Dépendances



## 👤 Author

**Corentin Jay**

- GitHub: [@CorentinJay] https://github.com/CorentinJay
- Linkedin : https://www.linkedin.com/in/corentin-jay/


⭐ If you like this repo, give it a star !