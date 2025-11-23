import re
from hoppie.hoppie import poll_messages, send_message
from utils.logging import log
from tasks.cpdlc import parse_cpdlc_packet, respond_to_cpdlc_response
from tasks.telex import respond_to_telex

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

        # Track per-callsign serial numbers
        msg_counter[callsign] = msg_counter.get(callsign, 0) + 1
        msg_id = f"{callsign}-{msg_counter[callsign]}"

        if msg_type == "cpdlc":
            # Process and parse CPDLC messages
            msg_data = parse_cpdlc_packet(raw_text)
            respond_to_cpdlc_response(msg_data, callsign)
            text = msg_data["message"]
        
        elif msg_type == "telex":
            # Parse and process TELEX or Free text messages
            text = raw_text
            respond_to_telex(text, callsign)

            #
        log(f"Received {msg_type.upper()} message from {callsign}: {text}")
        