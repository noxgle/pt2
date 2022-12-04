#!/bin/bash
# 
# Script start in project folder.
SRC="/home/pi/workspace/pt2/"
DST="pi@192.168.200.237:pt2/"

rsync -r -a -v --delete --exclude 'venv' --exclude 'tmp' --exclude '__pycache__' --exclude 'design' --exclude '.git' --exclude '.idea' $SRC $DST