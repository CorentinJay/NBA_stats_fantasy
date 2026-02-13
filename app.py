import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import plotly.graph_objects as go
import numpy as np

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
        ["🏠 Home", "👤 Players", "⚔️ Player VS", "🏥 Injuries", "🔮 Fantasy Predictions"],
        label_visibility="collapsed",
        index=["🏠 Home", "👤 Players", "⚔️ Player VS", "🏥 Injuries", "🔮 Fantasy Predictions"].index(st.session_state.page)
    )
    
    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()
    
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
    
    if 'Heure_paris' in row.index:
        time_str = row['Heure_paris'].strftime('%H:%M')
    else:
        time_obj = pd.to_datetime(row['Heure'])
        time_str = time_obj.strftime('%H:%M')
    
    return f"{time_str} - {away_team} @ {home_team} - {arena}"

def get_today_games():
    try:
        df_schedule = pd.read_parquet('season_schedule.parquet')
        df_schedule['Date'] = pd.to_datetime(df_schedule['Date'], format='mixed', dayfirst=True)
        
        def parse_et_time(statut, date):
            try:
                time_str = statut.replace(' ET', '').strip()
                dt_str = f"{date.strftime('%Y-%m-%d')} {time_str}"
                dt_et = pd.to_datetime(dt_str, format='%Y-%m-%d %I:%M %p')
                eastern_tz = pytz.timezone('US/Eastern')
                paris_tz = pytz.timezone('Europe/Paris')
                dt_et_aware = eastern_tz.localize(dt_et)
                dt_paris = dt_et_aware.astimezone(paris_tz)
                return dt_paris
            except:
                return None
        
        df_schedule['Heure_paris'] = df_schedule.apply(
            lambda row: parse_et_time(row['Statut'], row['Date']), axis=1
        )
        
        now_paris = datetime.now(pytz.timezone('Europe/Paris'))
        today_paris = now_paris.date()
        
        today_games = df_schedule[df_schedule['Date'].dt.date == today_paris].copy()
        
        if today_games.empty:
            st.info("🏀 No games for today...")
            return pd.DataFrame()
        
        today_games = today_games.sort_values('Heure_paris')
        
        return today_games
    except Exception as e:  # ← CORRECTION ICI
        st.error(f"❌ Error loading schedule: {str(e)}")  # ← ET ICI
        return pd.DataFrame()

def get_first_game_time():
    today_games = get_today_games()
    if not today_games.empty and 'Heure_paris' in today_games.columns:
        first_time = today_games.iloc[0]['Heure_paris']
        return first_time.strftime('%H:%M')
    return None

def create_radar_chart(player1_data, player2_data, categories, title, player1_name, player2_name, is_percentage=False):
    """Create a radar chart comparing two players"""
    
    fig = go.Figure()
    
    # Determine appropriate range based on data
    if is_percentage:
        # Fixed scale for percentages
        max_range = 100
        tick_vals = [0, 20, 40, 60, 80, 100]
        suffix = '%'
    else:
        # Dynamic scale for stats
        all_values = player1_data + player2_data
        max_val = max(all_values) if all_values else 1
        
        # Calculate appropriate max range with some headroom
        if max_val <= 3:
            max_range = 3.5
            tick_vals = [0, 0.7, 1.4, 2.1, 2.8, 3.5]
        elif max_val <= 10:
            max_range = 12
            tick_vals = [0, 2, 4, 6, 8, 10, 12]
        elif max_val <= 20:
            max_range = 25
            tick_vals = [0, 5, 10, 15, 20, 25]
        elif max_val <= 30:
            max_range = 35
            tick_vals = [0, 7, 14, 21, 28, 35]
        else:
            max_range = int((max_val / 10 + 1.5)) * 10
            tick_vals = [i * max_range / 5 for i in range(6)]
        suffix = ''
    
    # Player 1
    fig.add_trace(go.Scatterpolar(
        r=player1_data,
        theta=categories,
        fill='toself',
        name=player1_name,
        line=dict(color=NBA_BLUE, width=3),
        fillcolor=f'rgba(29, 66, 138, 0.25)',
        hovertemplate='%{theta}: %{r:.1f}' + suffix + '<extra></extra>'
    ))
    
    # Player 2
    fig.add_trace(go.Scatterpolar(
        r=player2_data,
        theta=categories,
        fill='toself',
        name=player2_name,
        line=dict(color=NBA_RED, width=3),
        fillcolor=f'rgba(200, 16, 46, 0.25)',
        hovertemplate='%{theta}: %{r:.1f}' + suffix + '<extra></extra>'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_range],
                showticklabels=True,
                tickfont=dict(size=11, color='#888'),
                tickvals=tick_vals,
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            angularaxis=dict(
                tickfont=dict(size=13, color='white', family='Arial Black'),
                gridcolor='rgba(255, 255, 255, 0.2)'
            ),
            bgcolor='rgba(0, 0, 0, 0)'
        ),
        showlegend=True,
        title=dict(
            text=title,
            font=dict(size=16, color=NBA_BLUE, family="Arial Black"),
            x=0.5,
            xanchor='center'
        ),
        height=450,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.12,
            xanchor="center",
            x=0.5,
            font=dict(size=12, family='Arial')
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=70, b=60, l=50, r=50)
    )
    
    return fig

