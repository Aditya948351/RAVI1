from flask import Flask, jsonify, request
import time
import threading
import random

app = Flask(__name__)
distance_list = []

def measure_distance():
    if len(distance_list) < 5:
        # Generate a random distance between 1 and 40 cm
        distance = random.uniform(1, 100)
        distance_list.append(distance)
        return distance

def rain_detected():
    return True  # Simulate that rain is always detected

@app.route('/get_data', methods=['GET'])
def get_data():
    distance = measure_distance()
    is_raining = rain_detected()

    return jsonify({
        'distance': distance,
        'rain': is_raining
    })

@app.route('/control_buzzer', methods=['GET'])
def control_buzzer():
    print("Buzzer activated for 5 seconds")
    return "Buzzer activated for 5 seconds (simulated)", 200

@app.route('/control_led', methods=['POST'])
def control_led():
    data = request.get_json()
    if 'state' in data:
        if data['state'] == 'on':
            print("LED turned on")
            return "LED turned on", 200
        elif data['state'] == 'off':
            print("LED turned off")
            return "LED turned off", 200

    return "Invalid request", 400

def sensor_monitoring():
    while True:
        if rain_detected():
            print(" Rain detected, buzzer would be triggered.")
            time.sleep(3)
        time.sleep(3)

if __name__ == "__main__":
    sensor_thread = threading.Thread(target=sensor_monitoring)
    sensor_thread.daemon = True
    sensor_thread.start()

    app.run(host='0.0.0.0', port=5000)
