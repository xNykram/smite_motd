from datetime import datetime, timedelta
import hashlib
import json
from db.database import db
from urllib.request import urlopen
import urllib
from smiteapi.smiteobjects import Player
from smiteapi.smiteapiscripts import read_auth_config


# May be incorrect
ERROR_CODE_DICT = {
     503: 'Bad request',
     404: 'Bad request',
     400: 'API Auth invaild'
}

ITEMS_DICT = {}
GODS_DICT = {}
QUEUES_DICT = {
    448: 'Joust',
    434: 'MOTD',
    435: 'Arena',
    426: 'Conquest',
    445: 'Assault',
    466: 'Clash',
    451: 'Conquest(R)',
    450: 'Joust(R)',
    440: 'Joust Solo(R)',
    459: 'Siege'
}

AUTH = read_auth_config()


def validate_sessions(sessions):
    """removes not vaild sessions from sessions array"""
    for smite_obj in sessions:
        if not smite_obj.test_session():
            sessions.remove(smite_obj)

def ensure_sessions(sessions, n):
    """makes sure that sessions array contains n Smite objects"""
    while n > len(sessions):
        instance = Smite()
        if instance.test_session():
            sessions.append(Smite())
        else:
            break
    return len(sessions)


class Smite(object):
    def __init__(self, session=None):
        self.dev_id = AUTH[0]
        self.auth_key = AUTH[1]
        self.BASE_URL = 'https://api.smitegame.com/smiteapi.svc'
        self.session = session
        if self.session is None:
            self.open_session()
            self.update_items()
            self.update_gods()

    def test_session(self):
        response = self.make_request('testsession') 
        # first character of API success response is 'T'
        return response is not None and response[0] == 'T'

    def create_timestamp(self):
        """returns timestamp needed for api calls"""
        now = datetime.utcnow()
        return now.strftime('%Y%m%d%H%M%S')

    def update_items(self, arr=ITEMS_DICT):
        """calls api and updates arr with items from response"""
        items = self.make_request('getitems', [1])
        for i in items:
            arr[i['ItemId']] = i['DeviceName']

    def update_gods(self, arr=GODS_DICT):
        """calls api and updates arr with gods info from response"""
        gods = self.make_request('getgods', [1])
        for god in gods:
            arr[god['id']] = god['Name']

    def create_signature(self, name):
        """returns hashed signature needed for api calls"""
        return hashlib.md5(self.dev_id.encode('utf-8')
                               + name.encode('utf-8')
                               + self.auth_key.encode('utf-8')
                               + self.create_timestamp().encode('utf-8')).hexdigest()

    def open_session(self, log=False):
        """attempts to open a new session"""
        signature = self.create_signature('createsession')
        url = '{0}/createsessionJson/{1}/{2}/{3}'.format(self.BASE_URL,
                                                         self.dev_id,
                                                         signature,
                                                         self.create_timestamp())
        try:
            html = urlopen(url).read()
            self.session = json.loads(html.decode('utf-8'))['session_id']
            if log:
                print("New session connected. Session id: {0}".format(self.session))
        except urllib.error.HTTPError as e:
            if log:
                print("Error: {0}".format(ERROR_CODE_DICT.get(e.code, e.code)))

    def create_request(self, name, params=None):
        """return request string based on name and params"""
        signature = self.create_signature(name)
        time = self.create_timestamp()
        path = [name + 'Json', self.dev_id, signature, self.session, time]
        if params:
            path += [str(s) for s in params]
        return self.BASE_URL + '/' + '/'.join(path)

    def make_request(self, name, params=None):
        """calls api with given request"""
        url = self.create_request(name, params)
        url = url.replace(' ', '%20')  # Cater for spaces in parameters
        try:
            html = urlopen(url).read()
            return json.loads(html.decode('utf-8'))
        except urllib.error.HTTPError as e:
            print("Couldn't make request [{0}]."
                  .format(ERROR_CODE_DICT.get(e.code, e.code)))
            return []

    def server_status(self, to_json=True):
        """calls for server status"""
        return self.make_request('gethirezserverstatus', to_json)[0]

    def get_player(self, name):
        """returns player object with given name"""
        response = self.make_request('getplayer', [name])
        if response == []:
            return None
        return Player(response[0])

    def get_player_id(self, name):
        """returns player id"""
        response = self.make_request('getplayeridbyname', [name])
        if response == []:
            return 0
        return response[0]['player_id']

    def get_match_ids(self, queue, date, hour=-1, limit=-1):
        """returns match id array limited by limit param"""
        count = 0
        response = self.make_request('getmatchidsbyqueue', [queue, date, hour])
        result = []
        for entry in response:
            if limit >= 0 and count >= limit:
                break
            result.append(entry['Match'])
            count += 1
        return result

    def save_motd(self):
        """takes tomorrow's motd and saves it in the database"""
        response = self.make_request('getmotd')
        date = self.get_current_date()
        date_future = date + timedelta(days=1)
        for row in response:
            mdate = datetime.strptime((row['startDateTime'][:-11]), '%m/%d/%Y')
            if mdate > date and mdate < date_future:
                row['description'] = row['description'].replace("<li>", " ")\
                    .replace("</li>", " ")
                try:
                    sql_command = "INSERT INTO smite_lore_motd (name, description, date) VALUES ('{}', '{}', '{}')"\
                        .format(row['name'], row['description'], row['startDateTime'])
                    db.query(sql_command)
                except Exception as e:
                    return 'Unable to update motd: ' + str(e)

    @staticmethod
    def get_current_date():
        """returns current date with format that smite api uses"""
        dt = datetime.now()
        dt.strftime('%m/%d/%Y %H:%M:%S')
        return dt
