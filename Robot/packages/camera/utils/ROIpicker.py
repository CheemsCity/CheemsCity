import cv2
import numpy as np
from camera.CameraStream import CameraStream
from camera.LineDetector.LaneFilter import LaneFilter
import time


def empty(a):
    pass


cv2.namedWindow("ROI")
cv2.resizeWindow("ROI", 320, 240)
cv2.createTrackbar("ROI max", "ROI", 0, 480, empty)

vs = CameraStream().start()
time.sleep(1.0)
white_flag = True
lanefilter = LaneFilter()

while white_flag:
    image = vs.read()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h = cv2.getTrackbarPos("ROI max", "ROI")
    roi = lanefilter.roi_to_height(gray, h)
    cv2.imshow("ROI result", roi)
    if cv2.waitKey(1) and 0xFF == ord('q'):
        white_flag = False
        cv2.waitKey(0)

cv2.destroyAllWindows()
