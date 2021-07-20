from smiteapi.smiteobjects import Match, Player, PlayerEntry
import sys

MAX_BATCH = 22


class Analyzer(object):
    def __init__(self, api, match_ids=[]):
        self.match_ids = match_ids
        self.api = api
        self.items = {}
        self.gods = {}

    def analyze(self, match):
        for player in match.entries:
            self.gods[player.god_id] = self.gods.get(player.god_id, 0) + 1
            for item in player.items:
                if item == '':
                    continue
                self.items[item] = self.items.get(item, 0) + 1
        self.match_ids.append(match.id)

    # since smite-api returns PlayerEntries(raw) instead of raw matches
    # we have to handle it separately
    def analyze_batch(self, batch):
        to_analyze = [Match()]
        index = 0
        for match in batch:
            match_id = match['Match']
            if to_analyze[index].id == 0:
                to_analyze[index].id = match_id
                to_analyze[index].entries.append(PlayerEntry(match))
            elif to_analyze[index].id != match_id:
                entry = Match()
                entry.id = match_id
                entry.entries.append(PlayerEntry(match))
                to_analyze.append(entry)
                index += 1
            else:
                to_analyze[index].entries.append(PlayerEntry(match))
        for match in to_analyze:
            self.analyze(match)
        return index + 1

    def analyze_queue(self, queue_id, date, hour=-1):
        response = self.api.make_request('getmatchidsbyqueue', [queue_id, date, hour])
        ids = list(map(lambda d: d['Match'], response))
        total = len(ids)
        count = 0
        while ids != []:
            id_str = ','.join(ids[:MAX_BATCH])
            batch = self.api.make_request('getmatchdetailsbatch', [id_str])
            ids = ids[MAX_BATCH:]
            count += self.analyze_batch(batch)
            print('\rAnalyzed {}/{} games.'.format(count, total), end='', flush=True)
        print('\nQueue {} with {} games analyzed.'.format(queue_id, count))
