import cherrypy as cp
import os, sys

class Site():

    exposed = True

    def __init__(self):
        
        with open("index.html", "r") as f:
            self.index_html = f.read()

        self.led = None
        self.ventola = None
        self.stufa = None
        

    def GET(self, *uri, **param):

        if len(uri) == 0:
            return self.index_html

        if uri[0] == "led":
            self.led = param.get("subject")

            if self.led == "on":
                return self.led
            else: # off
                return self.led

        if uri[0] == "ventola":
            self.ventola = param.get("vol")

            return self.ventola

        if uri[0] == "stufa":
            self.stufa = param.get("vol")
            
            return self.stufa

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

    cp.tree.mount(Site(), "/", conf)

    cp.config.update({'server.socket_port': 9090})

    cp.engine.start()
    cp.engine.block()
