import time
import json
import Adafruit_DHT
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

# ---------------------------
# ThingsBoard Configuration
# ---------------------------
THINGSBOARD_HOST = 'demo.thingsboard.io'  # or your server
ACCESS_TOKEN = '0ultbtjjhx48827ybu0o'

# ---------------------------
# Sensor Configuration
# ---------------------------
DHT_SENSOR = Adafruit_DHT.DHT22  # Change to DHT11 if needed
DHT_PIN = 4  # GPIO pin where the sensor is connected

# ---------------------------
# GPIO Setup for LED
# ---------------------------
LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# ---------------------------
# MQTT Setup
# ---------------------------
client = mqtt.Client()
client.username_pw_set(ACCESS_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)

# ---------------------------
# Functions
# ---------------------------
def read_sensor():
    """Read temperature and humidity from DHT sensor."""
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return round(temperature, 2), round(humidity, 2)
    else:
        return None, None

def send_data():
    """Read sensor and send telemetry to ThingsBoard."""
    temperature, humidity = read_sensor()
    if temperature is not None and humidity is not None:
        payload = json.dumps({"temperature": temperature, "humidity": humidity})
        client.publish('v1/devices/me/telemetry', payload, qos=1)
        print(f"Sent to ThingsBoard: {payload}")
    else:
        print("Failed to read from sensor.")

def on_message(client, userdata, message):
    """Handle RPC messages from ThingsBoard."""
    try:
        msg = json.loads(message.payload)
        if msg.get('method') == 'setLED':
            led_state = msg.get('params')
            if led_state == "ON":
                GPIO.output(LED_PIN, GPIO.HIGH)
                print("LED turned ON")
            elif led_state == "OFF":
                GPIO.output(LED_PIN, GPIO.LOW)
                print("LED turned OFF")
    except Exception as e:
        print("RPC Error:", e)

# ---------------------------
# MQTT Callback Setup
# ---------------------------
client.on_message = on_message
client.subscribe('v1/devices/me/rpc/request/+')

# ---------------------------
# Main Loop
# ---------------------------
try:
    while True:
        send_data()  # Only call this function in the loop
        client.loop()  # Handle MQTT callbacks
        time.sleep(5)

except KeyboardInterrupt:
    print("Stopping program...")
    GPIO.cleanup()
