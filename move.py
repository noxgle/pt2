from utils import *
import sys
import paho.mqtt.client as mqtt
import time
import json
from utils import *
# from subscriber import *
import RPi.GPIO as GPIO
from scipy.interpolate import interp1d
import math
from collections import deque
from motor import *


class Move:
    def __init__(self):
        self.subscriber_name = [('auto', 0), ('remote', 0)]
        self._run = True
        self.bridge_stby_status = True
        self.last_message_time=None

        self.main_cf = load_conf('MAIN')
        self.motor_conf = load_conf('MOTOR')
        self.gpio_cf = load_conf('GPIO')

        log_level = self.main_cf['log_level']
        if self.main_cf['log_to_file'] == 'True':
            set_logging(log_level, True)
        elif self.main_cf['log_to_file'] == 'False':
            set_logging(log_level, False)
        else:
            sys.exit()

        self.multiplier_speed = 5

        self.mqttBroker = self.main_cf['mosquitto_ip']
        self.m_user = self.main_cf['mosquitto_user']
        self.m_pass = self.main_cf['mosquitto_pass']

        self.client = mqtt.Client(f"{type(self).__name__} publisher")
        self.client.username_pw_set(self.m_user, self.m_pass)
        self.client.connect(self.mqttBroker, keepalive=0)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(self.m_user, self.m_pass)
        self.client_sub.connect(self.mqttBroker)

        gpio_mode = self.gpio_cf['mode']
        gpio_warn_on = self.gpio_cf['warn_on']

        if gpio_mode == 'board':
            GPIO.setmode(GPIO.BOARD)
        elif gpio_mode == 'bcm':
            GPIO.setmode(GPIO.BOARD)
        else:
            logging.critical(f"{type(self).__name__}: incorrect gpio_mode")
            sys.exit()

        if gpio_warn_on == 'True':
            GPIO.setwarnings(True)
        elif gpio_warn_on == 'False':
            GPIO.setwarnings(False)
        else:
            logging.critical(f"{type(self).__name__}: incorrect gpio_warn_on")
            sys.exit()

        self.bridge_stby = int(self.motor_conf['stby'])

        GPIO.setup(self.bridge_stby, GPIO.OUT)
        self.bridge_standby_on()

        self.pwm_max_fill = int(self.motor_conf['pwm_max_fill'])
        self.motor1 = Motor(int(self.motor_conf['ain1']), int(self.motor_conf['ain2']), int(self.motor_conf['pwm1']),
                            int(self.motor_conf['pwm_frequency']), self.pwm_max_fill)
        self.motor2 = Motor(int(self.motor_conf['bin1']), int(self.motor_conf['bin2']), int(self.motor_conf['pwm2']),
                            int(self.motor_conf['pwm_frequency']), self.pwm_max_fill)

        if self.motor_conf['public_joystick_data'] == 'True':
            self.public_joystick_data = True
        elif self.motor_conf['public_joystick_data'] == 'False':
            self.public_joystick_data = False
        else:
            logging.critical(f"{type(self).__name__}: incorrect public_joystick_data only True or False")
            sys.exit()

        self.speed_interpolation = interp1d([-1.0, 1.0], [-self.pwm_max_fill, self.pwm_max_fill])
        self.run()

    def bridge_standby_on(self):
        if self.bridge_stby_status is False:
            GPIO.output(self.bridge_stby, 0)
            self.bridge_stby_status = True
            payload = json.dumps({'move': {'bridge_stby_status': str(self.bridge_stby_status)}})
            self.client.publish('move', payload)

    def bridge_standby_off(self):
        if self.bridge_stby_status is True:
            GPIO.output(self.bridge_stby, 1)
            self.bridge_stby_status = False
            payload = json.dumps({'move': {'bridge_stby_status': str(self.bridge_stby_status)}})
            self.client.publish('move', payload)
            self.last_message_time = time.time()

    def forward(self):
        if self.motor1.speed > self.motor2.speed:
            x = self.motor1.speed
        elif self.motor1.speed < self.motor2.speed:
            x = self.motor2.speed
        else:
            x = self.motor1.speed + 5 * self.multiplier_speed

        self.motor1.speed = x
        self.motor1.forward()
        self.motor2.speed = x
        self.motor2.forward()
        payload = json.dumps({'move': {'motor1_speed': self.motor1.speed, 'motor2_speed': self.motor2.speed}})
        self.client.publish('move', payload)

    def backward(self):
        if self.motor1.speed > self.motor2.speed:
            x = self.motor2.speed
        elif self.motor1.speed < self.motor2.speed:
            x = self.motor1.speed
        else:
            x = self.motor1.speed - 5 * self.multiplier_speed

        self.motor1.speed = x
        self.motor1.forward()
        self.motor2.speed = x
        self.motor2.forward()
        payload = json.dumps({'move': {'motor1_speed': self.motor1.speed, 'motor2_speed': self.motor2.speed}})
        self.client.publish('move', payload)

    def left(self):
        self.motor1.speed += 5 * self.multiplier_speed
        self.motor1.forward()
        if (self.motor2.speed - 5 * self.multiplier_speed) < 0:
            self.motor2.speed = 0
        else:
            self.motor2.speed -= 5 * self.multiplier_speed
        self.motor2.backward()
        payload = json.dumps({'move': {'motor1_speed': self.motor1.speed, 'motor2_speed': self.motor2.speed}})
        self.client.publish('move', payload)

    def right(self):
        self.motor2.speed += 5 * self.multiplier_speed
        self.motor1.backward()
        if self.motor1.speed - 5 * self.multiplier_speed < 0:
            self.motor1.speed = 0
        else:
            self.motor1.speed -= 5 * self.multiplier_speed

        self.motor2.forward()
        payload = json.dumps({'move': {'motor1_speed': self.motor1.speed, 'motor2_speed': self.motor2.speed}})
        self.client.publish('move', payload)

    def stop_motors(self):
        self.motor1.speed = 0
        self.motor2.speed = 0
        self.motor1.stop_hard()
        self.motor2.stop_hard()
        payload = json.dumps({'move': {'motor1_speed': self.motor1.speed, 'motor2_speed': self.motor2.speed}})
        self.client.publish('move', payload)

    def joystick(self, data):
        logging.debug(f"{type(self).__name__}: data :  {data}")
        btn_status = int(data[0])
        if self.public_joystick_data is True:
            payload = json.dumps({'move': {'public_joystick_data': data}})
            self.client.publish('move', payload)

        if btn_status == 0:
            # unpressed
            self.stop_motors()
        elif btn_status == 1:
            # first press
            pass
        elif btn_status == 2:
            # pressed
            x = float(data[3])
            y = float(data[4])

            if x == 0 and y == 0:
                self.stop_motors()
            else:
                # taken from https://www.instructables.com/Joystick-to-Differential-Drive-Python/
                # First Compute the angle in deg
                # First hypotenuse
                z = math.sqrt(x * x + y * y)

                # angle in radians
                rad = math.acos(math.fabs(x) / z)

                # and in degrees
                angle = rad * 180 / math.pi

                # Now angle indicates the measure of turn
                # Along a straight line, with an angle o, the turn co-efficient is same
                # this applies for angles between 0-90, with angle 0 the coeff is -1
                # with angle 45, the co-efficient is 0 and with angle 90, it is 1

                tcoeff = -1 + (angle / 90) * 2
                turn = tcoeff * math.fabs(math.fabs(y) - math.fabs(x))
                turn = round(turn * 100, 0) / 100

                # And max of y or x is the movement
                mov = max(math.fabs(y), math.fabs(x))

                # First and third quadrant
                if (x >= 0 and y >= 0) or (x < 0 and y < 0):
                    rawLeft = mov
                    rawRight = turn
                else:
                    rawRight = mov
                    rawLeft = turn

                    # Reverse polarity
                if y < 0:
                    rawLeft = 0 - rawLeft
                    rawRight = 0 - rawRight

                if rawRight > 0:
                    self.motor1.forward()
                else:
                    self.motor1.backward()

                if rawLeft > 0:
                    self.motor2.forward()
                else:
                    self.motor2.backward()

                if rawRight > 1:
                    rawRight = 1

                if rawLeft > 1:
                    rawLeft = 1

                logging.debug(f"{type(self).__name__}: rawLeft :  {rawLeft}, rawRight {rawRight}")
                self.motor1.speed = self.speed_interpolation(rawRight)
                self.motor2.speed = self.speed_interpolation(rawLeft)

            payload = json.dumps(
                {'move': {'motor1_speed': str(self.motor1.speed), 'motor2_speed': str(self.motor2.speed)}})
            self.client.publish('move', payload)

    def run(self):
        try:
            self.client_sub.loop_start()
            self.client_sub.subscribe(self.subscriber_name)
            self.client_sub.on_message = self.on_message
            self.last_message_time=time.time()
            while self._run:
                if self.bridge_stby_status is False:
                    if self.motor1.speed == 0 and self.motor2.speed == 0 and time.time() > self.last_message_time + 5:
                        self.bridge_standby_on()
                time.sleep(0.1)

        except Exception as e:
            print(e)
        finally:
            self.client.loop_stop()
            self.client_sub.loop_stop()
            GPIO.cleanup()
            sys.exit()

    def exit(self):
        self._run = False

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")

            if payload['cmd'] == 'exit':
                self.exit()
            elif payload['cmd'] == 'forward':
                self.bridge_standby_off()
                self.forward()
            elif payload['cmd'] == 'backward':
                self.bridge_standby_off()
                self.backward()
            elif payload['cmd'] == 'left':
                self.bridge_standby_off()
                self.left()
            elif payload['cmd'] == 'right':
                self.bridge_standby_off()
                self.right()
            elif payload['cmd'] == 'break':
                self.stop_motors()
            elif payload['cmd'] == 'joystick':
                self.bridge_standby_off()
                self.joystick(payload['data'])
        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")


if __name__ == '__main__':
    Move()
