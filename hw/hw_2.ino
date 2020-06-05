#include <math.h>
#include <LiquidCrystal_PCF8574.h>

/* --------------------------------------- */
/*          Definizione Costanti           */
/* --------------------------------------- */

#define MIN 6e04
#define MSEC 1e03
#define K 273.15

// Costanti sensore temperatura
#define B 4275
#define R0 100000
#define VCC 1023
#define T0 298.15

// Valori in presenza di persone nella stanza
#define TEMP_VENTOLA_MIN_P  25.0
#define TEMP_VENTOLA_MAX_P 30.0
#define TEMP_LED_MIN_P  15.0
#define TEMP_LED_MAX_P 20.0

// Valori in assenza di persone nella stanza
#define TEMP_VENTOLA_MIN_A  27.0
#define TEMP_VENTOLA_MAX_A  32.0
#define TEMP_LED_MIN_A  17.0
#define TEMP_LED_MAX_A  22.0

/* 
    TIME_PEOPLE:
    Tempo in min dopo il quale non vi 
    sono persone nella stanza 
*/
#define TIME_PEOPLE_PIR 10
#define TIME_PEOPLE_NOISE 15
/* 
    PERIOD:
    Tempo in sec di attesa tra un loop ed un altro 
*/
#define PERIOD 10
/* 
    N_NOISE:
    Numero di rumori entro RANGE_TIME_NOISE
    per ottenere la conferma di persone nella stanza
    mediante sensore di rumore
*/
#define N_NOISE 10
#define RANGE_TIME_NOISE 5

/* --------------------------------------- */
/*  Definizione PIN dei vari componenti    */
/* --------------------------------------- */

#define TEMP_PIN A1
#define LED_PIN_2 11
#define LED_PIN 10
#define VENTOLA_PIN 9
#define PIR_PIN 7
#define NOISE_PIN 4

/* --------------------------------------- */
/*         Definizione MACRO utili         */
/* --------------------------------------- */

/*
    STEP:
    valore intervallo per mappare i valori da
    0 a 255
*/
#define STEP(min, max)  (max-min)/10
#define MAP(val, start_range, step)   step*(val-start_range) // da testare con valori double

// Sensore di temperatura
#define R(vsig) ((VCC/vsig) - 1)*R0
#define T(r) 1/((log(r/R0)/B) + (1/T0))

/* --------------------------------------- */
/*        Variabili Globali                */
/* --------------------------------------- */

LiquidCrystal_PCF8574 lcd(0x27);

int led_state_2 = LOW;
double led_state = 0.0;
double ventola_state = 0.0;

float temp_ventola_min = TEMP_VENTOLA_MIN_A; 
float temp_ventola_max = TEMP_VENTOLA_MAX_A; 

float temp_led_min = TEMP_LED_MIN_A; 
float temp_led_max = TEMP_LED_MAX_A; 

int cont_people_pir = 0;
unsigned long time_cont_people_pir = 0;

int cont_people_noise = 0;
unsigned long time_cont_people_noise[N_NOISE] = {0};
/*
    Valori per sapere la posizione degli ultimi valori 
    nel vettore di tempi time_cont_people_noise
*/
int last_noise = 0;
int index_noise = 0;

int valori_mod = 0;

int cont_bat = 0;

/* --------------------------------------- */
/*    **          Prototipi       **       */
/* --------------------------------------- */

void regola_ventola(double current_temp);
void regola_led(double current_temp);
double misura_temperatura();
void people_in_room_pir();
void controllo_people_in_room_pir();
void people_in_room_noise();
void controllo_people_in_room_noise();
void remove_old_val();
void regola_valori();
void stampa_on_lcd(String first_line, String second_line);
void cambia_val_temp();
void accendi_battiti();

/* --------------------------------------- */
/*                 Funzioni                */
/* --------------------------------------- */

void setup()
{
    // Set serial
    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB 3\nSmart home controller\nManco Davide\nCorvaglia Alessio\nManco Marco");
    
    // Set dei pin
    pinMode(TEMP_PIN, INPUT);
    pinMode(PIR_PIN, INPUT);
    pinMode(NOISE_PIN, INPUT);
    pinMode(VENTOLA_PIN, OUTPUT);
    pinMode(LED_PIN_2, OUTPUT);
    pinMode(LED_PIN, OUTPUT);

     // LCD
    lcd.begin(16, 2);
    lcd.setBacklight(255);
    lcd.home();
    lcd.clear();
    //lcd.print("Temperatura:");
    
    // VENTOLA
    analogWrite(VENTOLA_PIN, ventola_state);
    Serial.println("Ventola Attivata");
    
    // LED
    analogWrite(LED_PIN, led_state);
    Serial.println("LED Attivata");

    // PIR
    attachInterrupt(digitalPinToInterrupt(PIR_PIN), people_in_room_pir, CHANGE);
}

void loop()
{
    
    cambia_val_temp();

    if(digitalRead(NOISE_PIN)==LOW)
    {
        //people_in_room_noise();
        accendi_battiti();
    }

    controllo_people_in_room_pir();
    //controllo_people_in_room_noise();

    double current_temp = misura_temperatura();
    regola_ventola(current_temp);
    regola_led(current_temp);
    regola_valori();
    String pres = (cont_people_noise || cont_people_pir)?"1":"0";
    String f_s = "T:"+String(current_temp, 1)+" Pres:"+pres;
    float ac = (ventola_state*100)/255;
    float ht = (led_state*100)/255;
    String s_s = "AC:"+String(ac, 1)+"% HT:"+String(ht, 1)+"%";
    stampa_on_lcd(f_s, s_s);
    delay(PERIOD*MSEC/2);

    f_s = "AC m:"+String(temp_ventola_min, 1)+" M:"+String(temp_ventola_max, 1);
    s_s = "HT m:"+String(temp_led_min, 1)+" M:"+String(temp_led_max, 1);
    stampa_on_lcd(f_s, s_s);
    delay(PERIOD*MSEC/2);
}

