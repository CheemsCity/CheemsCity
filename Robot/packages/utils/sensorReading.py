from threading import Thread
import time

class sensorReading:
    def __init__(self, communication):

        self.comm = communication
        #ticks motore destro e sinistro
        #right and left motor ticks from encoders
        self.tickD = 0
        self.tickS = 0
        
        #variable to stop the thread
        self.stopped = False

        self.message = None

    def start(self):
        #start il thread che legge i frame dai video
        Thread(target=self.update, args =()).start()
        return self
    
    def update(self):
        #looppa all'infinito finchè il thread non è bloccato
        while not self.stopped:
            try:
                self.message = self.comm.read()
            except:
                time.sleep(1/2000)
                continue
            
        if self.stopped:
            self.stream.close()
            self.rawCapture.close()
            self.camera.close()
            return
    
    def read(self):
        #ritorna il frame più recente
        return self.message
   
    def stop(self):
        #indica che il thread deve fermarsi
        self.stopped = True