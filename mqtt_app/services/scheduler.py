"""
Periodic data-logging scheduler.

Uses APScheduler's BackgroundScheduler to save a WaterReading row every
5 minutes.  The scheduler is started once from MqttAppConfig.ready().
"""

import logging
from datetime import timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

from mqtt_app.services.state import LATEST_CALCULATED, MOTOR_STATE

logger = logging.getLogger(__name__)

_scheduler = None
LOG_INTERVAL_MINUTES = 5


def _log_reading():
    """Save the current sensor snapshot to the database."""
    # Import model here to avoid AppRegistryNotReady
    from mqtt_app.models import WaterReading

    calc = dict(LATEST_CALCULATED)
    motor = dict(MOTOR_STATE)

    # Skip if no sensor data has arrived yet
    if not calc or calc.get("PERCENTAGE") is None:
        logger.info("[Scheduler] No sensor data yet — skipping log.")
        return

    now = timezone.now()
    recent_cutoff = now - timedelta(minutes=LOG_INTERVAL_MINUTES)

    # Guard against duplicate scheduler instances/processes.
    latest = WaterReading.objects.order_by("-created_at").only("created_at").first()
    if latest and latest.created_at >= recent_cutoff:
        logger.info(
            "[Scheduler] Skipping duplicate log — latest row is within the last %s minutes",
            LOG_INTERVAL_MINUTES,
        )
        return

    try:
        WaterReading.objects.create(
            total_height=calc.get("TOTAL_HEIGHT", 0),
            total_volume=calc.get("TOTAL_VOLUME", 0),
            distance=calc.get("DISTANCE", 0),
            percentage=calc.get("PERCENTAGE", 0),
            filled_water_in_volume=calc.get("FILLED_WATER_IN_VOLUME", 0),
            battery_voltage=calc.get("BATTERY_VOLTAGE", 0),
            motor_mode=motor.get("MOTOR_MODE", 0),
            motor_status=motor.get("MOTOR_MANUAL_STATUS", 0),
        )
        logger.info("[Scheduler] ✅ Reading logged to DB")
    except Exception as exc:
        logger.error("[Scheduler] ❌ Failed to log reading: %s", exc)

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
