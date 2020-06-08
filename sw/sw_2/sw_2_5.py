import cherrypy as cp 
import os
import sys
import json
import time 
import threading
from MyMQTT import MyMQTT

class Loop(threading.Thread):

    def __init__(self, time, obj):
        threading.Thread.__init__(self)
        self.time = time
        self.obj = obj

    def run(self):
        while True:
            self.obj.delete_old()
            time.sleep(self.time)

class Catalog():
    exposed = True
    file = "values.json"
    thread_lock = threading.Lock()
    
    def __init__(self, domain, ip="", port=""):
        self.messagebroker =   {
                                "domain":domain,
                                "ip":ip,
                                "port":port
                                }
        self.devices = list()
        self.users = list()
        self.services = list()

        self.leggi_values()

        self.clientID = "tiot-16"
        self.myMqttClient = MyMQTT(self.clientID, "mqtt.eclipse.org", 1883, self)
        self.run()
        self.myMqttClient.mySubscribe("/tiot/16/GET")
        self.myMqttClient.mySubscribe("/tiot/16/GET/messagebroker")
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices/+")
        self.myMqttClient.mySubscribe("/tiot/16/GET/users/+")
        self.myMqttClient.mySubscribe("/tiot/16/GET/services/+")
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices")
        self.myMqttClient.mySubscribe("/tiot/16/GET/devices")
        self.myMqttClient.mySubscribe("/tiot/16/PUT/newdevice")
        self.myMqttClient.mySubscribe("/tiot/16/PUT/newuser")
        self.myMqttClient.mySubscribe("/tiot/16/PUT/newservice")

    def run(self):
        print ("running Catalog MQTT %s" % (self.clientID))
        self.myMqttClient.start()

    def end(self):
        print ("ending %s" % (self.clientID))
        self.myMqttClient.stop()

    def notify(self, topic, msg):

        request_type = topic.split("/")[3]
        type_ = topic.split("/")[4]
        ot = len(topic.split("/"))
        id_ = topic.split("/")[5] if ot == 6 else ""

        if request_type == "GET":
            self.get_mqtt([ot, request_type, type_, id_], msg)
        else:
            self.put_mqtt([ot, request_type, type_, id_], msg)


    def get_mqtt(self, uri, params):

        if uri[0] == 4:
            
            self.myMqttClient.myPublish ("/tiot/16/GET/response", (""" <h1>LAB parte 2 software</h1>
                        <strong>Membri del gruppo:</strong>
                        <ul>
                            <li>Corvaglia Alessio</li>
                            <li>Manco Marco</li>
                            <li>Manco Davide</li>
                        </ul>
                    """))

        if uri[2] == "messagebroker":
            self.myMqttClient.myPublish ("/tiot/16/GET/messagebroker/response", (json.dumps(self.messagebroker, indent=4)))

        elif uri[2] == "devices":
            if uri[0] == 5:
                self.myMqttClient.myPublish ("/tiot/16/GET/devices/response", (json.dumps({"devices":self.devices}, indent=4)))
            else:
                device = Catalog.search_id(self.devices, uri[3])
                if device == None:
                    device = f"<h1>Nessun dispositivo trovato con l'id {uri[3]}</h1>"
                else:
                    device = json.dumps(device, indent=4)
                self.myMqttClient.myPublish (f"/tiot/16/GET/devices/{uri[3]}/response", (device))

        elif uri[2] == "users":
            if uri[0] == 5:
                self.myMqttClient.myPublish ("/tiot/16/GET/users/response", (json.dumps({"users":self.users}, indent=4)))
            else:
                user = Catalog.search_id(self.users, uri[3])
                if user == None:
                    user = f"<h1>Nessun utente trovato con l'id {uri[3]}</h1>"
                else:
                    user = json.dumps(user, indent=4)
                self.myMqttClient.myPublish (f"/tiot/16/GET/users/{uri[3]}/response", (user))
        
        elif uri[2] == "services":
            if uri[0] == 5:
                self.myMqttClient.myPublish ("/tiot/16/GET/services/response", (json.dumps({"services":self.services}, indent=4)))
            else:
                service= Catalog.search_id(self.services, uri[3])
                if service == None:
                    service = f"<h1>Nessun service trovato con l'id {uri[3]}</h1>"
                else:
                    service = json.dumps(service, indent=4)
                self.myMqttClient.myPublish (f"/tiot/16/GET/services/{uri[3]}/response", (service))
    
    def put_mqtt(self, uri, params):

        if uri[2] == "newdevice":
            body = json.loads(params.decode("utf-8"))
            body["timestamp"] = time.time()
            self.cerca_value(body, "device")

            self.salva_values()
                
        elif uri[2] == "newuser":
            body = json.loads(params.decode("utf-8"))
            self.cerca_value(body, "user")

            self.salva_values()

        elif uri[2] == "newservice":
            body = json.loads(params.decode("utf-8"))
            body["timestamp"] = time.time()
            self.cerca_value(body, "service")

            self.salva_values()

    def leggi_values(self):
        """
            Legge i valori salvati nel file
        """
        self.thread_lock.acquire()
        with open(self.file, "r") as f:
            diz = json.loads(f.read())
        
        self.devices = diz["devices"]
        self.users = diz["users"]
        self.services = diz["services"]

        self.thread_lock.release()

    def salva_values(self):
        """
            Scrive i valori su file
        """

        self.thread_lock.acquire()
        diz = {
                "users":self.users,
                "devices":self.devices,
                "services":self.services
              }
        
        with open(self.file, "w") as f:
            f.write(f"{json.dumps(diz)}")

        self.thread_lock.release()

    def cerca_value(self, value, type):

        id_val = value["id"]

        if type == "user":
            for e in self.users:
                if e["id"] == id_val:
                    break
            else:
                self.users.append(value)

        if type == "device":
            for n, e in enumerate(self.devices):
                if e["id"] == id_val:
                    self.devices[n]["timestamp"] = value["timestamp"]
                    break
            else:
                self.devices.append(value)

        if type == "service":
            for n, e in enumerate(self.services):
                if e["id"] == id_val:
                    self.services[n]["timestamp"] = value["timestamp"]
                    break
            else:
                self.services.append(value)

    @staticmethod
    def search_id(list_, id):
        """
            Metodo statico 
            restituisce l'elemento nella lista con un determinato id
        """
        for d in list_:
            if d["id"] == id:
                return d
        return None

    @staticmethod
    def get_min(tempo):
        """
            Prende in input time.time() e restituisce i minuti
        """

        return int(time.ctime(tempo).split()[3].split(":")[1])

    def delete_old(self):
        """
            Metodo che elimina gli elementi con timestamp maggiore di un det valore
        """
        time_ = time.time()
        if len(self.devices) > 0:
            for n, e in enumerate(self.devices):
                if Catalog.get_min(time_) - Catalog.get_min(e.get("timestamp")) >= 2:
                    self.devices.pop(n)
        if len(self.services) > 0:           
            for n, e in enumerate(self.services):
                if Catalog.get_min(time_) - Catalog.get_min(e.get("timestamp")) >= 2:
                    self.services.pop(n)
        self.salva_values()
                

    def GET(self, *uri, **params):
        """ Metodo GET
            
        """

        if len(uri) == 0:
            return  """ <h1>LAB parte 2 software</h1>
                        <strong>Membri del gruppo:</strong>
                        <ul>
                            <li>Corvaglia Alessio</li>
                            <li>Manco Marco</li>
                            <li>Manco Davide</li>
                        </ul>
                    """

        if uri[0] == "messagebroker":
            return json.dumps(self.messagebroker, indent=4)

        elif uri[0] == "devices":
            if len(uri) == 1:
                return json.dumps({"devices":self.devices}, indent=4)
            else:
                device = Catalog.search_id(self.devices, uri[1])
                if device == None:
                    device = f"<h1>Nessun dispositivo trovato con l'id {uri[1]}</h1>"
                else:
                    device = json.dumps(device, indent=4)
                return device

        elif uri[0] == "users":
            if len(uri) == 1:
                return json.dumps({"users":self.users}, indent=4)
            else:
                user = Catalog.search_id(self.users, uri[1])
                if user == None:
                    user = f"<h1>Nessun utente trovato con l'id {uri[1]}</h1>"
                else:
                    user = json.dumps(user, indent=4)
                return user

        elif uri[0] == "services":
            if len(uri) == 1:
                return json.dumps({"services":self.services}, indent=4)
            else:
                service = Catalog.search_id(self.services, uri[1])
                if service == None:
                    service = f"<h1>Nessun servizio trovato con l'id {uri[1]}</h1>"
                else:
                    service = json.dumps(service, indent=4)
                return service
        else:
            cp.HTTPError(404, "Not found")

    def PUT(self, *uri, **params):
        """ Metodo PUT
            Aggiunge users, devices e services all'elenco 
        """

        if len(uri) != 1:
            cp.HTTPError(400, "Bad request")

        if uri[0] == "newdevice":
            body = json.loads(cp.request.body.read().decode("utf-8"))
            body["timestamp"] = time.time()
            self.cerca_value(body, "device")

            self.salva_values()
        
        elif uri[0] == "newuser":
            body = json.loads(cp.request.body.read().decode("utf-8"))
            self.cerca_value(body, "user")

            self.salva_values()

        elif uri[0] == "newservice":
            body = json.loads(cp.request.body.read().decode("utf-8"))
            body["timestamp"] = time.time()
            self.cerca_value(body, "service")

            self.salva_values()

        else:
            cp.HTTPError(404, "Not found")

if __name__ == "__main__":
    
    conf =  {
                '/':    {
                            'request.dispatch': cp.dispatch.MethodDispatcher(),
                            'tools.sessions.on':True,
                            'tools.staticdir.root': os.path.abspath(os.getcwd())
                        }
            }
    catalog = Catalog("mqtt.eclipse.org", port=1883)
    loop = Loop(2*60, catalog)
    loop.start()
    cp.tree.mount(catalog, '/', conf)
    cp.config.update({'server.socket_port':9090})
    cp.engine.start()
    cp.engine.block()

#{"users": [],"devices": [],"services": []}
#{"id":"123Stella","nome":"Marco","surname":"Manco","email":"prova@lab.com"}