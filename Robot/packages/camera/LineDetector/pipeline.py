from camera.LineDetector.Curves import curves
from camera.LineDetector.LaneFilter import LaneFilter
from camera.LineDetector.BirdView import BirdView
from camera.ColorFinder.finder import ColorFinder
import numpy as np
import math
import yaml
import cv2
import os
from pkg_resources import resource_string
import matplotlib.pyplot as plt
import time


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
        file = resource_string('camera.LineDetector',
                               'line_detector_settings.yaml')
        self.settings = yaml.full_load(file)

        file = resource_string('camera.LineDetector', 'birdview_settings.yaml')
        data = yaml.full_load(file)
        self.source_points = data['source']
        self.dest_points = data['dest']

        self.birdview = BirdView(self.source_points, self.dest_points,
                                 self.matrix, self.dist_coef)
        self.curves = curves(9, 20, 50)
        sens = 100  #sensitività del colore
        self.lower_white = np.array([0, 0, 255 - sens])  #convenzione HSV
        self.upper_white = np.array([255, sens, 255])
        self.curveList = []

        self.cf = ColorFinder()
        self.colorCheems = [255, 193, 0]
        self.upperCheems = np.array([179, 255, 255])
        self.lowerCheems = np.array([0, 95, 180])
        self.radius = 50

    def lineDetector(self, image, count=False, debug=False):
        if count:
            start = time.time_ns()

        #STEP 1: rettifichiamo l'immagine, così da non avere problemi col fisheye
        lane_image = np.copy(image[200:, :, :])
        canny_image = np.copy(image[200:, :, :])
        rect = self.birdview.undistortFaster(lane_image)

        #STEP 2: isolare il colore Bianco
        frameHSV = cv2.cvtColor(rect, cv2.COLOR_BGR2HSV)
        frameHSV = cv2.inRange(frameHSV, self.lower_white, self.upper_white)

        if count:
            t1 = time.time_ns()
            dt1 = t1 - start
            print("tempo immagine 1 = ", dt1 / 1000000000)
        if debug:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
            cv2.imshow("immagine 1", frameHSV)

        #STEP 3: chiudere eventuali buchi con un dilate:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        frameHSV = cv2.dilate(frameHSV, kernel)
        if debug:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
            cv2.imshow("immagine 2", frameHSV)

        #STEP 4: applichiamo il canny sull'immagine di partenza e uniamo con un AND
        # le due immagini risultato (canny + color detection)
        edges = cv2.Canny(canny_image, 80, 200, apertureSize=3)
        edge_color = cv2.bitwise_and(frameHSV, edges)

        if count:
            t2 = time.time_ns()
            dt2 = t2 - start
            print("tempo immagine 2 = ", dt2 / 1000000000)

        if debug:

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
            cv2.imshow("immagine 3", edge_color)

        #STEP 5: troviamo le linee con la HOUGH transform.
        lines = self.birdview.Hough(edge_color)

        if count:
            t3 = time.time_ns()
            dt3 = t3 - start
            print("tempo totale = ", dt2 / 1000000000)
            print("\n")

        return lines

    def lineDetector2(self, image, display=False):

        numberCurve = 10  # numero massimo di dati curvatura storati

        lane_image = np.copy(image)
        #Unimage = self.birdview.undistortFaster(lane_image)
        #cv2.imshow("Unimage", Unimage)
        frameHSV = cv2.cvtColor(lane_image, cv2.COLOR_BGR2HSV)
        frameHSV = cv2.inRange(frameHSV, self.lower_white, self.upper_white)
        #cv2.imshow("Color", frameHSV)
        filtered = self.lanefilter.roiToHeight(frameHSV, 150)
        #cv2.imshow("postROI", filtered)
        #skyview = self.birdview.sky_view(filtered)
        #cv2.imshow("postROI", skyview)
        middlePoint = self.birdview.getHistogram(filtered, 6, minPer=0.2)
        curveAveragePoint = self.birdview.getHistogram(filtered, 1, minPer=0.5)
        curveRaw = curveAveragePoint - middlePoint

        if display:
            cv2.circle(image, (middlePoint, image.shape[0]), 20, (0, 255, 255),
                       cv2.FILLED)
            cv2.putText(image, str(curveRaw), (image.shape[1] // 2 - 80, 85),
                        cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
            cv2.line(image, (middlePoint, image.shape[0]),
                     (curveAveragePoint, image.shape[0] // 3 * 2),
                     (255, 0, 255), 4)

        self.curveList.append(curveRaw)
        if len(self.curveList) > numberCurve:
            self.curveList.pop(0)
        curve = int(sum(self.curveList) / len(self.curveList))

        return middlePoint, curve

    def lineDetector3(self, image, display=False):
        #copio le immagini per evitare di modificare l'orginale
        lane_image1 = np.copy(image)
        lane_image2 = np.copy(image)

        ########################### riconoscimento Cheems##########################
        #lane_image1 = cv2.cvtColor(lane_image1, cv2.COLOR_BGR2RGB)

        #self.cf.newImage(lane_image1)
        #self.cf.changeValues(self.colorCheems, self.radius)

        #bool_Md = self.cf.distInRange()
        lane_image1 = cv2.cvtColor(lane_image1, cv2.COLOR_BGR2HSV)
        bool_Md = cv2.inRange(lane_image1, self.lowerCheems, self.upperCheems)
        kernel = np.ones((5, 5), np.uint8)
        mg_erode = cv2.erode(bool_Md, kernel, iterations=1)
        #cv2.imshow("erode", mg_erode)
        mg_dilation = cv2.dilate(mg_erode, kernel, iterations=1)
        #cv2.imshow("postED", mg_dilation)
        im2, contours, hierarchy = cv2.findContours(mg_dilation,
                                                    cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        areas = []
        for contour in contours:
            area = cv2.contourArea(contour)
            areas.append(area)
        '''una certa area attiverà la risposta freno del robot'''
        ######################### calcolo centro lineee ############################
        numberCurve = 10  # numero massimo di dati curvatura storati

        frameHSV = cv2.cvtColor(lane_image2, cv2.COLOR_BGR2HSV)
        frameHSV = cv2.inRange(frameHSV, self.lower_white, self.upper_white)
        filtered = self.lanefilter.roiToHeight(frameHSV, 150)
        #calcola la somma dei punti delle colonne dell'immagine e ne calcola
        #la media pesata.
        middlePoint = self.birdview.getHistogram(filtered, 6, minPer=0.2)
        curveAveragePoint = self.birdview.getHistogram(filtered, 1, minPer=0.5)
        curveRaw = curveAveragePoint - middlePoint

        if display:
            print("display = True")
            cv2.circle(image, (middlePoint, image.shape[0]), 20, (0, 255, 255),
                       cv2.FILLED)
            cv2.putText(image, str(curveRaw), (image.shape[1] // 2 - 80, 85),
                        cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
            cv2.line(image, (middlePoint, image.shape[0]),
                     (curveAveragePoint, image.shape[0] // 3 * 2),
                     (255, 0, 255), 4)
            #for sone in sones:
            #image = cv2.rectangle(image, sone[0], sone[1], (255, 0, 0), 2)
            cv2.drawContours(image, contours, -1, (0, 255, 0), 3)
            cv2.imshow("CheemsRec", image)

        self.curveList.append(curveRaw)
        if len(self.curveList) > numberCurve:
            self.curveList.pop(0)
        curve = int(sum(self.curveList) / len(self.curveList))

        print(areas)
        #return sones, middlePoint, curve
        if len(areas) == 0:
            areaMax = 0
        else:
            areaMax = np.max(areas)

        return areaMax, middlePoint, curve

    def viewAll(self, image):
        lane_image = np.copy(image)
        filtered = self.lanefilter.toCanny(lane_image)
        filtered = self.lanefilter.ROI(filtered)
        roi = np.copy(filtered)
        skyview = self.birdview.sky_view(filtered)
        result = self.curves.Detect(skyview, 0)  #molto lento, va ottimizzato
        if result != -1:
            combo = self.birdview.Visual(image, skyview,
                                         result['pixel_left_best_fit_curve'],
                                         result['pixel_right_best_fit_curve'])
            self.comboBig = cv2.resize(
                combo, self.settings['line_detector_resizeImage'])
        else:
            self.comboBig = cv2.resize(
                lane_image, self.settings['line_detector_resizeImage'])

        res = {'roi': roi, 'combo': self.comboBig, 'skyview': skyview}
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
        '''start = time.time()
        # center, curve = detector.lineDetector2(image,display= True)
        # print("centro della strada: ", center)
        # print("curvature: ", curve)
        # end = time.time()
        # print("the time is: ",end-start )
        sones, center, curve = detector.lineDetector3(image, display = True)
        print("centro della strada: ", center)
        print("curvature: ", curve)
        end = time.time()
        print("the time is: ", end-start)
        print( "area is : ", sones)'''
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  #ESC
            white_flag = False
        detector.lineDetector(image, count=True)

    cv2.destroyAllWindows()
