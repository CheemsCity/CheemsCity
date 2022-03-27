from camera.LineDetector.Curves import curves
from camera.LineDetector.LaneFilter import LaneFilter 
from camera.LineDetector.BirdView import BirdView
import numpy as np
import yaml
import cv2
import os
from pkg_resources import resource_string
import matplotlib.pyplot as plt

class LineDetectorPipeline:
    def __init__(self):
        self.lanefilter = LaneFilter()
        #self.height = 479
        #self.source_points = [(0, self.height), (600, self.height), (360,240), (230, 240)]
        #self.dest_points = [(130, self.height), (500, self.height), (500, 0), (130, 0)]

        #with open(r'/home/pi/CheemsCity/Robot/packages/camera/FinalCalibration.yml') as file:
        file = resource_string('camera', 'Calibration160.yml')
        calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
        self.matrix = calibration_data['camera_matrix']
        self.dist_coef = calibration_data['distortion_coefficient']

        #with open(r'/home/pi/CheemsCity/Robot/packages/camera/LineDetector/line_detector_settings.yaml') as file:
        file = resource_string('camera.LineDetector','line_detector_settings.yaml')
        self.settings = yaml.full_load(file)

        file = resource_string('camera.LineDetector','birdview_settings.yaml')
        data = yaml.full_load(file)
        self.source_points = data['source']
        self.dest_points = data['dest']

        self.birdview = BirdView(self.source_points, self.dest_points, self.matrix, self.dist_coef)
        self.curves = curves(9, 20, 50)
        sens = 100 #sensitività del colore
        self.lower_white = np.array([0,0, 255-sens]) #convenzione HSV
        self.upper_white = np.array([255, sens,255])
        self.curveList = []

    def lineDetector(self, image):
        lane_image = np.copy(image)
        filtered = self.lanefilter.toCanny(lane_image)
        filtered = self.lanefilter.ROI(filtered)
        skyview = self.birdview.sky_view(filtered)
        result = self.curves.Detect(skyview,0) #molto lento, va ottimizzato
        if result != -1:
            combo = self.birdview.Visual(image, skyview, result['pixel_left_best_fit_curve'], result['pixel_right_best_fit_curve'])
            self.comboBig = cv2.resize(combo, self.settings['line_detector_resizeImage'])
        else:
            self.comboBig = cv2.resize(lane_image, self.settings['line_detector_resizeImage'])

        return self.comboBig
    def lineDetector2(self, image, display = False):
        
        numberCurve = 10# numero massimo di dati curvatura storati

        lane_image = np.copy(image)
        frameHSV = cv2.cvtColor(lane_image, cv2.COLOR_BGR2HSV)
        frameHSV = cv2.inRange(frameHSV,self.lower_white, self.upper_white)
        #cv2.imshow("Color", frameHSV)
        filtered = self.lanefilter.roiToHeight(frameHSV,150)
        #cv2.imshow("postROI", filtered)
        
        middlePoint = self.birdview.getHistogram(filtered,6, minPer=0.5)
        curveAveragePoint = self.birdview.getHistogram(filtered,1, minPer=0.9)
        curveRaw = curveAveragePoint - middlePoint

        if display:
            cv2.putText(image, str(curveRaw), (image.shape[1]//2-80,85), cv2.FONT_HERSHEY_COMPLEX,2,(255,0,255),3)
            cv2.line(image, (middlePoint, image.shape[0]), (curveAveragePoint, image.shape[0]//2), (255,0,255),5)
        
        self.curveList.append(curveRaw)
        if len(self.curveList)>numberCurve:
            self.curveList.pop(0)
        curve = int(sum(self.curveList)/len(self.curveList))

        return middlePoint, curve

    def viewAll(self, image):
        lane_image = np.copy(image)
        filtered = self.lanefilter.toCanny(lane_image)
        filtered = self.lanefilter.ROI(filtered)
        roi = np.copy(filtered)
        skyview = self.birdview.sky_view(filtered)
        result = self.curves.Detect(skyview,0) #molto lento, va ottimizzato
        if result != -1:
            combo = self.birdview.Visual(image, skyview, result['pixel_left_best_fit_curve'], result['pixel_right_best_fit_curve'])
            self.comboBig = cv2.resize(combo, self.settings['line_detector_resizeImage'])
        else:
            self.comboBig = cv2.resize(lane_image, self.settings['line_detector_resizeImage'])

        res = {
            'roi' : roi,
            'combo' : self.comboBig,
            'skyview': skyview
        }
        return res
    
if __name__ == '__main__':
    detector = LineDetectorPipeline()

    from camera.CameraStream import CameraStream
    import time
    import timeit
    
    vs = CameraStream().start()
    time.sleep(1.0)
    white_flag = True
    while white_flag:
        image = vs.read()
        start = time.time()
        #res = detector.viewAll( image)
        center, curve = detector.lineDetector2(image,display= True)
        print("centro della strada: ", center)
        print("curvature: ", curve)
        end = time.time()
        print("the time is: ",end-start )
        #cv2.imshow("frame", res['combo'])
        cv2.imshow("frame", image)
        #cv2.imshow("roi", res['roi'])
        #cv2.imshow("skyview", res['skyview'])
        #plt.imshow(res['roi'])
        #plt.imshow(res['skyview'])
        #plt.show()
        key = cv2.waitKey(1) & 0xFF
        if key == 27:         #ESC
            white_flag = False

    cv2.destroyAllWindows()
