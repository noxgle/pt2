# venv/bin/python
import termios, fcntl, sys, os
import sys
import socket
import json
import time
from utils import *
import paho.mqtt.client as mqtt

remote_type='bt'

main_cf = load_conf('MAIN')
#mqttBroker = 'pt2.local'
mqttBroker = '192.168.200.237'
m_user = main_cf['mosquitto_user']
m_pass = main_cf['mosquitto_pass']



client = mqtt.Client("Remote control")
client.username_pw_set(m_user, m_pass)
client.connect(mqttBroker,keepalive=0)


fd = sys.stdin.fileno()

oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

try:
    while True:
        try:
            c = sys.stdin.read(1)
            if c:
                if c == "w":
                    client.publish("remote", json.dumps({'cmd': 'forward'}),qos=0)
                elif c == "s":
                    client.publish("remote", json.dumps({'cmd': 'backward'}),qos=0)
                elif c == "a":
                    client.publish("remote", json.dumps({'cmd': 'left'}),qos=0)
                elif c == "d":
                    client.publish("remote", json.dumps({'cmd': 'right'}),qos=0)
                elif c == " ":
                    client.publish("remote", json.dumps({'cmd': 'break'}),qos=0)
                elif c == "1":
                    client.publish("remote", json.dumps({'cmd': 'cam_on'}), qos=1)
                elif c == "2":
                    client.publish("remote", json.dumps({'cmd': 'cam_off'}), qos=1)
                elif c == "q":
                    # client.publish("remote", 'stop')
                    break
                elif c == '\x1b':
                    break
                else:
                    print("Got character", repr(c))
            else:
                time.sleep(0.1)
        except KeyboardInterrupt:
            break

        except IOError:
            pass
        except Exception as e:
            print(e)
finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    sys.exit()
