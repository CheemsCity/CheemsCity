import cv2
from picamera import PiCamera
from threading import Thread
import time
import numpy as np
import os
from camera.LineDetector.BirdView import BirdView
from camera.LineDetector.Curves import curves
from camera.LineDetector.LaneFilter import LaneFilter 
from camera.CameraStream import CameraStream
from PID import PID
from pkg_resources import resource_string
from hardware.Motor import Motor

vs = CameraStream().start()
time.sleep(2.0)

import yaml
file = resource_string('camera', 'FinalCalibration.yml')
#with open(r'FinalCalibration.yml') as file:
# The FullLoader parameter handles the conversion from YAML
# scalar values to Python the dictionary format
calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

lanefilter = LaneFilter()

matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

#height = 240
#source_points = [(0, height), (300, height), (250,150), (50, 150)]
#dest_points = [(100, height), (220, height), (220, 0), (100, 0)]

file = resource_string('camera.LineDetector','birdview_settings.yaml')
data = yaml.full_load(file)
source_points = data['source']
dest_points = data['dest']

birdview = BirdView(source_points, dest_points, matrix, dist_coef)
curve = curves(9, 20, 50)

print("prova 1, pre definizione del PID")
basePower = 50
pid = PID(0,0,0)
print("definizione del PID")
pid.tune(0.04,0.04, 0.008)
motor = Motor()



while True:
    
    image = vs.read()
    lane_image = np.copy(image)
    filtered = lanefilter.toCanny(lane_image)
    filtered = lanefilter.ROI(filtered)
    skyview = birdview.sky_view(filtered)
    undistort = birdview.undistort(image)
    result = curve.Detect(skyview,0)

    if result != -1:
        combo = birdview.Visual(image, skyview, result['pixel_left_best_fit_curve'], result['pixel_right_best_fit_curve'])
        comboBig = cv2.resize(combo, (640,480))  
        move = pid.compute(result['Center_distance'])
        powerLeft = basePower - move
        powerRight = basePower + move
        if powerLeft < 0:
            powerLeft = 0
        if powerLeft > 100:
            powerLeft = 100
        if powerRight < 0:
            powerRight = 0
        if powerRight > 100:
            powerRight = 100

        print("Potenza sinistra: " + str(powerLeft))
        print("Potenza destra: " + str(powerRight))
        #motor.Power('l', powerLeft)
        #motor.Power('r', powerRight)
            
        #rappresenta real time tramite delle colonne come cambaino i valori dei motori
        comboBig = cv2.rectangle(comboBig, (50,int(480- (powerLeft * 3))), (100, 480), (255, 0, 0), 5)
        comboBig = cv2.rectangle(comboBig, ((640-100),int(480- (powerRight * 3))), (640-50, 480), (255, 0, 0), 5)
        comboBig = cv2.line(comboBig, (320,480), (320, 0), (0,0,255), 5)
        comboBig = cv2.putText(comboBig,"distanza: " + str( result['Center_distance']), (5, 20) ,cv2.FONT_HERSHEY_SIMPLEX,0.5,(255,255, 0), 2, 1)
        comboBig = cv2.putText(comboBig, "error De = " + str(pid.Derivative),(5, 40),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0),2,1)
        comboBig = cv2.putText(comboBig, "error I = " + str(pid.Integral), (5, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,0), 2, 1)
        cv2.imshow("frame", comboBig)
        key = cv2.waitKey(1) & 0xFF
        
        
        print("[INFO] velocita motore sinistro = " + str(powerLeft) + " , motore destro = " + str(powerRight))

    else:
        comboBig = cv2.resize(lane_image, (640,480))
        cv2.imshow("frame", comboBig)
        key = cv2.waitKey(1) & 0xFF
    

    
        
    
    
