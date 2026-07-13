import csv
import json
import time
from datetime import timedelta

from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from mqtt_app.mqtt.client import get_mqtt_client
from mqtt_app.mqtt.topics import MQTT_TOPIC, get_topic_for_mac
from mqtt_app.services.state import get_device_state
from mqtt_app.services.water_logic import calculate
from mqtt_app.mqtt.keys import OUTGOING_KEYS, COMMAND_IDS, build_command


def dashboard(request):
    return render(request, "dashboard.html")


# ── NEW DEVICE REGISTRATION AND CONFIGURATION ─────────────────────────────


@csrf_exempt
def register_device(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)
    
    data = json.loads(request.body)
    mac = data.get("mac_address")
    serial = data.get("serial_number")
    name = data.get("device_name", "Water Tank")
    height = float(data.get("total_height", 3.0))
    volume = float(data.get("total_volume", 1000.0))
    min_pct = float(data.get("min_percentage", 20.0))
    max_pct = float(data.get("max_percentage", 90.0))
    deep_sleep = int(data.get("deep_sleep", 0))
    sensor_interval = int(data.get("sensor_interval", 5000))
    sleep_interval = int(data.get("sleep_interval", 300))

    if not mac:
        return JsonResponse({"error": "mac_address is required"}, status=400)

    from mqtt_app.models import Device
    device, created = Device.objects.update_or_create(
        mac_address=mac,
        defaults={
            "serial_number": serial,
            "device_name": name,
            "total_height": height,
            "total_volume": volume,
            "min_percentage": min_pct,
            "max_percentage": max_pct,
            "deep_sleep": deep_sleep,
            "sensor_interval": sensor_interval,
            "sleep_interval": sleep_interval,
        }
    )

    # Initialize and pre-populate state so UI reflects it immediately
    state = get_device_state(mac)
    state["LATEST_INPUT"]["total_height"] = height
    state["LATEST_INPUT"]["total_volume"] = volume
    state["LATEST_INPUT"]["min_percentage"] = min_pct
    state["LATEST_INPUT"]["max_percentage"] = max_pct
    state["LATEST_INPUT"]["deep_sleep"] = deep_sleep
    state["LATEST_INPUT"]["sensor_interval"] = sensor_interval
    state["LATEST_INPUT"]["sleep_interval"] = sleep_interval
    state["LATEST_CALCULATED"]["TOTAL_HEIGHT"] = height
    state["LATEST_CALCULATED"]["TOTAL_VOLUME"] = volume
    state["LATEST_CALCULATED"]["MIN_PERCENTAGE"] = min_pct
    state["LATEST_CALCULATED"]["MAX_PERCENTAGE"] = max_pct
    state["LATEST_CALCULATED"]["DEEP_SLEEP"] = deep_sleep
    state["LATEST_CALCULATED"]["SENSOR_INTERVAL"] = sensor_interval
    state["LATEST_CALCULATED"]["SLEEP_INTERVAL"] = sleep_interval
    state["LATEST_CALCULATED"]["LAST_UPDATED"] = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
    state["LATEST_CALCULATED"]["LAST_UPDATED_EPOCH"] = time.time()

    # Publish config to ESP32 via MQTT using wrapper format
    try:
        client = get_mqtt_client()
        payload = {
            OUTGOING_KEYS["total_height"]: height,
            OUTGOING_KEYS["total_volume"]: volume,
            OUTGOING_KEYS["min_percentage"]: min_pct,
            OUTGOING_KEYS["max_percentage"]: max_pct,
            OUTGOING_KEYS["motor_mode"]: 0,
            OUTGOING_KEYS["motor_status"]: 0,
            OUTGOING_KEYS["deep_sleep"]: deep_sleep,
            OUTGOING_KEYS["sensor_interval"]: sensor_interval,
            OUTGOING_KEYS["sleep_interval"]: sleep_interval,
        }
        cmd = build_command(COMMAND_IDS["config"], mac, serial, payload)
        cmd["_source"] = "django"
        topic = get_topic_for_mac(mac)
        client.publish(topic, json.dumps(cmd))
        
        # Dynamically subscribe to this device's telemetry topic
        try:
            client.subscribe(topic)
            print(f"[OK] Dynamically subscribed to new device topic: {topic}")
        except Exception as sub_err:
            print("[WARN] Failed to dynamically subscribe to new device topic:", sub_err)

        print(f"\n{'='*50}")
        print(f"[REGISTER] Device registered & config published")
        print(f"  MAC : {mac}")
        print(f"  SN  : {serial}")
        print(f"{'='*50}\n")
    except Exception as e:
        print("[WARN] Failed to publish new device config to MQTT:", e)

    return JsonResponse({"status": "device registered", "created": created, "mac_address": mac})


