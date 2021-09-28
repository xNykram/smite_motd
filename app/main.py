import sys
import getopt
from socket import gethostname
from api.smite import Smite, QUEUES_DICT, validate_sessions, ensure_sessions
from analyzer import Analyzer, MAX_BATCH
from utils.config import read_latest_sessions
from time import sleep
from datetime import datetime, timedelta
from db.motd import update_motd_god_ids
from db.database import db
from utils.images import save_god_images
from db.tierlist import update_tier_list

# Number of top gods inserted to database for each motd
TOP_COUNT = 8

# Path to directory where will be stored gods images
PATH_TO_GODS_IMAGES = '../smite_lore/smite_lore/static/gods/'

log_file = None
sessions = []
smite = None
analyzer = None
initialized = False
debug = False


def main(argv):
    global log_file, debug
    try:
        opts, args = getopt.getopt(argv, 'mauq:idf')
    except getopt.GetoptError:
        print_usage()
        sys.exit(2)
    if opts == []:
        print_usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-m':
            try:
                fill()
            except Exception as err:
                print_log('Error occurred while analyzing latest motds.')
                print_log(err, with_time=False)
        elif opt == '-a':
            try:
                analyze_yeasterday()
            except Exception as err:
                print_log(
                    'Error occurred while analyzing yeasterday queues.')
                print_log(err, with_time=False)
        elif opt == '-u':
            try:
                update_all()
            except Exception as err:
                print_log(
                    'Error occurred while synchronizing data with database.')
                print_log(err, with_time=False)
        elif opt == '-q':
            try:
                analyze_update(arg)
            except Exception as err:
                print_log(f'Error occurred while analyzing queue {arg}')
                print_log(err, with_time=False)
        elif opt == '-f':
            try:
                fill()
            except Exception as err:
                print_log('Error occurred while filling database')
                print_log(err, with_time=False)
        elif opt == '-i':
            try:
                initialize()
                count = save_god_images(PATH_TO_GODS_IMAGES, file=log_file)
                print_log(f'Gods images update was successfully done ({count} downloaded).')
                if count > 0:
                    response = f'Downloaded {count} images'
                else:
                    response = ''
                log_to_database('updateGodsImages', 'Success', response)
            except Exception as err:
                print_log('Error occurred while saving god images')
                print_log(err, with_time=False)
                log_to_database('updateGodsImages', 'Failure', str(err.with_traceback()))
        elif opt == '-d':
            debug = True
            print_log('Debug mode: ON')
    log_file.close()
    sys.exit(1)


def print_usage():
    print('Use ./main.py <task>')
    print('options')
    print('-m  -- motd, analyzes and updates latest motds')
    print('-u  -- update, updates top gods')
    print('-f  -- fill, fill database with latest motds')
    print('-a  -- all, analyzes all queues on yeasterday, not working yet')
    print('-q [id] -- analyzes queue with given id only')
    print('-d  -- debug, turns on debug mode')
    print(f"-i  -- images, updates gods images in directory '{PATH_TO_GODS_IMAGES}')") 


def print_log(msg, with_time=True):
    """Prints given message to log file

    Args:
        with_time(bool): A flag is used to print logs with its date (default: True)
    """
    global log_file
    if with_time:
        today = datetime.now()
        now_str = today.strftime('%d.%m.%Y %H:%M:%S')
        print(f'[{now_str}] {msg}', file=log_file)
    else:
        print(msg, file=log_file)


def initialize():
    """ Initializes sessions and log file """
    global smite, analyzer, initialized, log_file, debug
    if initialized:
        return
    if debug:
        log_file = sys.stdout
    else:
        log_file = open('../log.txt', mode='a')
        sys.stderr = log_file

    # Read latest sessions
    print_log('Loading existing sessions...')

    sessions_ids = read_latest_sessions()
    sessions = [Smite(s_id) for s_id in sessions_ids]
    validate_sessions(sessions)  # Check for closed sessions
    print_log(f'Found {len(sessions)} existing sessions.')

    if len(sessions) == 0:
        print_log('Ensuring there is 1 opened sessions...')
        ensure_sessions(sessions, 1)

    smite = sessions[0]
    analyzer = Analyzer.from_db()
    initialized = True


