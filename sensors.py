import json
import sys
import time
import socket
import logging
from utils import *
import paho.mqtt.client as mqtt


class Network:
    def __init__(self, sensors):
        self.default_ip = None

        self.client = mqtt.Client(f"{type(sensors).__name__} publisher")
        self.client.username_pw_set(sensors.m_user, sensors.m_pass)
        self.client.connect(sensors.mqttBroker)
        self.default_ip=self.get_default_ip()

    def get_default_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception as e:
            logging.warning(f'{type(self).__name__}, {e}')
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP




class Sensors:
    def __init__(self):
        self._run = True

        self.main_cf = load_conf('MAIN')
        self.mqttBroker = self.main_cf['mosquitto_ip']
        self.m_user = self.main_cf['mosquitto_user']
        self.m_pass = self.main_cf['mosquitto_pass']

        log_level = self.main_cf['log_level']
        if self.main_cf['log_to_file'] == 'True':
            set_logging(log_level,True)
        elif self.main_cf['log_to_file'] == 'False':
            set_logging(log_level,False)
        else:
            sys.exit()

        self.netwrok = Network(self)
        self.netwrok.get_default_ip()

        self.run()

    def run(self):
        t_ip = time.time()
        try:
            while self.run:
                if time.time() > t_ip + 10:
                    ip=self.netwrok.get_default_ip()
                    if ip!=self.netwrok.default_ip:
                        payload = json.dumps({'default_ip': self.netwrok.default_ip})
                        self.netwrok.client.publish('sensors', payload)
                        self.netwrok.default_ip=ip
                    t_ip = time.time()
                time.sleep(1)

        except Exception as e:
            print(e)
        finally:
            sys.exit()


if __name__ == '__main__':
    Sensors()
