const int numReadings = 10; // sets the number of readings we take from the sensor to take the average, the more reasings the more smooth the data
int readings[numReadings];  // the readings from the analog input
int readIndex = 0;          // the index of the current reading
float total = 0;              // the running total
float average = 0;            // the average
float sensorPin = A5; // just allows us to refernce the pin as sensor pin, makes reading easier
int pressed = LOW; // same thing
int l = 0; // random variable
int decToPct = 100; // random variable
int current = 0; // initializes variable to be used later
int buttonStatusLeft; // initializes variable to be used later
float counter = 0; // initializes variable to be used later
int aState; // initializes variable to be used later
int aLastState; // initializes variable to be used later
int button = 6; // reference digital pin 6 as a digital pin
int mode = 0; // initializes variable to be used later
int rollerButtonPin = 3; // reference digital pin 3 as a button pin
int rollerSignalPin = 4; // reference digital pin 4 as a signal pin
int rollerSignalPinPhase = 5; // reference digital pin 5 as a phase pin
float currentLength = 0; // initializes variable to be used later
float circumfrence = 0; // initializes variable to be used later
int rollerButton = 0; // initializes variable to be used later

struct calVariables { //creates a struct "variable" which has multiple variables inside it
  float max;
  float percentage;
  float length;
  float radius;
  int lightInv;
  float rollInv;
  float lastX; /* as of this moment unused variable which stored the last recorded length of used tube to be re-referenced the 
  next time the function is run to get total used volume without having to re-roll through the tube */
  float volume;
  float currentX;
  float spacer; // this variable only exists because for some reason if you call multiple variables of a struct to be defined in a function the last one doesnt update kms
  int arrayPos; //i think this is un used because i found a better way to accomplish whatever i was trying to do
  float inventoryPackages; 
};
//creates modifier for variables inside struct, allows the variables to actually be accessed and changed by creating a bridge variable
calVariables value;

