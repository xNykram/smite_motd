from smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT
from analyzer import Analyzer


def sort_and_map(d1, d2):
    mapped = {d2.get(k, ''): v for k, v in d1.items()}
    return {k: v for k, v in sorted(mapped.items(), key=lambda d: d[1])}


smite = Smite()

test = smite.get_player('LyQsPL')

analyzer = Analyzer(smite)

queue = test.latest_queue(smite)
date = smite.create_timestamp()[:8]

analyzer.analyze_queue(queue, date, -1)

analyzer.load_to_db()

#gods_top = sort_and_map(analyzer.gods, GODS_DICT)
#items_top = sort_and_map(analyzer.items, ITEMS_DICT)
