from utils.SerialCommunication import SerialCommunication
import time

class Motor:
    
    def __init__(self):
        self.comm = SerialCommunication()

    def __del__(self):
        self.Stop()

    
    def Power(self, motor, power):
        #motor è un char che indica se motore destro(r) o sinistro(l)
        #power è un float compreso tra -100 e 100, con i numeri negativi a significare la direzione contraria.
        try:
            msg = "s" + "m" + motor + str(-(power)) + "\n"
            print(msg)
            self.comm.SendCommand(msg)
            time.sleep(0.01)
            return True
        except:
            return False
    
    def Stop(self):
        self.Power('r', 0)
        self.Power('l', 0)
        
    def Test(self):
        print("accendendo motore destro con direzione avanti")
        for i in range(1000):
            ret=self.Power('r', 100)
            if(ret == False):
                print("problema comunicazione motore destro")
        ret = self.Power('r', 1)
        time.sleep(1)
        
        print("accendendo motore sinistro con direzione avanti")
        for i in range(1000):
            ret=self.Power('l', 100)
            if(ret == False):
                print("problema comunicazione motore sinistro")
        ret = self.Power('l', 0)
        time.sleep(1)
        
        print("accendendo motore destro con direzione indietro")
        for i in range(1000):
            ret=self.Power('r', -100)
            if(ret == False):
                print("problema comunicazione motore destro")
        ret = self.Power('r', 0)
        time.sleep(1)
        
        print("accendendo motore sinistro con direzione indietro")
        for i in range(1000):
            ret=self.Power('l', -100)
            if(ret == False):
                print("problema comunicazione motore destro")

        ret = self.Power('l', 0)
        time.sleep(1)
    
    def Avanti(self, power):
        ret=self.Power('r',power)
        if(ret==False):
            print("problema motore destro")
        ret = self.Power('l', power)
        if(ret==False):
            print("problema motore sinistro")

    
    def Indietro(self, power):
        ret = self.Power('r', power*(-1))
        if(ret==False):
            print("problema motore destro")
        ret = self.Power('l', power * (-1))
        if(ret==False):
            print("problema motore sinistro")

    def Left(self, power):
        ret = self.Power('r', power)
        if(ret==False):
            print("problema motore destro")

    def Right(self, power):
        ret = self.Power('l', power)
        if(ret==False):
            print("problema motore sinistro")
    
    #-------------------------------------------------------------------------------
    #                   funzioni utili per il joystick a 6 frecce
    #-------------------------------------------------------------------------------
    
    #Sud-Est, il robot esegue una curva a potenza power, indietro e verso destra
    def SE(self, power):
        ret = self.Power('l', (-1)*(power))
        if(ret==False):
            print("problema motore sinistro")
    
    #Sud-Ovest, il robot esegue una curva a potenza power, indietro e verso sinistra
    def SO(self, power):
        ret = self.Power('r', (-1)*(power))
        if(ret==False):
            print("problema motore destro")
    
    #Nord-Est, il robot esegue una curva a potenza power, avanti e verso destra
    def NE(self, power):
        ret = self.Power('l', power)
        if(ret==False):
            print("problema motore sinistro")
    
    #Nord-Ovest, il robot esegue una curva a potenza power, avanti e verso sinistra
    def NO(self, power):
        ret = self.Power('r', power)
        if(ret==False):
            print("problema motore destro")
        

    
    
                  
