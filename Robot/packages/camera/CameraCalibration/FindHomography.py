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

vs = CameraStream().start()
time.sleep(2.0)

file = resource_string('camera', 'Calibration160.yml')
calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
matrix = calibration_data['camera_matrix']
dist_coef = calibration_data['distortion_coefficient']

file = resource_string('camera.LineDetector','birdview_settings.yaml')
data = yaml.full_load(file)
source_points = data['source']
dest_points = data['dest']

with open(r'camera_calibration_settings.yaml') as file:
    settings = yaml.full_load(file)

birdview = BirdView(source_points, dest_points, matrix, dist_coef)
chessboards = []

ret = False

while not ret:
    frame = vs.read()
    rect = birdview.undistortFaster(frame)
    print("[INFO] immagine letta e rettificata")
    flags = cv2.CALIB_CB_ADAPTIVE_THRESH

    offsety = 3*settings['camera_calibration_squareSize']
    offsetx = 0.102
    board_offset = np.array([offsetx, -offsety])

    #nota, se hai una scacchiera non quadrata, il lato lungo deve essere messo parallelo alla direzione della fotocamera del robot
    ##luce sembra influire molto
    print("[INFO] calcolo chessboard")
    chessboard = Chessboard(nx = settings['camera_calibration_chessboardY'], ny = settings['camera_calibration_chessboardX'],frame = rect, square_size = settings['camera_calibration_squareSize'], flag = flags) #metri
    ret = chessboard.ret
    print(ret)
    print("\n")
    if chessboard.ret == True:
        print("[INFO] Scacchiera riconosciuta")
        cv2.drawChessboardCorners(rect, (settings['camera_calibration_chessboardY'],  settings['camera_calibration_chessboardX']), chessboard.imgpoints, chessboard.ret)
        
        print("[info] sto disegnando")
        imgplot = plt.imshow(rect)
        plt.show()

        src_pts = []
        square_size = settings['camera_calibration_squareSize']
        for r in range(settings['camera_calibration_chessboardX']):
            for c in range(settings['camera_calibration_chessboardY']):
                src_pts.append(np.array([r * square_size , c * square_size] , dtype='float32')
                            + board_offset)
        
        print("calcolo matrice omografica")
        H, _mask = cv2.findHomography(chessboard.imgpoints.reshape(len(chessboard.imgpoints), 2), np.array(src_pts), cv2.RANSAC)
        print(H)
        
print(" \n fine")


        
