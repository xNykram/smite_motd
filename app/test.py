import sys, getopt
from app.smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT, QUEUES_DICT, validate_sessions, ensure_sessions
from threading import Thread
import curses
from analyzer import Analyzer, ResultSet
from app.smiteapi.smiteapiscripts import read_latest_sessions, write_latest_sessions
from time import sleep
from datetime import datetime, timedelta
from app.crons.motd import update_motd_god_ids 
from db.database import db
from functools import reduce

sessions_ids = read_latest_sessions()
sessions = [Smite(s_id) for s_id in sessions_ids]
ensure_sessions(sessions, 1)

smite = sessions[0]

me = smite.get_player('LyQsPL')

analyzer = Analyzer.from_db()
rs = analyzer.analyze_queue(smite, 434, '20210906')

db.query('SELECT items_odds FROM analyzer')
db.cursor.fetchall()

x = list(analyzer.results.items())

x = [s[1] for s in x if s[0][0] != 434]

rs = reduce(ResultSet.accumulate, x)

x = rs.items_odds

y = {GODS_DICT[god_id][0]: x[god_id] for god_id in x}

for god, items_dict in list(y.items()): 
    y[god] = {ITEMS_DICT.get(item_id, ''): items_dict[item_id] for item_id in items_dict}

test = y['Ullr']

test = list(filter(lambda d: d[1][0] + d[1][1] >= 20, test.items()))


def sorter(d):
    wins = d[1][0]
    loses = d[1][1]
    total = wins + loses
    return wins / total


test2 = sorted(test, key=sorter)