def list_devices(request):
    from mqtt_app.models import Device
    devices = list(Device.objects.all().values(
        "mac_address", "serial_number", "device_name", "total_height", "total_volume", 
        "min_percentage", "max_percentage", "deep_sleep", "sensor_interval", "sleep_interval"
    ))
    return JsonResponse({"devices": devices})


# ── INPUT (height + volume) → sensor ────────────────────


@csrf_exempt
def send_input(request):
    data = json.loads(request.body)
    height = float(data["total_height"])
    volume = float(data["total_volume"])
    min_pct = float(data.get("min_percentage", 20.0))
    max_pct = float(data.get("max_percentage", 90.0))
    deep_sleep = int(data.get("deep_sleep", 0))
    sensor_interval = int(data.get("sensor_interval", 5000))
    sleep_interval = int(data.get("sleep_interval", 300))
    mac = data.get("mac_address")

    state = get_device_state(mac)
    LATEST_INPUT = state["LATEST_INPUT"]
    LATEST_SENSOR = state["LATEST_SENSOR"]
    LATEST_CALCULATED = state["LATEST_CALCULATED"]
    MOTOR_STATE = state["MOTOR_STATE"]

    # Store values locally in cache
    LATEST_INPUT["total_height"] = height
    LATEST_INPUT["total_volume"] = volume
    LATEST_INPUT["min_percentage"] = min_pct
    LATEST_INPUT["max_percentage"] = max_pct
    LATEST_INPUT["deep_sleep"] = deep_sleep
    LATEST_INPUT["sensor_interval"] = sensor_interval
    LATEST_INPUT["sleep_interval"] = sleep_interval

    # Recalculate immediately using current sensor distance
    dist = LATEST_SENSOR.get("distance")
    if dist is not None:
        result = calculate(
            total_height=height,
            total_volume=volume,
            distance=dist,
            battery_voltage=LATEST_SENSOR.get("battery_voltage", 0),
        )
        result["MIN_PERCENTAGE"] = min_pct
        result["MAX_PERCENTAGE"] = max_pct
        result["DEEP_SLEEP"] = deep_sleep
        result["SENSOR_INTERVAL"] = sensor_interval
        result["SLEEP_INTERVAL"] = sleep_interval
        result["MOTOR_MODE"] = MOTOR_STATE.get("MOTOR_MODE", 0)
        result["MOTOR_STATUS"] = MOTOR_STATE.get("MOTOR_MANUAL_STATUS", 0)
        result["LAST_UPDATED"] = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        result["LAST_UPDATED_EPOCH"] = time.time()
        result["MAC_ADDRESS"] = mac or "default"
        LATEST_CALCULATED.clear()
        LATEST_CALCULATED.update(result)

    # Sync configuration to Device DB Model + get serial number
    serial_number = None
    if mac and mac != "default":
        try:
            from mqtt_app.models import Device
            device = Device.objects.filter(mac_address=mac).first()
            if device:
                serial_number = device.serial_number
                device.total_height = height
                device.total_volume = volume
                device.min_percentage = min_pct
                device.max_percentage = max_pct
                device.deep_sleep = deep_sleep
                device.sensor_interval = sensor_interval
                device.sleep_interval = sleep_interval
                device.save()
        except Exception as db_err:
            print("[WARN] Failed to sync update to Device database:", db_err)

    # ── Always publish full config via MQTT ──
    client = get_mqtt_client()
    motor_mode = MOTOR_STATE.get("MOTOR_MODE", 0)
    motor_status_val = MOTOR_STATE.get("MOTOR_MANUAL_STATUS", 0)
    payload = {
        OUTGOING_KEYS["total_height"]: height,
        OUTGOING_KEYS["total_volume"]: volume,
        OUTGOING_KEYS["min_percentage"]: min_pct,
        OUTGOING_KEYS["max_percentage"]: max_pct,
        OUTGOING_KEYS["motor_mode"]: motor_mode,
        OUTGOING_KEYS["motor_status"]: motor_status_val,
        OUTGOING_KEYS["deep_sleep"]: deep_sleep,
        OUTGOING_KEYS["sensor_interval"]: sensor_interval,
        OUTGOING_KEYS["sleep_interval"]: sleep_interval,
    }
    cmd = build_command(COMMAND_IDS["config"], mac, serial_number, payload)
    cmd["_source"] = "django"
    client.publish(get_topic_for_mac(mac), json.dumps(cmd))
    print(f"\n{'='*50}")
    print(f"[SAVE CONFIG] Configuration published to MQTT")
    print(f"  MAC : {mac}")
    print(f"  SN  : {serial_number}")
    print(f"  Data: {payload}")
    print(f"{'='*50}\n")

    return JsonResponse({"status": "sent"})


