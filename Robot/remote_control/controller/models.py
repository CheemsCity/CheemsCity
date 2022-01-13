from django.db import models
from camera.CameraStream import CameraStream
import time


class Camera(models.Model):
    def __init__(self):
        self.cam = CameraStream()
        self.cam.start()
        time.sleep(1.0)

    def __del__(self):
        self.cam.stop()

    def frame(self):
        f = self.cam.frameController()
        return f