def normalize_percentage(value, max_val=100):
    """Normalize percentage values for radar chart"""
    return min(value, max_val)

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
            st.markdown(f"<div style='background-color: {NBA_WHITE}; border: 1px solid {NBA_BLUE}; border-radius: 5px; padding: 8px; margin: 5px 0; text-align: center;'><p style='color: {NBA_BLUE}; margin: 0; font-size: 14px;'>{game_display}</p></div>", 
                       unsafe_allow_html=True)
    else:
        st.info("No games scheduled for today")
    
    st.markdown("---")
    st.markdown("### 📊 Season Leaders")
    
    try:
        df_season = pd.read_parquet('player_season.parquet')
        
        stats = {
            'PTS': '🏀 Points',
            'REB': '🔄 Rebounds',
            'AST': '🎯 Assists',
            'STL': '🖐️ Steals',
            'BLK': '🚫 Blocks'
        }
        
        cols = st.columns(5)
        
        for idx, (stat_col, stat_title) in enumerate(stats.items()):
            with cols[idx]:
                st.markdown(f"**{stat_title}**")
                if stat_col in df_season.columns:
                    top_5 = df_season.nlargest(5, stat_col)[['PLAYER', stat_col]]
                    top_5 = top_5.reset_index(drop=True)
                    st.dataframe(top_5, use_container_width=True, height=220, hide_index=True)
                else:
                    st.warning(f"{stat_col} not found")
    except Exception as e:
        st.error(f"❌ Error loading season stats: {str(e)}")
    
    st.markdown("---")
    st.markdown("### Navigation")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("👤 Players\n\nPlayer statistics and info", use_container_width=True):
            st.session_state.page = "👤 Players"
            st.rerun()
    
    with col2:
        if st.button("⚔️ Player VS\n\nCompare two players", use_container_width=True):
            st.session_state.page = "⚔️ Player VS"
            st.rerun()
    
    with col3:
        if st.button("🏥 Injuries\n\nInjury reports", use_container_width=True):
            st.session_state.page = "🏥 Injuries"
            st.rerun()
    
    with col4:
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
            
            filter_cols = [col for col in df_season.columns if 'PLAYER' in col.upper() or 'TEAM' in col.upper()]
            
            if filter_cols:
                cols = st.columns(len(filter_cols))
                filters = {}
                for idx, col in enumerate(filter_cols):
                    with cols[idx]:
                        unique_values = ['All'] + sorted(df_season[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"season_{col}")
                
                filtered_df = df_season.copy()
                for col, filter_val in filters.items():
                    if filter_val and filter_val != 'All':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
            else:
                filtered_df = df_season
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        except Exception as e:
            st.error(f"❌ Error loading season stats: {str(e)}")
        
        st.markdown("---")
        st.subheader("📈 Player Trends")
        
        try:
            df_trend = pd.read_parquet('player_trend.parquet')
            
            filter_cols = [col for col in df_trend.columns if 'PLAYER' in col.upper() or 'TEAM' in col.upper()]
            
            if filter_cols:
                cols = st.columns(len(filter_cols))
                filters = {}
                for idx, col in enumerate(filter_cols):
                    with cols[idx]:
                        unique_values = ['All'] + sorted(df_trend[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"trend_{col}")
                
                filtered_df = df_trend.copy()
                for col, filter_val in filters.items():
                    if filter_val and filter_val != 'All':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
            else:
                filtered_df = df_trend
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        except Exception as e:
            st.error(f"❌ Error loading trends: {str(e)}")
        
        st.markdown("---")
        st.caption("📊 **Data Source:** NBA Official Stats API | Updated daily")
    
    with tab2:
        st.subheader("📈 Career Statistics")
        
        try:
            df_career = pd.read_parquet('player_career.parquet')
            
            filter_cols = [col for col in df_career.columns if 'PLAYER' in col.upper() or 'TEAM' in col.upper()]
            
            if filter_cols:
                cols = st.columns(len(filter_cols))
                filters = {}
                for idx, col in enumerate(filter_cols):
                    with cols[idx]:
                        unique_values = ['All'] + sorted(df_career[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"career_{col}")
                
                filtered_df = df_career.copy()
                for col, filter_val in filters.items():
                    if filter_val and filter_val != 'All':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
            else:
                filtered_df = df_career
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
            
            st.markdown("---")
            st.caption("📈 **Data Source:** NBA Official Stats API | Complete career statistics")
            
        except Exception as e:
            st.error(f"❌ Error loading career stats: {str(e)}")
    
    with tab3:
        st.subheader("ℹ️ Player Information")
        
        try:
            df_info = pd.read_parquet('player_info.parquet')
            
            filter_cols = [col for col in df_info.columns if 'PLAYER' in col.upper() or 'TEAM' in col.upper()]
            
            if filter_cols:
                cols = st.columns(len(filter_cols))
                filters = {}
                for idx, col in enumerate(filter_cols):
                    with cols[idx]:
                        unique_values = ['All'] + sorted(df_info[col].dropna().unique().tolist())
                        filters[col] = st.selectbox(f"{col}", unique_values, key=f"info_{col}")
                
                filtered_df = df_info.copy()
                for col, filter_val in filters.items():
                    if filter_val and filter_val != 'All':
                        filtered_df = filtered_df[filtered_df[col] == filter_val]
            else:
                filtered_df = df_info
            
            st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
            
            st.markdown("---")
            st.caption("ℹ️ **Data Source:** NBA Official Stats API | Player information")
            
        except Exception as e:
            st.error(f"❌ Error loading player info: {str(e)}")

elif st.session_state.page == "⚔️ Player VS":
    st.title("⚔️ Player Comparison")
    
    try:
        df_season = pd.read_parquet('player_season.parquet')
        
        # Get player list
        player_col = None
        for col in df_season.columns:
            if 'PLAYER' in col.upper() and 'ID' not in col.upper():
                player_col = col
                break
        
        if player_col is None:
            st.error("❌ Unable to find player names column")
        else:
            players_list = sorted(df_season[player_col].dropna().unique().tolist())
            
            # Player selection
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"<h3 style='color: {NBA_BLUE}; text-align: center;'>Player 1</h3>", unsafe_allow_html=True)
                player1 = st.selectbox("Select Player 1", players_list, key="player1", label_visibility="collapsed")
            
            with col2:
                st.markdown(f"<h3 style='color: {NBA_RED}; text-align: center;'>Player 2</h3>", unsafe_allow_html=True)
                player2 = st.selectbox("Select Player 2", players_list, key="player2", label_visibility="collapsed")
            
            if player1 and player2:
                # Get player data
                player1_stats = df_season[df_season[player_col] == player1].iloc[0]
                player2_stats = df_season[df_season[player_col] == player2].iloc[0]
                
                st.markdown("---")
                
                # Classic stats - split into two categories for better readability
                # Volume stats: PTS, OREB, AST, MIN
                volume_stats = ['PTS', 'OREB', 'AST', 'MIN']
                volume_values1 = []
                volume_values2 = []
                valid_volume_stats = []
                
                for stat in volume_stats:
                    if stat in df_season.columns:
                        val1 = player1_stats[stat] if pd.notna(player1_stats[stat]) else 0
                        val2 = player2_stats[stat] if pd.notna(player2_stats[stat]) else 0
                        volume_values1.append(float(val1))
                        volume_values2.append(float(val2))
                        valid_volume_stats.append(stat)
                
                # Defensive stats: STL, BLK, DREB
                defensive_stats = ['STL', 'BLK', 'DREB']
                defensive_values1 = []
                defensive_values2 = []
                valid_defensive_stats = []
                
                for stat in defensive_stats:
                    if stat in df_season.columns:
                        val1 = player1_stats[stat] if pd.notna(player1_stats[stat]) else 0
                        val2 = player2_stats[stat] if pd.notna(player2_stats[stat]) else 0
                        defensive_values1.append(float(val1))
                        defensive_values2.append(float(val2))
                        valid_defensive_stats.append(stat)
                
                # Shooting efficiency radar chart
                shooting_stats_map = {
                    'FG%': 'FG%',
                    'FG3%': 'FG3%', 
                    '3P%': 'FG3%',  # Alternative name
                    'FT%': 'FT%'
                }
                
                shooting_values1 = []
                shooting_values2 = []
                valid_shooting_stats = []
                
                for display_name, possible_names in [('FG%', ['FG%']), ('FG3%', ['FG3%', '3P%']), ('FT%', ['FT%'])]:
                    found = False
                    for stat_name in possible_names:
                        if stat_name in df_season.columns:
                            val1 = player1_stats[stat_name] if pd.notna(player1_stats[stat_name]) else 0
                            val2 = player2_stats[stat_name] if pd.notna(player2_stats[stat_name]) else 0
                            
                            # Convert to percentage if needed (value between 0-1)
                            if val1 > 0 and val1 <= 1:
                                val1 *= 100
                            if val2 > 0 and val2 <= 1:
                                val2 *= 100
                            
                            shooting_values1.append(float(val1))
                            shooting_values2.append(float(val2))
                            valid_shooting_stats.append(display_name)
                            found = True
                            break
                    
                    if not found:
                        # Add 0 values for missing stats to keep chart balanced
                        shooting_values1.append(0)
                        shooting_values2.append(0)
                        valid_shooting_stats.append(f"{display_name} (N/A)")
                
                # Display all three charts in one row
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if valid_volume_stats:
                        fig1 = create_radar_chart(
                            volume_values1,
                            volume_values2,
                            valid_volume_stats,
                            "📊 Volume Stats",
                            player1,
                            player2,
                            is_percentage=False
                        )
                        st.plotly_chart(fig1, use_container_width=True)
                    else:
                        st.warning("Volume stats not available")
                
                with col2:
                    if valid_defensive_stats:
                        fig2 = create_radar_chart(
                            defensive_values1,
                            defensive_values2,
                            valid_defensive_stats,
                            "🛡️ Defensive Stats",
                            player1,
                            player2,
                            is_percentage=False
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                    else:
                        st.warning("Defensive stats not available")
                
                with col3:
                    if valid_shooting_stats:
                        # Remove "(N/A)" entries if all are N/A
                        if not all("(N/A)" in stat for stat in valid_shooting_stats):
                            fig3 = create_radar_chart(
                                shooting_values1,
                                shooting_values2,
                                valid_shooting_stats,
                                "🎯 Shooting Efficiency",
                                player1,
                                player2,
                                is_percentage=True
                            )
                            st.plotly_chart(fig3, use_container_width=True)
                        else:
                            st.warning("No shooting efficiency stats available")
                    else:
                        st.warning("Shooting stats not available")
                
                # Detailed comparison table
                st.markdown("---")
                st.subheader("📋 Detailed Comparison")
                
                all_stats = valid_volume_stats + valid_defensive_stats + valid_shooting_stats
                all_values1 = volume_values1 + defensive_values1 + shooting_values1
                all_values2 = volume_values2 + defensive_values2 + shooting_values2
                
                comparison_data = {
                    'Stat': all_stats,
                    player1: all_values1,
                    player2: all_values2
                }
                
                df_comparison = pd.DataFrame(comparison_data)
                
                # Add difference column
                df_comparison['Difference'] = df_comparison[player2] - df_comparison[player1]
                df_comparison['Winner'] = df_comparison.apply(
                    lambda row: player1 if row[player1] > row[player2] else (player2 if row[player2] > row[player1] else 'Equal'),
                    axis=1
                )
                
                st.dataframe(df_comparison, use_container_width=True, hide_index=True)
                
    except Exception as e:
        st.error(f"❌ Error loading player data: {str(e)}")

elif st.session_state.page == "🏥 Injuries":
    st.title("🏥 Injury List")
    
    try:
        df = pd.read_parquet('injury_list.parquet')
        
        filter_cols = [col for col in df.columns if 'PLAYER' in col.upper() or 'TEAM' in col.upper()]
        
        filtered_df = df.copy()
        
        if filter_cols:
            cols = st.columns(len(filter_cols))
            filters = {}
            for idx, col in enumerate(filter_cols):
                with cols[idx]:
                    unique_values = ['All'] + sorted(df[col].dropna().unique().tolist())
                    filters[col] = st.selectbox(f"{col}", unique_values, key=f"injury_{col}")
            
            for col, filter_val in filters.items():
                if filter_val and filter_val != 'All':
                    filtered_df = filtered_df[filtered_df[col] == filter_val]
        
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
        
        filter_cols = [col for col in df.columns if 'PLAYER' in col.upper() or 'TEAM' in col.upper()]
        
        if filter_cols:
            cols = st.columns(len(filter_cols))
            filters = {}
            for idx, col in enumerate(filter_cols):
                with cols[idx]:
                    unique_values = ['All'] + sorted(df[col].dropna().unique().tolist())
                    filters[col] = st.selectbox(f"{col}", unique_values, key=f"fantasy_{col}")
            
            filtered_df = df.copy()
            for col, filter_val in filters.items():
                if filter_val and filter_val != 'All':
                    filtered_df = filtered_df[filtered_df[col] == filter_val]
        else:
            filtered_df = df
        
        st.dataframe(filtered_df, use_container_width=True, height=600, hide_index=True)
        
        st.markdown("---")
        st.caption("🔮 **Data Source:** Prediction model based on NBA statistics | Generated daily")
        
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")