"""
Periodic data-logging scheduler.

Uses APScheduler's BackgroundScheduler to save a WaterReading row every
5 minutes.  The scheduler is started once from MqttAppConfig.ready().
"""

import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from mqtt_app.services.state import DEVICES_STATE

logger = logging.getLogger(__name__)

_scheduler = None
LOG_INTERVAL_MINUTES = 5


def _log_reading():
    """Save the current sensor snapshot to the database for all active devices."""
    # Import model here to avoid AppRegistryNotReady
    from mqtt_app.models import WaterReading, Device
    from mqtt_app.services.state import DEVICES_STATE

    now = timezone.now()

    for mac_address, state in list(DEVICES_STATE.items()):
        calc = dict(state.get("LATEST_CALCULATED", {}))
        motor = dict(state.get("MOTOR_STATE", {}))

        # Skip if no sensor data has arrived yet for this device
        if not calc or calc.get("PERCENTAGE") is None:
            continue

        recent_cutoff = now - timedelta(minutes=LOG_INTERVAL_MINUTES)

        try:
            device = Device.objects.filter(mac_address=mac_address).first()
        except Exception:
            device = None

        # Guard against duplicate scheduler instances/processes for this device.
        latest = WaterReading.objects.filter(device=device).order_by("-created_at").only("created_at").first()
        if latest and latest.created_at >= recent_cutoff:
            logger.info(
                "[Scheduler] Skipping duplicate log for device %s — latest row is within the last %s minutes",
                mac_address,
                LOG_INTERVAL_MINUTES,
            )
            continue

        try:
            WaterReading.objects.create(
                device=device,
                total_height=calc.get("TOTAL_HEIGHT", 0),
                total_volume=calc.get("TOTAL_VOLUME", 0),
                distance=calc.get("DISTANCE", 0),
                percentage=calc.get("PERCENTAGE", 0),
                filled_water_in_volume=calc.get("FILLED_WATER_IN_VOLUME", 0),
                battery_voltage=calc.get("BATTERY_VOLTAGE", 0),
                motor_mode=motor.get("MOTOR_MODE", 0),
                motor_status=motor.get("MOTOR_MANUAL_STATUS", 0),
            )
            logger.info("[Scheduler] ✅ Reading logged to DB for device %s", mac_address)
        except Exception as exc:
            logger.error("[Scheduler] ❌ Failed to log reading for device %s: %s", mac_address, exc)

    # Optionally prune entries older than 7 days
    try:
        cutoff = now - timedelta(days=7)
        deleted, _ = WaterReading.objects.filter(created_at__lt=cutoff).delete()
        if deleted:
            logger.info("[Scheduler] 🗑  Pruned %d old readings", deleted)
    except Exception as exc:
        logger.warning("[Scheduler] Prune failed: %s", exc)



def start_scheduler():
    """Start the background scheduler (idempotent)."""
    global _scheduler
    if _scheduler is not None:
        return

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        _log_reading,
        trigger="cron",
        minute="*/5",
        second=0,
        id="log_sensor_reading",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    logger.info("[Scheduler] 🚀 Started — logging at exact 5-minute marks")
