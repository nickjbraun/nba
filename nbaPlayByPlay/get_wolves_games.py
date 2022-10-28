# %% imports
import requests
import pandas as pd
import numpy as np
import io
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
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
# %%
# get game logs from the 2022-23 regular season
gamefinder = leaguegamefinder.LeagueGameFinder(
    season_nullable='2022-23',
    league_id_nullable='00',
    season_type_nullable='Regular Season')
games = gamefinder.get_data_frames()[0]

# %% Filter for only wolves games
wolves_games = games[games['TEAM_ABBREVIATION'] == 'MIN']
# Get a list of distinct game ids 
wolves_game_ids = wolves_games['GAME_ID'].unique().tolist()
# %%
# create function that gets pbp logs from the 2020-21 season
def get_data(game_id):
    play_by_play_url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_"+game_id+".json"
    response = requests.get(url=play_by_play_url, headers=custom_headers).json()
    play_by_play = response['game']['actions']
    df = pd.DataFrame(play_by_play)
    df['gameid'] = game_id
    return df

# %% get data from all ids (takes awhile)
df_pbp = []
for game_id in wolves_game_ids:
    game_data = get_data(game_id)
    df_pbp.append(game_data)
df_pbp = pd.concat(df_pbp, ignore_index=True)
# %% create wolves or opponent column
df_pbp.loc[df_pbp['teamTricode'] != 'MIN', 'team'] = 'Opponent'
df_pbp.loc[df_pbp['teamTricode'] == 'MIN', 'team'] = 'Timberwolves'

# %% add in point value column for made shots and filter for made shots
ft_mask = (df_pbp['actionType'] == 'freethrow') & (df_pbp['shotResult'] ==  'Made')
fg2_mask = (df_pbp['actionType'] == '2pt') & (df_pbp['shotResult'] ==  'Made')
fg3_mask = (df_pbp['actionType'] == '3pt') & (df_pbp['shotResult'] ==  'Made')
df_pbp.loc[df_pbp['actionType'] == 'freethrow', 'points_scored'] = 1
df_pbp.loc[df_pbp['actionType'] == '2pt', 'points_scored'] = 2
df_pbp.loc[df_pbp['actionType'] == '3pt', 'points_scored'] = 3
df_pbp = df_pbp[df_pbp['shotResult'] == 'Made']
# %% pare down the df so it is easier to read
df_pbp = df_pbp[['gameid', 'team', 'period', 'clock', 'description', 'actionType', 'shotResult', 'points_scored',
                 'scoreHome', 'scoreAway']]

# %% clean up the clock columns
df_pbp.loc[df_pbp['period'] == 1, 'dummy_q_start_dt'] = dt.datetime(1900, 1, 1, 0, 12, 0)
df_pbp.loc[df_pbp['period'] == 2, 'dummy_q_start_dt'] = dt.datetime(1900, 1, 1, 0, 24, 0)
df_pbp.loc[df_pbp['period'] == 3, 'dummy_q_start_dt'] = dt.datetime(1900, 1, 1, 0, 36, 0)
df_pbp.loc[df_pbp['period'] == 4, 'dummy_q_start_dt'] = dt.datetime(1900, 1, 1, 0, 48, 0)
df_pbp.loc[df_pbp['period'] == 5, 'dummy_q_start_dt'] = dt.datetime(1900, 1, 1, 0, 53, 0)

df_pbp['clock_min'] = df_pbp['clock'].str[2:4]
df_pbp['clock_sec'] = df_pbp['clock'].str[5:7]
df_pbp['clock_dt'] = pd.to_datetime(df_pbp['clock_min'] + df_pbp['clock_sec'],
                                    format='%M%S')
df_pbp['elapsed'] = df_pbp['dummy_q_start_dt'] - df_pbp['clock_dt']
df_pbp['min_of_game'] = (df_pbp['elapsed'] / np.timedelta64(1,'m')).round(0)

# %% group by team and minutes sum points
df_sum = df_pbp.groupby(['team','min_of_game'])[['points_scored']].sum().reset_index()

df_sum.loc[df_sum['team'] == 'Opponent', 'points_scored'] = -df_sum['points_scored']
df_sum = df_sum.sort_values('min_of_game')
df_min = df_sum[df_sum['team']=='Timberwolves']
df_opp = df_sum[df_sum['team']=='Opponent']
df_cum_sum = df_sum.groupby(['min_of_game'])[['points_scored']].sum().cumsum().reset_index()

# %%
fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=df_cum_sum['min_of_game'],
        y=df_cum_sum['points_scored'],
        name='Cumulative Net Points',
        marker_color='#79C019'
    ))
fig.add_trace(
    go.Bar(
        x=df_min['min_of_game'],
        y=df_min['points_scored'],
        name='Timberwolves Points',
        marker_color='#041D3E'
    ))
fig.add_trace(
    go.Bar(
        x=df_opp['min_of_game'],
        y=df_opp['points_scored'],
        name='Opponent Points',
        marker_color='#1E6194'
    ))
fig.update_layout(barmode='overlay')
fig.update_layout(
    title="Timberwolves vs. Opponent Points, minute-by-minute",
    xaxis_title="Minute of game",
    yaxis_title="Cumulative points (bars),</br></br> Cumulative net points (line)",
    # font=dict(
    #     family="Courier New, monospace",
    #     size=12,
    #     color="black"
    # )
)

# fig.update_layout(plot_bgcolor='#FFF8EA',
#                   paper_bgcolor='#FFF8EA')
fig.update_layout(
    xaxis = dict(
        tickmode = 'linear',
        tick0 = 0,
        dtick = 2
    )
)
fig.add_hline(y=0)
fig.add_vline(x=11.5, line_dash="dash")
fig.add_vline(x=23.5, line_dash="dash")
fig.add_vline(x=35.5, line_dash="dash")
fig.add_vline(x=47.5, line_dash="dash")
fig.show()





# # %%
# season = '2021-22'
# teams = pd.DataFrame(teams.get_teams()) # get team info

# names = teams['abbreviation'].values # get list of teams abbreviations
# # %%
# # create the url parts that do not change
# base_url = r'http://stats.nba.com/media/img/teams/logos/season/'
# season = season
# url_end = r'_logo.svg'

# # use gridspec to create the subplots
# plt.figure(figsize=(30,30))
# gs1 = gridspec.GridSpec(6, 5)
# gs1.update(wspace=0.01, hspace=0.01) # set the spacing between axes. 

# for i,name in enumerate(names):
#     ax1 = plt.subplot(gs1[i])
#     I = svg2png(url=base_url + season + '//' +name + url_end) # convert svg to png string
#     Im = Image.open(io.StringIO(I)) # convert png string to an image format
#     ax1.imshow(Im) # plot image
#     plt.gca().axis('off')
# %%
