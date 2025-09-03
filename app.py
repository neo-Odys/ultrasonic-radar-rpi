import RPi.GPIO as GPIO
import time
from flask import Flask, render_template, jsonify
import threading

app = Flask(__name__)

# Ustawienia pinów
TRIG = 20
ECHO = 16
SERVO = 21

# Ustawienia GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Wyłącz ostrzeżenia
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(SERVO, GPIO.OUT)

# Ustawienia serwomechanizmu
pwm = GPIO.PWM(SERVO, 50)  # 50 Hz
pwm.start(0)

# Globalne zmienne do przechowywania danych
data = []

# Funkcja do ustawiania kąta serwomechanizmu
def set_servo_angle(angle):
    duty = angle / 18 + 2  # Przekształcenie kąta na wartość PWM
    GPIO.output(SERVO, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.1)  # Zmniejszenie czasu na stabilizację
    GPIO.output(SERVO, False)
    pwm.ChangeDutyCycle(0)

# Funkcja do zbierania danych z radaru
def collect_data():
    while True:
        for angle in range(0, 181, 1):  # Zbieraj dane od 0 do 180 co 1 stopień
            set_servo_angle(angle)

            # Wysyłanie impulsu
            GPIO.output(TRIG, True)
            time.sleep(0.00001)  # 10 mikrosekund
            GPIO.output(TRIG, False)

            # Czekanie na odbiór impulsu
            while GPIO.input(ECHO) == 0:
                start_time = time.time()

            while GPIO.input(ECHO) == 1:
                stop_time = time.time()

            # Obliczanie odległości
            elapsed_time = stop_time - start_time
            distance = (elapsed_time * 34300) / 2  # w centymetrach

            # Dodawanie danych do listy
            data.append({'angle': angle, 'distance': distance})
            print(f"Kąt: {angle}, Odległość: {distance:.2f} cm")  # Logowanie do terminala

            time.sleep(0.1)  # Zmniejszenie czasu oczekiwania przed kolejnym pomiarem

# Uruchomienie zbierania danych w osobnym wątku
threading.Thread(target=collect_data, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def get_data():
    print("Dane zwracane z endpointu /data:", data)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

