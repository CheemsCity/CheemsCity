import math
import time

from threading import Thread
import RPi.GPIO as GPIO

from utils.Signals import motorSignal
from pysignals import receiver
from pkg_resources import resource_string
import yaml


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


class Motor:
    '''Class representing the two robot's DC motors.

    Automatically uses the I2C communication to comunicate with arduino.
    Arduino translates the high level methods of this class in low level commands
    that the DRV8833 can understand. Baud rate and Serial port number are specified
    in the Serial Communication class

    ITA: classe che rappresenta una combinazione di 2 motori appartenenti al robot.
    utilizza la comunicazione I2C per comunicare con Arduino che gestisce tutte le
    operazioni di basso livello, il nome della porta a cui è connesso arduino e il 
    baud rate sono specificati nella classe Serial communication.

    '''

    def __init__(self, left_trim=0, right_trim=0):
        '''ITA: left_trim specifica l'offset in velocità del motore sinistro e 
        right_trim per quello destro, il valore di default è 0.
        i valori saranno calibrati con un programma apposito
        
        ENG: left_trim is the amount of offset of the speed of the left motor, while right_trim
        is the offset of the right motor. Default value is 0.'''

        self._left_trim = left_trim
        self._right_trim = right_trim
        #self.enc = Encoder()
        #self.kin = InvKin()

    def __del__(self):
        self.stop()

    def power(self, motor: str, power: int) -> bool:
        '''Send motor pwm value to arduino.

        Metodo che definisce la potenza dei motori, motor è un char che indica se
        motore destro('r') o sinistro('l'), mentre power è un int compreso tra -100 e 100
        con i numeri negativi a significare la direzione contraria.
        una potenza pari a 0 spegnerà i motori
        '''
        if (power < -100 or power > 100):
            raise ValueError(
                "[ERROR] La potenza dei motori deve essere compresa tra -100 e 100"
            )
            return False
        if (motor != 'r' and motor != 'l'):
            raise ValueError("[ERROR] motor può essere solo uguale a r o l")
            return False
        try:
            if power == 0:
                speed = 0
            elif motor == 'r':
                speed = power + self._right_trim
            else:
                speed = (abs(power) + self._left_trim)
                speed = math.copysign(speed, (-1) * power)
            speed = max(-100, min(100, speed))
            print("velocità impostata ")
            print(speed)
            msg = "<" "s" + "m" + motor + str(-(speed)) + ">"
            print(msg)
            responses = motorSignal.send(sender=self.__class__, msg=msg)
            time.sleep(0.006)
            return True
        except:
            if motor == 'r':
                print("[ERROR] problema comunicazione con motore destro")
            else:
                print("[ERROR] problema comunicazione con motore sinistro")
            return False

    def stop(self):
        '''ITA: ferma tutti i movimenti dei due motori'''
        '''ENG: Stop all movements'''
        self.power('r', 0)
        self.power('l', 0)
    
    def set_vel(elf, motor: str, power: int):
        #dovrà utilizzare i thread per il controllo della velocità del motore
        return

    def test(self):
        print("accendendo motore destro con direzione avanti")
        ret = self.power('r', 100)
        time.sleep(3)
        ret = self.power('r', 0)
        time.sleep(1)

        print("accendendo motore sinistro con direzione avanti")
        ret = self.power('l', 100)
        time.sleep(3)
        ret = self.power('l', 0)
        time.sleep(1)

        print("accendendo motore destro con direzione indietro")
        ret = self.power('r', -100)
        time.sleep(3)
        ret = self.power('r', 0)
        time.sleep(1)

        print("accendendo motore sinistro con direzione indietro")
        ret = self.power('l', -100)
        time.sleep(3)
        ret = self.power('l', 0)
        time.sleep(1)

    def Avanti(self, power):
        '''ITA: si muove avanti ad una desiderata potenza'''
        '''ENG: Move forward at the specified power (0, 100)'''
        ret = self.power('r', power)
        ret = self.power('l', power)

    def Indietro(self, power):
        '''ITA: si muove indietro ad una specificata potenza.
        ENG: Move backward at the specified power (0, 100)'''
        ret = self.power('r', power * (-1))
        ret = self.power('l', power * (-1))

    def Left(self, power):
        ret = self.power('r', power)

    def Right(self, power):
        ret = self.power('l', power)

    #-------------------------------------------------------------------------------
    #                   funzioni utili per il joystick a 6 frecce
    #-------------------------------------------------------------------------------

    #Sud-Est, il robot esegue una curva a potenza power, indietro e verso destra
    def SE(self, power):
        ret = self.power('l', (-1) * (power))

    #Sud-Ovest, il robot esegue una curva a potenza power, indietro e verso sinistra
    def SO(self, power):
        ret = self.power('r', (-1) * (power))

    #Nord-Est, il robot esegue una curva a potenza power, avanti e verso destra
    def NE(self, power):
        ret = self.power('l', power)

    #Nord-Ovest, il robot esegue una curva a potenza power, avanti e verso sinistra
    def NO(self, power):
        ret = self.power('r', power)
