import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(
    page_title="NBA Stats Fantasy",
    page_icon="🏀",
    layout="wide",
    initial_sidebar_state="expanded"
)

NBA_BLUE = "#1D428A"
NBA_RED = "#C8102E"
NBA_WHITE = "#FFFFFF"

st.markdown(f"""
    <style>
        [data-testid="stSidebar"] {{
            background-color: {NBA_BLUE};
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: {NBA_WHITE};
        }}
        
        .stRadio > label {{
            color: {NBA_WHITE} !important;
            font-weight: bold;
        }}
        
        h1 {{
            color: {NBA_BLUE};
        }}
        
        h2, h3 {{
            color: {NBA_RED};
        }}
        
        [data-testid="stMetricValue"] {{
            color: {NBA_BLUE};
        }}
        
        [data-testid="stDataFrame"] {{
            border: 2px solid {NBA_BLUE};
        }}
        
        .stButton > button {{
            background-color: {NBA_RED};
            color: {NBA_WHITE};
            border: none;
            padding: 15px 25px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            width: 100%;
        }}
        
        .stButton > button:hover {{
            background-color: {NBA_BLUE};
            color: {NBA_WHITE};
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {NBA_WHITE};
            color: {NBA_BLUE};
            border-radius: 4px 4px 0 0;
            padding: 10px 20px;
            font-weight: bold;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {NBA_BLUE};
            color: {NBA_WHITE};
        }}
        
        .game-card {{
            background-color: {NBA_WHITE};
            border: 2px solid {NBA_BLUE};
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            text-align: center;
        }}
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state:
    st.session_state.page = "🏠 Home"

with st.sidebar:
    st.markdown(f"<h1 style='color: {NBA_WHITE}; text-align: center;'>🏀 NBA Stats</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Home", "👤 Players", "🏥 Injuries", "🔮 Fantasy Predictions"],
        label_visibility="collapsed",
        key="nav_radio"
    )
    st.session_state.page = page
    
    st.markdown("---")
    st.markdown(f"<p style='color: {NBA_WHITE}; text-align: center;'><b>Created by Corentin Jay</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: {NBA_WHITE}; text-align: center;'><a href='https://github.com/CorentinJay' style='color: {NBA_WHITE};'>GitHub</a></p>", unsafe_allow_html=True)

def get_french_time():
    paris_tz = pytz.timezone('Europe/Paris')
    return datetime.now(paris_tz)

def format_game_display(row):
    away_team = row['Equipe_Exterieur']
    home_team = row['Equipe_Domicile']
    arena = row['Arena']
    time_str = row['Heure']
    
    return f"{time_str} - {away_team} @ {home_team} - {arena}"

def get_today_games():
    try:
        df_schedule = pd.read_parquet('season_schedule.parquet')
        df_schedule['Date'] = pd.to_datetime(df_schedule['Date'])
        
        today = get_french_time().date()
        today_games = df_schedule[df_schedule['Date'].dt.date == today].copy()
        
        return today_games
    except Exception as e:
        st.error(f"❌ Error loading schedule: {str(e)}")
        return pd.DataFrame()

def get_first_game_time():
    today_games = get_today_games()
    if not today_games.empty and 'Heure' in today_games.columns:
        times = today_games['Heure'].dropna()
        if not times.empty:
            return times.iloc[0]
    return None

if st.session_state.page == "🏠 Home":
    st.title("🏀 NBA Stats Fantasy")
    
    current_time = get_french_time()
    st.markdown(f"### 📅 {current_time.strftime('%A, %B %d, %Y')}")
    
    st.markdown("---")
    st.markdown("### 🏀 Today's Games")
    
    today_games = get_today_games()
    
    if not today_games.empty:
        for _, game in today_games.iterrows():
            game_display = format_game_display(game)
            st.markdown(f"<div class='game-card'><h4 style='color: {NBA_BLUE}; margin: 0;'>{game_display}</h4></div>", 
                       unsafe_allow_html=True)
    else:
        st.info("No games scheduled for today")
    
    st.markdown("---")
    st.markdown("### Navigation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👤 Players\n\nPlayer statistics and info", use_container_width=True):
            st.session_state.page = "👤 Players"
            st.rerun()
    
    with col2:
        if st.button("🏥 Injuries\n\nInjury reports", use_container_width=True):
            st.session_state.page = "🏥 Injuries"
            st.rerun()
    
    with col3:
        if st.button("🔮 Predictions\n\nFantasy predictions", use_container_width=True):
            st.session_state.page = "🔮 Fantasy Predictions"
            st.rerun()

elif st.session_state.page == "👤 Players":
    st.title("👤 Player Statistics")
    
    tab1, tab2, tab3 = st.tabs(["📊 Season Stats", "📈 Career Stats", "ℹ️ Players Info"])
    
    with tab1:
        st.subheader("📊 Season Statistics")
        
        try:
            df_season = pd.read_parquet('player_season.parquet')
            
            cols = st.columns(len(df_season.columns))
            filters = {}
            for idx, col in enumerate(df_season.columns):
                with cols[idx]:
                    if df_season[col].dtype == 'object':
                        unique_values = ['All'] + sorted(df_season[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"season_{col}")
                    else:
                        filters[col] = st.text_input(f"{col}", key=f"season_{col}")
            
            filtered_df = df_season.copy()
            for col, filter_val in filters.items():
                if filter_val and filter_val != 'All':
                    if df_season[col].dtype == 'object':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
                    else:
                        try:
                            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(filter_val), na=False)]
                        except:
                            pass
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        except Exception as e:
            st.error(f"❌ Error loading season stats: {str(e)}")
        
        st.markdown("---")
        st.subheader("📈 Player Trends")
        
        try:
            df_trend = pd.read_parquet('player_trend.parquet')
            
            cols = st.columns(len(df_trend.columns))
            filters = {}
            for idx, col in enumerate(df_trend.columns):
                with cols[idx]:
                    if df_trend[col].dtype == 'object':
                        unique_values = ['All'] + sorted(df_trend[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"trend_{col}")
                    else:
                        filters[col] = st.text_input(f"{col}", key=f"trend_{col}")
            
            filtered_df = df_trend.copy()
            for col, filter_val in filters.items():
                if filter_val and filter_val != 'All':
                    if df_trend[col].dtype == 'object':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
                    else:
                        try:
                            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(filter_val), na=False)]
                        except:
                            pass
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        except Exception as e:
            st.error(f"❌ Error loading trends: {str(e)}")
        
        st.markdown("---")
        st.caption("📊 **Data Source:** NBA Official Stats API | Updated daily")
    
    with tab2:
        st.subheader("📈 Career Statistics")
        
        try:
            df_career = pd.read_parquet('player_career.parquet')
            
            cols = st.columns(len(df_career.columns))
            filters = {}
            for idx, col in enumerate(df_career.columns):
                with cols[idx]:
                    if df_career[col].dtype == 'object':
                        unique_values = ['All'] + sorted(df_career[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"career_{col}")
                    else:
                        filters[col] = st.text_input(f"{col}", key=f"career_{col}")
            
            filtered_df = df_career.copy()
            for col, filter_val in filters.items():
                if filter_val and filter_val != 'All':
                    if df_career[col].dtype == 'object':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
                    else:
                        try:
                            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(filter_val), na=False)]
                        except:
                            pass
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
            
            st.markdown("---")
            st.caption("📈 **Data Source:** NBA Official Stats API | Complete career statistics")
            
        except Exception as e:
            st.error(f"❌ Error loading career stats: {str(e)}")
    
    with tab3:
        st.subheader("ℹ️ Player Information")
        
        try:
            df_info = pd.read_parquet('player_info.parquet')
            
            cols = st.columns(len(df_info.columns))
            filters = {}
            for idx, col in enumerate(df_info.columns):
                with cols[idx]:
                    if df_info[col].dtype == 'object':
                        unique_values = ['All'] + sorted(df_info[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"info_{col}")
                    else:
                        filters[col] = st.text_input(f"{col}", key=f"info_{col}")
            
            filtered_df = df_info.copy()
            for col, filter_val in filters.items():
                if filter_val and filter_val != 'All':
                    if df_info[col].dtype == 'object':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
                    else:
                        try:
                            filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(filter_val), na=False)]
                        except:
                            pass
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
            
            st.markdown("---")
            st.caption("ℹ️ **Data Source:** NBA Official Stats API | Player information")
            
        except Exception as e:
            st.error(f"❌ Error loading player info: {str(e)}")

elif st.session_state.page == "🏥 Injuries":
    st.title("🏥 Injury List")
    
    try:
        df = pd.read_parquet('injury_list.parquet')
        
        cols = st.columns(len(df.columns))
        filters = {}
        for idx, col in enumerate(df.columns):
            with cols[idx]:
                if df[col].dtype == 'object':
                    unique_values = ['All'] + sorted(df[col].dropna().unique().tolist())
                    filters[col] = st.selectbox(f"{col}", unique_values, key=f"injury_{col}")
                else:
                    filters[col] = st.text_input(f"{col}", key=f"injury_{col}")
        
        filtered_df = df.copy()
        for col, filter_val in filters.items():
            if filter_val and filter_val != 'All':
                if df[col].dtype == 'object':
                    filtered_df = filtered_df[filtered_df[col] == filter_val]
                else:
                    try:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(filter_val), na=False)]
                    except:
                        pass
        
        st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        
        st.markdown("---")
        st.caption("🏥 **Data Source:** ESPN injury report | Updated daily")
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")

elif st.session_state.page == "🔮 Fantasy Predictions":
    st.title("🔮 Fantasy Predictions")
    
    first_game_time = get_first_game_time()
    if first_game_time:
        st.markdown(f"### ⏰ Deadline: {first_game_time} (first game of the day)")
    
    try:
        df = pd.read_parquet('fantasy_daily_predictions.parquet')
        
        cols = st.columns(len(df.columns))
        filters = {}
        for idx, col in enumerate(df.columns):
            with cols[idx]:
                if df[col].dtype == 'object':
                    unique_values = ['All'] + sorted(df[col].dropna().unique().tolist())
                    filters[col] = st.selectbox(f"{col}", unique_values, key=f"fantasy_{col}")
                else:
                    filters[col] = st.text_input(f"{col}", key=f"fantasy_{col}")
        
        filtered_df = df.copy()
        for col, filter_val in filters.items():
            if filter_val and filter_val != 'All':
                if df[col].dtype == 'object':
                    filtered_df = filtered_df[filtered_df[col] == filter_val]
                else:
                    try:
                        filtered_df = filtered_df[filtered_df[col].astype(str).str.contains(str(filter_val), na=False)]
                    except:
                        pass
        
        st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        
        st.markdown("---")
        st.caption("🔮 **Data Source:** Prediction model based on NBA statistics | Generated daily")
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")