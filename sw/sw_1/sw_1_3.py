import cherrypy as cp 
import os
import sys
import json

class Converter():
    exposed = True

    def PUT(self, *uri, **params):
        """ Metodo PUT
            Prende in input un JSON nel body della request con
                1. Lista valori da convertire
                2. Unita' di misura iniziale
                3. Unita' di misura target
        """

        try:
            diz = json.loads(cp.request.body.read())
        except:
            cp.HTTPError(400, "Richiesta non valida\nError nel json")

        values = diz.get("values")
        originalUnit = diz.get("originalUnit")
        targetUnit = diz.get("targetUnit")

        val_finale = [ Converter.converting(value, originalUnit, targetUnit) for value in values]
        diz["newValues"] = val_finale

        return json.dumps(diz, indent=4)

    @staticmethod
    def converting(value, originalUnit, targetUnit):
        """
            Metodo statico
            Prende le unita' di misura iniziale e richiama il metodo adeguato per la conversione
        """

        if originalUnit == "C":
           val_finale = Converter.fromCelsiusToOther(value, targetUnit)
        if originalUnit == "K":
           val_finale = Converter.fromKelvinToOther(value, targetUnit)
        if originalUnit == "F":
           val_finale = Converter.fromFahrenheitToOther(value, targetUnit)

        return val_finale

    @staticmethod
    def fromCelsiusToOther(val, targetUnit):
        """
            Metodo statico 
            Converte da Celsius in Kelvin o Fahrenheit
            Prende in input due params:
                1. Valore iniziale 
                2. Unita di misura target
            Restituisce 
                1. Valore Finale
        """

        val_finale = 0.0

        if targetUnit == 'K':
            val_finale = val + 273.15
        else:
            val_finale = (val * (9/5)) + 32

        return val_finale

    @staticmethod
    def fromKelvinToOther(val, targetUnit):
        """
            Metodo statico 
            Converte da Kelvin in Celsius o Fahrenheit
            Prende in input due params:
                1. Valore iniziale 
                2. Unita di misura target
            Restituisce 
                1. Valore Finale
        """

        val_finale = 0.0

        if targetUnit == 'C':
            val_finale = val - 273.15
        else:
            val_finale = (val - 273.15) * (9/5) + 32

        return val_finale

    @staticmethod
    def fromFahrenheitToOther(val, targetUnit):
        """
            Metodo statico 
            Converte da Fahrenheit in Celsius o Kelvin
            Prende in input due params:
                1. Valore iniziale 
                2. Unita di misura target
            Restituisce 
                1. Valore Finale
        """

        val_finale = 0.0

        if targetUnit == 'C':
            val_finale = (val - 32) * (5/9)
        else:
            val_finale = (val - 32) * (5/9) + 273.15

        return val_finale

if __name__ == "__main__":
    conf =  {
                '/':    {
                            'request.dispatch': cp.dispatch.MethodDispatcher()
                        }
            }

    cp.tree.mount(Converter(), '/converter', conf)
    cp.config.update({'server.socket_port':9090})
    cp.engine.start()
    cp.engine.block()
