from hardware.Motor import Motor
import time
from utils.SerialCommunication import SerialCommunication 

comm = SerialCommunication()
motori = Motor()

motori.Test()
motori.Power('r', 0)
time.sleep(1)
motori.Power('l', 0)
