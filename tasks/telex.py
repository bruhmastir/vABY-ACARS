from hoppie.messages import send_arrival_info
from vamsys.flights import get_flight_from_callsign, get_flight_from_id
from utils.time_utils import calculate_eta, hhmm_to_minutes
from hoppie.hoppie import poll_messages, send_message
from utils.logging import log

def respond_to_telex(text: str, callsign: str):
    
    if text.upper() == "REQUEST ARR INFO":
        flight_data = get_flight_from_callsign(callsign)
        dest = flight_data["dest"]
        time_rem = hhmm_to_minutes(flight_data["time_rem"])
        eta = calculate_eta(time_rem)
        send_arrival_info(callsign, arrival_airport=dest, eta=eta)
        return

    if any(greet in text.lower() for greet in ("hello", "hi")):
        reply = "vABY Dispatch: Hello, Captain! ACARS has been initialised"
        send_message(callsign, "text", reply)
        log(f"Replied to {callsign}: {reply}")
        return