import streamlit as st
import numpy as np
import pandas as pd
from dataclasses import dataclass
from st_files_connection import FilesConnection

from util.style import team_images

_CHECKBOX_KEY = "remove_worst_player"
_CHECKBOX_DEFAULT = True
s3_bucket = st.secrets["AWS_S3_BUCKET"]


@st.cache_data(ttl=300)
def _load_stats_detail():
    file_path = "marqueur/stats_detail.csv"
    conn = st.connection(name='s3', type=FilesConnection)
    df = conn.read(f"{s3_bucket}/{file_path}", input_format="csv", ttl=30)

    df['team_logo'] = df['pooler_team'].apply(lambda x: team_images[x])
    df['player_team'] = df['player_team'].apply(lambda x: team_images[x])
    df['players'] = df['position'].apply(lambda x: 1 if x != 'Team' else 0)

    return df


def get_stats_detail():
    df = _load_stats_detail()
    if st.session_state.get(_CHECKBOX_KEY, _CHECKBOX_DEFAULT):
        df_players = df[df['position'] != 'Team']
        df_players_sorted = df_players.sort_values(by=['pooler_name', 'value_dt', 'total_points'],
                                                   ascending=[True, True, False])
        df_top_11 = df_players_sorted.groupby(['pooler_name', 'value_dt']).head(11)
        df_team = df[df['position'] == 'Team']
        df = pd.concat([df_top_11, df_team])
    return df


def get_stats_summary():
    df = get_stats_detail()

    # Filter data for max value_dt
    df["value_dt"] = pd.to_datetime(df["value_dt"])
    max_value_dt = df["value_dt"].max()
    df = df[df["value_dt"] == max_value_dt]
    df = df.drop(columns=["value_dt"])

    # Sum game_played and total_point by pooler_name
    df = df.drop(columns=["position", "player_name", "player_team"])
    df = df.groupby(["team_logo", "pooler_name"]).sum().reset_index()
    df['average_points'] = df['total_points'] / df['game_played'].replace(0, np.nan)
    df['delta_average'] = df['delta_points'] / df['delta_game'].replace(0, np.nan)
    df = df.sort_values(by=["total_points"], ascending=False)
    df['point_deficit'] = df['total_points'] - max(df['total_points'])
    df['rank'] = np.arange(len(df)) + 1

    return df


def render_remove_checkbox():
    return st.checkbox("Remove worst player", value=_CHECKBOX_DEFAULT, key=_CHECKBOX_KEY)
