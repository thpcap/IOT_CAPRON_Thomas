#define LastBargraphPin 12
#define FirstBargraphPin 3

int iterator = 3;

void setup() {
  // put your setup code here, to run once:
  //Pins du bargraph de 3 à 12
  for(int i = FirstBargraphPin;i <= LastBargraphPin;i++){
    pinMode(i,OUTPUT);
  }
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(iterator , HIGH);
  if(iterator==FirstBargraphPin){
    //si le pin à activer est le 3 le pin 12 doit ^etre désactivé
    digitalWrite(LastBargraphPin , LOW);
  }else{
    digitalWrite(iterator-1 , LOW);
  }
  if(iterator >= LastBargraphPin){
    iterator = FirstBargraphPin;
  }else{
    iterator++;
  }
  delay(100);
}
