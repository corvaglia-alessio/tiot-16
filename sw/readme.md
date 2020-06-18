# tiot-16

## Dialogare con il Catalog (sw_2, sw_3, sw_4)

Per ottenere informazioni sugli **endpoint** del _Catalog_ e sulla **struttura json** da introdurre nel body delle richieste PUT, facendo una richiesta all'indirizzo del catalog (_nel nostro caso lavorando in locale `127.0.0.1`_) e alla porta `9090`. Il catalog restituirà un json con la seguente struttura:

![alt text](/schema_richiesta_home.png "Schema UML")

```json
{
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
"/tiot/16/PUT/newservice"],
"description":"Struttura del body/json per le varie richieste PUT:
newdevice:	{"id":"<id>", "endpoint":["<endpoint>", ..], "resource":"<resource>"}
newservice:	{"id":"<id>", "endpoint":["<endpoint>", ..], "resource":"<resource>"}
newsuser:	{"id":"<id>", "name":"<name>", "surname":"<surname>", "email":"<email>"}
Le response per richieste MQTT sono pubblicate sui topic:
/tiot/16/GET/+/response
/tiot/16/GET/+/+/response"
}
```

Più in particolare:

| HOST | PORT | PATH | PROTOCOL | REQUEST | TOPIC | BODY |
| --- | --- | --- | --- | --- | --- | --- |
| 127.0.0.1 | 9090 | /messagebroker | HTTP | GET | | |
| 127.0.0.1 | 9090 | /devices | HTTP | GET | | |
| 127.0.0.1 | 9090 | /devices/\<id\> | HTTP | GET | | |
| 127.0.0.1 | 9090 | /users | HTTP | GET | | |
| 127.0.0.1 | 9090 | /users/\<id\> | HTTP | GET | | |
| 127.0.0.1 | 9090 | /services | HTTP | GET | | |
| 127.0.0.1 | 9090 | /services/\<id\> | HTTP | GET | | |
| 127.0.0.1 | 9090 | /newdevice | HTTP | PUT | | {"id":"\<id\>", "endpoint":["\<endpoint\>", ..], "resource":"\<resource\>"} |
| 127.0.0.1 | 9090 | /newuser | HTTP | PUT | | {"id":"\<id\>", "name":"\<name\>", "surname":"\<surname\>", "email":"\<email\>"} |
| 127.0.0.1 | 9090 | /newservice | HTTP | PUT | | {"id":"\<id\>", "endpoint":["\<endpoint\>", ..], "resource":"\<resource\>"} |
|  |  |  | MQTT | | /tiot/16/GET/messagebroker | |
|  |  |  | MQTT | | /tiot/16/GET/devices | |
|  |  |  | MQTT | | /tiot/16/GET/devices/\<id\> | |
|  |  |  | MQTT | | /tiot/16/GET/users | |
|  |  |  | MQTT | | /tiot/16/GET/users/\<id\> | |
|  |  |  | MQTT | | /tiot/16/GET/services | |
|  |  |  | MQTT | | /tiot/16/GET/services/\<id\> | |
|  |  |  | MQTT | | /tiot/16/PUT/newdevice | {"id":"\<id\>", "endpoint":["\<endpoint\>", ..], "resource":"\<resource\>"} |
|  |  |  | MQTT | | /tiot/16/PUT/newuser | {"id":"\<id\>", "name":"\<name\>", "surname":"\<surname\>", "email":"\<email\>"} |
|  |  |  | MQTT | | /tiot/16/PUT/newservice | {"id":"\<id\>", "endpoint":["\<endpoint\>", ..], "resource":"\<resource\>"} |
