import configparser
import socket
import sys
import cv2
import paho.mqtt.client as mqtt
import numpy as np
import logging


def load_conf(section):
    conf = {}
    try:
        cf = configparser.ConfigParser()
        cf.read_file(open('conf'))
        conf =dict(cf[section])
    except Exception as e:
        print(e)
        sys.exit()
    return conf

def resize_img(img, size, interpolation):
    '''
    :param img: image (frame)
    :param size: resize to width: size, height: size
    :param interpolation: resize interpolation
    :return: resized frame, resize value as dict as like: x_pos, y_pos, ratio
    '''
    h, w = img.shape[:2]
    c = None if len(img.shape) < 3 else img.shape[2]
    if h == w: return cv2.resize(img, (size, size), interpolation), h / size
    if h > w:
        dif = h
    else:
        dif = w
    x_pos = int((dif - w) / 2.)
    y_pos = int((dif - h) / 2.)
    if c is None:
        mask = np.zeros((dif, dif), dtype=img.dtype)
        mask[y_pos:y_pos + h, x_pos:x_pos + w] = img[:h, :w]
    else:
        mask = np.zeros((dif, dif, c), dtype=img.dtype)
        mask[y_pos:y_pos + h, x_pos:x_pos + w, :] = img[:h, :w, :]
    return cv2.resize(mask, (size, size), interpolation), {'x_pos': x_pos, 'y_pos': y_pos, 'ratio': dif / size}

def set_logging(level='error',file=False):
    if level=='debug':
        set_level=logging.DEBUG
    elif level=='info':
        set_level=logging.INFO
    elif level=='warn':
        set_level=logging.WARN
    elif level=='error':
        set_level=logging.ERROR
    elif level=='critical':
        set_level=logging.CRITICAL

    logging.basicConfig(
        level=set_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            #logging.FileHandler("debug.log"),
            logging.StreamHandler()
        ]
    )
