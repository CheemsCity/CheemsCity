import cv2 
import numpy as np

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
        
    def Visual(self, image, ImgBinary, left_fit, right_fit, color = (0, 255, 0), debug = False):
        z = np.zeros_like(ImgBinary)
        filtered = np.dstack((z,z,z))

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
        if debug == True:
            plt.imshow(filtered)
            plt.show()
        shape = (filtered.shape[1], filtered.shape[0])
        #faccio l'inversa della maschera per rimetterla sull'immagine originale
        ground_lane = cv2.warpPerspective(filtered, self.inv_sky_matrix, shape)
        combo = cv2.addWeighted(image,1,ground_lane, 0.3, 0)
        return combo