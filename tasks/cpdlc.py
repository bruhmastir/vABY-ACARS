import re
from database.db_operations import assign_stand, get_sent_message_by_min
from vamsys.flights import get_flight_from_callsign

CPDLC_FULL_REGEX = re.compile(
    r"^/data2/"
    r"(?P<min>\d+)/"
    r"(?P<mrn>\d*)/"
    r"(?P<code>[A-Z]{2})/"
    r"(?P<message>.*)$",
    re.IGNORECASE
)

ARR_INFO_REGEX = re.compile(
    # Start of string followed by the required prefix
    r"^ARRIVAL INFO "
    
    # 1. Callsign
    r"@(?P<callsign>[^@]+)@ - "
    r"@(?P<arrival_airport>[^@]+)@ "
    r"ARR STAND: @(?P<stand>[^@]+)@ "
    r"ETA: @(?P<eta>[^@]+)@$",
    
    re.IGNORECASE
)


def parse_cpdlc_packet(packet: str):
    match = CPDLC_FULL_REGEX.match(packet.strip())
    if not match:
        return {}

    min_id = int(match.group("min"))
    mrn_raw = match.group("mrn")
    mrn = int(mrn_raw) if mrn_raw.isdigit() else None
    code = match.group("code").upper()
    message = match.group("message").strip()

    data = {
        "min": min_id,
        "mrn": mrn,
        "code": code,
        "message": message
    }

    return data


def respond_to_cpdlc_response(msg_data: dict, callsign: str):
    mrn = msg_data["mrn"]
    min_id = msg_data["min"]
    code = msg_data["code"]
    msg = msg_data["message"]

    flight_data = get_flight_from_callsign(callsign)
    flight_id = flight_data["flight_id"]
    dest1 = flight_data["dest"]

    orig_msg = get_sent_message_by_min(mrn)
    orig_text = orig_msg["message"]
    orig_msg_data = parse_arr_info_msg(orig_text)
    dest = orig_msg_data["dest"]
    stand = orig_msg_data["stand"]

    if dest != dest1:
        return

    if msg == "WILCO":
        assign_stand(flight_id, callsign, dest, stand, mrn)
        return

def change_min(old_msg, min_id):
    data = parse_cpdlc_packet(old_msg)
    new_msg = f"/data2/{min_id}/{data["mrn"]}/{data["code"]}/{data["message"]}"

    return new_msg

def parse_arr_info_msg(msg):
    """
    Parse and break down an arrival information message.
    """

    match = ARR_INFO_REGEX.match(msg.strip())
    if not match:
        return {}
    # Access captured variables by their names
    callsign = match.group('callsign')
    arrival_airport = match.group('arrival_airport')
    stand = match.group('stand')
    eta = match.group('eta')

    data = {
        "callsign": callsign,
        "dest": arrival_airport,
        "stand": stand,
        "eta": eta
    }

    return data