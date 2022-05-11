import cv2
import numpy as np
import math

class ColorFinder():
    def __init__(self, image = None, color = None, radius = None):
        self.or_image = image #copia dell'immagine originale per bu
        self.image = self.or_image #immagine su cui lavoro
        self.color = color #colore da cercare
        self.raggio = radius #"raggio" di'incertezza, per info vedasi documentazione
        if self.image is not None:
            self.width = self.image.shape[0] #larghezza immagine
            self.height = self.image.shape[1] #altezza immagine
        self.risk_coeff = 0.1 #coefficiente di rischio per tenere la distanza dall'oggetto trovato

    def changeValues(self, colorNew = None, radiusNew = None, riskCoeffNew = 0.1):
        if colorNew is not None:
            self.color = colorNew
        if radiusNew is not None:
            self.raggio = radiusNew
        self.risk_coeff = riskCoeffNew
    
    def newImage(self, imageNew):
        self.image = imageNew
        self.or_image = self.image
        self.width = self.image.shape[0] #larghezza immagine
        self.height = self.image.shape[1] #altezza immagine

    def distInRange(self, display = False):
        #creo i due vettori di minimo e massimo per il range in cui cercare i colori
        #vengono creati sottraendo o aggiungendo al colore cercato il raggio d'errore
        self.lower = np.array([])
        for i in range(3):
            if self.color[i]-self.raggio < 0:
                self.lower = np.append(self.lower,0)
            else:
                self.lower = np.append(self.lower, self.color[i]-self.raggio)
        self.upper = np.array([])
        for i in range(3):
            if self.color[i]+self.raggio > 255:
                self.upper = np.append(self.upper, 255)
            else:
                self.upper = np.append(self.upper, self.color[i]+self.raggio)

        self.bool_Md = cv2.inRange(self.image, self.lower, self.upper)

        #print([self.lower, self.upper])
        if display:
            cv2.imshow("c", self.bool_Md)
        return self.bool_Md

    ##########################################################################################################################

    def mat_diff(self):
        Mcolor = np.ones((self.width,self.height,3))
        #tensore di soli 1 grande quanto l'immagine
        for i in range(3):
            Mcolor[:,:,i] = self.color[i]*Mcolor[:,:,i]
            #creo un tensore tale che per ogni matrice abbia solo il numero relativo al RGB del colore fissato
        self.Mdiff = self.image - Mcolor
        #calcolo la differenza tra le due matrici

    def mat_dist(self):
        self.Mdiff = self.Mdiff**2
        #elevo i tutti gli elementi del tensore differenza al quadrato
        self.Md = np.sqrt(self.Mdiff[:,:,0] + self.Mdiff[:,:,1] + self.Mdiff[:,:,2])
        #sommo gli elementi al quadrato e ne prendo la radice, così ottengo la distanza euclidea tra i vettori di dimensione 3
        #della profondità dell'immagine con il vettore colore
        return self.Md

    #l'idea usata nel codice di cui sopra è essenzialmente questa:
    #voglio prendere il vettore image[i,j] fatto da RGB del pixel (i,j)
    #e calcolarne la distanza euclidea dal vettore color fatto dal suo RGB
    #sqrt((R_m-R_c)^2 + (G_m-G_c)^2 + (B_m-G_c)^2)
    #quindi ottenere una matrice ove ogni (i,j) è la distanza tra il colore del pixel e quello color
    #iterare per ogni (i,j) rende particolarmente lento il processo, dovrebbe esserre O(n^3)
    #il processo che faccio è allora di creare una matrice grande quanto a quella dell'immagine
    #e mettere in [:,:,0] solo R del color, [:,:,1] solo G del color e [:,:,2] solo B del color
    #a questo punto fare image - la matrice sopra così da avere 3 matrici con per esempio la prima fatta da
    #R_mij-R per ogni i,j
    #a questo punto elevo al quadrato ogni elemento, li sommo tutti 3 a 3 e ottengo le distanze al quadrato
    #prendo la radice quadrata e ho le distanze

    def bool_mat(self):
        self.bool_Md = np.zeros((self.width, self.height), dtype=np.uint8)
        for i in range(self.width):
            for j in range(self.height):
                if(self.Md[i,j] > self.raggio):
                    self.bool_Md[i,j] = 0
                else:
                    self.bool_Md[i,j] = 255
        return self.bool_Md

    def CannyContour(self): #IN DISUSO
        self.contour_Md = cv2.Canny(self.bool_Md, 70, 150)
        #trovo i contorni tramite l'algoritmo Canny sfruttando il fatto che ove era nel raggio
        #ora c'è il nero e nel resto c'è il bianco
        return self.contour_Md

    def ColorContour(self, draw): #IN DISUSO
        self.contours, self.hierarchy = cv2.findContours(self.contour_Md,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #trovo i contorni dell'immagine tramite l'algoritmo di OpenCv
        if draw==1:
            cv2.drawContours(self.image, self.contours, -1, (0, 255, 0), 3)
        #li disegno nell'immagine
        return self.image

    def findBiggest(self): #IN DISUSO
        length_list = list(len(self.contours[i]) for i in range(len(self.contours)))
        #creo una lista con tutte le lunghezze dei vari contorni
        max_item = max(length_list)
        #prendo il contorno maggiore 
        self.biggest_list = list(filter(lambda i: len(self.contours[i]) >= max_item, range(len(self.contours))))
        #prendo gli indici degli elementi che hanno quel valore
        return self.biggest_list

    def findBiggerThan(self,limit): #IN DISUSO
        self.result_bigger_list = list(filter(lambda i: len(self.contours[i]) > limit, range(len(self.contours))))
        #prendo gli indici degli elementi che hanno lunghezza maggiore di un limite
        return self.result_bigger_list

    def defineRectangularContour(self):
        self.SO = (math.ceil(min(np.nonzero(self.bool_Md)[1])*(1-self.risk_coeff)),math.ceil(max(np.nonzero(self.bool_Md)[0])*(1+self.risk_coeff)))
        self.NE = (math.ceil(max(np.nonzero(self.bool_Md)[1])*(1+self.risk_coeff)),math.ceil(min(np.nonzero(self.bool_Md)[0])*(1-self.risk_coeff)))
        #prendo i 2 punti che costruiscono il rettangolo più grande che contiene l'oggetto
        #inflaziono il rettangolo aumentando i massimi del coefficiente di rischio
        #e diminuendo i minimi dello sesso coefficiente

        #ridimensiono i punti all'interno dell'immagine
        if self.SO[0] < 0:
            self.SO[0] = 0
        if self.SO[1] > self.height:
            self.SO[1] = self.height
        if self.NE[0] > self.width:
            self.NE[0] = self.width
        if self.NE[1] < 0:
            self.NE[1] = 0
        
        return[self.SO, self.NE]

    def defineRectangularContourCustom(self, customImage):
        try:
            self.SO = (math.ceil(min(np.nonzero(customImage)[1])*(1-self.risk_coeff)),math.ceil(max(np.nonzero(customImage)[0])*(1+self.risk_coeff)))
            self.NE = (math.ceil(max(np.nonzero(customImage)[1])*(1+self.risk_coeff)),math.ceil(min(np.nonzero(customImage)[0])*(1-self.risk_coeff)))
        except:
            return [None, None]
        #prendo i 2 punti che costruiscono il rettangolo più grande che contiene l'oggetto
        #inflaziono il rettangolo aumentando i massimi del coefficiente di rischio
        #e diminuendo i minimi dello sesso coefficiente

        #ridimensiono i punti all'interno dell'immagine
        if self.SO[0] < 0:
            self.SO[0] = 0
        if self.SO[1] > self.height:
            self.SO[1] = self.height
        if self.NE[0] > self.width:
            self.NE[0] = self.width
        if self.NE[1] < 0:
            self.NE[1] = 0
        
        return[self.SO, self.NE]

    def rectangleOnOriginalImage(self):
        return cv2.rectangle(self.or_image, self.SO, self.NE, (255,0,0), 2)
        #restituisco il rettangolo calcolato in sovraimpressione all'immagine originale