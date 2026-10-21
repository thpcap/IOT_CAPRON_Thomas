//inclusions
#include "DHT.h"
#include "rgb_lcd.h"
#include <RTClib.h>
#include "WiFiS3.h"
#include <NTPClient.h>
#include <WiFiUdp.h>

//Pins
#define LED_LIFE 2 
#define DHT22_DATA A0

//arduino_secrets.h header file
#define SECRET_SSID "IoT IMT Nord Europe"
#define SECRET_PASS "72Hin@R*"

#define Version (String)1.0

const char* IpNTP = "192.168.1.254";

float old_t = 0;
float old_h = 0;

unsigned long life_time=0;
unsigned long life_time2=0;
unsigned long read_time=0;
unsigned long sec_time=0;

RTC_Millis rtc;
DHT dht(DHT22_DATA, DHT22);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, IpNTP, 0, 60000);
rgb_lcd lcd;

int status = WL_IDLE_STATUS;


void InitializeWifi(){
  lcd.clear();
  int i=1;
  while (status != WL_CONNECTED) {
    lcd.setCursor(0,0);
    lcd.print("Connecting...");
    lcd.setCursor(0,1);
    lcd.print(String(i)+" try");
    // Connect to WPA/WPA2 network:
    status = WiFi.begin(SECRET_SSID, SECRET_PASS);
    digitalWrite(LED_LIFE, !digitalRead(LED_LIFE));
    // wait 10 seconds for connection:
    delay(10000);
    i++;
  }

  
  updateNTP();

  //reset the screen
  /*lcd.setCursor(0,0);
  lcd.print("20/10/26 16:00:00");
  lcd.setCursor(0,1);
  lcd.print("T tt.t C/H hh.h%");
  lcd.setCursor(6,1);
  //impression du charactère "°"
  lcd.print((char)223);*/
}

void updateNTP(){
  //updates the date of the RTC
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("RTC syncing");
  timeClient.begin();
  if (timeClient.forceUpdate()) {
    // NTP fournit ici l'heure UTC
    unsigned long epoch = timeClient.getEpochTime();

    // Conversion UTC vers date/heure
    rtc.adjust(DateTime(epoch));

    lcd.setCursor(0,01);
    lcd.print("RTC sync");
  } else {
    lcd.setCursor(0,1);
    lcd.print("RTC sync fail");
  }
  delay(1000);
  resetScreen();
}
//reset the screen to the normal screen
void resetScreen(){
  lcd.setCursor(0,0);
  DateTime now = rtc.now();
  lcd.print("V"+Version+" "+
              String(now.day()) + "/" +
              String(now.month()) + "/" +
              String(now.year() % 100));
  lcd.setCursor(0,1);
  IPAddress ip = WiFi.localIP();
  lcd.print(ip);
}


void setup() {
  // put your setup code here, to run once:


  Serial.begin(9600);
  //initialisation des pins
  pinMode(LED_LIFE, OUTPUT);
  //initialisations
  dht.begin();
  rtc.begin(DateTime(F(__DATE__), F(__TIME__)));

  // initialize the lcd 
  lcd.begin(16, 2);

  InitializeWifi();





  
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
    /*if(t!=old_t ){
      old_t=t;
      lcd.setCursor(2,1);
      lcd.print(t,1);//ici le 1 veux dire 1 chiffre àaprès la virgule
    }
    if(h!=old_h ){
      old_h=h;
      lcd.setCursor(11,1);
      lcd.print(h,1);
    }*/

    //réinitialisation de l'écran pour afficher la temperature et l'humidité
    Serial.print("Temperature : ");
    Serial.print(t, 1);
    Serial.print(" oC | Humidite : ");
    Serial.print(h, 1);
    Serial.println(" %\r\n");
  }

  if(time>sec_time){
    sec_time=sec_time+1000;
    DateTime now = rtc.now();
    lcd.setCursor(0,0);
    lcd.print("V"+Version+" "+String(now.day()) + "/" +
                String(now.month()) + "/" +
                String(now.year() % 100));
    /*
    lcd.setCursor(0,0);
    lcd.print(String(now.day()) + "/" +
              String(now.month()) + "/" +
              String(now.year() % 100) + " " +
              String(now.hour()) + ":" +
              String(now.minute()) + ":" +
              String(now.second()%100)
            );*/
  }
  delay(50);
  


}
