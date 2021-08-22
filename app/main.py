from smiteapi.smite import Smite, GODS_DICT, ITEMS_DICT, QUEUES_DICT, validate_sessions, ensure_sessions
from threading import Thread
import curses
from analyzer import Analyzer
from smiteapi.smiteapiscripts import read_latest_sessions, write_latest_sessions
from time import sleep

screen = curses.initscr()
curses.noecho()
curses.cbreak()

# Read latest sessions

screen.addstr(0, 0, 'Loading existing sessions...')
screen.refresh()

sessions_ids = read_latest_sessions()
sessions = [Smite(s_id) for s_id in sessions_ids]
validate_sessions(sessions) # Check for closed sessions

screen.addstr(1, 0, 'Loaded {} existing sessions.'.format(len(sessions)))
screen.refresh()

# Ensuring there is enough sessions for analysis

size = len(QUEUES_DICT)

screen.addstr(2, 0, 'Ensuring there is {} opened sessions...'.format(size))
screen.refresh()

count = ensure_sessions(sessions, size)
write_latest_sessions(sessions)

if count != size:
    screen.addstr(3, 0, '''Error, couldn't ensure {} api sessions ({} available).'''.format(size, count))
    screen.refresh()
    write_latest_sessions(sessions)
    sleep(5)
    curses.endwin()
    exit(-1)

smite = sessions[0]

screen.addstr(3, 0, f'Ensured {count} sessions.')
screen.refresh()
sleep(1)

date = smite.create_timestamp()[:8] # today
screen.addstr(4, 0, 'Starting analysis...')
screen.refresh()
sleep(1)

screen.clear()
screen.refresh()
              
# analysis here

analyzer = Analyzer()
#analyzer.analyze_match_list(match_ids, sessions=sessions, screen=screen)
index = 0

to_analyze = {}

for queue_id, queue_name in QUEUES_DICT.items():
    buffer = f'Downloading match ids for {queue_name}...'
    screen.addstr(index, 0, buffer)
    screen.refresh()
    to_analyze[queue_id] = smite.get_match_ids(queue_id, date, hour=1)
    screen.addstr(index, len(buffer), 'DONE!') 
    screen.refresh()
    index += 1

for queue_id, queue_name in QUEUES_DICT.items():
    buffer = f'Analyzing {queue_name} ...'
    screen.addstr(index, 0, buffer)
    screen.refresh()
    rs = analyzer.analyze_match_list(to_analyze[queue_id], sessions=sessions, screen=screen, log_index=index+1)
    analyzer.results[(queue_id, date)] = rs
    rs.load_to_db(queue_id, date, log=False)
    index += 2
                  
screen.addstr(index + 3, 0, '...done')
screen.refresh()
sleep(5)

curses.endwin()

exit(1)
