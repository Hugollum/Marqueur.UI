import streamlit as st
from st_files_connection import FilesConnection
import pandas as pd
import numpy as np
from pathlib import Path
import base64

from progress_bar import render_progress_bar
from season_chart import create_fig as create_season_chart
from position_charts import create_fig as create_position_chart
from distribution_charts import create_plot


# Title of the Streamlit app
#st.title("")

# Remove whitespace from the top of the page and sidebar
st.markdown("""
        <script>
            function toggleZoomScreen() {
            document.body.style.zoom = (1 / window.devicePixelRatio);
            }
        </script>
        <style>
            .css-1d391kg {
                padding-top: 3.5rem;
                padding-right: 1rem;
                padding-bottom: 3.5rem;
                padding-left: 1rem;
            }
            .stMainBlockContainer {
                width: 800px; /* Set your desired width */
                margin: 0 auto;   /* Center the content */
                padding-left: 5px;
                padding-right: 5px;
            }
        </style>
        """, unsafe_allow_html=True)

render_progress_bar()

remove_worst_player = st.checkbox("Remove worst player", value=True)
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
    conn = st.connection('s3', type=FilesConnection)
    df = conn.read("061039763978/marqueur/stats_detail.csv", input_format="csv", ttl=600)
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

df['players'] = df['position'].apply(lambda x: 1 if x != 'Team' else 0)

if remove_worst_player:
    df_players = df[df['position'] != 'Team']
    df_players_sorted = df_players.sort_values(by=['pooler_name', 'value_dt', 'total_points'],
                                               ascending=[True, True, False])
    df_top_11 = df_players_sorted.groupby(['pooler_name', 'value_dt']).head(11)
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


event = st.dataframe(summary_df,
                     height=598,
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
st.plotly_chart(fig, config={'staticPlot': True})

positions = ['Forward', 'Defender', 'Goalie', 'Team']
for position in positions:
    st.markdown(f"**{position}**")
    if position == positions[-1]:
        showticklabels = True
    else:
        showticklabels = False
    fig = create_position_chart(df, position, selected_poolers, showticklabels)
    st.plotly_chart(fig, config={'staticPlot': True})