
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
        #tempo di campionamento da decidere 
        self.deltaTime = 0
        # definiamo l'integrale discreto come la sommma di tutti gli errori per il tempo di campionamento
        # ogni tot tempo dovremo azzerarlo per evitare che errori vecchi diano ancora problemi 
        self.i  = 0 #count, arrivati a tot si azzera per non alzare l'integrale
        self.Integral = 0
        #valore di controllo finale
        self.u = 0

    def PIDloop(self, pv, kp = 0, ki = 0, kp = 0):
        #controllo principale loop
        self.u = 0
        self.PV = pv
        self.error = self.SETPOINT - self.PV
        self.Derivative = ( (self.error - self.lastError) / self.deltaTime )
        self.UniversalTime 
        if(i=='tot'): #tot da decidere
            i=0
            self.Integral = 0
        self.Integral += self.error * self.deltaTime * self.i
        self.i ++
        





    
    def PIDloopGraph(self):
        #l'idea sarebbe creare un loop pid che conserva tutti i dati per creare un grafico
        # per debug
        self.u = 0
     