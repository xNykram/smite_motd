from datetime import datetime
import hashlib
import json
from urllib.request import urlopen
import urllib

# May be incorrect
ERROR_CODE_DICT = {
     503: 'Bad request',
     404: 'Bad request',
     400: 'API Auth invaild'
}


class Smite(object):
    def __init__(self, dev_id, auth_key):
        self.dev_id = str(dev_id)
        self.auth_key = str(auth_key)
        self.BASE_URL = 'https://api.smitegame.com/smiteapi.svc'
        self.session = None

    def create_timestamp(self):
        now = datetime.utcnow()
        return now.strftime('%Y%m%d%H%M%S')

    def create_signature(self, name):
        return hashlib.md5(self.dev_id.encode('utf-8')
                               + name.encode('utf-8')
                               + self.auth_key.encode('utf-8')
                               + self.create_timestamp().encode('utf-8')).hexdigest()

    def open_session(self):
        signature = self.create_signature('createsession')
        url = '{0}/createsessionJson/{1}/{2}/{3}'.format(self.BASE_URL,
                                                         self.dev_id,
                                                         signature,
                                                         self.create_timestamp())
        try:
            html = urlopen(url).read()
            self.session = json.loads(html.decode('utf-8'))['session_id']
            print("Smite API connected. Session id: {0}".format(self.session))
        except urllib.error.HTTPError as e:
            print("Error: {0}".format(ERROR_CODE_DICT.get(e.code, e.code)))

    def create_request(self, name, params=None):
        signature = self.create_signature(name)
        time = self.create_timestamp()
        path = [name + 'Json', self.dev_id, signature, self.session, time]
        if params:
            path += [str(s) for s in params]
        return self.BASE_URL + '/' + '/'.join(path)

    def make_request(self, name, params=None):
        url = self.create_request(name, params)
        url = url.replace(' ', '%20')  # Cater for spaces in parameters
        try:
            html = urlopen(url).read()
            return json.loads(html.decode('utf-8'))
        except urllib.error.HTTPError as e:
            print("Couldn't make request [{0}]."
                  .format(ERROR_CODE_DICT.get(e.code, e.code)))

    def ping(self):
        url = '{0}/pingJson'.format(self.BASE_URL)
        try:
            html = urlopen(url).read()
            return json.loads(html.decode('utf-8'))
        except urllib.error.HTTPError as e:
            print("Error: {0}".format(ERROR_CODE_DICT.get(e.code, e.code)))

    def server_status(self):
        return self.make_request('gethirezserverstatus')[0]

    def get_player(self, name):
        return self.make_request('getplayer', [name])
    
    def get_player_id(self, name):
        response = smite.make_request('getplayeridbyname', [name])
        if response == []:
            return 0 
        return response[0]['player_id']


file = open('../auth.json')
auth = json.load(file)
file.close()

DEV_ID = auth['devId']
AUTH_KEY = auth['authKey']

smite = Smite(DEV_ID, AUTH_KEY)
smite.open_session()
