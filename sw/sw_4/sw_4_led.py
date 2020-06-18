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
        self.values_arduino_yun = list()

        response = requests.get('http://127.0.0.1:9090/messagebroker')
        txt = json.loads(response.text)
        print(txt)
        self.broker = txt["domain"]
        self.port = txt["port"]

        

        self.myMqttClient = MyMQTT(id_, self.broker, self.port, self)
        self.myMqttClient.start()
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices/+/response")
        self.myMqttClient.mySubscribe("/tiot/16/service/val/luce/+")
        self.info_device("Yun_16")
        self.info_device("bright_01")

    
    def info_device(self, id_):
        
        self.myMqttClient.myPublish(f"/tiot/16/GET/devices/{id_}")
            

    def notify(self, topic, msg):

        topic_list = topic.split("/")
        len_ = len(topic_list)
        type_ = ""

        if len_ > 4:
            type_ = topic_list[4]


        if type_ == "devices":
            jsonb=json.loads(msg)
            if jsonb["id"] == "bright_01":
                self.myMqttClient.mySubscribe(jsonb["endpoint"][0])
            else:
                self.topic_luce = json.loads(msg)["endpoint"][0]

        if type_ == "luce":
            dati = { 'bn': 'Yun', 'e': [ { 'n' : 'led','t': None, 'v' : int(topic_list[5]), 'u':None} ] }         
            self.myMqttClient.myPublish(self.topic_luce,json.dumps(dati))
        if topic_list[4] == "brightness":
            valLuce=json.loads(msg)["e"][0]["v"];
            if valLuce<200:
                dati = { 'bn': 'Yun', 'e': [ { 'n' : 'led','t': None, 'v' : 1, 'u':None} ] }
                print("BBB")
                self.myMqttClient.myPublish("/tiot/16/yun/lampadina",json.dumps(dati))
            else:
                dati = { 'bn': 'Yun', 'e': [ { 'n' : 'led','t': None, 'v' : 0, 'u':None} ] }
                print("AAAAA")
                self.myMqttClient.myPublish("/tiot/16/yun/lampadina",json.dumps(dati))




if __name__ == "__main__":
    id_ = "Service_led"
    description = "Service MQTT"
    endpoint = ["/tiot/16/service/val/luce/+"]


    service = Service(id_=id_)
    broker = service.broker
    port = service.port
    print(broker, port)

    loop_request = Loop(1*60, id_=id_+"_loop", description=description, endpoint=endpoint, broker=broker, port=port)
    loop_request.start()