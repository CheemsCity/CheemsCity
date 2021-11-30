from picamera import PiCamera
from CameraStream import CameraStream
from threading import Thread
import time
from FPS import FPS
import cv2
import matplotlib.pyplot as plt
import numpy as np

print("[INFO] sampling THREADED frames from `picamera` module...")
vs = CameraStream().start()
time.sleep(2.0)
fps = FPS().start()
# loop over some frames...this time using the threaded stream
while fps.numFrames < 100:
    print(fps.numFrames)
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
    frame = vs.read()
    #cv2.imshow("Frame", frame)
    #key = cv2.waitKey(1) & 0xFF
    # update the FPS counter
    fps.frames()
# stop the timer and display FPS information
fps.stop()
cv2.imwrite("prova.jpg", frame)
print("[INFO] elasped time: {:.2f}".format(fps.time()))
print("[INFO] approx. FPS: {:.2f}".format(fps.FPS()))
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()