# ── POLL endpoints ──────────────────────────────────────


def get_calculated(request):
    mac = request.GET.get("mac")
    state = get_device_state(mac)
    return JsonResponse(state["LATEST_CALCULATED"])


def get_input(request):
    mac = request.GET.get("mac")
    state = get_device_state(mac)
    return JsonResponse(state["LATEST_INPUT"])


# ── MOTOR CONTROL → sensor ──────────────────────────────
#    ⚠  THIS LOGIC MUST NOT BE CHANGED — it is the core
#       of the project.


@csrf_exempt
def motor_control(request):
    data = json.loads(request.body)
    status = int(data["status"])
    mac = data.get("mac_address")

    state = get_device_state(mac)
    MOTOR_STATE = state["MOTOR_STATE"]
    MOTOR_MODE_CHANGE_TIME = state["MOTOR_MODE_CHANGE_TIME"]

    # Update locally so dashboard reflects it instantly
    MOTOR_STATE["MOTOR_MODE"] = 1          # manual
    MOTOR_STATE["MOTOR_MANUAL_STATUS"] = status
    MOTOR_STATE["_auto_locked"] = False     # Allow ESP32 to sync mode again
    MOTOR_MODE_CHANGE_TIME["timestamp"] = time.time()

    # Look up serial number for wrapper envelope
    serial_number = None
    if mac:
        try:
            from mqtt_app.models import Device
            dev = Device.objects.filter(mac_address=mac).first()
            if dev:
                serial_number = dev.serial_number
        except Exception:
            pass

    # Publish using wrapper format
    client = get_mqtt_client()
    payload = {
        OUTGOING_KEYS["motor_mode"]: 1,
        OUTGOING_KEYS["motor_status"]: status,
    }
    cmd = build_command(COMMAND_IDS["config"], mac, serial_number, payload)
    cmd["_source"] = "django"
    client.publish(get_topic_for_mac(mac), json.dumps(cmd))

    return JsonResponse({"status": "motor command sent"})


