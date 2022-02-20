from utils.SerialCommunication import SerialCommunication
import time

class Motor:
    '''ITA: classe che rappresenta una combinazione di 2 motori appartenenti al robot,
    utilizza la comunicazione I2C per comunicare con Arduino che gestisce tutte le
    operazioni di basso livello, il nome della porta a cui è connesso arduino e il 
    baud rate sono specificati nella classe Serial communication.

    ENG: Class representing the two robot's DC motors. Automatically uses the I2C
    communication to comunicate with arduino. Arduino translates the high level methods
    of this class in low level commands thath the DRV8833 can understand.
    Baud rate and Serial port number are specified in the Serial Communication class'''

    
    def __init__(self, left_trim =0, right_trim = 0):
        '''ITA: left_trim specifica l'offset in velocità del motore sinistro e 
        right_trim per quello destro, il valore di default è 0.
        i valori saranno calibrati con un programma apposito
        
        ENG: left_trim is the amount of offset of the speed of the left motor, while right_trim
        is the offset of the right motor. Default value is 0.'''

        self.comm = SerialCommunication()
        self._left_trim = left_trim
        self._right_trim = right_trim

    def __del__(self):
        self.Stop()

    
    def Power(self, motor:str, power:int) -> bool:
        '''Metodo che definisce la potenza dei motori, motor è un char che indica se
        motore destro('r') o sinistro('l'), mentre power è un int compreso tra -100 e 100
        con i numeri negativi a significare la direzione contraria.
        una potenza pari a 0 spegnerà i motori'''
        if (power < -100 or power > 100):
            raise ValueError("[ERROR] La potenza dei motori deve essere compresa tra -100 e 100")
            return False
        if (motor != 'r' and motor !='l'):
            raise ValueError("[ERROR] motor può essere solo uguale a r o l")
            return False
        try:
            if power == 0:
                speed = 0
            elif motor=='r':
                speed = power + self._right_trim
            else:
                speed = power + self._left_trim
            speed = max(-100, min(100, speed))
            print("velocità impostata ")
            print(speed)
            msg = "s" + "m" + motor + str(-(speed)) + "\n"
            print(msg)
            self.comm.SendCommand(msg)
            time.sleep(0.01)
            return True
        except:
            if motor=='r':
                print("[ERROR] problema comunicazione con motore destro")
            else:
                print("[ERROR] problema comunicazione con motore sinistro")
            return False
    
    def Stop(self):
        '''ITA: ferma tutti i movimenti dei due motori'''
        '''ENG: Stop all movements'''
        self.Power('r', 0)
        self.Power('l', 0)
        
    def Test(self):
        print("accendendo motore destro con direzione avanti")
        for i in range(1000):
            ret=self.Power('r', 100)
        ret = self.Power('r', 0)
        time.sleep(1)
        
        print("accendendo motore sinistro con direzione avanti")
        for i in range(1000):
            ret=self.Power('l', 100)
        ret = self.Power('l', 0)
        time.sleep(1)
        
        print("accendendo motore destro con direzione indietro")
        for i in range(1000):
            ret=self.Power('r', -100)
        ret = self.Power('r', 0)
        time.sleep(1)
        
        print("accendendo motore sinistro con direzione indietro")
        for i in range(1000):
            ret=self.Power('l', -100)
        ret = self.Power('l', 0)
        time.sleep(1)
    
    def Avanti(self, power):
        '''ITA: si muove avanti ad una desiderata potenza'''
        '''ENG: Move forward at the specified power (0, 100)'''
        ret=self.Power('r',power)
        ret = self.Power('l', power)

    def Indietro(self, power):
        '''ITA: si muove indietro ad una specificata potenza.
        ENG: Move backward at the specified power (0, 100)'''
        ret = self.Power('r', power*(-1))
        ret = self.Power('l', power * (-1))

    def Left(self, power):
        ret = self.Power('r', power)

    def Right(self, power):
        ret = self.Power('l', power)
    
    #-------------------------------------------------------------------------------
    #                   funzioni utili per il joystick a 6 frecce
    #-------------------------------------------------------------------------------
    
    #Sud-Est, il robot esegue una curva a potenza power, indietro e verso destra
    def SE(self, power):
        ret = self.Power('l', (-1)*(power))
    
    #Sud-Ovest, il robot esegue una curva a potenza power, indietro e verso sinistra
    def SO(self, power):
        ret = self.Power('r', (-1)*(power))
    
    #Nord-Est, il robot esegue una curva a potenza power, avanti e verso destra
    def NE(self, power):
        ret = self.Power('l', power)
    
    #Nord-Ovest, il robot esegue una curva a potenza power, avanti e verso sinistra
    def NO(self, power):
        ret = self.Power('r', power)
        

    
    
                  
