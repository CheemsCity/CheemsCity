import cv2 
import numpy as np

#andiamo ad analizzare un'array binario contenente 1 dove dovrebbero esserci ipixel delle linee (utilizzo np.logical_and)
#devo utilizzare lo sliding window algorithm

class curves:
    
    def __init__(self, ImgBinary, NumberOfWindows, Margin, nPixelActivation):
        self.img = imgBinary
        self.h, self.w = img.shape[0], img.shape[1]
        self.mid = self.h / 2
        self.n = NumberOfWindows #numero di  sliding windows
        self.window_height = np.int(self.h / self.n) #altezza delle sliding box
        self.m = Margin #margine dalla x centrale in avanti e indietro del box ; 100
        self.nActivation = nPixelActivation #numero di pixel di attivazione per ativare lo spostamento di midx : 50
        self.left_indices = [],[]
        self.right_indices = [],[]
        self.left_curve = none
        self.right_curve = none
                
    def start(self, img):
        #creiamo istogramma di tutte le colonne della metà inferiore dell'immagine binaria e i dovremmo ottenere 2 vette coe possibili starting point della ricerca dei punti della curve
        ### Each portion of the histogram below displays how many white pixels are in each column of the image. ###
        ###We then take the highest peaks of each side of the image, one for each lane line.###
        hist = np.sum(img[np.int(self.h /2):, :], axis = 0)
        mid = np.int(hist.shape[0]/2)
        start_leftx = np.argmax(hist[:mid])
        start_rightx = np.argmax(hist[mid:]) + mid
        return start_leftx, start_rightx
    
    def findY(self, box):
        #funzione che in base al numero del box restituisce il valore della y max e y min dei suoi vertici
        yLow = self.h - (box+1)* self.window_height
        yHigh = self.h - box* self.window_height
        return yLow, yHigh
    
    def findX(self, current):
        xLeft = current - self.m
        xRight = current + self.m
        return xLeft, xRight
    
    def indices_in_box(self, yLow, yHigh, xLeft, xRight):
        index = [],[]
        count = 0
        for j in range(yLow, yHigh+1):
            for i in range(xLeft, xRight +1):
                if(img[j][i]!=0):
                    index[count][0] = j+ yLow
                    index[count][1] = i + xLeft
                    count +1
        
        return index
    
    def newStart(self,img, current, pointIndices):
        if len(pointIndices) > self.nActivation:
            current = np.int(np.mean(self.all_pixels_x[pointIndices]))
        
        return current
    
    def Detect(self,img):
        start_leftx, start_rightx = self.start(image)
        left_points_index, right_points_index = [], []
        x = [none, none, none, none]
        y = [none,none]
        
        for box in range(self.n):
            #cerchiamo le coordinate del box
            y[0], y[1] = self.findY(box)
            x[0], x[1] = self.findX(start_leftx)
            x[2], x[3] = self.findX(start_rightx)
            
            #scrivere funzione che disegni il rettangolo in foto per debug
            
            left_box_indices = self.indices_in_box(img,y[0],y[1], x[0], x[1])
            right_box_indices = self.indices_in_box(img,y[0],y[1], x[0], x[1])
            
            self.left_indices.append(left_box_indices)
            self.right_indices.append(right_box_indices)
            
            start_leftx = self.newStart(img,start_leftx, left_box_indices)
            start_rightx = self.newStart(img,start_rightx, right_box_indices)
            
        left_xpoints = self.left_indices[:,1]
        left_ypoints = self.left_indices[:,0]
        
        right_xpoints = self.right_indices[:,1]
        right_ypoints = self.right_indices[:,0]
        
        self.left_curve = np.polyfit(left_xpoints, left_ypoints,2)
        self.right_curve = np.polyfit(right_xpoints, right_ypoints,2)
        
        
        
        
            
            
            
        
        
    
        
    