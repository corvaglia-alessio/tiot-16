import os
import sys
import json
import time 
import threading
import requests
from MyMQTT import MyMQTT

class Loop(threading.Thread):

    def __init__(self, time_, id_, description, endpoint, broker, port):
        threading.Thread.__init__(self)
        self.time_ = time_
        self.broker = broker
        self.port = port
        self.request_json = {
                                "id":id_,
                                "description":description,
                                "endpoint":endpoint
                            }

        self.myMqttClient = MyMQTT(id_, broker, port, self)
        self.myMqttClient.start()

    def run(self):
        while True:
            self.myMqttClient.myPublish("/tiot/16/PUT/newservice", (json.dumps(self.request_json)))
            time.sleep(self.time_)

class Service():
    exposed = True
    
    def __init__(self, id_):

        self.id_ = id_

        # Valori in presenza di persone nella stanza
        self.TEMP_VENTOLA_MIN_P =  25.0
        self.TEMP_VENTOLA_MAX_P = 30.0
        self.TEMP_LED_MIN_P = 15.0
        self.TEMP_LED_MAX_P = 20.0

        # Valori in assenza di persone nella stanza
        self.TEMP_VENTOLA_MIN_A = 27.0
        self.TEMP_VENTOLA_MAX_A = 32.0
        self.TEMP_LED_MIN_A = 17.0
        self.TEMP_LED_MAX_A = 22.0

        self.temp_ventola_min = self.TEMP_VENTOLA_MIN_A; 
        self.temp_ventola_max = self.TEMP_VENTOLA_MAX_A; 

        self.temp_led_min = self.TEMP_LED_MIN_A; 
        self.temp_led_max = self.TEMP_LED_MAX_A; 

        self.values_arduino_yun = list()
        self.cont_t = 0

        response = requests.get('http://127.0.0.1:9090/messagebroker')
        txt = json.loads(response.text)
        self.broker = txt["domain"]
        self.port = txt["port"]

        self.people = 0
        self.temperatura = None

        self.myMqttClient = MyMQTT(id_, self.broker, self.port, self)
        self.myMqttClient.start()
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices/+/response")

    
    def info_device(self, id_):
        self.myMqttClient.myPublish(f"/tiot/16/GET/devices/{id_}")

    def notify(self, topic, msg): ## Gestire piu' topic dello YUN
        len_ = len(topic.split("/"))
        type_ = ""

        if len_ > 4:
            type_ = topic.split("/")[4]
            json_msg = json.loads(msg)

        if type_ == "devices":
            self.endpoint_yun = json_msg["endpoint"]
        
            for e in self.endpoint_yun:
                self.myMqttClient.mySubscribe(e)
        
        if type_ == "temp":
            temperatura(self, json_msg)
        
        if type_ == "people":
            people(self, json_msg)

    def temperatura(self, json_temp):
        try:
            self.temp = float(json_temp["e"][0]["v"])
        except:
            print("errore fun temperatura")
            return
        self.cont_t -= -1
        self.regola_valori()
        self.regola_ventola(self.temp)
        self.regola_led(self.temp)

        if self.cont_t == 1:
            f_s = f"T:{self.temp} Pres:{self.people}"
            s_s = f"AC:{self.ventola_state}% HT:{self.led_state}"
            json_lcd = {"riga-1":f_s, "riga-2":s_s}
            self.myMqttClient.myPublish("/tiot/16/yun/disp", json.dumps(json_lcd))
        else:
            self.cont_t = 0
            f_s = f"AC m:{self.temp_ventola_min} M:{self.temp_ventola_max}"
            s_s = f"HT m:{self.temp_led_min} M:{self.temp_led_max}"
            json_lcd = {"riga-1":f_s, "riga-2":s_s}
            self.myMqttClient.myPublish("/tiot/16/yun/disp", json.dumps(json_lcd))


    def regola_valori(self):

        if self.people == 1:
            self.temp_ventola_min = self.TEMP_VENTOLA_MIN_P
            self.temp_ventola_max = self.TEMP_VENTOLA_MAX_P

            self.temp_led_min = self.TEMP_LED_MIN_P
            self.temp_led_max = self.TEMP_LED_MAX_P
        else:
            self.temp_ventola_min = self.TEMP_VENTOLA_MIN_A
            self.temp_ventola_max = self.TEMP_VENTOLA_MAX_A

            self.temp_led_min = self.TEMP_LED_MIN_A
            self.temp_led_max = self.TEMP_LED_MAX_A


    def regola_ventola(self, temp):

        if temp > self.temp_ventola_max:
            temp = self.temp_ventola_max

        if temp < self.temp_ventola_min:
            temp = self.temp_ventola_min;

        self.ventola_state = map(temp, self.temp_ventola_max, self.temp_ventola_min)
        json_state = {"bn":f"{self.id_}", "e":[{"n":"ventola", "t":time.time(), "v":self.ventola_state, "u":"%"}]}
        self.myMqttClient.myPublish("/tiot/16/yun/ventola", json.dumps(json_state))

    def regola_led(self, temp):
        if temp > self.temp_led_max:
            temp = self.temp_led_max

        if temp < self.temp_led_min:
            temp = self.temp_led_min

        self.led_state = 100 - map(temp, self.temp_led_max, self.temp_led_min)
        json_state = {"bn":f"{self.id_}", "e":[{"n":"led", "t":time.time(), "v":self.led_state, "u":"%"}]}
        self.myMqttClient.myPublish("/tiot/16/yun/led", json.dumps(json_state))

    def people(self, json_people):
        try:
            self.people = json_people["e"][0]["v"]
        except:
            print("errore fun people")
            return

    @staticmethod
    def map(val, max, min):
        return ((val - min)/(max-min))*100


if __name__ == "__main__":
    id_ = "gp16"
    description = "Service MQTT"
    endpoint = ["/tiot/16/service"]


    service = Service(id_=id_)
    broker = service.broker
    port = service.port
    print(broker, port)
    service.info_device(id_="Yun_16")

    loop_request = Loop(1*60, id_=id_+"service", description=description, endpoint=endpoint, broker=broker, port=port)
    loop_request.start()