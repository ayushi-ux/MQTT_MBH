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
]