from json import load as json_load
import sys, os


def read_config():
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
