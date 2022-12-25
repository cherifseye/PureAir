#include <Wire.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);
#define DHTPIN 7
#define DHTTYPE DHT22

float hum, temp;
int pushPin(2), pushState(0), potPin(4);
int smokePin = A3;
DHT dht(DHTPIN, DHTTYPE);
int redPin(12), greenPin(11), yellowPin(10); 
float potVal;

void setup() {
    Serial.begin(9600);
    lcd.init();
    dht.begin();
    lcd.backlight();
    pinMode(smokePin, INPUT);
    pinMode(redPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(yellowPin, OUTPUT);
    pinMode(pushPin, INPUT);
    pinMode(potPin, INPUT);

}

void loop() {

    hum = dht.readHumidity();
    temp = dht.readTemperature();
    float Co = analogRead(smokePin);
    potVal = digitalRead(potPin);
    Serial.println(String(temp) + "," + String(hum) + "," + String(Co));
    lcd.setBacklight(potVal);
    lcd.setCursor(0, 0);
    lcd.print("Temperature: ");
    lcd.print(temp);
    lcd.setCursor(0, 1);
    lcd.print("Humidity: ");
    lcd.print(hum);
    lcd.setCursor(0, 2);
    lcd.print("Smoke: ");
    lcd.print(Co);
    delay(70);

    if (temp <= 20 && Co < 60 && hum < 60){
        digitalWrite(greenPin, 1);
        digitalWrite(redPin, 0);
        digitalWrite(yellowPin, 0);

    }else if(temp <= 30 && Co <= 150 && hum <= 75){
        digitalWrite(redPin, 0);
        digitalWrite(greenPin, 1);        
        digitalWrite(yellowPin, 1);

        
    }else{
        digitalWrite(redPin, 1);
        digitalWrite(greenPin, 1);
        digitalWrite(yellowPin, 1);
        tone(8, 1000, 1000);
        delay(1000);
        noTone(8);
        delay(3000);
        if (pushState == 1){
            noTone(8);
            delay(500000);
       }
    }

    pushState = digitalRead(pushPin);


  }
