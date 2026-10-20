#include "DHT.h"

//Sensor PIN
#define DHT22_DATA A0

//LED Pins
#define RED 12
#define GREEN  3

DHT dht(DHT22_DATA, DHT22);



void setup() {
  dht.begin();
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
}

void loop() {
  //float h = dht.readHumidity();
  float t = dht.readTemperature();

  //t in °C
  if (t < 20.0) {
    digitalWrite(RED, LOW);
    digitalWrite(GREEN, HIGH);
  }else{
    digitalWrite(RED, HIGH);
    digitalWrite(GREEN, LOW);
  }
  
}
