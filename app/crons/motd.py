from smiteapi.smite import Smite, GODS_DICT, ensure_dicts
from smiteapi.smiteapiscripts import read_auth_config
from db.database import db
from functools import reduce
from analyzer import ResultSet, Analyzer

MINIMUM_GAMES_REQUIRED = 60 

def run_save_motd():
    try:
        keys = read_auth_config()
        smite = Smite()
        smite.save_motd()
    except Exception as Error:
        return str(Error)


def load_motd_names(arr):
    if db.query('SELECT name FROM motds'):
        MOTD_NAMES = db.cursor.fetchall()

GOD_ID_DB_NAME = 'smite_lore_prefgodsformotd'

def update_motd_god_ids(motd_name, n=5, analyzer=None):
    """pushes top n gods for motd_name into database"""
    ensure_dicts()
    if analyzer is None:
        analyzer = Analyzer.from_db()
    results = list(analyzer.results.values())
    filtered_results = [result_set for result_set in results if result_set.name == motd_name]
    final_result = reduce(ResultSet.accumulate, filtered_results)
    wins = final_result.wins
    loses = final_result.loses
    result = []
    for god_id in wins:
        win_count = wins.get(god_id, 0)
        lose_count = loses.get(god_id, 0)
        god_name, icon_url = GODS_DICT.get(god_id, ('', ''))
        god_name = god_name.replace("'", "''") # fix special chars
        total = win_count + lose_count
        ratio = round(win_count / total, 4) * 100
        if total >= MINIMUM_GAMES_REQUIRED:
            result.append((god_id, icon_url, god_name, ratio, total, win_count, lose_count))

    top = sorted(result, key=lambda d: d[3], reverse=True)
    # delete old data
    db.query(f"DELETE FROM {GOD_ID_DB_NAME} WHERE motdName = '{motd_name}'")
    
    columns = '(godID, godImageUrl, godName, motdName, ratio, total, wins, loses)'
    for i in range(0, min(n, len(top))):
        data = top[i]
        values = f'''({data[0]}, '{data[1]}', '{data[2]}', '{motd_name}', {data[3]}, {data[4]}, {data[5]}, {data[6]})'''
        query = f'INSERT INTO {GOD_ID_DB_NAME} {columns} VALUES {values}'
        db.query(query)

    return top


if __name__ == '__main__':
    run_save_motd()