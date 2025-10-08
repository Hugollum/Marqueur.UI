import streamlit as st

column_order = ["rank", "team_logo", "pooler_name", "delta_game", "delta_points", "game_played", "total_points", "point_deficit", "average_points", "injured", "hot", "cold", "players"]
column_config={
        "rank": st.column_config.NumberColumn(
            label="#",
            help="Position",
            step=1,
            format="%d",
        ),
        "pooler_name": st.column_config.TextColumn(
            label="Pooler",
        ),
        "team_logo": st.column_config.ImageColumn(
            label="Team",
            width="small",
            pinned=True,
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


def render_summary_df(df):
    return st.dataframe(df,
                        height=int((len(df)+1)*35.2),
                        width=800,
                        hide_index=True,
                        column_config=column_config,
                        column_order=column_order,
                        on_select="rerun",
                        selection_mode="multi-row")