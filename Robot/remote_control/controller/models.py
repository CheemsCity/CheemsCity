from django.db import models
from camera.CameraStream import CameraStream
import time


#qui chiamo direttamente le funzioni del pacchetto camera
#NOTA: passo da qua perché se chiamo diretto CameraStream mi vengono degli errori sull'istanza iterata della cam ad ogni chiamata della vista
class Camera(models.Model):
    def __init__(self):
        self.cam = CameraStream()
        self.cam.start()
        time.sleep(1.0)

    def __del__(self):
        self.cam.stop()

    def frame_clear(self):
        f = self.cam.frame_clear()
        return f

    def frame_cheems_detector(self):
        f = self.cam.frame_cheems_detector()
        return f

    def frame_aruco_detector(self):
        f = self.cam.frame_aruco_detector()
        return f
    
    def frame_camera_calibration(self):
        f, chessboard, h ,w = self.cam.frame_camera_calibration()
        return f, chessboard, h, w
