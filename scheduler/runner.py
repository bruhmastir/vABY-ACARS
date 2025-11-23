from random import randint
from time import sleep
from config import POLL_INTERVAL_MIN, POLL_INTERVAL_MAX

def run_periodic(callback):
    """Runs callback periodically with random delay."""
    try:
        while True:
            callback()
            delay = randint(POLL_INTERVAL_MIN, POLL_INTERVAL_MAX)
            print(f"{delay} seconds")
            sleep(delay)
    except KeyboardInterrupt:
        print("Keyboard shutdown (Ctrl+C)")
        quit()
