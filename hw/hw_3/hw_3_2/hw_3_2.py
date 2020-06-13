import cherrypy as cp 
import os
import sys
import json

class Converter():
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

    cp.tree.mount(Converter(), '/', conf)
    cp.config.update({'server.socket_port':9090})
    cp.engine.start()
    cp.engine.block()
