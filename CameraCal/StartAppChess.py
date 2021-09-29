from CamerCal import ChessboardApp
import time
import cv2

vs = cv2.VideoCapture(0)
time.sleep(2.0)

pba = ChessboardApp(vs,"")
pba.root.mainloop()
