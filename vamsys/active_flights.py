import json
from vamsys.flights import get_flight_from_id
# Temporary mock data until API connected
from mock_data.active_flights_json import ACTIVE_FLIGHTS_JSON

def parse_active_flights(active_json_str: str):
    flights_raw = json.loads(active_json_str)["data"]["flights"]
    flights = []

    for flight_id, flight in flights_raw.items():

        if not isinstance(flight, dict):
            continue  # Skip invalid entries

        booking_id = str(flight["bookingId"])
        arrival_airport = flight["arrivalAirport"]
        time_remaining = flight["progress"]["timeRemaining"]
        callsign = get_flight_from_id(flight_id)["callsign"]

        flights.append({
            "flight_id": flight_id,
            "booking_id": booking_id,
            "arrival_airport": arrival_airport,
            "time_remaining": time_remaining,
            "callsign": callsign
        })

    return flights

def get_live_flight_data():
    # TODO: Implement vAMSYS API call
    return ACTIVE_FLIGHTS_JSON