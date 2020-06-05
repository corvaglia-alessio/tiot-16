import cherrypy as cp 
import os
import sys
import json

class MyDashboard():
    exposed = True

    def GET(self, *uri, **params):
        """
            Metodo GET
            Restituisce la pagina index.html di freeboard
        """

        with open("index.html") as f:
            page = f.read()

        return page

    def POST(self, *uri, **params):
        """ 
            Metodo POST
            Salva la configurazione della dashboard
            come JSON
        """

        if uri[0] == 'saveDashboard':
            with open("dashboard/dashboard.json", 'w') as f:
                f.write(params.get("json_string"))
        else:
            cp.HTTPError(400, "Richiesta non valida")

        
if __name__ == "__main__":
    conf =  {
                '/':    {
                            'request.dispatch': cp.dispatch.MethodDispatcher(),
                            'tools.sessions.on':True,
                            'tools.staticdir.root': os.path.abspath(os.getcwd())
                        },
                '/css': {
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': './css'
                        },
                '/js': {
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': './js'
                        },  
                '/img': {
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': './img'
                        },
                '/dashboard': {
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': './dashboard'
                        },
                '/plugins': {
                            'tools.staticdir.on': True,
                            'tools.staticdir.dir': './plugins'
                        },
            }

    cp.tree.mount(MyDashboard(), '/', conf)
    cp.config.update({'server.socket_port':9090})
    cp.engine.start()
    cp.engine.block()
