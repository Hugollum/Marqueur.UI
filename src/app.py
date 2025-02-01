import streamlit as st

from data.marqueur import render_mulligan_checkbox, render_projections_checkbox, get_stats_detail, get_roster_stats, get_stats_summary

from live_games import render_score
from progress_bar import render_progress_bar
from summary_df import render_summary_df
from roster_df import render_roaster_df
from season_chart import create_fig as create_season_chart
from position_charts import create_fig as create_position_chart

import sys
sys.stdout.reconfigure(encoding="utf-8")


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

# Title of the Streamlit app
#st.title("")

render_progress_bar()
render_score()
render_mulligan_checkbox()

df_summary = get_stats_summary()
df_detail = get_stats_detail()
df_roster = get_roster_stats()

with st.popover("Pooler roster", use_container_width=800):
    pooler_name = st.selectbox('Pooler', options=df_summary['pooler_name'].drop_duplicates())
    df_roster = df_roster[df_roster['pooler_name'] == pooler_name]
    render_roaster_df(df_roster)

summary_df_event = render_summary_df(df_summary)

if summary_df_event.selection.rows:
    selected_poolers = df_summary.iloc[summary_df_event.selection.rows]['pooler_name'].tolist()
else:
    selected_poolers = None

render_projections_checkbox()
fig = create_season_chart(df_detail, selected_poolers)
st.plotly_chart(fig, config={'staticPlot': True})

st.markdown(f"**Game Played**")
fig = create_position_chart(df_detail, "game_played", None, selected_poolers, True)
st.plotly_chart(fig, config={'staticPlot': True})

positions = ['Forward', 'Defender', 'Goalie', 'Team']
for position in positions:
    st.markdown(f"**{position}**")
    if position == positions[-1]:
        showticklabels = True
    else:
        showticklabels = False
    fig = create_position_chart(df_detail, 'total_points', position, selected_poolers, showticklabels)
    st.plotly_chart(fig, config={'staticPlot': True})
