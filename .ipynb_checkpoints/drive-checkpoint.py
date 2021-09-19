import cv2
import numpy as np
import yaml
import matplotlib.pyplot as plt

from Curves import curves
from LaneFilter import LaneFilter 
from BirdView import BirdView

class AutoDrive():
    
    def __init__(self):
        stream = file('calibration_data.yml', 'r')
        yaml.load(stream)
        self.matrix = calibration_data['camera_matrix']
        self.dist_coef = calibration_data['distortion_coefficient']

        source_points = [(200, 700), (1100, 700), (790,400), (400, 400)]
        dest_points = [(320, 704), (960, 704), (960, 0), (320, 0)]
        
        #andiamo ad inizializzare i costruttori delle varie classi
        self.lanefilter = LaneFilter()
        self.birdview = BirdView(source_points, dest_points, self.matrix, self.dist_coef)
        self.curves = curves(9, 100, 50)
        
    
    def drive(image):
        
        