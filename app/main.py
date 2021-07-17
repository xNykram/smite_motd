from smiteapi.smite import Smite

import json

file = open('../auth.json')
jsfile = json.load(file)
DEV_ID = jsfile['devId']
AUTH_KEY = jsfile['authKey']
file.close()

smite = Smite(DEV_ID, AUTH_KEY)
smite.open_session()

test = smite.get_player('xNykram')
