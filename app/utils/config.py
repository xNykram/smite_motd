from json import load as json_load
import os


def read_db_config() -> tuple:
    """ Read database config that is stored in json 

        Returns:
            Tuple of server_name, login, password, dbname
    """
    project_dir = os.path.abspath('..')
    config_dir = os.path.join(project_dir, r"dbconfig.json")
    with open(config_dir, 'r') as dbconfig:
        config = json_load(dbconfig)
        server_name = config['database']['server_name']
        dbname = config['database']['dbname']
        login = config['database']['login']
        passwd = config['database']['password']
    return (server_name, login, passwd, dbname)


def read_auth_config():
    """ Read auth config that is stored in json

        Returns:
            Tuple of dev_id, auth_id
    """
    project_dir = os.path.abspath('..')
    config_dir = os.path.join(project_dir, r"auth.json")
    with open(config_dir, 'r') as authconfig:
        config = json_load(authconfig)
        dev_id = config['devId']
        auth_id = config['authKey']
    return dev_id, auth_id


LATEST_SESSION_FILE = '../latest_sessions.txt'


def read_latest_sessions() -> list:
    """ Read session ids from latest_sessions.txt file 

        Returns:
            List of readed session ids
    """
    if not os.path.isfile(LATEST_SESSION_FILE):
        return []
    with open('latest_sessions.txt', 'r') as file:
        result = file.readlines()
        return [session.replace('\n', '') for session in result]


def write_latest_sessions(sessions: list):
    """ Write latest session ids to latest_sessions.txt 

        Args:
            sessions (list): List of smite objects to save
    """
    with open(LATEST_SESSION_FILE, 'w') as file:
        for smite_obj in sessions:
            file.write(smite_obj.session)
            file.write('\n')
