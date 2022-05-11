import cv2
import numpy as np
import yaml
from pkg_resources import resource_string

class LaneFilter:
    
    def __init__(self):
        self.problem = 0

        file = resource_string('camera', 'cameraConfig.yaml')
        self.settings = yaml.full_load(file)
        self.height = self.settings['res_h']
        self.width = self.settings['res_w']
        
    def toCanny(self,img):
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        except:
            gray = img
        blur = cv2.GaussianBlur(gray, (5,5),0)
        canny = cv2.Canny(blur, 70, 170)
        return canny
    
    def ROI(self,img):
        #roy da modificare quando avremo la struttura della macchina e quindi posizione fissa della telecamera
        trapezio = np.array([
            [(0, self.height), (self.width, self.height), (self.width, 200), (0,200)]
        ])
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, trapezio, 255) #crea maschera
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    def roiToHeight(self,img, height:int):
        '''Metodo che restituisce un'immagine con ROI personalizzato
        di tipo rettangolo la cui base maggiore è il lato inferiore
        della foto e come parametro personalizzabile l'altezza'''
        if(height > self.height):
            raise ValueError("[ERROR] Altezza inserita supera l'altezza della foto: {}".format(self.height))
        trapezio = np.array([
            [(0, self.height), (self.width, self.height), (self.width, (self.height -height)), (0, (self.height-height))]
            ])
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, trapezio, 255)
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image

    def customRoi(self, img, height:int, wRight:int, wLeft:int):
        '''Metodo che restituisce un'immagine con un ROI personalizzato
        avente come base maggiore il lato inferiore della foto e parametri
        regolabili quali l'altezza del trapezio e la posizione lungo
        y[width] dei due punti superiori'''
        if(height > self.height):
            raise ValueError("[ERROR] Altezza ROI superiore ad altezza massima foto: {} > {}".format(height, self.height))
        if(wLeft < 0):
            raise ValueError("[ERROR] wLeft ROI inferiore a 0: {} < 0".format(wleft))
        if(wRight > self.width):
            raise ValueError("[ERROR] wRight ROI superiore a larghezza massima foto: {} > {}".format(wRight, self.width))
        trapezio = np.array([
            [(0, self.height), (self.width, self.height), (wRight, (self.height -height)), (wLeft, (self.height-height))]
            ])
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, trapezio, 255)
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image









