MQTT_TOPIC = "factory/esp32/esp32_1/water_management_system"

def get_topic_for_mac(mac):
    if not mac or mac == "default":
        return "factory/esp32/esp32_1/water_management_system"
    return f"factory/esp32/{mac}/water_management_system"
