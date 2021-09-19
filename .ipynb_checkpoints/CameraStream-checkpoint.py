from threading import Thread
import cv2

#distributing the frame gathering to a separate thread will definitely improve performance
# by using a dedicated thread (separate from the main thread) to read frames from our camera sensor, we #can dramatically increase the FPS processing rate of our pipeline. This speedup is obtained by (1) #reducing I/O latency and (2) ensuring the main thread is never blocked, allowing us to grab the most #recent frame read by the camera at any moment in time
class CameraStream:
    def __init__(self, src = 0):
        #src è usato in caso si voglia passare un link
        self.stream = cv2.VideoCapture(src)
        self.ret, self.frame = self.stream.read()
        
        #variable to stop the thread
        self.stop = False
    
    def start(self):
        #start il thread che legge i frame dai video
        Thread(target=self.update, args =()).start()
        return self
    
    def update(self):
        #looppa all'infinito finchè il thread non è bloccato
        while True:
            if self.stopped:
                return
            
            self.ret, self.frame = self.stream.read()
    
    def read(self):
        #ritorna il frame più recente
        return self.frame
    
    def stop(self):
        #indica che il thread deve fermarsi
        self.stopped = True
            