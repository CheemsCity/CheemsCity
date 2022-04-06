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
from camera.LineDetector.pipelineTest import LineDetectorPipeline
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
motor = Motor(left_trim=-6)

pipeline = LineDetectorPipeline()

while True:
    image = vs.read()
    areas, basePoint, curve = pipeline.lineDetector3(image)
    curve = curve//3
    sen = 1.3
    maxControl = 15
    basepower = 60
    thresh = 2000
    
    #prima condizione: presenza cheemsVicini = stop
    for area in areas:
        if area > thresh:
            '''attiviamo la funzione di stop'''
            motor.Stop()
            break
            
    #seconda parte: riconoscimento linee e direzione strada
    if curve > maxControl: curve = maxControl
    if curve < -maxControl: curve = - maxControl
    print(curve)
    #definiamo la deadzone
    #if curve >0:
       # sen = 1.7
       # if curve<5: curve = 0
    #else:
        #if curve>-5: curve = 0
    powerRight = basepower - curve*sen
    powerLeft = basepower + curve*sen
    print("motore destro: ", powerRight, " e motore sinisto", powerLeft)
    motor.Power('l', powerLeft)
    motor.Power('r', powerRight)





