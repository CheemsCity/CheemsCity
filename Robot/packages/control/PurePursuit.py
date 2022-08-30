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
# The FullLoader parameter handles the conversion from YAML
# scalar values to Python the dictionary format
calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

file = resource_string('camera.LineDetector','birdview_settings.yaml')
data = yaml.full_load(file)
source_points = data['source']
dest_points = data['dest']

birdview = BirdView(source_points, dest_points, matrix, dist_coef)

pipeline = LineDetectorPipeline()

#Liste che conservano il valore dei punti
Road_points_p1 = []
Road_points_p2 = []

Start = True

while True:
    image = vs.read()
    if Start:
        h, w = image.size
        Start = False
    
    lines = pipeline.lineDetector(image)

    #TO-DO: ragionare sulla geometria di proiezione dei punti sul terreno

    if lines is not None:
        for line in lines:
            p1, p2 = line.reshape(2,2)
            Road_points_p1.append(p1)
            Road_points_p2.append(p2)
    
    #per poter effettuare più operazioni sui punti dobbiamo passare
    #ad un array numpy
    Road_vec1 = np.array(Road_points_p1, ndmin = 2)
    Road_vec2 = np.array(Road_points_p2, ndmin = 2)

    #normalizziamo i punti rispetto alla foto
    #i punti avranno come zero la dimensione dell'immagine - il punto 
    # di taglio del roi, per questo motivo va aggiunto
    roi_vect = np.array((0, 200))

    #creiamo un vettore che permette di ottenere tutti valori compresi tra
    # 0 e 1
    #Normalize_vector = np.array((1.0/w, 1.0/h))

    #normalizzazione
    #Road_vec1 = (Road_vec1 + roi_vect) * Normalize_vector
    #Road_vec2 = (Road_vec2 + roi_vect) * Normalize_vector

    Road_vec1 = (Road_vec1 + roi_vect)
    Road_vec2 = (Road_vec2 + roi_vect)

    #otteniamo quante più informazioni possibili da questi punti:
    

