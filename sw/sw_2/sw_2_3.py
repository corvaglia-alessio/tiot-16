import os
import sys
import json
import time 
import requests

class aggiungiDev():
        @staticmethod
        def addDev():
                       data = {"id":"30","endpoint":["getting"],"resource":"temperatura"}
                       data_json = json.dumps(data)
                       payload = {'json_payload': data_json}
                       r = requests.put('http://127.0.0.1:9090/newdevice', data=data_json)
                       print(r.status_code)
                       time.sleep(10)
                       aggiungiDev.addDev()

if __name__ == "__main__":
    pr=aggiungiDev()
    pr.addDev()






