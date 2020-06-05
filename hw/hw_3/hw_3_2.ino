#include <Bridge.h>
#include <ArduinoJson.h>
#include <Process.h>

#define TEMP_PIN A1
#define LED_INT_PIN 13
#define K 273.15
#define B 4275
#define R0 100000
#define VCC 1023
#define T0 298.15
#define R(vsig) ((VCC/vsig)-1)*R0
#define T(r) 1/((log(r/R0)/B)+(1/T0))
#define MSEC 1e03
#define DELAY 10

const int cap = JSON_OBJECT_SIZE(2)+JSON_ARRAY_SIZE(1)+JSON_OBJECT_SIZE(4)+40;
DynamicJsonDocument doc_snd(cap);

void setup() {
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_INT_PINT, OUTPUT);
  
  Serial.begin(9600);
  while(!Serial);
  Serial.println("LAB HW PARTE 3, gruppo: Manco Marco, Manco Davide, Corvaglia Alessio");
  
  digitalWrite(LED_INT_PIN, 0);
  Bridge.begin();
  digitalWrite(LED_INT_PIN, 1); 
}

void loop() {
  double temp = temp_read();
  String data = encode_sen_ml("temperature", temp, "°C");
  int returnCode = postRequest(data);
  if(returnCode != 0){
    Serial.println("Error:"+returnCode);
  }
  delay(DELAY*MSEC); 
}

int postRequest(String data){
  Process p;
  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("POST");
  p.addParameter("-d");
  p.addParameter(data);
  p.addParameter("http://172.20.10.2:9090/log");
  p.run();
  int value = p.exitValue();
  return value;
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
