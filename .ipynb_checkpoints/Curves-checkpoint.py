import cv2 
import numpy as np
import matplotlib.pyplot as plt
#andiamo ad analizzare un'array binario contenente 1 dove dovrebbero esserci ipixel delle linee (utilizzo np.logical_and)
#devo utilizzare lo sliding window algorithm

class curves:
    
    def __init__(self, ImgBinary, NumberOfWindows, Margin, nPixelActivation):
        self.img = ImgBinary
        self.h, self.w = self.img.shape[0], self.img.shape[1]
        self.mid = self.h / 2
        self.n = NumberOfWindows #numero di  sliding windows
        self.window_height = np.int(self.h / self.n) #altezza delle sliding box
        self.m = Margin #margine dalla x centrale in avanti e indietro del box ; 100
        self.nActivation = nPixelActivation #numero di pixel di attivazione per ativare lo spostamento di midx : 50
        self.left_indices = []
        self.right_indices = []
        self.left_curve = None
        self.right_curve = None
        self.left_xpoints = None
        self.left_ypoints = None
        self.right_xpoints = None
        self.right_xpoints = None
        self.left_fit_curve_pix = None
        self.right_fit_curve_pix = None
        self.out_img = None
        
                
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
    
    def indices_in_box(self,img, yLow, yHigh, xLeft, xRight):
        self.all_pixels_x = np.array(img.nonzero()[1])
        self.all_pixels_y = np.array(img.nonzero()[0])
        cond1 = (self.all_pixels_y >= yLow)
        cond2 = (self.all_pixels_y < yHigh)
        cond3 = (self.all_pixels_x >= xLeft)
        cond4 = (self.all_pixels_x < xRight)
        return (cond1 & cond2 & cond3 & cond4 ).nonzero()[0]
    
    def newStart(self,img, current, pointIndices):
        if len(pointIndices) > self.nActivation:
            current = np.int(np.mean(self.all_pixels_x[pointIndices]))
        
        return current
    
    def plot(self, t = 4):
        
        #creo un tensore della dimensione dell'immagine con 3 canali binari uno per colore
        self.out_img[self.left_ypoints, self.left_xpoints] = [255, 0, 255]
        self.out_img[self.right_ypoints, self.right_xpoints] = [0, 255, 255]

        self.left_fit_curve_pix = np.polyfit(self.left_ypoints, self.left_xpoints, 2)
        self.right_fit_curve_pix = np.polyfit(self.right_ypoints, self.right_xpoints, 2)
        
        #kl e kr contengono i coefficienti dell'equazione di secondo grado
        kl, kr = self.left_fit_curve_pix, self.right_fit_curve_pix
        #linspace genera un insieme di self.h punti equalmente distanti da 0 a self.h, 
        ys = np.linspace(0, self.h - 1, self.h)
        self.ys = ys
        
        #ricaviamo i punti delle x a partire dall'equazione e dalle y
        left_xs = kl[0] * (ys**2) + kl[1] * ys + kl[2]
        self.left_xs = left_xs
        right_xs = kr[0] * (ys**2) + kr[1] * ys + kr[2]

        xls, xrs, ys = left_xs.astype(np.uint32), right_xs.astype(np.uint32), ys.astype(np.uint32)

        for xl, xr, y in zip(xls, xrs, ys):
            cv2.line(self.out_img, (xl - t, y), (xl + t, y), (255, 255, 0), int(t / 2))
            cv2.line(self.out_img, (xr - t, y), (xr + t, y), (0, 0, 255), int(t / 2))
        
    def pixel_location(self, indices, img):
        all_pixels_x = np.array(img.nonzero()[1])
        all_pixels_y = np.array(img.nonzero()[0])
        return all_pixels_x[indices], all_pixels_y[indices]
    
    def draw_boundaries(self, p1, p2, color, thickness = 5):
        cv2.rectangle(self.out_img, p1, p2, color, thickness)
    
    def Detect(self,img):
        start_leftx, start_rightx = self.start(img)
        left_indices, right_indices = [], []
        x = [None, None, None, None]
        y = [None,None]
        self.out_img = np.dstack((img, img, img))*255
        
        for box in range(self.n):
            #cerchiamo le coordinate del box
            y[0], y[1] = self.findY(box)
            x[0], x[1] = self.findX(start_leftx)
            x[2], x[3] = self.findX(start_rightx)
            
            self.draw_boundaries((x[0],y[0]),(x[1],y[1]), (255, 0 ,0))
            self.draw_boundaries((x[2],y[0]),(x[3],y[1]), (0, 255 ,0))
            #scrivere funzione che disegni il rettangolo in foto per debug
            
            left_box_indices = self.indices_in_box(img,y[0],y[1], x[0], x[1])
            right_box_indices = self.indices_in_box(img,y[0],y[1], x[2], x[3])
            
            left_indices.append(left_box_indices)
            right_indices.append(right_box_indices)
            
            start_leftx = self.newStart(img,start_leftx, left_box_indices)
            start_rightx = self.newStart(img,start_rightx, right_box_indices)
            
        
        self.left_indices = np.concatenate(left_indices)
        self.right_indices = np.concatenate(right_indices)
        
        self.left_xpoints, self.left_ypoints = self.pixel_location(self.left_indices, img)
        
        self.right_xpoints, self.right_ypoints = self.pixel_location(self.right_indices, img)
        
        self.left_curve = np.polyfit(self.left_xpoints, self.left_ypoints,2)
        self.right_curve = np.polyfit(self.right_xpoints, self.right_ypoints,2)
        
        self.plot()
        self.result = {
          'image': self.out_img,
          'real_left_best_fit_curve': self.left_curve,
          'real_right_best_fit_curve': self.right_curve, 
          'pixel_left_best_fit_curve': self.left_fit_curve_pix,
          'pixel_right_best_fit_curve': self.right_fit_curve_pix, 
          'curve_pointsx': self.left_xs,
          'curve_pointsy': self.ys
        }

        return self.result
    
        
        
        
            
            
            
        
        
    
        
    