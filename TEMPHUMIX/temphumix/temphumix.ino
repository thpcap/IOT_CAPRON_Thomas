//inclusions
#include "DHT.h"
#include "rgb_lcd.h"
#include <RTClib.h>
#include "WiFiS3.h"
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <ArduinoMqttClient.h>

//Pins
#define LED_LIFE 2 
#define DHT22_DATA A0
#define LastBargraphPin 12
#define FirstBargraphPin 3

//arduino_secrets.h header file
#define SECRET_SSID "IoT IMT Nord Europe"
#define SECRET_PASS "72Hin@R*"

#define Version (String)"1.1"

#define ID_Sensor (String)"42900"

const char* IpNTP = "192.168.1.254";
// Broker MQTT
const char broker[] = "192.168.1.1";
const int port = 1883;

const char mqttUser[] = "mos_user";
const char mqttPassword[] = "mos_user";

RTC_Millis rtc;
DHT dht(DHT22_DATA, DHT22);
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, IpNTP, 7200, 60000);
rgb_lcd lcd;
WiFiClient wifiClient;
MqttClient mqttClient(wifiClient);


int status = WL_IDLE_STATUS;

float old_t = 0;
float old_h = 0;

unsigned long life_time=0;
unsigned long read_time=0;
unsigned long sec_time=0;

//Does the sesor measure
bool measure = true;
//Life LED Blink Time
int blink_time=250;
//blink time stocké en attente 
int blink_time_tmp = 0;

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
  
  Serial.println("Wifi connected");

  IPAddress ip = WiFi.localIP();

  Serial.print("IP: ");
  Serial.println(ip);
  
  int bg1[10]={0,0,0,0,0,0,0,0,1,1};
  bargraph(bg1);
  connectMQTT();
  int bg2[10]={0,0,0,0,0,0,0,1,1,1};
  bargraph(bg2);
  updateNTP();
  int bg3[10]={0,0,0,0,0,0,1,1,1,1};
  bargraph(bg3);
  resetScreen();
  int bg4[10]={0,0,0,0,0,1,1,1,1,1};
  bargraph(bg4);
  mqttClient.onMessage(ReadMQTT);
  int bg5[10]={0,0,0,0,0,0,0,0,0,0};
  bargraph(bg5);
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
    Serial.println("RTC sync");
  } else {
    lcd.setCursor(0,1);
    lcd.print("RTC sync fail");
    Serial.println("RTC sync fail");
  }
  delay(1000);
  
}

void connectMQTT(){
  // Connexion MQTT
  lcd.clear();
  lcd.setCursor(0,01);
  lcd.print("Connexion MQTT...");
  Serial.print("Connexion MQTT...");
  mqttClient.setId("ido_client_"+ID_Sensor);
  mqttClient.setUsernamePassword(mqttUser, mqttPassword);
  if (!mqttClient.connect(broker, port)) {
    Serial.print("Echec : ");
    Serial.println(mqttClient.connectError());
    while (1);
  }
  Serial.println("MQTT OK");
  mqttClient.subscribe("/iot/COMMAND_42900");
  mqttClient.subscribe("/iot/BARGRAPH_42900");
  mqttClient.subscribe("/iot/BLINK_42900");
  delay(1000);

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

void bargraph(int data[10]){
  for(int i=0;i<=LastBargraphPin-FirstBargraphPin;i++){
    if(data[i]){
      digitalWrite(i+FirstBargraphPin , HIGH);
    }else{
       digitalWrite(i+FirstBargraphPin , LOW);
    }
  }

}

void bargraph2(int nombre){
  int bin[10];
  for(int i=0;i<10;i++){
    bin[9-i]=(nombre>>(9-i))&1;
  }
  bargraph(bin);
}


void ReadMQTT(int messageSize){
  //Serial.println(messageSize);
  if (messageSize) {
    String res="";
    String topic=mqttClient.messageTopic();
    Serial.print("Message recu sur ");
    Serial.print(topic);
    Serial.print(" : ");
    while (mqttClient.available()) {
      res=res+(char)mqttClient.read();
    }
    Serial.print(res);
    if(topic=="/iot/COMMAND_42900"){
      switch(res.toInt()){
        case 10:
          updateNTP();
          resetScreen();
          break;
        case 20:
          measure=true;
          break;
        case 30:
          measure=false;
          break;
        case 40:
          blink_time=2000;
          break;
        case 50:
          blink_time=250;
          break;
        case 60:
          if(blink_time_tmp!=0){
            blink_time=blink_time_tmp;
            life_time=millis()+blink_time;
          }
          break;
        default:
          Serial.println("Commande inconnue : " + res);
          break;
      }
    }else if(topic=="/iot/BARGRAPH_42900"){
      bargraph2(res.toInt());
    }else if(topic=="/iot/BLINK_42900"){
      if(res.toInt()!=0){
        blink_time_tmp=res.toInt()/2;
      }
    }

    
    
  }
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  dht.begin();
  rtc.begin(DateTime(F(__DATE__), F(__TIME__)));
  // initialize the lcd 
  lcd.begin(16, 2);

  //initialisation des pins
  pinMode(LED_LIFE, OUTPUT);
  for(int i = FirstBargraphPin;i <= LastBargraphPin;i++){
    pinMode(i,OUTPUT);
  }
  //initialisations
  int bg[10]={0,0,0,0,0,0,0,0,0,1};
  bargraph(bg);

  InitializeWifi();

  life_time=millis();
  read_time=millis();
  sec_time=millis();
}

void loop() {
  mqttClient.poll();
  // put your main code here, to run repeatedly:
  unsigned long time=millis();
  if(time>life_time){
    life_time=life_time+blink_time;
    digitalWrite(LED_LIFE, !digitalRead(LED_LIFE));
  }
  if(time>read_time){
    read_time=read_time+2000;
    if(measure){
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

      if (mqttClient.connected()) {
        mqttClient.beginMessage("/iot/TEMPERATURE_42900");
        mqttClient.print(t, 1);
        mqttClient.endMessage();

        mqttClient.beginMessage("/iot/HUMIDITY_42900");
        mqttClient.print(h, 1);
        mqttClient.endMessage();

        DateTime now = rtc.now();
        String date= String(now.day()) + "/" +
                String(now.month()) + "/" +
                String(now.year() % 100) + " " +
                String(now.hour()) + ":" +
                String(now.minute()) + ":" +
                String(now.second());
        mqttClient.beginMessage("/iot/GET_DATE_42900");
        mqttClient.print(date);
        mqttClient.endMessage();

        mqttClient.beginMessage("/iot/VERSION_42900");
        mqttClient.print(Version);
        mqttClient.endMessage();
      }
    }

    //réinitialisation de l'écran pour afficher la temperature et l'humidité
    /*DateTime now = rtc.now();
    Serial.println(
              String(now.day()) + "/" +
              String(now.month()) + "/" +
              String(now.year() % 100) + " " +
              String(now.hour()) + ":" +
              String(now.minute()) + ":" +
              String(now.second())
            );
    Serial.print("Temperature : ");
    Serial.print(t, 1);
    Serial.print(" oC | Humidite : ");
    Serial.print(h, 1);
    Serial.println(" %\r\n");*/
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
