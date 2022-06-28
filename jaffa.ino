#include <dht_nonblocking.h>
#include "MQ135.h"

#define HWSERIAL Serial5

#define RZERO 100.0 //this value will change from sensor to sensor, you will need to calibrate the zero value before planning to use code
#define DHT_SENSOR_TYPE DHT_TYPE_11

const int ledPin = LED_BUILTIN;
static const int DHT_SENSOR_PIN = 18;
DHT_nonblocking dht_sensor( DHT_SENSOR_PIN, DHT_SENSOR_TYPE );

MQ135 gasSensor = MQ135(A2);

int dustPin=A0;
float dustVal=0; 
int ledPower=15;
int delayTime=280;
int delayTime2=40;
float offTime=9680;

float totalParticle = 0;
float totalPPM = 0;
int readCount = 0;

void setup(){
Serial.begin(9600);
HWSERIAL.begin(9600);
delay(50);
pinMode(ledPower,OUTPUT);
pinMode(dustPin, INPUT);

pinMode(ledPin, OUTPUT);
digitalWrite(ledPin, HIGH);

}
 
void loop() {
  
//this block of code is what's involved in reading an air particulate value from the KS0196
//it seems backward to set the sensing LED to low in order to turn in on, but that's how they made the sensor, not sure why
//the delay cannot be changed, KS0196 specifically requires those values in order to provide best results
digitalWrite(ledPower, LOW); // power on the LED
delayMicroseconds(280);
dustVal = analogRead(dustPin); // read the dust value
delayMicroseconds(40);
digitalWrite(ledPower, HIGH); // turn the LED off

//because the sensor is very noise prone, we keep a running average between data reads from the hub
totalParticle = totalParticle + dustVal;
readCount++;
HWSERIAL.println(totalParticle / readCount);

//read the volatile compounds value from the MQ-135
//this sensor is also noise prone, so we again keen a running average between hub reads
//float rzero = gasSensor.getRZero(); #see MQ-135 library reference manual online for instruction on zero-ing the sensor
float ppm = gasSensor.getPPM();
totalPPM = totalPPM + ppm;
HWSERIAL.println(totalPPM / readCount);

//has the hub send us some input? If a 1, that signifies that they've just read the sensor's output
//If that's the case, we can restart the running averages
if(HWSERIAL.available() == true)
{
  char inByte = HWSERIAL.read();
  if(inByte == '1')
  {
    totalParticle = 0;
    totalPPM = 0;
    readCount = 0;
  }
}

float temperature;
float humidity;

if(dht_sensor.measure(&temperature, &humidity)) //read from the DHT11 humidity sensor, don't need a running average, noise is negligable
{
  //HWSERIAL.print( temperature, 1 ); uncomment if you wish to transmit temperature in addition to humidity, note that the hub program will need to be modified in order to accommodate the new input
  HWSERIAL.println( humidity, 1 );
}

delay(1000); //power savings by only running the sensor program once a second

}
