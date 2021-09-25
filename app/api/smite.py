from datetime import datetime, timedelta
import hashlib
import json
from db.database import db
from urllib.request import urlopen
import urllib
from api.smiteobjects import Player
from utils.config import read_auth_config, write_latest_sessions
from utils.tools import map_with_threads


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

sessions = []


def ensure_dicts():
    """ Ensures that GODS_DICT and ITEMS_DICT are not empty """
    if ITEMS_DICT != {} and GODS_DICT != {}:
        return
    validate_sessions(sessions)
    ensure_sessions(sessions, 1)
    api = sessions[0]
    api.update_gods()
    api.update_items()


def validate_sessions(sessions: list) -> int:
    """ Removes not vaild sessions from sessions array 

        Args:
            sessions (list): List of Smite objects to check

        Returns:
            Length of filtered list
    """
    def validate(smite_obj):
        if not smite_obj.test_session():
            sessions.remove(smite_obj)
    map_with_threads(fun=validate, container=sessions)
    return len(sessions)


def ensure_sessions(sessions, n, save=True):
    """ Makes sure that sessions array contains n Smite objects 
        
        Args:
            sessions (list): List of Smite objects to check
            n (int): Number of sessions to ensure
            save (bool): A flag for saving ensured sessions to latest_sessions.txt
                        (Default: True)

        Returns:
            Length of ensured sessions list
    """
    def ensure(dummy):
        instance = Smite()
        if instance.test_session():
            sessions.append(instance)
    map_with_threads(fun=ensure, container=list(range(0, n - len(sessions))))
    if save:
        write_latest_sessions(sessions)
    return len(sessions)


