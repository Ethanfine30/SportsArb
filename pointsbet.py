import json
import pandas as pd
from unidecode import unidecode
import warnings
import requests
import numpy as np
from multiprocessing import Process, Manager
warnings.filterwarnings('ignore')

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
cookies = {'cookie_name': 'cookie_value'}

def american(odds):
    odds = float(odds)
    if odds == 1:
        return "Undefined"
    if odds >= 2:
        return '+' + str(round(100* (odds-1)))
    if odds < 2:
        return round(-100/ (odds-1))

def pointsbet(league_list):
    final_list = []
    league_dict = {'EPL': '18034', 'Bundesliga': '13895', 'LaLiga': '19787', 'SerieA': '18042', 'Ligue1': '19791', 
        'MLS': '17989'}
    for league in league_list:
        league_json = requests.get('https://api.nj.pointsbet.com/api/v2/competitions/%s/events/featured' %(league_dict[league]), 
            headers = headers).json()
        game_ids = [game['key'] for game in league_json['events'] if game['isLive'] == False]
        final_list += game_ids
    return final_list

def parse(gameID, results):
    props_dict = {'PLAYER TOTAL SHOTS': 'Shots', 'PLAYER TOTAL TACKLES': 'Tackles',
                'PLAYER TOTAL SHOTS ON TARGET': 'Shots on Target', 'PLAYER TOTAL PASSES': 'Passes'}
    url = 'https://api.nj.pointsbet.com/api/mes/v3/events/%s' %(gameID)
    game_json = requests.get(url, headers = headers).json()
    props = pd.DataFrame(columns = ['playerID', 'line', 'odds', 'prop'])
    for market in game_json['fixedOddsMarkets']:
        if market['eventName'] in props_dict:
            for prop in market['outcomes']:
                props.loc[len(props)] = [prop['playerId'], prop['points'], american(prop['price']), 
                props_dict[market['eventName']]]
    players = pd.DataFrame(columns = ['playerID', 'playerName'])
    for player in game_json['presentationData']['presentationFilters']:
        if player['id'].startswith('Player-'):
            players.loc[len(players)] = [player['id'][player['id'].find('-')+1:], player['name'] ]
    props = pd.merge(props, players, on = 'playerID')
    props = props.pivot_table(index=['playerName', 'prop'], columns='line', values='odds', fill_value='-', aggfunc='first')
    props.reset_index(inplace=True)
    results.append(props)

def main(gameIDs):
    with Manager() as manager:
        results = manager.list()
        processes = []
        for game_id in gameIDs:
            p = Process(target=parse, args=(game_id, results))
            p.start()
            processes.append(p)

        for process in processes:
            process.join()

        final_df = pd.concat(results, ignore_index=True)  # Concatenate the results into a single DataFrame
        final_df['playerName'] = final_df['playerName'].apply(lambda x: unidecode(x))
        return final_df

def get_df():
    gameIDs = pointsbet(['EPL'])
    return main(gameIDs)

if __name__ == "__main__":
    df = get_df()
    print(df)