#!/bin/bash
# 
# Script start in project folder.

sudo systemctl stop pt2
sudo systemctl disable pt2
sudo rm /etc/systemd/system/pt2.service
sudo rm /usr/lib/systemd/system/pt2.service
sudo systemctl daemon-reload
sudo systemctl reset-failed

