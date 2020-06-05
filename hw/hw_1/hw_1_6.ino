#include <math.h>
#include <LiquidCrystal_PCF8574.h>

LiquidCrystal_PCF8574 lcd(0x27);

#define MSEC 1e03
#define USEC 1e06
#define K 273.15

#define TEMP_PIN A1
#define B 4275
#define R0 100000
#define VCC 1023
#define T0 298.15

#define R(vsig) ((VCC/vsig) - 1)*R0
#define T(r) 1/((log(r/R0)/B) + (1/T0))

#define PERIOD 10

double func_controllo_temperatura()
{
    double val_temp =(double) analogRead(TEMP_PIN);
    double r = R(val_temp);
    double t = T(r) - K;
    return t;
}

void stampa_su_display(String temp_str){
    lcd.setCursor(0, 11);
    lcd.print(temp_str);
}

void setup()
{
    // Set serial
    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB 1 parte 1 gruppo\nManco Davide\nCorvaglia Alessio\nManco Marco");

    // Set dei pin
    pinMode(TEMP_PIN, INPUT);

    // Set lcd
    lcd.begin(16, 2);
    lcd.setBlacklight(255);
    lcd.home();
    lcd.clear();
    lcd.print("Temperatura:");
}

void loop()
{
    double temp = func_controllo_temperatura();
    String temp_str = String(temp, 2);
    stampa_su_display(temp_str);
    delay(PERIOD*MSEC);
}