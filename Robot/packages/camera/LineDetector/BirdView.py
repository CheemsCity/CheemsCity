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
        
    def undistort(self, raw_image):
     
        image = cv2.undistort(raw_image, self.cam_matrix, self.dist_coeff, None, self.cam_matrix)
        return image 

    def sky_view(self, ground_image):

        temp_image = self.undistort(ground_image)
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


    def Hough(self, image, binary):
        print("[INFO] sta avvenendo la trasformazione Hough")
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
                if slope < 0:
                    left.append((slope, y_int))
                else:
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


        
    def Visual(self, image, ImgBinary, left_fit, right_fit, color = (0, 255, 0), debug = False):
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
