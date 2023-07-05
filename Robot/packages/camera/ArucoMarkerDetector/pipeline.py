from camera.ArucoMarkerDetector.ArucoDetector import ArucoDetector
from camera.StreetLight.StreetLight import StreetLight
import time
import yaml
import sys
from pkg_resources import resource_string


class ArucoDetectorPipeline():

    def __init__(self):
        #with open(r'/home/pi/CheemsCity/Robot/packages/camera/FinalCalibration.yml') as file:
        #calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
        file = resource_string('camera', 'Calibration160.yml')
        calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
        self.cam_matrix = calibration_data['camera_matrix']
        self.dist_coeff = calibration_data['distortion_coefficient']

        self.detector = ArucoDetector(self.cam_matrix, self.dist_coeff)

    def aruco_detector(self, raw_image):
        #correggo la curvatura derivante dalla camera
        self.image = self.detector.undistort(raw_image)
        #self.image = raw_image
        #calcolo le coordinate dei vertici dei quadrati
        corner = self.detector.frameDetector(self.image)
        #calcolo il vettore distanza dalla camera e la rotazione rispetto ad essa per ogni aruco marker
        rvec, tvec, _ = self.detector.estimatePoseMarkers()
        #distanza dal marker numero 0 è pari a tvec[0][0][2] nella stessa unità di misura del aruco_markerLength in aruco_settings.yaml
        #stampo sull'immagine i rettangoli intorno ai marker
        self.image = self.detector.drawDetectedMarkers(self.image)
        #stampo sull'immagine gli assi centrati
        self.image = self.detector.drawAxis(self.image)
        return corner
        return self.image

    def print_image(self, image=None, SO=None, NE=None):
        if ((SO is None or NE is None) and image is None):
            key = self.detector.printImage(self.image)
        elif image is None:
            key = self.detector.printImage(self.image[NE[1]:SO[1],
                                                      SO[0]:NE[0]])
        else:
            key = self.detector.printImage(image)
        return key

    def close(self):
        self.detector.close()


if __name__ == '__main__':
    from camera.CameraStream import CameraStream

    vs = CameraStream().start()
    time.sleep(1.0)
    detector = ArucoDetectorPipeline()
    streetlight = StreetLight()

    white_flag = True
    while white_flag:
        raw_image = vs.read()
        corner = detector.aruco_detector(raw_image)
        streetlight.change_image(raw_image)
        try:
            SO, NE = streetlight.roi(corner[0])
            red, yellow, green = streetlight.color()
        except:
            SO = None
            NE = None
            red = None
            yellow = None
            green = None
            print(' ')
        print([SO, NE])
        #key = detector.printImage(SO=SO,NE=NE)
        key = detector.print_image(image=red)
        if key == 27:  # wait for ESC key to exit and terminate progra,
            detector.close()
            white_flag = False

    sys.exit("[INFO] Chiudo l'ArucoDetector")
