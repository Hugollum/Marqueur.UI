import streamlit as st


def render_progress_bar():
    # Define the start, playoff, and end dates of the hockey season
    today = st.session_state.get('today')
    season_start = st.session_state.get('season_start')
    season_end = st.session_state.get('season_end')
    playoff_start = st.session_state.get('playoff_start')

    if today < season_start:
        progress_percent = 0
        playoff_percent = 0
        message = "The hockey season hasn't started yet."
    elif today > season_end:
        progress_percent = 100
        playoff_percent = (playoff_start - season_start).days / (season_end - season_start).days * 100
        message = "The hockey season is over."
    else:
        total_days = (season_end - season_start).days
        elapsed_days = (today - season_start).days
        progress_percent = (elapsed_days / total_days) * 100
        playoff_percent = (playoff_start - season_start).days / total_days * 100
        message = f"The hockey season is {elapsed_days} days in."

    html = f"""
        <style>
        .progress-container {{
            position: relative;
            width: 100%;
            background-color: #F0F2F6; /* Light gray background */
            border-radius: 10px;
            height: 30px;
            margin: 20px 0;
        }}
        .progress-bar {{
            width: {progress_percent}%;
            height: 100%;
            background-color: #444444; /* Black progress */
            border-radius: 10px 0 0 10px; /* Rounded left corner only */
        }}
        .playoff-line {{
            position: absolute;
            left: {playoff_percent}%;
            top: 0;
            bottom: 0;
            border-left: 2px dashed #444444; /* Dashed black line */
            z-index: 2;
        }}
        .regular-season-label, .playoff-label {{
            position: absolute;
            top: -30px; /* Position above the bar */
            font-size: 14px;
            color: #444444;;
            font-weight: bold;
        }}
        .regular-season-label {{
            left: 0;
            width: {playoff_percent}%;
            text-align: center;
        }}
        .playoff-label {{
            left: {playoff_percent}%;
            width: {100 - playoff_percent}%;
            text-align: center;
        }}

        </style>
        <div class="progress-container">
            <div class="progress-bar"></div>
            <div class="playoff-line"></div>
            <div class="regular-season-label">Regular Season</div>
            <div class="playoff-label">Playoffs</div>
        </div>
    """

    st.markdown(html, unsafe_allow_html=True)