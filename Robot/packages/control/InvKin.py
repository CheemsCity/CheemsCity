#classe legata ai comanda di cinematica inversa
#class linked to inverse kynematics

from hardware.Motor import Motor
from hardware.Encoder import Encoder
from pkg_resources import resource_string
import yaml
import numpy as np

class InvKin:
    def __init__(self):

        #load robot physical parameters file
        #carichiamo il file con i parametri del robot
        file = resource_string('control','HardwareSettings.yml')
        settings = yaml.full_load(file)

        #insert this settings into variables
        #assegnamo i parametri a delle variabili
        self.wheelRadius = settings['wheelRadius']
        self.encoderResolution = settings['encoderResolution']
        self.wheelDistance = settings['wheelDistance']

        #initialize Motor object
        #definiamo l'oggetto motor
        self.mot = Motor(left_trim=-3) #oggetto per comunicazione seriale con i motori

        self.enc = Encoder()

    def MoveUpDistance(self, meters, speed):
        self.enc.ResetEncoder()
        distance = 0
        i = 0
        while distance < meters:
            i = i + 1
            self.mot.Avanti(speed)
            print("tickL = ", self.enc.tickL)
            print("tickR = ", self.enc.tickR)
            distance = ((self.enc.tickL + self.enc.tickR)/2)*(self.wheelRadius * np.pi / self.encoderResolution)
            print(i)
            if i == 148:
                self.mot.Stop()
                break
    
    def Stop(self):
        self.mot.Stop()

if __name__ == '__main__':
    commands = InvKin()
    commands.MoveUpDistance(0.3, 65)
    