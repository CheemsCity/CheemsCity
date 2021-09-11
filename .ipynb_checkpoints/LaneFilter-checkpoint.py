import cv2
import numpy as np

class LaneFilter:
    
    def __init__(self):
        self.problem = 0
        
    def toCanny(self,img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5),0)
        canny = cv2.Canny(blur, 70, 150)
        return canny
    
    def ROI(self,img):
        height = img.shape[0]
        trapezio = np.array([
            [(200, height), (1100, height), (790,400), (400, 400)]
        ])
        mask = np.zeros_like(img)
        cv2.fillPoly(mask, trapezio, 255) #crea maschera
        masked_image = cv2.bitwise_and(img, mask)
        return masked_image