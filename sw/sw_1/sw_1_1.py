import cherrypy as cp 
import os
import sys
import json

class Converter():
    exposed = True

    def GET(self, *uri, **params):
        """ Metodo GET
            Prende in input tre parametri:
                1. Valore da convertire
                2. Unita' di misura iniziale
                3. Unita' di misura target
        """

        print(len(params)) ######
        if len(params) != 3:
            cp.HTTPError(400, "Richiesta non valida\nNumero params non valido")

        value = float(params.get("value"))
        originalUnit = params.get("originalUnit")
        targetUnit = params.get("targetUnit")

        print(value, originalUnit, targetUnit)

        out =   {
                    "value": value,
                    "originalUnit": originalUnit,
                    "targetUnit": targetUnit
                }

        val_finale = Converter.converting(value, originalUnit, targetUnit)
        out["newValue"] = val_finale

        return json.dumps(out, indent=4)

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
