# Fresh install
This steps is only for fresh install RASSPBERRY PI (64bit).

## Base install
Before start expand your filesystem:
```
sudo raspi-config 
```
### Step 1: update and upgrade
```
sudo apt update && sudo apt -y upgrade
```
### Step 2: install lib and other stuff
```
sudo apt-get install python3-pip libjpeg-dev libopenblas-dev libopenmpi-dev libomp-dev

sudo apt-get install build-essential libssl-dev libffi-dev python3-dev

sudo apt-get install python3-venv, virtualenv screen

sudo apt-get install mosquitto
```
### Step 3: install and configure mosquitto service:
```
sudo mosquitto_passwd -c -b /etc/mosquitto/passwd pt2 gorkd34!
echo "password_file /etc/mosquitto/passwd" | sudo tee --append /etc/mosquitto/mosquitto.conf
echo "allow_anonymous false" | sudo tee --append /etc/mosquitto/mosquitto.conf
```
### Step 5:
```
reboot
```


## Optional (bluetooth)
### Step 1: install lib and other stuff
```
sudo apt-get install libbluetooth-dev

sudo pip3 install pybluez
```
```
cat /etc/group | grep bluetooth
bluetooth:x:113:pi
```

If it's not, add pi to bluetooth group:
```
sudo usermod -G bluetooth -a pi
```
### Step 2: install service:
```
cd install && ./install_service_bt.bash
```
### Step 5:
```
reboot
```

### Step 6: pairing with Android 
```
bluetoothctl
```
Paste below one by one in console:
- discoverable on
- pairable on
- agent on
- default-agent
- scan on

Now try to connect from your Android device with bluetooth, you need accept connections in console
After if you have active connections you can install "BlueDot" from google play. And from this app you can control robot 
move.