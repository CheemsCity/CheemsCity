import cv2
import numpy as np
import matplotlib.pyplot as plt
from pkg_resources import resource_string
import yaml


class BirdView:
    '''Class used for images transformation for autonomous driving.
    
    Birdview collects methods and variables needed to calculate important points on 
    the image and to apply geometrical transformations. It's the most important class
    for image analysis for autonomous driving. 
    
    '''

    def __init__(self,
                 cam_matrix,
                 distortion_coeff,
                 Hmatrix=False,
                 view_points=None,
                 sky_points=None):
        self.vpoints = view_points
        self.spoints = sky_points
        self.view_points = np.array(view_points, np.float32)
        self.sky_points = np.array(sky_points, np.float32)
        self.cam_matrix = cam_matrix
        self.dist_coeff = distortion_coeff
        self.sky_matrix = None

        if Hmatrix:
            file = resource_string('camera', 'homography.yml')
            calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
            self.sky_matrix = calibration_data['H_matrix']
            #self.sky_matrix[1, :] = self.sky_matrix[1, :] * -1

        else:
            try:
                self.sky_matrix = cv2.getPerspectiveTransform(
                    self.view_points, self.sky_points)
                self.inv_sky_matrix = cv2.getPerspectiveTransform(
                    self.sky_points, self.view_points)
            except:
                print("Homography matrix not declared")
        self.start = True
        self.mapx, self.mapy = None, None

    def undistort(self, raw_image):

        image = cv2.undistort(raw_image, self.cam_matrix, self.dist_coeff,
                              None, self.cam_matrix)
        return image

    def undistort_faster(self, raw_image):
        ''' undistort an image faster than cv2.undistort.
        
        it saves the undistort map (a function from the distorted image to the 
        undistorted) for future usage, while cv2.undistort needs to recreate the map 
        everytime it gets called.
        
        Args:
            raw_image: an image
        
        Returns:
            An binary image unidstorted from radial and tangential distortion
            
        '''
        if self.start:
            h, w = raw_image.shape[:2]
            self.mapx, self.mapy = cv2.initUndistortRectifyMap(
                self.cam_matrix, self.dist_coeff, None, self.cam_matrix,
                (w, h), 5)
            self.start = False
        return cv2.remap(raw_image, self.mapx, self.mapy, cv2.INTER_LINEAR)

    def sky_view_points(self, points):
        '''Calculate the new points' coordinates in the skyview image.

        ITA: funzione che permette di calcolare le coordinate di un insieme di punti
        nell'immagine post skyview
        '''
        if self.sky_matrix is None:
            print("Homography matrix missing")
            return None
        vector = np.append(points, np.array([1]))
        ground_point = np.dot(self.sky_matrix, vector)
        x = ground_point[0]
        y = ground_point[1]
        z = ground_point[2]

        skyPoints = np.array([(y / z), (x / z)])
        return skyPoints

    def sky_view(self, ground_image):
        '''Apply the skyview transformation to an image.

        This function return the image but seen from a different point of view: the top;
        The method needs a sky matrix, that can be calculated with a camera calibration 
        or by manually passing some points in the initialization of the class.
        ex. an image of a road will be returned as it was taken from the sky. 
        '''
        if self.sky_matrix is None:
            print("[ERROR] Homography matrix missing")
            return ground_image
        temp_image = self.undistort_faster(ground_image)
        shape = (temp_image.shape[1], temp_image.shape[0])
        warp_image = cv2.warpPerspective(temp_image,
                                         self.sky_matrix,
                                         shape,
                                         flags=cv2.INTER_LINEAR)
        return warp_image

    def DrawHough(self, image, binary):
        #NOTES: ragionare se ha senso tenerla
        '''Metodo che utilizza la trasformazione Hough per trovare le 
        linee della strada (come equazioni di primo grado) nell'immagine 
        che ha gia subito il ROI ed i vari filtri.
        Restituisce l'immagine completa con disegnate le linee della strada'''

        #print("[INFO] sta avvenendo la trasformazione Hough")
        lines = cv2.HoughLinesP(binary,
                                rho=2,
                                theta=np.pi / 180,
                                threshold=60,
                                minLineLength=20,
                                maxLineGap=5,
                                lines=np.array([]))
        left = []
        right = []
        #print("[INFO] divisione linee destra e sinistra")
        try:
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                parameters = np.polyfit((x1, x2), (y1, y2), 1)
                slope = parameters[0]
                y_int = parameters[1]
                if (slope < 0 and slope > -2):
                    left.append((slope, y_int))
                elif (slope < 2):
                    right.append((slope, y_int))

            #print("[INFO] calcolo average")
            #print("[INFO] media destra")
            right_avg = np.average(right, axis=0)
            #print("[INFO] media sinistra")
            left_avg = np.average(left, axis=0)
            #print("[INFO] left_line, makepoints")
            left_line = self.make_points(binary, left_avg)
            #print("[INFO] right_line, makepoints")
            right_line = self.make_points(binary, right_avg)
            coordinates = [left_line, right_line]

            z = np.zeros_like(binary)
            lines_image = np.dstack((z, z, z))
            #print("[INFO] rappresetazione linee medie")
            for x1, y1, x2, y2 in coordinates:
                print("coeff : ", x1, " ", y1, " |  ", x2, "- ", y2)
                cv2.line(lines_image, (x1, y1), (x2, y2), (255, 255, 0), 10)
                print("avvenuto riconoscimento")
            combo = cv2.addWeighted(image, 1, lines_image, 0.3, 0)
            print("return image Weighted")
            return combo
        except:
            return image

    def hough(self, binary):
        """Apply the Hough transformation to an image.
        
        Args:
            binary: binary image (made by 0 and 1, only one channel).
        """
        lines = cv2.HoughLinesP(binary,
                                rho=1,
                                theta=np.pi / 180,
                                threshold=2,
                                minLineLength=3,
                                maxLineGap=1,
                                lines=np.array([]))

        return lines

    def get_histogram(self, binary, region, minPer=0.1, display=False):
        '''Calculate the number of white pixels for every columns of the image.
        
        Funzione che calcola per ogni colonna dell'immagine la quantità di pixel
        bianchi e restituisce poi la posizione di una W media ottenuta facendo la
        media pesata delle colonne. In modalità display TRUE è possibile vedere 
        rappresentati i dati in un istogramma.
        Casi d'uso: ottenere il valore w medio verso cui tende una strada a partire
        da un'immagine in bianco e nero.
        
        Args:
            binary: binary image (made by 0 and 1, only one channel).
            region: an integer that define the ROI of interest.
            minPer: a value to filter the columns with little white pixels.
        '''

        histValues = np.sum(binary[-binary.shape[0] // region:, :], axis=0)
        maxValue = np.max(histValues)
        minValue = minPer * maxValue

        indexArray = np.where(histValues >= minValue)
        basePoint = int(np.average(indexArray))

        if display:
            imgHist = np.zeros((binary.shape[0], binary.shape[1], 3), np.uint8)
            for x, intensity in enumerate(histValues):
                cv2.line(imgHist, (x, binary.shape[0]),
                         (x, binary.shape[0] - intensity // 255 // region),
                         (255, 0, 255), 1)
                cv2.circle(imgHist, (basePoint, binary.shape[0]), 20,
                           (0, 255, 255), cv2.FILLED)
                cv2.imshow("Display Histogram", imgHist)

        return basePoint

    def hough_center(self, binary, x: int):
        '''funzione che restituisce la coordinata y (width)
        del centro della strada ad una data altezza x
        (più è in basso nell'immagine,maggiore il valore di x).
        Questo metodo effettua solo i calcoli e non disegna le 
        linee sull'immagine'''
        lines = cv2.HoughLinesP(binary,
                                rho=2,
                                theta=np.pi / 180,
                                threshold=60,
                                minLineLength=20,
                                maxLineGap=5,
                                lines=np.array([]))
        left = []
        right = []

        try:
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                parameters = np.polyfit((x1, x2), (y1, y2), 1)
                slope = parameters[0]
                y_int = parameters[1]
                if (slope < 0 and slope > -2):
                    left.append((slope, y_int))
                elif (slope < 2):
                    right.append((slope, y_int))

            #print("[INFO] calcolo average")
            #print("[INFO] media destra")
            right_avg = np.average(right, axis=0)
            #print("[INFO] media sinistra")
            left_avg = np.average(left, axis=0)
            #print("[INFO] left_line, makepoints")
            slopeLeft, yLeft = left_avg
            slopeRight, yRight = right_avg
            yL = slopeLeft * x + yLeft
            yR = slopeRight * x + yRight
            return (yL - yR)
        except:
            return None