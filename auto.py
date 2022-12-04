import logging
import sys

from utils import *

import time
import json


class Auto:
    def __init__(self):
        self.subscriber_name = [('view', 0), ('pitank', 0), ('sensors', 0)]
        self._run = True

        self.main_cf = load_conf('MAIN')

        self.mqttBroker = self.main_cf['mosquitto_ip']
        self.m_user = self.main_cf['mosquitto_user']
        self.m_pass = self.main_cf['mosquitto_pass']

        log_level = self.main_cf['log_level']
        set_logging(log_level)

        self.client = mqtt.Client(f"{type(self).__name__} publisher")
        self.client.username_pw_set(self.m_user, self.m_pass)
        self.client.connect(self.mqttBroker)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(self.m_user, self.m_pass)
        self.client_sub.connect(self.mqttBroker)

        self.run()

    def run(self):
        self.client_sub.loop_start()
        self.client_sub.subscribe(self.subscriber_name)
        self.client_sub.on_message = self.on_message
        try:
            while self._run:
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
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")

        except Exception as e:
            print(e)

if __name__ == "__main__":
    Auto()