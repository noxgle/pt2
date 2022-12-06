Pt2 is software for simple robots (toys) for Raspberry Pi 3/4. This code is for testing and fun.

![Screenshot](diagram.png)

Description

Pt2 have two main service:
- mosquitto broker for communication with process and external services
- pitank it's main process which starts every module

Main modules:
- "auto" is for autonomous actions, default empty
- "view" is for access to camera 
- "move" is used for control engines
- "remote" is for bluetooth remote control 
- "sensors" in this module we can add different sensors, default is network sensor for monitoring ip address  

Pt2 software is used in my prototype robot "prot1".
![Screenshot](prot1.jpg)

- prot1 is moving between lines.

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/L91djZ4qats/0.jpg)](https://youtu.be/L91djZ4qats)