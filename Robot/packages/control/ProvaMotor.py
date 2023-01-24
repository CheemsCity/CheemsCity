from hardware.Motor import Motor
import time
from utils.SerialCommunication import SerialCommunication 
import serial

#comm = SerialCommunication()
#motori = Motor()

portName = "/dev/ttyACM0"
baud = 115200
arduino = serial.Serial(portName, baud, timeout=1)

print("arduino stato: {}".format(arduino.isOpen()))
msg = "<smr100>"
ret = arduino.write(msg.encode('utf-8'))
print("ritorno 1: {}".format(ret))
time.sleep(4)

'''
motori.Test()
motori.Power('r', 0)
time.sleep(1)
motori.Power('l', 0)
'''

msg = "<smr0>"
ret2 = arduino.write(msg.encode('utf-8'))
print("ritorno 1: {}".format(ret))
time.sleep(1)