import streamlit as st

column_order = ["player_team", "position", "player_name", "delta_game", "delta_points", "game_played", "total_points", "average_points", "injured", "hot", "cold"]
column_config={
        "player_team": st.column_config.ImageColumn(
            label="Team",
            width="small",
        ),
        "position": st.column_config.TextColumn(
            label="Position",
        ),
        "name": st.column_config.TextColumn(
            label="Player",
        ),
        "delta_game": st.column_config.NumberColumn(
            label="📆",
            help="Playing today",
            step=1,
            format="%d",
        ),
        "delta_points": st.column_config.NumberColumn(
            label="LP",
            help="Points gained today",
            step=1,
            format="+%d",
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
        "average_points": st.column_config.NumberColumn(
            label="AP",
            help="Total points / Game played",
            format="%0.2f",
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


def render_roaster_df(df):
    return st.dataframe(df,
                        width=800,
                        hide_index=True,
                        column_config=column_config,
                        column_order=column_order)