void setup() {
  // initialize serial communication with computer:
  Serial.begin(9600);
  //sets one pin low to use for buttons so it doesnt mis-register a press at startup
  digitalWrite(6, LOW);
  
  // initialize all the readings to 0: sets up array to be used to get average sensor value
  for (int thisReading = 0; thisReading < numReadings; thisReading++) {
    readings[thisReading] = 0;
  }
  //allows for input from button and other digital pins without power noise from arduino
  pinMode(6, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  //begin first time calibration
  for (int j = 0; j < 40; j++) { // just prints a bunch of spaces to the console
    Serial.println(" ");
  }
  delay(100);
  //***OPTIONAL STARTUP CALIBRATION TURNED OFF FOR DEMO PURPOSES***
  //Serial.println("first time calibration will now begin");
  //delay(2000);

  //value.max = calibrationLoop();
  //value.percentage = calibrationLoop2();
  //Serial.println("the roller will now be calibrated");
  //value.length; value.radius = rollerCalibration();
 for (int j = 0; j < 40; j++) {
    Serial.println(" ");
  }
value.arrayPos = 0; // like i said useless
}

void loop() {
  mode = 0;
  Serial.println("to select your chosen action enter one of the following in the consle: 1 - light inventory, 2 - roller inventory, 3 - light calibration, 4 - roller calibration");
  //digital switch counter
  unsigned long startTime = millis(); // Capture current time
  int lastState = 1;
  while(millis() - startTime < 5000) { // 5 second timer
    if (Serial.available() > 0) {
    mode = Serial.parseInt(); // whatever was said in console is parsed as a number and saved as variable mode
    }
  }
  Serial.print("mode selected: ");
  Serial.println(mode);
  //switch case checks value of mode
  //FLOAT WILL DEFAULT O TO BE RUN, HARDWARE WILL DEFAULT 0
  switch (mode) {
  
  case 0:
  break;

  case 1:
  lightSensor();
  break;
  
  case 2:
  value.rollInv; value.lastX = roller(); //calls for roller() to define rollInv and lastX
  break;

  case 3:
  value.max = calibrationLoop(); //calls for function to define max light variable
  value.percentage = calibrationLoop2(); //calls for function to define percentage variable
  /* I split this calibration into 2 functions because the struct variables were returning odd and it was not 
  performing calculations with the right numbers, would be fixed with global variable */
  break;

  case 4:
  value.length; value.radius; value.spacer = rollerCalibration(); // calls for function to define length and radius values of tube
  value.volume;value.spacer = rollerTotalVolume(); // calls for function to define max volume of tube
  mode = 0;
  }
}

float calibrationLoop() {
  Serial.println("before beginning calibration, ensure there is nothing between the lights and sensor");
  delay(10);
  Serial.println("when ready, press the button to measure light maximum");
  //wait for button press
  while (digitalRead(button) != 0) {
    delay(10); //just  description for new users so they know how it works
  }
//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!!
  for (int i = 0; i < 10; i++) {
    // subtract the last reading:
    total = total - readings[readIndex];
    // read from the sensor:
    readings[readIndex] = analogRead(sensorPin);
    // add the reading to the total:
    total = total + readings[readIndex];
    // advance to the next position in the array:
    readIndex = readIndex + 1;
    // calculate the average:
    average = total / numReadings;
    // if we're at the end of the array...
    if (readIndex >= numReadings) {
      // ...wrap around to the beginning:
      readIndex = 0;
    }
    delay(100);
  }
  //set max and print average value in monitor
  value.max = average;
  Serial.print("maximum light level recorded: ");
  Serial.println(value.max);
  return value.max;
// end of important code
  delay(1000);
 
}

float calibrationLoop2() {
  Serial.println("to continue to the next step, press the button");
  while (digitalRead(button) != 0) {
    delay(10);
  }
  for (int j = 0; j < 40; j++) {
    Serial.println(" ");
  }
  delay(1000);
  Serial.println("please place one unit of TINTED material or storage medium between the lights and sensor");
  Serial.println("when ready, press the button to calculate light transmission percentage");
  while (digitalRead(button) != 0) {
    delay(10);
    // spam code to tell new users how to use 
  }
//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! 
  for (int i = 0; i < 10; i++) {
    total = total - readings[readIndex];
    // read from the sensor:
    readings[readIndex] = analogRead(sensorPin);
    // add the reading to the total:
    total = total + readings[readIndex];
    // advance to the next position in the array:
    readIndex = readIndex + 1;
    // calculate the average:
    average = total / numReadings;
    // if we're at the end of the array...
    if (readIndex >= numReadings) {
      // ...wrap around to the beginning:
      readIndex = 0;
    }
    delay(100);
  }
  delay(50);
  //calculate percentage
  float current = average;
  Serial.println(current);
  value.percentage = ((current/value.max));
  //prints average value in console
  Serial.print("transmission percentage: ");
  Serial.print(value.percentage*100);
  Serial.println("%");
// end of important code
  delay(2000);
  Serial.println("once the terminal clears, inventory can be manually started by selecting one in the menu");
  delay(2000);
  for (int j = 0; j < 40; j++) {
    Serial.println(" ");
  }
  return value.percentage;
}

void lightSensor() {
          Serial.println(value.max);
          Serial.println(value.percentage); //prints values to console, just for debug purposes

//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!!
          for (int i = 0; i < 10; i++) {
            total = total - readings[readIndex];
            // read from the sensor:
            readings[readIndex] = analogRead(sensorPin);
            // add the reading to the total:
            total = total + readings[readIndex];
            // advance to the next position in the array:
            readIndex = readIndex + 1;
            // calculate the average:
            average = total / numReadings;
            // if we're at the end of the array...
            if (readIndex >= numReadings) {
              // ...wrap around to the beginning:
              readIndex = 0;
          }
          }
          //calculate inventory
          value.inventoryPackages = round((log(average)-log(value.max))/log(value.percentage));
// end of important code
          //print inventory
          Serial.print("no. of packages calculated: ");
          Serial.println(value.inventoryPackages);
          delay(100);
          delay (3000);
}

float roller() {
  counter = 0; // resets counter so previous readings dont interfere
  value.rollInv = 0;
  value.currentX = 0;
Serial.println("ensure your tube is inserted far enough that the crimped edge is outside the roller (in line with the edge of the cut out)");

Serial.println("to calculate percentage left, press down lightly on the turn-handle until it clicks");
delay (3000);

//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! Same as before just used a lot

while(digitalRead(3) != 0) {
  aState = digitalRead(rollerSignalPin); // Reads the "current" state of the outputA
   // If the previous and the current state of the outputA are different, that means a Pulse has occured (i.e. rotation)
   if (aState != aLastState){     
     // If the outputB state is different to the outputA state, that means the encoder is rotating clockwise
     if (digitalRead(rollerSignalPinPhase) != aState) { 
       counter ++;
     } else {
       counter --;
     }
     Serial.print("Position: ");
     Serial.println(counter);
   } 
   aLastState = aState; // Updates the previous state of the outputA with the current state
   value.currentX = ((counter/15)*3.14159265*(11)) + 17; // the length we have currently rolled the shaft = (count/number of pins *circumfrence) +minimum distance needed to mount tube in roller

// end of important code

    Serial.print("current length extruded: ");
     Serial.println(value.currentX);
     value.currentX = (value.currentX)*1000; //stores value as mm instead of meters I think
}
Serial.println("now beginning calculation with following values"); //debug values
float lengthLeft = value.length-value.currentX;
Serial.print("length left: ");
Serial.println(lengthLeft/1000);
Serial.print("volume of tube: ");
Serial.println(value.volume);
Serial.print("length of tube: ");
Serial.println(value.length/1000);
Serial.print("radius of tube: ");
Serial.println(value.radius);
Serial.print("extruded length of tube: ");
Serial.println(value.currentX/1000);

//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! Same as before just used a lot

for (float summation = 0; summation < (lengthLeft/10);) { //takes a reimann sum from the top of the tube to the end over the length calibrated
value.rollInv = value.rollInv + (((sqrt(-summation+(value.length/10))*((value.radius/10)/(sqrt(value.length/10))))*((3.14159265)*(value.radius/10))*.25)/1000);
summation = summation + .25;
}
Serial.println(value.rollInv);
float percentLeft;
percentLeft = (value.rollInv/value.volume)*100;
Serial.print("remaining pct: ");
Serial.println(percentLeft);
  Serial.println("%");

// end of important code 

delay(5000);
return value.rollInv;
}

float rollerCalibration() {
Serial.println("please rotate roller until the number matches the length of your tube from the area before the cap to before the crimped edge in millimeters ");
Serial.println("then lightly press down on the turn-handle until it clicks");
delay (3000);
//description to tell new users calibration steps

//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! Same as before just used a lot

while(digitalRead(3) != 0) { //while button on top of roller isnt pressed, length rolled is shown, records value when pressed
  aState = digitalRead(rollerSignalPin); // Reads the "current" state of the outputA
   // If the previous and the current state of the outputA are different, that means a Pulse has occured
   if (aState != aLastState){     
     // If the outputB state is different to the outputA state, that means the encoder is rotating clockwise
     if (digitalRead(rollerSignalPinPhase) != aState) { 
       counter ++;
     } else {
       counter --;
     }
     Serial.print("Position: ");
     Serial.println(counter);
   } 
   aLastState = aState; // Updates the previous state of the outputA with the current state
   currentLength = (counter/30)*3.14159265*(12); //the length we have currently rolled the shaft = (count/number of pins *circumfrence) +minimum distance needed to mount tube in roller

// end of important code

   Serial.print("current length: ");
   Serial.print(currentLength);
   Serial.println(" mm");
   delay(10);
}
counter = 0;
value.length = currentLength*1000;
for (int j = 0; j < 40; j++) {
    Serial.println(" ");
  }

Serial.println("now rotate roller until the number matches the largest circumfrence before the cap of your tube in millimeters");
Serial.println("then lightly press down on the turn-handle until it clicks");
delay(3000);

//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! Same as before just used a lot

while(digitalRead(3) != 0) {//while button on top of roller isnt pressed, length rolled is shown, records value when pressed
  aState = digitalRead(rollerSignalPin); // Reads the "current" state of the outputA
   // If the previous and the current state of the outputA are different, that means a Pulse has occured
   if (aState != aLastState){     
     // If the outputB state is different to the outputA state, that means the encoder is rotating clockwise
     if (digitalRead(rollerSignalPinPhase) != aState) { 
       counter ++;
     } else {
       counter --;
     }
     Serial.print("Position: ");
     Serial.println(counter);
     delay(10);
   } 
   
   aLastState = aState; // Updates the previous state of the outputA with the current state
   circumfrence = (counter/15)*3.14159265*(12);
   Serial.print("circumfrence: ");
   Serial.print(circumfrence);
   Serial.println(" mm");
  value.radius = ((circumfrence)/3.14159265)/2;
  Serial.print("radius: ");

//end of important code 

  Serial.print(value.radius);
  Serial.println(" mm");
  }

}
float rollerTotalVolume() { //seperate function which calculates total volume of tube with calibration values for later use

//IMPORTANT CODE !!!!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! IMPORTANT CODE !!!!!!!!!!!!! Same as before just used a lot

for (float summation = 0; summation < (value.length/10);) {
value.volume = value.volume + (((sqrt(-summation+(value.length/10))*((value.radius/10)/(sqrt(value.length/10))))*((3.14159265)*(value.radius/10))*.25)/1000);
summation = summation + .25;
}
Serial.print("volume: ");
Serial.print(value.volume);
  Serial.println(" mL");
delay(2000);
for (int j = 0; j < 40; j++) {
    Serial.println("");
  }

//end of important code

counter = 0;
return value.volume;
}

