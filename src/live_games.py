import streamlit as st
from bs4 import BeautifulSoup

from util.style import team_images
from data.nhl import get_score


css = """
    <style>
    .grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr); /* 4 items per row */
        gap: 20px;
        justify-items: center;
        padding-bottom: 20px;
    }

    .container {
        text-align: center;
        font-weight: bold;
        width: 100%;
        min-width: 140px;
        padding: 0;
        color: #444444;
    }

    .game-status {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        font-weight: bold;
    }

    hr.game-info-split {
        margin: 1px 0;
    }

    .scoreboard {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .team img {
        width: 40px;
        height: 40px;
    }

    .score {
        font-size: 14px;
        font-weight: bold;
        margin: 0 4px;
    }
    </style>
"""


def render_score():
    scores = get_score()
    if scores is None:
        return

    st.markdown(css, unsafe_allow_html=True)
    st.markdown(f"***{scores['current_date']}***")

    html = '<div class="grid">'
    for game in scores['games']:
        if game['game_state'] in ('LIVE', 'CRIT'):
            game_status_html = f"""<div class="period">{game['period_label']}</div> <div class="time">{game['time_remaining']}</div>"""
        elif game['game_state'] in ('FINAL', 'OFF'):
            game_status_html = f"""<div class="period">{game['period_label']}</div><div class="time">Final</div>"""
        elif game['game_state'] in ('FUT', 'PRE'):
            game_status_html = f"""<div class="period">Starts at</div><div class="time">{game['start_time']}</div>"""
        else:
            game_status_html = game['game_state']
        
        # HTML content with the desired layout
        html += f"""
        <a href="https://www.nhl.com{game['game_center_link']}" target="_blank" style="text-decoration: none;">
        <div class="container">
            <div class="game-status">
                {game_status_html}
            </div>
            <hr class="game-info-split"/>
            <div class="scoreboard">
                <div class="team home-team">
                    <img src="{team_images.get(game['home_team'])}" alt="{game['home_team']}"/>
                </div>
                <div class="score">
                    <span class="home-score">{game['home_score']}</span> - <span class="away-score">{game['away_score']}</span>
                </div>
                <div class="team away-team">
                    <img src="{team_images.get(game['away_team'])}" alt="{game['away_team']}"/>
                </div>
            </div>
        </div>
        </a>
        """
    html += '</div>'

    html = BeautifulSoup(html, features="html.parser").prettify()
    st.markdown(html, unsafe_allow_html=True)
