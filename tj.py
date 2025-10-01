import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

SuccessLED = 17
FailLED = 27
Buzzer = 22

GPIO.setup(SuccessLED, GPIO.OUT)
GPIO.setup(FailLED, GPIO.OUT)
GPIO.setup(Buzzer, GPIO.OUT)

# Blue LED ON
GPIO.output(SuccessLED, GPIO.HIGH)
time.sleep(1)
GPIO.output(SuccessLED, GPIO.LOW)

# Red LED ON
GPIO.output(FailLED, GPIO.HIGH)
time.sleep(1)
GPIO.output(FailLED, GPIO.LOW)

# Buzzer ON for 1s
GPIO.output(Buzzer, GPIO.HIGH)
time.sleep(1)
GPIO.output(Buzzer, GPIO.LOW)

GPIO.cleanup()
