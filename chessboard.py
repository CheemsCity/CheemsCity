#abbiamo bisogno di almeno 10 test patter
import numpy as np
import cv2 
import os

class Chessboard:
    def __init__(self, nx, ny, path):
    
        self.nx, self.ny = nx, ny
        self.n = (self.nx, self.ny)
        self.path = path

        #prepariamo gli object points (punti 3D), come (0,0,0), (1,0,0)...
        objp = np.zeros((self.nx*self.ny, 3), np.float32)
        #https://numpy.org/doc/stable/reference/generated/numpy.mgrid.html
        #popoliamo l'array
        objp[:,:2] = np.mgrid[0:self.nx, 0:self.ny].T.reshape(-1,2)

        #Array to store the object points
        self.objpoints = objp  #3d points

        img=cv2.imread(self.path)
        gray = cv2.cvtColor(img, cv.COLOR_BGR2GRAY)

        #trova gli spigoli
        self.ret, corners = cv2.findChessboardCorners(gray, self.n, none)

        #se trovato, aggiungi gli object points e gli image points
        if self.ret == True:
            corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
            self.imgpoints=corners2


                

