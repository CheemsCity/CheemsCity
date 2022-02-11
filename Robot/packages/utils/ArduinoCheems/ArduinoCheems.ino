  // # Editor     : Riccardo from CheemsCity
  // # Date       : 04.11.21
  
  // # Connection:
  // #        MA1  pin  -> Digital pin 5
  // #        A2 pin  -> Digital pin 6
  // #        MMB1 pin  -> Digital pin 9
  // #        MB2 pin  -> Digital pin 10
  // #        Motor Power Supply -> Centor blue screw connector(5.08mm 3p connector)
  
  // # collegare standby a 5 volt arduibo

String msg = "";
bool stringComplete = false;
bool ret = false;
int power = 0;
  int MA1 = 5;
  int MA2 = 6; //A = motore 1
  int MB1 = 9;
  int MB2 = 10; //B = motore 2

void setup() {
  pinMode(MA1, OUTPUT);
  pinMode(MA2, OUTPUT);
  pinMode(MB1, OUTPUT);
  pinMode(MB2, OUTPUT);

  //comincia con i driver off
  digitalWrite(MA1, LOW);
  digitalWrite(MA2, LOW);
  digitalWrite(MB1, LOW);
  digitalWrite(MB2, LOW);

  Serial.begin(57600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB
  }
}

void loop() {
  if(stringComplete){
    //inserire tutte le condizioni derivanti dalla lettura
    ret = msgAnal(msg);
  }

  //reset string
  stringComplete = false;
  msg = "";
  delay(10); //capire il giusto tempo di pausa
  if(Serial.available()>0){ serialEvent();}
}

void sendData() {
  //write data
  Serial.print(" received : ");
  Serial.print(msg);
}

void serialEvent(){
  while(Serial.available()){
    char inChar = (char)Serial.read();
    msg += inChar;
    if (inChar == '\n'){
      stringComplete = true;
    }    
  }
}

void setPower(int power, int IN1_PIN, int IN2_PIN){
	int pwm =0;
	if(power < 0){
		pwm = int(-power*(255/100));
		analogWrite(IN1_PIN, pwm);
		digitalWrite(IN2_PIN, pwm);
	}
	else{
		pwm = int(power*(255/100));
		digitalWrite(IN1_PIN, pwm);
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
      if(msg[2]=='l'){
        //controllo motore destro
        power = msg.substring(3).toInt();
	setMotorPower(power,'l');
        
      }
      else if(msg[2]=='r'){
        //controllo motore sinistro
        power = msg.substring(3).toFloat();
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
