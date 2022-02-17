import cv2
import numpy as np
import math

class ColorFinder():
    def __init__(self, image, color, radius):
        self.or_image = image #copia dell'immagine originale per bu
        self.image = self.or_image #immagine su cui lavoro
        self.color = color #colore da cercare
        self.raggio = radius #"raggio" di'incertezza, per info vedasi documentazione
        self.width = self.image.shape[0] #larghezza immagine
        self.height = self.image.shape[1] #altezza immagine
        self.risk_coeff = 0.1 #coefficiente di rischio per tenere la distanza dall'oggetto trovato

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

    def CannyContour(self):
        self.contour_Md = cv2.Canny(self.bool_Md, 70, 150)
        #trovo i contorni tramite l'algoritmo Canny sfruttando il fatto che ove era nel raggio
        #ora c'è il nero e nel resto c'è il bianco
        return self.contour_Md

    def ColorContour(self, draw):
        self.contours, self.hierarchy = cv2.findContours(self.contour_Md,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #trovo i contorni dell'immagine tramite l'algoritmo di OpenCv
        if draw==1:
            cv2.drawContours(self.image, self.contours, -1, (0, 255, 0), 3)
        #li disegno nell'immagine
        return self.image

    def findBiggest(self):
        length_list = list(len(self.contours[i]) for i in range(len(self.contours)))
        #creo una lista con tutte le lunghezze dei vari contorni
        max_item = max(length_list)
        #prendo il contorno maggiore 
        self.biggest_list = list(filter(lambda i: len(self.contours[i]) >= max_item, range(len(self.contours))))
        #prendo gli indici degli elementi che hanno quel valore
        return self.biggest_list

    def findBiggerThan(self,limit):
        self.result_bigger_list = list(filter(lambda i: len(self.contours[i]) > limit, range(len(self.contours))))
        #prendo gli indici degli elementi che hanno lunghezza maggiore di un limite
        return self.result_bigger_list

    def defineRectangularContour(self,index):
        column = []
        row = []
        l = self.contours[index]
        #prendo la lista dei punti che costituiscono il contorno più grande in foto
        for i in range(len(l)):
            row.append(l[i][0][0])
            column.append(l[i][0][1])
        #creo la lista delle colonne e la lista delle righe
        self.SO = (math.ceil(max(row)*(1+self.risk_coeff)),math.ceil(min(column)*(1-self.risk_coeff)))
        self.SE = (math.ceil(max(row)*(1+self.risk_coeff)),math.ceil(max(column)*(1+self.risk_coeff)))
        self.NE = (math.ceil(min(row)*(1-self.risk_coeff)),math.ceil(max(column)*(1+self.risk_coeff)))
        self.NO = (math.ceil(min(row)*(1-self.risk_coeff)),math.ceil(min(column)*(1-self.risk_coeff)))
        #prendo i 4 punti che costruiscono il rettangolo più grande che contiene l'oggetto
        #inflaziono il rettangolo aumentando i massimi del coefficiente di rischio
        #e diminuendo i minimi dello sesso coefficiente

        return[self.SO, self.SE, self.NE, self.NO]

    def rectangleOnOriginalImage(self):
        return cv2.rectangle(self.or_image, self.SO, self.NE, (255,0,0), 2)
        #restituisco il rettangolo calcolato in sovraimpressione all'immagine originale