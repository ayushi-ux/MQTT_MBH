# mqtt_app/mqtt/keys.py

# ==============================================================================
# MQTT JSON KEY CONFIGURATION
# Modify this file to scale or change the JSON keys sent/received by the sensor.
# ==============================================================================

# INCOMING TELEMETRY KEYS (from Sensor to Django)
# Map logical fields to one or more possible JSON keys in the received payload.
# If multiple keys are provided, we check them in order (short-form first).
INCOMING_KEYS = {
    "mac_address": ("mac", "mac_address"),
    "serial_number": ("sn", "serial_number"),
    
    # Sensor Readings
    "distance": ("d", "Distance", "distance", "DISTANCE"),
    "percentage": ("p", "Percentage", "percentage", "PERCENTAGE"),
    "filled_water_in_volume": ("fv", "Filled_water_in_volume", "filled_water_in_volume", "FILLED_WATER_IN_VOLUME"),
    "battery_voltage": ("bv", "Battery_voltage", "battery_voltage", "BATTERY_VOLTAGE"),
    
    # Motor Settings
    "motor_mode": ("mm", "Motor_mode", "motor_mode", "MOTOR_MODE"),
    "motor_status": ("ms", "Motor_status", "motor_status", "MOTOR_STATUS"),
    
    # Sensor Parameters (may be absent in some payloads)
    "total_height": ("h", "th", "Total_height", "total_height", "TOTAL_HEIGHT"),
    "total_volume": ("v", "tv", "Total_Volume", "Total_volume", "total_volume", "TOTAL_VOLUME"),
    "min_percentage": ("minp", "min_percentage", "Min Percentage", "min_pct", "min"),
    "max_percentage": ("maxp", "max_percentage", "Max Percentage", "max_pct", "max"),
    "deep_sleep": ("ds", "deep_sleep", "Deep Sleep"),
    "sensor_interval": ("si", "sensor_interval", "Sensor_Interval"),
    "sleep_interval": ("sli", "sleep_interval", "Sleep_Interval"),
    
    # Faults / Diagnostics
    "faults": ("f", "faults"),
}

# OUTGOING COMMAND KEYS (from Django to Sensor via MQTT)
# These are the exact short-form keys placed inside the "payload" object.
OUTGOING_KEYS = {
    "total_height": "h",
    "total_volume": "v",
    "motor_mode": "mm",
    "motor_status": "ms",
    "min_percentage": "minp",
    "max_percentage": "maxp",
    "deep_sleep": "ds",
    "sensor_interval": "si",
    "sleep_interval": "sli",
}

# COMMAND IDS for the wrapper envelope
COMMAND_IDS = {
    "config": 33,   # Device config: h, v, minp, maxp, mm, ms, ds, si, sli
    "wifi": 49,      # WiFi provisioning: ssid, password
}

# BLE PROVISIONING KEYS (used on browser-side Web Bluetooth)
# Specify the exact JSON keys used when communicating with the sensor via Bluetooth.
BLE_KEYS = {
    "ssid": "ssid",
    "password": "password",
    "mac_address": "mac_address",
    "serial_number": "serial_number",
    "min_percentage": "min_percentage",
    "max_percentage": "max_percentage",
    "deep_sleep": "deep_sleep",
    "sensor_interval": "sensor_interval",
    "sleep_interval": "sleep_interval",
}


def get_sensor_value(data, field, default=None):
    """
    Looks up a logical field (e.g. 'distance') in the incoming JSON dictionary 'data',
    using the configured candidate keys in INCOMING_KEYS.
    """
    candidate_keys = INCOMING_KEYS.get(field)
    if not candidate_keys:
        return default
        
    # If the candidate_keys is a single string instead of tuple/list
    if isinstance(candidate_keys, str):
        candidate_keys = (candidate_keys,)
        
    for key in candidate_keys:
        if key in data and data[key] is not None:
            return data[key]
            
    return default


def build_command(command_id, mac, serial_number, payload):
    """
    Wraps a payload dict in the standard command envelope:
    {
        "command_id": <int>,
        "command_type": 1,
        "sn": "<serial_number>",
        "mac": "<mac_address>",
        "payload": { ... }
    }
    """
    return {
        "command_id": command_id,
        "command_type": 1,
        "sn": serial_number or "",
        "mac": mac or "",
        "payload": payload,
    }
