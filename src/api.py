import requests
import streamlit as st
import aiohttp
import asyncio
import time

from data import load_history, save_history, load_fixture_statistics, save_fixture_statistics, load_standings, save_standings
from variables import live_games_api_url, team_history_api_url, fixture_statistics_api_url, standings_api_url, headers


def get_live_games():
    response = requests.get(live_games_api_url, headers=headers)
    if response.status_code == 200:
        games = response.json().get('response', [])
        print('os Jogos Ao Vivo Foram coletados')
        return [game for game in games if game['fixture']['status']['elapsed'] is None or game['fixture']['status']['elapsed'] < 71]
    else:
        st.error("Erro ao buscar jogos ao vivo")
        return []


def get_team_history(team_name, team_id, last_n=20):
    history_data = load_history()
    if str(team_id) in history_data:
        print(f'Consultando Localmente {team_name}')
        return history_data[str(team_id)]['response']
    else:
        params = {
            "team": team_id,
            "last": last_n
        }
        response = requests.get(team_history_api_url, headers=headers, params=params)
        if response.status_code == 200:
            print(f'Consultando na API {team_name}')
            history_data[str(team_id)] = response.json()
            save_history(history_data)
            return history_data[str(team_id)]['response']
        else:
            st.error(f"Erro ao buscar histórico para o time {team_id}")
            return []


async def get_fixture_statistics(fixture_ids):
    stats_data = load_fixture_statistics()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for fixture_id in fixture_ids:
            if str(fixture_id) in stats_data:
                print(f'Consultando Localmente estatísticas para fixture {fixture_id}')
            else:
                tasks.append(fetch_fixture_statistics(session, fixture_id))

        if tasks:
            new_responses = await asyncio.gather(*tasks)
            for fixture_id, stats in new_responses:
                stats_data[str(fixture_id)] = stats
            save_fixture_statistics(stats_data)

        return {fixture_id: stats_data.get(str(fixture_id), []) for fixture_id in fixture_ids}


async def fetch_fixture_statistics(session, fixture_id):
    params = {"fixture": str(fixture_id), "type": "Corner Kicks"}
    async with session.get(fixture_statistics_api_url, headers=headers, params=params) as response:
        if response.status == 200:
            data = await response.json()
            return fixture_id, data.get('response', [])
        else:
            print(f"Erro ao buscar estatísticas: {response.status}")
            return fixture_id, []


def get_standings(league_id, season):
    standings_data = load_standings()
    cache_key = f"{league_id}_{season}"

    if cache_key in standings_data:
        cached_data = standings_data[cache_key]
        return cached_data['data']

    params = {
        "league": league_id,
        "season": season
    }
    response = requests.get(standings_api_url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        standings_data[cache_key] = {
            'data': data.get('response', []),
            'timestamp': int(time.time())
        }
        return data.get('response', [])
    else:
        print(f"Erro ao buscar classificação: {response.status_code}")
        return []