import time

import serial

from hardware.Motor import Motor
from utils.SerialCommunication import SerialCommunication

comm = SerialCommunication()
motori = Motor()

motori.test()
motori.power('r', 0)
time.sleep(1)
motori.power('l', 0)
