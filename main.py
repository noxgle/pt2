from utils import *
import subprocess
import paho.mqtt.client as mqtt
import sys
import time
import signal
# from subscriber import *
import json

signal.signal(signal.SIGCHLD, signal.SIG_IGN)


class PiTank:
    def __init__(self):
        self.subscriber_name = [('auto', 0), ('move', 0), ('remote', 0), ('sensors', 0)]
        self.modules_name = []
        self.modules = {}

        self.main_cf = load_conf('MAIN')
        self.module_cf = load_conf('MODULE')

        log_level = self.main_cf['log_level']
        set_logging(log_level)

        mqttBroker = self.main_cf['mosquitto_ip']
        m_user = self.main_cf['mosquitto_user']
        m_pass = self.main_cf['mosquitto_pass']

        module_move_enable = self.module_cf['move_enable']
        view_enable = self.module_cf['view_enable']
        remote_enable = self.module_cf['remote_enable']
        auto_enable = self.module_cf['auto_enable']
        sensors_enable = self.module_cf['sensors_enable']

        if module_move_enable == 'True':
            self.modules_name.append('move')
        if view_enable == 'True':
            self.modules_name.append('view')
        if remote_enable == 'True':
            self.modules_name.append('remote')
        if auto_enable == 'True':
            self.modules_name.append('auto')
        if sensors_enable == 'True':
            self.modules_name.append('sensors')

        self.client_pub = mqtt.Client(f"{type(self).__name__} publisher")
        self.client_pub.username_pw_set(m_user, m_pass)
        self.client_pub.connect(mqttBroker, keepalive=0)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(m_user, m_pass)
        self.client_sub.connect(mqttBroker)

    def on_message(self, client, userdata, message):

        try:
            payload = json.loads(message.payload.decode("utf-8"))
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")

        except Exception as e:
            print(e)

    def run(self):
        self.start()

        self.client_sub.loop_start()
        self.client_sub.subscribe(self.subscriber_name)
        self.client_sub.on_message = self.on_message
        try:

            while True:
                time.sleep(1)

        except Exception as e:
            logging.critical(f"{type(self).__name__}: {e}")
        finally:
            self.client_pub.loop_stop()
            self.client_sub.loop_stop()
            self.stop()

    def start(self):
        for name in self.modules_name:
            try:
                proc = subprocess.Popen(
                    ['venv/bin/python', f"{name}.py"], stdout=subprocess.PIPE)
            except Exception as e:
                print(e)
            self.modules[name] = proc
            time.sleep(0.1)

    def stop(self):
        for name in self.modules:
            self.modules[name].terminate()
            time.sleep(0.1)
        sys.exit()


if __name__ == '__main__':
    pitank = PiTank()
    pitank.run()
