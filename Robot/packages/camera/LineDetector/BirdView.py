import cv2 
import numpy as np
import matplotlib.pyplot as plt

class BirdView:
    
    def __init__(self, view_points, sky_points, cam_matrix, distortion_coeff):
        self.vpoints = view_points
        self.spoints = sky_points
        self.view_points = np.array(view_points, np.float32)
        self.sky_points = np.array(sky_points, np.float32)
        self.cam_matrix = cam_matrix
        self.dist_coeff = distortion_coeff
        
        self.sky_matrix = cv2.getPerspectiveTransform(self.view_points, self.sky_points)
        self.inv_sky_matrix = cv2.getPerspectiveTransform( self.sky_points, self.view_points)
        self.start= True
        self.mapx, self.mapy = None, None

    def undistort(self, raw_image):
     
        image = cv2.undistort(raw_image, self.cam_matrix, self.dist_coeff, None, self.cam_matrix)
        return image
    
    def undistortFaster(self, raw_image):
        '''cv2.undistort chiama il metodo initUndistortRectifyMap ogni volta che viene chiamato,
        spendendo così del tempo a creare ogni volta le mappe. undistortFaster tiene salvate le mappe della
        prima chiamata e applica poi il remap  '''
        if self.start:
            h, w = raw_image.shape[:2]
            self.mapx, self.mapy =  cv2.initUndistortRectifyMap(self.cam_matrix, self.dist_coeff,None, self.cam_matrix,(w,h),5)
            self.start = False
        return cv2.remap(raw_image, self.mapx, self.mapy, cv2.INTER_LINEAR)
    
    def skyViewPoints(self, points):
        '''ITA: funzione che permette di calcolare le coordinate di un insieme di punti nell'immagine
        post skyview
        ENG: this function is used to calculate the coordinates of some points in an image after the
        skyview transformation'''

        #TO-DO
        return skyPoints

    def sky_view(self, ground_image):

        temp_image = self.undistortFaster(ground_image)
        shape = (temp_image.shape[1], temp_image.shape[0])
        warp_image = cv2.warpPerspective(temp_image, self.sky_matrix, shape, flags = cv2.INTER_LINEAR)
        return warp_image

    def make_points(self, image, average):
        slope, y_int = average
        y1 = image.shape[0]
        y2 = int(y1* (3/5))
        x1 = int((y1- y_int) / slope)
        x2 = int((y2 - y_int) / slope)
        return np.array([x1, y1, x2, y2])

    def DrawHough(self, image, binary):
        '''Metodo che utilizza la trasformazione Hough per trovare le 
        linee della strada (come equazioni di primo grado) nell'immagine 
        che ha gia subito il ROI ed i vari filtri.
        Restituisce l'immagine completa con disegnate le linee della strada'''

        #print("[INFO] sta avvenendo la trasformazione Hough")
        lines = cv2.HoughLinesP(binary, rho=2, theta=np.pi/180,threshold= 60, minLineLength=20, maxLineGap=5,lines =np.array([]))
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
                elif(slope<2):
                    right.append((slope, y_int))

            #print("[INFO] calcolo average")
            #print("[INFO] media destra")
            right_avg = np.average(right, axis=0)
            #print("[INFO] media sinistra")
            left_avg = np.average(left, axis = 0)
            #print("[INFO] left_line, makepoints")
            left_line = self.make_points(binary, left_avg)
            #print("[INFO] right_line, makepoints")
            right_line = self.make_points(binary, right_avg)
            coordinates = [left_line, right_line]

            z = np.zeros_like(binary)
            lines_image = np.dstack((z,z,z))
            #print("[INFO] rappresetazione linee medie")
            for x1, y1, x2, y2 in coordinates:
                print("coeff : ", x1 , " ", y1, " |  ", x2, "- ", y2)
                cv2.line(lines_image, (x1, y1), (x2, y2), (255, 255, 0), 10)
                print("avvenuto riconoscimento")
            combo =  cv2.addWeighted(image, 1, lines_image, 0.3, 0)
            print("return image Weighted")
            return combo
        except:
            return image
    
    def Hough(self, binary):
        lines = cv2.HoughLinesP(
            binary,
            rho=1,
            theta=np.pi/180,
            threshold= 2,
            minLineLength=3,
            maxLineGap=1,
            lines =np.array([])
        )
        
        return lines


    def getHistogram(self, binary, region, minPer=0.1, display = False):

        '''funzione che permette la creazione di un diagramma a colonne
        a partire da un'immagine in bianco e nero. per ogni colonna
        dell'immagine ne viene calcolata la quantità di pixel bianchi'''

        histValues = np.sum(binary[-binary.shape[0]//region:,:], axis=0)
        maxValue = np.max(histValues)
        minValue = minPer*maxValue
        
        indexArray = np.where(histValues >= minValue)
        basePoint = int(np.average(indexArray))

        if display:
            imgHist = np.zeros((binary.shape[0],binary.shape[1],3),np.uint8)
            for x,intensity in enumerate(histValues):
                cv2.line(imgHist,(x,binary.shape[0]),(x,binary.shape[0]-intensity//255//region),(255,0,255),1)
                cv2.circle(imgHist,(basePoint,binary.shape[0]),20,(0,255,255),cv2.FILLED)
                cv2.imshow("Display Histogram", imgHist)

        return basePoint
        
    def LaneCurvatureP(self, image, binary):
        return
        


    def HoughCenter(self, binary, x:int):
        '''funzione che restituisce la coordinata y (width)
        del centro della strada ad una data altezza x
        (più è in basso nell'immagine,maggiore il valore di x.
        Questo metodo effettua solo i calcoli e non disegna le 
        linee sull'immagine'''
        lines = cv2.HoughLinesP(binary, rho=2, theta=np.pi/180, threshold=60, minLineLength=20, maxLineGap=5, lines=np.array([]))
        left = []
        right=[]

        try:
            for line in lines:
                x1, y1, x2, y2 = line.reshape(4)
                parameters = np.polyfit((x1, x2), (y1, y2), 1)
                slope = parameters[0]
                y_int = parameters[1]
                if (slope < 0 and slope > -2):
                    left.append((slope, y_int))
                elif(slope<2):
                    right.append((slope, y_int))

            #print("[INFO] calcolo average")
            #print("[INFO] media destra")
            right_avg = np.average(right, axis=0)
            #print("[INFO] media sinistra")
            left_avg = np.average(left, axis = 0)
            #print("[INFO] left_line, makepoints")
            slopeLeft, yLeft = left_avg
            slopeRight, yRight = right_avg
            yL = slopeLeft*x + yLeft
            yR = slopeRight*x + yRight
            return (yL - yR)
        except:
            return None

        
    def Visual(self, image, ImgBinary, left_fit, right_fit, color = (0, 255, 0),debug = False):
        z = np.zeros_like(ImgBinary)
        filtered = np.dstack((z,z,z))
        
        try:
            kl, kr = left_fit, right_fit
            h = filtered.shape[0]
            ys = np.linspace(0, h -1, h)
            lxs = kl[0] * (ys**2) + kl[1] * ys + kl[2]
            rxs = kr[0] * (ys**2) + kr[1] * ys + kr[2]
            #creiamo un array verticale che contine i punti x e y della curva
            pts_left = np.array([np.transpose(np.vstack([lxs,ys]))])
            #qua uso transpose perche si inverte l'ordine dei punti e si può fare una bella area
            pts_right = np.array([np.flipud(np.transpose(np.vstack([rxs,ys])))])
            #creiamo un array orizzontale dei 2 punti delle curve
            pts = np.hstack((pts_left, pts_right))
            #riempiamo lo spazio tra i punti
            cv2.fillPoly(filtered, np.int_(pts), color)
            cv2.line(filtered, (0,int(filtered.shape[0]*(3/4))), (filtered.shape[1], int(filtered.shape[0]*(3/4))), (152, 2, 137), 6)
            if debug == True:
                plt.imshow(filtered)
                plt.show()
            shape = (filtered.shape[1], filtered.shape[0])
            #faccio l'inversa della maschera per rimetterla sull'immagine originale
            ground_lane = cv2.warpPerspective(filtered, self.inv_sky_matrix, shape)
            combo = cv2.addWeighted(image,1,ground_lane, 0.3, 0)
            return combo
        except:
            return image
