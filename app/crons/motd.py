from smiteapi.smite import Smite
from smiteapi.smiteapiscripts import read_auth_config


def run_save_motd():
    try:
        keys = read_auth_config()
        smite = Smite()
        smite.save_motd()
    except Exception as Error:
        return str(Error)
run_save_motd()