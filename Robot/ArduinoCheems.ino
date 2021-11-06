  // # Editor     : Riccardo from CheemsCity
  // # Date       : 04.11.21
  
  // # Connection:
  // #        M1 pin  -> Digital pin 4
  // #        E1 pin  -> Digital pin 5
  // #        M2 pin  -> Digital pin 7
  // #        E2 pin  -> Digital pin 6
  // #        Motor Power Supply -> Centor blue screw connector(5.08mm 3p connector)
  // #        Motor A  ->  Screw terminal close to E1 driver pin
  // #        Motor B  ->  Screw terminal close to E2 driver pin
  // #
  // # Note: You should connect the GND pin from the DF-MD v1.3 to your MCU controller. They should share the GND pins.
  // #

String msg = "";
bool stringComplete = false;
bool ret = false;
int power = 0;
  int E1 = 6;
  int M1 = 7; //M1 = motore 1
  int E2 = 5;
  int M2 = 4; //M2 = motore 2

void setup() {
  pinMode(M1, OUTPUT);
  pinMode(M2, OUTPUT);
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
      if(msg[2]=='r'){
        //controllo motore destro
        power = msg.substring(3).toInt();
        if (power >0){
          digitalWrite(M1,LOW);
        }
        else{
          digitalWrite(M1,HIGH);
        }
        analogWrite(E1, power*(255/100));
        
      }
      else if(msg[2]=='l'){
        //controllo motore sinistro
        power = msg.substring(3).toInt();
        if (power >0){
          digitalWrite(M2,LOW);
        }
        else{
          digitalWrite(M2,HIGH);
        }
        analogWrite(E2, power*(255/100));
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