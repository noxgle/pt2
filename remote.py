import logging
import sys

from utils import *
from bluetooth import *
import time
import json
import threading
import subprocess
import socket


class Remote:
    def __init__(self):
        self.subscriber_name = [('pitank', 0), ('sensors', 0)]
        self._run = True

        self.main_cf = load_conf('MAIN')
        self.bluetooth_cf = load_conf('BLUETOOTH')

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
        self.client.connect(self.mqttBroker, keepalive=0)

        self.client_sub = mqtt.Client(f"{type(self).__name__} subscriber")
        self.client_sub.username_pw_set(self.m_user, self.m_pass)
        self.client_sub.connect(self.mqttBroker,keepalive=0)

        self.bluetooth_server = Bluetooth_controller(self)
        self.bluetooth_server.start()

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
        self.bluetooth_server.stop()
        self._run = False

    def on_message(self, client, userdata, message):

        try:
            payload = json.loads(message.payload.decode("utf-8"))
            logging.debug(f"{type(self).__name__}: topic received message: {message.topic}, {payload}")

        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")


class Bluetooth_controller(threading.Thread):
    def __init__(self, remote):
        threading.Thread.__init__(self)
        self._run = True
        self.setDaemon(True)
        self.remote = remote
        self.controller = self.remote.bluetooth_cf['controller']

    def client_connect(self, server_sock):
        client_sock, client_info = server_sock.accept()
        logging.debug(f"{type(self).__name__}: Accepted connection from  {client_info}")
        self.remote.client.publish("remote", json.dumps({'status': 'on'}), qos=1)
        try:
            while True:
                payload = client_sock.recv(1024)
                if len(payload) == 0: break
                logging.debug(f"{type(self).__name__}: received {payload}")
                if self.controller == 'server':
                    self.remote.client.publish("remote", payload.decode('UTF-8'), qos=0)
                elif self.controller == 'bluedot':
                    data = payload.decode('UTF-8').rstrip('\n').split(",")
                    if len(data) == 5:
                        self.remote.client.publish("remote", json.dumps({'cmd': 'joystick', 'data': data}), qos=0)

                # client_sock.send('')
        except IOError as e:
            logging.warning(f"{type(self).__name__}: {e}")
        finally:
            self.remote.client.publish("remote", json.dumps({'status': 'off'}), qos=1)
            client_sock.close()

    def run(self):
        time.sleep(5)
        cmd = '/usr/bin/sudo /usr/bin/hciconfig hci0 piscan'
        try:
            subprocess.check_output(cmd, shell=True)
        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")

        s = BluetoothSocket(RFCOMM)
        s.bind(("", PORT_ANY))
        s.listen(1)
        port = s.getsockname()[1]
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        advertise_service(s, "SampleServer",
                          service_id=uuid,
                          service_classes=[uuid, SERIAL_PORT_CLASS],
                          profiles=[SERIAL_PORT_PROFILE],
                          # protocols = [ OBEX_UUID ]
                          )

        while self._run:
            logging.info(f"{type(self).__name__}: waiting for connection on RFCOMM channel %d" % port)
            self.client_connect(s)
            logging.info(f"{type(self).__name__}: disconnected")
        s.close()
        sys.exit()

    def stop(self):
        self._run = False


if __name__ == "__main__":
    Remote()
