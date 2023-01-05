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
    """
    The PiTank class is responsible for starting and stopping other modules, as well as communicating with them using
    the MQTT protocol. In order to start the appropriate modules, it reads a configuration file in which the options
    for turning on individual modules are set. In addition, this class can set logging options and MQTT broker
    connection options based on the configuration file.

    During the program's operation, the PiTank receives messages
    from other modules using MQTT and is able to stop the operation of all modules and end the operation of the
    entire program. This is achieved through the start() method, which starts all modules, and the stop() method,
    which stops the operation of all modules and ends the operation of the entire program.

    This class also allows for the receipt of messages from other modules using MQTT and their logging. To do this,
    the on_message() method is used, which is called after the broker receives a message.
    """

    def __init__(self):
        self.subscriber_name = [('auto', 0), ('move', 0), ('remote', 0), ('sensors', 0)]
        self.modules_name = []
        self.modules = {}

        self.main_cf = load_conf('MAIN')
        self.module_cf = load_conf('MODULE')

        log_level = self.main_cf['log_level']
        if self.main_cf['log_to_file'] == 'True':
            set_logging(log_level, True)
        elif self.main_cf['log_to_file'] == 'False':
            set_logging(log_level, False)
        else:
            sys.exit()

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
        if sensors_enable == 'True':
            self.modules_name.append('sensors')
        if auto_enable == 'True':
            self.modules_name.append('auto')

        self.client_pub = mqtt.Client(f"{type(self).__name__} publisher")
        self.client_pub.username_pw_set(m_user, m_pass)
        self.client_pub.connect(mqttBroker, keepalive=0)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(m_user, m_pass)
        self.client_sub.connect(mqttBroker, keepalive=0)

    def on_message(self, client, userdata, message):

        try:
            payload = json.loads(message.payload.decode("utf-8"))
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")

        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")

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
