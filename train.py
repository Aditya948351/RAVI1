import requests
import time
from twilio.rest import Client
import pyttsx3
import speech_recognition as sr
import sqlite3
import pyautogui
import os

RPI_IP = "Add your desktops ip"
DATA_PORT = 5000
LED_CONTROL_PORT = 5000
account_sid = 'replace with the sid'
auth_token = 'replace with twilio auth token'
twilio_phone = 'Add generated twillio phone number'
user_phone = 'Add your registered number'

client = Client(account_sid, auth_token)
engine = pyttsx3.init()

conn = sqlite3.connect('memory.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS facts (
    question TEXT PRIMARY KEY,
    answer TEXT
)
''')

def speak(message):
    engine.say(message)
    engine.runAndWait()

def get_location():
    try:
        response = requests.get('http://ipinfo.io')
        data = response.json()
        city = data.get('city', 'Unknown')
        return city
    except Exception:
        return "Error fetching location"

def get_weather(location):
    """Get the weather for the given location."""
    url = f"http://wttr.in/{location}?format=%C+%t"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Sorry, I couldn't fetch the weather information."
    except Exception as e:
        return f"An error occurred: {e}"

def teach(question, answer):
    cursor.execute('INSERT OR REPLACE INTO facts (question, answer) VALUES (?, ?)', (question, answer))
    conn.commit()
    print(f"Stored in DB - Question: {question}, Answer: {answer}")

def respond(question):
    cursor.execute('SELECT answer FROM facts WHERE question LIKE ?', (f"%{question}%",))
    result = cursor.fetchone()
    return result[0] if result else "I don't know about it."

def forget(question):
    cursor.execute('DELETE FROM facts WHERE question LIKE ?', (f"%{question}%",))
    conn.commit()
    print(f"Forgot the fact: {question}")
    speak(f"I have forgotten what {question} is.")

def control_light(state):
    url = f'http://{RPI_IP}:{LED_CONTROL_PORT}/control_led'
    try:
        response = requests.post(url, json={'state': state})
        print(response.text)
        speak(f"The light is now {'on' if state == 'on' else 'off'}")
    except requests.RequestException as e:
        print(f"Error controlling light: {e}")

def send_rain_alert():
    message = client.messages.create(
        body="Message from Ravi, Alert! Gas leak detected at your house. Please check it as soon as possible.",
        from_=twilio_phone,
        to=user_phone
    )
    print(f"Gas Leak Alert Sent. SID: {message.sid}")

def get_sensor_data():
    try:
        url = f'http://{RPI_IP}:{DATA_PORT}/get_data'
        response = requests.get(url)
        data = response.json()
        return data['distance'], data['rain']
    except requests.RequestException as e:
        print(f"Error in Sensors: {e}")
        return None, None

def process_command(command):
    command = command.lower()

    if command.startswith("teach yourself that") or command.startswith("remember that") or command.startswith("do you know that"):
        fact = command.split("that", 1)[1].strip()
        if " is " in fact:
            subject, predicate = fact.split(" is ", 1)
            question = f"who is {subject.strip()}?"
            answer = f"{subject.strip()} is {predicate.strip()}."
            teach(question, answer)
            speak("Got it! I have learned that.")
        else:
            speak("I don't remember anything.")

    elif command.startswith("forget that"):
        question = command.split("that", 1)[1].strip()
        forget(question)

    elif "turn on the light" in command:
        control_light('on')
    elif "turn off the light" in command:
        control_light('off')

    elif "terminate yourself" in command:
        speak("Goodbye! Sir, You may go.")

    elif "what time is it now" in command:
        current_time = time.strftime("%I:%M %p")
        speak(f"The current time is {current_time}")

    elif "open vs code" in command:
        pyautogui.hotkey("win", "r")
        time.sleep(1)
        file_PATH = r"C:\Users\Acer\Desktop\Visual Studio Code.lnk"
        pyautogui.typewrite(file_PATH)
        pyautogui.hotkey('enter')

    elif "close it" in command:
        pyautogui.hotkey('Alt', 'F4')

    elif command == "open chrome" or command == "open my personal account in chrome":
        file_PATH = r"C:\Users\Acer\Desktop\Google Chrome.lnk"
        if os.path.exists(file_PATH):
            os.startfile(file_PATH)
            speak("Chrome is opening.")
            time.sleep(2)

    elif "going good" in command:
        speak("Ohh! Day seems good today")

    elif "weather" in command:
        location = get_location()
        weather = get_weather(location)
        if "Error" in location:
            speak("Sorry, I couldn't determine your location.")
        else:
            speak(f"The weather in {location} is {weather}")
            print(f"The weather in {location} is {weather}")

    else:
        answer = respond(command)
        speak(answer)
def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Listening for commands...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio, language="en-IN")
        print(f"You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not catch that.")
        return None
    except sr.RequestError:
        speak("Sorry, my speech recognition service is down.")
        return None

def main():
    rain_alert_sent = False
    previous_distance = None

    while True:
        distance, rain = get_sensor_data()
        if distance is not None:
            print(f"Distance: {distance:.2f} cm")
            if previous_distance is None or (previous_distance >= 50 and distance < 50):
                speak("Welcome sir! How is your day going?")
            elif previous_distance is None or (previous_distance < 50 and distance >= 50):
                speak("Goodbye sir! I will be monitoring your house.")
            previous_distance = distance

        if rain and not rain_alert_sent:
            send_rain_alert()
            rain_alert_sent = True
        elif not rain:
            rain_alert_sent = False

        command = listen()
        if command:
            process_command(command)
if __name__ == "__main__":
    main()
