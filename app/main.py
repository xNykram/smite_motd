from smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT
from  analyzer import Analyzer
from smiteapi.smiteapiscripts import read_auth_config


def sort_and_map(d1, d2):
    mapped = {d2.get(k, ''): v for k, v in d1.items()}
    return {k: v for k, v in sorted(mapped.items(), key=lambda d: d[1])}


keys = read_auth_config()

smite = Smite(keys[0], keys[1])


print(smite.save_motd())