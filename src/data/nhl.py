import streamlit as st
from enum import Enum
import requests
import datetime as dt
import pytz

api = "https://api-web.nhle.com"


class GameState(str, Enum):
    FUTURE = "FUT"
    PREGAME = "PRE"
    LIVE = "LIVE"
    ENDED = "OFF"


@st.cache_data(tt=10)
def get_score():
    endpoint = "/v1/score/now"
    scores = None

    try:
        response = requests.get(api + endpoint)
        response.raise_for_status()

        data = response.json()
        games = data.get("games", [])
        if not games:
            return scores

        scores = {}
        current_date = data.get('currentDate')
        if current_date:
            # TODO: Put in utils
            current_date = dt.datetime.strptime(current_date, "%Y-%m-%d")

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

            day = current_date.day
            ordinal_suffix = get_ordinal_suffix(day)
            current_date = current_date.strftime(f"%B {day}{ordinal_suffix}, %Y")
        scores['current_date'] = current_date

        scores['games'] = []
        for game in games:
            score = {}
            score['game_id'] = game.get('id')
            score['game_type'] = game.get('gameType')  # Season=2, Playoff=3
            score['game_date'] = game.get('gameDate')

            start_time = game.get('startTimeUTC')
            if start_time:
                start_time = dt.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
                utc_zone = pytz.utc
                et_zone = pytz.timezone("US/Eastern")
                start_time = utc_zone.localize(start_time)
                start_time = start_time.astimezone(et_zone)
                start_time = start_time.strftime("%H:%M ET")
            score['start_time'] = start_time
            score['game_state'] = GameState(game.get('gameState'))  # FUT, PRE, LIVE, OFF
            score['home_team'] = game.get("homeTeam", {}).get("abbrev", "")
            score['home_score'] = game.get("homeTeam", {}).get("score", 0)
            score['home_odds'] = game.get("homeTeam", {}).get("odds", [])  # TODO: Use
            score['away_team'] = game.get("awayTeam", {}).get("abbrev", "")
            score['away_score'] = game.get("awayTeam", {}).get("score", 0)
            score['away_odds'] = game.get("awayTeam", {}).get("score", 0)  # TODO: Use

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
            score['period_label'] = period_label

            clock = game.get("clock", {})
            time_remaining = clock.get('timeRemaining')
            in_intermission = clock.get('inIntermission')
            if in_intermission:
                time_remaining = "Intermission"
            score['time_remaining'] = time_remaining

            score['goals'] = game.get("goals", [])  # TODO: Use?
            score['game_center_link'] = game.get("gameCenterLink", "")

            scores['games'].append(score)

    except requests.RequestException as e:
        print(f"Error fetching data: {e}")

    return scores
