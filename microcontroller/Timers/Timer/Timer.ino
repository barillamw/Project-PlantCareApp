/*
  Blink

  Turns an LED on for one second, then off for one second, repeatedly.

  Most Arduinos have an on-board LED you can control. On the UNO, MEGA and ZERO
  it is attached to digital pin 13, on MKR1000 on pin 6. LED_BUILTIN is set to
  the correct LED pin independent of which board is used.
  If you want to know what pin the on-board LED is connected to on your Arduino
  model, check the Technical Specs of your board at:
  https://www.arduino.cc/en/Main/Products

  modified 8 May 2014
  by Scott Fitzgerald
  modified 2 Sep 2016
  by Arturo Guadalupi
  modified 8 Sep 2016
  by Colby Newman

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/Blink
*/

const uint16_t t3_load = 0;
const uint16_t t3_comp = 62500;

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);

  TCCR3A |= (1<<COM3A1);
  TCCR3A |= (1<<COM3A0);
  TCCR3A &= ~(1<<COM3B1);
  TCCR3A &= ~(1<<COM3B0);
  TCCR3A &= ~(1<<COM3C1);
  TCCR3A &= ~(1<<COM3C0);
  TCCR3A &= ~(1<<WGM31);
  TCCR3A &= ~(1<<WGM30);

  TCCR3B &= ~(1<<ICNC3);
  TCCR3B &= ~(1<<ICES3);
  TCCR3B &= ~(1<<WGM33);
  TCCR3B |= (1<<WGM32);
  TCCR3B |= (1<<CS32);
  TCCR3B &= ~(1<<CS31);
  TCCR3B &= ~(1<<CS30);

  TCNT3 = t3_load;
  OCR3A = t3_comp;

  TIMSK3 |= (1<<OCIE3A);

  sei();
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}

ISR(TIMER3_COMPA_vect){
   Serial.print("1 Second\n");
}
