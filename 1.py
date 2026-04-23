import Adafruit_DHT
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import json
import time
import signal
import sys

# ---------------- CONFIG ----------------
SENSOR = Adafruit_DHT.DHT11   # or Adafruit_DHT.DHT22
DHT_PIN = 4

LED_PIN = 17

THINGSBOARD_HOST = "demo.thingsboard.io"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

TELEMETRY_TOPIC = "v1/devices/me/telemetry"
RPC_TOPIC = "v1/devices/me/rpc/request/+"

# ---------------- GPIO SETUP ----------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# ---------------- MQTT SETUP ----------------
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)

# ---------------- RPC HANDLER ----------------
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        print("RPC Received:", payload)

        if "method" in payload:
            if payload["method"] == "setLED":
                state = payload.get("params", False)

                if state:
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    print("LED ON")
                else:
                    GPIO.output(LED_PIN, GPIO.LOW)
                    print("LED OFF")

    except Exception as e:
        print("RPC Error:", e)

# ---------------- CONNECT ----------------
def connect_mqtt():
    try:
        client.connect(THINGSBOARD_HOST, 1883, 60)
        client.subscribe(RPC_TOPIC)
        client.on_message = on_message
        client.loop_start()
        print("Connected to ThingsBoard")
    except Exception as e:
        print("MQTT Connection Failed:", e)
        sys.exit(1)

# ---------------- TELEMETRY LOOP ----------------
def send_telemetry():
    try:
        humidity, temperature = Adafruit_DHT.read(SENSOR, DHT_PIN)

        if humidity is not None and temperature is not None:
            data = {
                "temperature": temperature,
                "humidity": humidity
            }

            client.publish(TELEMETRY_TOPIC, json.dumps(data))
            print("Sent:", data)

        else:
            print("Sensor read failed")

    except Exception as e:
        print("Telemetry Error:", e)

# ---------------- CLEAN EXIT ----------------
def cleanup(signum, frame):
    print("\nExiting gracefully...")

    try:
        client.loop_stop()
        client.disconnect()
    except:
        pass

    GPIO.cleanup()
    sys.exit(0)

# Catch Ctrl+C
signal.signal(signal.SIGINT, cleanup)

# ---------------- MAIN ----------------
def main():
    connect_mqtt()

    while True:
        send_telemetry()
        time.sleep(5)

if __name__ == "__main__":
    main()