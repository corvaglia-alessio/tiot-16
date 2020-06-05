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
}

void loop()
{
    redState = !redState;
    digitalWrite(RED_PIN, redState);
    delay(RED_PERIOD*MSEC);
}

