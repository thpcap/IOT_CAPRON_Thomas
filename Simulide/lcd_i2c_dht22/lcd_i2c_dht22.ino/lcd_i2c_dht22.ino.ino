#include <LiquidCrystal_AIP31068_I2C.h>
#include "DHT.h"
// set the LCD address to 0x3E for a 16 chars and 2 line display
LiquidCrystal_AIP31068_I2C lcd(0x3E,16,2);  
//Sensor PIN
#define DHT22_DATA A0

DHT dht(DHT22_DATA, DHT22);

float old_t = 0;
float old_h = 0;

void setup()
{
  dht.begin();
  // initialize the lcd 
  lcd.init();
  // Print a message to the LCD.
  lcd.setCursor(2,0);
  lcd.print("IMT NE - PPI");
  lcd.setCursor(0,1);
  lcd.print("T tt.toC/H hh.h%");
  lcd.setCursor(6,1);
  //impression du charactère "°"
  lcd.print((char)223);
}

void loop()
{
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if(h!=old_t ){
    old_t=t;
    lcd.setCursor(2,1);
    lcd.print(t,1);//ici le 1 veux dire 1 chiffre àaprès la virgule
  }
  if(h!=old_h ){
    old_h=h;
    lcd.setCursor(11,1);
    lcd.print(h,1);
  }
}