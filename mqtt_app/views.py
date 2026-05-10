import csv
import json
import time
from datetime import timedelta

from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from mqtt_app.mqtt.client import get_mqtt_client
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


def dashboard(request):
    return render(request, "dashboard.html")


# ── INPUT (height + volume) → sensor ────────────────────


@csrf_exempt
def send_input(request):
    data = json.loads(request.body)
    height = float(data["total_height"])
    volume = float(data["total_volume"])

    # Store locally
    LATEST_INPUT["total_height"] = height
    LATEST_INPUT["total_volume"] = volume

    # Recalculate immediately using current sensor distance
    dist = LATEST_SENSOR.get("distance")
    if dist is not None:
        result = calculate(
            total_height=height,
            total_volume=volume,
            distance=dist,
            battery_voltage=LATEST_SENSOR.get("battery_voltage", 0),
        )
        result["MOTOR_MODE"] = MOTOR_STATE.get("MOTOR_MODE", 0)
        result["MOTOR_STATUS"] = MOTOR_STATE.get("MOTOR_MANUAL_STATUS", 0)
        result["LAST_UPDATED"] = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M:%S")
        LATEST_CALCULATED.clear()
        LATEST_CALCULATED.update(result)

    # Publish in the format the ESP32 expects
    client = get_mqtt_client()
    client.publish(
        MQTT_TOPIC,
        json.dumps({
            "Total_height": str(height),
            "Total_volume": str(volume),
            "_source": "django",
        })
    )

    return JsonResponse({"status": "sent"})


# ── POLL endpoints ──────────────────────────────────────


def get_calculated(request):
    return JsonResponse(LATEST_CALCULATED)


def get_input(request):
    return JsonResponse(LATEST_INPUT)


# ── MOTOR CONTROL → sensor ──────────────────────────────
#    ⚠  THIS LOGIC MUST NOT BE CHANGED — it is the core
#       of the project.


@csrf_exempt
def motor_control(request):
    data = json.loads(request.body)
    status = int(data["status"])

    # Update locally so dashboard reflects it instantly
    MOTOR_STATE["MOTOR_MODE"] = 1          # manual
    MOTOR_STATE["MOTOR_MANUAL_STATUS"] = status
    MOTOR_STATE["_auto_locked"] = False     # Allow ESP32 to sync mode again
    MOTOR_MODE_CHANGE_TIME["timestamp"] = time.time()

    # Publish in the format the ESP32 expects:
    #   {"Motor_mode": "1", "Motor_status": "1"}
    client = get_mqtt_client()
    client.publish(
        MQTT_TOPIC,
        json.dumps({
            "Motor_mode": str(1),
            "Motor_status": str(status),
            "_source": "django",
        })
    )

    return JsonResponse({"status": "motor command sent"})


@csrf_exempt
def motor_auto(request):
    # Update locally — clear manual status to prevent ghost-firing
    MOTOR_STATE["MOTOR_MODE"] = 0
    MOTOR_STATE["MOTOR_MANUAL_STATUS"] = 0  # Reset manual command state
    MOTOR_STATE["_auto_locked"] = False      # Prevent ESP32 from overriding back to manual
    MOTOR_MODE_CHANGE_TIME["timestamp"] = time.time()

    # Publish to ESP32
    client = get_mqtt_client()
    client.publish(
        MQTT_TOPIC,
        json.dumps({
            "Motor_mode": str(0),
            "Motor_status": str(0),
            "_source": "django",
        })
    )

    return JsonResponse({"status": "auto mode enabled"})


def get_motor_state(request):
    return JsonResponse(MOTOR_STATE)


# ═══════════════════════════════════════════════════════════
#  NEW  — History, Logs, CSV export, Live buffer
# ═══════════════════════════════════════════════════════════


def get_history(request):
    """Return historical data for Chart.js graphs.

    Query params:
        hours  – 1, 6, or 24 (default 1)
    """
    from mqtt_app.models import WaterReading

    hours = int(request.GET.get("hours", 1))
    since = timezone.now() - timedelta(hours=hours)

    readings = (
        WaterReading.objects
        .filter(created_at__gte=since)
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
    """
    from mqtt_app.models import WaterReading

    page = max(1, int(request.GET.get("page", 1)))
    size = min(100, max(1, int(request.GET.get("size", 20))))

    qs = WaterReading.objects.order_by("-created_at")
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
    """Stream all WaterReading rows as a downloadable CSV."""
    from mqtt_app.models import WaterReading

    readings = WaterReading.objects.order_by("-created_at").iterator(chunk_size=500)

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
    data = list(HISTORY_BUFFER)
    return JsonResponse({"entries": data})
