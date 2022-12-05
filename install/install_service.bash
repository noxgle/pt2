#!/bin/bash
# 
# Script start in project folder.

sudo cp pt2.service /etc/systemd/system/
sudo systemctl start pt2
sudo systemctl enable pt2

