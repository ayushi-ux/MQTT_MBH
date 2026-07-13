import time
from collections import deque

DEVICES_STATE = {}

def get_default_mac():
    try:
        from mqtt_app.models import Device
        dev = Device.objects.first()
        return dev.mac_address if dev else "default"
    except Exception:
        return "default"

def get_device_state(mac_address=None):
    """Retrieve or initialize the state for a specific device MAC address.
    If no MAC is provided, falls back to the first device in the database.
    """
    if not mac_address:
        mac_address = get_default_mac()

    if mac_address not in DEVICES_STATE:
        DEVICES_STATE[mac_address] = {
            "LATEST_INPUT": {},
            "LATEST_SENSOR": {},
            "LATEST_CALCULATED": {},
            "MOTOR_STATE": {
                "MOTOR_MODE": 0,           # 0 = AUTO, 1 = MANUAL
                "MOTOR_MANUAL_STATUS": 0,  # valid only in MANUAL
            },
            "MOTOR_MODE_CHANGE_TIME": {"timestamp": 0},
            "HISTORY_BUFFER": deque(maxlen=720)
        }
    return DEVICES_STATE[mac_address]