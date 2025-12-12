from datetime import datetime, timezone

# Print logs as needed for development and bug reports
def log(msg: str):
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{now}Z] {msg}")
