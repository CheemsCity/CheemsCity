#classe legata ai comanda di cinematica inversa
#class linked to inverse kynematics
#Vecchia, va unita alla classe motor

from hardware.Motor import Motor
from hardware.Encoder import Encoder
from pkg_resources import resource_string
import yaml
import numpy as np


class InvKin:

    def __init__(self):

        #load robot physical parameters file
        #carichiamo il file con i parametri del robot
        file = resource_string('control', 'HardwareSettings.yml')
        settings = yaml.full_load(file)

        #insert this settings into variables
        #assegnamo i parametri a delle variabili
        self.wheelRadius = settings['wheelRadius']
        self.encoderResolution = settings['encoderResolution']
        self.wheelDistance = settings['wheelDistance']
        self.k = settings['motorConstant']
        self.left_trim = settings['leftTrim']
        self.right_trim = settings['rightTrim']

        #initialize Motor object
        #definiamo l'oggetto motor
        self.mot = Motor(right_trim=self.rightTrim, left_trim=self.left_trim
                         )  #oggetto per comunicazione seriale con i motori
        self.enc = Encoder()

    def MoveUpDistance(self, meters, speed):
        self.enc.ResetEncoder()
        distance = 0
        while distance < meters:
            self.mot.Avanti(speed)
            print("tickL = ", self.enc.tickL)
            print("tickR = ", self.enc.tickR)
            distance = ((self.enc.tickL + self.enc.tickR) / 2) * (
                self.wheelRadius * np.pi / self.encoderResolution)

    def Stop(self):
        self.mot.Stop()

    def InverseKinematics(v, w):
        '''---------INPUT------------
            v -> velocity of the center of mass of the robot
            w -> angular velocity of the robot
        '''

        #assumiamo costante dei motori uguale per destro e sinistro
        #we assume the motor constant k for both motors
        k_r = k_l = self.k

        #inverse kinematics 1 (from v and w to single motor rotation)
        w_r = (v + 0.5 * self.wheelDistance * w) / self.wheelRadius
        w_r = (v - 0.5 * self.wheelDistance * w) / self.wheelRadius

        #inverse kinematics 2 (from rad/s to duty cicle)
        u_r = w_r / k_r
        u_l = w_l / k_l

        return max(min(u_r, 255), 0), max(min(u_l, 255), 0)


if __name__ == '__main__':
    commands = InvKin()
    commands.MoveUpDistance(0.3, 65)
