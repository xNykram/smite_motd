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
        #driver = 'SQL+Server'
        #config_url = "mssql+pyodbc://" + login + ':' + passwd + "@" \
        #             + server_name + "/" + dbname + "?driver=" + driver
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
