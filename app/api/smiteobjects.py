class Player(object):
    def __init__(self, data):
        self.name = data['Name']
        self.id = data['Id']
        self.team_id = data['TeamId']

    def latest_match_id(self, api):
        response = api.make_request('getmatchhistory', [self.id])
        if response == []:
            return None
        else:
            return response[0].get('Match', 0)

    def latest_match(self, api):
        """returns latest match as Match object"""
        return Match(match_id=self.latest_match_id(api), api=api)

    def latest_queue(self, api):
        """returns latest queue id"""
        response = api.make_request('getmatchhistory', [self.id])
        if response == []:
            return None
        else:
            return response[0].get('Match_Queue_Id', 0)

    def raw_api_data(self, api):
        """calls for data and return raw json"""
        return api.make_request('getplayer', [self.name])


class PlayerEntry(object):
    def __init__(self, data):
        self.name = data['playerName']
        self.id = data['playerId']
        self.god_id = data['GodId']
        self.win_status = data['Win_Status']
        self.items = []
        self.actives = []
        for i in range(1, 3):
            item = data.get('ActiveId{}'.format(i), '')
            if item != '':
                self.actives.append(item)
        for i in range(1, 7):
            item = data.get('ItemId{}'.format(i), '')
            if item != '':
                self.items.append(item)


class Match(object):
    def __init__(self, entry=[], match_id='', api=None):
        self.id = 0
        self.queue_id = 0
        self.entries = []
        data = entry
        if match_id != '' and api is not None:
            data = api.make_request('getmatchdetails', [match_id])
        elif entry == []:
            return
        self.queue_id = data[0]['match_queue_id']
        self.id = data[0]['Match']
        for i in data:
            if i['playerName'] != '':
                self.entries.append(PlayerEntry(i))

    def raw_api_data(self, api):
        """calls for data and return raw json"""
        return api.make_request('getmatchdetails', [self.id])
