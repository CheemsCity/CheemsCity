import serial, time
#sfrutta la libreria SerialPy
#https://pyserial.readthedocs.io/en/latest/index.html
class SerialCommunication:
    def __init__(self):
        self.portName = "/dev/ttyACM0"
        self.baud = 115200
        self.arduino = serial.Serial(self.portName, self.baud, timeout=1)
        time.sleep(0.1)
        if self.arduino.isOpen():
            print("{} connected!".format(self.arduino.port))

    def ArduinoReset(self,debug=False):
        #forza l'arduino al reset come se fosse stato premuto l'interruttore.
        ret = False
        try:
            print("cominciando il riavvio dell'arduino")
            self.arduino.close()
            if debug == True:
                print("procedura 1:ok")
            self.arduino.dtr = False
            if debug == True:
                print("procedura 2: ok")
            time.sleep(3)
            #self.arduino.reset_input_buffer()
            #if debug == True:
               # print("proc 3:ok")
            #time.sleep(1)
            self.arduino.dtr = True
            if debug == True:
                print("proc4: ok")
            time.sleep(5)
            self.arduino.open()
            print("Arduino reset completato")
            ret = True
        except:
            print("reset non andato a buon fine")
        
        return ret
        
    
        
    
    def SendCommand(self, message):
        #funzione per inviare comandi all'arduino, vedere documentazione sul
        #come impostare questi comandi
        try:
            self.arduino.write(message.encode('utf-8'))
            return True
        except:
            return False

    def Read(self):
        #funzione per leggere i dati inviati dal raspberry
        try:
            self.arduino.flush()
            msg = self.arduino.readline().decode('utf-8').rstrip()
            self.arduino.reset_input_buffer()
            return msg
        except:
            return False

            
            
                  
                  
                
    
                  
        
        
