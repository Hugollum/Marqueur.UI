import streamlit as st
from datetime import datetime

seasons = {
    '2025-2026': {
        'label': 2526,
        'years': '20252026',
        'season_start_dt': datetime(2025, 9, 30),
        'playoff_start_dt': datetime(2026, 4, 16),
        'season_end_dt':  datetime(2026, 6, 30),
        'is_current': True,
    },
    '2024-2025': {
        'label': 2425,
        'years': '20242025',
        'season_start_dt': datetime(2024, 9, 30),
        'playoff_start_dt': datetime(2025, 4, 17),
        'season_end_dt':  datetime(2025, 6, 30),
        'is_current': False,
    },
}

def render_season_selector():
    season_select_box = st.selectbox('Season', seasons.keys())

    season = seasons[season_select_box]
    st.session_state['season_label'] = season['label']
    st.session_state['season_years'] = season['years']
    st.session_state['season_start'] = season['season_start_dt']
    st.session_state['playoff_start'] = season['playoff_start_dt']
    st.session_state['season_end'] = season['season_end_dt']
    st.session_state['is_current_season'] = season['is_current']

