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
        
    