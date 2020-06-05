#include <TimerOne.h>
#include <math.h>

#define MSEC 1e03
#define USEC 1e06
#define K 273.15

#define TEMP_PIN A1
#define B 4275
#define R0 100000
#define VCC 5
#define T0 298.15
#define R(vsig) ((VCC/vsig) - 1)*R0
#define T(r) 1/((log(r/R0)/B) + (1/T0))

#define PERIOD 10

double func_controllo_temperatura()
{
    double val_temp = analogRead(TEMP_PIN);
    double r = R(val_temp);
    double t = T(r) - K;
    return t;
}

void setup()
{
    // Set serial
    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB 1 parte 1 gruppo\nManco Davide\nCorvaglia Alessio\nManco Marco");

    // Set dei pin
    pinMode(TEMP_PIN, INPUT);
}

void loop()
{
    double temp = func_controllo_temperatura();
    Serial.print("Temperatura: ");
    Serial.println(temp, DEC);
    delay(PERIOD*MSEC);
}
