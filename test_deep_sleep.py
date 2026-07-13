import json
import time
import urllib.request
import paho.mqtt.client as mqtt

MAC = "84:1F:E8:2C:52:78"
TOPIC = "factory/esp32/esp32_1/water_management_system"

print("==================================================")
print("DEEP SLEEP CONFIGURATION INTEGRATION TEST")
print("==================================================")

# 1. Setup MQTT client to capture published configs
received_messages = []

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    data = json.loads(payload)
    if data.get("_source") == "django":
        print(f"   [MQTT EVENT] Captured command from Django: {payload}")
        received_messages.append(data)

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.emqx.io", 1883, 60)
client.subscribe(TOPIC)
client.loop_start()

time.sleep(1) # wait for connection and subscription

# 2. Trigger configuration change via Django send-input API
print("\n1. Triggering Deep Sleep Update via Django REST API (Enable Deep Sleep, Interval = 300s)...")
try:
    url = "http://127.0.0.1:8000/api/send-input/"
    payload = {
        "mac_address": MAC,
        "total_height": 3.0,
        "total_volume": 5000.0,
        "min_percentage": 20.0,
        "max_percentage": 90.0,
        "deep_sleep": 1,
        "sleep_interval": 300
    }
    req = urllib.request.Request(url, method="POST", data=json.dumps(payload).encode())
    req.add_header("Content-Type", "application/json")
    res = urllib.request.urlopen(req)
    print("   REST API response:", res.read().decode())
except Exception as e:
    print("   Connection failed. Make sure your Django server is running first!")
    print(f"   Error: {e}")
    client.loop_stop()
    exit(1)

# Wait to capture the published MQTT command from Django
time.sleep(3)

# 3. Simulate sensor sending telemetry with current deep sleep status
print("\n2. Simulating sensor heartbeat telemetry with deep sleep enabled (ds=1, si=300)...")
telemetry = {
  "sn": "SN-789123",
  "mac": MAC,
  "d": 1.5,
  "p": 50,
  "fv": 2500,
  "ms": 0,
  "mm": 0,
  "bv": 3.45,
  "ds": 1,
  "si": 300
}
client.publish(TOPIC, json.dumps(telemetry))

time.sleep(2) # Wait for Django to process telemetry

# Shutdown MQTT
client.loop_stop()
client.disconnect()

print("\n=================== TEST RESULTS ===================")
config_pub = [m for m in received_messages if m.get("Deep Sleep") == "1" and m.get("Sleep_Interval") == "300"]

print(f"Total commands captured: {len(received_messages)}")
if len(config_pub) > 0:
    print("SUCCESS: Django successfully published deep sleep config (ds=1, si=300) to MQTT!")
else:
    print("FAILURE: Django did not publish the expected deep sleep command.")
print("====================================================")
