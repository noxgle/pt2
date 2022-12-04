import sys
from utils import *
import threading
import time
import cv2
import json
import paho.mqtt.client as mqtt
# from subscriber import *
import base64
import numpy as np
#import pickle5 as pickle
import _pickle as pickle
from picamera2 import Picamera2


class Cam(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._run = True
        self.frame = np.zeros((240, 320, 3), np.uint8)

        self.cap = cv2.VideoCapture(-1, cv2.CAP_V4L2)
        self.frame_rate = self.cap.get(5)
        # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        # self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

    def get_frame(self):
        return self.frame

    def run(self):
        time.sleep(1)
        try:
            while self._run:
                r, frame = self.cap.read()
                if r is True:
                    self.frame = frame
                time.sleep(0.01)
        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")
        finally:
            self.cap.release()
            sys.exit()

    def stop(self):
        self._run = False

class Cam2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._run = True
        self.frame = np.zeros((240, 320, 3), np.uint8)

        self.cap = Picamera2()
        #self.cap.configure(self.cap.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))

        #video_config =self.cap.create_still_configuration(main={"size": (320, 240),"format": 'XRGB8888'}, raw={"size":  self.cap.sensor_resolution},controls={"FrameDurationLimits": (16, 16)})
        #video_config['main']['format'] = 'RGB888'
        #self.cap.configure(video_config)
        self.cap.configure(self.cap.create_preview_configuration({"size": (320, 240)}, raw=self.cap.sensor_modes[1]))
        #self.cap.set_controls({"ExposureTime": 40, "AnalogueGain": 1.5})
        #video_config = self.cap.create_video_configuration(raw=self.cap.sensor_modes[1])
        #self.cap.configure(video_config)
        self.cap.
        self.cap.start()


    def get_frame(self):
        return self.frame

    def run(self):
        time.sleep(2)
        try:
            while self._run:
                frame = self.cap.capture_array('main')
                self.frame = frame
        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")
        finally:
            self.cap.stop()
            sys.exit()

    def stop(self):
        self._run = False

class View:
    def __init__(self):
        self.subscriber_name = [('auto', 0), ('remote', 0), ('sensors', 0)]
        self._run = True
        self.cam = None
        self.frame_rate = 15
        # self.jpg_quality = 75
        # self.frame_resize = 0
        # self.resize_inter = cv2.INTER_NEAREST

        self.main_cf = load_conf('MAIN')
        self.motor_conf = load_conf('MOTOR')
        self.cam_cf = load_conf('CAM')

        self.mqttBroker = self.main_cf['mosquitto_ip']
        self.m_user = self.main_cf['mosquitto_user']
        self.m_pass = self.main_cf['mosquitto_pass']

        log_level = self.main_cf['log_level']
        set_logging(log_level)

        self.cam_enable = self.cam_cf['cam_enable']
        self.frame_rate = int(self.cam_cf['frame_rate'])
        self.jpg_quality = int(self.cam_cf['jpg_quality'])

        self.client = mqtt.Client(f"{type(self).__name__} publisher")
        self.client.username_pw_set(self.m_user, self.m_pass)
        self.client.connect(self.mqttBroker)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(self.m_user, self.m_pass)
        self.client_sub.connect(self.mqttBroker)

        self.run()

    def cam_on(self):
        self.cam = Cam2()
        self.cam.start()
        time.sleep(1)

    def cam_off(self):
        self.cam.stop()
        self.cam = None

    def new_frame_rate(self, new_frame_rate):
        if new_frame_rate > self.cam.frame_rate:
            self.frame_rate = new_frame_rate

    # def frame_processing(self):
    #     if self.frame_resize > 0:
    #         frame, _ = resize_img(self.cam.get_frame(), self.frame_resize, self.resize_inter)
    #     else:
    #         frame = self.cam.get_frame()
    #     #_, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpg_quality])
    #     logging.debug(f"{type(self).__name__}: cam set: {self.cam.cap.sensor_modes[1]}")
    #     return pickle.dumps(frame)
    #     # return base64.b64encode(buffer)

    def run(self):
        self.client_sub.loop_start()
        self.client_sub.subscribe(self.subscriber_name)
        self.client_sub.on_message = self.on_message
        if self.cam_enable == 'True':
            self.cam_on()
        try:
            #self.new_frame_rate(self.frame_rate)
            prev = 0
            while self._run:
                time_elapsed = time.time() - prev
                if time_elapsed > 1. / self.frame_rate and self.cam is not None:
                    prev = time.time()
                    frame=self.cam.get_frame()
                    self.client.publish('view',  pickle.dumps(frame), qos=0)
                time.sleep(0.001)


        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")
        finally:
            if self.cam is not None:
                self.cam_off()
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
                if payload['cmd'] == 'exit':
                    self.exit()
                elif payload['cmd'] == 'cam_on':
                    self.cam_on()
                elif payload['cmd'] == 'cam_off':
                    self.cam_off()


        except Exception as e:
            print(e)


if __name__ == '__main__':
    View()
