# Hoppie's ACARS logon details
LOGON_CODE = ""
CALLSIGN = "TESTOPS"

# Configure how many minutes before arrival should the arrival messages be automatically sent
TIME_REMAINING_TO_SEND = int(35) # minutes

# Hoppie's ACARS API settings. Standard protocol - Not to be changed
BASE_URL = "http://www.hoppie.nl/acars/system/connect.html"
POLL_INTERVAL_MIN = 45  # seconds
POLL_INTERVAL_MAX = 75  # seconds
HTTP_TIMEOUT = 15       # seconds
