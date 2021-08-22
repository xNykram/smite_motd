from smiteapi.smiteobjects import Match, PlayerEntry
from db.database import db
from ast import literal_eval
from functools import reduce
from smiteapi.smite import Smite, QUEUES_DICT, ensure_sessions
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
        self.odds = {} # dict of (god_id, dict of (god, odds))
        self.wins = {} # dict of (god_id, int)
        self.loses = {} # dict of (god_id, int)
        self.name = 'NULL' # optional name of motd

    def accumulate(self, other):
        """TODO: sum up two result sets"""
        instance = ResultSet()
        instance.is_completed = self.is_completed and other.is_completed 
        instance.gods = accumulate_dict(self.gods, other.gods)
        instance.items = accumulate_dict(self.items, other.items)
        #instance.odds = {god_id: odds.copy() for god_id, odds in self.odds.items()}
        #for god_id, odds in other.odds.items():
        #    instance.odds = accumulate_dict(instance.odds[god_id], odds)
        instance.wins = accumulate_dict(self.wins, other.wins)
        instance.loses = accumulate_dict(self.loses, other.loses)
        return instance

    def serialize(self):
        """return series of string and ints which representates this object"""
        gods_str = 'NULL'
        items_str = 'NULL'
        odds_str = 'NULL'
        wins_str = 'NULL'
        loses_str = 'NULL'
        completed = 0
        if self.gods != {}:
            gods_str = self.gods.__str__()
        if self.items != {}:
            items_str = self.items.__str__()
        if self.odds != {}:
            odds_str = self.odds.__str__()
        if self.wins != {}:
            wins_str = self.wins.__str__()
        if self.loses != {}:
            loses_str = self.loses.__str__()
        if self.is_completed:
            completed = 1

        return (completed, gods_str, items_str, odds_str, wins_str, loses_str)

    def load_to_db(self, queue_id, api_date, log=False):
        """inserts result set into database along with queue_id and date"""
        query = """INSERT INTO analyzer (name, queue_id, date, is_completed, gods, items, odds, wins, loses, analyzed_count) VALUES ('{}', {}, '{}', {}, '{}', '{}', '{}', '{}', '{}', {})"""
        data = self.serialize()
        date = date_api_to_sql(api_date)
        query = query.format(self.name, queue_id, date, data[0], data[1], data[2], data[3], data[4], data[5], self.analyzed_count)

        return db.query(query, log)

class Analyzer(object):
    """analyzes smite data"""
    def __init__(self, match_ids=[]):
        self.results = {} # dict of {(int, date), ResultSet}
        self.match_list = []
        self.analyzed_count = 0

    def analyze(self, match, result_set):
        """analyzes single match object"""
        winners = [player for player in match.entries if player.win_status == 'Winner']
        losers  = [player for player in match.entries if player.win_status == 'Loser']
        for player in match.entries:
            result_set.gods[player.god_id] = result_set.gods.get(player.god_id, 0) + 1
            for item in player.items:
                if item == ' ':
                    continue
                result_set.items[item] = result_set.items.get(item, 0) + 1
        odds = result_set.odds
        wins = result_set.wins
        loses = result_set.loses
        for winner in winners:
            winner_god = winner.god_id
            winner_odds = odds.get(winner_god, {})
            wins[winner_god] = wins.get(winner_god, 0) + 1
            for loser in losers:
                loser_god = loser.god_id
                loser_odds = odds.get(loser_god, {})
                winner_odds[loser_god] = winner_odds.get(loser_god, 0) + 1
                loser_odds[winner_god] = loser_odds.get(winner_god, 0) - 1
                odds[loser_god] = loser_odds
            odds[winner_god] = winner_odds
        for loser in losers:
            loses[loser.god_id] = loses.get(loser.god_id, 0) + 1
        result_set.analyzed_count += 1


    def analyze_match_list(self, match_list, session_count=10, sessions=None, result_set=None, screen=None, log_index=0):
        if result_set is None:
            result_set = ResultSet()
        if sessions is None:
            sessions = []
        total = len(match_list)
        ensure_sessions(sessions, session_count)   
        analyzed_count = 0
        def pop_matches(api, count=MAX_BATCH):
            nonlocal match_list
            nonlocal analyzed_count
            while match_list != []:
                poped = match_list[:count]
                id_str = ','.join(poped)
                match_list = match_list[count:]
                batch = api.make_request('getmatchdetailsbatch', [id_str])
                self.analyze_batch(batch, result_set) 
                analyzed_count += len(poped)
        for i in range(session_count):
            Thread(target=pop_matches, args=[sessions[i]]).start()
        while match_list != []:
            if screen is not None:
                screen.addstr(log_index, 0, f'Analyzed {analyzed_count} out of {total} games.')
                screen.refresh()
            sleep(0.25)
        return result_set

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
    def from_db(api=None, log=False):
        """builds analyzer object basing on data from database"""
        query = 'SELECT queue_id, CONVERT(varchar, date, 112), is_completed, gods, items, odds, wins, loses, name, analyzed_count  FROM analyzer'
        instance = Analyzer(api)
        if not db.query(query, log):
            return None

        response = db.cursor.fetchall()

        for item in response:
            queue_id = item[0]
            date = item[1]
            is_completed = item[2]
            gods = str_to_dict(item[3])
            items = str_to_dict(item[4])
            odds = str_to_dict(item[5])
            wins = str_to_dict(item[6])
            loses = str_to_dict(item[7])
            name = item[8]
            analyzed_count = item[9]

            rs = ResultSet(is_completed)
            rs.gods = gods
            rs.items = items
            rs.odds = odds
            rs.wins = wins
            rs.loses = loses
            rs.name = name
            rs.analyzed_count = analyzed_count

            instance.results[(queue_id, date)] = rs

        return instance
