from utils import *
import threading
from picamera2 import Picamera2
import time


class Cam(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._run = True
        self.frame = np.zeros((240, 320, 3), np.uint8)

        self.cap = Picamera2()
        # self.cap.configure(self.cap.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))

        # video_config =self.cap.create_still_configuration(main={"size": (320, 240),"format": 'XRGB8888'}, raw={"size":  self.cap.sensor_resolution},controls={"FrameDurationLimits": (16, 16)})
        # video_config['main']['format'] = 'RGB888'
        # self.cap.configure(video_config)
        #self.cap.configure(self.cap.create_preview_configuration({"size": (320, 240)}, raw=self.cap.sensor_modes[1]))
        #self.cap.set_controls({"ExposureTime": 40, "AnalogueGain": 1.5})
        #self.cap.create_video_configuration(raw=self.cap.sensor_modes[0])
        #self.cap.configure(self.cap.create_preview_configuration({"size": (640, 480)}, raw=self.cap.sensor_modes[0]))
        self.cap.configure(self.cap.create_preview_configuration({"size": (320, 240)}, raw=self.cap.sensor_modes[0]))
        # self.cap.configure(video_config)
        self.cap.start()

    def get_frame(self):
        return self.frame

    def run(self):
        time.sleep(2)
        try:
            while self._run:
                frame = self.cap.capture_array('main')
                self.frame = frame
        except Exception as e:
            logging.error(f"{type(self).__name__}: {e}")
        finally:
            self.cap.stop()
            sys.exit()

    def stop(self):
        self._run = False

