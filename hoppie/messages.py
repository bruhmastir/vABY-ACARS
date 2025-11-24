from vamsys.flights import get_flight_from_callsign
from .hoppie import send_message
from utils.serial import next_serial
from utils.stands import find_company_stands

def send_arrival_info(callsign, arrival_airport, eta):
    message_id = next_serial()
    stand = find_company_stands(arrival_airport)

    msg = (
        f"/data2/{message_id}//WU/ARRIVAL INFO "
        f"@{callsign}@ - @{arrival_airport}@ "
        f"ARR STAND: @{stand}@ "
        f"ETA: @{eta}@"
    )

    flight_id = get_flight_from_callsign(callsign)["flight_id"]
    print(send_message(callsign, "cpdlc", msg, flight_id))

    
    return msg
