from app.smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT
from app.smiteapi.smiteobjects import Match
from app.analyzer import Analyzer

import json

file = open('../auth.json')
jsfile = json.load(file)
DEV_ID = jsfile['devId']
AUTH_KEY = jsfile['authKey']
file.close()

def sort_and_map(d1, d2):
    mapped = {d2.get(k, ''): v for k, v in d1.items()}
    return {k: v for k, v in sorted(mapped.items(), key=lambda d: d[1])}


smite = Smite(DEV_ID, AUTH_KEY)

test = smite.get_player('LyQsPL')

analyzer = Analyzer(smite)

queue = test.latest_queue(smite)
date = smite.create_timestamp()[:8]

analyzer.analyze_queue(queue, date, 3)

gods_top = sort_and_map(analyzer.gods, GODS_DICT)
items_top = sort_and_map(analyzer.items, ITEMS_DICT)

