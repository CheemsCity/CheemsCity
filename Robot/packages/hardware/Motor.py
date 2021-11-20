from SerialCommunication import SerialCommunication
import time

class Motor:
    
    def __init__():
        self.comm = SerialCommunication()
    
    def Power(self, motor, power):
        #motor è un char che indica se motore destro(r) o sinistro(l)
        #power è un float compreso tra -100 e 100, con i numeri negativi a significare la direzione contraria.
        try:
            msg = "s" + "m" + motor + str(power) + "\n"
            self.comm.SendCommand(msg)
            return True
        else:
            return False
        
    def Test(self):
        print("accendendo motore destro con direzione avanti")
        for i in range(10):
            ret=self.Power('r', 50)
            if(ret == False):
                print("problema comunicazione motore destro")
        time.sleep(1)
        
        print("accendendo motore sinistro con direzione avanti")
        for i in range(10):
            ret=self.Power('l', 50)
            if(ret == False):
                print("problema comunicazione motore sinistro")
        time.sleep(1)
        
        print("accendendo motore destro con direzione indietro")
        for i in range(10):
            ret=self.Power('r', -50)
            if(ret == False):
                print("problema comunicazione motore destro")
        time.sleep(1)
        
        print("accendendo motore sinistro con direzione indietro")
        for i in range(10):
            ret=self.Power('l', -50)
            if(ret == False):
                print("problema comunicazione motore destro")
        time.sleep(1)
    
    def Avanti(self, power):
        ret=self.Power('r',power)
        if(!ret):
            print("problema motore destro")
        ret = self.Power('l', power)
        if(!ret):
            print("problema motore sinistro")

    
    def Indietro(self, power):
        ret = self.Power('r', power*(-1))
        if(!ret):
            print("problema motore destro")
        ret = self.Power('l', power * (-1))
        if(!ret):
            print("problema motore sinistro")

    def Left(self, power):
        ret = self.Power('r', power)
        if(!ret):
            print("problema motore destro")

    def Right(self, power):
        ret = self.Power('l', power)
        if(!ret):
            print("problema motore sinistro")
