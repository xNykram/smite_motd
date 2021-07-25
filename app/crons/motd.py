from app.main import smite


def run_save_motd():
    try:
        smite.save_motd()
    except Exception as Error:
        return str(Error)


run_save_motd()
