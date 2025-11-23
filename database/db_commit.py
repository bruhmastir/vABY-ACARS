import sqlite3

# Define the default database file name
DB_NAME = 'atc_data.db'

def connect_db(db_name=DB_NAME):
    """Establishes and returns a connection to the SQLite database."""
    # Ensure foreign key constraints are enforced
    conn = sqlite3.connect(db_name)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# --- C: CREATE (INSERT) Operations ---

def insert_message_sent(min_id, flight_id, callsign, msg_type, message):
    """Inserts a new message into the messages_sent table."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages_sent (MIN, FLIGHT_ID, CALLSIGN, TYPE, MESSAGE)
            VALUES (?, ?, ?, ?, ?)
            """,
            (min_id, flight_id, callsign, msg_type, message)
        )
        conn.commit()
        return f"Successfully inserted MIN {min_id} into messages_sent."
    except sqlite3.IntegrityError as e:
        return f"Error inserting message sent (Integrity Error): {e}"
    except sqlite3.Error as e:
        return f"Database Error: {e}"
    finally:
        if conn:
            conn.close()


def insert_message_received(min_id, flight_id, callsign, msg_type, mrn, message):
    """Inserts a new message into the messages_received table."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        # ID is AUTOINCREMENT, so we don't include it in the insert statement
        cursor.execute(
            """
            INSERT INTO messages_received (MIN, FLIGHT_ID, CALLSIGN, TYPE, MRN, MESSAGE)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (min_id, flight_id, callsign, msg_type, mrn, message)
        )
        conn.commit()
        return f"Successfully inserted new message into messages_received."
    except sqlite3.Error as e:
        return f"Database Error: {e}"
    finally:
        if conn:
            conn.close()


def assign_stand(flight_id, callsign, airport, stand, min_id):
    """
    Inserts a new stand assignment.
    Requires a valid MIN ID to exist in messages_sent due to the foreign key.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO stand_assignments (FLIGHT_ID, CALLSIGN, AIRPORT, STAND, MIN)
            VALUES (?, ?, ?, ?, ?)
            """,
            (flight_id, callsign, airport, stand, min_id)
        )
        conn.commit()
        return f"Successfully assigned stand {stand} to {callsign}."
    except sqlite3.IntegrityError as e:
        # This will catch errors like duplicate FLIGHT_ID or non-existent MIN_ID
        return f"Error assigning stand (Integrity Error): Check if FLIGHT_ID exists or if MIN ID is valid. Details: {e}"
    except sqlite3.Error as e:
        return f"Database Error: {e}"
    finally:
        if conn:
            conn.close()

# --- R: READ (SELECT) Operations ---

def get_messages_by_callsign(callsign):
    """Retrieves all sent and received messages for a specific callsign."""
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        cursor = conn.cursor()

        # Get sent messages
        cursor.execute(
            "SELECT MIN, FLIGHT_ID, TYPE, MESSAGE FROM messages_sent WHERE CALLSIGN = ?",
            (callsign,)
        )
        sent_msgs = [dict(row) for row in cursor.fetchall()]

        # Get received messages
        cursor.execute(
            "SELECT ID, MIN, MRN, TYPE, MESSAGE FROM messages_received WHERE CALLSIGN = ?",
            (callsign,)
        )
        recv_msgs = [dict(row) for row in cursor.fetchall()]

        return {
            'sent': sent_msgs,
            'received': recv_msgs
        }
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return {'sent': [], 'received': []}
    finally:
        if conn:
            conn.close()

def get_stand_assignment_details(min_id):
    """
    Retrieves stand assignment details based on the MIN (message sent) ID.
    Uses an explicit JOIN.
    """
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                s.MIN, s.FLIGHT_ID, s.CALLSIGN, s.MESSAGE,
                a.STAND, a.AIRPORT
            FROM messages_sent s
            JOIN stand_assignments a ON s.MIN = a.MIN
            WHERE s.MIN = ?
            """,
            (min_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- D: DELETE Operations ---

def delete_stand_assignment(flight_id):
    """Deletes a stand assignment by FLIGHT_ID."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM stand_assignments WHERE FLIGHT_ID = ?",
            (flight_id,)
        )
        rows_affected = cursor.rowcount
        conn.commit()
        if rows_affected > 0:
            return f"Successfully deleted stand assignment for FLIGHT_ID {flight_id}."
        else:
            return f"No stand assignment found for FLIGHT_ID {flight_id}."
    except sqlite3.Error as e:
        return f"Database Error: {e}"
    finally:
        if conn:
            conn.close()