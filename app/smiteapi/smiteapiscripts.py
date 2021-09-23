from json import load as json_load
import os
from pathlib import Path


def read_db_config():
    """read database config that is stored in json"""
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
    """read auth config that is stored in json"""
    project_dir = os.path.abspath('..')
    config_dir = os.path.join(project_dir, r"auth.json")
    with open(config_dir, 'r') as authconfig:
        config = json_load(authconfig)
        dev_id = config['devId']
        auth_id = config['authKey']
    return dev_id, auth_id


LATEST_SESSION_FILE = 'latest_sessions.txt'


def read_latest_sessions():
    if not os.path.isfile(LATEST_SESSION_FILE):
        return []
    with open('latest_sessions.txt', 'r') as file:
        result = file.readlines()
        return [session.replace('\n', '') for session in result]


def write_latest_sessions(sessions):
    with open(LATEST_SESSION_FILE, 'w') as file:
        for smite_obj in sessions:
            file.write(smite_obj.session)
            file.write('\n')
