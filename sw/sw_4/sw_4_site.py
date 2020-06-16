import cherrypy as cp
import os, sys
import paho.mqtt.client as pmqtt
import threading
from MyMQTT import MyMQTT
import time
import requests
import json

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

class Site():

    exposed = True

    def __init__(self, ClientID):
        
        with open("index.html", "r") as f:
            self.index_html = f.read()

        self.led = None
        self.ventola = None
        self.stufa = None

        response = requests.get('http://127.0.0.1:9090/messagebroker')
        txt = json.loads(response.text)
        self.broker = txt["domain"]
        self.port = txt["port"]
        self.id_ = ClientID

        self.serv = False
        self.topic_led = None
        self.topic_ventola = None
        self.topic_luce = None

        self.myMqttClient = MyMQTT(id_, self.broker, self.port, self)
        self.myMqttClient.start()
        self.myMqttClient.mySubscribe("/tiot/16/GET/services/+/response")
        self.info_service(id_="Service_temperature_loop")
        self.serv = False
        self.info_service(id_="Service_led_loop")

    def notify(self, topic, msg):

        topic_list = topic.split("/")
        len_ = len(topic_list)
        type_ = ""

        if len_ > 4:
            type_ = topic_list[4]
            if type_ != "range":
                json_msg = json.loads(msg)

        if type_ == "services":
            self.endpoint = json_msg["endpoint"]
        
            for e in self.endpoint:
                type_e = e.split("/")
                e = e[0:len(e)-2]
                if type_e[5] == "led":
                    self.topic_led = e
                if type_e[5] == "ventola":
                    self.topic_ventola = e
                if type_e[5] == "luce":
                    self.topic_luce = e
            print(self.topic_led, self.topic_luce, self.topic_ventola)
            self.serv = True

    def info_service(self, id_):
        #while not(self.serv):
        self.myMqttClient.myPublish(f"/tiot/16/GET/services/{id_}")
        time.sleep(4)

    def GET(self, *uri, **param):

        if len(uri) == 0:
            return self.index_html

        if uri[0] == "luce":
            self.luce = param.get("subject")

            if self.luce == "on":
                self.myMqttClient.myPublish(f"{self.topic_luce}/1")
            else: # off
                self.myMqttClient.myPublish(f"{self.topic_luce}/0")
            
            return self.index_html

        if uri[0] == "ventola":
            self.ventola = param.get("vol")
            self.myMqttClient.myPublish(f"{self.topic_ventola}/{self.ventola}")
            return self.index_html

        if uri[0] == "led":
            self.led = param.get("vol")
            self.myMqttClient.myPublish(f"{self.topic_led}/{self.led}")
            return self.index_html

        cp.HTTPError(404, "Page not found")


if __name__ == "__main__":
    conf = {
                "/" :   {
                            "request.dispatch": cp.dispatch.MethodDispatcher(),
                            "tools.staticdir.root":os.path.abspath(os.getcwd())
                        },
                "/img": {
                            "tools.staticdir.on": True,
                            "tools.staticdir.dir": "./img"
                        },
                "/css": {
                            "tools.staticdir.on": True,
                            "tools.staticdir.dir": "./css"
                        }
            }
    id_ = "Service_site"
    description = "Service site"
    endpoint = ["GET /"]

    site = Site(id_)
    broker = site.broker
    port = site.port
    cp.tree.mount(site, "/", conf)

    cp.config.update({'server.socket_port': 9070})

    loop_request = Loop(1*60, id_=id_+"_loop", description=description, endpoint=endpoint, broker=broker, port=port)
    loop_request.start()

    cp.engine.start()
    cp.engine.block()
