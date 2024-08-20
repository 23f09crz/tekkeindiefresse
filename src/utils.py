import streamlit as st
from typing import List, Dict
import asyncio
from api import get_team_history

def get_team_position(standings, team_id):
    for league in standings:
        for standing in league.get('league', {}).get('standings', []):
            for team in standing:
                if team['team']['id'] == team_id:
                    return team['rank']
    return None



async def get_team_history_async(team_name: str, team_id: int):
    return await asyncio.to_thread(get_team_history, team_name, team_id)


def calculate_average_goals(team_history: Dict, team_name: str, limit=10):
    try:
        valid_games = [game for game in team_history if
                       game['goals']['home'] is not None and game['goals']['away'] is not None]
        total_goals = sum(
            game['goals']['home'] if game['teams']['home']['name'] == team_name else game['goals']['away'] for game in
            valid_games[:limit])
        return total_goals / limit
    except Exception as e:
        st.error(f"Erro ao calcular média de gols: {e}")
        return "Não foi possível calcular a média"


def filter_second_half_games(games: List[Dict]) -> List[Dict]:
    return [game for game in games if
            game['fixture']['status']['short'] == "HT" or
            (game['fixture']['status']['short'] == '2H' and game['fixture']['status']['elapsed'] < 71)]


def has_first_half_goal_tendency(team_history: List[Dict], team_name: str, threshold: int = 6,
                                 sample_size: int = 10) -> bool:
    recent_games = team_history[:sample_size]
    games_with_first_half_goals = 0

    for game in recent_games:
        home_team = game['teams']['home']['name']
        away_team = game['teams']['away']['name']
        home_score = game['score']['halftime']['home']
        away_score = game['score']['halftime']['away']

        # Debug print
        print(f"{home_team} vs {away_team}: Halftime score {home_score}-{away_score}")

        if home_team == team_name:
            if home_score is not None and home_score > 0:
                games_with_first_half_goals += 1
        elif away_team == team_name:
            if away_score is not None and away_score > 0:
                games_with_first_half_goals += 1

    print(f"{team_name}: {games_with_first_half_goals} games with first half goals out of {len(recent_games)}")
    return games_with_first_half_goals >= threshold


async def filter_first_half_games(live_games: List[Dict]) -> List[Dict]:
    first_half_games = [game for game in live_games if (game['fixture']['status']['short'] == '1H' and game['fixture']['status']['elapsed'] < 36) ]

    async def process_game(game):
        home_team = game['teams']['home']
        away_team = game['teams']['away']

        home_history = await get_team_history_async(home_team['name'], home_team['id'])
        away_history = await get_team_history_async(away_team['name'], away_team['id'])

        home_tendency = has_first_half_goal_tendency(home_history, home_team['name'])
        away_tendency = has_first_half_goal_tendency(away_history, away_team['name'])

        return game if home_tendency or away_tendency else None

    results = await asyncio.gather(*[process_game(game) for game in first_half_games])
    return [game for game in results if game is not None]

