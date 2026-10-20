//inclusions
#include "DHT.h"
#include <LiquidCrystal_AIP31068_I2C.h>

//Pins
#define LED_LIFE 2 
#define DHT22_DATA A0



int year=26;
int month=10;
int day=20;
int hour=16;
int min=0;
int sec=0;
float old_t = 0;
float old_h = 0;

unsigned long life_time=0;
unsigned long life_time2=0;
unsigned long read_time=0;
unsigned long sec_time=0;


DHT dht(DHT22_DATA, DHT22);

// set the LCD address to 0x3E for a 16 chars and 2 line display
LiquidCrystal_AIP31068_I2C lcd(0x3E,16,2);  

void setup() {
  // put your setup code here, to run once:

  Serial.begin(9600);
  //initialisation des pins
  pinMode(LED_LIFE, OUTPUT);

  dht.begin();
  
  // initialize the lcd 
  lcd.init();
  lcd.setCursor(0,0);
  lcd.print("20/10/26 16:00:00");
  lcd.setCursor(0,1);
  lcd.print("T tt.t C/H hh.h%");
  lcd.setCursor(6,1);
  //impression du charactère "°"
  lcd.print((char)223);
  life_time=millis();
  life_time2=millis();
  read_time=millis();
  sec_time=millis();

}

void loop() {
  // put your main code here, to run repeatedly:
  unsigned long time=millis();
  if(time>life_time){
    life_time=life_time+250;
    digitalWrite(LED_LIFE, !digitalRead(LED_LIFE));
  }
  if(time>read_time){
    read_time=read_time+2000;

    float h = dht.readHumidity();
    float t = dht.readTemperature();
    if(t!=old_t ){
      old_t=t;
      lcd.setCursor(2,1);
      lcd.print(t,1);//ici le 1 veux dire 1 chiffre àaprès la virgule
    }
    if(h!=old_h ){
      old_h=h;
      lcd.setCursor(11,1);
      lcd.print(h,1);
    }

    Serial.println(String(day)+"/"+String(month)+"/"+String(year)+" "+String(hour)+":"+String(min)+":"+String(sec));
    Serial.print("Temperature : ");
    Serial.print(t, 1);
    Serial.print(" oC | Humidite : ");
    Serial.print(h, 1);
    Serial.println(" %\r\n");
  }

  if(time>sec_time){
    sec_time=sec_time+1000;
    if(sec<60){
      sec++;
    }else{
      sec=0;
      if(min<60){
        min++;
      }else{
        min=0;
        if(hour<24){
          hour++;
        }else{
          hour=0;
          if(day<30){
            day++;
          }else{
            day=0;
            if(month<12){
              month++;
            }else{
              month=0;
              year++;
              lcd.setCursor(6,0);
              lcd.print(year);
            }
            lcd.setCursor(3,0);
            lcd.print(month);
          }
          lcd.setCursor(0,0);
          lcd.print(day);
        }
        lcd.setCursor(9,0);
          lcd.print(hour);
      }
      lcd.setCursor(12,0);
      lcd.print(min);
    }
    lcd.setCursor(15,0);
    lcd.print(sec);
  }
  



}
