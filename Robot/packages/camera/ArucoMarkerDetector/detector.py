from camera.ArucoMarkerDetector.ArucoDetector import ArucoDetector
from camera.CameraStream import CameraStream
import time
import yaml
import sys 


with open(r'../FinalCalibration.yml') as file:
    calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
    cam_matrix = calibration_data['camera_matrix']
    dist_coeff = calibration_data['distortion_coefficient']

vs = CameraStream().start()
time.sleep(2.0)

detector = ArucoDetector(cam_matrix, dist_coeff)

white_flag = True
while white_flag:
    raw_image = vs.read()
    #correggo la curvatura derivante dalla camera
    image = detector.undistort(raw_image)
    #calcolo le coordinate dei vertici dei quadrati
    corner = detector.frameDetector(image)
    #calcolo il vettore distanza dalla camera e la rotazione rispetto ad essa per ogni aruco marker
    rvec, tvec, _ = detector.estimatePoseMarkers()
    #stampo sull'immagine i rettangoli intorno ai marker
    image = detector.drawDetectedMarkers(image)
    #stampo sull'immagine gli assi centrati
    image = detector.drawAxis(image)
    key = detector.printImage(image)
    if key == 27:         # wait for ESC key to exit and terminate progra,
        detector.close()
        white_flag = False

sys.exit("[INFO] Chiudo l'ArucoDetector")