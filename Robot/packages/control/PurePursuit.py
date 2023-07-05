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
from utils.SerialCommunication import SerialCommunication
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

birdview = BirdView(matrix,
                    dist_coef,
                    Hmatrix=True)

pipeline = LineDetectorPipeline()

motor = Motor(left_trim=-10)
print("motor left trim: ")
print(motor._left_trim)
comm = SerialCommunication()

#massimo valore da aggiungere o sottrarre al basePower
maxControl = 20
basepower = 70

Start = True

print("motore destro: ", basepower + 10, " e motore sinisto",  basepower + 10)
motor.power('l', basepower + 10)
motor.power('r', basepower + 10)

while True:
    #Liste che conservano il valore dei punti
    road_points_p1 = []
    road_points_p2 = []
    road_points = []

    image = vs.read()

    if Start:
        h, w = image.shape[:2]
        Start = False

    lines = pipeline.line_detector(image)

    #TO-DO: ragionare sulla geometria di proiezione dei punti sul terreno

    if lines is not None:
        for line in lines:
            p1, p2 = line.reshape(2, 2)
            #road_points_p1.append(p1)
            #road_points_p2.append(p2)
            road_points.append(p1)
            road_points.append(p2)

    #per poter effettuare più operazioni sui punti dobbiamo passare ad un array numpy
    #road_vec1 = np.array(road_points_p1, ndmin=2)
    #road_vec2 = np.array(road_points_p2, ndmin=2)
    road_vec = np.array(road_points, ndmin =2)

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

    #road_vec1 = (road_vec1 + roi_vect)
    #road_vec2 = (road_vec2 + roi_vect)
    road_vec = (road_vec + roi_vect)

    numPoints = road_vec.shape[0] if road_vec.shape[1] == 2 else 0
    sky_list1 = []
    sky_list2 = []
    sky_list = []
    for i in range(numPoints):
        #sky_list1.append(birdview.sky_view_points(road_vec1[i, :]))
        #sky_list2.append(birdview.sky_view_points(road_vec2[i, :]))
        sky_list.append(birdview.sky_view_points(road_vec[i, :]))

    #sky_points1 = np.array(sky_list1, ndmin=2)
    #sky_points2 = np.array(sky_list2, ndmin=2) 
    sky_points = np.array(sky_list, ndmin=2) 
    #TO-DO: sistemare problema matrice omografica, non devo fare un reverse
    #dei punti ma voglio che punto con pixel di valori minore sia il 7 e non+
    #il 9 delle caselle della scacchiera

    #otteniamo quante più informazioni possibili da questi punti:
    #controlliamo siano nel formato giusto
    numPoints = sky_points.shape[0] if sky_points.shape[1] == 2 else 0
    avg_dir = 0
    if numPoints > 1:

        #prendiamo tutti quei punti non troppo distanti dal robot
        #ricordiamo che il centro del loro sistema di riferimento
        #è la telecamera del robot
        #asse 0 array numpy = verticale
        #asse 1 array numpy = orizzontale
        '''l'array numpy sarà così formato:
            [y1 x1
             y2 x2
             ....] '''
        points_keep1 = np.linalg.norm(sky_points, axis=1) < 0.2
        points_keep2 = np.linalg.norm(sky_points, axis=1) > 0.15
        points_keep3 = np.linalg.norm(sky_points, axis=1) < 0.15
        points_keep4 = np.linalg.norm(sky_points, axis=1) > 0.1
        points_keep11 = np.logical_and(points_keep1, points_keep2)
        points_keep22 = np.logical_and(points_keep3, points_keep4)
        #print(np.hstack((sky_points1,np.linalg.norm(sky_points1, axis=1))))
        num_points = np.sum(points_keep11)
        #sky_points1 = sky_points1[points_keep]
        #sky_points2 = sky_points2[points_keep]
        sky_points1 = sky_points[points_keep11]
        sky_points2 = sky_points[points_keep22]

        print("dimensione array: ")
        print(sky_points1.shape)

        xp = sky_points1[sky_points1[:,0]>0 ]
        xn = sky_points1[sky_points1[:,0]<0 ]
        xpm = np.mean(xp[:,0], axis=0)
        xpn = np.mean(xn[:,0], axis=0)
        x = (xpm + xpn)/2
        y = 0.2

        xp2 = sky_points2[sky_points2[:,0]>0 ]
        xn2 = sky_points2[sky_points2[:,0]<0 ]
        xpm2 = np.mean(xp2[:,0], axis=0)
        xpn2 = np.mean(xn2[:,0], axis=0)
        x2 = (xpm2 + xpn2)/2
        y2 = 0.1

        x = xpm- xpm2

        plt.figure(3)
        plt.plot(xp[:, 0], xp[:, 1], 'ro')
        plt.plot(xn[:, 0], xn[:, 1], 'go')
        plt.plot(xpm,0.2, 'bo')
        plt.plot(xpn,0.2, 'bo')
        plt.plot(xpm2,0.1, 'bo')
        plt.plot(xpn2,0.1, 'bo')
        plt.arrow(0, 0, x, 0.15, head_width=0.005, head_length=0.01, fc='k', ec='k', color = 'red')
        plt.arrow(0, 0, 0, 0.2, head_width=0.005, head_length=0.01, fc='k', ec='k', color = 'blue')
        plt.show()
        plt.close()

        '''t = sky_points2 - sky_points1
        t_norm = t / np.linalg.norm(t, axis=1, keepdims=True)
        #avg abs dir è utile per modificare la velocità in funzione della pendenza
        #la normalizziamo in modo da avere un valore da 0 a 1
        avg_abs_dir = np.mean(np.abs(t_norm), axis=0)
        avg_dir_normalized = avg_abs_dir / np.linalg.norm(avg_abs_dir)'''

        '''print("direzione strada normalizzata {}".format(avg_dir_normalized[1]))
        if avg_dir_normalized[1] > 0.6:
            print("- strada dritta ")
        else:
            print("- curva ")
        '''
        '''
        #calcoliamo ora il punto da raggiungere
        points = np.vstack([sky_points1, sky_points2])
        PPpoint = [np.mean(points[:, 0], axis=0), 0.2]
        print("valore del punto da raggiungere: ")
        print(PPpoint[0])
        '''
        '''points_keep2 = np.linalg.norm(sky_points12, axis=1) < 0.6
        num_points2 = np.sum(points_keep2)
        sky_points12 = sky_points12[points_keep2]
        sky_points22 = sky_points22[points_keep2]
        t = sky_points22 - sky_points12
        t_norm = t / np.linalg.norm(t, axis=1, keepdims=True)
        #avg abs dir è utile per modificare la velocità in funzione della pendenza
        #la normalizziamo in modo da avere un valore da 0 a 1
        avg_abs_dir = np.mean(np.abs(t_norm), axis=0)
        avg_dir_normalized = avg_abs_dir / np.linalg.norm(avg_abs_dir)
        print(avg_dir_normalized[1])'''
        '''
        control = (PPpoint[0] * 50)//1
        if control > maxControl: control = maxControl
        if control < (-1)*maxControl: control = (-1)*maxControl
        control = control * (1.3 - (avg_dir_normalized[1])/3)
        print(control)

        if avg_dir_normalized[1] < 0.6:
            basepower = 65
        '''
        '''powerRight = basepower - control
        powerLeft = basepower + control
        print("motore destro: ", powerRight, " e motore sinisto", powerLeft)
        motor.power('l', powerLeft)
        motor.power('r', powerRight)'''

    