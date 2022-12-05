from utils import *
import RPi.GPIO as GPIO

class Motor:
    def __init__(self, in1, in2, pwm, frequency, max_fill):
        self.frequency = frequency
        self.max_speed = max_fill
        self.speed = 0
        self.in1 = in1
        self.in2 = in2

        GPIO.setup(pwm, GPIO.OUT)
        self.pwm = GPIO.PWM(pwm, self.frequency)
        self.pwm.start(self.speed)

        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)

        GPIO.output(in1, 0)
        GPIO.output(in2, 0)

    def forward(self):
        self.speed_change()

    def backward(self):
        self.speed_change()

    def stop_hard(self):
        self.speed_change()

    def stop_soft(self):
        GPIO.output(self.in1, 0)
        GPIO.output(self.in2, 0)

    def speed_change(self):
        if self.speed > 0:
            GPIO.output(self.in1, 1)
            GPIO.output(self.in2, 0)
        elif self.speed < 0:
            GPIO.output(self.in1, 0)
            GPIO.output(self.in2, 1)
        elif self.speed == 0:
            GPIO.output(self.in1, 0)
            GPIO.output(self.in2, 0)

        if self.speed < -self.max_speed:
            self.speed = -self.max_speed
        elif self.speed > self.max_speed:
            self.speed = self.max_speed

        self.pwm.ChangeDutyCycle(abs(self.speed))