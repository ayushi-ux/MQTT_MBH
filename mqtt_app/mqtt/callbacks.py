import json
import time

from django.utils import timezone

from mqtt_app.mqtt.topics import MQTT_TOPIC
from mqtt_app.services.state import (
    HISTORY_BUFFER,
    LATEST_CALCULATED,
    LATEST_INPUT,
    LATEST_SENSOR,
    MOTOR_MODE_CHANGE_TIME,
    MOTOR_STATE,
)
from mqtt_app.services.water_logic import calculate


# -- Helpers -----------------------------------------------------------


def _get(data, *keys, default=0):
    """Return the value for the first key found in *data*.

    Unlike chaining ``data.get(k1) or data.get(k2)`` this correctly
    handles falsy-but-valid values such as ``0`` and ``0.0``.
    """
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


# -- MQTT callbacks ----------------------------------------------------


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] MQTT connected")
        client.subscribe(MQTT_TOPIC)
        print("[OK] Subscribed to:", MQTT_TOPIC)
    else:
        print("[ERR] MQTT connection failed | rc =", rc)


def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
    except Exception:
        print("[ERR] Invalid JSON on", msg.topic)
        return

    # -- 1. Ignore messages that WE published -------------------------
    #    Every message Django publishes carries "_source": "django".
    #    The ESP32 ignores unknown keys, so this is safe.
    if data.get("_source") == "django":
        return

    print("[MQTT] SENSOR DATA:", data)

    # -- 2. Detect ESP32 sensor data ----------------------------------
    #    ESP32 payload always contains a "Distance" key (Title_case).
    #    Example:
    #    {
    #      "Distance": 2.13, "Total_height": 1, "Percentage": 0,
    #      "Total_Volume": 1000, "Filled_water_in_volume": 1000,
    #      "Motor_mode": 0, "Motor_status": 1, "Battery_voltage": 3.705
    #    }
    has_distance = (
        "Distance" in data
        or "distance" in data
        or "DISTANCE" in data
    )

    if not has_distance:
        print("[WARN] Message has no Distance key - ignored:", data)
        return

    try:
        distance = float(_get(data, "Distance", "distance", "DISTANCE"))
        battery  = float(_get(data, "Battery_voltage", "battery_voltage", "BATTERY_VOLTAGE"))
        motor_mode   = int(float(_get(data, "Motor_mode", "motor_mode", "MOTOR_MODE")))
        motor_status = int(float(_get(data, "Motor_status", "motor_status", "MOTOR_STATUS")))

        sensor_height = float(_get(data, "Total_height", "total_height", "TOTAL_HEIGHT"))
        sensor_volume = float(_get(data, "Total_Volume", "Total_volume", "total_volume", "TOTAL_VOLUME"))
    except (ValueError, TypeError) as exc:
        print("[ERR] Bad sensor values:", exc)
        return

    # -- 3. Update raw sensor state -----------------------------------
    LATEST_SENSOR.clear()
    LATEST_SENSOR.update({
        "distance": distance,
        "battery_voltage": battery,
    })

    # -- 4. Update motor state (Source of Truth Logic) ----------------
    #    To prevent "ghosting" where the mode flips back to Manual due to
    #    stale packets or network latency, we make the Django Backend the
    #    absolute authority for the MOTOR_MODE.
    #    The sensor's reported mode is IGNORED for state management.
    
    grace_period = 5.0
    now_epoch = time.time()
    last_change = MOTOR_MODE_CHANGE_TIME.get("timestamp", 0)

    # Always use the Backend's mode as the master mode
    motor_mode = MOTOR_STATE["MOTOR_MODE"]

    if (now_epoch - last_change) > grace_period:
        # Outside grace period: sync the actual motor ON/OFF status
        MOTOR_STATE["MOTOR_MANUAL_STATUS"] = motor_status
    else:
        # Inside grace period: keep the local intended status to prevent flickering
        motor_status = MOTOR_STATE["MOTOR_MANUAL_STATUS"]

    # -- 5. Always sync LATEST_INPUT with what the sensor has stored ---
    #    This ensures the dashboard reflects the sensor's actual config.
    #    When the user submits new values, the sensor processes them and
    #    sends back updated Total_height / Total_Volume in its next packet.
    if sensor_height > 0:
        LATEST_INPUT["total_height"] = sensor_height
        LATEST_INPUT["total_volume"] = sensor_volume

    # -- 6. Use sensor's OWN calculations (Percentage, Filled_water_in_volume)
    #    The sensor computes these internally; we just pass them through.
    sensor_pct   = float(_get(data, "Percentage", "percentage", "PERCENTAGE", default=0))
    sensor_fill  = float(_get(data, "Filled_water_in_volume", "filled_water_in_volume",
                                "FILLED_WATER_IN_VOLUME", default=0))

    now_local = timezone.localtime(timezone.now())

    LATEST_CALCULATED.clear()
    LATEST_CALCULATED.update({
        "PERCENTAGE": round(sensor_pct, 2),
        "FILLED_WATER_IN_VOLUME": round(sensor_fill, 2),
        "MOTOR_STATUS": motor_status,
        "MOTOR_MODE": motor_mode,
        "BATTERY_VOLTAGE": round(battery, 2),
        "DISTANCE": round(distance, 2),
        "TOTAL_HEIGHT": sensor_height,
        "TOTAL_VOLUME": sensor_volume,
        "LAST_UPDATED": now_local.strftime("%Y-%m-%d %H:%M:%S"),
    })

    print("[OK] SENSOR DATA STORED:", LATEST_CALCULATED)

    # Append to in-memory ring buffer for real-time charting
    HISTORY_BUFFER.append({
        "timestamp": now_local.strftime("%Y-%m-%d %H:%M:%S"),
        "percentage": round(sensor_pct, 2),
        "filled_water_in_volume": round(sensor_fill, 2),
        "distance": round(distance, 2),
        "battery_voltage": round(battery, 2),
        "motor_mode": motor_mode,
        "motor_status": motor_status,
    })

    print("[OK] Sensor data processed")


def on_disconnect(client, userdata, rc):
    print("[WARN] MQTT disconnected | rc =", rc)
