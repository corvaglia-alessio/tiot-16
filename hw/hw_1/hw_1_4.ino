#define MSEC 1e03
#define USEC 1e06

#define VENTOLA_PIN 9
#define STEP 25.5

int cont_step = 0;
float current_speed = 0;

void setup()
{
    // Set serial
    Serial.begin(9600);
    while(!Serial);
    Serial.println("LAB 1 parte 1 gruppo\nManco Davide\nCorvaglia Alessio\nManco Marco");

    // Set dei pin
    pinMode(VENTOLA_PIN, OUTPUT);
    analogWrite(VENTOLA_PIN, (float) current_speed);
    Serial.print("Current speed: ");
    Serial.print(current_speed, DEC);
}

void loop(){
    if(Serial.available() > 0){   
        char inB = (char) Serial.read();
        if(inB == '+'){
            if(cont_step == 10){
                Serial.print("Massima velocita' della ventola");
            }
            else{
                cont_step++;
                current_speed += STEP;
                analogWrite(VENTOLA_PIN, (float) current_speed);
                Serial.print("Increasing speed: ");
                Serial.println(current_speed, DEC);               
            }
        }
        else {
            if(inB == '-'){
                if(cont_step == 0){
                    Serial.print("Minima velocita' della ventola");
                }
                else{
                    cont_step--;
                    current_speed -= STEP;
                    analogWrite(VENTOLA_PIN, (float) current_speed);
                    Serial.print("Decreasing speed: ");
                    Serial.println(current_speed, DEC);
                }
            }
            else{
                Serial.print("Errore char");
            }    
        }
    }
}