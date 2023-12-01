import requests
from multiprocessing import Process, Manager

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
leagues_conversion = {'basketball': ['NBA'], 'americanfootball': ['NFL'], 'icehockey': ['NHL']}
def get_gameIDs(leagues):
    l_links = []
    for league in leagues:
        sport = requests.get(url = 
        'https://api.americanwagering.com/regions/us/locations/ny/brands/czr/sb/v3/sports/%s/events/schedule' %(league),
        headers= headers).json()
        for competition in sport['competitions']:
            if competition['name'] in leagues_conversion[league]:
                l_links.append('https://api.americanwagering.com/regions/us/locations/ny/brands/czr/sb/v3/sports/%s/events/schedule/?competitionIds=%s' %(league, competition['id']))
    g_links = []
    for link in l_links:
        league_json = requests.get(url = link, headers= headers).json()
        for game in league_json['competitions'][0]['events']:
            id = game['id']
            g_links.append('https://api.americanwagering.com/regions/us/locations/ny/brands/czr/sb/v3/events/%s' %(id))
    return g_links

stat_conversion = {'NFL': {'Player Total Passing TDs': 'Pass TDs', 'Player Total Passing Yards': 'Pass Yards', 
'Player Total Passing Completions': 'Completions', 'Player Total Passing Attempts': 'Pass Attempts',
'Player Total Receiving Yards': 'Rec Yards', 'Player Total Receptions': 'Receptions', 
'Player Total Rushing Yards': 'Rush Yards', 'Player Total Rushing + Receiving Yards': 'Rush + Rec Yards', 
'Player Total Rushing Attempts': 'Rush Attempts', 'Player Total Tackles + Assists': 'Tackles + Assists', 
'Player Total Made Field Goals': 'FG Made', 'Player Total Kicking Points': 'Kicking Points'},

'NBA': {'Player Total Points': 'Points', 'Player Total 3pt Field Goals': '3PM', 
'Player Total Points + Assists + Rebounds': 'Pts + Reb + Ast', 'Player Total Points + Rebounds': 'Pts + Reb', 
'Player Total Points + Assists': 'Pts + Ast', 'Player Total Rebounds + Assists': 'Reb + Ast', 
'Player Total Rebounds': 'Rebounds', 'Player Total Assists': 'Assists', 'Player Total Steals': 'Steals', 
'Player Total Blocks': 'Blocks', 'Player Total Blocks + Steals': 'Blocks + Steals'},
}

def parse(link, props_dict):
    props = {}
    game_json = requests.get(url = link, headers=headers).json()
    league = game_json['competitionName']
    for market in game_json['markets']:
        if market['displayName'] in stat_conversion[league].keys():
            stat = stat_conversion[league][market['displayName']]
            p_name = market['metadata']['player']
            date = game_json['startTime'][:game_json['startTime'].find('T')]
            key = p_name + '-' + stat + '-' + league + '-' + date
            line = market['line']
            props[key] = {line: [int(market['selections'][0]['price']['a']), int(market['selections'][1]['price']['a'])]}
    props_dict.update(props)

def c_main():
    manager = Manager()
    props_dict = manager.dict()
    jsons = get_gameIDs(['basketball', 'americanfootball'])
    processes = []
    for link in jsons:
        p = Process(target = parse, args = (link, props_dict))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    #print(dict(props_dict))
    return (dict(props_dict))

if __name__ == '__main__':
    c_main()