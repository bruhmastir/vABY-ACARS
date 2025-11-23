import os

SERIAL_FILE = "serial.txt"

def load_serial():
    if not os.path.exists(SERIAL_FILE):
        return 1
    with open(SERIAL_FILE, "r") as f:
        return int(f.read().strip())

def save_serial(value: int):
    with open(SERIAL_FILE, "w") as f:
        f.write(str(value))

def next_serial():
    current = load_serial()
    next_value = current + 1
    save_serial(next_value)
    return current
