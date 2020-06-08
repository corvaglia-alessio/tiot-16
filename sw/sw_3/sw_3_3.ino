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
  mqtt.subscribe("/tiot/16/led", changeLedValue);
}

void loop() {
  
  mqtt.monitor();
  String jsondisp = encode_disp();
  mqtt.publish("/tiot/16/PUT/newdevice",jsondisp);
  delay(2*MSEC);
  }

String encode_disp(){
  doc_snd2.clear();
  doc_snd2["id"] = "Yùn - Gruppo 16";
  doc_snd2["endpoint"]=["/tiot/16/led"];
  doc_snd2["resource"]="Led";
  String out;
  serializeJson(doc_snd2, out);
  return out;
}
//"{"bn": "Yun", "e": [{  "n" : "led","t": null, "v" : 1, "u":null}]}"

void changeLedValue(const String& topic, const String& subtopic, const String& message){
  DeserializationError e = deserializeJson(doc_rcv, message);
  if(e){
    Serial.print("Deserializion failed with code");
    Serial.println(e.c_str());
  }
  else{
    if(doc_rcv["e"][0]["n"]=="led"){
      int statuss = (int) doc_rcv["e"][0]["v"];
      if(statuss == 0 || statuss == 1){
          digitalWrite(LED_PIN, statuss);
      }
      else{
        Serial.print("Error: status for led not valid");
      }
    }
  }
}
