import cherrypy as cp 
import os
import sys
import json
import time 
import threading

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
            return  """{
"gruppo":"Gruppo tiot 16",
"membri":["Marco Manco", "Alessio Corvaglia", "Davide Manco"],
"endpoint":["GET 127.0.0.1:9090/messagebroker",
"GET 127.0.0.1:9090/devices",
"GET 127.0.0.1:9090/devices/<id>",
"GET 127.0.0.1:9090/users",
"GET 127.0.0.1:9090/users/<id>",
"GET 127.0.0.1:9090/services",
"GET 127.0.0.1:9090/services/<id>",
"PUT 127.0.0.1:9090/newdevice",
"PUT 127.0.0.1:9090/newuser",
"PUT 127.0.0.1:9090/newservice",
"/tiot/16/GET/messagebroker",
"/tiot/16/GET/devices",
"/tiot/16/GET/devices/<id>",
"/tiot/16/GET/users",
"/tiot/16/GET/users/<id>",
"/tiot/16/GET/services",
"/tiot/16/GET/services/<id>",
"/tiot/16/PUT/newdevice",
"/tiot/16/PUT/newuser",
"/tiot/16/PUT/newservice",
],
"description":"
Struttura del body/json per le varie richieste PUT:
newdevice:	{"id":"<id>",
							 "endpoint":["<endpoint>", ..],
							 "resurce":"<resurce>"
							}
newservice:	{"id":"<id>",
							 "endpoint":["<endpoint>", ..],
							 "resurce":"<resurce>"
							}
newsuser:	{"id":"<id>",
							 "name":"<name>",
							 "surname":"<surname>",
							 "email":"<email>"
							}
Le response per richieste MQTT sono pubblicate sui topic:
/tiot/16/GET/+/response
/tiot/16/GET/+/+/response"
}
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