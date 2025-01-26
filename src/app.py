import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import base64

from season_chart import create_fig as create_season_chart
from distribution_charts import create_plot


# Title of the Streamlit app
#st.title("")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <style>
               .css-18e3th9 {
                    padding-top: 0rem;
                    padding-bottom: 10rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
               .css-1d391kg {
                    padding-top: 3.5rem;
                    padding-right: 1rem;
                    padding-bottom: 3.5rem;
                    padding-left: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

# Define the start, playoff, and end dates of the hockey season
season_start = datetime(2024, 9, 30)  # Start of the season
playoff_start = datetime(2025, 4, 17) # Start of playoffs
season_end = datetime(2025, 6, 30)    # End of the season

today = datetime.now()
if today < season_start:
    progress_percent = 0
    playoff_percent = 0
    message = "The hockey season hasn't started yet."
elif today > season_end:
    progress_percent = 100
    playoff_percent = (playoff_start - season_start).days / (season_end - season_start).days * 100
    message = "The hockey season is over."
else:
    total_days = (season_end - season_start).days
    elapsed_days = (today - season_start).days
    progress_percent = (elapsed_days / total_days) * 100
    playoff_percent = (playoff_start - season_start).days / total_days * 100
    message = f"The hockey season is {elapsed_days} days in."

# Custom HTML for the progress bar
st.markdown(f"""
    <style>
    .progress-container {{
        position: relative;
        width: 100%;
        background-color: #efefef; /* Light gray background */
        border-radius: 10px;
        height: 30px;
        margin: 20px 0;
    }}
    .progress-bar {{
        width: {progress_percent}%;
        height: 100%;
        background-color: #444444; /* Black progress */
        border-radius: 10px 0 0 10px; /* Rounded left corner only */
    }}
    .playoff-line {{
        position: absolute;
        left: {playoff_percent}%;
        top: 0;
        bottom: 0;
        border-left: 2px dashed #444444; /* Dashed black line */
        z-index: 2;
    }}
    .regular-season-label, .playoff-label {{
        position: absolute;
        top: -30px; /* Position above the bar */
        font-size: 14px;
        color: #444444;;
        font-weight: bold;
    }}
    .regular-season-label {{
        left: 0;
        width: {playoff_percent}%;
        text-align: center;
    }}
    .playoff-label {{
        left: {playoff_percent}%;
        width: {100 - playoff_percent}%;
        text-align: center;
    }}
    
    </style>
    <div class="progress-container">
        <div class="progress-bar"></div>
        <div class="playoff-line"></div>
        <div class="regular-season-label">Regular Season</div>
        <div class="playoff-label">Playoffs</div>
    </div>
""", unsafe_allow_html=True)

eleven_players = st.checkbox("Remove worst players")
csv_path = r"stats_detail.csv"

column_order = ["rank", "team_logo", "pooler_name", "game_played", "total_points", "point_deficit", "average_points", "players", "hot", "cold", "injured"]
column_config={
        "rank": st.column_config.NumberColumn(
            label="#",
            help="Game played",
            step=1,
            format="%d",
        ),
        "pooler_name": st.column_config.TextColumn(
            label="Pooler",
        ),
        "team_logo": st.column_config.ImageColumn(
            label="Team",
            width="small",
        ),
        "game_played": st.column_config.NumberColumn(
            label="GP",
            help="Game played",
            step=1,
            format="%d",
        ),
        "total_points": st.column_config.NumberColumn(
            label="TP",
            help="Total points",
            step=1,
            format="%d",
        ),
        "point_deficit": st.column_config.NumberColumn(
            label="PD",
            help="Point deficit with lead",
            step=1.0,
            format="%d",
        ),
        "average_points": st.column_config.NumberColumn(
            label="AP",
            help="Total points / Game played",
            format="%0.2f",
        ),
        "players": st.column_config.NumberColumn(
            label="🏒",
            help="Number of players",
            step=1,
            format="%d",
        ),
        "hot": st.column_config.NumberColumn(
            label="🔥",
            help="Number of players on hot streak",
            step=1,
            format="%d",
        ),
        "cold": st.column_config.NumberColumn(
            label="❄️",
            help="Number of players on cold streak",
            step=1,
            format="%d",
        ),
        "injured": st.column_config.NumberColumn(
            label="🚑",
            help="Number of players injured",
            step=1,
            format="%d",
        )
    }

def load_data(file_path):
    df = pd.read_csv(file_path)
    return df
df = load_data(csv_path)


@st.cache_data()
def load_team_images():

    def open_image(path: str):
        with open(path, "rb") as p:
            file = p.read()
            return f"data:image/png;base64,{base64.b64encode(file).decode()}"

    dir_path = Path(r"assets/img/teams")
    files = [file for file in dir_path.iterdir() if file.is_file()]
    return {file.stem: open_image(f"{dir_path}/{file.name}") for file in files if file.suffix == ".png"}
team_images = load_team_images()

df['team_logo'] = df['pooler_team'].apply(lambda x: team_images[x])
df['player_team'] = df['player_team'].apply(lambda x: team_images[x])

if eleven_players:
    df_players = df[df['position'] != 'Team']
    df_players_sorted = df_players.sort_values(by=['pooler_name', 'value_dt', 'total_points'],
                                               ascending=[True, True, False])
    df_top_11 = df_players_sorted.groupby(['pooler_name', 'value_dt']).head(11)
    # Step 4: Add back the 'Team' row(s)
    df_team = df[df['position'] == 'Team']
    df = pd.concat([df_top_11, df_team])

# Filter data for max value_dt
df["value_dt"] = pd.to_datetime(df["value_dt"])
max_value_dt = df["value_dt"].max()
df_now = df[df["value_dt"] == max_value_dt]
df_now = df_now.drop(columns=["value_dt"])

# Sum game_played and total_point by pooler_name
summary_df = df_now.drop(columns=["position", "player_name", "player_team"])
summary_df = summary_df.groupby(["team_logo", "pooler_name"]).sum().reset_index()
summary_df['average_points'] = summary_df['total_points']/summary_df['game_played'].replace(0, np.nan)
summary_df = summary_df.sort_values(by=["total_points"], ascending=False)
summary_df['point_deficit'] = summary_df['total_points'] - max(summary_df['total_points'])
summary_df['rank'] = np.arange(len(summary_df)) + 1


with st.container(border=True):
    event = st.dataframe(summary_df,
                         height=210,
                         width=800,
                         hide_index=True,
                         column_config=column_config,
                         column_order=column_order,
                         on_select="rerun",
                         selection_mode="multi-row")
    if event.selection.rows:
        selected_poolers = summary_df.iloc[event.selection.rows]['pooler_name'].tolist()
    else:
        selected_poolers = None
    fig = create_season_chart(df, selected_poolers)
    st.plotly_chart(fig)