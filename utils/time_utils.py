from datetime import datetime, timedelta

def calculate_eta(minutes_remaining: int) -> str:
    now = datetime.now()
    eta = now + timedelta(minutes=minutes_remaining)
    return eta.strftime("%H:%M")

def hhmm_to_minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m
