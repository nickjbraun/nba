# %% imports
import requests
import pandas as pd
import numpy as np
import io
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder

# %% custom headers
custom_headers  = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-token': 'true',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}
# %% get games
play_by_play_url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0042000404.json"
response = requests.get(url=play_by_play_url, headers=custom_headers).json()
play_by_play = response['game']['actions']
df = pd.DataFrame(play_by_play)
# %%
# get game logs from the 2021-22 and 2022-23 regular season
# 2021-2022
gamefinder = leaguegamefinder.LeagueGameFinder(
    season_nullable='2021-22',
    league_id_nullable='00',
    season_type_nullable='Regular Season')
games21_22 = gamefinder.get_data_frames()[0]
# 2022-2023
gamefinder = leaguegamefinder.LeagueGameFinder(
    season_nullable='2022-23',
    league_id_nullable='00',
    season_type_nullable='Regular Season')
games22_23 = gamefinder.get_data_frames()[0]

games = pd.concat([games21_22, games22_23])
# %% Filter for only wolves games
wolves_games = games[games['TEAM_ABBREVIATION'] == 'MIN']
# Get a list of distinct game ids 
wolves_game_ids = wolves_games['GAME_ID'].unique().tolist()
# %%



# create function that gets pbp logs from the 2020-21 season
def get_data(game_id):
    play_by_play_url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_"+game_id+".json"
    response = requests.get(url=play_by_play_url, headers=headers).json()
    play_by_play = response['game']['actions']
    df = pd.DataFrame(play_by_play)
    df['gameid'] = game_id
    return df

# %%
