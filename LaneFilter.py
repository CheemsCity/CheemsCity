import cv2
immport numpy as np

class LaneFilter:
    
    def __init__(self)
    
    def toCanny(img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5,5),0)
        canny = cv2.Canny(blur, 70, 150)
        return canny
    
    def ROI(img):
        height = image.shape[0]
        triangle = np.array([
            [(200, height), (1100, height), (550, 250)]
        ])
        mask = np.zeros_like(image)
        cv2.fillPoly(mask, triangle, 255) #crea maschera
        masked_image = cv2.bitwise_and(image, mask)
        return masked_image