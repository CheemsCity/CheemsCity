'''
sfrutta la libreria SerialPy
#https://pyserial.readthedocs.io/en/latest/index.html
'''
import serial

import time
import pysignals

from utils.Signals import motorSignal


class SerialCommunication:
    '''Class that implements the communication with the Arduino.

    To make possible for every module to communicate with the arduino without problem
    of having multiple serialcommunication object, the class use a publish and
    subscribe system. This system is implemented through the library PySignal.
    First a signal is declared in Signals.py and then connected with 
    signal_name.connect(SerialCommunication.SendCommand) at the end of this module.
    '''

    port_name = "/dev/ttyACM0"
    baud = 115200
    arduino = serial.Serial(port_name, baud, timeout=1)

    def __init__(self):
        time.sleep(0.1)
        if SerialCommunication.arduino.isOpen():
            print("{} connected!".format(SerialCommunication.arduino.port))
            print("just wait 2 seconds")
            time.sleep(2)
            print("OK!")

    def arduino_reset(self, debug=False):
        '''Force the arduino reset, just as the reset button was pushed.
        
        Args:
            debug: if true, the function will print the status of every passage.
        
        Returns:
            True if successful, False otherwise.
        '''
        ret = False
        try:
            print("cominciando il riavvio dell'arduino")
            SerialCommunication.arduino.close()
            if debug == True:
                print("arduino.close: ok")
            SerialCommunication.arduino.dtr = False
            if debug == True:
                print("arduino.dtr false: ok")
            time.sleep(3)
            #self.arduino.reset_input_buffer()
            #if debug == True:
            # print("proc 3:ok")
            #time.sleep(1)
            SerialCommunication.arduino.dtr = True
            if debug == True:
                print("arduino.dtr true: ok")
            time.sleep(5)
            SerialCommunication.arduino.open()
            print("Arduino reset completato")
            ret = True
        except:
            print("reset non andato a buon fine")

        return ret

    @classmethod
    def send_command(self, sender, msg, **kwargs):
        '''Send a message to the arduino.
        
        The correct way of sending a message to the arduino is trough a pysignal
        connected to this method. This is not a standard method that you can call
        in a script to send a message to the arduino.
        '''
        
        print("tipo del messaggio ricevuto: {}".format(type(msg)))
        try:
            SerialCommunication.arduino.write(msg.encode('utf-8'))
            print("messaggio inviato")
            print(" ")
            return True
        except:
            print("qualcosa è andato storto")
            return False

    def read(self):
        '''Read messages from Raspberry'''
        try:
            SerialCommunication.arduino.flush()
            msg = SerialCommunication.arduino.readline().decode(
                'utf-8').rstrip()
            SerialCommunication.arduino.reset_input_buffer()
            return msg
        except:
            return False


motorSignal.connect(SerialCommunication.send_command)
