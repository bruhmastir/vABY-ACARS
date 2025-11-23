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

    print(send_message(callsign, "cpdlc", msg))