def update_all():
    """ Updates today's motd schedule and pref gods """
    global analyzer, smite
    initialize()
    print_log('Updating motd schedule...')
    try:
        smite.save_motd()
        log_to_database('updateMotd', 'Success')
    except Exception as err:
        print_log("Error. Couldn't save tommorow's motd!")
        print_log(err.args[1], with_time=False)
        log_to_database('updateMotd', 'Failure', err.args[1])
    update_motd_pref_gods()
    try:
        for queue_id in QUEUES_DICT:
            name = QUEUES_DICT[queue_id]
            print_log(f'Updating tierlist of {name}...')
            update_tier_list(queue_id, analyzer)
        print_log('Tierlist update done!')
        log_to_database('updateTierList', 'Success')
    except Exception as err:
        print_log("Error. Couldn't update tierlist")
        print_log(str(err), with_time=False)
        log_to_database('updateTierList', 'Failure', str(err))


def update_motd_pref_gods():
    global analyzer, smite
    for motd_name in smite.get_motd_names():
        try:
            print_log(f'Updating winrate of {motd_name}...')
            update_motd_god_ids(motd_name, n=TOP_COUNT, analyzer=analyzer)
            print_log(f'{motd_name} updated!')
        except Exception as err:
            response = f"Error while saving {motd_name}: {str(err)}"
            print_log(response)
            log_to_database('updateMotdPrefGods', 'Failure', response)
            break
    log_to_database('updateMotdPrefGods', 'Success')


def analyze_update(queue):
    """ Analyzes yeasterday's queue and pushes results to database """
    queue = int(queue)
    if queue not in QUEUES_DICT:
        print('Invaild queue id.')
        print('Available queues:')
        for q_id, name in QUEUES_DICT.items():
            print(f'{q_id} => {name}')
        return
    initialize()
    yeasterday = datetime.now() - timedelta(days=1)
    date = yeasterday.strftime('%Y%m%d')
    handle_queue(queue, date)


def analyze_yeasterday():
    """ Analyzes all yesterday's queues and pushes results to database """
    initialize()
    yeasterday = datetime.now() - timedelta(days=1)
    date = yeasterday.strftime('%Y%m%d')
    print_log(f"Yesterday date is {yeasterday.strftime('%d.%m.%Y')}")
    for queue_id, name in QUEUES_DICT.items():
        if not handle_queue(queue_id, date, name):
            break


def handle_queue(queue_id, date, name=None):
    """ Analyzes queue and pushes result to database

        Args:
            queue_id (int): Id of queue to analyze
            date (string in format YYYYMMDD): Date of queue to analyze
            name (string): Optional argument for analyzing motds
    """
    if name is None:
        name = QUEUES_DICT.get(queue_id, 'UNKNOWN')
    if (queue_id, date) in analyzer.results:
        print_log(f'{name} @ {date} is already analyzed. Skipping...')
        return True
    requests = smite.request_left()
    buffer = f'Fetching match list for {name} @ {date}...'
    print_log(buffer)
    match_ids = smite.get_match_ids(queue_id, date)
    print_log(f'Downloaded {len(match_ids)} games.')
    if requests < len(match_ids) / MAX_BATCH + 11:
        print_log('Daily request limit reached. Aborting')
        return False
    rs = analyzer.analyze_match_list(match_ids, sessions=sessions)
    rs.name = name
    rs.load_to_db(queue_id, date)

    return True


def fill():
    """ Analyzes all available motds and pushes results to database """
    initialize()
    delta = 1
    name, date = smite.get_latest_motd(delta)
    while name != '':
        if not handle_queue(434, date, name):
            break
        delta += 1
        name, date = smite.get_latest_motd(delta)

    print_log('Fill done.')


def log_to_database(log_type: str, info: str, response='') -> bool:
    host = gethostname()
    if response == '' or response is None:
        query = "INSERT INTO logs (type, logInfo, date, response, host) \
                VALUES ('{}', '{}', GETDATE(), NULL, '{}')"
        info = info.replace("'", "''")
        final_query = query.format(log_type, info, host)
    else:
        query = "INSERT INTO logs (type, logInfo, date, response, host) \
                VALUES ('{}', '{}', GETDATE(), '{}', '{}')"
        info = info.replace("'", "''")
        response = response.replace("'", "''")
        final_query = query.format(log_type, info, response, host)

    try:
        db.query(final_query)
    except Exception as err:
        print_log(f"Error: Couldn't execute query. {err}")
        print_log(final_query, False)


if __name__ == '__main__':
    main(sys.argv[1:])
