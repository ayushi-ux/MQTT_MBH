import json
import time

from django.utils import timezone

from mqtt_app.mqtt.topics import MQTT_TOPIC, get_topic_for_mac
from mqtt_app.services.state import get_device_state
from mqtt_app.services.water_logic import calculate
from mqtt_app.mqtt.keys import get_sensor_value, INCOMING_KEYS, OUTGOING_KEYS, COMMAND_IDS, build_command


# -- MQTT callbacks ----------------------------------------------------


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[OK] MQTT connected")
        # 1. Subscribe to the default topic
        client.subscribe(MQTT_TOPIC)
        print("[OK] Subscribed to default topic:", MQTT_TOPIC)

        # 2. Subscribe to all registered devices in the database
        try:
            from mqtt_app.models import Device
            devices = Device.objects.all()
            for dev in devices:
                topic = get_topic_for_mac(dev.mac_address)
                client.subscribe(topic)
                print(f"[OK] Subscribed to registered device topic: {topic}")
        except Exception as e:
            print("[WARN] Failed to load devices for MQTT subscription:", e)
    else:
        print("[ERR] MQTT connection failed | rc =", rc)


def on_message(client, userdata, msg):
    try:
        raw_data = json.loads(msg.payload.decode())
    except Exception:
        print("[ERR] Invalid JSON on", msg.topic)
        return

    # -- 1. Ignore messages that WE published -------------------------
    #    Every message Django publishes carries "_source": "django".
    #    The ESP32 ignores unknown keys, so this is safe.
    if raw_data.get("_source") == "django":
        return

    # -- 1b. Unwrap command envelope if present -----------------------
    #    If the message uses the wrapper format:
    #    {"command_id": N, "command_type": 1, "sn": "...", "mac": "...", "payload": {...}}
    #    Extract mac/sn from top level and flatten payload into data dict.
    if "payload" in raw_data and isinstance(raw_data["payload"], dict):
        data = dict(raw_data["payload"])
        # Carry top-level mac and sn into data so get_sensor_value can find them
        if "mac" in raw_data and "mac" not in data:
            data["mac"] = raw_data["mac"]
        if "sn" in raw_data and "sn" not in data:
            data["sn"] = raw_data["sn"]
        print(f"[MQTT] Unwrapped command_id={raw_data.get('command_id')} payload")
    else:
        data = raw_data

    print("[MQTT] SENSOR DATA:", data)

    # -- 2. Detect ESP32 sensor data ----------------------------------
    #    ESP32 payload always contains a distance key.
    has_distance = any(k in data for k in INCOMING_KEYS.get("distance", ()))

    if not has_distance:
        print("[WARN] Message has no Distance key - ignored:", data)
        return

    try:
        distance = float(get_sensor_value(data, "distance", 0.0))
        battery  = float(get_sensor_value(data, "battery_voltage", 0.0))
        motor_mode   = int(float(get_sensor_value(data, "motor_mode", 0.0)))
        motor_status = int(float(get_sensor_value(data, "motor_status", 0.0)))

        sensor_height = float(get_sensor_value(data, "total_height", 0.0))
        sensor_volume = float(get_sensor_value(data, "total_volume", 0.0))
        
        sensor_pct = float(get_sensor_value(data, "percentage", 0.0))
        sensor_fill = float(get_sensor_value(data, "filled_water_in_volume", 0.0))
        
        sensor_min_pct = get_sensor_value(data, "min_percentage", None)
        sensor_max_pct = get_sensor_value(data, "max_percentage", None)
        sensor_min_pct = float(sensor_min_pct) if sensor_min_pct is not None else None
        sensor_max_pct = float(sensor_max_pct) if sensor_max_pct is not None else None

        sensor_deep_sleep = get_sensor_value(data, "deep_sleep", None)
        sensor_interval = get_sensor_value(data, "sensor_interval", None)
        sensor_sleep_interval = get_sensor_value(data, "sleep_interval", None)
        sensor_deep_sleep = int(float(sensor_deep_sleep)) if sensor_deep_sleep is not None else None
        sensor_interval = int(float(sensor_interval)) if sensor_interval is not None else None
        sensor_sleep_interval = int(float(sensor_sleep_interval)) if sensor_sleep_interval is not None else None
        
        # Diagnostics
        faults = int(float(get_sensor_value(data, "faults", 0.0)))
    except (ValueError, TypeError) as exc:
        print("[ERR] Bad sensor values:", exc)
        return


    # Extract MAC Address from topic first as it is 100% reliable, then fallback to payload
    topic_parts = msg.topic.split("/")
    mac_from_topic = topic_parts[2] if len(topic_parts) >= 3 else None

    mac_address = get_sensor_value(data, "mac_address", None)
    if not mac_address:
        mac_address = get_sensor_value(data, "mac", None)
    if not mac_address:
        mac_address = mac_from_topic
    if not mac_address:
        mac_address = "default"

    serial_number = get_sensor_value(data, "serial_number", None)
    if not serial_number:
        serial_number = get_sensor_value(data, "sn", None)
    
    # Auto-register/sync device in database
    try:
        from mqtt_app.models import Device
        device, created = Device.objects.get_or_create(
            mac_address=mac_address,
            defaults={
                "serial_number": serial_number,
                "total_height": sensor_height if sensor_height > 0 else 3.0,
                "total_volume": sensor_volume if sensor_volume > 0 else 1000.0,
                "min_percentage": sensor_min_pct if sensor_min_pct is not None else 20.0,
                "max_percentage": sensor_max_pct if sensor_max_pct is not None else 90.0,
                "deep_sleep": sensor_deep_sleep if sensor_deep_sleep is not None else 0,
                "sensor_interval": sensor_interval if sensor_interval is not None else 5000,
                "sleep_interval": sensor_sleep_interval if sensor_sleep_interval is not None else 300,
                "device_name": f"Tank {mac_address[-5:]}" if mac_address != "default" else "Default Tank"
            }
        )
        if not created:
            updated = False
            # Always sync serial_number from sensor to prevent stale values
            if serial_number and device.serial_number != serial_number:
                device.serial_number = serial_number
                updated = True
            if sensor_height > 0 and device.total_height != sensor_height:
                device.total_height = sensor_height
                updated = True
            if sensor_volume > 0 and device.total_volume != sensor_volume:
                device.total_volume = sensor_volume
                updated = True
            if sensor_min_pct is not None and device.min_percentage != sensor_min_pct:
                device.min_percentage = sensor_min_pct
                updated = True
            if sensor_max_pct is not None and device.max_percentage != sensor_max_pct:
                device.max_percentage = sensor_max_pct
                updated = True
            if sensor_deep_sleep is not None and device.deep_sleep != sensor_deep_sleep:
                device.deep_sleep = sensor_deep_sleep
                updated = True
            if sensor_interval is not None and device.sensor_interval != sensor_interval:
                device.sensor_interval = sensor_interval
                updated = True
            if sensor_sleep_interval is not None and device.sleep_interval != sensor_sleep_interval:
                device.sleep_interval = sensor_sleep_interval
                updated = True
            if updated:
                device.save()
        
        final_height = sensor_height if sensor_height > 0 else device.total_height
        final_volume = sensor_volume if sensor_volume > 0 else device.total_volume
        final_min_pct = sensor_min_pct if sensor_min_pct is not None else device.min_percentage
        final_max_pct = sensor_max_pct if sensor_max_pct is not None else device.max_percentage
        final_deep_sleep = sensor_deep_sleep if sensor_deep_sleep is not None else device.deep_sleep
        final_sensor_interval = sensor_interval if sensor_interval is not None else device.sensor_interval
        final_sleep_interval = sensor_sleep_interval if sensor_sleep_interval is not None else device.sleep_interval
    except Exception as db_exc:
        print("[ERR] Failed to sync device db model in MQTT callback:", db_exc)

    # Get device-specific in-memory states
    state = get_device_state(mac_address)
    LATEST_SENSOR = state["LATEST_SENSOR"]
    LATEST_INPUT = state["LATEST_INPUT"]
    LATEST_CALCULATED = state["LATEST_CALCULATED"]
    MOTOR_STATE = state["MOTOR_STATE"]
    MOTOR_MODE_CHANGE_TIME = state["MOTOR_MODE_CHANGE_TIME"]
    HISTORY_BUFFER = state["HISTORY_BUFFER"]

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

    if motor_mode == 0:  # AUTO MODE
        # Check thresholds to toggle pump
        if sensor_pct < final_min_pct:
            if MOTOR_STATE["MOTOR_MANUAL_STATUS"] != 1:
                print(f"[AUTO] Water level {sensor_pct}% below min {final_min_pct}%. Turning motor ON.")
                MOTOR_STATE["MOTOR_MANUAL_STATUS"] = 1
                
                # Publish start command to ESP32 using wrapper format
                try:
                    auto_payload = {
                        OUTGOING_KEYS["motor_mode"]: str(0),
                        OUTGOING_KEYS["motor_status"]: str(1),
                    }
                    cmd = build_command(COMMAND_IDS["config"], mac_address, serial_number, auto_payload)
                    cmd["_source"] = "django"
                    client.publish(get_topic_for_mac(mac_address), json.dumps(cmd))
                except Exception as pub_err:
                    print("[WARN] Auto motor start publish failed:", pub_err)
                    
        elif sensor_pct >= final_max_pct:
            if MOTOR_STATE["MOTOR_MANUAL_STATUS"] != 0:
                print(f"[AUTO] Water level {sensor_pct}% at/above max {final_max_pct}%. Turning motor OFF.")
                MOTOR_STATE["MOTOR_MANUAL_STATUS"] = 0
                
                # Publish stop command to ESP32 using wrapper format
                try:
                    auto_payload = {
                        OUTGOING_KEYS["motor_mode"]: str(0),
                        OUTGOING_KEYS["motor_status"]: str(0),
                    }
                    cmd = build_command(COMMAND_IDS["config"], mac_address, serial_number, auto_payload)
                    cmd["_source"] = "django"
                    client.publish(get_topic_for_mac(mac_address), json.dumps(cmd))
                except Exception as pub_err:
                    print("[WARN] Auto motor stop publish failed:", pub_err)

    if (now_epoch - last_change) > grace_period:
        # Outside grace period: sync the actual motor ON/OFF status
        MOTOR_STATE["MOTOR_MANUAL_STATUS"] = motor_status
    else:
        # Inside grace period: keep the local intended status to prevent flickering
        motor_status = MOTOR_STATE["MOTOR_MANUAL_STATUS"]

    # -- 5. Always sync LATEST_INPUT with what the sensor has stored ---
    #    This ensures the dashboard reflects the sensor's actual config.
    if sensor_height > 0:
        LATEST_INPUT["total_height"] = sensor_height
        LATEST_INPUT["total_volume"] = sensor_volume
    elif "total_height" not in LATEST_INPUT or LATEST_INPUT["total_height"] <= 0:
        LATEST_INPUT["total_height"] = final_height
        LATEST_INPUT["total_volume"] = final_volume
        
    LATEST_INPUT["min_percentage"] = final_min_pct
    LATEST_INPUT["max_percentage"] = final_max_pct
    LATEST_INPUT["deep_sleep"] = final_deep_sleep
    LATEST_INPUT["sensor_interval"] = final_sensor_interval
    LATEST_INPUT["sleep_interval"] = final_sleep_interval

    # -- 6. Use sensor's OWN calculations (Percentage, Filled_water_in_volume)

    now_local = timezone.localtime(timezone.now())

    LATEST_CALCULATED.clear()
    LATEST_CALCULATED.update({
        "PERCENTAGE": round(sensor_pct, 2),
        "FILLED_WATER_IN_VOLUME": round(sensor_fill, 2),
        "MOTOR_STATUS": motor_status,
        "MOTOR_MODE": motor_mode,
        "BATTERY_VOLTAGE": round(battery, 2),
        "DISTANCE": round(distance, 2),
        "TOTAL_HEIGHT": final_height,
        "TOTAL_VOLUME": final_volume,
        "MIN_PERCENTAGE": final_min_pct,
        "MAX_PERCENTAGE": final_max_pct,
        "DEEP_SLEEP": final_deep_sleep,
        "SENSOR_INTERVAL": final_sensor_interval,
        "SLEEP_INTERVAL": final_sleep_interval,
        "LAST_UPDATED": now_local.strftime("%Y-%m-%d %H:%M:%S"),
        "LAST_UPDATED_EPOCH": time.time(),
        "MAC_ADDRESS": mac_address,
        "FAULTS": faults,
    })

    print("[OK] SENSOR DATA STORED:", LATEST_CALCULATED)

    # Save a WaterReading row to database (throttled to at most once every 60 seconds per device)
    try:
        from mqtt_app.models import WaterReading
        recent_reading = WaterReading.objects.filter(device=device).order_by("-created_at").only("created_at").first()
        if not recent_reading or (timezone.now() - recent_reading.created_at).total_seconds() >= 60:
            WaterReading.objects.create(
                device=device,
                total_height=final_height,
                total_volume=final_volume,
                distance=round(distance, 2),
                percentage=round(sensor_pct, 2),
                filled_water_in_volume=round(sensor_fill, 2),
                battery_voltage=round(battery, 2),
                motor_mode=motor_mode,
                motor_status=motor_status,
                faults=faults,
            )
            print(f"[DB] Saved new WaterReading to database for MAC: {mac_address}")
    except Exception as db_err:
        print("[WARN] Failed to write WaterReading to database:", db_err)

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
