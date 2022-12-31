import logging
import sys

from utils import *

import time
import json
import _pickle as pickle

class Auto:
    def __init__(self):
        self.subscriber_name = [('pitank', 0), ('move', 0), ('view', 0), ('sensors', 0), ('remote', 1)]
        self._run = True


        self.main_cf = load_conf('MAIN')

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

        self.client = mqtt.Client(f"{type(self).__name__} publisher")
        self.client.username_pw_set(self.m_user, self.m_pass)
        self.client.connect(self.mqttBroker)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(self.m_user, self.m_pass)
        self.client_sub.connect(self.mqttBroker)

        self.power_save = int(self.main_cf['power_save'])
        self.remote_status = False
        self.cam_status=True
        self.run()

    def run(self):

        self.client_sub.loop_start()
        self.client_sub.subscribe(self.subscriber_name)
        self.client_sub.on_message = self.on_message
        time.sleep(5)
        try:
            while self._run:
                if self.power_save == 0:
                    pass
                elif self.power_save == 1:
                    if self.remote_status is True:
                        if self.cam_status is False:
                            payload = json.dumps({'cmd': 'cam_on'})
                            self.client.publish('auto', payload)
                            self.cam_status=True
                    elif self.remote_status is False:
                        if self.cam_status is True:
                            payload = json.dumps({'cmd': 'cam_off'})
                            self.client.publish('auto', payload)
                            self.cam_status = False

                time.sleep(1)
        except Exception as e:
            logging.critical(f"{type(self).__name__}: {e}")
        finally:
            self.client.loop_stop()
            self.client_sub.loop_stop()
            sys.exit()

    def stop(self):
        self._run = False

    def on_message(self, client, userdata, message):

        try:
            topic = message.topic
            if topic == 'pitank':
                payload = json.loads(message.payload.decode("utf-8"))
            elif topic == 'move':
                payload = json.loads(message.payload.decode("utf-8"))
            elif topic == 'view':
                payload=pickle.loads(message.payload)
                payload=f'frame size: {payload.shape}'
            elif topic == 'sensors':
                payload = json.loads(message.payload.decode("utf-8"))
            elif topic == 'remote':
                payload = json.loads(message.payload.decode("utf-8"))
                if payload['status'] == 'on':
                    self.remote_status = True
                elif payload['status'] == 'off':
                    self.remote_status = False


            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")

        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")


if __name__ == "__main__":
    Auto()
