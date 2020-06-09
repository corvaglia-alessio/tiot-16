# tiot-16

## Dialogare con il Catalog (sw_2, sw_3)

Per ottenere informazioni sugli **endpoint** del _Catalog_ e sulla **struttura json** da introdurre nel body delle richieste PUT, facendo una richiesta all'indirizzo del catalog (_nel nostro caso lavorando in locale 127.0.0.1_) e alla porta 9090. Il catalog restituirà un json con la seguente struttura:

![alt text](https://github.com/corvaglia-alessio/tiot-16/tree/master/img/schema_richiesta_home.png "Schema UML")

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
"/tiot/16/PUT/newservice",
],
"description":"
Struttura del body/json per le varie richieste PUT:
newdevice:	{"id":"<id>", "endpoint":["<endpoint>", ..], "resurce":"<resurce>"}
newservice:	{"id":"<id>", "endpoint":["<endpoint>", ..], "resurce":"<resurce>"}
newsuser:	{"id":"<id>", "name":"<name>", "surname":"<surname>", "email":"<email>"}
Le response per richieste MQTT sono pubblicate sui topic:
/tiot/16/GET/+/response
/tiot/16/GET/+/+/response"
}
```