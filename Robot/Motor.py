from SerialCommunication import SerialCommunication
import time

class Motor:
    
    def __init__():
        self.comm = SerialCommunication()
    
    def Power(self, motor, power):
        #motor è un char che indica se motore destro(r) o sinistro(l)
        #power è un int compreso tra 0 e 100, min e max
        try:
            msg = "s" + "m" + motor + str(power)
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
    
    def Avanti(self, meter)
    
    def Indietro(self, meter)
    
    def Gira(self, angle)