from smiteapi.smiteobjects import Match, PlayerEntry
from db.database import db
from ast import literal_eval
from functools import reduce
from smiteapi.smite import Smite, QUEUES_DICT
from threading import Thread
import curses
from time import sleep

# max number of returned games from single api call, limited by hi-rez
MAX_BATCH = 22

def date_api_to_sql(date):
    """reformat dates as YYYYMMDD -> YYYY-MM-DD"""
    if len(date) < 8:
        return ''
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]

def str_to_dict(dict_str):
    """makes dictionary from string"""
    return literal_eval(dict_str)

def accumulate_dict(first, second):
    result = first.copy()
    for k in second:
        result[k] = first.get(k, 0) + second.get(k, 0)
    return result

class ResultSet(object):
    """container for raw analyze results"""
    def __init__(self, is_completed=True):
        self.is_completed = is_completed # true if result comes from a analyze performed on whole day 
        self.analyzed_count = 0 # count of analzyed games
        self.gods = {} # dict of (god_id, count)
        self.items = {} # dict of (item_id, count)

    def accumulate(self, other):
        """TODO: sum up two result sets"""
        instance = ResultSet()
        instance.is_completed = self.is_completed and other.is_completed 
        instance.gods = accumulate_dict(self.gods, other.gods)
        instance.items = accumulate_dict(self.items, other.items)
        return instance

    def serialize(self):
        """return series of string and ints which representates this object"""
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
        """inserts result set into database along with queue_id and date"""
        query = """INSERT INTO analyzer (queue_id, date, is_completed, gods, items, analyzed_count) VALUES ({}, '{}', {}, '{}', '{}', {})"""
        data = self.serialize()
        date = date_api_to_sql(api_date)
        query = query.format(queue_id, date, data[0], data[1], data[2], self.analyzed_count)

        return db.query(query, log=True)

class Analyzer(object):
    """analyzes smite data"""
    def __init__(self, match_ids=[]):
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

    def analyze_queue(self, api, queue_id, date, hour=-1, log=-1, screen=None):
        """calls for all games from the given queue and analyzes them"""
        response = api.make_request('getmatchidsbyqueue', [queue_id, date, hour])
        ids = list(map(lambda d: d['Match'], response))
        result_set = ResultSet(hour == -1)
        total = len(ids)
        count = 0
        queue_name = QUEUES_DICT.get(queue_id, 'UNKNOWN')
        while ids != []:
            if log >= 0 and screen is not None:
                buffer = 'Analyzed {}/{} ({}%) {} games.'
                buffer = buffer.format(count, total, int((count/total)*100), queue_name)
                screen.addstr(log, 0, buffer)
                screen.refresh()
            id_str = ','.join(ids[:MAX_BATCH])
            batch = api.make_request('getmatchdetailsbatch', [id_str])
            ids = ids[MAX_BATCH:]
            count += self.analyze_batch(batch, result_set)
        if log >= 0 and screen is not None:
            buffer = 'Completed {} analysis with {} games!'.format(queue_name, count)
            screen.addstr(log, 0, buffer)
            screen.refresh()
        result_set.analyzed_count = count
        self.results[(queue_id, date)] = result_set

    def load_to_db(self):
        """loads analyzer results to database"""
        for item in self.results.items():
            (queue_id, date) = item[0]
            item[1].load_to_db(queue_id, date)

    def accumulated_result(self):
        rs = list(self.results.values())
        return reduce(ResultSet.accumulate, rs)

    @staticmethod
    def from_db(api=None):
        """builds analyzer object basing on data from database"""
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
