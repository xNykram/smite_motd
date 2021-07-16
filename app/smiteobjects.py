class Player(object):
    def __init__(self, data):
        self.Name = data['Name'] 
        self.Id = data['Id']
        self.TeamId = data['TeamId']

    def latest_match(self, api):
        response = api.make_request('getmatchhistory', [self.Id]) == []
        if response == []:
            return []
        else:
            return response[0]