double misura_temperatura()
{
    double val_temp =(double) analogRead(TEMP_PIN);
    double r = R(val_temp);
    double t = T(r) - K;
    return t;
}

void regola_ventola(double current_temp)
{
    if(current_temp > temp_ventola_max)
        current_temp = temp_ventola_max;
    if(current_temp < temp_ventola_min)
        current_temp = temp_ventola_min;

    ventola_state = (float) MAP(current_temp, temp_ventola_min, STEP(temp_ventola_min, temp_ventola_max));
    analogWrite(VENTOLA_PIN, ventola_state);
    //Serial.print("Velocita' ventola: ");
    //Serial.println(ventola_state, DEC); 
}

void regola_led(double current_temp)
{
    if(current_temp > temp_led_max)
        current_temp = temp_led_max;
    if(current_temp < temp_led_min)
        current_temp = temp_led_min;

    led_state = (float) MAP(current_temp, temp_led_min, STEP(temp_led_min, temp_led_max));
    led_state = 255 - led_state;
    analogWrite(LED_PIN, led_state);
    //Serial.print("Intensita' LED: ");
    //Serial.println(led_state, DEC);
}

void people_in_room_pir()
{
    time_cont_people_pir = millis();
    cont_people_pir = 1;
    //Serial.println("Rilevate persone nella stanza PIR");
}

void controllo_people_in_room_pir()
{
    unsigned long current_time = millis() - time_cont_people_pir;
    if(cont_people_pir != 0 && current_time >= TIME_PEOPLE_PIR*MIN)
    {
        cont_people_pir = 0;
        //if(cont_people_noise == 0) Serial.println("Stanza vuota");
    }
}

void people_in_room_noise()
{   
    int n_rumori;

    remove_old_val();

    //Serial.println("Rilevato rumore");

    index_noise = index_noise % N_NOISE;
    time_cont_people_noise[index_noise] = millis();

    index_noise++;

    n_rumori = (last_noise>index_noise)? \
                (N_NOISE-last_noise)+index_noise: \
                index_noise-last_noise;

    if(n_rumori == N_NOISE)
    {
        cont_people_noise = 1;
        //Serial.println("Rilevate persone nella stanza NOISE");
        time_cont_people_noise[0] = time_cont_people_noise[index_noise-1];
        index_noise = 1;
        last_noise = 0;
    }
}

void controllo_people_in_room_noise()
{
    unsigned long current_time = millis() - time_cont_people_noise[index_noise-1];
    if(cont_people_noise != 0 && current_time >= TIME_PEOPLE_NOISE*MIN)
    {
        cont_people_noise = 0;
        //if(cont_people_pir == 0) Serial.println("Stanza vuota");
    }
}

void remove_old_val()
{
    unsigned long current_time = millis();
    
    while (1)
    {
        if(last_noise != index_noise)
        {
            last_noise = last_noise%N_NOISE;
            
            if(current_time - time_cont_people_noise[last_noise] >= RANGE_TIME_NOISE*MIN)
            {
                time_cont_people_noise[last_noise] = 0;
                last_noise++;
            }
            else
                break;  
        }
        else
            break; 
    }
}

void regola_valori()
{
    if(valori_mod) return;

    if(cont_people_noise || cont_people_pir)
    {
        //Serial.println("Valori cambiati in presenza");
        temp_ventola_min = TEMP_VENTOLA_MIN_P; 
        temp_ventola_max = TEMP_VENTOLA_MAX_P; 

        temp_led_min = TEMP_LED_MIN_P; 
        temp_led_max = TEMP_LED_MAX_P;
    }
    else
    {
        //Serial.println("Valori cambiati in assenza");
        temp_ventola_min = TEMP_VENTOLA_MIN_A; 
        temp_ventola_max = TEMP_VENTOLA_MAX_A; 

        temp_led_min = TEMP_LED_MIN_A; 
        temp_led_max = TEMP_LED_MAX_A;
    }
    
}
void stampa_on_lcd(String first_line, String second_line)
{
    lcd.home();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(first_line);
    lcd.setCursor(0, 1);
    lcd.print(second_line);
}

void cambia_val_temp()
{
    if(Serial.available() > 0)
    {   
        char comando = Serial.readStringUntil(';')[0];
        float min = Serial.readStringUntil(';').toFloat();
        float max = Serial.readStringUntil(';').toFloat();

        if(comando == 'L')
        {
            temp_led_min = min;
            temp_led_max = max;
            Serial.println("\nMin letto");
            Serial.print(temp_led_min, DEC);
            Serial.println("\nMax letto");
            Serial.print(temp_led_max, DEC);
            valori_mod = 1;
        }
        else
        {
            if(comando == 'V')
            {
                temp_ventola_min = min;
                temp_ventola_max = max;
                Serial.println("min letto");
                Serial.print(temp_ventola_min, DEC);
                Serial.println("max letto");
                Serial.print(temp_ventola_max, DEC);
                valori_mod = 1;
            }
            else
            {
                Serial.println("Errore char non valido");
            }
            
        }
    }
}

void accendi_battiti()
{
    cont_bat++;

    if( cont_bat == 2)
    {
        led_state_2 = !led_state_2;
        cont_bat = 0;
        digitalWrite(LED_PIN_2, led_state_2);
    }
}