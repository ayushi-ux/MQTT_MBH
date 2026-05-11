# pyrefly: ignore [missing-import]
import paho.mqtt.client as mqtt

_client = None


def get_mqtt_client():
    global _client
    if _client:
        return _client

    # paho-mqtt 2.x requires CallbackAPIVersion
    try:
        _client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    except (AttributeError, TypeError):
        _client = mqtt.Client()

    # Attach callbacks BEFORE connecting
    from mqtt_app.mqtt.callbacks import on_connect, on_message, on_disconnect
    _client.on_connect = on_connect
    _client.on_message = on_message
    _client.on_disconnect = on_disconnect

    _client.connect("broker.emqx.io", 1883, 60)
    _client.loop_start()

    return _client
