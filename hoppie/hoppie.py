import requests
from requests.exceptions import RequestException
from config import LOGON_CODE, CALLSIGN, HTTP_TIMEOUT
from database.db_operations import insert_message_sent
from tasks.cpdlc import change_min

BASE_URL = "http://www.hoppie.nl/acars/system"

def send_message(to, msg_type, text, flight_id: str = "", included_min: int = 0):
    """
    Inserts message, confirms MIN, updates header, and sends the message 
    via Hoppie ACARS.
    
    :param to: The recipient's callsign.
    :param msg_type: The message type (e.g., "CPDLC").
    :param text: The raw message text, potentially containing a guessed MIN.
    :param flight_id: The associated flight ID.
    :returns: A tuple (success_status, response_text, final_min)
    """

    params = {
        "logon": LOGON_CODE,
        "from": CALLSIGN,
        "to": to,
        "type": msg_type,
        "packet": text
    }
    
    # --- 1. Insert and Get Actual MIN ---
    
    # We need to insert the *original* message text first to get the database's MIN.
    # The new_min will be the MIN from the DB, or None if the insert failed.
    status, min_id, sts_msg = insert_message_sent(flight_id, to, msg_type, text)

    if not min_id:
        return False, "Database insertion failed. Message not sent."
    
    # --- 2. If needed, Compare MINs ---
    
    # Check if the message includes a header with MIN
    if included_min != 0 and msg_type == "cpdlc":

        # Check that the MIN that was *guessed* and placed in the message header matches the MIN in the DB
        min_matches = included_min == min_id

        if not min_matches:

            # If it does not match, then change the MIN in the message
            text = change_min(text, min_id)
    try:

        # Send the message
        r = requests.get(f"{BASE_URL}/connect.html", params=params, timeout=HTTP_TIMEOUT)
        return status, r.text
    except RequestException as e:
        return False, f"Send failed: {e}"



def poll_messages():
    """Poll for incoming messages via Hoppie ACARS."""
    params = {
        "logon": LOGON_CODE,
        "from": CALLSIGN,
        "to": "some",
        "type": "poll",
        "packet": "text"
    }
    try:
        r = requests.get(f"{BASE_URL}/connect.html", params=params, timeout=HTTP_TIMEOUT)
        return True, r.text
    except RequestException as e:
        return False, f"Send failed: {e}"