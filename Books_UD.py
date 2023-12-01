import requests
from datetime import datetime, timedelta
from draftkings import dk_main, noVig
from caesars import c_main

standard_conversion = {'Pass Yards', 'Pass Attempts', 'Pass TDs', 'Completions', 'Interceptions', 'Pass + Rush Yards',
'Rush Yards', 'Rush Attempts', 'Rush TDs', 'Rush + Rec Yards',
'Rec Yards', 'Receptions', 'Rec TDs',
'Solo Tackles', 'Tackels + Assists', 'Sacks', 'Assists',
'FG Made', 'Kicking Points',
'Points', 'Rebounds', 'Assists', '3PM', 'Blocks', 'Steals', 'Pts + Reb + Ast', 'Pts + Reb', 'Pts + Ast', 'Reb + Ast',
'Blocks + Steals',
'Shots', 'Points', 'Assists', 'Power Play Points', 'Blocks', 'Saves', 'Goals'}

stat_conversion = {'NFL': {'Rushing TDs': 'Rush TDs', 'Rec TDs': 'Rec TDs', 'Passing TDs': 'Pass TDs', 'Passing Yards': 'Pass Yards', 
'Completions': 'Completions', 'Passing Attempts': 'Pass Attempts', 'Pass + Rush Yards': 'Pass + Rush Yards', 'Interceptions':
'Interceptions', 'Receiving Yards': 'Rec Yards', 'Receptions': 'Receptions', 'Rushing Yards': 'Rush Yards', 'Rush + Rec Yards':
'Rush + Rec Yards', 'Rushing Attempts': 'Rush Attempts', 'Sacks': 'Sacks', 'Solo Tackles': 'Solo Tackles', 'Assists': 'Assists',
'Tackles + Assist': 'Tackles + Assists', 'FG Made': 'FG Made', 'Kicking Pts': 'Kicking Points'},
'NBA': {'Points': 'Points', '3-Pointers Made': '3PM', 'Pts + Rebs + Asts': 'Pts + Reb + Ast', 'Points + Rebounds': 'Pts + Reb', 
'Points + Assists': 'Pts + Ast', 'Rebounds + Assists': 'Reb + Ast', 'Rebounds': 'Rebounds', 'Assists': 'Assists', 
'Steals': 'Steals', 'Blocks': 'Blocks', 'Blocks + Steals': 'Blocks + Steals'},
'NHL': {'Shots': 'Shots', 'Points': 'Points', 'Assists': 'Assists', 'Power Play Points': 'Power Play Points',
'Blocked Shots': 'Blocks', 'Saves': 'Saves'}}

if __name__ == '__main__':
    dk_props_dict = dk_main()
    c_props_dict = c_main()
    #print(c_props_dict)

    UD = requests.get(url = 'https://api.underdogfantasy.com/beta/v5/over_under_lines').json()
    games = {}
    for game in UD['games']:
        date = datetime.strptime(game['scheduled_at'].split('T')[0], '%Y-%m-%d').strftime('%Y-%m-%d')
        games[game['away_team_id']] = game['sport_id']+'-'+date
        games[game['home_team_id']] = game['sport_id']+'-'+date
    apps = {}
    for app in UD['appearances']:
        apps[app['id']] = app['team_id']
    for prop in UD['over_under_lines']:
        stat = prop['over_under']['appearance_stat']['display_stat']
        title = prop['over_under']['title']
        p_name = title[:title.find(stat)-1]
        stat_value = prop['stat_value']
        app_id = apps[prop['over_under']['appearance_stat']['appearance_id']]
        if app_id not in games or app_id == None:
            continue
        league = games[app_id][:games[app_id].find('-')]
        if league not in stat_conversion or '+' in p_name or stat not in stat_conversion[league]:
            continue
        key = p_name + '-' + stat_conversion[league][stat] + '-' + games[app_id]
        if key in dk_props_dict:
            DK_line = list(dk_props_dict[key].keys())[0]
            if DK_line == float(stat_value):
                print(key, dk_props_dict[key], '-'+str(noVig(dk_props_dict[key][DK_line])), ' - Draftkings') \
                if noVig(dk_props_dict[key][DK_line]) >= 120 \
                and prop['options'][0]['payout_multiplier'] == '1.0' else None
        if key in c_props_dict:
            C_line = list(c_props_dict[key].keys())[0]
            if C_line == float(stat_value):
                print(key, c_props_dict[key], '-'+str(noVig(c_props_dict[key][C_line])), ' - Caesars') \
                if noVig(c_props_dict[key][C_line]) >= 120 \
                and prop['options'][0]['payout_multiplier'] == '1.0' else None