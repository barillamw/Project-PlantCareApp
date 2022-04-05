#include <Servo.h>
#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>

// macros for on and off for anything using the relays
#define ON LOW
#define OFF HIGH

// initialize all of the pin numbers
int servoPin1 = 6;
int servoPin2 = 7;
int pumpPin = 8;
int lightPin = 9;
int lightSensor = A0;
int soilSensor = A1;

// initialize all sensor readings to 0
int uvIndex = 0;
int soilIndex = 0;

// intialize the two servos to direct traffic (water)
Servo servo1;
Servo servo2;

// variable to keep track of which plant is getting watered
// default 0 is everything closed
int state = 0;

// initialize the server for the Yun
YunServer server;

void setup() {
  // start the serial output
  Serial.begin(115200);
  // setup the builtin LED to know if the Bridge is working or not
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
  Bridge.begin();
  digitalWrite(13, HIGH);
  digitalWrite(pumpPin, OFF);
  digitalWrite(lightPin, OFF);
  server.listenOnLocalhost();
  server.begin();

  // attach the two servos to the correct pins
  servo1.attach(servoPin1);
  servo2.attach(servoPin2);
  pinMode(pumpPin, OUTPUT);
  pinMode(lightPin, OUTPUT);

  // close both valves
  servo1.write(0);
  servo2.write(0);

  //TODO include timer config function
  //TODO sensor calibration?
}

void loop() {
  // start the server
  YunClient client = server.accept();

  //TODO establish way to retreive the IP Address and send it to the client someway

  // if a command comes in via HTTP Request
  if (client) {
    // process whatever the command is
    process(client);
    // stop the server
    client.stop();
  }
  // wait a little while
  delay(50);
}

/**
 * determines what kind of command is coming in and redirects to the appropriate function
 * @param client - YunClient the bridge that holds input in a buffer
 */ 
void process(YunClient client) {
  String command = client.readStringUntil('/');
  client.print(F(""));
  // parse the input to figure out what kind of command it is
  if (command == "pump") {
    pumpCommand(client);
  } else if (command == "light") {
    lightCommand(client);
  } 
  
  else{
  //Report error to client
  client.println("Error: Unknown Command");
  }
}

/**
 * function to turn the pump on and direct it towards a certain plant
 * @param client - YunClient the bridge that holds input in a buffer
 */
void pumpCommand(YunClient client) {
  // see if we are turning it on or off
  String command = client.readStringUntil('/');
  Serial.print(command);

  if (command == "status") {
    //Report the Status of the pump to the client
    client.print(F("Pump is "));
    if(digitalRead(pumpPin) == ON) client.print(F("on."));
    else client.print(F("off."));
    
  } else if(command == "on") { 
    //Turn the pump on and report to client
    // TODO need a scheduler to figure keep track of watering a plant if one is already being watered

    //int plantNum = client.parseInt();
      
      // move the servos to direct towards the right pump
      //bool out = controlFlow(plantNum);
      // set to the new state
      //if (out) {
        //state = plantNum;
     // }
      //delay so the servos can move
      delay(200);
      // turn the pump on
      digitalWrite(pumpPin, ON); 
      client.print(F("Pump Turned On."));
      // TODO time the pump so it turns off after a plant specific amount of time using timer interrupt
      
    } else if (command == "off") {
      //Turn the pump off and report to the client
      digitalWrite(pumpPin, OFF);
      client.print(F("Pump Turned Off."));
      //TODO turn off the pump timer
      
    }else if(command == "sensor"){
      //Read the Light Sensor, Store in uvIndex and report to Client
      soilIndex = analogRead(soilSensor);
      client.print(F("The Soil Index is..."));
      client.print(soilIndex);
      //TODO make this work for the multiple plants. Use an Array?
    }
    else {
      //Report unknown command to the Client
      client.print(F("Error: Pump Command Unkown."));
    }
  }


/**
 * function to turn the light on and off and read the sensor value
 * @param client - YunClient the bridge that holds input in a buffer
 */
void lightCommand(YunClient client) {
  String command = client.readStringUntil('/');
  Serial.print("Light");
  // TODO need an interrupt to keep track of how long the light has been on for
  if (command == "on") {
      //Turn the light on and report to the Client
      digitalWrite(lightPin, ON);
      client.print(F("The light is on."));
      
    } else if (command == "off") {
      //Turn the Light off and report to the client
      digitalWrite(lightPin, OFF);
      client.print(F("The light is off."));
      
    } else if (command == "sensor") {
      //Read the Light Sensor, Store in uvIndex and report to Client
      uvIndex = analogRead(lightSensor)*10;
      client.print(F("The UV Index is..."));
      client.print(uvIndex);
      
    } else if (command == "status") {
      //Report the Status of the Light to the Client
      client.print(F("Pump is "));
      if(digitalRead(lightPin) == ON) client.print(F("on."));
      else client.print(F("off."));
      
    } else {
      //Report the unknown command to the client
      Serial.print("Error: Unknown Light Command.");
    }
}

/**
 * directs the servos towards the specified plant
 * @param plantNum - number of the plant we want to water
 * @return int of the new directions that the water would flow to
 */
int controlFlow(int plantNum) {
  if (plantNum> 4 || plantNum< 0) {
    return false;
  }
  // interface, get signal saying either 0, 1, 2, 3, 4
  // 0, 1, 2, 3, 4 indicate which plant is getting watered
  switch (plantNum) {
    case 0:
      servo1.write(0);
      servo2.write(0);
      break;
    case 1:
      servo1.write(180);
      servo2.write(0);
      break;
    case 2:
      servo1.write(90);
      servo2.write(0);
      break;
    case 3:
      servo1.write(0);
      servo2.write(90);
      break;
    case 4:
      servo1.write(0);
      servo2.write(180);
      break;
  }
  return 0;
}


// thing to parse incoming digital commands used for outputs and binary inputs, reference
void digitalCommand(YunClient client) {
  int pin, value;
  pin = client.parseInt();

  if (client.read() == '/') {
    value = client.parseInt();
    digitalWrite(pin, value);
  }
  else {
    value = digitalRead(pin);
  }
  client.print(F("Pin D"));
  client.print(pin);
  client.print(F(" set to "));
  client.println(value);

  String key = "D";
  key += pin;
  Bridge.put(key, String(value));
}

// thing to parse incoming analog commands used for sensors, reference
void analogCommand(BridgeClient client) {
  int pin, value;

  // Read pin number
  pin = client.parseInt();

  // If the next character is a '/' it means we have an URL
  // with a value like: "/analog/5/120"
  if (client.read() == '/') {
    // Read value and execute command
    value = client.parseInt();
    analogWrite(pin, value);

    // Send feedback to client
    client.print(F("Pin D"));
    client.print(pin);
    client.print(F(" set to analog "));
    client.println(value);

    // Update datastore key with the current pin value
    String key = "D";
    key += pin;
    Bridge.put(key, String(value));
  } else {
    // Read analog pin
    value = analogRead(pin);

    // Send feedback to client
    client.print(F("Pin A"));
    client.print(pin);
    client.print(F(" reads analog "));
    client.println(value);

    // Update datastore key with the current pin value
    String key = "A";
    key += pin;
    Bridge.put(key, String(value));
  }
}
