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
DynamicJsonDocument doc_snd2(cap);
DynamicJsonDocument doc_rcv(cap);

void setup() {
  Serial.begin(9600);
  while(!Serial);
  Serial.println("LAB HW PARTE 3, gruppo: Manco Marco, Manco Davide, Corvaglia Alessio");
  
  pinMode(LED_PIN, OUTPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_INT_PIN, OUTPUT);

  digitalWrite(LED_PIN, LOW);
  Bridge.begin();
  digitalWrite(LED_INT_PIN, HIGH);

  mqtt.begin("mqtt.eclipse.org", 1883);

}

void loop() {
  
  mqtt.monitor();
  double temp = temp_read();
  
  String data = encode_sen_ml("temperature", temp, "°C");
  Serial.println(data);
  mqtt.publish("/tiot/16/temperature", data);
  String jsondisp = encode_disp();
  mqtt.publish("/tiot/16/PUT/newdevice",jsondisp);
  delay(2*MSEC);
  }


double temp_read(){
  double reading = (double) analogRead(TEMP_PIN);
  double r = R(reading);
  double t = T(r) - K;
  return t;
}

String encode_disp(){
  doc_snd2.clear();
  doc_snd2["id"] = "Yùn - Gruppo 16";
  doc_snd2["endpoint"]="/tiot/16/temperature";
  doc_snd2["resource"]="Temperature";
  String out;
  serializeJson(doc_snd2, out);
  return out;
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
