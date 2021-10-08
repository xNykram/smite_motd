from api.smite import GODS_DICT, ITEMS_DICT, ensure_dicts
from functools import reduce
from analyzer import ResultSet, Analyzer

MIN_AMOUNT_REQUAIRED = 10
MIN_WINRATE = 0.51

# TODO. Not done yet, create table for this and push into it


def update_pref_items(n=5, analyzer=None):
    ensure_dicts()
    if analyzer is None:
        analyzer = Analyzer.from_db()
    results = list(analyzer.results.items())
    filtered_results = [s[1] for s in results if s[0][0] != 434]
    rs = reduce(ResultSet.accumulate, filtered_results)
    pref_items_dict = {
        GODS_DICT[god_id][0]: rs.items_odds[god_id] for god_id in rs.items_odds}
    for god, items_dict in list(pref_items_dict.items()):
        pref_items_dict[god] = {ITEMS_DICT.get(
            item_id, ''): items_dict[item_id] for item_id in items_dict if item_id != 0}

    def item_filter(d):
        wins = d[1][0]
        loses = d[1][1]
        total = wins + loses
        winrate = wins / total
        return total >= MIN_AMOUNT_REQUAIRED and winrate >= MIN_WINRATE

    def item_sorter(d):
        wins = d[1][0]
        loses = d[1][1]
        total = wins + loses
        return wins / total
    result = {}
    for god in pref_items_dict:
        buffer = list(filter(item_filter, pref_items_dict[god].items()))
        buffer = sorted(buffer, key=item_sorter, reverse=True)
        result[god] = [
            (d[0], d[1], round(d[1][0] / (d[1][0] + d[1][1]) * 100, 2)) for d in buffer]
    return result
