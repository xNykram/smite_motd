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
    screen.addstr(3, 0, '''Error, couldn't ensure {} api sessions.'''.format(size))
    screen.refresh()
    write_latest_sessions(sessions)
    sleep(1)
    curses.endwin()
    exit(-1)

screen.addstr(3, 0, '''Done. Starting analysis...''')
screen.refresh()
sleep(1)

screen.clear()
screen.refresh()

# analysis here

analyzer = Analyzer()
date = sessions[0].create_timestamp()[:8] # today

threads = []
index = 0
for queue_id in QUEUES_DICT:
    thread = Thread(target=analyzer.analyze_queue, args=[sessions[index], queue_id, date, 23, index, screen])
    threads.append(thread)
    thread.start()
    index += 1

while threads != []:
    for thread in threads:
        if not thread.is_alive():
            threads.remove(thread)
    sleep(0.5)

screen.addstr(index + 2, 0, 'Pushing results to database...')
screen.refresh()
analyzer.load_to_db()

screen.addstr(index + 3, 0, '...done')
screen.refresh()
sleep(5)

curses.endwin()

exit(1)
