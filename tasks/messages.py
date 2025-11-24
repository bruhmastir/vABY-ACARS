import re
from hoppie.hoppie import poll_messages, send_message
from utils.logging import log
from tasks.cpdlc import parse_cpdlc_packet, respond_to_cpdlc_response
from tasks.telex import respond_to_telex
from database.db_commit import get_last_received_min, insert_message_received
from vamsys.flights import get_flight_from_callsign

# Matches structures like:
# {ABY287 telex {HELLO WORLD}}
HOPPIE_PATTERN = re.compile(
    r"\{(?P<callsign>[A-Z0-9]+)\s+(?P<type>[A-Z]+)\s+\{(?P<text>.*?)\}\}",
    re.IGNORECASE
)


msg_counter = {}

def process_hoppie_messages():
    status, response = poll_messages()

    # REMOVE THIS when done testing
    response = "ok {ABY287 telex {HELLO}} {ABY287 telex {REQUEST DESCENT}} {ABY333D cpdlc {/data2/29/3/WU/WILCO}}"

    if not status:
        log("Hoppie polling error")
        return

    if response.strip() == "ok":
        log("No messages received")
        return

    log(f"Raw Hoppie: {response}")

    # Extract all messages cleanly
    matches = list(HOPPIE_PATTERN.finditer(response))

    if not matches:
        log("No valid messages found")
        return

    for match in matches:
        callsign = match.group("callsign").upper()
        msg_type = match.group("type").lower()
        raw_text = match.group("text").strip()
        flight_id = get_flight_from_callsign(callsign)["flight_id"]

        # Track per-callsign serial numbers
        msg_counter[callsign] = msg_counter.get(callsign, 0) + 1
        msg_id = f"{callsign}-{msg_counter[callsign]}"

        if msg_type == "cpdlc":
            # Process and parse CPDLC messages
            msg_data = parse_cpdlc_packet(raw_text)
            respond_to_cpdlc_response(msg_data, callsign)
            text = msg_data["message"]
            min_id = msg_data["min"]
            mrn = msg_data["mrn"]
        
        elif msg_type == "telex":
            # Parse and process TELEX or Free text messages
            text = raw_text
            respond_to_telex(text, callsign)
            prev_min = get_last_received_min(flight_id)
            min_id = prev_min + 1
            mrn = None
        else:
            # In case a different type of message such as ADS-C or PROGRESS.
            text = raw_text
            reply = f"I am sorry! I can't yet process messages of type @{msg_type.upper()}@. Safe landings!"
            send_message(callsign, "telex", reply, flight_id)

        log(f"Received {msg_type.upper()} message from {callsign}: {text}")

        # Save the received message to the DB for reference
        insert_message_received(min_id, flight_id, callsign, msg_type, mrn, text)
        