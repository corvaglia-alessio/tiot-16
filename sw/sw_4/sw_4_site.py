import cherrypy as cp
import os, sys

class Site():

    exposed = True

    def __init__(self):
        
        with open("index.html", "r") as f:
            self.index_html = f.read()

        

    def GET(self, *uri, **param):

        if len(uri) == 0:
            return self.index_html

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
