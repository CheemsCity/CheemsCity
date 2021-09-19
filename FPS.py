import datetime

#class to calculate the fps used in a process
class FPS:
    def __init__(self):
        #store start time, end time, number of frames
        self._start = None
        self._end = None
        self.numFrames = 0
        
    def start(self):
        #start timer
        self._start = datetime.datetime.now()
        return self
    
    def stop(self):
        #stop timer
        self._stop = datetime.datetime.now()
        return self
    
    def frames(self):
        self.numFrames += 1
        return self
    
    def time(self):
        #delta time
        return (self._end - self._start).total_seconds()
    
    def FPS(self):
        #compute frame per second
        return self.numFrames / self.time()