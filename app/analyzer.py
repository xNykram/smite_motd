from api.smiteobjects import Match, PlayerEntry
from db.database import db
from ast import literal_eval
from functools import reduce
from api.smite import ensure_sessions
from threading import Thread
from time import sleep
import sys

# max number of returned games from single api call, limited by hi-rez
MAX_BATCH = 22


def date_api_to_sql(date: str) -> str:
    """ Reformat dates as YYYYMMDD -> YYYY-MM-DD """
    if len(date) < 8:
        return ''
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]


def str_to_dict(dict_str: str) -> dict:
    """ Makes dictionary from string 

        Args:
            dict_str (str): Dictionary represented as string
             (f.e "{1: 5, 3: 6}")
    """
    if dict_str is None or dict_str == '' or dict_str == 'NULL':
        return {}
    return literal_eval(dict_str)


def accumulate_dict(first: dict, second: dict) -> dict:
    """ Merge two dictionaries """
    result = first.copy()
    for k in second:
        result[k] = first.get(k, 0) + second.get(k, 0)
    return result


class ResultSet(object):
    """container for raw analyze results"""

    def __init__(self, is_completed=True):
        # true if result comes from a analyze performed on whole day
        self.is_completed = is_completed
        self.analyzed_count = 0  # count of analzyed games
        self.gods = {}  # dict of (god_id, count)
        self.items = {}  # dict of (item_id, count)
        self.items_odds = {}  # dict of (item_id, int)
        self.odds = {}  # dict of (god_id, dict of (god, odds))
        self.wins = {}  # dict of (god_id, int)
        self.loses = {}  # dict of (god_id, int)
        self.name = 'NULL'  # optional name of motd

    def accumulate(self, other):
        """ Merge two result set into one """
        instance = ResultSet()
        instance.is_completed = self.is_completed and other.is_completed
        instance.gods = accumulate_dict(self.gods, other.gods)
        instance.items = accumulate_dict(self.items, other.items)
        instance.items_odds = self.items_odds.copy()
        for god in set(self.items_odds) | set(other.items_odds):
            instance.items_odds[god] = {}
            d1 = self.items_odds.get(god, {})
            d2 = other.items_odds.get(god, {})
            for item in set(d1) | set(d2):
                w1, l1 = d1.get(item, (0, 0))
                w2, l2 = d2.get(item, (0, 0))
                instance.items_odds[god][item] = (w1 + w2, l1 + l2)

        #instance.odds = {god_id: odds.copy() for god_id, odds in self.odds.items()}
        # for god_id, odds in other.odds.items():
        #    instance.odds = accumulate_dict(instance.odds[god_id], odds)
        instance.wins = accumulate_dict(self.wins, other.wins)
        instance.loses = accumulate_dict(self.loses, other.loses)
        return instance

    def serialize(self) -> str:
        """ Returns series of string and ints which representates this object """
        gods_str = None
        items_str = None
        items_odds_str = None
        odds_str = None
        wins_str = None
        loses_str = None
        completed = 0
        if self.gods != {}:
            gods_str = self.gods.__str__()
        if self.items != {}:
            items_str = self.items.__str__()
        if self.items_odds != {}:
            items_odds_str = self.items_odds.__str__()
        if self.odds != {}:
            odds_str = self.odds.__str__()
        if self.wins != {}:
            wins_str = self.wins.__str__()
        if self.loses != {}:
            loses_str = self.loses.__str__()
        if self.is_completed:
            completed = 1

        return (completed, gods_str, items_str, items_odds_str, odds_str, wins_str, loses_str)

    def load_to_db(self, queue_id: int, api_date: str, log=False):
        """ Inserts result set into database along with queue_id and date

            Args:
                log (bool): A flag to log results (error or success). Default: False
        """
        query = """INSERT INTO analyzer (name, queue_id, date, is_completed, gods, items, items_odds, odds, wins, loses, analyzed_count) VALUES ('{}', {}, '{}', {}, '{}', '{}', '{}', '{}', '{}', '{}', {})"""
        data = self.serialize()
        date = date_api_to_sql(api_date)
        query = query.format(self.name, queue_id, date,
                             data[0], data[1], data[2], data[3], data[4], data[5], data[6], self.analyzed_count)

        return db.query(query, log)


