import time

from utils import *
import json
import paho.mqtt.client as mqtt
# from subscriber import *
import base64
import numpy as np
# import pickle5 as pickle
import _pickle as pickle
from cam import *
import sys


class View:
    def __init__(self):
        self.subscriber_name = [('auto', 0), ('remote', 0), ('sensors', 0)]
        self._run = True
        self.cam = None
        self.cam_cap = None
        self.frame_rate = 15

        self.main_cf = load_conf('MAIN')
        self.motor_conf = load_conf('MOTOR')
        self.cam_cf = load_conf('CAM')

        self.mqttBroker = self.main_cf['mosquitto_ip']
        self.m_user = self.main_cf['mosquitto_user']
        self.m_pass = self.main_cf['mosquitto_pass']

        log_level = self.main_cf['log_level']
        if self.main_cf['log_to_file'] == 'True':
            set_logging(log_level, True)
        elif self.main_cf['log_to_file'] == 'False':
            set_logging(log_level, False)
        else:
            sys.exit()

        self.cam_enable = self.cam_cf['cam_enable']
        self.frame_rate = int(self.cam_cf['frame_rate'])
        self.jpg_quality = int(self.cam_cf['jpg_quality'])

        self.client = mqtt.Client(f"{type(self).__name__} publisher")
        self.client.username_pw_set(self.m_user, self.m_pass)
        self.client.connect(self.mqttBroker,keepalive=0)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(self.m_user, self.m_pass)
        self.client_sub.connect(self.mqttBroker,keepalive=0)

        if self.cam_enable == 'True':
            self.cam = Cam()
            self.cam.start()
            self.cam_cap = True
            time.sleep(1)

        self.run()

    def new_frame_rate(self, new_frame_rate):
        if new_frame_rate > self.cam.frame_rate:
            self.frame_rate = new_frame_rate

    def run(self):
        self.client_sub.loop_start()
        self.client_sub.subscribe(self.subscriber_name)
        self.client_sub.on_message = self.on_message

        try:
            prev = 0
            while self._run:
                if self.cam is not None and self.cam_cap is True:
                    time_elapsed = time.time() - prev
                    if time_elapsed > 1. / self.frame_rate:
                        prev = time.time()
                        frame = self.cam.get_frame()
                        self.client.publish('view', pickle.dumps(frame), qos=0)
                    time.sleep(0.001)
                else:
                    time.sleep(1)


        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")
        finally:
            if self.cam is not None:
                self.cam.cap.stop()
            self.client.loop_stop()
            self.client_sub.loop_stop()
            sys.exit()

    def exit(self):
        self._run = False

    def on_message(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            topic = message.topic
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")
            if topic == 'sensors':
                pass
            else:
                if 'cmd' in payload:
                    if payload['cmd'] == 'exit':
                        self.exit()
                    elif payload['cmd'] == 'cam_on':
                        self.cam.cap.start()
                        self.cam_cap = True
                    elif payload['cmd'] == 'cam_off':
                        self.cam.cap.stop()
                        self.cam_cap = False


        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")


if __name__ == '__main__':
    View()
