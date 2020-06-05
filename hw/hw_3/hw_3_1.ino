#include <BridgeServer.h>
#include <BridgeClient.h>
#include <Bridge.h>
#include <ArduinoJson.h>

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

BridgeServer s;
const int cap = JSON_OBJECT_SIZE(2)+JSON_ARRAY_SIZE(1)+JSON_OBJECT_SIZE(4)+40;
DynamicJsonDocument doc_snd(cap);

void setup() {
  pinMode(LED_PIN, OUTPUT);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_INT_PIN, OUTPUT);
  digitalWrite(LED_INT_PIN, 0);
  Bridge.begin();
  digitalWrite(LED_INT_PIN, 1);
  s.listenOnLocalhost();
  s.begin();
}

void loop() {
  BridgeClient c = s.accept();
  if(c){
    process_req(c);
    c.stop();
  }
  delay(50);
  
}

void process_req(BridgeClient c){
  String command = c.readStringUntil('/');
  command.trim();
  
  if(command=="led"){
    int state = c.parseInt();
    if(state==0 || state==1){
      digitalWrite(LED_PIN, state);
      print_resp(c, 200, encode_sen_ml("led", state, ""));
    }
    else{
      print_resp(c, 400, ""); /*bad request, per il led solo 0 o 1*/
    }
  }
  else{
    if(command=="temperature"){
      double temp = temp_read();
      print_resp(c, 200, encode_sen_ml("temperature", temp, "°C"));
    }
    else{
      print_resp(c, 404, ""); /* not found */
    }
  }
}

double temp_read(){
  double reading = (double) analogRead(TEMP_PIN);
  double r = R(reading);
  double t = T(r) - K;
  return t;
}

void print_resp(BridgeClient c, int statusCode, String body){
  c.println("Status: "+String(statusCode));
  
  if(statusCode==200){
    c.println("Content-type: application/json; charset=utf-8");
    c.println();
    c.println(body);
  }
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
