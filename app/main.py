import sys, getopt
from smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT, QUEUES_DICT, validate_sessions, ensure_sessions
from threading import Thread
import curses
from analyzer import Analyzer
from smiteapi.smiteapiscripts import read_latest_sessions, write_latest_sessions
from time import sleep
from crons.motd import update_motd_god_ids 

screen = None
sessions = []
smite = None
analyzer = None

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'ma')
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

def print_usage():
    print('Use ./main.py <task>')
    print('task list:')
    print('-m  -- motd, analyzes and updates latest motds')
    print('-a  -- all, analyzes all queues on yeasterday, not working yet')

def initialize():
    global screen, smite, analyzer
    screen = curses.initscr()
    curses.noecho()
    curses.cbreak()

    # Read latest sessions

    screen.addstr(0, 0, 'Loading existing sessions...')
    screen.refresh()

    sessions_ids = read_latest_sessions()
    sessions = [Smite(s_id) for s_id in sessions_ids]
    validate_sessions(sessions) # Check for closed sessions
    screen.addstr(1, 0, f'Found {len(sessions)} existing sessions.')
    screen.refresh()

    ensure_sessions(sessions, 1)

    smite = sessions[0]
    analyzer = Analyzer.from_db()

def analyze_yeasterday():
    print("This feature isn't working yet.")

def fill():
    initialize()
    log = 2
    delta = 1
    name, date = smite.get_latest_motd(delta)
    while name != '':
        if (434, date) in analyzer.results:
            screen.addstr(log, 0, f'{name} @ {date} is already analyzed. Skipping...')
            screen.refresh()
            log += 1
            delta += 1
            name, date = smite.get_latest_motd(delta)
            continue
        buffer = f'Fetching match list for {name} @ {date}...'
        screen.addstr(log, 0, buffer)
        screen.refresh()
        match_ids = smite.get_match_ids_motd(date)
        screen.addstr(log, len(buffer), 'DONE!')
        screen.refresh()
        rs = analyzer.analyze_match_list(match_ids, sessions=sessions, screen=screen, log_index=log+1)
        rs.name = name
        rs.load_to_db(434, date)
        log += 2
        delta += 1
        name, date = smite.get_latest_motd(delta)

    for motd_name in smite.get_motd_names():
        buffer = f'Updating winrate of {motd_name}...'
        screen.addstr(log, 0, buffer)
        screen.refresh()
        update_motd_god_ids(motd_name)
        screen.addstr(log, len(buffer), 'DONE!')
        screen.refresh()
        log += 1

    screen.addstr(log + 1, 0, 'All done.')
    screen.refresh()
    sleep(2)

    curses.endwin()

if __name__ == '__main__':
    main(sys.argv[1:])
