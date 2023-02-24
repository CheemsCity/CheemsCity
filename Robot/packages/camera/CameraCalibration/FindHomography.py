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
from pkg_resources import resource_string
from chessboard import Chessboard
import yaml
import matplotlib.pyplot as plt
'''COME FUNZIONA: 
    bisogna avere una scacchiera (appoggiata al terreno) e un punto di riferimento fisso dove il robot viene messo
    (TO-DO: creare file di stampa con scacchiera e punto dove posizionare ROBOT).
    Si vogliono trasformare le coordinate in pixel della scacchiera in coordinate di 
    un sistema di riferimento piano con origine nel ROBOT'''

vs = CameraStream().start()
time.sleep(2.0)

file = resource_string('camera', 'Calibration160.yml')
calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

with open(r'camera_calibration_settings.yaml') as file:
    settings = yaml.full_load(file)

birdview = BirdView(matrix, dist_coef)
chessboards = []

ret = False

while not ret:
    frame = vs.read()
    rect = birdview.undistort_faster(frame)
    print("[INFO] immagine letta e rettificata")
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH

    offsety = 3 * settings['camera_calibration_squareSize']
    offsetx = 0.102
    board_offset = np.array([offsetx, -offsety])

    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
    cv2.imshow("immagine 1", rect)

    #nota, se hai una scacchiera non quadrata, il lato lungo deve essere messo parallelo alla direzione della fotocamera del robot
    ##luce sembra influire molto!!
    print("[INFO] calcolo chessboard")
    chessboard = Chessboard(
        nx=settings['camera_calibration_chessboardY'],
        ny=settings['camera_calibration_chessboardX'],
        frame=rect,
        square_size=settings['camera_calibration_squareSize'],
        flag=flags)  #metri
    ret = chessboard.ret
    print(ret)
    print("\n")
    if chessboard.ret == True:
        print("[INFO] Scacchiera riconosciuta")
        cv2.drawChessboardCorners(rect,
                                  (settings['camera_calibration_chessboardY'],
                                   settings['camera_calibration_chessboardX']),
                                  chessboard.imgpoints, chessboard.ret)

        print("[info] sto disegnando")
        imgplot = plt.imshow(rect)
        plt.show()

        #punti del nuovo sistema di riferimento, l'origine della scacchiera sarà nel suo
        #punto in basso a destra (questo spiega l'offset)

        src_pts = []
        square_size = settings['camera_calibration_squareSize']
        for r in range(settings['camera_calibration_chessboardY']):
            for c in range(settings['camera_calibration_chessboardX']):
                src_pts.append(
                    np.array([r * square_size, c * square_size],
                             dtype='float32') + board_offset)

        #noi vogliamo che lo zero nel nuovo piano si trovi nel Robot,
        #quindi dato che le immagini di opencv sono array nel cui punto più alto sta lo zero
        #dovremo invertire la lista dei punti delle coordinate che cerchiamo
        src_pts.reverse()

        print("[INFO] calcolo matrice omografica")
        print("[INFO] premere x sull'immagine per andare avanti")
        H, _mask = cv2.findHomography(
            chessboard.imgpoints.reshape(len(chessboard.imgpoints), 2),
            np.array(src_pts), cv2.RANSAC)

        #save MATRIX:
        print("[INFO] salvataggio matrice")
        calibration_data = {
            "H_matrix": H,
        }

        with open('../homography.yml', 'w') as outfile:
            yaml.dump(calibration_data, outfile, default_flow_style=False)

        print("[INFO] salvataggio effettuato")

print(" \n fine")