@csrf_exempt
def motor_auto(request):
    # Support loading parameters from request body or GET param
    mac = None
    if request.body:
        try:
            data = json.loads(request.body)
            mac = data.get("mac_address")
        except Exception:
            pass
    if not mac:
        mac = request.GET.get("mac")

    state = get_device_state(mac)
    MOTOR_STATE = state["MOTOR_STATE"]
    MOTOR_MODE_CHANGE_TIME = state["MOTOR_MODE_CHANGE_TIME"]

    # Update locally — clear manual status to prevent ghost-firing
    MOTOR_STATE["MOTOR_MODE"] = 0
    MOTOR_STATE["MOTOR_MANUAL_STATUS"] = 0  # Reset manual command state
    MOTOR_STATE["_auto_locked"] = False      # Prevent ESP32 from overriding back to manual
    MOTOR_MODE_CHANGE_TIME["timestamp"] = time.time()

    # Look up serial number for wrapper envelope
    serial_number = None
    if mac:
        try:
            from mqtt_app.models import Device
            dev = Device.objects.filter(mac_address=mac).first()
            if dev:
                serial_number = dev.serial_number
        except Exception:
            pass

    # Publish using wrapper format
    client = get_mqtt_client()
    payload = {
        OUTGOING_KEYS["motor_mode"]: 0,
        OUTGOING_KEYS["motor_status"]: 0,
    }
    cmd = build_command(COMMAND_IDS["config"], mac, serial_number, payload)
    cmd["_source"] = "django"
    client.publish(get_topic_for_mac(mac), json.dumps(cmd))

    return JsonResponse({"status": "auto mode enabled"})


def get_motor_state(request):
    mac = request.GET.get("mac")
    state = get_device_state(mac)
    return JsonResponse(state["MOTOR_STATE"])


# ═══════════════════════════════════════════════════════════
#  History, Logs, CSV export, Live buffer
# ═══════════════════════════════════════════════════════════


def get_history(request):
    """Return historical data for Chart.js graphs.

    Query params:
        hours  – 1, 6, or 24 (default 1)
        mac    – Device MAC address
    """
    from mqtt_app.models import WaterReading, Device

    mac = request.GET.get("mac")
    try:
        device = Device.objects.filter(mac_address=mac).first() if mac else Device.objects.first()
    except Exception:
        device = None

    hours = int(request.GET.get("hours", 1))
    since = timezone.now() - timedelta(hours=hours)

    readings = (
        WaterReading.objects
        .filter(device=device, created_at__gte=since)
        .order_by("created_at")
        .values(
            "created_at", "percentage", "filled_water_in_volume",
            "distance", "battery_voltage", "motor_mode", "motor_status",
        )
    )

    labels = []
    timestamps = []  # Full timestamps for client-side time filtering
    water_level = []
    battery_voltage = []
    distance = []
    motor_status = []
    motor_events = []

    prev_motor = None
    for r in readings:
        ts = timezone.localtime(r["created_at"]).strftime("%H:%M")
        full_ts = timezone.localtime(r["created_at"]).strftime("%Y-%m-%d %H:%M:%S")
        labels.append(ts)
        timestamps.append(full_ts)
        water_level.append(r["percentage"])
        battery_voltage.append(r["battery_voltage"])
        distance.append(r["distance"])
        motor_status.append(r["motor_status"])

        # Detect motor state transitions for annotation markers
        if prev_motor is not None and r["motor_status"] != prev_motor:
            motor_events.append({"time": ts, "status": r["motor_status"]})
        prev_motor = r["motor_status"]

    return JsonResponse({
        "labels": labels,
        "timestamps": timestamps,
        "water_level": water_level,
        "battery_voltage": battery_voltage,
        "distance": distance,
        "motor_status": motor_status,
        "motor_events": motor_events,
    })