class Analyzer(object):
    """ A class responsible for analyzing smite data """

    def __init__(self, match_ids=[]):
        self.results = {}  # dict of {(int, date), ResultSet}
        self.match_list = []
        self.analyzed_count = 0

    def analyze(self, match: Match, result_set: ResultSet):
        """ Analyzes single match object

            Args:
                match (Match): Match to analyze
                result_set (ResultSet): Object for storing result
        """
        winners = [
            player for player in match.entries if player.win_status == 'Winner']
        losers = [
            player for player in match.entries if player.win_status == 'Loser']
        for player in match.entries:
            result_set.gods[player.god_id] = result_set.gods.get(
                player.god_id, 0) + 1
            for item in player.items:
                if item == ' ':
                    continue
                result_set.items[item] = result_set.items.get(item, 0) + 1
        odds = result_set.odds
        items_odds = result_set.items_odds
        wins = result_set.wins
        loses = result_set.loses
        winners_items = {}
        losers_items = {}
        for winner in winners:
            for item in winner.items:
                winners_items[item] = winners_items.get(item, 0) + 1
        for loser in losers:
            for item in loser.items:
                losers_items[item] = losers_items.get(item, 0) + 1
        for winner in winners:
            winner_god = winner.god_id
            winner_odds = odds.get(winner_god, {})
            winner_items_odds = items_odds.get(winner, {})
            for item, count in losers_items.items():
                w, l = winner_items_odds.get(item, (0, 0))
                winner_items_odds[item] = (w, l + count)
            items_odds[winner_god] = winner_items_odds
            wins[winner_god] = wins.get(winner_god, 0) + 1
            for loser in losers:
                loser_god = loser.god_id
                loser_odds = odds.get(loser_god, {})
                winner_odds[loser_god] = winner_odds.get(loser_god, 0) + 1
                loser_odds[winner_god] = loser_odds.get(winner_god, 0) - 1
                odds[loser_god] = loser_odds
            odds[winner_god] = winner_odds
        for loser in losers:
            loser_god = loser.god_id
            loses[loser_god] = loses.get(loser_god, 0) + 1
            wins[loser_god] = wins.get(loser_god, 0) + 1
            loser_items_odds = items_odds.get(loser_god, {})
            for item, count in winners_items.items():
                w, l = loser_items_odds.get(item, (0, 0))
                loser_items_odds[item] = (w + count, l)
            items_odds[loser_god] = loser_items_odds
        result_set.analyzed_count += 1

    def analyze_match_list(self, match_list: list, session_count=10, sessions=None, result_set=None) -> ResultSet:
        """ Runs analyzer for every match from match_list 

            Args:
                match_list (list): List of match to analyze
                session_count (int): A number of session to use to speed-up analysis.
                                    Should be a number between 1 to 50 due to api limitations
                sessions (list): (Optional) list of opened sessions
                                    Used for saving some api requests
                result_set (ResultSet): (Optional) object to store results
                                    If not specified, then the new one is created

            Returns:
                A ResultSet object containing results of analysis of all matches
        """
        if result_set is None:
            result_set = ResultSet()
        if sessions is None:
            sessions = []
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
            sleep(0.25)
        return result_set

    # since smite-api returns PlayerEntries(raw) instead of raw matches
    # we have to handle it separately
    def analyze_batch(self, batch: list, result_set: ResultSet) -> int:
        """ Analyzes set of raw PlayerEntries 

            Args:
                batch (list): List of raw player entries to analyze
                result_set (ResultSet): Object to save analysis results

            Returns:
                Number of matches analyzed
        """
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

    def analyze_queue(self, api, queue_id, date, hour=-1):
        """ Calls for all games from the given queue and analyzes them
            
            Args:
                api (Smite): Api object to use for downloading data
                queue_id (int): Id of queue to analyze
                date (string formated as YYYYMMDD): Date to analyze
                hour (int): A hour to analyze (0-23) or -1 in case of whole day
                            (Default: -1)

            Returns:
                ResultSet object containing all results of analysis
        """
        response = api.make_request(
            'getmatchidsbyqueue', [queue_id, date, hour])
        ids = list(map(lambda d: d['Match'], response))
        result_set = ResultSet(hour == -1)
        count = 0
        while ids != []:
            id_str = ','.join(ids[:MAX_BATCH])
            batch = api.make_request('getmatchdetailsbatch', [id_str])
            ids = ids[MAX_BATCH:]
            count += self.analyze_batch(batch, result_set)
        result_set.analyzed_count = count
        self.results[(queue_id, date)] = result_set
        return result_set

    def load_to_db(self):
        """ Loads analyzer results to database """
        for item in self.results.items():
            (queue_id, date) = item[0]
            item[1].load_to_db(queue_id, date)

    def accumulated_result(self) -> ResultSet:
        """ Merge all ResultSet into one
            
            Returns:
                A ResultSet object containing accumulated results
        """
        rs = list(self.results.values())
        return reduce(ResultSet.accumulate, rs)

    @staticmethod
    def from_db(api=None):
        """ Builds analyzer object basing on data from database 
            
            Args:
                api (Smite): (Optional) Api used to build Analyzer
                log (bool): A flag used to log all info while downloading data from database

            Returns:
                A new Analyzer object containg all results from database

        """
        query = 'SELECT queue_id, CONVERT(varchar, date, 112), is_completed, gods, items, odds, wins, loses, name, analyzed_count, items_odds FROM analyzer'
        instance = Analyzer(api)

        try:
            db.query(query)
        except Exception as err:
            print("Error: Couldn't load Analyzer from database", file=sys.stderr)
            print(str(err.with_traceback), file=sys.stderr)
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
            items_odds = str_to_dict(item[10])

            rs = ResultSet(is_completed)
            rs.gods = gods
            rs.items = items
            rs.odds = odds
            rs.wins = wins
            rs.loses = loses
            rs.name = name
            rs.analyzed_count = analyzed_count
            rs.items_odds = items_odds

            instance.results[(queue_id, date)] = rs

        return instance
