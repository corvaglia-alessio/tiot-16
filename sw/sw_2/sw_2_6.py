import os
import sys
import json
import time 
from MyMQTT import MyMQTT

class IoTDevice():
    
    def __init__(self, broker, port, clientID, endpoint, resources):
        self.broker = broker
        self.port = port
        self.clientID = clientID
        self.endpoint = endpoint
        self.resources = resources
        self.myMqttClient = MyMQTT(self.clientID, self.broker, self.port, self)
        self.myMqttClient.start()
        
    def loop(self):
        data = {"id":self.clientID,"endpoint":self.endpoint,"resource":self.resources}
        while True:
            self.myMqttClient.myPublish("/tiot/16/PUT/newdevice", json.dumps(data))
            time.sleep(60)
            
if __name__ == "__main__":
    d = IoTDevice("mqtt.eclipse.org", 1883, "device-tiot-16", ["GET", "PUT"], "temperature")
    d.loop()
            