#include <math.h>
#include <LiquidCrystal_PCF8574.h>
#include <MQTTclient.h>
#include <ArduinoJson.h>
#include <Bridge.h>

#define MIN 6e04
#define MSEC 1e03

#define K 273.15
#define B 4275
#define R0 100000
#define VCC 1023
#define T0 298.15

#define PERIOD 60

#define N_NOISE 10
#define RANGE_TIME_NOISE 5

#define TIME_PEOPLE_PIR 10
#define TIME_PEOPLE_NOISE 15

#define TEMP_PIN A1
#define LED_PIN_2 11
#define LED_PIN 10
#define VENTOLA_PIN 9
#define PIR_PIN 7
#define NOISE_PIN 4
#define LED_INT_PIN 13

#define R(vsig) ((VCC/vsig) - 1)*R0
#define T(r) 1/((log(r/R0)/B) + (1/T0))

LiquidCrystal_PCF8574 lcd(0x27);

double led_state = 0.0;
double ventola_state = 0.0; 

int cont_people_pir = 0;
unsigned long time_cont_people_pir = 0;

int cont_people_noise = 0;
unsigned long time_cont_people_noise[N_NOISE] = {0};

int last_noise = 0;
int index_noise = 0;

const int cap = JSON_OBJECT_SIZE(2)+JSON_ARRAY_SIZE(1)+JSON_OBJECT_SIZE(4)+40;
DynamicJsonDocument doc_snd(cap);
DynamicJsonDocument doc_rcv(cap);

void setup()
{
    // Set serial
    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB SW 3_4\nSmart home controller online\nManco Davide\nCorvaglia Alessio\nManco Marco");

     // Set dei pin
    pinMode(TEMP_PIN, INPUT);
    pinMode(PIR_PIN, INPUT);
    pinMode(NOISE_PIN, INPUT);
    pinMode(VENTOLA_PIN, OUTPUT);
    pinMode(LED_INT_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);

    //impostazione del bridge
    digitalWrite(LED_INT_PIN, LOW);
    Bridge.begin();
    digitalWrite(LED_INT_PIN, HIGH);

    // LCD
    lcd.begin(16, 2);
    lcd.setBacklight(255);
    lcd.home();
    lcd.clear();
    
    // VENTOLA
    analogWrite(VENTOLA_PIN, ventola_state);
    Serial.println("Ventola Attivata");
    
    // LED
    analogWrite(LED_PIN, led_state);
    Serial.println("LED Attivato");

    // PIR
    attachInterrupt(digitalPinToInterrupt(PIR_PIN), people_in_room_pir, CHANGE);

    //sottoscrizione ai topic attuazione
    mqtt.begin("mqtt.eclipse.org", 1883);
    mqtt.subscribe("/tiot/16/yun/led", regola_led);
    mqtt.subscribe("/tiot/16/yun/disp", stampa_on_lcd);
    mqtt.subscribe("/tiot/16/yun/ventola", regola_ventola);
}

void loop()
{
    if(digitalRead(NOISE_PIN)==LOW)
    {
        people_in_room_noise();
    }

    //registrazione al catalog
    registra_catalog();
    
    controllo_people_in_room_pir();
    controllo_people_in_room_noise();

    //invio propri dati
    people();
    misura_temperatura();
    
    delay(PERIOD*MSEC);
}

void people()
{
  String msg;
  if(cont_people_pir == 0 && cont_people_noise == 0){
    msg = encode_sen_ml("people",0,"");
  }
  else{
    msg=encode_sen_ml("people",1,"");
  }
  mqtt.publish("tiot/16/yun/people", msg);
}

void registra_catalog()
{
  doc_snd.clear();
  doc_snd["id"]="Yun_16";
  doc_snd["endpoint"][0]="/tiot/16/yun/temp";
  doc_snd["endpoint"][1]="/tiot/16/yun/people";
  doc_snd["endpoint"][2]="/tiot/16/yun/ventola";
  doc_snd["endpoint"][3]="/tiot/16/yun/led";
  doc_snd["endpoint"][4]="/tiot/16/yun/disp";
  doc_snd["resource"][0]="temperature";
  doc_snd["resource"][1]="people";
  doc_snd["resource"][2]="ventola";
  doc_snd["resource"][3]="led";
  doc_snd["resource"][4]="disp";
  String out;
  serializeJson(doc_snd, out);
  mqtt.publish("/tiot/16/PUT/newdevice", out);
}

