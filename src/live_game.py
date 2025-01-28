import streamlit as st
import requests
from pathlib import Path
import base64
import datetime as dt
import pytz
from bs4 import BeautifulSoup

url = "https://api-web.nhle.com/v1/score/now"


def render_score():
    def load_team_images():
        def open_image(path: str):
            with open(path, "rb") as p:
                file = p.read()
                return f"data:image/png;base64,{base64.b64encode(file).decode()}"

        dir_path = Path(r"assets/img/teams")
        files = [file for file in dir_path.iterdir() if file.is_file()]
        return {file.stem: open_image(f"{dir_path}/{file.name}") for file in files if file.suffix == ".png"}
    team_images = load_team_images()

    # CSS styles for the layout
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

    # Display the styled HTML in Streamlit
    st.markdown(css, unsafe_allow_html=True)

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        games = data.get("games", [])
        if not games:
            return None

        current_date = data.get('currentDate')
        if current_date:
            # TODO: Put in utils
            current_date  = dt.datetime.strptime(current_date, "%Y-%m-%d")
            # Helper function to determine the ordinal suffix
            def get_ordinal_suffix(day):
                if 11 <= day <= 13:  # Special case for 11th, 12th, 13th
                    return "th"
                elif day % 10 == 1:
                    return "st"
                elif day % 10 == 2:
                    return "nd"
                elif day % 10 == 3:
                    return "rd"
                else:
                    return "th"

            # Get the day and its ordinal suffix
            day = current_date .day
            ordinal_suffix = get_ordinal_suffix(day)
            current_date = current_date.strftime(f"%B {day}{ordinal_suffix}, %Y")

            st.markdown(f"***{current_date}***")
        html = '<div class="grid">'
        # TODO: Put in function
        for i, game in enumerate(games):
            game_id = game.get('id')
            game_type = game.get('gameType')  # Season=2, Playoff=3
            game_date = game.get('gameDate')
            start_time = game.get('startTimeUTC')
            if start_time:
                start_time = dt.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
                utc_zone = pytz.utc
                et_zone = pytz.timezone("US/Eastern")
                start_time = utc_zone.localize(start_time)
                start_time = start_time.astimezone(et_zone)
                start_time = start_time.strftime("%H:%M ET")
            game_state = game.get('gameState')  # FUT, PRE, LIVE, OFF

            home_team = game.get("homeTeam", {}).get("abbrev", "")
            home_score = game.get("homeTeam", {}).get("score", 0)
            home_odds = game.get("homeTeam", {}).get("odds", [])  # TODO: Use
            away_team = game.get("awayTeam", {}).get("abbrev", "")
            away_score = game.get("awayTeam", {}).get("score", 0)
            away_odds = game.get("awayTeam", {}).get("score", 0)  # TODO: Use

            period_descriptor = game.get('periodDescriptor', {})
            period_number = period_descriptor.get('number')
            period_type = period_descriptor.get('periodType')  # REG, OT, SO
            if period_type == 'REG':
                period_label = f'P{period_number}'
            elif period_type == 'OT':
                period_label = f'OT{period_number % 3}'
            elif period_type == 'SO':
                period_label = f'SO'
            else:
                period_label = f'{period_type}{period_number}'

            clock = game.get("clock", {})
            time_remaining = clock.get('timeRemaining')
            in_intermission = clock.get('inIntermission')
            if in_intermission:
                time_remaining = "Intermission"

            goals = game.get("goals", []) # TODO: Use?
            game_link = game.get("gameCenterLink", "")

            if game_state == "LIVE":
                game_status_html = f"""<div class="period">{period_label}</div> <div class="time">{time_remaining}</div>"""
            elif game_state == "OFF":
                game_status_html = f"""<div class="period">{period_label}</div><div class="time">Final</div>"""
            elif game_state in ("FUT", "PRE"):
                game_status_html = f"""<div class="period">Starts at</div><div class="time">{start_time}</div>"""  # TODO: Parse time

            # HTML content with the desired layout
            html += f"""
            <a href="https://www.nhl.com{game_link}" target="_blank" style="text-decoration: none;">
            <div class="container">
                <div class="game-status">
                    {game_status_html}
                </div>
                <hr class="game-info-split"/>
                <div class="scoreboard">
                    <div class="team home-team">
                        <img src="{team_images[home_team]}" alt="{home_team}"/>
                    </div>
                    <div class="score">
                        <span class="home-score">{home_score}</span> - <span class="away-score">{away_score}</span>
                    </div>
                    <div class="team away-team">
                        <img src="{team_images[away_team]}" alt="{away_team}"/>
                    </div>
                </div>
            </div>
            </a>
            """
        html += '</div>'

        html = BeautifulSoup(html,features="html.parser").prettify()
        st.markdown(html, unsafe_allow_html=True)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")


