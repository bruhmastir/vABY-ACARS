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

def insert_message_sent(flight_id, callsign, msg_type, message):
    """Inserts a new message into the messages_sent table."""
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages_sent (FLIGHT_ID, CALLSIGN, TYPE, MESSAGE)
            VALUES (?, ?, ?, ?)
            """,
            (flight_id, callsign, msg_type, message)
        )
        conn.commit()
        return f"Successfully inserted the message into messages_sent."
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

def get_messages_by_flight(flight_id):
    """Retrieves all sent and received messages for a specific flight."""
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row  # Allows accessing columns by name
        cursor = conn.cursor()

        # Get sent messages
        cursor.execute(
            "SELECT MIN, FLIGHT_ID, TYPE, MESSAGE FROM messages_sent WHERE FLIGHT_ID = ?",
            (flight_id,)
        )
        sent_msgs = [dict(row) for row in cursor.fetchall()]

        # Get received messages
        cursor.execute(
            "SELECT ID, MIN, MRN, TYPE, MESSAGE FROM messages_received WHERE FLIGHT_ID = ?",
            (flight_id,)
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

def get_stand_assignment_by_flight_id(flight_id):
    """
    Retrieves stand assignment details based on the FLIGHT_ID.
    Uses an explicit JOIN to include the associated message details.
    """
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                s.MIN, s.FLIGHT_ID, s.CALLSIGN, s.MESSAGE AS SENT_MESSAGE,
                a.STAND, a.AIRPORT
            FROM stand_assignments a
            JOIN messages_sent s ON a.MIN = s.MIN
            WHERE a.FLIGHT_ID = ?
            """,
            (flight_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_last_received_min(flight_id):
    """
    Retrieves the MIN (Message Identification Number) of the most recent 
    message received for a specific flight_id. Returns 0 if no messages are found.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # Use the MAX aggregate function to find the highest MIN value
        cursor.execute(
            """
            SELECT
                MAX(MIN)
            FROM messages_received
            WHERE FLIGHT_ID = ?
            """,
            (flight_id,)
        )
        
        # fetchone() will return a tuple (min_value,) or (None,) if no rows matched the WHERE clause
        result = cursor.fetchone()[0]

        # If MAX returns None (meaning no rows were found), we return 0 as requested.
        return result if result is not None else 0

    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        return 0
    finally:
        if conn:
            conn.close()

def get_last_received_message(flight_id):
    """
    Retrieves the most recent message received for a specific flight_id.
    This is determined by the highest MIN (Message Identification Number).
    """
    try:
        conn = connect_db()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                ID, MIN, CALLSIGN, TYPE, MRN, MESSAGE
            FROM messages_received
            WHERE FLIGHT_ID = ?
            ORDER BY MIN DESC
            LIMIT 1
            """,
            (flight_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else {"min": 0}
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        # return None
        return {"error": e}
    finally:
        if conn:
            conn.close()

# --- U: UPDATE Operations ---

def update_stand_assignment_stand(flight_id, new_stand):
    """
    Updates the STAND assigned to a specific flight_id in the stand_assignments table.
    """
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE stand_assignments
            SET STAND = ?
            WHERE FLIGHT_ID = ?
            """,
            (new_stand, flight_id)
        )
        rows_affected = cursor.rowcount
        conn.commit()

        if rows_affected > 0:
            return f"Successfully updated stand for FLIGHT_ID {flight_id} to {new_stand}."
        else:
            return f"No stand assignment found or updated for FLIGHT_ID {flight_id}."

    except sqlite3.Error as e:
        return f"Database Error: {e}"
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