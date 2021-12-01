import cv2
import numpy as np
import math

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
        self.rvec = None
        self.tvec = None
        self._ = None
        #lunghezza di un lato di un marker nelle dimensioni reali in metri
        self.markerLength = 0.03

    def undistort(self, raw_image):
        #annullare gli effetti di curvatura della camera
        #gray = cv2.cvtColor(raw_image, cv2.COLOR_BGR2GRAY)
        image = cv2.undistort(raw_image, self.cam_matrix, self.dist_coeff, None, self.cam_matrix)
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
        self.rvec, self.tvec, self._ = cv2.aruco.estimatePoseSingleMarkers(self.corners, self.markerLength, self.cam_matrix, self.dist_coeff)
        return self.rvec, self.tvec, self._

    def rodrigues(self, r):
        #applico la formula di rodrigues per la trasformazione di un vettore rotazione in una matrice di rotazione
        #https://courses.cs.duke.edu/fall13/compsci527/notes/rodrigues.pdf
        #pag 5
        theta = np.linalg.norm(r)
        u = np.array(r / theta)
        cross_u = np.array([[0,-u[2],u[1]],[u[2],0,-u[0]],[-u[1],u[0],0]])
        R = np.array(np.eye(3)*math.cos(theta) + (1-math.cos(theta))*np.matmul(u,u.T) + cross_u*math.sin(theta))
        return R

    def drawDetectedMarkers(self, image):
        #disegna un rettangolo attorno ai marker, a mano questo codice disegna i sementi tra i punti definiti in corners
        return cv2.aruco.drawDetectedMarkers(image, self.corners)

    def drawAxis(self, image):
        #disegna i sistemi di riferimento centrati nel cetro dei vari marker, a mano rvec mi da la distanza dalla camera al centro dei marker
        #tvec mi da una rotazione del marker e markerLegnth mi da la lunghezza vera del lato del marker
        #questi dati mi permettono di definire le coordinate 3D del centro e dei corner, a quel punto basta definire il piano passante
        #per i 4 punti e si ha il sistema di riferimento
        for i in range(len(self.ids)):
            image = cv2.aruco.drawAxis(image, self.cam_matrix, self.dist_coeff, self.rvec[i], self.tvec[i], self.markerLength/2)
        return image

    def printImage(self, image):
        comboBig = cv2.resize(image, (640,480))
        cv2.imshow("frame", comboBig)
        key = cv2.waitKey(1) & 0xFF
        #TODO il programma non ha una safe exit, l'unico modo per chiuderlo è usare killall python, un po' brutale