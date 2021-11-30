import cv2
import matplotlib.pyplot as plt
import numpy as np

class ArucoDetector:

    def __init__(self, cam_matrix, dist_coeff):
        #prendo il dizionario dei 50 simboli aruco 6x6
        self.dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
        #qua posso definire paramtri personalizzati, per ora vanno bene quelli standard
        self.params = cv2.aruco.DetectorParameters_create()
        self.cam_matrix = cam_matrix
        self.dist_coeff = dist_coeff
        self.corners = None
        self.ids = None
        self.rejected = None
        #lunghezza di un lato di un marker nelle dimensioni reali in metri
        self.markerLength = 0.06

    def undistort(self, raw_image):
        #annullare gli effetti di curvatura della camera
        gray = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        image = cv2.undistort(gray, self.cam_matrix, self.dist_coeff, None, self.cam_matrix)
        return image

    def frameDetector(self, image):
        try:
            #funzione presente in cv2 per il riconoscimento degli aruco markers
            (self.corners, self.ids, self.rejected) = cv2.aruco.detectMarkers(image, self.dict, parameters=self.params)
            print("[INFO] Trovati {:d} aruco\n".format(len(self.ids)))
        except:
            print("[ERRORE] Impossibile riconoscere i markers\n")
        return self.corners
    
    def estimatePoseMarkers(self):
        #questa funzione mi restituisce le cooridnate del centro del marker nel sistema di rifermineto centrato nella camera
        #le coordinate dei vertici del marker sono (-markerLength/2, markerLength/2, 0), (markerLength/2, markerLength/2, 0), (markerLength/2, -markerLength/2, 0), (-markerLength/2, -markerLength/2, 0)
        return cv2.aruco.estimatePoseSingleMarkers(self.corners, self.markerLength, self.cam_matrix, self.dist_coeff)