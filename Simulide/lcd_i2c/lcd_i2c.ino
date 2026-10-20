#include <LiquidCrystal_AIP31068_I2C.h>

// set the LCD address to 0x3E for a 16 chars and 2 line display
LiquidCrystal_AIP31068_I2C lcd(0x3E,16,2);  

void setup()
{
  // initialize the lcd 
  lcd.init();
  // Print a message to the LCD.
  lcd.setCursor(1,0);
  lcd.print("HELLO");
  lcd.setCursor(8,1);
  lcd.print("WORLD");
}


void loop()
{
}