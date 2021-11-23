from threading import Thread
from picamera import PiCamera
#https://picamera.readthedocs.io/en/release-1.13/api_array.html
from picamera.array import PiRGBArray
import cv2

#distributing the frame gathering to a separate thread will definitely improve performance
# by using a dedicated thread (separate from the main thread) to read frames from our camera sensor, 
#we can dramatically increase the FPS processing rate of our pipeline. This speedup is obtained by 
#(1)reducing I/O latency and (2) ensuring the main thread is never blocked, allowing us to grab the most recent frame read by the camera at any moment in time
class CameraStream:
    def __init__(self, resolution=(320,240), framerate = 32):
        #inizializzo lo stream
        #codice ispirato a pyimagesearch
        self.camera = PiCamera()
        self.camera.rotation = 180 #montata al contrario per necessità in attesa di un modello finito
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        self.frame = None
        
        #variable to stop the thread
        self.stopped = False
    
    def start(self):
        #start il thread che legge i frame dai video
        Thread(target=self.update, args =()).start()
        return self
    
    def update(self):
        #looppa all'infinito finchè il thread non è bloccato
        for f in self.stream:
            #prendi il frame dalla stream
            self.frame = f.array
            self.rawCapture.truncate(0)
            
            
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return
    
    def read(self):
        #ritorna il frame più recente
        return self.frame
    
    def stop(self):
        #indica che il thread deve fermarsi
        self.stopped = True