from camera.ArucoMarkerDetector.ArucoDetector import ArucoDetector
import time
import yaml
import sys
from pkg_resources import resource_string

class ArucoDetectorPipeline():
    def __init__(self):
        #with open(r'/home/pi/CheemsCity/Robot/packages/camera/FinalCalibration.yml') as file:
            #calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
        file = resource_string('camera', 'FinalCalibration.yml')
        calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
        self.cam_matrix = calibration_data['camera_matrix']
        self.dist_coeff = calibration_data['distortion_coefficient']
        
        self.detector = ArucoDetector(self.cam_matrix, self.dist_coeff)

    def arucoDetector(self, raw_image):
        #correggo la curvatura derivante dalla camera
        self.image = self.detector.undistort(raw_image)
        #self.image = raw_image
        #calcolo le coordinate dei vertici dei quadrati
        corner = self.detector.frameDetector(self.image)
        #calcolo il vettore distanza dalla camera e la rotazione rispetto ad essa per ogni aruco marker
        rvec, tvec, _ = self.detector.estimatePoseMarkers()
        #stampo sull'immagine i rettangoli intorno ai marker
        self.image = self.detector.drawDetectedMarkers(self.image)
        #stampo sull'immagine gli assi centrati
        self.image = self.detector.drawAxis(self.image)
        return self.image
    
    def printImage(self):
        key = self.detector.printImage(self.image)
        return key

    def close(self):
        self.detector.close()
        

if __name__ == '__main__':
    from camera.CameraStream import CameraStream

    vs = CameraStream().start()
    time.sleep(1.0)
    detector = ArucoDetectorPipeline()

    white_flag = True
    while white_flag:
        raw_image = vs.read()
        detector.arucoDetector(raw_image)
        key = detector.printImage()
        if key == 27:         # wait for ESC key to exit and terminate progra,
            detector.close()
            white_flag = False

    sys.exit("[INFO] Chiudo l'ArucoDetector")
