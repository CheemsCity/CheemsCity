import cv2
from picamera import PiCamera
from CameraStream import CameraStream
from threading import Thread
import time
import numpy as np
import os
from Curves import curves
from LaneFilter import LaneFilter 
from BirdView import BirdView
import matplotlib.pyplot as plt

vs = CameraStream().start()
time.sleep(2.0)

import yaml
with open(r'FinalCalibration.yml') as file:
# The FullLoader parameter handles the conversion from YAML
# scalar values to Python the dictionary format
    calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
    matrix = calibration_data['camera_matrix']
    dist_coef = calibration_data['distortion_coefficient']

lanefilter = LaneFilter()

matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

height = 240
source_points = [(0, height), (300, height), (250,150), (50, 150)]
dest_points = [(100, height), (220, height), (220, 0), (100, 0)]

birdview = BirdView(source_points, dest_points, matrix, dist_coef)
curves = curves(9, 20, 50)

while True:
    image = vs.read()
    lane_image = np.copy(image)
    filtered = lanefilter.toCanny(lane_image)
    filtered = lanefilter.ROI(filtered)
    skyview = birdview.sky_view(filtered)
    undistort = birdview.undistort(image)
    result = curves.Detect(skyview,0)
    if result != -1:
        combo = birdview.Visual(image, skyview, result['pixel_left_best_fit_curve'], result['pixel_right_best_fit_curve'])
        comboBig = cv2.resize(combo, (640,480))
        cv2.imshow("frame", comboBig)
        key = cv2.waitKey(1) & 0xFF
    else:
        comboBig = cv2.resize(lane_image, (640,480))
        cv2.imshow("frame", comboBig)
        key = cv2.waitKey(1) & 0xFF
    
