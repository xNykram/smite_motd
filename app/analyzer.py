from smiteapi.smiteobjects import Match, Player, PlayerEntry


class Analyzer(object):
    def __init__(self, api, match_ids=[]):
        self.match_ids = match_ids
        self.api = api
        self.items = {}

    def analyze(self, match_raw):
        match = Match(match_raw) 
        for player in match.entries:
            for item in player.items:
                if item == '':
                    continue
                self.items[item] = self.items.get(item, 0) + 1
        self.match_ids.append(match.id)
        print("Match {} analyzed.".format(match.id))


    def analyze_queue(self, queue_id, date, hour=-1, limit=-1):
        count = 0
        response = self.api.make_request('getmatchidsbyqueue', [queue_id, date, hour])
        for entry in response:
            if limit >= 0 and count >= limit:
                break
            count += 1
            self.analyze(entry['Match'])
        print('Analyzed {} games from queue {} @ {} @ {}PM  analyzed.'.format(count, queue_id, date, hour))

