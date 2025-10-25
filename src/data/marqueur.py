import streamlit as st
import re
import numpy as np
import pandas as pd
import boto3
from botocore.exceptions import ClientError
import logging

from datetime import datetime, timedelta
from st_files_connection import FilesConnection

from util.style import team_images


_MULLIGAN_CHECKBOX_KEY = "mulligan_checkbox"
_MULLIGAN_CHECKBOX_DEFAULT = False
_PROJECTIONS_CHECKBOX_KEY = "projections_checkbox"
_PROJECTIONS_CHECKBOX_DEFAULT = False
s3_bucket = st.secrets["AWS_S3_BUCKET"]


def format_name(name):
    return re.sub(r"(\b\w)", lambda m: m.group(1).upper(), name.lower())


@st.cache_data(ttl=300)
def _load_player_injury():
    file_path = "marqueur/player_injury.csv"
    conn = st.connection(name='s3', type=FilesConnection)
    df = conn.read(f"{s3_bucket}/{file_path}", input_format="csv", ttl=30, encoding="ISO-8859-1")
    df['player_name'] = df['player_name']
    return df


@st.cache_data(ttl=300)
def _load_stats_detail(season_label):
    file_path = "marqueur/stats_detail.csv"
    conn = st.connection(name='s3', type=FilesConnection)
    df = conn.read(f"{s3_bucket}/{file_path}", input_format="csv", ttl=30, encoding="ISO-8859-1")
    df = df[df['season'] == season_label]

    df = pd.merge(df, _load_player_injury(), how='left', on='player_name')

    df['season_ended'] = df['season_ended'].fillna(False)
    df['team_logo'] = df['pooler_team'].apply(lambda x: team_images[x])
    df['player_team_abbv'] = df['player_team']
    df['player_team'] = df['player_team'].apply(lambda x: team_images[x])
    df['players'] = df.apply(lambda x: 1 if x['position'] != 'Team' and not x['season_ended'] else 0, axis='columns')
    df['player_name'] = df['player_name'].apply(lambda x: format_name(x))

    return df


@st.cache_data(ttl=3600)
def get_headlines():
    file_path = "marqueur/headlines.md"
    s3_client = boto3.client('s3')

    try:
        response = s3_client.get_object(Bucket=s3_bucket, Key=file_path)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except Exception as e:
        print(f"Error reading S3 file: {e}")
        return None


def get_stats_detail(season_label):
    df = _load_stats_detail(season_label)

    # Apply Mulligan
    if st.session_state.get(_MULLIGAN_CHECKBOX_KEY, _MULLIGAN_CHECKBOX_DEFAULT):
        df_players = df[df['position'] != 'Team']
        df_players_sorted = df_players.sort_values(by=['pooler_name', 'value_dt', 'total_points'],
                                                   ascending=[True, True, False])
        df_top_11 = df_players_sorted.groupby(['pooler_name', 'value_dt']).head(11)
        df_team = df[df['position'] == 'Team']
        df = pd.concat([df_top_11, df_team])

    # Remove projections
    if not st.session_state.get(_PROJECTIONS_CHECKBOX_KEY, _PROJECTIONS_CHECKBOX_DEFAULT):
        df = df[~df['is_projection']]

    return df


def get_roster_stats(season_label):
    df = get_stats_detail(season_label)

    # Filter out projections
    df = df[~df['is_projection']]

    # Filter data for max value_dt
    df["value_dt"] = pd.to_datetime(df["value_dt"])
    max_value_dt = df["value_dt"].max()
    df = df[df["value_dt"] == max_value_dt]
    df = df.drop(columns=["value_dt"])

    # Sum game_played and total_point by pooler_name
    df['average_points'] = df['total_points'] / df['game_played'].replace(0, np.nan)
    df['delta_average'] = df['delta_points'] / df['delta_game'].replace(0, np.nan)

    position_priority = {"Forward": 1, "Defender": 2, "Goalie": 3, "Team": 4}
    df = df.sort_values(
        by=["position", "average_points"],
        key=lambda col: col.map(position_priority) if col.name == "position" else col,
        ascending=[True, False]  #
    )

    return df


def get_stats_summary(season_label):
    df = get_stats_detail(season_label)

    # Filter out projections
    df = df[~df['is_projection']]

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
    df['rank'] = df['total_points'].rank(method='min', ascending=False).astype(int)

    return df


def render_mulligan_checkbox():
    return st.checkbox("With mulligan", value=_MULLIGAN_CHECKBOX_DEFAULT, key=_MULLIGAN_CHECKBOX_KEY)

def render_projections_checkbox():
    return st.checkbox("With trends", value=_PROJECTIONS_CHECKBOX_DEFAULT, key=_PROJECTIONS_CHECKBOX_KEY)
