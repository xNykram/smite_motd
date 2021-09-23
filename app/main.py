import sys
import getopt
from smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT, QUEUES_DICT, validate_sessions, ensure_sessions
from threading import Thread
import curses
from analyzer import Analyzer, MAX_BATCH
from smiteapi.smiteapiscripts import read_latest_sessions, write_latest_sessions
from time import sleep
from datetime import datetime, timedelta
from crons.motd import update_motd_god_ids

screen = None
sessions = []
smite = None
analyzer = None
log = 0
initialized = False


def main(argv):
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
            fill()
        elif opt == '-a':
            analyze_yeasterday()
        elif opt == '-u':
            update_all()
        elif opt == '-q':
            analyze_update(arg)


def print_usage():
    print('Use ./main.py <task>')
    print('task list:')
    print('-m  -- motd, analyzes and updates latest motds')
    print('-u  -- update, updates top gods')
    print('-a  -- all, analyzes all queues on yeasterday, not working yet')
    print('-q [id] -- analyzes queue with given id only')


def print_curses(msg, y=0, delta=0):
    global log
    if screen is None:
        print(msg)
    screen.addstr(log + delta, y, msg)
    screen.refresh()
    if delta >= 0:
        log += max(delta, 1)


def initialize():
    global screen, smite, analyzer, log, initialized
    if initialized:
        return
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()

    # Read latest sessions

    print_curses('Loading existing sessions...')

    sessions_ids = read_latest_sessions()
    sessions = [Smite(s_id) for s_id in sessions_ids]
    validate_sessions(sessions)  # Check for closed sessions
    print_curses(f'Found {len(sessions)} existing sessions.')
    screen.refresh()

    if len(sessions) == 0:
        print_curses('Ensuring there is 1 opened sessions...')
        ensure_sessions(sessions, 1)

    smite = sessions[0]
    analyzer = Analyzer.from_db()
    initialized = True


def update_all():
    global analyzer, log
    initialize()
    for motd_name in smite.get_motd_names():
        buffer = f'Updating winrate of {motd_name}...'
        print_curses(buffer)
        update_motd_god_ids(motd_name)
        print_curses('DONE!', y=len(buffer)+1, delta=-1)


def analyze_update(queue):
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
    initialize()
    yeasterday = datetime.now() - timedelta(days=1)
    date = yeasterday.strftime('%Y%m%d')
    print_curses(f"Yesterday date is {yeasterday.strftime('%d.%m.%Y')}")
    for queue_id, name in QUEUES_DICT.items():
        if not handle_queue(queue_id, date, name):
            break
    sleep(2)


def handle_queue(queue_id, date, name=None):
    global log
    if name is None:
        name = QUEUES_DICT.get(queue_id, 'UNKNOWN')
    if (queue_id, date) in analyzer.results:
        print_curses(f'{name} @ {date} is already analyzed. Skipping...')
        return True
    requests = smite.request_left()
    buffer = f'Fetching match list for {name} @ {date}...'
    print_curses(buffer)
    match_ids = smite.get_match_ids(queue_id, date)
    print_curses(f'DONE! Fetched {len(match_ids)} games.', y=len(
        buffer)+1, delta=-1)
    if requests < len(match_ids) / MAX_BATCH + 11:
        print_curses('Daily request limit reached. Aborting')
        return False
    rs = analyzer.analyze_match_list(
        match_ids, sessions=sessions, screen=screen, log_index=log)
    log += 1
    rs.name = name
    rs.load_to_db(queue_id, date)

    return True


def fill():
    global log
    initialize()
    delta = 1
    name, date = smite.get_latest_motd(delta)
    while name != '':
        if not handle_queue(434, date, name):
            break
        delta += 1
        name, date = smite.get_latest_motd(delta)

    update_all()

    print_curses('All done.', delta=1)
    sleep(2)

    curses.endwin()


if __name__ == '__main__':
    main(sys.argv[1:])
