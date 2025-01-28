import streamlit as st

from data.marqueur import render_remove_checkbox, stats

from live_games import render_score
from progress_bar import render_progress_bar
from summary_df import render_summary_df
from season_chart import create_fig as create_season_chart
from position_charts import create_fig as create_position_chart

# Title of the Streamlit app
#st.title("")

render_progress_bar()
render_score()
render_remove_checkbox()

summary_df_event = render_summary_df()

if summary_df_event.selection.rows:
    selected_poolers = stats.summary.iloc[summary_df_event.selection.rows]['pooler_name'].tolist()
else:
    selected_poolers = None

fig = create_season_chart(stats.detail, selected_poolers)
st.plotly_chart(fig, config={'staticPlot': True})

st.markdown(f"**Game Played**")
fig = create_position_chart(stats.detail, "game_played", None, selected_poolers, True)
st.plotly_chart(fig, config={'staticPlot': True})

positions = ['Forward', 'Defender', 'Goalie', 'Team']
for position in positions:
    st.markdown(f"**{position}**")
    if position == positions[-1]:
        showticklabels = True
    else:
        showticklabels = False
    fig = create_position_chart(stats.detail, 'total_points', position, selected_poolers, showticklabels)
    st.plotly_chart(fig, config={'staticPlot': True})
