import os
import sys
import json
import time 
import threading
import requests
from MyMQTT import MyMQTT

url = 'http://127.0.0.1:9090/messagebroker'
#"/tiot/16/PUT/newservice"    "mqtt.eclipse.org"

class Loop(threading.Thread):

    def __init__(self, time, id_, description, endpoint, broker, port):
        threading.Thread.__init__(self)
        self.time = time
        self.broker = broker
        self.port
        self.request_json = {
                                "id":id_,
                                "description":description,
                                "endpoint":endpoint
                            }

        self.myMqttClient = MyMQTT(id_, broker, port, self)
        self.myMqttClient.start()

    def run(self):
        self.myMqttClient.myPublish("/tiot/16/PUT/newservice", (json.dumps(self.request_json, indent=4)))
        time.sleep(self.time)

class Service():
    exposed = True
    
    def __init__(self, id_):
        """
        self.values_arduino_yun = list()
        """

        response = requests.get('http://127.0.0.1:9090/messagebroker')
        self.broker = response.text["domain"]
        self.port = response.text["port"]

        self.myMqttClient = MyMQTT(id_, self.broker, self.port, self)
        self.myMqttClient.start()
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices/+/response")

    
    def info_device(self, id_):
        self.myMqttClient.myPublish(f"/tiot/16/GET/devices/{id_}")

    def notify(self, topic, msg):
        type_ = topic.split("/")[4]

        if type_ == "devices":
            endpoint = msg["endpoint"][0]
            self.myMqttClient.mySubscribe(endpoint)
        elif topic.split("/")[3] == "temperature":
            print(msg)
        


if __name__ == "__main__":
    id_ = "gp16"
    description = "Service MQTT"
    endpoint = ["/tiot/16/service"]


    service = Service(id_=id_)
    broker = service.broker
    port = service.port
    service.info_device(id_="Yùn - Gruppo 16")

    loop_request = Loop(1*60, id_=id_, description=description, endpoint=endpoint, broker=broker, port=port)
    loop_request.start()