import cherrypy as cp 
import os
import sys
import json
import time 
import threading
import requests
from MyMQTT import MyMQTT

url = 'http://127.0.0.1:9090/newservice'
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
        """
        while True:
            response = requests.put(url, data=json.dumps(self.request_json))
            print(response.status_code)
            time.sleep(self.time)
        """



class Service():
    exposed = True
    
    def __init__(self):
        self.values_arduino_yun = list()

    def GET(self, *uri, **params):
        """ Metodo GET
            Restituisce la lista di valori rilevati dall' Arduino Yun
        """

        if uri[0] == 'log':
            return f"{self.values_arduino_yun}"
        else:
            cp.HTTPError(404, "Risorsa not found!")

    def POST(self, *uri, **params):
        """ Metodo POST
            salva i valori rilevati dall' Arduino Yun
        """
        
        if uri[0] == 'log':
            self.values_arduino_yun.append(cp.request.body.read())
        else:
            cp.HTTPError(404, "Risorsa not found!")
        

if __name__ == "__main__":
    conf =  {
                '/':    {
                            'request.dispatch': cp.dispatch.MethodDispatcher()
                        }
            }

    id_ = "gp16"
    description = "Service riceve nel body della POST le informazioni dei vari devices e restituisce i valori salvati tramite request GET"
    endpoint = ["GET https://127.0.0.1:9010/log", "POST https://127.0.0.1:9010/log"]


    service = Service()

    loop_request = Loop(1*60, id_=id_, description=description, endpoint=endpoint)
    loop_request.start()

    cp.tree.mount(service, '/', conf)
    cp.config.update({'server.socket_port':9010})
    cp.engine.start()
    cp.engine.block()
