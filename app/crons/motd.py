from app.smiteapi.smite import Smite
from app.smiteapi.smiteapiscripts import read_auth_config


def run_save_motd():
    try:
        keys = read_auth_config()
        smite = Smite(keys[0], keys[1])
        smite.save_motd()
    except Exception as Error:
        return str(Error)


run_save_motd()
