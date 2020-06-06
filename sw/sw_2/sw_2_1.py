import cherrypy as cp 
import os
import sys
import json
import time #   time.ctime(time.time()) restituisce qualcosa che hai gia' visto 
            #   e rivedeitelo se non te lo ricordi

class NomeClasse():
    exposed = True
    file = "values.json"
    
    def __init__(self, domain, ip="", port=""):
        self._messagebroker =   {
                                "domain":domain,
                                "ip":ip,
                                "port":port
                                }
        self.leggi_values()

    @property
    def messagebroker(self):
        return self._messagebroker

    @messagebroker.setter
    def messagebroker(self, messagebroker):
        self._messagebroker = messagebroker

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, devices):
        self._devices.append(devices)

    @property
    def users(self):
        return self._users

    @users.setter
    def users(self, users):
        self._users.append(users)

    @property
    def services(self):
        return self._services

    @services.setter
    def services(self, services):
        self._services.append(services)

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
                device = NomeClasse.search_id(self.devices, uri[1])
                if device == None:
                    device = f"<h1>Nessun dispositivo trovato con l'id {uri[1]}</h1>"
                else:
                    device = json.dumps(device, indent=4)
                return device

        elif uri[0] == "users":
            if len(uri) == 1:
                return json.dumps({"users":self.users}, indent=4)
            else:
                user = NomeClasse.search_id(self.users, uri[1])
                if user == None:
                    user = f"<h1>Nessun dutente trovato con l'id {uri[1]}</h1>"
                else:
                    user = json.dumps(user, indent=4)
                return user

        elif uri[0] == "services":
            if len(uri) == 1:
                return json.dumps({"services":self.services}, indent=4)
            else:
                service = NomeClasse.search_id(self.services, uri[1])
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

    def leggi_values(self):
        """
            Legge i valori salvati nel file

            probabilmente servira un semafor se implementiamo i thread
            reader e writer tornano AMEN
        """

        with open(self.file, "r") as f:
            diz = json.loads(f.read())
        
        self._devices = diz["devices"]
        self._users = diz["users"]
        self._services = diz["services"]
    
    def salva_values(self):
        """
            Scrive i valori su file

            probabilmente servira un semafor se implementiamo i thread
            reader e writer tornano AMEN
        """

        diz = {
                "users":self.users,
                "devices":self.devices,
                "services":self.services
              }

        with open(self.file, "w") as f:
            f.write(f"{json.dumps(diz)}")

    def cerca_value(self, value, type):

        id_val = value["id"]

        if type == "user":
            for e in self.users:
                if e["id"] == id:
                    break
            else:
                slef.users = value

        if type == "device":
            for n, e in enumerate(self.devices):
                if e["id"] == id:
                    self.devices[n]["timestamp"] = value["timestamp"]
                    break
            else:
                slef.users = value

        if type == "service":
            for n, e in enumerate(self.services):
                if e["id"] == id:
                    self.services[n]["timestamp"] = value["timestamp"]
                    break
            else:
                slef.users = value

        

    @staticmethod
    def search_id(list_, id):
        for d in list_:
            if d["id"] == id:
                return d
        return None

if __name__ == "__main__":
    
    conf =  {
                '/':    {
                            'request.dispatch': cp.dispatch.MethodDispatcher(),
                            'tools.sessions.on':True,
                            'tools.staticdir.root': os.path.abspath(os.getcwd())
                        }
            }

    cp.tree.mount(NomeClasse("prova"), '/', conf)
    cp.config.update({'server.socket_port':9090})
    cp.engine.start()
    cp.engine.block()

#{"users":[],"devices":[],"services":[]}
#{"id":"123Stella","nome":"Marco","surname":"Manco","email":"prova@lab.com"}