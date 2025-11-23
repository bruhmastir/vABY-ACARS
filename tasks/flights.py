from config import TIME_REMAINING_TO_SEND
from utils.logging import log
from utils.time_utils import hhmm_to_minutes, calculate_eta
from vamsys.active_flights import parse_active_flights, get_live_flight_data
from hoppie.messages import send_arrival_info


flights_messaged = set()

def find_arriving_flights():
    """Checks VAMSYS data and sends messages for arriving flights."""
    live_flight_data = get_live_flight_data()
    flights = parse_active_flights(live_flight_data)

    for f in flights:
        flight_id = f["flight_id"]

        minutes_remaining = hhmm_to_minutes(f["time_remaining"])
        eta = calculate_eta(minutes_remaining)

        if minutes_remaining <= TIME_REMAINING_TO_SEND:
            if flight_id not in flights_messaged:
                log(f"Sending arrival info for {f['callsign']} (ETA {eta})")
                send_arrival_info(f["callsign"], f["arrival_airport"], eta)
                flights_messaged.add(flight_id)
