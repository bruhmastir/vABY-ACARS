def get_flight_from_callsign(callsign: str):
    # TODO: Real logic later
    flight_id = "5291784"
    origin = "OMSJ"
    dest = "LTFM"
    time_rem = "00:34"
    pilot_id = "55"

    flight_data = {"flight_id": flight_id, "origin": origin, "dest": dest, "time_rem": time_rem, "pilot_id": pilot_id}

    return flight_data

def get_flight_from_id(flight_id: str):
    # TODO: Real logic later
    callsign = "ABY287"
    origin = "OMSJ"
    dest = "LTFM"
    time_rem = "00:34"
    pilot_id = "55"

    flight_data = {"callsign": callsign, "origin": origin, "dest": dest, "time_rem": time_rem, "pilot_id": pilot_id}

    return flight_data

# def 