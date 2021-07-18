from smiteapi.smite import Smite
from smiteapi.smiteobjects import Match
from analyzer import Analyzer

import json

file = open('../auth.json')
jsfile = json.load(file)
DEV_ID = jsfile['devId']
AUTH_KEY = jsfile['authKey']
file.close()

smite = Smite(DEV_ID, AUTH_KEY)

test = smite.get_player('LyQsPL')

analyzer = Analyzer(smite)

queue = test.latest_queue(smite)
date = '20210717'

analyzer.analyze_queue(queue, date, 6)
