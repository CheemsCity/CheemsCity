from camera.ArucoMarkerDetector.ArucoDetector import ArucoDetector
from camera.CameraStream import CameraStream
import time
import cv2
import yaml
from threading import Thread
import matplotlib.pyplot as plt

with open(r'FinalCalibration.yml') as file:
    calibration_data = yaml.load(file, Loader=yaml.UnsafeLoader)
    cam_matrix = calibration_data['camera_matrix']
    dist_coeff = calibration_data['distortion_coefficient']

vs = CameraStream().start()
time.sleep(2.0)

#img = cv2.imread('prova.jpg', 0) 

detector = ArucoDetector(cam_matrix, dist_coeff)

#while True:
raw_image = vs.read()
image = detector.undistort(raw_image)
corner = detector.frameDetector(image)
rvec, tvec, _ = detector.estimatePoseMarkers()
print(rvec[0][0])
#print(tvecs)
for i in range(1):
    for j in range(4):
        plt.plot(corner[i][0][j][0],corner[i][0][j][1],marker='v', color="white")
plt.imshow(image)
plt.show()
#comboBig = cv2.resize(image, (640,480))
#cv2.imshow("frame", comboBig)
#key = cv2.waitKey(1) & 0xFF

    
