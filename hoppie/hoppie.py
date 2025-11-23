import requests
from requests.exceptions import RequestException
from config import LOGON_CODE, CALLSIGN, HTTP_TIMEOUT

BASE_URL = "http://www.hoppie.nl/acars/system"

def send_message(to, msg_type, text):
    """Send a message via Hoppie ACARS."""
    params = {
        "logon": LOGON_CODE,
        "from": CALLSIGN,
        "to": to,
        "type": msg_type,
        "packet": text
    }
    try:
        r = requests.get(f"{BASE_URL}/connect.html", params=params, timeout=HTTP_TIMEOUT)
        return True, r.text
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