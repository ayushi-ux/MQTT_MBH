from django.urls import path
from .views import (
    dashboard,
    get_motor_state,
    motor_auto,
    motor_control,
    send_input,
    get_calculated,
    get_input,
    get_history,
    get_logs,
    export_csv,
    get_live_history,
    register_device,
    list_devices,
    get_json_keys,
    send_wifi_credentials,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),

    # ✅ EXISTING API ROUTES (unchanged)
    path("api/send-input/", send_input),
    path("api/calculated/", get_calculated),
    path("api/input/", get_input),
    path("api/motor-control/", motor_control),
    path("api/motor-auto/", motor_auto),
    path("api/motor-state/", get_motor_state),

    # ✅ NEW — History, Logs, CSV, Live buffer
    path("api/history/", get_history),
    path("api/logs/", get_logs),
    path("api/export-csv/", export_csv),
    path("api/live-history/", get_live_history),

    # ✅ NEW — Device registration
    path("api/register-device/", register_device),
    path("api/list-devices/", list_devices),
    path("api/json-keys/", get_json_keys),
    path("api/send-wifi/", send_wifi_credentials),
]