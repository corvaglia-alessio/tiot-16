import requests

class Client():
    
    def __init__(self, url, port):
        self.url=url
        self.port=port
          
    def find_message_broker(self):
        r = requests.get("http://"+self.url+":"+self.port+"/messagebroker")
        print(r.text)
        
    def registered_devices(self):
        r = requests.get("http://"+self.url+":"+self.port+"/devices")
        print (r.text)

    def find_device(self, deviceID):
        r = requests.get("http://"+self.url+":"+self.port+"/devices/"+deviceID)
        print (r.text)

    def registered_users(self):
        r = requests.get("http://"+self.url+":"+self.port+"/users")
        print (r.text)

    def find_user(self, userID):
        r = requests.get("http://"+self.url+":"+self.port+"/users/"+userID)
        print (r.text)
     
    def registered_services(self):
        r = requests.get("http://"+self.url+":"+self.port+"/services")
        print (r.text)

    def find_service(self, serviceID):
        r = requests.get("http://"+self.url+":"+self.port+"/services/"+serviceID)
        print (r.text)
        
if __name__ == "__main__":
    
    c = Client("127.0.0.1", "9090")
    c.find_message_broker()
    c.registered_devices()
    c.find_device(input("Insert device ID to search: "))
    c.registered_users()
    c.find_user(input("Insert user ID to search: "))
    c.registered_services()
    c.find_service(input("Insert service ID to search: "))
    
    
    