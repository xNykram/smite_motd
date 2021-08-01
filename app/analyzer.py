from smiteapi.smiteobjects import Match, PlayerEntry
from db.database import db
from ast import literal_eval

# max number of returned games from single api call, limited by hi-rez
MAX_BATCH = 22

def date_api_to_sql(date):
    if len(date) < 8:
        return ''
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]

def str_to_dict(dict_str):
    return literal_eval(dict_str)

class ResultSet(object):
    def __init__(self, is_completed=True):
        self.is_completed = is_completed 
        self.analyzed_count = 0
        self.gods = {}
        self.items = {}

    def accumulate(self, other):
        """sum up two result sets"""
        pass

    def serialize(self):
        gods_str = 'NULL'
        items_str = 'NULL'
        completed = 0
        if self.gods != {}:
            gods_str = self.gods.__str__()
        if self.items != {}:
            items_str = self.items.__str__()
        if self.is_completed:
            completed = 1


        return (completed, gods_str, items_str)
    
    def load_to_db(self, queue_id, api_date):
        query = """INSERT INTO analyzer (queue_id, date, is_completed, gods, items, analyzed_count) VALUES ({}, '{}', {}, '{}', '{}', {})"""
        data = self.serialize()
        date = date_api_to_sql(api_date)
        query = query.format(queue_id, date, data[0], data[1], data[2], self.analyzed_count)
        return db.query(query, log=True)

class Analyzer(object):
    """analyzes smite data"""
    def __init__(self, api, match_ids=[]):
        self.api = api
        self.results = {} # dict of {(int, date), ResultSet} 

    def analyze(self, match, result_set):
        """analyzes single match object"""
        for player in match.entries:
            result_set.gods[player.god_id] = result_set.gods.get(player.god_id, 0) + 1
            for item in player.items:
                if item == ' ':
                    continue
                result_set.items[item] = result_set.items.get(item, 0) + 1
        

    # since smite-api returns PlayerEntries(raw) instead of raw matches
    # we have to handle it separately
    def analyze_batch(self, batch, result_set):
        """analyzes set of raw PlayerEntries"""
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
            self.analyze(match, result_set)
        return index + 1

    def analyze_queue(self, queue_id, date, hour=-1):
        """calls for all games from the given queue and analyzes them"""
        response = self.api.make_request('getmatchidsbyqueue', [queue_id, date, hour])
        ids = list(map(lambda d: d['Match'], response))
        result_set = ResultSet(hour == -1)
        total = len(ids)
        count = 0
        while ids != []:
            id_str = ','.join(ids[:MAX_BATCH])
            batch = self.api.make_request('getmatchdetailsbatch', [id_str])
            ids = ids[MAX_BATCH:]
            count += self.analyze_batch(batch, result_set)
            print('\rAnalyzed {}/{} games.'.format(count, total), end='', flush=True)
        print('\nQueue {} with {} games analyzed.'.format(queue_id, count))
        result_set.analyzed_count = count
        self.results[(queue_id, date)] = result_set 

    def load_to_db(self):
        for item in self.results.items():
            (queue_id, date) = item[0]
            return item[1].load_to_db(queue_id, date)

    
    @staticmethod
    def from_db(api=None):
        """TODO gets analyzed data from a database and creates a new Analyzer object based on it"""
        query = 'SELECT queue_id, CONVERT(varchar, date, 112), is_completed, gods, items FROM analyzer'
        instance = Analyzer(api)
        if not db.query(query, log=True):
            return None
        
        response = db.cursor.fetchall()

        for item in response:
            queue_id = item[0]
            date = item[1]
            is_completed = item[2]
            gods = str_to_dict(item[3])
            items = str_to_dict(item[4])

            rs = ResultSet(is_completed)
            rs.gods = gods
            rs.items = items

            instance.results[(queue_id, date)] = rs

        return instance
