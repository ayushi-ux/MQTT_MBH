import json
import time
import urllib.request
import paho.mqtt.client as mqtt

# Configure testing parameters
MAC = "84:1F:E8:2C:52:78"
TOPIC = "factory/esp32/esp32_1/water_management_system"

print("==================================================")
print("WATER TANK AUTO-REFILL LOGIC INTEGRATION TEST")
print("==================================================")

# 1. Enable AUTO mode on Django backend
print("\n1. Setting Motor Mode to AUTO via Django API...")
try:
    url = f"http://127.0.0.1:8000/api/motor-auto/?mac={MAC}"
    req = urllib.request.Request(url, method="POST", data=b"{}")
    req.add_header("Content-Type", "application/json")
    res = urllib.request.urlopen(req)
    print("   Response:", res.read().decode())
except Exception as e:
    print("   Connection failed. Make sure your Django server is running first!")
    print(f"   Error: {e}")
    exit(1)

# 2. Setup MQTT client to listen to published commands
received_messages = []

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    data = json.loads(payload)
    if data.get("_source") == "django":
        print(f"   [MQTT COMMAND RECEIVED] Django published command to ESP32: {payload}")
        received_messages.append(data)

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.emqx.io", 1883, 60)
client.subscribe(TOPIC)
client.loop_start()

time.sleep(1) # wait for connection and subscription

# 3. Publish LOW water level (15%) -> expected to start the motor (Motor_status: 1)
print("\n2. Simulating Sensor LOW level (15% | threshold is 20%)...")
low_water_payload = {
  "sn": "SN-789123",
  "mac": MAC,
  "d": 2.5,
  "p": 15,
  "fv": 150,
  "ms": 0,
  "mm": 0,
  "bv": 3.45,
  "f": 0
}
client.publish(TOPIC, json.dumps(low_water_payload))

# Wait for Django to process telemetry and publish motor command
time.sleep(3) 

# 4. Publish HIGH water level (95%) -> expected to stop the motor (Motor_status: 0)
print("\n3. Simulating Sensor HIGH level (95% | threshold is 90%)...")
high_water_payload = {
  "sn": "SN-789123",
  "mac": MAC,
  "d": 0.2,
  "p": 95,
  "fv": 950,
  "ms": 1,
  "mm": 0,
  "bv": 3.45,
  "f": 0
}
client.publish(TOPIC, json.dumps(high_water_payload))

# Wait for Django to process telemetry and publish motor command
time.sleep(3) 

# Shutdown MQTT
client.loop_stop()
client.disconnect()

print("\n=================== TEST RESULTS ===================")
starts = [m for m in received_messages if m.get("Motor_status") == "1"]
stops = [m for m in received_messages if m.get("Motor_status") == "0"]

print(f"Total commands captured: {len(received_messages)}")
if len(starts) > 0 and len(stops) > 0:
    print("SUCCESS: Auto motor start and stop triggered successfully!")
else:
    print("FAILURE: Missing start or stop command.")
print("====================================================")
