import sys
import getopt
from api.smite import Smite, QUEUES_DICT, validate_sessions, ensure_sessions
from analyzer import Analyzer, MAX_BATCH
from utils.config import read_latest_sessions
from time import sleep
from datetime import datetime, timedelta
from db.motd import update_motd_god_ids

# Number of top gods inserted to database for each motd
TOP_COUNT = 10

log_file = None
sessions = []
smite = None
analyzer = None
initialized = False


def main(argv):
    global log_file
    try:
        opts, args = getopt.getopt(argv, 'mauq:')
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
    log_file.close()
    sys.exit(1)


def print_usage():
    print('Use ./main.py <task>')
    print('task list:')
    print('-m  -- motd, analyzes and updates latest motds')
    print('-u  -- update, updates top gods')
    print('-a  -- all, analyzes all queues on yeasterday, not working yet')
    print('-q [id] -- analyzes queue with given id only')


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
    global smite, analyzer, initialized, log_file
    if initialized:
        return
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
    smite.save_motd()
    for motd_name in smite.get_motd_names():
        print_log(f'Updating winrate of {motd_name}...')
        update_motd_god_ids(motd_name, n=TOP_COUNT, analyzer=analyzer)
        print_log(f'{motd_name} updated!')


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


if __name__ == '__main__':
    main(sys.argv[1:])