def get_logs(request):
    """Return paginated log entries for the table.

    Query params:
        page  – 1-based (default 1)
        size  – items per page (default 20, max 100)
        mac   – Device MAC address
    """
    from mqtt_app.models import WaterReading, Device

    mac = request.GET.get("mac")
    try:
        device = Device.objects.filter(mac_address=mac).first() if mac else Device.objects.first()
    except Exception:
        device = None

    page = max(1, int(request.GET.get("page", 1)))
    size = min(100, max(1, int(request.GET.get("size", 20))))

    qs = WaterReading.objects.filter(device=device).order_by("-created_at")
    total = qs.count()
    start = (page - 1) * size
    entries = qs[start : start + size]

    rows = []
    for e in entries:
        rows.append({
            "timestamp": timezone.localtime(e.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            "percentage": e.percentage,
            "filled_volume": e.filled_water_in_volume,
            "distance": e.distance,
            "battery_voltage": e.battery_voltage,
            "motor_mode": "AUTO" if e.motor_mode == 0 else "MANUAL",
            "motor_status": "ON" if e.motor_status == 1 else "OFF",
        })

    return JsonResponse({
        "page": page,
        "size": size,
        "total": total,
        "total_pages": (total + size - 1) // size,
        "rows": rows,
    })


def export_csv(request):
    """Stream all WaterReading rows for a device as a downloadable CSV."""
    from mqtt_app.models import WaterReading, Device

    mac = request.GET.get("mac")
    try:
        device = Device.objects.filter(mac_address=mac).first() if mac else Device.objects.first()
    except Exception:
        device = None

    readings = WaterReading.objects.filter(device=device).order_by("-created_at").iterator(chunk_size=500)

    class Echo:
        """Pseudo-buffer that csv.writer can write to."""
        def write(self, value):
            return value

    def rows():
        writer = csv.writer(Echo())
        yield writer.writerow([
            "Timestamp", "Water Level (%)", "Filled Volume (L)",
            "Distance (m)", "Battery (V)", "Motor Mode", "Motor Status",
        ])
        for r in readings:
            yield writer.writerow([
                timezone.localtime(r.created_at).strftime("%Y-%m-%d %H:%M:%S"),
                r.percentage,
                r.filled_water_in_volume,
                r.distance,
                r.battery_voltage,
                "AUTO" if r.motor_mode == 0 else "MANUAL",
                "ON" if r.motor_status == 1 else "OFF",
            ])

    response = StreamingHttpResponse(rows(), content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="water_tank_logs.csv"'
    return response


def get_live_history(request):
    """Return the in-memory ring buffer for real-time charting."""
    mac = request.GET.get("mac")
    state = get_device_state(mac)
    data = list(state["HISTORY_BUFFER"])
    return JsonResponse({"entries": data})


def get_json_keys(request):
    """Return keys configuration to client-side for BLE pairing/scanning alignment."""
    from mqtt_app.mqtt.keys import BLE_KEYS, INCOMING_KEYS, OUTGOING_KEYS
    return JsonResponse({
        "ble": BLE_KEYS,
        "incoming": INCOMING_KEYS,
        "outgoing": OUTGOING_KEYS
    })


@csrf_exempt
def send_wifi_credentials(request):
    """Publish WiFi credentials to MQTT using command_id 49 wrapper format."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    data = json.loads(request.body)
    mac = data.get("mac_address")
    ssid = data.get("ssid")
    password = data.get("password")

    if not mac or not ssid:
        return JsonResponse({"error": "mac_address and ssid are required"}, status=400)

    # Look up serial number for wrapper envelope
    serial_number = None
    try:
        from mqtt_app.models import Device
        dev = Device.objects.filter(mac_address=mac).first()
        if dev:
            serial_number = dev.serial_number
    except Exception:
        pass

    # Publish WiFi credentials using command_id 49 wrapper format
    try:
        client = get_mqtt_client()
        payload = {
            "ssid": ssid,
            "password": password,
        }
        cmd = build_command(COMMAND_IDS["wifi"], mac, serial_number, payload)
        cmd["_source"] = "django"
        client.publish(get_topic_for_mac(mac), json.dumps(cmd))
        print(f"\n{'='*50}")
        print(f"[WIFI] WiFi credentials published")
        print(f"  MAC : {mac}")
        print(f"  SN  : {serial_number}")
        print(f"  SSID: {ssid}")
        print(f"{'='*50}\n")
    except Exception as e:
        print("[WARN] Failed to publish WiFi credentials to MQTT:", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"status": "wifi credentials sent", "mac_address": mac})
