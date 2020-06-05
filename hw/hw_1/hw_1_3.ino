#define MSEC 1e03
#define USEC 1e06

#define LED_PIN 12
#define PIR_PIN 7

int ledState = LOW
int cont_eventi = 0

void func_pir()
{
    // Read del valore del sensore
    int val_sensore_pir = digitalRead(PIR_PIN);
    // Scrittura del valore sul led
    digitalWrite(LED_PIN, val_sensore_pir);
    // Contiamo il numero di eventi
    cont_eventi++;
}

void setup()
{
    // Set dei pin 
    pinMode(LED_PIN, OUTPUT);
    pinMode(PIR_PIN, INPUT);

    // Set serial
    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB 1 parte 1 gruppo\nManco Davide\nCorvaglia Alessio\nManco Marco");

    // Set ISR su entrambi i fronti del sensore PIR
    attachInterrupt(digitalPinToInterrupt(PIR_PIN), func_pir, CHANGE);
}

void loop()
{
    Serial.print("Totale eventi contati: ");
    Serial.println(cont_eventi, DEC);
    delay(30*MSEC);
}
