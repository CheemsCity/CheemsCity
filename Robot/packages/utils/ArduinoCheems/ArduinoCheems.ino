  // # Editor     : Riccardo from CheemsCity
  // # Date       : 04.11.21
  
  // # Connection:
  // #        MA1  pin  -> Digital pin 5
  // #        A2 pin  -> Digital pin 6
  // #        MMB1 pin  -> Digital pin 9
  // #        MB2 pin  -> Digital pin 10
  // #        Motor Power Supply -> Centor blue screw connector(5.08mm 3p connector)
  
  // # collegare standby a 5 volt arduibo

//------------------------------ Assegnazione Pin ------------------
//------------------------------ pin assignements ------------------
int MA1 = 5; //A = motore 1  Destro (motor 1, right)
int MA2 = 6; 
int MB1 = 9; //B = motore 2 Sinistro (motor 2, left)
int MB2 = 10; 
// interrupts PIN
int sensorS = 3; //encoder S (sinista, left)
int sensorD = 2;  //encoder D (destra, right)

//---------------------------- Message utils -----------------------
//variables needed to receive orders from raspberry
//variabili necessarie per gestire comunicazione con raspberry
const byte numChars = 32;
char receivedChars[numChars];
char value[4];
bool stringComplete = false;
bool ret = false;
bool newData = false;
//-------------------------- other Datas ----------------------------
int   const  holes  = 20;   // number of slots in optical wheel encoder
                            //numero di fori nell cerchio nero dell'encoder
int   power  = 0;
int   speedMa = 0;          //Speed Motor A, Velocità motore A *ticks/s
int   speedMb = 0;          //Speed Motor B, Velocità motore B *ticks/s
int   tickA = 0;            //number of ticks counted for Motor A
int   tickB = 0;            //number of ticks counted for Motor B
long  prevT = 0;
long  time = 0;
int   posPrev = 0;
int   i = 0;
//------------------------ Timers ----------------------------------
//utilizziamo il timer T2 (utilizzato dalla funzione tone), 8 bit
//questo è seguito da un prescaler per modificare il valore.
//si può controllare il timer tramite i registri TTCR2A O TTCR2B
//mentre il conteggio è tenuto nel registro TCNT2
//mentre il registro TIMSK2 associa l'azione alla fine del timer.


void setup() {
  pinMode(MA1, OUTPUT);
  pinMode(MA2, OUTPUT);
  pinMode(MB1, OUTPUT);
  pinMode(MB2, OUTPUT);
  pinMode(sensorS, INPUT_PULLUP);
  pinMode(sensorD, INPUT_PULLUP);
  
  //definiamo le funzioni per l'interrupt degli encoder
  //define interrupts related to encoders
  //attachInterrupt(digitalPinToInterrupt(sensorS), updateTickB, HIGH);
  //attachInterrupt(digitalPinToInterrupt(sensorD), updateTickA, HIGH);

  //comincia con i driver off
  digitalWrite(MA1, LOW);
  digitalWrite(MA2, LOW);
  digitalWrite(MB1, LOW);
  digitalWrite(MB2, LOW);

  

  Serial.begin(115200);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
}

void loop() {
  recvWithStartEndMarkers();
  if(newData==true) {
    Serial.println(receivedChars);
    msgAnal(receivedChars);
    newData = false;
  }
  //sendData();
}
void updateTickB(){
  tickB = tickB + 1;
}

void updateTickA(){
  tickA = tickA + 1;
}

void sendData() {

  Serial.print('<');
  Serial.print(tickA);
  Serial.print('>');
  Serial.print('\n');
}

void recvWithStartEndMarkers() {
  static bool recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while(Serial.available() > 0 && newData == false){
    rc = (char)Serial.read();

    if (recvInProgress==true) {
      if(rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
            ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

void setPower(int power, int IN1_PIN, int IN2_PIN){
	int pwm =0;
	
	if(power == 0){
		digitalWrite(IN1_PIN, LOW);
		digitalWrite(IN2_PIN, LOW);
	}
	else if(power < 0){
		pwm = int(-power*(255/100));
		analogWrite(IN1_PIN, pwm);
		digitalWrite(IN2_PIN, LOW);
	}
	else{
		pwm = int(power*(255/100));
		digitalWrite(IN1_PIN, LOW);
		analogWrite(IN2_PIN, pwm);
	}
}

void setMotorPower(int power, char motor){
	if(motor == 'r'){
		setPower(-(power), MA1, MA2);
	}
	else if(motor == 'l'){
		setPower(power, MB1, MB2);
	}
}

bool msgAnal(String msg){
  int len = msg.length();
  
  //è una richiesta di info
  if(msg[0] == 'r'){
    //richesta, andare poi a fornire i vari casi
  }
  
  //è un comando 
  else if(msg[0] == 's'){
    if(msg[1]=='m'){
      //è un comando di gestione dei motori
      i=3;
        while(msg[i]!='\0'){
          value[i-3]=msg[i];
          i=i+1;
        }
        value[i-3] = '\0';
        Serial.println(value);
        power = atoi(value);
        Serial.println(power);
      if(msg[2]=='l'){
        //controllo motore destro
        //power = msg.substring(3).toInt();
        //Serial.println(power);
	      setMotorPower(power,'l');
        
      }
      else if(msg[2]=='r'){
        //controllo motore sinistro
        //power = msg.substring(3).toInt();
        setMotorPower(power, 'r');
      }
      else{
        return false;
        Serial.print("Errore nei motori"); //provare a creare un sistema di log
      }
    }
  }
  else{
    return false;
  }
}
