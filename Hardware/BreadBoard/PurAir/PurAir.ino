#include <Wire.h>
#include <DHT.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 20, 4);
#define DHTPIN 7
#define DHTTYPE DHT22

float hum, temp;
int pushPin(2), pushState(0);
int smokePin = A3;
DHT dht(DHTPIN, DHTTYPE);
int redPin(12), greenPin(11), yellowPin(10); 
void setup() {
    lcd.init();
    dht.begin();
    lcd.backlight();
    pinMode(smokePin, INPUT);
    pinMode(redPin, OUTPUT);
    pinMode(greenPin, OUTPUT);
    pinMode(yellowPin, OUTPUT);
    pinMode(pushPin, INPUT);

}

void loop() {

    hum = dht.readHumidity();
    temp = dht.readTemperature();
    float Co = analogRead(smokePin);
    lcd.setCursor(0, 0);
    lcd.print("Temperature: ");
    lcd.print(temp);
    lcd.setCursor(0, 1);
    lcd.print("Humidity: ");
    lcd.print(hum);
    lcd.setCursor(0, 2);
    lcd.print("Smoke: ");
    lcd.print(Co);
    delay(100);
    if (temp <= 20){
        digitalWrite(greenPin, 1);
        digitalWrite(redPin, 0);
        digitalWrite(yellowPin, 0);
        noTone(8);
    }else if(temp <= 30){
        digitalWrite(redPin, 1);
        digitalWrite(greenPin, 1);        
        digitalWrite(yellowPin, 0);
        noTone(8);
        
    }else{
        digitalWrite(redPin, 1);
        digitalWrite(greenPin, 1);
        digitalWrite(yellowPin, 1);
        tone(8, 1000, 50);
        delay(2000);    
    }

    pushState = digitalRead(pushPin);

    if (pushState == 1){
      noTone(8);
    }
  }
