from json import load as json_load
import sys, os


def read_db_config():
    """read database config that is stored in json"""
    project_dir = sys.path[1]
    config_dir = os.path.join(project_dir, r"app\dbconfig.json")
    with open(config_dir, 'r') as dbconfig:
        config = json_load(dbconfig)
        server_name = config['database']['server_name']
        dbname = config['database']['dbname']
        login = config['database']['login']
        passwd = config['database']['password']
        config_url = "mssql+pyodbc://" + login + ':' + passwd + "@" \
                     + server_name + "/" + dbname + "?driver=SQL+Server"
    return config_url

def read_auth_config():
    """read auth config that is stored in json"""
    project_dir = sys.path[1]
    config_dir = os.path.join(project_dir, r"auth.json")
    with open(config_dir, 'r') as authconfig:
        config = json_load(authconfig)
        dev_id = config['devId']
        auth_id = config['authKey']
    return dev_id, auth_id
