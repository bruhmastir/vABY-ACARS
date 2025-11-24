import sqlite3
from config import DB_NAME

def db_init(db_name=DB_NAME):
    """
    Initializes the SQLite database and creates the necessary tables.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Table 1: messages_sent
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages_sent (
            MIN INTEGER PRIMARY KEY AUTOINCREMENT,
            FLIGHT_ID TEXT NOT NULL,
            CALLSIGN TEXT NOT NULL,
            TYPE TEXT NOT NULL,
            MESSAGE TEXT
        )
    """)

    # Table 2: messages_received
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages_received (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            MIN INTEGER NOT NULL,
            FLIGHT_ID TEXT NOT NULL,
            CALLSIGN TEXT NOT NULL,
            TYPE TEXT NOT NULL,
            MRN INTEGER,
            MESSAGE TEXT
        )
    """)

    # Table 3: stand_assignments (includes Foreign Key to messages_sent)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stand_assignments (
            FLIGHT_ID TEXT PRIMARY KEY,
            CALLSIGN TEXT NOT NULL,
            AIRPORT TEXT NOT NULL,
            STAND TEXT NOT NULL,
            MIN INTEGER NOT NULL,
            FOREIGN KEY(MIN) REFERENCES messages_sent(MIN)
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' initialized with all tables.")

db_init()