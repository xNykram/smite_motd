from analyzer import Analyzer, ResultSet
from functools import reduce
from api.smite import GODS_DICT, ITEMS_DICT, QUEUES_DICT, ensure_dicts
from utils.config import read_tiers_file
from db.database import db
import json

TIERS_DICT = {}


def get_tier(ratio: float) -> str:
    """ Get's tier of given ratio """
    global TIERS_DICT
    if TIERS_DICT == {}:
        TIERS_DICT = read_tiers_file()
    max_tier = ''
    max_value = -1
    for tier, value in TIERS_DICT.items():
        if value > max_value and ratio >= value:
            max_value = value
            max_tier = tier

    return max_tier


def update_tier_list(queue_id, analyzer=None):
    """ Updates and pushes tierlist to database

        Args:
            queue_id (int): Id of queue to create tierlist
            analyzer (Analyzer): Analyzer object to use
    """
    
    if analyzer is None:
        analyzer = Analyzer.from_db()
    ensure_dicts()
    mode = QUEUES_DICT.get(queue_id, 'UNKNOWN')
    results = [entry[1]
               for entry in analyzer.results.items() if entry[0][0] == queue_id]
    rs = reduce(ResultSet.accumulate, results, ResultSet())
    if rs is None:
        return

    wins = {GODS_DICT.get(god_id, ("", ""))[
        0]: rs.wins[god_id] for god_id in rs.wins}
    loses = {GODS_DICT.get(god_id, ("", ""))[
        0]: rs.loses[god_id] for god_id in rs.loses}

    db.query(f"DELETE FROM tierlist WHERE mode = '{mode}'")
    top = []
    for god in wins | loses:
        w = wins.get(god, 0)
        l = loses.get(god, 0)
        total = w + l
        ratio = 100 * w / total
        tier = get_tier(ratio)
        god = god.replace("'", "''")  # fix special chars
        top.append((god, w, l, ratio, tier))
        query = "INSERT INTO tierlist VALUES ('{}', '{}', '{}', {}, GETDATE())"
        query = query.format(god, mode, tier, ratio)
        db.query(query)

    return top
