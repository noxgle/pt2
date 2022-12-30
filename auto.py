import logging
import sys

from utils import *

import time
import json


class Auto:
    def __init__(self):
        self.subscriber_name = [('pitank', 0), ('move', 0), ('view', 0), ('sensors', 0), ('remote', 1)]
        self._run = True
        self.remote_status = False

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

        self.run()

    def run(self):
        self.client_sub.loop_start()
        self.client_sub.subscribe(self.subscriber_name)
        self.client_sub.on_message = self.on_message
        try:
            while self._run:
                if self.power_save == 0:
                    pass
                elif self.power_save == 1:
                    if self.remote_status is True:
                        payload = json.dumps({'cmd': 'cam_on'})
                        self.client.publish('auto', payload)
                    elif self.remote_status is False:
                        payload = json.dumps({'cmd': 'cam_off'})
                        self.client.publish('auto', payload)

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
            payload = json.loads(message.payload.decode("utf-8"))
            topic = message.topic
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")
            if topic == 'pitank':
                pass
            elif topic == 'move':
                pass
            elif topic == 'view':
                pass
            elif topic == 'sensors':
                pass
            elif topic == 'remote':
                if payload['status'] == 'on':
                    self.remote_status = True
                elif payload['status'] == 'off':
                    self.remote_status = False


        except Exception as e:
            logging.debug(f"{type(self).__name__},{e}")


if __name__ == "__main__":
    Auto()
