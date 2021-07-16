from json import load as json_load


def read_config():
    with open('../db/dbconfig.json', 'r') as dbconfig:
        config = json_load(dbconfig)
        server_name = config['database']['server_name']
        dbname = config['database']['dbname']
        login = config['database']['login']
        passwd = config['database']['password']
    return server_name, dbname, login, passwd
