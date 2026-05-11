from django.apps import AppConfig
import os


class MqttAppConfig(AppConfig):
    name = "mqtt_app"

    def ready(self):
        # Only start MQTT and Scheduler in the main process (RUN_MAIN=true)
        # to avoid double-initialization in the Django reloader.
        if os.environ.get("RUN_MAIN") == "true":
            from .mqtt.client import get_mqtt_client
            get_mqtt_client()

            from .services.scheduler import start_scheduler
            start_scheduler()
