import paho.mqtt.client as PahoMQTT
import json
import time
import random

class brightness_sensor():
    
    def __init__(self, clientID, broker, port, pub_topic):
        '''
        Create an MQTT client that connects to a broker and register 
        its self as a device and as a service to a catalog via given topics.
        All the published message are in JSON format 
        '''
        self.broker=broker
        self.port=port
        self.clientID=clientID
        self.pub_topic=pub_topic
        self._paho_mqtt = PahoMQTT.Client(clientID, False)
        self._paho_mqtt.connect(self.broker, self.port)
        self._paho_mqtt.loop_start()
        print("Successfully connected to the broker")
        
        
    def brightness_read(self):
        '''
        Read the brightness in lux (random number), encode in JSON format following the
        SenML standards and publish it on the topic
        '''
        b = random.randint(20, 800)
        diz={"bn":self.clientID, "e":[{"t":time.time(), "n":"brightness", "u":"lux", "v":b}]}
        msg=json.dumps(diz)
        self._paho_mqtt.publish(self.pub_topic, msg, 2)
        print("Brightness sent")
        
if __name__ == "__main__":
    b = brightness_sensor("bright_01", "mqtt.eclipse.org", 1883, "/tiot/16/GET/brightness")
    while True:
        diz={"id":"bright_01", "endpoint":["/tiot/16/GET/brightness"], "resource": "brightness"}
        msg=json.dumps(diz)
        b._paho_mqtt.publish("/tiot/16/PUT/newdevice", msg, 2)
        print("Successfully registered on the catalog")
        b.brightness_read()
        time.sleep(60)
