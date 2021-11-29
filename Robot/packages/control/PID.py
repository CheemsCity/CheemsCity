import time

class PID:

    def __init__(self, kp, ki, kd):
    # variabili essenziali per il funzionamento del PID sono:
    #1) SETPOINT: misura attesa
    #2) PV (process variable): la variabile che riceviamo.
    #3) coefficiente kp, ki, kd
    #4) errore = differenza tra il SETPOINT e il PV
        self.SETPOINT = 0
        self.PV = 0
        self.error = 0
        self.kp = kp
        self.ki = ki
        self.kd = kd
    # scriviamo il PID in tempo discreto che avrà bisogno di queste variabili ausiliarie:
        # variabili utili per il calcolo della derivata discreta
        self.lastError = 0
        self.Derivative = 0
        #tempo di campionamento
        self.currTime = time.time()
        self.prevTime = self.currTime
        self.deltaTime
        # definiamo l'integrale discreto come la sommma di tutti gli errori per il tempo di campionamento
        # ogni tot tempo dovremo azzerarlo per evitare che errori vecchi diano ancora problemi 
        self.UniversalTime = 0 # arrivati a tot si azzera per non alzare l'integrale
        self.Integral = 0
        #valore di controllo finale
        self.u = 0

    def compute(self, pv):
        time.sleep(0.2)

        #prendiamo il tempo e calcoliamo delta time
        self.currTime = time.time()
        self.deltaTime = self.currTime - self.prevTime
        self.UniversalTime += self.deltaTime

        # Applicazione algoritmo PID
        self.u = 0
        self.PV = pv
        self.error = self.SETPOINT - self.PV
        self.Derivative = ( (self.error - self.lastError) / self.deltaTime ) if self.deltaTime > 0 else 0
        if(self.i=='tot'): #tot da decidere
            i=0
            self.Integral = 0
        self.Integral += self.error * self.deltaTime * self.ki   

        #windup implementazione
        if self.Integral > 'tot':
            self.Integral = 'tot'
        if self.Integral < 'tot':
            self.Integral = 'tot'

        self.i += 1
        self.u = self.kp * self.error + self.ki * self.Integral + self.kd * self.Derivative
        #il valore dell'output andrà tra 0 e 50

        self.lastError = self.error
        self.prevTime = self.currTime
        return self.u
    
    #utile per cambiare il valore 
    def tune(self, kp, ki, kd):
        print("Setto il coefficiente P a : " + kp)
        self.kp = kp
        print("Setto il coefficiente I a : " + ki)
        self.ki = ki
        print("Setto il coefficiente D a : " + kd)
        self.kd = kd
    


     