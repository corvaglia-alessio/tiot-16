import paho.mqtt.client as PahoMQTT
import json
import time
import random

class brightness_sensor():
    
    def __init__(self, clientID, endpoints, broker, port, pub_topic, catalog_topic_reg_device, catalog_topic_reg_service):
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
        diz={"id":clientID, "endpoint":endpoints, "resource": "brightness"}
        msg=json.dumps(diz)
        self._paho_mqtt.publish(catalog_topic_reg_device, msg, 2)
        self._paho_mqtt.publish(catalog_topic_reg_service, msg, 2)
        print("Successfully registered on the catalog")
        
    def brightness_read(self):
        '''
        Read the brightness in lux (randon number), encode in JSON format following the
        SenML standards and publish it on the topic
        '''
        b = random.randint(20, 800)
        diz={"bn":self.clientID, "e":{"t":time.time(), "n":"brightness", "u":"lux", "v":b}}
        msg=json.dumps(diz)
        self._paho_mqtt.publish(self.pub_topic, msg, 2)
        print("Brigthness sent")
        
if __name__ == "__main__":
    b = brightness_sensor("bright_01", ["/tiot/16/GET/brightness"], "mqtt.eclipse.org", 1883, "/tiot/16/GET/brightness", "/tiot/16/PUT/newdevice", "/tiot/16/PUT/newservice")
    while True:
        b.brightness_read()
        time.sleep(60)
