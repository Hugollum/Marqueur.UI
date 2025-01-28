import streamlit as st
from data.marqueur import stats

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


def render_summary_df():
    return st.dataframe(stats.summary,
                        height=598,
                        width=800,
                        hide_index=True,
                        column_config=column_config,
                        column_order=column_order,
                        on_select="rerun",
                        selection_mode="multi-row")