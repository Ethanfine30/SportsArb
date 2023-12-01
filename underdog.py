import requests
import json
import pandas as pd
from unidecode import unidecode

def underdog():
    UD_json_data = requests.get('https://api.underdogfantasy.com/beta/v5/over_under_lines').json()
    UD_players_df = pd.json_normalize(UD_json_data['over_under_lines'])
    UD_players_df.drop(columns = ['id', 'live_event_stat', 'over_under_id', 'rank', 'status', 'over_under.id',
        'over_under.appearance_stat.id', 'over_under.appearance_stat.appearance_id', 'over_under.appearance_stat.stat',
        'options', 'over_under.appearance_stat.graded_by', 'over_under.boost', 'over_under.scoring_type_id', 
        'over_under.appearance_stat.pickem_stat_id', 'live_event'], inplace = True)
    UD_players_df.rename(columns = {'stat_value': 'line_score', 
        'over_under.appearance_stat.display_stat': 'stat_type'}, inplace = True)
    UD_players_df['name'] = UD_players_df.apply(lambda row: row['over_under.title'].split(row['stat_type'])[0].strip(), axis=1)
    UD_players_df.drop(columns = ['over_under.title'], inplace = True)
    UD_players_df['name'] = UD_players_df['name'].apply(unidecode)
    UD_players_df = UD_players_df[~UD_players_df['name'].str.contains('\+')]
    UD_propType_replacement_dict = {'Shots Attempted': 'Shots'}
    UD_players_df['stat_type'] = UD_players_df['stat_type'].replace(UD_propType_replacement_dict)
    UD_players = pd.DataFrame(columns = ['name', 'sport'])
    for player in UD_json_data['players']:
        UD_players.loc[len(UD_players)] = [player['first_name'] + ' ' + player['last_name'], player['sport_id']]
    UD_final_df = pd.merge(UD_players_df, UD_players, on = 'name')
    print(UD_final_df)
    return UD_final_df
UD = underdog()