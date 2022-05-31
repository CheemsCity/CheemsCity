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

    def frameClear(self):
        f = self.cam.frameClear()
        return f

    def frameLineDetector(self):
        f = self.cam.frameLineDetector()
        return f

    def frameArucoDetector(self):
        f = self.cam.frameArucoDetector()
        return f
    
    def frameCameraCalibration(self):
        f, chessboard = self.cam.frameCameraCalibration()
        return f, chessboard