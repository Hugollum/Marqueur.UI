import streamlit as st
from PIL import Image
import pandas as pd

from data.marqueur import render_mulligan_checkbox, render_projections_checkbox, get_stats_detail, get_roster_stats, get_stats_summary
from data.nhl import get_standings, get_playoff_team
from util.config import season_start, season_end, playoff_start, today

from live_games import render_score
from progress_bar import render_progress_bar
from summary_df import render_summary_df
from roster_df import render_roaster_df
from season_chart import create_fig as create_season_chart
from position_charts import create_fig as create_position_chart
from playoff_chart import create_fig as create_playoff_chart
from standings_charts import create_fig as create_standings_chart
from playoff_brackets import create_fig as create_playoff_brackets

import sys

st.set_page_config(
    page_title="flcdlp",
    page_icon="assets/img/favicon.ico",
    layout="wide",
)

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
# render_mulligan_checkbox()

df_summary = get_stats_summary()
df_detail = get_stats_detail()
df_breakdown = df_detail[~df_detail['is_projection']]
df_roster = get_roster_stats()
df_standings = get_standings()
df_playoff_team = get_playoff_team()
df_playoff = pd.merge(df_roster, df_playoff_team, left_on=['player_team_abbv'], right_on=['team'], how='left', indicator=True)
df_playoff['in_playoff'] = df_playoff['_merge'] == 'both'
df_playoff = df_playoff[list(df_roster.columns) + ['in_playoff']]

st.subheader("Poolers", divider="gray")
with st.expander("Pooler roster", expanded=False):
    col, _, _ = st.columns(3)
    with col:
        pooler_name = st.selectbox('Pooler', options=df_summary['pooler_name'].drop_duplicates())
    df_roster = df_roster[df_roster['pooler_name'] == pooler_name]
    render_roaster_df(df_roster)

st.markdown(f"##### Leaderboard")
summary_df_event = render_summary_df(df_summary)

if summary_df_event.selection.rows:
    selected_poolers = df_summary.iloc[summary_df_event.selection.rows]['pooler_name'].tolist()
else:
    selected_poolers = None

render_projections_checkbox()
fig = create_season_chart(df_detail, selected_poolers)
st.plotly_chart(fig, config={'staticPlot': True})

st.markdown(f"##### Pool Breakdown")
st.markdown(f"**Game Played**")
fig = create_position_chart(df_breakdown, "game_played", None, selected_poolers)
st.plotly_chart(fig, config={'staticPlot': True})

positions = ['Forward', 'Defender', 'Goalie', 'Team']
for position in positions:
    st.markdown(f"**{position}**")
    fig = create_position_chart(df_breakdown, 'total_points', position, selected_poolers)
    st.plotly_chart(fig, config={'staticPlot': True})


st.markdown(f"##### Playoff Composition")
fig = create_playoff_chart(df_playoff, selected_poolers)
st.plotly_chart(fig, config={'staticPlot': True})


st.subheader("Standings", divider="gray")
def render_regular_season():
    st.markdown(f"##### Regular Season")
    conferences = [('Eastern', ['Atlantic', 'Metropolitan']), ('Western', ['Central', 'Pacific'])]
    for conference, divisions in conferences:
        for division in divisions:
            st.markdown(f"**{division}**")
            if division == 'Pacific':
                showticklabels = True
            else:
                showticklabels = False
            fig = create_standings_chart(df_standings, conference, division, showticklabels)
            st.plotly_chart(fig, config={'staticPlot': True})

    st.markdown(
        '<div style="display: flex; align-items: center;">'
        '<div style="width: 15px; height: 15px; background-color: #F0F2F6; margin-right: 5px;"></div>'
        '<span>In Playoff</span>'
        '</div>',
        unsafe_allow_html=True
    )

def render_playoff_bracket():
    st.markdown(f"##### Playoff")
    fig = create_playoff_brackets()
    st.plotly_chart(fig, config={'staticPlot': True})

if today < playoff_start:
    render_regular_season()
    st.markdown(f"")
    render_playoff_bracket()
else:
    render_playoff_bracket()
    st.markdown(f"")
    render_regular_season()