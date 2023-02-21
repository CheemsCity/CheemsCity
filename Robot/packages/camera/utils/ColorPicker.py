import cv2
import numpy as np
from camera.CameraStream import CameraStream
import time


def empty(a):
    pass


cv2.namedWindow("HSV")
cv2.resizeWindow("HSV", 320, 240)
cv2.createTrackbar("HUE min", "HSV", 0, 179, empty)
cv2.createTrackbar("HUE max", "HSV", 179, 179, empty)
cv2.createTrackbar("SAT min", "HSV", 0, 255, empty)
cv2.createTrackbar("SAT max", "HSV", 255, 255, empty)
cv2.createTrackbar("VALUE min", "HSV", 0, 255, empty)
cv2.createTrackbar("VALUE max", "HSV", 255, 255, empty)

vs = CameraStream().start()
time.sleep(1.0)
white_flag = True

while white_flag:
    image = vs.read()
    imgHsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("HUE min", "HSV")
    h_max = cv2.getTrackbarPos("HUE max", "HSV")
    s_min = cv2.getTrackbarPos("SAT min", "HSV")
    s_max = cv2.getTrackbarPos("SAT max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE max", "HSV")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHsv, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    hStack = np.hstack([image, mask, result])
    cv2.imshow("Horizontal Stacking", hStack)
    if cv2.waitKey(1) and 0xFF == ord('q'):
        white_flag = False
        cv2.waitKey(0)

cv2.destroyAllWindows()