class Smite(object):
    """ A class responsible for api calls """ 
    def __init__(self, session=None):
        self.dev_id = AUTH[0]
        self.auth_key = AUTH[1]
        self.BASE_URL = 'https://api.smitegame.com/smiteapi.svc'
        self.session = session
        self.motds = None
        if self.session is None:
            self.open_session()
            self.update_items()
            self.update_gods()

    def test_session(self) -> bool:
        """ Test if session is OK 

            Returns:
                True if sessions is OK
                False otherwise 
        """
        response = self.make_request('testsession')
        # first character of API success response is 'T'
        return response is not None and response[0] == 'T'

    def create_timestamp(self) -> str:
        """ Creates timestamp needed for api calls 
            
            Returns:
                String representing today's date 
        """
        now = datetime.utcnow()
        return now.strftime('%Y%m%d%H%M%S')

    def update_items(self, items_dict=ITEMS_DICT):
        """ Calls api and updates items_dict with items from response 

            Args:
                items_dict (dict): A dictionary to update (Default: ITEMS_DICT)
        """
        items = self.make_request('getitems', [1])
        for i in items:
            items_dict[i['ItemId']] = i['DeviceName']

    def update_gods(self, gods_dict=GODS_DICT):
        """ Calls api and updates items_dict with items from response 

            Args:
                gods_dict (dict): A dictionary to update (Default: GODS_DICT)
        """
        gods = self.make_request('getgods', [1])
        for god in gods:
            gods_dict[god['id']] = (god['Name'], god['godIcon_URL'])

    def create_signature(self, name: str) -> str:
        """ Creates hashed signature needed for api calls
            
            Args:
                name (str): Name to encode
            
            Returns:
                Encoded(utf-8) and hashed(md5) signature as string

        """
        return hashlib.md5(self.dev_id.encode('utf-8')
                           + name.encode('utf-8')
                           + self.auth_key.encode('utf-8')
                           + self.create_timestamp().encode('utf-8')).hexdigest()

    def open_session(self, log=False):
        """ Attempts to open a new session 
        
            Args:
                log (bool): A flag for printing debug informations
                            (Default: False)
        """
        signature = self.create_signature('createsession')
        url = '{0}/createsessionJson/{1}/{2}/{3}'.format(self.BASE_URL,
                                                         self.dev_id,
                                                         signature,
                                                         self.create_timestamp())
        try:
            html = urlopen(url).read()
            self.session = json.loads(html.decode('utf-8'))['session_id']
            if log:
                print(html)
        except urllib.error.HTTPError as e:
            if log:
                print("Error: {0}".format(ERROR_CODE_DICT.get(e.code, e.code)))

    def create_request(self, name: str, params=None) -> str:
        """ Creates request string 

            Args:
                name (str): A request name
                params (list): List of request parameters
            Returns:
                Url(str) based on given name and params
        """
        signature = self.create_signature(name)
        time = self.create_timestamp()
        path = [name + 'Json', self.dev_id, signature, self.session, time]
        if params:
            path += [str(s) for s in params]
        return self.BASE_URL + '/' + '/'.join(path)

    def make_request(self, name: str, params=None) -> list:
        """ Creates and sends request 

            Args:
                name (str): A request name
                params (list): List of request parameters
            Returns:
                Response from api as list
        """
        url = self.create_request(name, params)
        url = url.replace(' ', '%20')  # Cater for spaces in parameters
        html = urlopen(url).read()
        return json.loads(html.decode('utf-8'))

    def request_left(self) -> int:
        """ Returns number of requests which can be made today """
        try:
            response = self.make_request('getdataused')
            total = response[0]['Total_Requests_Today']
            limit = response[0]['Request_Limit_Daily']
            return limit - total
        except Exception:
            return 0

    def server_status(self) -> str:
        """ Calls api for server status

            Returns:
                Smite server status (string)
        """
        return self.make_request('gethirezserverstatus', True)[0]

    def get_player(self, name: str) -> Player:
        """ Calls api for particular player

            Args:
                name (str): Name of player to call
            Returns:
                Player object if player was found
                None otherwise
        """
        response = self.make_request('getplayer', [name])
        if response == []:
            return None
        return Player(response[0])

    def get_player_id(self, name):
        """ Calls api for particular player

            Args:
                name (str): Name of player to call
            Returns:
                Player unique id if player was found
                0 otherwise
        """
        response = self.make_request('getplayeridbyname', [name])
        if response == []:
            return 0
        return response[0]['player_id']

    def get_match_ids(self, queue: int, date: str, hour=-1, limit=-1) -> list:
        """ Calls for match id in given time 

            Args:
                queue (int): Queue id of matches to look for
                date (str): Date formated as YYYYMMDD to look for
                hour (int): Number between 0-23 to look for
                            or -1 in case of whole day
                            (Default: -1)
                limit (int): A maximum number of matches to return
                            or -1 in case of no limit
                            (Default: -1)
            Returns:
                List of match ids in given date, hour, limitted by limit param
        """
        count = 0
        response = self.make_request('getmatchidsbyqueue', [queue, date, hour])
        result = []
        for entry in response:
            if limit >= 0 and count >= limit:
                break
            result.append(entry['Match'])
            count += 1
        return result

    def get_match_ids_motd(self, date: str) -> list:
        """ Calls api for motd match ids

            Args:
                date (str): Date formated as YYYYMMDD to look for
            Returns:
                List of all MOTD match ids at given date
        """
        today = datetime.strptime(date, '%Y%m%d')
        tomorrow = today + timedelta(days=1)
        today_apistr = today.strftime('%Y%m%d')
        tomorrow_apistr = tomorrow.strftime('%Y%m%d')

        result = []
        for hour in range(9, 24):
            result.extend(self.get_match_ids(434, today_apistr, hour))
        for hour in range(1, 9):
            result.extend(self.get_match_ids(434, tomorrow_apistr, hour))

        return result

    def get_latest_motd(self, days_delta=0) -> str:
        """ Calls api for latest motd name 

            Args:
                days_delta (int): A param for retriving latest motd
                                 (0 = today, 1 = yeasterday etc...)
                                 It should be small due to api limitations (max 23)
                                 (Default: 0)
            Returns:
                Title of desired motd as string
        """
        if self.motds is None:
            self.motds = self.make_request('getmotd')
        start_date_time = self.motds[0]['startDateTime']
        date_obj = datetime.strptime(start_date_time, '%m/%d/%Y %H:%M:%S %p')
        today_obj = datetime.today()
        diff = date_obj - today_obj
        index = diff.days + 1 + days_delta
        date_api = (date_obj - timedelta(days=index)).strftime('%Y%m%d')
        if index < 0 or index >= len(self.motds):
            return ('', '')
        return (self.motds[index]['title'], date_api)

    def get_motd_names(self) -> set:
        """ Calls api for all latest motd names

            Returns:
                Set of motd titles (string)
        """
        if self.motds is None:
            self.motds = self.make_request('getmotd')
        return {motd['title'] for motd in self.motds}

    def save_motd(self):
        """ Save tommorow's motd to database """
        response = self.make_request('getmotd')
        date = self.get_current_date()
        date_future = date + timedelta(days=1)
        for row in response:
            mdate = datetime.strptime((row['startDateTime'][:-11]), '%m/%d/%Y')
            if mdate > date and mdate < date_future:
                row['description'] = row['description']
                sql_command = "INSERT INTO smite_lore_motd (name, description, date) VALUES ('{}', '{}', '{}')"\
                    .format(row['name'], row['description'], row['startDateTime'])
                db.query(sql_command)

    @staticmethod
    def get_current_date():
        """ Gets current date formated as MM/DD/YY HH:MM:SS """
        dt = datetime.now()
        dt.strftime('%m/%d/%Y %H:%M:%S')
        return dt
