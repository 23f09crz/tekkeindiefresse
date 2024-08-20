import streamlit as st
from datetime import datetime

from api import get_team_history, get_standings
from utils import get_team_position
def get_result_emoji(team, home_score, away_score):
    if home_score > away_score:
        return "✅" if team == "home" else "❌"
    elif home_score < away_score:
        return "❌" if team == "home" else "✅"
    else:
        return "⏸"

async def display_team_history(team_id, team_name, half, limit=10):
    team_history = get_team_history(team_name, team_id)
    valid_games = [game for game in team_history if
                   game['goals']['home'] is not None and game['goals']['away'] is not None]
    st.write(f"Últimos {limit} jogos de {team_name}:")

    fixture_ids = [game['fixture']['id'] for game in valid_games[1:limit + 1]]

    for game in valid_games[1:limit + 1]:
        fixture = game['fixture']
        date = datetime.strptime(fixture['date'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d/%m')
        home_team = game['teams']['home']['name']
        away_team = game['teams']['away']['name']
        match(half):
            case 1:
                home_score = game['score']['halftime']['home']
                away_score = game['score']['halftime']['away']
                print(home_score)
                print(away_score)
            case _:
                home_score = game['goals']['home']
                away_score = game['goals']['away']


        if home_team == team_name:
            color = 'green' if home_score > 0 else 'red'
            result_emoji = get_result_emoji("home", home_score, away_score)
            st.markdown(
                f"{date}: {result_emoji} <span style='color:{color}'><b>{home_team} {home_score}</b></span> x {away_score} {away_team}",
                unsafe_allow_html=True)
        else:
            color = 'green' if away_score > 0 else 'red'
            result_emoji = get_result_emoji("away", home_score, away_score)
            st.markdown(
                f"{date}: {result_emoji} {home_team} {home_score} x <span style='color:{color}'><b>{away_team} {away_score}</b></span>",
                unsafe_allow_html=True
            )


async def display_game(selected_game, half):
    print('DISPLAY GAME RAN')
    home_team = selected_game['teams']['home']
    away_team = selected_game['teams']['away']

    home_team_id = home_team['id']
    away_team_id = away_team['id']
    home_team_name = home_team['name']
    away_team_name = away_team['name']

    # Get standings
    league_id = selected_game['league']['id']
    season = selected_game['league']['season']
    standings = get_standings(league_id, season)

    # Get team positions
    home_team_position = get_team_position(standings, home_team_id)
    away_team_position = get_team_position(standings, away_team_id)

    status = selected_game['fixture']['status']
    time_elapsed = status['elapsed']
    status_description = status['short']

    if status_description == 'HT':
        status_text = "INTERVALO"
    else:
        status_text = f"{time_elapsed} mins"
    

    if home_team_position:
        st.title(
            f"{home_team_name} ({home_team_position}°) x {away_team_name} ({away_team_position}°) - {status_text}")
    else:
        st.title(f"{home_team_name} x {away_team_name} - {status_text}")

    goals = selected_game['goals']
    home_score = goals['home']
    away_score = goals['away']
    st.header(f"{home_score} x {away_score}")

    home_team_history = get_team_history(home_team_name, home_team_id)
    away_team_history = get_team_history(away_team_name, away_team_id)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Histórico {home_team_name}:")
        await display_team_history(home_team_id, home_team_name, half)

    with col2:
        st.subheader(f"Histórico {away_team_name}:")
        await display_team_history(away_team_id, away_team_name, half)
