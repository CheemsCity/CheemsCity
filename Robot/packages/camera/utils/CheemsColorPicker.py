import os
import time

import cv2
import numpy as np
from pkg_resources import resource_string
from picamera import PiCamera
from threading import Thread
import yaml

from camera.LineDetector.LaneFilter import LaneFilter
from camera.CameraStream import CameraStream
from camera.LineDetector.pipeline import LineDetectorPipeline

vs = CameraStream().start()
time.sleep(2.0)

file = resource_string('camera', 'FinalCalibration.yml')
# The FullLoader parameter handles the conversion from YAML
# scalar values to Python the dictionary format
calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

pipeline = LineDetectorPipeline()

def empty(a):
    pass

cv2.namedWindow("HSV")
cv2.createTrackbar("HUE min", "HSV", 0, 179, empty)
cv2.createTrackbar("HUE max", "HSV", 179, 179, empty)
cv2.createTrackbar("SAT min", "HSV", 0, 255, empty)
cv2.createTrackbar("SAT max", "HSV", 255, 255, empty)
cv2.createTrackbar("VALUE min", "HSV", 0, 255, empty)
cv2.createTrackbar("VALUE max", "HSV", 255, 255, empty)

time.sleep(1)

while True:
    h_min = cv2.getTrackbarPos("HUE min", "HSV")
    h_max = cv2.getTrackbarPos("HUE max", "HSV")
    s_min = cv2.getTrackbarPos("SAT min", "HSV")
    s_max = cv2.getTrackbarPos("SAT max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE max", "HSV")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    pipeline.change_cheems_color(lower, upper)
    image = vs.read()
    pipeline.cheems_recognition(image, display = True)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
