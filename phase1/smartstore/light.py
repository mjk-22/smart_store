import os
import time

RUN_GPIO =True
try:
    import RPi.GPIO as GPIO
except Exception:
    RUN_GPIO = False

SuccessLED = 17
FailLED = 27
Buzzer = 22 

def _setup():
    if not RUN_GPIO:
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(SuccessLED,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(FailLED,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(Buzzer,GPIO.OUT,initial=GPIO.LOW)
def show_success():
    """Blue LED on, make sure red/buzzer are off."""
    if not RUN_GPIO:
        return
    _setup()
    GPIO.output(FailLED,GPIO.LOW)
    GPIO.output(Buzzer,GPIO.LOW)
    GPIO.output(SuccessLED,GPIO.HIGH)
    # if you want the light to turn off after validating
    # time.sleep(1)
    # GPIO.output(SuccessLED,GPIO.LOW)

def show_failure():
    """Red LED on,beep buzzer twice."""
    if not RUN_GPIO:
        return
    _setup()
    GPIO.output(SuccessLED,GPIO.LOW)
    GPIO.output(FailLED,GPIO.HIGH)
    p = GPIO.PWM(Buzzer,1000)
    p.start(50)
    time.sleep(0.18)
    p.stop()
    time.sleep(0.12)
    p = GPIO.PWM(Buzzer,1000)
    p.start(50)
    time.sleep(0.18)
    p.stop()

def clear_output():
    """Turn everything off"""
    if not RUN_GPIO:
        return
    _setup()
    GPIO.output(FailLED,GPIO.LOW)
    GPIO.output(Buzzer,GPIO.LOW)
    GPIO.output(SuccessLED,GPIO.LOW)
