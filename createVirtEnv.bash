#!/bin/bash
# 
# Script start in project folder.
DIR=`pwd`

if ! [ -x "$(command -v pip3)" ]; then
  echo 'Error: pip3 is not installed.' >&2
  exit 1
fi

if ! [ -x "$(command -v virtualenv)" ]; then
  echo 'Error: virtualenv is not installed.' >&2
  exit 1
fi

virtualenv --python=/usr/bin/python3 --system-site-packages venv
#virtualenv --python=/usr/bin/python3 venv
source $DIR/venv/bin/activate
pip3 install pip --upgrade
pip3 install --upgrade pip setuptools wheel
pip3 install -r requirements.txt
deactivate