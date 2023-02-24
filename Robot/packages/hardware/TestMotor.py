import time

import serial

from hardware.Motor import Motor
from utils.SerialCommunication import SerialCommunication

'''use this script to test if the motors work without problems'''

comm = SerialCommunication()
motori = Motor()

motori.test()
motori.power('r', 0)
time.sleep(1)
motori.power('l', 0)
