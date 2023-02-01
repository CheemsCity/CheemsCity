import serial, time
#sfrutta la libreria SerialPy
#https://pyserial.readthedocs.io/en/latest/index.html
import pysignals

from utils.Signals import motorSignal


class SerialCommunication:

    portName = "/dev/ttyACM0"
    baud = 115200
    arduino = serial.Serial(portName, baud, timeout=1)

    def __init__(self):
        time.sleep(0.1)
        if SerialCommunication.arduino.isOpen():
            print("{} connected!".format(SerialCommunication.arduino.port))

    def ArduinoReset(self, debug=False):
        #forza l'arduino al reset come se fosse stato premuto l'interruttore.
        ret = False
        try:
            print("cominciando il riavvio dell'arduino")
            SerialCommunication.arduino.close()
            if debug == True:
                print("procedura 1:ok")
            SerialCommunication.arduino.dtr = False
            if debug == True:
                print("procedura 2: ok")
            time.sleep(3)
            #self.arduino.reset_input_buffer()
            #if debug == True:
            # print("proc 3:ok")
            #time.sleep(1)
            SerialCommunication.arduino.dtr = True
            if debug == True:
                print("proc4: ok")
            time.sleep(5)
            SerialCommunication.arduino.open()
            print("Arduino reset completato")
            ret = True
        except:
            print("reset non andato a buon fine")

        return ret

    @classmethod
    def SendCommand(self, sender, msg, **kwargs):
        #funzione per inviare comandi all'arduino, vedere documentazione sul
        #come impostare questi comandi
        print("tipo del messaggio ricevuto: {}".format(type(msg)))
        try:
            SerialCommunication.arduino.write(msg.encode('utf-8'))
            print("messaggio inviato")
            print(" ")
            return True
        except:
            print("qualcosa è andato storto")
            return False

    def Read(self):
        #funzione per leggere i dati inviati dal raspberry
        try:
            SerialCommunication.arduino.flush()
            msg = SerialCommunication.arduino.readline().decode(
                'utf-8').rstrip()
            SerialCommunication.arduino.reset_input_buffer()
            return msg
        except:
            return False


motorSignal.connect(SerialCommunication.SendCommand)
