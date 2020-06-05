#include <TimerOne.h>

#define MSEC 1e03
#define USEC 1e06

#define RED_PIN 12
#define GREEN_PIN 11

#define RED_PERIOD 3
#define GREEN_PERIOD 7

int redState = LOW;
int greenState = LOW;

void func_green()
{
    greenState = !greenState;
    digitalWrite(GREEN_PIN, greenState);
}

void setup()
{
    pinMode(RED_PIN, OUTPUT);
    pinMode(GREEN_PIN, OUTPUT);
    Timer1.initialize(GREEN_PERIOD*USEC);
    Timer1.attachInterrupt(func_green);

    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB 1 parte 1 gruppo\nManco Davide\nCorvaglia Alessio\nManco Marco");
}

void loop()
{
    if(Serial.available() > 0)
    {   
        char inB = (char) Serial.read()
        if(inB == 'R')
        {
            Serial.print("Stato led rosso: ");
            Serial.println(redState, DEC);
        }
        else {
            if(inB == 'L')
            {
                Serial.print("Stato led verde: ");
                Serial.println(greenState, DEC);
            }
            else
            {
                Serial.print("Errore char");
            }
            
        }
    }
    redState = !redState;
    digitalWrite(RED_PIN, redState);
    delay(RED_PERIOD*MSEC);
}