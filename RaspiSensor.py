from flask import Flask, jsonify, request
import time
import threading
import random
import RPi.GPIO as GPIO

app = Flask(__name__)

# ------------------- GPIO SETUP -------------------
BUZZER_PIN = 17  # GPIO pin for buzzer
LED_PIN = 27     # GPIO pin for LED

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

distance_list = []

# ------------------- SENSOR FUNCTIONS -------------------

def measure_distance():
    """Simulate distance measurement (replace with real sensor if needed)."""
    if len(distance_list) < 5:
        distance = random.uniform(1, 100)  # Random distance
        distance_list.append(distance)
        return distance
    return random.uniform(1, 100)

def rain_detected():
    """Simulate rain detection (replace with actual sensor logic)."""
    return True  # Always raining for simulation

# ------------------- FLASK ROUTES -------------------

@app.route('/get_data', methods=['GET'])
def get_data():
    distance = measure_distance()
    is_raining = rain_detected()
    return jsonify({'distance': distance, 'rain': is_raining})

@app.route('/control_buzzer', methods=['GET'])
def control_buzzer():
    """Activate the buzzer for 5 seconds."""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(5)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    return "Buzzer activated for 5 seconds", 200

@app.route('/control_led', methods=['POST'])
def control_led():
    """Control LED state via JSON POST: {'state': 'on'/'off'}"""
    data = request.get_json()
    if 'state' in data:
        state = data['state'].lower()
        if state == 'on':
            GPIO.output(LED_PIN, GPIO.HIGH)
            return "LED turned on", 200
        elif state == 'off':
            GPIO.output(LED_PIN, GPIO.LOW)
            return "LED turned off", 200
    return "Invalid request", 400

# ------------------- BACKGROUND SENSOR MONITORING -------------------

def sensor_monitoring():
    """Background thread to monitor rain and trigger buzzer."""
    while True:
        if rain_detected():
            print("Rain detected! Activating buzzer for 3 seconds.")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(3)
            GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(3)

# ------------------- MAIN -------------------

if __name__ == "__main__":
    try:
        sensor_thread = threading.Thread(target=sensor_monitoring, daemon=True)
        sensor_thread.start()
        app.run(host='0.0.0.0', port=5000)
    finally:
        GPIO.cleanup()  # Ensure GPIO pins are cleaned up on exit
