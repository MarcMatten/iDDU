int msg;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  
  Serial.begin(9600);
  delay(1000);
  
  while (Serial) {  // wait for serial port to connect. Needed for native USB port only  
    if(Serial.available()){ // if serial is available read data
      msg = Serial.read();
      if (msg == 123){  // if message recieved matches ID ('123')
        Serial.print('A');  // Send back ID
        break;
      }
    }
  }
}

void loop() {
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
}
