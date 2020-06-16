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

        self.modificati_led = False
        self.modificati_ventola = False
        self.modificati_led_val = False
        self.modificati_ventola_val = False

        self.temp_ventola_min = self.TEMP_VENTOLA_MIN_A; 
        self.temp_ventola_max = self.TEMP_VENTOLA_MAX_A; 

        self.temp_led_min = self.TEMP_LED_MIN_A; 
        self.temp_led_max = self.TEMP_LED_MAX_A; 

        self.values_arduino_yun = list()
        self.ardu = False
        self.cont_t = 0

        response = requests.get('http://127.0.0.1:9090/messagebroker')
        txt = json.loads(response.text)
        self.broker = txt["domain"]
        self.port = txt["port"]

        self.people_val = 0
        self.temp = None
        self.tr = False

        self.myMqttClient = MyMQTT(id_, self.broker, self.port, self)
        self.myMqttClient.start()
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices/+/response")
        self.myMqttClient.mySubscribe("/tiot/16/service/range/led/#")
        self.myMqttClient.mySubscribe("/tiot/16/service/range/ventola/#")
        self.myMqttClient.mySubscribe("/tiot/16/service/val/ventola/+")
        self.myMqttClient.mySubscribe("/tiot/16/service/val/led/+")
        self.info_device(id_="Yun_16")

    
    def info_device(self, id_):
        while not(self.ardu):
            self.myMqttClient.myPublish(f"/tiot/16/GET/devices/{id_}")
            time.sleep(2)

    def notify(self, topic, msg):

        topic_list = topic.split("/")
        len_ = len(topic_list)
        type_ = ""

        if len_ > 4:
            type_ = topic_list[4]
            if type_ != "range":
                json_msg = json.loads(msg)

        if type_ == "devices" and not(self.tr):
            self.endpoint_yun = json_msg["endpoint"]
            self.tr = True
            for e in self.endpoint_yun:
                self.myMqttClient.mySubscribe(e)

            self.ardu = True
        
        if type_ == "temp":
            self.temperatura(json_msg)
        
        if type_ == "people":
            self.people(json_msg)

        if type_ == "val":
            elemento = topic_list[5]
            print("VALLLLLLL")
            if elemento == "led":
                self.modificati_led_val = True
                self.led_state = float(topic_list[6])
                self.invia_led()
            else:
                self.modificati_ventola_val = True
                self.ventola_state = float(topic_list[6])
                self.invia_ventola()

        if type_ == "range":
            elemento = topic_list[5]
            estremo = topic_list[6]
            valore = topic_list[7]

            if elemento == "led":
                self.modificati_led = True

                if estremo == "min":
                    self.temp_led_min = float(valore)
                else:
                    self.temp_led_max = float(valore)
            
            else:
                self.modificati_ventola = True

                if estremo == "min":
                    self.temp_ventola_min = float(valore)
                else:
                    self.temp_ventola_max = float(valore)

    def temperatura(self, json_temp):

        try:
            self.temp = float(json_temp["e"][0]["v"])
        except:
            print("errore fun temperatura")
            return
        self.cont_t -= -1
        self.regola_valori()
        if not(self.modificati_ventola_val):
            self.regola_ventola(self.temp)
        if not(self.modificati_led_val):
            self.regola_led(self.temp)

        if self.cont_t == 1:
            f_s = f"T:{self.temp} Pres:{self.people_val}"
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

        if self.people_val == 1:
            if self.modificati_ventola == False:
                self.temp_ventola_min = self.TEMP_VENTOLA_MIN_P
                self.temp_ventola_max = self.TEMP_VENTOLA_MAX_P

            if self.modificati_led == False:
                self.temp_led_min = self.TEMP_LED_MIN_P
                self.temp_led_max = self.TEMP_LED_MAX_P
        else:
            if self.modificati_ventola == False:
                self.temp_ventola_min = self.TEMP_VENTOLA_MIN_A
                self.temp_ventola_max = self.TEMP_VENTOLA_MAX_A

            if self.modificati_led == False:
                self.temp_led_min = self.TEMP_LED_MIN_A
                self.temp_led_max = self.TEMP_LED_MAX_A


    def regola_ventola(self, temp):

        if temp > self.temp_ventola_max:
            temp = self.temp_ventola_max

        if temp < self.temp_ventola_min:
            temp = self.temp_ventola_min;

        self.ventola_state = Service.map(temp, self.temp_ventola_max, self.temp_ventola_min)
        self.invia_ventola()

    def invia_ventola(self):
        json_state = {"bn":f"{self.id_}", "e":[{"n":"ventola", "t":time.time(), "v":self.ventola_state, "u":"%"}]}
        self.myMqttClient.myPublish("/tiot/16/yun/ventola", json.dumps(json_state))

    def regola_led(self, temp):
        if temp > self.temp_led_max:
            temp = self.temp_led_max

        if temp < self.temp_led_min:
            temp = self.temp_led_min

        self.led_state = 100 - Service.map(temp, self.temp_led_max, self.temp_led_min)
        self.invia_led()

    def invia_led(self):
        json_state = {"bn":f"{self.id_}", "e":[{"n":"led", "t":time.time(), "v":self.led_state, "u":"%"}]}
        self.myMqttClient.myPublish("/tiot/16/yun/led", json.dumps(json_state))

    def people(self, json_people):
        try:
            self.people_val = json_people["e"][0]["v"]
        except:
            print("errore fun people")
            return

    @staticmethod
    def map(val, max, min):
        return ((val - min)/(max-min))*100


if __name__ == "__main__":
    id_ = "Service_temperature"
    description = "Service MQTT"
    endpoint = ["/tiot/16/service/range/led/#", "/tiot/16/service/range/ventola/#", "/tiot/16/service/val/ventola/+", "/tiot/16/service/val/led/+"]


    service = Service(id_=id_)
    broker = service.broker
    port = service.port
    #service.info_device(id_="Yun_16")

    loop_request = Loop(1*60, id_=id_+"_loop", description=description, endpoint=endpoint, broker=broker, port=port)
    loop_request.start()