import cv2
import numpy as np
import math
import yaml

class ArucoDetector:

    def __init__(self, cam_matrix, dist_coeff):
        with open(r'aruco_settings.yaml') as file:
            self.settings = yaml.full_load(file)
        self.arucoDictionary = {
            "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
            "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
            "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
            "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
            "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
            "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
            "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
            "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
            "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
            "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
            "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
            "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
            "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
            "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
            "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
            "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
            "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
            "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
            "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
            "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
            "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
        }.get(self.settings['aruco_dictionary'], 'ERROR')
        #se c'è un errore nella richiesta del dizionario nelle settings
        if(self.arucoDictionary == 'ERROR'):
            print('Dizionario definito nell aruco_settings non esistente (DEFAULT: DICT_6X6_50)\n')
            self.arucoDictionary = cv2.aruco.DICT_6X6_50
        #prendo il dizionario dei simboli aruco definitivi nelle settings
        self.dict = cv2.aruco.Dictionary_get(self.arucoDictionary)
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
        self.markerLength = self.settings['aruco_markerLength']

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
        try:
            for i in range(len(self.ids)):
                image = cv2.aruco.drawAxis(image, self.cam_matrix, self.dist_coeff, self.rvec[i], self.tvec[i], self.markerLength/2)
            return image
        except:
            print("[ERRORE] Non ci sono markers di cui calcolare gli assi")
            return image

    def printImage(self, image):
        comboBig = cv2.resize(image, self.settings['aruco_canvasResolution'])
        cv2.imshow("frame", comboBig)
        key = cv2.waitKey(1) & 0xFF
        return key

    def close(self):
        cv2.destroyAllWindows()