import os
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from pkg_resources import resource_string
from picamera import PiCamera
from threading import Thread
import yaml

from camera.LineDetector.BirdView import BirdView
from camera.LineDetector.LaneFilter import LaneFilter
from camera.CameraStream import CameraStream
from camera.LineDetector.pipeline import LineDetectorPipeline
from PID import PID
from hardware.Motor import Motor


vs = CameraStream().start()
time.sleep(2.0)

file = resource_string('camera', 'FinalCalibration.yml')
# The FullLoader parameter handles the conversion from YAML
# scalar values to Python the dictionary format
calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

birdview = BirdView(None,
                    None,
                    matrix,
                    dist_coef,
                    Hmatrix=True)

pipeline = LineDetectorPipeline()

#Liste che conservano il valore dei punti
road_points_p1 = []
road_points_p2 = []

Start = True

while True:
    image = vs.read()

    if Start:
        h, w = image.shape[:2]
        Start = False

    lines = pipeline.line_detector(image)

    #TO-DO: ragionare sulla geometria di proiezione dei punti sul terreno

    if lines is not None:
        for line in lines:
            p1, p2 = line.reshape(2, 2)
            road_points_p1.append(p1)
            road_points_p2.append(p2)

    #per poter effettuare più operazioni sui punti dobbiamo passare ad un array numpy
    road_vec1 = np.array(road_points_p1, ndmin=2)
    road_vec2 = np.array(road_points_p2, ndmin=2)

    #normalizziamo i punti rispetto alla foto, i punti avranno come zero la dimensione
    #dell'immagine - il punto di taglio del roi, per questo motivo devo aggiungere 200
    #alle coordinate h.
    roi_h = 200
    roi_vect = np.array((0, roi_h))

    #creiamo un vettore che permette di ottenere tutti valori compresi tra
    # 0 e 1
    #Normalize_vector = np.array((1.0/w, 1.0/h))

    #normalizzazione
    #Road_vec1 = (Road_vec1 + roi_vect) * Normalize_vector
    #Road_vec2 = (Road_vec2 + roi_vect) * Normalize_vector

    road_vec1 = (road_vec1 + roi_vect)
    road_vec2 = (road_vec2 + roi_vect)

    numPoints = road_vec1.shape[0] if road_vec1.shape[1] == 2 else 0
    sky_list1 = []
    sky_list2 = []
    for i in range(numPoints):
        sky_list1.append(birdview.sky_view_points(Road_vec1[i, :]))
        sky_list2.append(birdview.sky_view_points(Road_vec2[i, :]))

    sky_points1 = np.array(sky_list1, ndmin=2)
    sky_points2 = np.array(sky_list2, ndmin=2)

    #otteniamo quante più informazioni possibili da questi punti:
    #controlliamo siano nel formato giusto
    numPoints = sky_points1.shape[0] if sky_points1.shape[1] == 2 else 0
    avg_dir = 0
    if numPoints > 1:

        #prendiamo tutti quei punti non troppo distanti dal robot
        #ricordiamo che il centro del loro sistema di riferimento
        #è la telecamera del robot
        points_keep = np.linalg.norm(sky_points1, axis=1) < 0.7
        num_points = np.sum(points_keep)
        sky_points1 = sky_points1[points_keep]
        sky_points2 = sky_points2[points_keep]
        t = sky_points2 - sky_points1
        t_norm = t / np.linalg.norm(t, axis=1, keepdims=True)
        #avg abs dir è utile per modificare la velocità in funzione della pendenza
        #la normalizziamo in modo da avere un valore da 0 a 1
        avg_abs_dir = np.mean(np.abs(t_norm), axis=0)
        avg_dir_normalized = avg_abs_dir / np.linalg.norm(avg_abs_dir)

        #calcoliamo ora il punto da raggiungere
        points = np.vstack([sky_points1, sky_points2])
        PPpoint = [np.mean(points[:, 0], axis=0), 0.2]

    plt.plot(points[:, 0], points[:, 1], 'ro')
    plt.plot(PPpoint[0], PPpoint[1], 'bo')
    plt.show()
