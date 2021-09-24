from threading import Thread
from time import sleep

# This one should be removed in the future

def map_with_threads(fun, container, key=lambda x: x, check_delay=0.5):
    """maps all items creating new threads for each operation"""
    threads = []
    for element in container:
        thread = Thread(target=fun, args=[key(element)])
        threads.append(thread)
        thread.start()
    while threads != []:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        sleep(check_delay)
