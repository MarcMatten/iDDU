// LED settings
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN 15

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS 32

// setting up the NeoPixel library
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

// color definition
uint32_t red = pixels.Color(255, 0, 0);
uint32_t green = pixels.Color(0, 255, 0);
uint32_t blue = pixels.Color(0, 0, 255);
uint32_t yellow = pixels.Color(255, 255, 0);
uint32_t magenta = pixels.Color(255, 0, 255);
uint32_t cyan = pixels.Color(0, 255, 255);
uint32_t white = pixels.Color(255, 255, 255);
uint32_t black = pixels.Color(0, 0, 0);

uint32_t RPMColours[] = {green, green, green, yellow, yellow, yellow, red, red};
uint32_t allColours[] = {yellow, yellow, yellow, yellow, blue, blue, blue, blue, green, green, green, yellow, yellow, yellow, red, red};

int currentValue = 0;
int values[] = {0,0,0,0,0,0,0};

int BInit = 0;
int RPM = 0;
int SlipFL = 0;
int SlipFR = 0;
int SlipRL = 0;
int SlipRR = 0;
int ABS = 0;

const int BUFFER_SIZE = 7;
byte buf[BUFFER_SIZE];
int rlen = 0;


// =========================================================
// =========================================================

void setup() {
  // Setup for fan controll
  Serial.begin(9600);
  Serial.setTimeout(2);

  // These lines are specifically to support the Adafruit Trinket 5V 16 MHz.
  // Any other board, you can remove this part (but no harm leaving it):
  #if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
    clock_prescale_set(clock_div_1);
  #endif
  // END of Trinket-specific code.

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
  pixels.setBrightness(25);
  initLEDS();


// =========================================================
// =========================================================
}

void loop() {
  if (Serial.available() > 0) {
    rlen = Serial.readBytesUntil('\n', buf, BUFFER_SIZE);
  }

  if (rlen == 7) {
    RPM = min(buf[0], 8);
    SlipFL = min(buf[1], 4);
    SlipFR = min(buf[2], 4);
    SlipRL = min(buf[3], 4);
    SlipRR = min(buf[4], 4);
    BInit = min(buf[5], 1);
    ABS = min(buf[6], 4);
    rlen = 0;
  }
  else {
    BInit = 0;
  }
    
  pixels.clear();

  // init
  if (BInit > 0) {
    initLEDS();
  }  

  // shift lights
  if (0 < RPM < 8) {
    for (int i = 1; i <= RPM; i++) {
      pixels.setPixelColor(7+i, RPMColours[i-1]);
      pixels.setPixelColor(24-i, RPMColours[i-1]);
    }
    if (RPM == 7){
      pixels.fill(red, 15, 2);     
    }
  }
  
  if (RPM == 8) {
    pixels.fill(blue, 8, 16);
  }

  // Slip Lights  
  if (SlipFL > 0) {
    pixels.fill(yellow, 24, SlipFL);
  }
  if (SlipFR > 0) {
    pixels.fill(yellow, 8-SlipFR, SlipFR);
  }
  if (SlipRL > 0) {
    pixels.fill(blue, 32-SlipRL, SlipRL);
  }
  if (SlipRR > 0) {
    pixels.fill(blue, 0, SlipRR);
  }

  // ABS  
  if (ABS > 0) {
    if (ABS == 1) {
      pixels.fill(green, 0, 2);
      pixels.fill(green, 30, 31);
    }
    if (ABS == 2) {
      pixels.fill(yellow, 0, 4);
      pixels.fill(yellow, 28, 31);
    }
    if (ABS == 3) {
      pixels.fill(red, 0, 6);
      pixels.fill(red, 26, 31);
    }
    if (ABS == 4) {
      pixels.fill(blue, 0, 8);
      pixels.fill(blue, 24, 31);
    }
  }
  
  pixels.show();   // Send the updated pixel colors to the hardware.
  
}

void initLEDS() {
  for (int i=0; i < 16; i++) {
    pixels.setPixelColor(i, allColours[i]);
    pixels.setPixelColor(31 - i, allColours[i]);
    pixels.show();
    delay(30);
  }
 
  delay(250);
  
  for (int i=0; i < 16; i++) {
    pixels.fill(black, 15-i, (i+1)*2);
    pixels.show();
    delay(30);
  }
  
  pixels.clear();
  BInit = 0;
  values[1] = 0;
}
