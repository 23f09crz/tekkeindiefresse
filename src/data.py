import json
import os
import time
import portalocker

def acquire_lock(file_obj):
    portalocker.lock(file_obj, portalocker.LOCK_EX)

def release_lock(file_obj):
    portalocker.unlock(file_obj)

def load_history():
    history_path = 'historico.json'
    if os.path.exists(history_path):
        try:
            with open(history_path, 'r+') as file:
                acquire_lock(file)
                try:
                    data = json.load(file)
                finally:
                    release_lock(file)
                return data
        except json.JSONDecodeError:
            with open(history_path, 'w') as file:
                acquire_lock(file)
                try:
                    json.dump({}, file)
                finally:
                    release_lock(file)
            return {}
    return {}

def save_history(data):
    with open('historico.json', 'w') as file:
        acquire_lock(file)
        try:
            json.dump(data, file, indent=4)
        finally:
            release_lock(file)

def remove_old_games_from_history(data):
    for team_id in list(data.keys()):
        data[team_id]['response'] = [game for game in data[team_id]['response'] if game['fixture']['status']['elapsed'] is None or game['fixture']['status']['elapsed'] > 70]
    save_history(data)

def load_fixture_statistics():
    stats_path = 'fixture_statistics.json'
    if os.path.exists(stats_path):
        try:
            with open(stats_path, 'r+') as file:
                acquire_lock(file)
                try:
                    data = json.load(file)
                finally:
                    release_lock(file)
                return data
        except json.JSONDecodeError:
            with open(stats_path, 'w') as file:
                acquire_lock(file)
                try:
                    json.dump({}, file)
                finally:
                    release_lock(file)
            return {}
    return {}

def save_fixture_statistics(data):
    with open('fixture_statistics.json', 'w') as file:
        acquire_lock(file)
        try:
            json.dump(data, file, indent=4)
        finally:
            release_lock(file)

def load_standings():
    standings_path = 'standings.json'
    if os.path.exists(standings_path):
        try:
            with open(standings_path, 'r+') as file:
                acquire_lock(file)
                try:
                    data = json.load(file)
                finally:
                    release_lock(file)
                return data
        except json.JSONDecodeError:
            return {}
    return {}

def save_standings(data):
    with open('standings.json', 'w') as file:
        acquire_lock(file)
        try:
            json.dump(data, file, indent=4)
        finally:
            release_lock(file)

def remove_old_fixture_statistics(data):
    current_time = int(time.time())
    one_week = 7 * 24 * 60 * 60  # 7 days in seconds

    for fixture_id in list(data.keys()):
        fixture_time = data[fixture_id][0]['fixture']['timestamp']
        if current_time - fixture_time > one_week:
            del data[fixture_id]

    save_fixture_statistics(data)