#include "Adafruit_seesaw.h"

Adafruit_seesaw ss;
int levelReading = 0;
int uvIndex = 0;

void setup() {
  Serial.begin(115200);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);

  Serial.println("seesaw Soil Sensor example!");
  if (!ss.begin(0x36)) {
    Serial.println("ERROR! seesaw not found");
    while(1);
  } else {
    Serial.print("seesaw started! version: ");
    Serial.println(ss.getVersion(), HEX);
  }

}

void loop() {

  
  float tempC = ss.getTemp();
  uint16_t capread = ss.touchRead(0);
  levelReading = analogRead(A0);
  uvIndex = analogRead(A1)/0.1;

  Serial.print("Temperature: "); Serial.print(tempC); Serial.println("*C");
  Serial.print("Capacitive: "); Serial.println(capread);
  Serial.print("Water Level: "); Serial.println(levelReading);
  Serial.print("UV Index: "); Serial.println(uvIndex);
  Serial.println("-----------");

  
  delay(1000);
}
