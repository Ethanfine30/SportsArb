import requests
from multiprocessing import Process, Manager
from datetime import datetime, timedelta

standard_conversion = {'Pass Yards', 'Pass Attempts', 'Pass TDs', 'Completions', 'Interceptions', 'Pass + Rush Yards',
'Rush Yards', 'Rush Attempts', 'Rush TDs', 'Rush + Rec Yards',
'Rec Yards', 'Receptions', 'Rec TDs',
'Solo Tackles', 'Tackels + Assists', 'Sacks', 'Assists',
'FG Made', 'Kicking Points',
'Points', 'Rebounds', 'Assists', '3PM', 'Blocks', 'Steals', 'Pts + Reb + Ast', 'Pts + Reb', 'Pts + Ast', 'Reb + Ast',
'Blocks + Steals',
'Shots', 'Points', 'Assists', 'Power Play Points', 'Blocks', 'Saves', 'Goals'}

def noVig(odds):
    o1, o2 = 0, 0
    for odd in odds:
        if odd < 0:
            o = -odd / (-odd + 100)
        elif odd > 0:
            o = 100 / (odd + 100)
        else:
            raise ValueError("Odd cannot be zero")
        if o1 == 0:
            o1 = o
        else:
            o2 = o
    nvPercent = o1 / (o1 + o2)
    decOdds = 1 / nvPercent
    if decOdds >= 2.0:
        american_odds = int((decOdds - 1) * 100)
    else:
        american_odds = int(-100 / (decOdds - 1))
    return american_odds

def get_gameIDs(leagues):
    links = []
    for league in leagues:
        league_json = requests.get(url = 'https://sportsbook.draftkings.com/seo/leagues/%s' %(league)).json()
        urls = [link['body'][link['body'].find('identifier":"')+13: link['body'].find('url')] \
            for link in league_json['seo']['schemas']]
        nums = [link[link.find('-') + 1:link.find('"')] for link in urls]
        for num in nums:
            links.append('https://sportsbook-us-il.draftkings.com/sites/US-IL-SB/api/v3/event/%s?format=json' %(num))
    return links

props_to_analyze = {'TD Scorers': ['TD Scorer', 'Rush TDs', 'Rec TDs'], 
    'Passing Props': ['Pass TDs', 'Pass Yds', 'Pass Completions', 'Pass Attempts', 'Pass + Rush Yds', 'Interceptions'], 
    'Receiving Props': ['Receiving Yards', 'Receptions'], 
    'Rushing Props': ['Rush Yds', 'Rush + Rec Yds', 'Rush Attempts'],
    'D/ST Props': ['Sacks', 'Solo Tackles', 'Assists', 'Tackles + Ast', 'FG Made', 'Kicking Pts'],
    'Player Points': ['Points'], 
    'Player Threes': ['Threes'], 
    'Player Combos': ['Pts + Reb + Ast', 'Pts + Reb', 'Pts + Ast', 'Ast + Reb'], 
    'Player Rebounds': ['Rebounds'], 
    'Player Assists': ['Assists'], 
    'Player Defense': ['Steals', 'Blocks', 'Steals + Blocks'],
    'Goalscorer': ['Anytime Goalscorer'], 'Shots on Goal': ['Player Shots on Goal'], 
    'Player Props': ['Points', 'Assists', 'Power Play Points', 'Blocked Shots'],
    'Goalie Props': ['Saves']}

stat_conversion = {'NFL': {'Rush TDs': 'Rush TDs', 'Rec TDs': 'Rec TDs', 'Pass TDs': 'Pass TDs', 'Pass Yds': 'Pass Yards', 
'Pass Completions': 'Completions', 'Pass Attempts': 'Pass Attempts', 'Pass + Rush Yds': 'Pass + Rush Yards', 'Interceptions':
'Interceptions', 'Receiving Yards': 'Rec Yards', 'Receptions': 'Receptions', 'Rush Yds': 'Rush Yards', 'Rush + Rec Yds':
'Rush + Rec Yards', 'Rush Attempts': 'Rush Attempts', 'Sacks': 'Sacks', 'Solo Tackles': 'Solo Tackles', 'Assists': 'Assists',
'Tackles + Ast': 'Tackles + Assists', 'FG Made': 'FG Made', 'Kicking Pts': 'Kicking Points'},
'NBA': {'Points': 'Points', 'Threes': '3PM', 'Pts + Reb + Ast': 'Pts + Reb + Ast', 'Pts + Reb': 'Pts + Reb', 'Pts + Ast': 
'Pts + Ast', 'Ast + Reb': 'Reb + Ast', 'Rebounds': 'Rebounds', 'Assists': 'Assists', 'Steals': 'Steals', 'Blocks': 'Blocks',
'Steals + Blocks': 'Blocks + Steals'},
'NHL': {'Player Shots on Goal': 'Shots', 'Points': 'Points', 'Assists': 'Assists', 'Power Play Points': 'Power Play Points',
'Blocked Shots': 'Blocks', 'Saves': 'Saves'}}

def parse(link, props_dict):
    props = {}
    game_json = requests.get(url = link).json()
    if 'eventCategories' not in game_json or 'event' not in game_json:
        return
    date = datetime.strptime(game_json['event']['startDate'].split('T')[0], '%Y-%m-%d').strftime('%Y-%m-%d')
    league_date = game_json['event']['eventGroupName']+'-'+date
    for prop in game_json['eventCategories']:
        if prop['name'] in props_to_analyze:
            for compOffer in prop['componentizedOffers']:
                if compOffer['subcategoryName'] in props_to_analyze[prop['name']]:
                    for offer in compOffer['offers'][0]:
                        if 'line' not in offer['outcomes'][0] or len(offer['outcomes']) < 2:
                            continue
                        key = offer['outcomes'][0]['participant']+'-'+stat_conversion[game_json['event']['eventGroupName']][compOffer['subcategoryName']]+'-'+league_date
                        line = offer['outcomes'][0]['line']
                        props[key] = {line: [int(offer['outcomes'][0]['oddsAmerican']), int(offer['outcomes'][1]['oddsAmerican'])]}
    props_dict.update(props)

def dk_main():
    manager = Manager()
    props_dict = manager.dict()
    jsons = get_gameIDs(['basketball/nba', 'football/nfl', 'hockey/nhl'])
    processes = []
    for link in jsons:
        p = Process(target = parse, args = (link, props_dict))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    return (dict(props_dict))

if __name__ == '__main__':
    dk_main()