double misura_temperatura()
{
    double val_temp =(double) analogRead(TEMP_PIN);
    double r = R(val_temp);
    double t = T(r) - K;
    String msg = encode_sen_ml("temperature", t, "°C");
    mqtt.publish("/tiot/16/yun/temp", msg);
}

String encode_sen_ml(String sensor, double value, String unit){
  doc_snd.clear();
  doc_snd["bn"] = "Yùn - Gruppo 16";
  
  doc_snd["e"][0]["n"] = sensor;
  doc_snd["e"][0]["t"] = millis();
  doc_snd["e"][0]["v"] = value;
  
  if(unit != ""){
    doc_snd["e"][0]["u"]=unit;
  }
  else{
    doc_snd["e"][0]["u"]=(char*)NULL;
  }
  
  String out;
  serializeJson(doc_snd, out);
  return out;
}

void regola_ventola(const String& topic, const String& subtopic, const String& message)
{
  DeserializationError e = deserializeJson(doc_rcv, message);
  if(e){
    Serial.print("Deserializion failed with code");
    Serial.println(e.c_str());
  }
  else{
    if(doc_rcv["e"][0]["n"]=="ventola"){
      float statuss = (float) doc_rcv["e"][0]["v"];
      float val = (statuss*255)/100;
      if(val > 0 && val <256){
        analogWrite(VENTOLA_PIN, val);
        Serial.print("Ventola regolata");
        Serial.println(val);
      }
    else{
        Serial.println("Error: status for ventola not valid");
      }
    }
  } 
}

void regola_led(const String& topic, const String& subtopic, const String& message)
{
  DeserializationError e = deserializeJson(doc_rcv, message);
  if(e){
    Serial.print("Deserializion failed with code");
    Serial.println(e.c_str());
  }
  else{
    if(doc_rcv["e"][0]["n"]=="led"){
      float statuss = (float) doc_rcv["e"][0]["v"];
      float val = (statuss*255)/100;
      if(val > 0 && val <256){
        analogWrite(LED_PIN, val);
        Serial.print("Riscaldatore regolato");
        Serial.println(val);
      }
    else{
        Serial.println("Error: status for led not valid");
      }
    }
  } 
}

void people_in_room_pir()
{
    time_cont_people_pir = millis();
    cont_people_pir = 1;
}

void controllo_people_in_room_pir()
{
    unsigned long current_time = millis() - time_cont_people_pir;
    if(cont_people_pir != 0 && current_time >= TIME_PEOPLE_PIR*MIN)
    {
        cont_people_pir = 0;
    }
}

void people_in_room_noise()
{   
    int n_rumori;

    remove_old_val();

    //Serial.println("Rilevato rumore");

    index_noise = index_noise % N_NOISE;
    time_cont_people_noise[index_noise] = millis();

    index_noise++;

    n_rumori = (last_noise>index_noise)? \
                (N_NOISE-last_noise)+index_noise: \
                index_noise-last_noise;

    if(n_rumori == N_NOISE)
    {
        cont_people_noise = 1;
        time_cont_people_noise[0] = time_cont_people_noise[index_noise-1];
        index_noise = 1;
        last_noise = 0;
    }
}

void controllo_people_in_room_noise()
{
    unsigned long current_time = millis() - time_cont_people_noise[index_noise-1];
    if(cont_people_noise != 0 && current_time >= TIME_PEOPLE_NOISE*MIN)
    {
        cont_people_noise = 0;
    }
}

void remove_old_val()
{
    unsigned long current_time = millis();
    
    while (1)
    {
        if(last_noise != index_noise)
        {
            last_noise = last_noise%N_NOISE;
            
            if(current_time - time_cont_people_noise[last_noise] >= RANGE_TIME_NOISE*MIN)
            {
                time_cont_people_noise[last_noise] = 0;
                last_noise++;
            }
            else
                break;  
        }
        else
            break; 
    }
}

void stampa_on_lcd(const String& topic, const String& subtopic, const String& message)
{
  DeserializationError e = deserializeJson(doc_rcv, message);
  if(e){
    Serial.print("Deserializion failed with code");
    Serial.println(e.c_str());
  }
  else{
    String first_line=doc_rcv["riga-1"];
    String second_line=doc_rcv["riga-2"];
    lcd.home();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(first_line);
    lcd.setCursor(0, 1);
    lcd.print(second_line);
  }
}
