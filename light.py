import RPi.GPIO as GPIO

from time import sleep   

 
GPIO.cleanup()
class Result:
    def output(self, desired_output:bool):
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            SuccessLED = 17
            FailLED = 27
            Buzzer = 22
            
            
              
             
            if desired_output:
                GPIO.setup(SuccessLED,GPIO.OUT)
                GPIO.output(SuccessLED,GPIO.HIGH)
                sleep(3)
            else:
                GPIO.setup(FailLED,GPIO.OUT)
                GPIO.output(FailLED,GPIO.HIGH)
                GPIO.setup(Buzzer,GPIO.OUT)
                p = GPIO.PWM(Buzzer, 1000)
                GPIO.output(Buzzer,GPIO.HIGH)
                p.start(50)
                sleep(3)
            GPIO.cleanup()
        
r = Result()
r.output(True)
GPIO.cleanup()

