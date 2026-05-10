import time
from collections import deque

LATEST_INPUT = {}
LATEST_SENSOR = {}
LATEST_CALCULATED = {}

MOTOR_STATE = {
    "MOTOR_MODE": 0,           # 0 = AUTO, 1 = MANUAL
    "MOTOR_MANUAL_STATUS": 0,  # valid only in MANUAL
}

# Tracks the last time Django changed the motor mode (epoch seconds).
# Used to apply a grace period in the MQTT callback so that stale
# ESP32 packets don't immediately revert a mode change.
MOTOR_MODE_CHANGE_TIME = {"timestamp": 0}

# Ring buffer for real-time charting.
# Keeps the most recent 720 entries (~1 hour at one entry every 5 seconds).
HISTORY_BUFFER = deque(maxlen=720)