from scheduler.runner import run_periodic
from tasks.flights import find_arriving_flights
from tasks.messages import process_hoppie_messages
from utils.logging import log
from database.db_init import db_init



def periodic_tasks():
    log("Running periodic tasks...")

    # Check active flights on vAMSYS
    find_arriving_flights()

    # Poll and reply to Hoppie messages
    process_hoppie_messages()

if __name__ == "__main__":
    db_init()
    log("ACARS system started")
    run_periodic(periodic_tasks)
