import re

CPDLC_FULL_REGEX = re.compile(
    r"^/data2/"
    r"(?P<min>\d+)/"
    r"(?P<mrn>\d*)/"
    r"(?P<code>[A-Z]{2})/"
    r"(?P<message>.*)$",
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
