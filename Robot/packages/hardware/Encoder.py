from threading import Thread
import time
import RPi.GPIO as GPIO

class Encoder:
    def __init__(self):

        Eright = 18
        Eleft = 19
        #we need to specify wich convention we are using
        #for the pin's number
        #specifichiamo convenzione numero pin rapsberry
        GPIO.setmode(GPIO.BCM)

        #right encoder
        #encoder destro
        GPIO.setup(Eright, GPIO.IN)
        #left encoder
        #encoder sinistro
        GPIO.setup(Eleft, GPIO.IN)

        #thread to read the encoder
        #thread per leggere encoder
        GPIO.add_event_detect(Eright, GPIO.RISING, callback=self.updateR)
        GPIO.add_event_detect(Eleft, GPIO.RISING, callback=self.updateL)


        #ticks motore destro e sinistro
        #right and left motor ticks from encoders
        self.tickR = 0
        self.tickL = 0

    def updateR(self, Eright):
        #update tick counter Right
        self.tickR = self.tickR + 1
    
    def updateL(self, Eleft):
        #update tick counter L
        self.tickL = self.tickL + 1
    
    def ResetR(self):
        self.tickR = 0

    def ResetL(self):
        self.tickL = 0
    
    def ResetEncoder(self):
        self.tickR = 0
        self.tickL = 0

    def stop(self):
        GPIO.remove_event_detect(Eright)
        GPIO.remove_event_detect(Eleft)