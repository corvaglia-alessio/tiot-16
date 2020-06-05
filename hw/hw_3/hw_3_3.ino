#include <ArduinoJson.h>
#include <MQTTclient.h>
#include <Bridge.h>

#define LED_PIN 11
#define TEMP_PIN A1
#define LED_INT_PIN 13
#define K 273.15
#define B 4275
#define R0 100000
#define VCC 1023
#define T0 298.15
#define R(vsig) ((VCC/vsig)-1)*R0
#define T(r) 1/((log(r/R0)/B)+(1/T0))

#define DELAY 10
#define MSEC 1e03

const int cap = JSON_OBJECT_SIZE(2)+JSON_ARRAY_SIZE(1)+JSON_OBJECT_SIZE(4)+40;
DynamicJsonDocument doc_snd(cap);
DynamicJsonDocument doc_rcv(cap);

void setup() {
  Serial.begin(9600);
  while(!Serial);
  Serial.println("LAB HW PARTE 3, gruppo: Manco Marco, Manco Davide, Corvaglia Alessio");
  
  pinMode(LED_PIN, OUTPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_INT_PIN, OUTPUT);

  digitalWrite(LED_INT_PIN, 0);
  Bridge.begin();
  digitalWrite(LED_INT_PIN, 1);

  mqtt.begin("test.mosquitto.org", 1883);
  mqtt.subscribe("tiot/16/led", changeLedValue);
}

void loop() {
  mqtt.monitor();
  double temp = temp_read();
  String data = encode_sen_ml("temperature", temp, "°C");
  mqtt.publish("tiot/16/temperature", data);
  delay(DELAY*MSEC);
}

void changeLedValue(const String& topic, const String& subtopic, const String& message){
  DeserializationError e = deserializeJson(doc_rcv, message);
  if(e){
    Serial.print("Deserializion failed with code");
    Serial.println(e.c_str());
  }
  else{
    if(doc_rcv["e"][0]["n"]=="led"){
      int status = (int) doc_rcv["e"][0]["v"];
      if(status == 0 || status == 1){
          digitalWrite(LED_PIN, status);
      }
      else{
        Serial.print("Error: status for led not valid");
      }
    }
  }
}

double temp_read(){
  double reading = (double) analogRead(TEMP_PIN);
  double r = R(reading);
  double t = T(r) - K;
  return t;
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
